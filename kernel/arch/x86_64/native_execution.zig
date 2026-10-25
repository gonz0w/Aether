// SPDX-License-Identifier: BSD-2-Clause
// Per-context execution and wait state: mappings, grants and lifecycle remain domain-owned.
const std = @import("std");
const Frame = @import("context.zig").Frame;

pub const Execution = struct {
    frame: Frame = .{},
    fp: [512]u8 align(16) = @splat(0),
    fs: u64 = 0,
    clear_tid: usize = 0,
    tls_base: usize = 0,
    tls_bytes: usize = 0,
    wait: Wait = .{},
    signal_mask: u64 = 0,

    // Pure candidate for a validated image/stack. Publishing it requires the
    // caller to stop old execution and settle old mapping/TID obligations.
    // No user pointer is dereferenced and no old-image register survives.
    pub fn forImage(self: *const Execution, entry: u64, stack: u64) Execution {
        var next = Execution{
            .frame = .{ .rip = entry, .rsp = stack, .cs = 0x23, .ss = 0x1b, .flags = 0x202 },
            .signal_mask = self.signal_mask,
        };
        std.mem.writeInt(u16, next.fp[0..2], 0x037f, .little);
        std.mem.writeInt(u32, next.fp[24..28], 0x1f80, .little);
        return next;
    }

    // Only after the context is stopped, clear-TID is handled and mappings are
    // detached. The empty FP state must be initialized before restoring it.
    pub fn reset(self: *Execution) void {
        self.* = .{};
    }
};

comptime {
    if (@sizeOf(Frame) != 176 or @alignOf(Execution) < 16 or
        @offsetOf(Execution, "fp") % 16 != 0 or @sizeOf(Execution) % 16 != 0)
        @compileError("native execution save-area layout mismatch");
}

test "array and embedded execution save areas remain FX aligned" {
    var contexts: [2]Execution = @splat(.{});
    for (&contexts) |*context| {
        try std.testing.expectEqual(@as(usize, 0), @intFromPtr(&context.fp) % 16);
        try std.testing.expectEqual(@as(usize, 176), @sizeOf(@TypeOf(context.frame)));
    }
    var embedded: struct { prefix: u8 = 1, execution: Execution = .{} } = .{};
    try std.testing.expectEqual(@as(usize, 0), @intFromPtr(&embedded.execution.fp) % 16);
}

test "reclaim clears complete CPU state without changing another context" {
    var contexts: [2]Execution = @splat(.{});
    contexts[0].frame = .{ .rip = 0x201000, .rsp = 0x800fff0, .rax = 37 };
    @memset(&contexts[0].fp, 0xa5);
    contexts[0].fs = 0x10001000;
    contexts[0].clear_tid = 0x10003000;
    contexts[0].tls_base = 0x10000000;
    contexts[0].tls_bytes = 16384;
    contexts[0].signal_mask = 37;
    contexts[1].frame = .{ .rip = 0x202000, .rsp = 0x800ffe0, .rax = 91 };
    @memset(&contexts[1].fp, 0x5a);
    contexts[1].fs = 0x10005000;
    contexts[1].clear_tid = 0x10007000;
    const peer = contexts[1];
    contexts[0].reset();
    try std.testing.expectEqualDeep(Execution{}, contexts[0]);
    try std.testing.expectEqualDeep(peer, contexts[1]);
}

// One owner-local registration; caller validates user mappings under IF=0.
pub const Wait = struct {
    address: usize = 0,
    started: u64 = 0,
    deadline: u64 = 0,
    monotonic: bool = false,
    pub fn park(w: *Wait, address: usize, value: u32, expected: u32, now: u64, ticks: u64) i64 {
        if (address == 0 or address % 4 != 0 or ticks == 0 or ticks > 100 or now > std.math.maxInt(u64) - ticks) return -22;
        if (w.address != 0) return -16;
        if (value != expected) return -11;
        w.* = .{ .address = address, .started = now, .deadline = now + ticks };
        return 0;
    }
    pub fn parkIndefinite(w: *Wait, address: usize, value: u32, expected: u32, now: u64) i64 {
        if (address == 0 or address % 4 != 0) return -22;
        if (w.address != 0) return -16;
        if (value != expected) return -11;
        w.* = .{ .address = address, .started = now, .deadline = 0 };
        return 0;
    }
    pub fn parkAbsolute(w: *Wait, address: usize, value: u32, expected: u32, now: u64, deadline: u64) i64 {
        if (address == 0 or address % 4 != 0 or deadline > std.math.maxInt(i64) or
            (deadline > now and deadline - now > 1_000_000_000)) return -22;
        if (w.address != 0) return -16;
        if (value != expected) return -11;
        if (deadline <= now) return -110;
        w.* = .{ .address = address, .started = now, .deadline = deadline, .monotonic = true };
        return 0;
    }
    const Done = struct { status: i64, elapsed: u64 };
    pub fn time(w: *const Wait, ticks: u64, monotonic: ?u64) ?u64 {
        return if (w.monotonic) monotonic else ticks;
    }
    pub fn completeAt(w: *Wait, key: usize, ticks: u64, monotonic: ?u64) ?Done {
        if (w.address == 0) return null;
        const now = w.time(ticks, monotonic) orelse {
            w.* = .{};
            return .{ .status = -5, .elapsed = 0 };
        };
        if (now < w.started) {
            w.* = .{};
            return .{ .status = -5, .elapsed = 0 };
        }
        return w.complete(key, now);
    }
    pub fn complete(w: *Wait, key: usize, now: u64) ?Done {
        const expired = w.deadline != 0 and now >= w.deadline;
        if (w.address == 0 or (!expired and key != w.address)) return null;
        const result: Done = .{ .status = @as(i64, if (expired) -110 else 0), .elapsed = now - w.started };
        w.* = .{};
        return result;
    }
};

test "compare and register, matching wake and deadline precedence" {
    var w: Wait = .{};
    try std.testing.expectEqual(-11, w.park(4096, 2, 1, 10, 5));
    try std.testing.expectEqualDeep(Wait{}, w);
    try std.testing.expectEqual(0, w.park(4096, 1, 1, 10, 5));
    try std.testing.expectEqual(-16, w.park(8192, 1, 1, 11, 5));
    try std.testing.expect(w.complete(8192, 14) == null);
    const done = w.complete(4096, 14).?;
    try std.testing.expectEqual(0, done.status);
    try std.testing.expectEqual(4, done.elapsed);
    try std.testing.expect(w.complete(4096, 15) == null);
    _ = w.park(4096, 1, 1, 20, 5);
    try std.testing.expectEqual(-110, w.complete(4096, 25).?.status);
    _ = w.park(4096, 1, 1, 30, 5);
    try std.testing.expectEqual(-110, w.complete(0, 35).?.status);
}

test "bad waits do not publish and execution reset cancels registration" {
    var context: Execution = .{};
    for ([_]u64{ 0, 101, std.math.maxInt(u64) }) |ticks|
        try std.testing.expectEqual(-22, context.wait.park(4096, 1, 1, 0, ticks));
    try std.testing.expectEqual(-22, context.wait.park(4097, 1, 1, 0, 1));
    try std.testing.expectEqual(-22, context.wait.park(4096, 1, 1, std.math.maxInt(u64), 1));
    try std.testing.expectEqualDeep(Wait{}, context.wait);
    _ = context.wait.park(4096, 1, 1, 0, 1);
    context.reset();
    try std.testing.expect(context.wait.complete(4096, 1) == null);
}

// Pure geometry check; the runtime separately verifies every owned RW/NX page.
pub fn stackRange(base: u64, bytes: u64, rsp: u64, low: u64, high: u64) error{Invalid}!void {
    if (base < low or base > high or bytes == 0 or bytes % 4096 != 0 or base % 4096 != 0 or
        bytes > high - base or rsp % 16 != 8) return error.Invalid;
    if (rsp < base + 128 or rsp > base + bytes - 8) return error.Invalid;
}

test "bounded stack geometry accepts offset RSP and rejects overflow and red-zone loss" {
    const low = 0x10000000;
    const high = low + 8 * 1024 * 1024;
    try stackRange(low, 256 * 1024, low + 256 * 1024 - 264, low, high);
    try stackRange(low, high - low, high - 8, low, high);
    for ([_]struct { base: u64, bytes: u64, rsp: u64 }{
        .{ .base = low, .bytes = 0, .rsp = low + 4088 },
        .{ .base = low + 1, .bytes = 4096, .rsp = low + 4088 },
        .{ .base = low, .bytes = 4097, .rsp = low + 4088 },
        .{ .base = low, .bytes = 4096, .rsp = low + 8 },
        .{ .base = low, .bytes = 4096, .rsp = low + 4096 },
        .{ .base = low, .bytes = 4096, .rsp = low + 4104 },
        .{ .base = high, .bytes = 4096, .rsp = high + 4088 },
        .{ .base = low, .bytes = std.math.maxInt(u64) - 4095, .rsp = low + 4088 },
    }) |bad| try std.testing.expectError(error.Invalid, stackRange(bad.base, bad.bytes, bad.rsp, low, high));
}

test "wait without deadline survives ticks and only matching wake completes" {
    var w: Wait = .{};
    try std.testing.expectEqual(-11, w.parkIndefinite(4096, 1, 0, 5));
    try std.testing.expectEqualDeep(Wait{}, w);
    try std.testing.expectEqual(-22, w.parkIndefinite(4097, 0, 0, 5));
    try std.testing.expectEqual(0, w.parkIndefinite(4096, 0, 0, 5));
    try std.testing.expectEqual(-16, w.parkIndefinite(8192, 0, 0, 6));
    try std.testing.expect(w.complete(0, 105) == null);
    try std.testing.expect(w.complete(8192, std.math.maxInt(u64)) == null);
    const done = w.complete(4096, 205).?;
    try std.testing.expectEqual(0, done.status);
    try std.testing.expectEqual(200, done.elapsed);
    try std.testing.expectEqualDeep(Wait{}, w);
    var context: Execution = .{};
    _ = context.wait.parkIndefinite(4096, 0, 0, 0);
    context.reset();
    try std.testing.expectEqualDeep(Execution{}, context);
}

// Mask storage only: no pending signals or delivery are implemented.
pub fn maskAfter(old: u64, how: u64, input: u64) error{Invalid}!u64 {
    const unmaskable: u64 = (1 << 8) | (1 << 18);
    return (switch (how) {
        0 => old | input,
        1 => old & ~input,
        2 => input,
        else => return error.Invalid,
    }) & ~unmaskable;
}

test "signal masks retain all permitted bits and reject invalid transitions" {
    const allowed = ~@as(u64, (1 << 8) | (1 << 18));
    try std.testing.expectEqual(allowed, try maskAfter(0, 0, std.math.maxInt(u64)));
    try std.testing.expectEqual(0, try maskAfter(allowed, 1, std.math.maxInt(u64)));
    try std.testing.expectEqual(5, try maskAfter(allowed, 2, 5));
    try std.testing.expectEqual(4, try maskAfter(5, 1, 1));
    try std.testing.expectEqual(0, try maskAfter(0, 2, ~allowed));
    try std.testing.expectError(error.Invalid, maskAfter(5, 3, 0));
    try std.testing.expectError(error.Invalid, maskAfter(5, std.math.maxInt(u64), 0));
    var contexts: [2]Execution = @splat(.{});
    contexts[0].signal_mask = 5;
    contexts[1].signal_mask = contexts[0].signal_mask;
    contexts[1].signal_mask = try maskAfter(contexts[1].signal_mask, 2, 9);
    try std.testing.expectEqual(5, contexts[0].signal_mask);
    contexts[1].reset();
    try std.testing.expectEqual(0, contexts[1].signal_mask);
    try std.testing.expectEqual(5, contexts[0].signal_mask);
}

// IDs are local to a generation-bound domain grant. Retirement never replenishes
// either budget. Live child slots and memory are independent admission limits.
pub const child_admission_limit: u32 = 4;
pub const reuse_admission_limit: u32 = 512;
pub fn admissionLimit(reuse: bool) u32 {
    return if (reuse) reuse_admission_limit else child_admission_limit;
}
pub fn childIdForProfile(ordinal: u32, instance: usize, storage: bool, reuse: bool) ?u32 {
    if (ordinal >= admissionLimit(reuse) or instance >= 4) return null;
    return @as(u32, @intCast(if (storage) instance + 3 else 1)) + ordinal * 8;
}
pub fn childId(ordinal: u32, instance: usize, storage: bool) ?u32 {
    return childIdForProfile(ordinal, instance, storage, false);
}

test "both admission profiles preserve first identities and never wrap or repeat" {
    for ([_]bool{ false, true }) |reuse| {
        for (0..4) |instance| {
            for ([_]bool{ false, true }) |storage| {
                var previous: u32 = 0;
                for (0..admissionLimit(reuse)) |ordinal| {
                    const id = childIdForProfile(@intCast(ordinal), instance, storage, reuse).?;
                    try std.testing.expect(id > previous);
                    if (ordinal == 0) try std.testing.expectEqual(@as(u32, @intCast(if (storage) instance + 3 else 1)), id);
                    if (ordinal < child_admission_limit) try std.testing.expectEqual(childId(@intCast(ordinal), instance, storage).?, id);
                    previous = id;
                }
                try std.testing.expect(childIdForProfile(admissionLimit(reuse), instance, storage, reuse) == null);
                try std.testing.expect(childIdForProfile(std.math.maxInt(u32), instance, storage, reuse) == null);
            }
        }
        try std.testing.expect(childIdForProfile(0, 4, true, reuse) == null);
    }
}

// A single domain-owned child lifetime. Grants, mappings and admission budget
// stay with the domain; this record never supplies authority on its own.
pub const Child = struct {
    execution: Execution = .{},
    used: bool = false,
    id: u32 = 0,
    running: bool = false,
    status: u8 = 0,
    stack: usize = 0,
    stack_bytes: usize = 0,

    // Caller has checked domain authority, permitted profile role and bounds.
    pub fn retire(self: *Child, expected: u32) i64 {
        if (!self.used) return -2;
        if (expected != self.id) return -9;
        if (self.running or self.execution.clear_tid != 0 or self.execution.wait.address != 0) return -16;
        self.reset();
        return 0;
    }

    // Only after stop/clear-TID and required mapping cleanup, or validated retire.
    pub fn reset(self: *Child) void {
        self.* = .{};
    }
};

test "child retirement preserves rejected records and clears only the retired owner" {
    var children: [2]Child = @splat(.{});
    children[0] = .{ .used = true, .id = 11, .running = true, .status = 37, .stack = 0x10000000, .stack_bytes = 16384 };
    children[0].execution.frame.rip = 0x201000;
    children[0].execution.fs = 0x10001000;
    children[0].execution.tls_base = 0x10000000;
    children[0].execution.tls_bytes = 16384;
    children[0].execution.signal_mask = 37;
    @memset(&children[0].execution.fp, 0xa5);
    children[1] = children[0];
    children[1].id = 19;
    const peer = children[1];
    for (&children) |*child| try std.testing.expectEqual(@as(usize, 0), @intFromPtr(&child.execution.fp) % 16);
    const live = children[0];
    try std.testing.expectEqual(-9, children[0].retire(3));
    try std.testing.expectEqual(-16, children[0].retire(11));
    try std.testing.expectEqualDeep(live, children[0]);
    children[0].running = false;
    children[0].execution.clear_tid = 0x10002000;
    const uncleared = children[0];
    try std.testing.expectEqual(-16, children[0].retire(11));
    try std.testing.expectEqualDeep(uncleared, children[0]);
    children[0].execution.clear_tid = 0;
    _ = children[0].execution.wait.parkIndefinite(0x10003000, 7, 7, 1);
    const waiting = children[0];
    try std.testing.expectEqual(-16, children[0].retire(11));
    try std.testing.expectEqualDeep(waiting, children[0]);
    children[0].execution.wait = .{};
    try std.testing.expectEqual(0, children[0].retire(11));
    try std.testing.expectEqualDeep(Child{}, children[0]);
    try std.testing.expectEqual(-2, children[0].retire(11));
    try std.testing.expectEqualDeep(peer, children[1]);
}

// Validated domain-arena ranges only; subtraction avoids end overflow.
pub fn overlaps(a: u64, bytes: u64, b: u64, other_bytes: u64) bool {
    if (bytes == 0 or other_bytes == 0) return false;
    return if (a <= b) b - a < bytes else a - b < other_bytes;
}
pub fn nextContext(children: []const Child, current: usize, parent_waiting: bool) ?usize {
    const count = children.len + 1;
    for (1..count + 1) |offset| {
        const selected = (current + offset) % count;
        if (selected == 0) {
            if (!parent_waiting) return 0;
        } else {
            const c = &children[selected - 1];
            if (c.running and c.execution.wait.address == 0) return selected;
        }
    }
    return null;
}
test "pair scheduler rotates all runnable contexts and skips stopped or waiting children" {
    var children: [2]Child = @splat(.{ .used = true, .running = true });
    try std.testing.expectEqual(1, nextContext(&children, 0, false).?);
    try std.testing.expectEqual(2, nextContext(&children, 1, false).?);
    try std.testing.expectEqual(0, nextContext(&children, 2, false).?);
    children[0].execution.wait.address = 4096;
    try std.testing.expectEqual(2, nextContext(&children, 0, false).?);
    children[1].running = false;
    try std.testing.expectEqual(0, nextContext(&children, 0, false).?);
    try std.testing.expect(nextContext(&children, 0, true) == null);
    try std.testing.expect(overlaps(4096, 8192, 8192, 4096));
    try std.testing.expect(!overlaps(4096, 4096, 8192, 4096));
    try std.testing.expect(!overlaps(4096, 4096, 0, 0));
}

// Caller validates address and authority while the owner runs with IF=0.
pub fn wake(contexts: []const *Execution, key: usize, now: u64, monotonic: ?u64, limit: usize) usize {
    var count: usize = 0;
    for (contexts) |context| {
        const timestamp = context.wait.time(now, monotonic);
        const expired = if (timestamp) |value| context.wait.deadline != 0 and value >= context.wait.deadline else true;
        const matched = key != 0 and context.wait.address == key and !expired and count < limit;
        if (context.wait.completeAt(if (matched) key else 0, now, monotonic)) |done| {
            context.frame.rax = @bitCast(done.status);
            context.frame.rdx = done.elapsed;
            if (matched) count += 1;
        }
    }
    return count;
}
test "bounded wake preserves unmatched registrations and timeout precedence" {
    var a: Execution = .{};
    var b: Execution = .{};
    const contexts = [_]*Execution{ &a, &b };
    try std.testing.expectEqual(0, a.wait.park(4096, 0, 0, 1, 5));
    try std.testing.expectEqual(0, b.wait.parkIndefinite(4096, 0, 0, 1));
    try std.testing.expectEqual(0, wake(&contexts, 4096, 2, null, 0));
    try std.testing.expectEqual(4096, a.wait.address);
    try std.testing.expectEqual(4096, b.wait.address);
    try std.testing.expectEqual(0, wake(&contexts, 8192, 2, null, 1));
    try std.testing.expectEqual(1, wake(&contexts, 4096, 3, null, 1));
    try std.testing.expectEqual(0, a.wait.address);
    try std.testing.expectEqual(2, a.frame.rdx);
    try std.testing.expectEqual(4096, b.wait.address);
    try std.testing.expectEqual(0, a.wait.park(4096, 0, 0, 3, 2));
    try std.testing.expectEqual(1, wake(&contexts, 4096, 5, null, 1));
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -110))), a.frame.rax);
    try std.testing.expectEqual(0, b.frame.rax);
    try std.testing.expectEqual(4, b.frame.rdx);
    try std.testing.expectEqual(0, wake(&contexts, 4096, 6, null, 100));
    try std.testing.expectEqual(0, a.wait.parkIndefinite(4096, 0, 0, 6));
    try std.testing.expectEqual(0, b.wait.parkIndefinite(4096, 0, 0, 6));
    try std.testing.expectEqual(2, wake(&contexts, 4096, 7, null, std.math.maxInt(usize)));
}

// Distinct, writable owner-local keys and bounded counts are validated by caller.
pub fn requeue(contexts: []const *Execution, source: usize, destination: usize, now: u64, monotonic: ?u64, wakes: usize, moves: usize) usize {
    const woken = wake(contexts, source, now, monotonic, wakes);
    var moved: usize = 0;
    for (contexts) |context| {
        if (moved == moves) break;
        if (context.wait.address == source) {
            context.wait.address = destination;
            moved += 1;
        }
    }
    return woken + moved;
}
test "requeue preserves wait lifetime and completes timeout on original deadline" {
    var a: Execution = .{};
    var b: Execution = .{};
    var c: Execution = .{};
    const contexts = [_]*Execution{ &a, &b, &c };
    _ = a.wait.parkIndefinite(4096, 0, 0, 1);
    _ = b.wait.park(4096, 0, 0, 1, 5);
    _ = c.wait.parkIndefinite(4096, 0, 0, 1);
    b.frame.rax = 77;
    try std.testing.expectEqual(0, requeue(&contexts, 4096, 8192, 2, null, 0, 0));
    try std.testing.expectEqual(2, requeue(&contexts, 4096, 8192, 2, null, 1, 1));
    try std.testing.expectEqual(0, a.wait.address);
    try std.testing.expectEqual(8192, b.wait.address);
    try std.testing.expectEqual(4096, c.wait.address);
    try std.testing.expectEqual(1, b.wait.started);
    try std.testing.expectEqual(6, b.wait.deadline);
    try std.testing.expectEqual(77, b.frame.rax);
    try std.testing.expectEqual(0, wake(&contexts, 8192, 6, null, 1));
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -110))), b.frame.rax);
    try std.testing.expectEqual(5, b.frame.rdx);
    try std.testing.expectEqual(1, requeue(&contexts, 4096, 8192, 6, null, 0, 10));
    try std.testing.expectEqual(0, c.wait.deadline);
    try std.testing.expectEqual(1, wake(&contexts, 8192, 7, null, 1));
}

test "experimental signal CPU codec" {
    _ = @import("native_signal.zig");
    _ = @import("native_pending.zig");
}

test "image candidate resets old execution state without changing its source" {
    var source = Execution{
        .frame = .{ .rip = 0x201000, .rsp = 0x800c000, .rax = 91, .r12 = 73, .flags = 0x602 },
        .fs = 0x10001000,
        .clear_tid = 0x10002000,
        .tls_base = 0x10000000,
        .tls_bytes = 16384,
        .signal_mask = 1 << 11,
    };
    @memset(&source.fp, 0xa5);
    _ = source.wait.parkIndefinite(0x10003000, 7, 7, 1);
    const before = source;
    var candidate = source.forImage(0x401000, 0x800b000);
    try std.testing.expectEqualDeep(before, source);
    try std.testing.expectEqualDeep(Frame{ .rip = 0x401000, .rsp = 0x800b000, .cs = 0x23, .ss = 0x1b, .flags = 0x202 }, candidate.frame);
    try std.testing.expectEqual(source.signal_mask, candidate.signal_mask);
    try std.testing.expectEqual(@as(u64, 0), candidate.fs | candidate.tls_base | candidate.tls_bytes);
    try std.testing.expectEqual(@as(usize, 0), candidate.clear_tid);
    try std.testing.expectEqualDeep(Wait{}, candidate.wait);
    var expected_fp = [_]u8{0} ** 512;
    std.mem.writeInt(u16, expected_fp[0..2], 0x037f, .little);
    std.mem.writeInt(u32, expected_fp[24..28], 0x1f80, .little);
    try std.testing.expectEqualSlices(u8, &expected_fp, &candidate.fp);
    const repeated = candidate.forImage(0x501000, 0x800a000);
    try std.testing.expectEqual(source.signal_mask, repeated.signal_mask);
    try std.testing.expectEqualSlices(u8, &expected_fp, &repeated.fp);
    candidate.signal_mask = 0;
    candidate.fp[0] = 0;
    try std.testing.expectEqualDeep(before, source);
}

test "absolute wait validates before park and retains nanosecond epoch" {
    var wait: Wait = .{};
    try std.testing.expectEqual(-22, wait.parkAbsolute(4097, 0, 0, 10, 20));
    try std.testing.expectEqual(-22, wait.parkAbsolute(4096, 0, 0, 10, 1_000_000_011));
    try std.testing.expectEqual(-22, wait.parkAbsolute(4096, 0, 0, 10, std.math.maxInt(u64)));
    try std.testing.expectEqual(-11, wait.parkAbsolute(4096, 1, 0, 10, 9));
    try std.testing.expectEqual(-110, wait.parkAbsolute(4096, 0, 0, 10, 10));
    try std.testing.expectEqualDeep(Wait{}, wait);
    try std.testing.expectEqual(0, wait.parkAbsolute(4096, 0, 0, 10, 20));
    try std.testing.expectEqual(-16, wait.parkAbsolute(8192, 0, 0, 10, 20));
    try std.testing.expect(wait.completeAt(0, 99999, 19) == null);
    const expired = wait.completeAt(4096, 0, 20).?;
    try std.testing.expectEqual(-110, expired.status);
    try std.testing.expectEqual(10, expired.elapsed);
    try std.testing.expectEqualDeep(Wait{}, wait);
}

test "mixed clocks and requeue keep time domains and absolute deadlines" {
    var a: Execution = .{};
    var b: Execution = .{};
    const contexts = [_]*Execution{ &a, &b };
    _ = a.wait.park(4096, 0, 0, 1, 5);
    _ = b.wait.parkAbsolute(4096, 0, 0, 100, 200);
    try std.testing.expectEqual(1, requeue(&contexts, 4096, 8192, 2, 110, 0, 1));
    try std.testing.expectEqual(1, requeue(&contexts, 4096, 8192, 2, 110, 0, 1));
    try std.testing.expectEqual(200, b.wait.deadline);
    try std.testing.expect(b.wait.monotonic);
    try std.testing.expectEqual(0, wake(&contexts, 8192, 6, 200, 1));
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -110))), a.frame.rax);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -110))), b.frame.rax);
    try std.testing.expectEqual(5, a.frame.rdx);
    try std.testing.expectEqual(100, b.frame.rdx);
}

test "missing or regressing clock completes error rather than success or timeout" {
    var wait: Wait = .{};
    _ = wait.parkAbsolute(4096, 0, 0, 100, 200);
    try std.testing.expectEqual(-5, wait.completeAt(4096, 1, null).?.status);
    try std.testing.expectEqualDeep(Wait{}, wait);
    _ = wait.parkAbsolute(4096, 0, 0, 100, 200);
    try std.testing.expectEqual(-5, wait.completeAt(4096, 1, 99).?.status);
    _ = wait.parkAbsolute(4096, 0, 0, 100, 200);
    const done = wait.completeAt(4096, 999, 110).?;
    try std.testing.expectEqual(0, done.status);
    try std.testing.expectEqual(10, done.elapsed);
    var context: Execution = .{};
    _ = context.wait.parkAbsolute(4096, 0, 0, 100, 200);
    context.reset();
    try std.testing.expect(context.wait.completeAt(0, 1, 200) == null);
}
