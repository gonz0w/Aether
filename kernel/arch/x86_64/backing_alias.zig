// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
const geometry = @import("backing_geometry.zig");
const serial = @import("serial.zig");
const Frame = @import("context.zig").Frame;
const Table = [512]u64;
const nx: u64 = 1 << 63;
const kernel_base: u64 = 0xffffffff80000000;
extern const kernel_start: u8;
extern const kernel_end: u8;
extern const text_start: u8;
extern const text_end: u8;
extern const rodata_start: u8;
extern const rodata_end: u8;
extern fn restore_context(u64, *const Frame) callconv(.c) noreturn;

pub const Mode = enum { alias, alias_ro, alias_nx, alias_user, alias_detach, alias_skip_ro, alias_skip_nx, alias_skip_user, alias_skip_detach };
var roots: [2]Table align(4096) = @splat(@splat(0));
var kernel_pdpt: Table align(4096) = @splat(0);
var kernel_pd: Table align(4096) = @splat(0);
var kernel_pts: [8]Table align(4096) = @splat(@splat(0));
// One BSP owner; both roots reference the same kernel-only alias tables.
var pool: @import("backing_pool.zig").Pool = .{};
var user_pdpt: Table align(4096) = @splat(0);
var user_pd: Table align(4096) = @splat(0);
var code_pt: Table align(4096) = @splat(0);
var stack_pt: Table align(4096) = @splat(0);
var code: [4096]u8 align(4096) = @splat(0);
var user_stack: [4096]u8 align(4096) = @splat(0);
var kernel_stack: [16384]u8 align(16) = undefined;
var frame: Frame = .{};
var reservation: geometry.Plan = undefined;
var physical_base: u64 = 0;
var selected: Mode = .alias;
var expected_error: u64 = 0;
var expected_cpl: u64 = 0;
var expecting_fault = false;

fn require(ok: bool) void {
    if (!ok) @panic("backing alias invariant failed");
}
fn phys(pointer: anytype) u64 {
    const address = @intFromPtr(pointer);
    require(address >= kernel_base and address < @intFromPtr(&kernel_end));
    return physical_base + (address - kernel_base);
}
fn reload(root: usize) void {
    require(root < roots.len);
    asm volatile ("mov %[value], %%cr3"
        :
        : [value] "r" (phys(&roots[root])),
        : .{ .memory = true });
}
fn current(root: usize) void {
    const cr3 = asm volatile ("mov %%cr3, %[value]"
        : [value] "=r" (-> u64),
    );
    require(cr3 == phys(&roots[root]));
}
fn clear(backing: [*]u8) void {
    @memset(backing[0..geometry.bytes], 0);
    const words: [*]const volatile u64 = @ptrCast(@alignCast(backing));
    for (0..geometry.bytes / 8) |i| require(words[i] == 0);
}
fn writePattern(first: u8, last: u8) void {
    const backing: [*]volatile u8 = @ptrFromInt(geometry.base);
    backing[0] = first;
    backing[geometry.bytes - 1] = last;
}
fn checkPattern(first: u8, last: u8) void {
    const backing: [*]const volatile u8 = @ptrFromInt(geometry.base);
    require(backing[0] == first and backing[geometry.bytes - 1] == last);
}
fn userMode() bool {
    return selected == .alias_user or selected == .alias_skip_user;
}

// Called only after boot reservation and alias geometry preflight, before any
// AP/device/service/allocator. Every object needed after CR3 lives in this image.
pub fn start(plan: geometry.Plan, boot_alias: usize, pbase: u64, vbase: u64, mode: Mode) noreturn {
    asm volatile ("cli" ::: .{ .memory = true });
    const image_end = @intFromPtr(&kernel_end);
    require(vbase == kernel_base and @intFromPtr(&kernel_start) == kernel_base and image_end > kernel_base and
        image_end - kernel_base <= kernel_pts.len * 2 * 1024 * 1024 and pbase % 4096 == 0 and
        pbase < 1 << 32 and image_end - kernel_base <= (1 << 32) - pbase);
    require(plan.physical + geometry.bytes <= pbase or pbase + (image_end - kernel_base) <= plan.physical);
    const cr0 = asm volatile ("mov %%cr0, %[value]"
        : [value] "=r" (-> u64),
    );
    const cr4 = asm volatile ("mov %%cr4, %[value]"
        : [value] "=r" (-> u64),
    );
    const efer = asm volatile ("rdmsr"
        : [low] "={eax}" (-> u32),
        : [index] "{ecx}" (@as(u32, 0xc0000080)),
        : .{ .edx = true });
    require(cr0 & (1 << 16) != 0 and efer & (1 << 11) != 0 and cr4 & ((1 << 12) | (1 << 17)) == 0);
    // Drop any global translations inherited from firmware/boot HHDM. All new
    // leaves omit G; PCID is prohibited and each later switch/reload flushes.
    asm volatile ("mov %[value], %%cr4"
        :
        : [value] "r" (cr4 & ~@as(u64, 1 << 7)),
        : .{ .memory = true });
    reservation = plan;
    selected = mode;
    physical_base = pbase;
    @import("protection.zig").tables();
    kernel_pdpt[510] = phys(&kernel_pd) | 3;
    for (&kernel_pts, 0..) |*pt, i| kernel_pd[i] = phys(pt) | 3;
    var address = kernel_base;
    while (address < image_end) : (address += 4096) {
        const index = (address - kernel_base) / 4096;
        const flags: u64 = if (address >= @intFromPtr(&text_start) and address < @intFromPtr(&text_end))
            1
        else if (address >= @intFromPtr(&rodata_start) and address < @intFromPtr(&rodata_end))
            1 | nx
        else
            3 | nx;
        kernel_pts[index / 512][index % 512] = pbase + (address - kernel_base) | flags;
    }
    pool.initialize(plan, pbase);
    for (&roots) |*root| {
        root[511] = phys(&kernel_pdpt) | 3;
        pool.attach(root, pbase);
    }
    if (mode == .alias_skip_user) {
        for (&roots) |*root| root[geometry.base >> 39 & 511] |= 4;
        pool.pdpt[0] |= 4;
        for (pool.pd[0..geometry.leaves]) |*entry| entry.* |= 4;
        for (&pool.pts) |*pt| for (pt) |*entry| {
            entry.* |= 4;
        };
    }
    if (userMode()) {
        // MOVABS alias,%rax; MOVZX (%rax),%eax; INT 0x80. The last operation
        // proves a deliberately exposed alias was read, instead of accepting UD.
        const instructions = [_]u8{ 0x48, 0xb8, 0, 0, 0, 0, 0, 0, 0, 0, 0x0f, 0xb6, 0x00, 0xcd, 0x80 };
        @memcpy(code[0..instructions.len], &instructions);
        std.mem.writeInt(u64, code[2..10], geometry.base, .little);
        roots[1][0] = phys(&user_pdpt) | 7;
        user_pdpt[0] = phys(&user_pd) | 7;
        user_pd[2] = phys(&code_pt) | 7;
        user_pd[4] = phys(&stack_pt) | 7;
        code_pt[0] = phys(&code) | 5;
        stack_pt[0] = phys(&user_stack) | 7 | nx;
        const index = (@intFromPtr(&code) - kernel_base) / 4096;
        kernel_pts[index / 512][index % 512] = phys(&code) | 1 | nx;
    }
    const backing: [*]u8 = @ptrFromInt(boot_alias);
    @memset(backing[0..geometry.bytes], 0xa5);
    clear(backing);
    frame = .{ .rip = @intFromPtr(&entered), .cs = 8, .ss = 16, .rsp = @intFromPtr(&kernel_stack) + kernel_stack.len - 8, .flags = 2 };
    restore_context(phys(&roots[0]), &frame);
}

fn fault(error_code: u64, cpl: u64) void {
    expected_error = error_code;
    expected_cpl = cpl;
    expecting_fault = true;
}
fn entered() callconv(.c) noreturn {
    current(0);
    for (0..geometry.pages) |i| {
        const flags: u64 = if (selected == .alias_skip_user) 7 else 3;
        require(pool.pts[i / 512][i % 512] == (reservation.frame(i) catch unreachable) | flags | nx);
    }
    require(roots[0][geometry.base >> 39 & 511] == roots[1][geometry.base >> 39 & 511]);
    writePattern(0xc3, 0x5a);
    reload(1);
    current(1);
    checkPattern(0xc3, 0x5a);
    // Both roots share the authoritative alias PTE. No other CPU/context runs.
    if (selected != .alias_skip_ro) pool.pts[0][0] &= ~@as(u64, 2);
    if (selected == .alias_skip_nx) pool.pts[0][0] &= ~nx;
    reload(1);
    if (selected == .alias_ro or selected == .alias_skip_ro) {
        fault(3, 0);
        const target: *volatile u8 = @ptrFromInt(geometry.base);
        target.* = 0xa5;
        @panic("backing readonly alias remained writable");
    }
    if (selected == .alias_nx or selected == .alias_skip_nx) {
        fault(17, 0);
        const target: *const fn () callconv(.c) void = @ptrFromInt(geometry.base);
        target();
        @panic("backing NX alias executed");
    }
    if (userMode()) {
        fault(5, 3);
        frame = .{ .rip = 0x400000, .cs = 0x23, .ss = 0x1b, .rsp = 0x800ff8, .flags = 2 };
        restore_context(phys(&roots[1]), &frame);
    }
    if (selected != .alias_skip_detach) pool.pts[0][0] = 0;
    reload(1);
    if (selected == .alias_detach or selected == .alias_skip_detach) {
        fault(0, 0);
        const target: *const volatile u8 = @ptrFromInt(geometry.base);
        _ = target.*;
        @panic("backing detached alias remained");
    }
    // Translation detached before write restoration and reuse. Zero the entire
    // retained region before publishing a second pattern through either root.
    require(pool.pts[0][0] == 0);
    pool.pts[0][0] = (reservation.frame(0) catch unreachable) | 3 | nx;
    reload(1);
    const backing: [*]u8 = @ptrFromInt(geometry.base);
    clear(backing);
    reload(0);
    current(0);
    writePattern(0x37, 0x91);
    reload(1);
    current(1);
    checkPattern(0x37, 0x91);
    clear(backing);
    serial.write("AETHER BACKING ALIAS PASS\n");
    serial.halt();
}

pub fn exception(f: *const Frame) *const Frame {
    if (selected == .alias_skip_user and f.vector == 128 and f.cs == 0x23 and f.rax == 0xc3)
        @panic("backing supervisor alias exposed");
    const address = asm volatile ("mov %%cr2, %[value]"
        : [value] "=r" (-> u64),
    );
    if (!expecting_fault or f.vector != 14 or f.error_code != expected_error or
        f.cs & 3 != expected_cpl or address != geometry.base or
        (selected == .alias_nx and f.rip != geometry.base) or
        (selected == .alias_user and f.rip != 0x40000a))
        @panic("backing alias fault mismatch");
    var note: [160]u8 = undefined;
    serial.write(std.fmt.bufPrint(&note, "BACKING alias fault vector={d} error={d} cpl={d} address={x}\n", .{ f.vector, f.error_code, f.cs & 3, address }) catch unreachable);
    serial.write("AETHER BACKING ALIAS FAULT PASS\n");
    serial.halt();
}
