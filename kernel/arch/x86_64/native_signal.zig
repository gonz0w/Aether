// SPDX-License-Identifier: BSD-2-Clause
// Experimental owner-local signal frame preparation. No live-state publication.
const std = @import("std");
const Frame = @import("context.zig").Frame;

pub const user_cs = 0x23;
pub const user_ss = 0x1b;
const status_flags: u64 = 0xcd5; // CF, PF, AF, ZF, SF, DF, OF; no TF/IOPL/RF/VM.
const fixed_flags: u64 = 0x202;
const unmaskable: u64 = (1 << 8) | (1 << 18);
const magic: u64 = 0x3146474953454141; // Private experiment identity, not a published ABI.

// The return slot precedes this payload. A normal RET leaves RSP at the payload,
// as required by the pinned musl restorer's trap-only entry. No ucontext_t claim.
pub const Payload = extern struct {
    identity: u64 = magic,
    reserved: u64 = 0,
    cpu: Frame,
    mask: u64,
    padding: u64 = 0,
    fp: [512]u8,
};
pub const bytes = @sizeOf(Payload);
comptime {
    if (bytes != 720 or @offsetOf(Payload, "cpu") != 16 or
        @offsetOf(Payload, "mask") != 192 or @offsetOf(Payload, "fp") != 208)
        @compileError("experimental signal payload layout changed");
}

pub const Placement = struct { entry_rsp: u64, payload: u64, end: u64 };

// low/high describe one approved stack range, not proof that pages are mapped.
// Preserve the interrupted 128-byte red zone and the SysV entry RSP alignment.
pub fn place(rsp: u64, low: u64, high: u64) error{Invalid}!Placement {
    if (low >= high or high > (1 << 47) or rsp > high or rsp < low or
        rsp - low < 128 + bytes + 8) return error.Invalid;
    const payload = (rsp - 128 - bytes) & ~@as(u64, 15);
    if (payload < low + 8) return error.Invalid;
    return .{ .entry_rsp = payload - 8, .payload = payload, .end = payload + bytes };
}

pub const Candidate = struct {
    cpu: Frame,
    mask: u64,
    fp: [512]u8 align(16),
};

// Input is a kernel-owned byte snapshot, never a borrowed user pointer. The
// hardware-supported MXCSR mask is trusted caller state, not the payload field.
// Input/output buffers must be disjoint owner storage. On any error the caller
// discards the output; never pass live Execution storage as candidate scratch.
// Output is only a candidate: callers must validate RX RIP and writable stack
// mappings before publication. No FS base, capabilities or wait state is copied.
pub fn decodeCpuInto(input: *const [bytes]u8, supported_mxcsr: u32, result: *Candidate) error{Invalid}!void {
    const p: *align(1) const Payload = @ptrCast(input);
    if (p.identity != magic or p.reserved != 0 or p.padding != 0 or
        p.cpu.cs != user_cs or p.cpu.ss != user_ss or
        p.cpu.flags & ~(status_flags | fixed_flags) != 0 or
        p.cpu.flags & fixed_flags != fixed_flags or
        p.cpu.vector != 0 or p.cpu.error_code != 0 or
        p.cpu.rip == 0 or p.cpu.rip >= (1 << 47) or
        p.cpu.rsp == 0 or p.cpu.rsp >= (1 << 47)) return error.Invalid;
    const mxcsr = std.mem.readInt(u32, p.fp[24..28], .little);
    // Never permit upper reserved bits even if the caller passes a bad mask.
    if (supported_mxcsr == 0 or supported_mxcsr & 0xffff0000 != 0 or
        mxcsr & ~supported_mxcsr != 0) return error.Invalid;
    result.cpu = p.cpu;
    result.mask = p.mask & ~unmaskable;
    result.fp = p.fp;
    // Reserved FXSAVE bytes carry no state. Use the trusted mask on re-encoding.
    result.fp[5] = 0;
    result.fp[7] &= 7;
    std.mem.writeInt(u32, result.fp[28..32], supported_mxcsr, .little);
    for (0..8) |i| @memset(result.fp[32 + i * 16 + 10 .. 32 + (i + 1) * 16], 0);
    @memset(result.fp[416..], 0);
    return;
}

// Value-returning conveniences below are for host tests only.
fn decodeCpu(input: *const [bytes]u8, supported_mxcsr: u32) error{Invalid}!Candidate {
    var result: Candidate = undefined;
    try decodeCpuInto(input, supported_mxcsr, &result);
    return result;
}

fn sample() Payload {
    var p = Payload{
        .cpu = .{ .rip = 0x200000, .rsp = 0x800ff0, .cs = user_cs, .ss = user_ss, .flags = fixed_flags | status_flags },
        .mask = ~@as(u64, 0),
        .fp = @splat(0),
    };
    std.mem.writeInt(u32, p.fp[24..28], 0x1f80, .little);
    return p;
}
fn decode(p: Payload) error{Invalid}!Candidate {
    return decodeCpu(std.mem.asBytes(&p), 0xffbf);
}

test "placement preserves interrupted red zone for every stack alignment" {
    for (0..16) |offset| {
        const rsp = 0x801000 - offset;
        const layout = try place(rsp, 0x800000, 0x801000);
        try std.testing.expectEqual(@as(u64, 8), layout.entry_rsp % 16);
        try std.testing.expectEqual(layout.entry_rsp + 8, layout.payload);
        try std.testing.expect(layout.end <= rsp - 128);
        try std.testing.expect(layout.entry_rsp >= 0x800000);
    }
    for ([_]u64{ 0, 127, 128 + bytes + 7, 4097, std.math.maxInt(u64) }) |offset|
        try std.testing.expectError(error.Invalid, place(offset, 0, 4096));
    try std.testing.expectError(error.Invalid, place(4096, 4096, 4096));
    try std.testing.expectError(error.Invalid, place(4096, 0, std.math.maxInt(u64)));
}

test "CPU round trip preserves all general registers and defined FP bytes" {
    var p = sample();
    inline for (.{ "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15" }, 1..) |name, i| {
        @field(p.cpu, name) = i * 0x1020304;
    }
    @memset(p.fp[160..416], 0xa5);
    @memset(p.fp[416..], 0xff);
    const result = try decode(p);
    try std.testing.expectEqualDeep(p.cpu, result.cpu);
    try std.testing.expectEqual(p.mask & ~unmaskable, result.mask);
    try std.testing.expectEqualSlices(u8, p.fp[160..416], result.fp[160..416]);
    try std.testing.expectEqualSlices(u8, &(@as([96]u8, @splat(0))), result.fp[416..]);
}

test "privileged selectors flags and noncanonical addresses are rejected" {
    inline for (.{ "cs", "ss" }) |field| {
        var p = sample();
        @field(p.cpu, field) = 8;
        try std.testing.expectError(error.Invalid, decode(p));
    }
    for (0..64) |bit| {
        const flag = @as(u64, 1) << @intCast(bit);
        if (flag & (fixed_flags | status_flags) != 0) continue;
        var p = sample();
        p.cpu.flags |= flag;
        try std.testing.expectError(error.Invalid, decode(p));
    }
    for ([_]u64{ 2, 0x200 }) |flag| {
        var p = sample();
        p.cpu.flags &= ~flag;
        try std.testing.expectError(error.Invalid, decode(p));
    }
    inline for (.{ "rip", "rsp" }) |field| {
        for ([_]u64{ 0, 1 << 47, std.math.maxInt(u64) }) |address| {
            var p = sample();
            @field(p.cpu, field) = address;
            try std.testing.expectError(error.Invalid, decode(p));
        }
    }
}

test "metadata and unsafe MXCSR fail without trusting payload mask" {
    inline for (.{ "identity", "reserved", "padding" }) |field| {
        var p = sample();
        @field(p, field) ^= 1;
        try std.testing.expectError(error.Invalid, decode(p));
    }
    inline for (.{ "vector", "error_code" }) |field| {
        var p = sample();
        @field(p.cpu, field) = 1;
        try std.testing.expectError(error.Invalid, decode(p));
    }
    for ([_]u32{ 0x40, 1 << 16, 1 << 31 }) |bad| {
        var p = sample();
        std.mem.writeInt(u32, p.fp[24..28], bad, .little);
        std.mem.writeInt(u32, p.fp[28..32], 0xffffffff, .little);
        try std.testing.expectError(error.Invalid, decode(p));
    }
    const p = sample();
    for ([_]u32{ 0, 0xffffffff }) |bad_mask|
        try std.testing.expectError(error.Invalid, decodeCpu(std.mem.asBytes(&p), bad_mask));
}

const page_bytes = 4096;
const nx: u64 = 1 << 63;
const Access = enum { code, stack };

// pages and backing are the same owner's parallel slot arrays. The owner must
// exclude mapping mutation and execution throughout validation and copying.
// No direct user pointers are dereferenced or retained. Metadata is trusted;
// array lengths are checked so inconsistent storage still fails closed.
fn slot(pages: anytype, address: u64, access: Access) error{Invalid}!usize {
    for (pages, 0..) |page, i| {
        if (page.address == 0 or address < page.address or address - page.address >= page_bytes) continue;
        const flags = page.flags;
        const valid = switch (access) {
            .code => flags & 7 == 5 and flags & nx == 0,
            .stack => flags & 7 == 7 and flags & nx != 0,
        };
        if (!valid) return error.Invalid;
        return i;
    }
    return error.Invalid;
}

fn range(pages: anytype, address: u64, count: usize, access: Access) error{Invalid}!void {
    if (count == 0 or address == 0 or address >= (1 << 47) or
        count > (1 << 47) - address) return error.Invalid;
    var at = address;
    const end = address + count;
    while (at < end) {
        _ = try slot(pages, at, access);
        at += @min(end - at, page_bytes - at % page_bytes);
    }
}

fn transfer(pages: anytype, backing: [][page_bytes]u8, address: u64, buffer: []u8, write: bool) void {
    var done: usize = 0;
    while (done < buffer.len) {
        const at = address + done;
        const i = slot(pages, at, .stack) catch unreachable; // Whole range validated under the same serialization.
        const offset = at % page_bytes;
        const count = @min(buffer.len - done, page_bytes - offset);
        const mapped = backing[i][offset..][0..count];
        if (write) @memcpy(mapped, buffer[done..][0..count]) else @memcpy(buffer[done..][0..count], mapped);
        done += count;
    }
}

pub const Entry = struct {
    cpu: Frame,
    fp: [512]u8,
    mask: u64,
    action_mask: u64,
    handler: u64,
    restorer: u64,
    signal: u6,
    stack_low: u64,
    stack_high: u64,
};

// Writes one complete return slot/payload only after all checks. Returns entry
// CPU state; the runtime owner must publish it before releasing serialization.
// This bounded helper covers ordinary signals only, not real-time or SIGINFO.
pub fn prepareEntryInto(pages: anytype, backing: [][page_bytes]u8, request: *const Entry, mxcsr_mask: u32, candidate: *Candidate) error{Invalid}!void {
    if (pages.len != backing.len or request.signal == 0 or request.signal > 31 or
        request.signal == 9 or request.signal == 19) return error.Invalid;
    var payload = Payload{ .cpu = request.cpu, .fp = request.fp, .mask = request.mask };
    // RF is transient CPU resume state, not a user-restorable signal flag.
    // Normalize only the trusted trap image; decodeCpuInto still rejects RF
    // in a user-supplied return payload.
    payload.cpu.flags &= ~@as(u64, 1 << 16);
    payload.cpu.vector = 0;
    payload.cpu.error_code = 0;
    try decodeCpuInto(std.mem.asBytes(&payload), mxcsr_mask, candidate);
    try range(pages, request.cpu.rip, 1, .code);
    try range(pages, request.handler, 1, .code);
    try range(pages, request.restorer, 1, .code);
    const layout = try place(request.cpu.rsp, request.stack_low, request.stack_high);
    try range(pages, layout.entry_rsp, @intCast(request.cpu.rsp - layout.entry_rsp), .stack);
    // Serialize sanitized state, never reserved bytes from a prior kernel save.
    payload.fp = candidate.fp;
    payload.mask = candidate.mask;
    var image: [8 + bytes]u8 = undefined;
    std.mem.writeInt(u64, image[0..8], request.restorer, .little);
    @memcpy(image[8..], std.mem.asBytes(&payload));
    transfer(pages, backing, layout.entry_rsp, &image, true);
    candidate.cpu.rip = request.handler;
    candidate.cpu.rsp = layout.entry_rsp;
    candidate.cpu.rdi = request.signal;
    candidate.cpu.flags &= ~@as(u64, 0x400); // SysV handler entry requires clear DF.
    candidate.mask = (candidate.mask | request.action_mask | (@as(u64, 1) << (request.signal - 1))) & ~unmaskable;
    return;
}

// Preparation only: caller owns suspend/pending state and serialization. Save
// the pre-suspend mask in the frame, but enter under the temporary mask. The
// ordinary helper performs every fallible check before writing backing bytes.
pub fn prepareSuspendEntryInto(pages: anytype, backing: [][page_bytes]u8, request: *const Entry, restore_mask: u64, mxcsr_mask: u32, candidate: *Candidate) error{Invalid}!void {
    var saved = request.*;
    saved.mask = restore_mask;
    try prepareEntryInto(pages, backing, &saved, mxcsr_mask, candidate);
    candidate.mask = (request.mask | request.action_mask | (@as(u64, 1) << (request.signal - 1))) & ~unmaskable;
}

// RET has popped the restorer address, leaving RSP at the aligned payload.
// No active token exists to leak on longjmp. Same-domain frame replay conveys
// no authority: execution/stack permissions are freshly checked on every call.
pub fn readReturnInto(pages: anytype, backing: [][page_bytes]u8, address: u64, mxcsr_mask: u32, candidate: *Candidate) error{Invalid}!void {
    if (pages.len != backing.len or address % 16 != 0) return error.Invalid;
    try range(pages, address, bytes, .stack);
    var snapshot: [bytes]u8 = undefined;
    transfer(pages, backing, address, &snapshot, false);
    try decodeCpuInto(&snapshot, mxcsr_mask, candidate);
    try range(pages, candidate.cpu.rip, 1, .code);
    if (candidate.cpu.rsp < 128) return error.Invalid;
    try range(pages, candidate.cpu.rsp - 128, 128, .stack);
    return;
}

fn prepareEntry(pages: anytype, backing: [][page_bytes]u8, request: Entry, mxcsr_mask: u32) error{Invalid}!Candidate {
    var candidate: Candidate = undefined;
    try prepareEntryInto(pages, backing, &request, mxcsr_mask, &candidate);
    return candidate;
}
fn readReturn(pages: anytype, backing: [][page_bytes]u8, address: u64, mxcsr_mask: u32) error{Invalid}!Candidate {
    var candidate: Candidate = undefined;
    try readReturnInto(pages, backing, address, mxcsr_mask, &candidate);
    return candidate;
}

const TestPage = struct { address: u64, flags: u64 };
fn requestForTest() Entry {
    const p = sample();
    return .{ .cpu = .{ .rip = 0x200000, .rsp = 0x801100, .cs = user_cs, .ss = user_ss, .flags = 0x602, .rax = 123 }, .fp = p.fp, .mask = 4, .action_mask = 8, .handler = 0x200080, .restorer = 0x200100, .signal = 10, .stack_low = 0x800000, .stack_high = 0x802000 };
}
fn testPages() [3]TestPage {
    return .{ .{ .address = 0x200000, .flags = 5 }, .{ .address = 0x800000, .flags = 7 | nx }, .{ .address = 0x801000, .flags = 7 | nx } };
}

test "cross-page frame entry and return preserve red zone and interrupted state" {
    const pages = testPages();
    var backing: [3][page_bytes]u8 = @splat(@splat(0xa5));
    const request = requestForTest();
    const entry = try prepareEntry(&pages, &backing, request, 0xffbf);
    try std.testing.expectEqual(request.handler, entry.cpu.rip);
    try std.testing.expectEqual(@as(u64, 10), entry.cpu.rdi);
    try std.testing.expectEqual(@as(u64, 0x202), entry.cpu.flags);
    try std.testing.expectEqual(@as(u64, 4 | 8 | 512), entry.mask);
    const result = try readReturn(&pages, &backing, entry.cpu.rsp + 8, 0xffbf);
    try std.testing.expectEqualDeep(request.cpu, result.cpu);
    try std.testing.expectEqual(request.mask, result.mask);
    try std.testing.expectEqualSlices(u8, &(@as([128]u8, @splat(0xa5))), backing[2][128..256]);
    const offset = entry.cpu.rsp - 0x800000;
    try std.testing.expectEqual(request.restorer, std.mem.readInt(u64, backing[1][offset..][0..8], .little));
}

test "failed entry is atomic across missing and denied stack or code mappings" {
    const request = requestForTest();
    for (0..3) |index| {
        for ([_]u64{ 0, 1, 5 | nx, 7 }) |flags| {
            var pages = testPages();
            pages[index].flags = flags;
            var backing: [3][page_bytes]u8 = @splat(@splat(0xa5));
            const before = backing;
            try std.testing.expectError(error.Invalid, prepareEntry(&pages, &backing, request, 0xffbf));
            try std.testing.expectEqualDeep(before, backing);
        }
    }
    var pages = testPages();
    pages[2].address = 0;
    var backing: [3][page_bytes]u8 = @splat(@splat(0xa5));
    const before = backing;
    try std.testing.expectError(error.Invalid, prepareEntry(&pages, &backing, request, 0xffbf));
    try std.testing.expectEqualDeep(before, backing);
}

test "return revalidates changed mappings and rejects corrupt frame without writes" {
    var pages = testPages();
    var backing: [3][page_bytes]u8 = @splat(@splat(0));
    const entry = try prepareEntry(&pages, &backing, requestForTest(), 0xffbf);
    const before = backing;
    pages[0].flags |= nx;
    try std.testing.expectError(error.Invalid, readReturn(&pages, &backing, entry.cpu.rsp + 8, 0xffbf));
    pages = testPages();
    pages[2].flags &= ~@as(u64, 2);
    try std.testing.expectError(error.Invalid, readReturn(&pages, &backing, entry.cpu.rsp + 8, 0xffbf));
    try std.testing.expectEqualDeep(before, backing);
    pages = testPages();
    backing[1][entry.cpu.rsp + 8 - 0x800000] ^= 1;
    const corrupted = backing;
    try std.testing.expectError(error.Invalid, readReturn(&pages, &backing, entry.cpu.rsp + 8, 0xffbf));
    try std.testing.expectError(error.Invalid, readReturn(&pages, &backing, std.math.maxInt(u64) - 15, 0xffbf));
    try std.testing.expectEqualDeep(corrupted, backing);
}

test "bad entry targets signal numbers and backing shape cannot write" {
    const pages = testPages();
    var backing: [3][page_bytes]u8 = @splat(@splat(0xa5));
    const before = backing;
    inline for (.{ "handler", "restorer" }) |field| {
        for ([_]u64{ 0, 0x800000, 0x300000, std.math.maxInt(u64) }) |address| {
            var request = requestForTest();
            @field(request, field) = address;
            try std.testing.expectError(error.Invalid, prepareEntry(&pages, &backing, request, 0xffbf));
            try std.testing.expectEqualDeep(before, backing);
        }
    }
    for ([_]u6{ 0, 9, 19, 32, 63 }) |signal| {
        var request = requestForTest();
        request.signal = signal;
        try std.testing.expectError(error.Invalid, prepareEntry(&pages, &backing, request, 0xffbf));
    }
    try std.testing.expectError(error.Invalid, prepareEntry(&pages, backing[0..2], requestForTest(), 0xffbf));
    try std.testing.expectEqualDeep(before, backing);
}

test "entry normalizes CPU resume flag while user return still rejects it" {
    var pages = testPages();
    var backing: [3][page_bytes]u8 = @splat(@splat(0));
    var request = requestForTest();
    request.cpu.flags |= 1 << 16;
    var candidate: Candidate = undefined;
    try prepareEntryInto(&pages, &backing, &request, 0xffbf, &candidate);
    try std.testing.expectEqual(@as(u64, 0x202), candidate.cpu.flags);
    const layout = try place(request.cpu.rsp, request.stack_low, request.stack_high);
    try readReturnInto(&pages, &backing, layout.payload, 0xffbf, &candidate);
    try std.testing.expectEqual(@as(u64, 0x602), candidate.cpu.flags);
    var payload = sample();
    payload.cpu.flags |= 1 << 16;
    try std.testing.expectError(error.Invalid, decodeCpuInto(std.mem.asBytes(&payload), 0xffbf, &candidate));
}

test "suspend entry separates temporary handler mask from restored mask" {
    const pages = testPages();
    for ([_]u64{ 0, 4, 1 << 16, ~@as(u64, 0) }) |original| {
        for ([_]u64{ 0, 2, 1 << 20, ~@as(u64, 0) }) |temporary| {
            var backing: [3][page_bytes]u8 = @splat(@splat(0xa5));
            var request = requestForTest();
            request.signal = 17;
            request.mask = temporary;
            request.action_mask = 8 | unmaskable;
            request.cpu.rax = @bitCast(@as(i64, -4));
            var entry: Candidate = undefined;
            try prepareSuspendEntryInto(&pages, &backing, &request, original, 0xffbf, &entry);
            try std.testing.expectEqual((temporary | 8 | (1 << 16)) & ~unmaskable, entry.mask);
            const restored = try readReturn(&pages, &backing, entry.cpu.rsp + 8, 0xffbf);
            try std.testing.expectEqual(original & ~unmaskable, restored.mask);
            try std.testing.expectEqualDeep(request.cpu, restored.cpu);
            try std.testing.expectEqualSlices(u8, &(@as([128]u8, @splat(0xa5))), backing[2][128..256]);
        }
    }
}

test "suspend entry rejects invalid stack without modifying backing or request" {
    var pages = testPages();
    pages[1].flags &= ~@as(u64, 2);
    var backing: [3][page_bytes]u8 = @splat(@splat(0xa5));
    const before = backing;
    const request = requestForTest();
    const original = request;
    var candidate: Candidate = undefined;
    try std.testing.expectError(error.Invalid, prepareSuspendEntryInto(&pages, &backing, &request, 1 << 16, 0xffbf, &candidate));
    try std.testing.expectEqualDeep(before, backing);
    try std.testing.expectEqualDeep(original, request);
}
