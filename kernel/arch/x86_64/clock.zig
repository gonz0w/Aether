// SPDX-License-Identifier: BSD-2-Clause
// Opt-in q35 HPET reference. Mutable source/device state belongs only to the BSP.
const std = @import("std");
const clock = @import("../../native_clock.zig");
const Table = [512]u64;
pub const alias: u64 = 0xffffffff40000000;
const device: u64 = 0xfed00000;
const frame_mask: u64 = 0x000ffffffffff000;
var pd: Table align(4096) = @splat(0);
var pt: Table align(4096) = @splat(0);
var pd_physical: u64 = 0;
var source: ?clock.Clock = null;

fn barrier() void {
    asm volatile ("mfence" ::: .{ .memory = true });
}
fn reg(offset: usize) *volatile u32 {
    return @ptrFromInt(alias + offset);
}
fn counter() clock.Error!u64 {
    barrier();
    for (0..8) |_| {
        const high = reg(0xf4).*;
        const low = reg(0xf0).*;
        const after = reg(0xf4).*;
        if (clock.sample(high, low, after)) |value| return value;
    }
    return error.Unavailable;
}
fn tableAt(physical: u64, hhdm: u64, memory: *const @import("../../limine.zig").MemoryResponse) clock.Error!*Table {
    if (physical == 0 or physical % 4096 != 0 or memory.count == 0 or memory.count > 4096) return error.Unavailable;
    const entries = memory.entries orelse return error.Unavailable;
    for (entries[0..@intCast(memory.count)]) |entry| {
        if (entry.kind != 0 and entry.kind != 5) continue;
        if (physical >= entry.base and physical - entry.base <= entry.length and entry.length - (physical - entry.base) >= 4096) {
            const address = std.math.add(u64, hhdm, physical) catch return error.Unavailable;
            if (address < 0xffff800000000000 or address % 4096 != 0 or address > std.math.maxInt(u64) - 4095) return error.Unavailable;
            return @ptrFromInt(address);
        }
    }
    return error.Unavailable;
}

pub fn initialize(pbase: u64, vbase: u64, hhdm: u64, memory: *const @import("../../limine.zig").MemoryResponse) clock.Error!void {
    if (source != null) return error.Unavailable;
    const flags = asm volatile ("pushfq; popq %[v]"
        : [v] "=r" (-> u64),
    );
    if (flags & (1 << 9) != 0) return error.Unavailable;
    const efer = asm volatile ("rdmsr"
        : [low] "={eax}" (-> u32),
        : [index] "{ecx}" (@as(u32, 0xc0000080)),
        : .{ .edx = true });
    if (efer & (1 << 11) == 0 or pbase % 4096 != 0 or
        @intFromPtr(&pd) < vbase or @intFromPtr(&pt) < vbase) return error.Unavailable;

    // The fixed MMIO address is allowed only for this deliberate q35 experiment.
    asm volatile ("outl %[v], %[p]"
        :
        : [v] "{eax}" (@as(u32, 0x80000000)),
          [p] "{dx}" (@as(u16, 0xcf8)),
    );
    const bridge = asm volatile ("inl %[p], %[v]"
        : [v] "={eax}" (-> u32),
        : [p] "{dx}" (@as(u16, 0xcfc)),
    );
    if (bridge != 0x29c08086) return error.Unavailable;
    pd_physical = std.math.add(u64, pbase, @intFromPtr(&pd) - vbase) catch return error.Unavailable;
    const pt_physical = std.math.add(u64, pbase, @intFromPtr(&pt) - vbase) catch return error.Unavailable;
    pd[0] = pt_physical | 3;
    pt[0] = device | 27 | (@as(u64, 1) << 63); // Supervisor RW/NX, PWT+PCD.
    const cr3 = asm volatile ("mov %%cr3, %[v]"
        : [v] "=r" (-> u64),
    );
    const root = try tableAt(cr3 & frame_mask, hhdm, memory);
    if (root[511] & 1 == 0) return error.Unavailable;
    const high = try tableAt(root[511] & frame_mask, hhdm, memory);
    if (high[509] != 0) return error.Unavailable;
    high[509] = pd_physical | 3;
    asm volatile ("invlpg (%[p])"
        :
        : [p] "r" (alias),
        : .{ .memory = true });
    barrier();
    const capabilities = (@as(u64, reg(4).*) << 32) | reg(0).*;
    var candidate = try clock.Clock.init(capabilities, 0);
    if (candidate.period_fs != 10_000_000 or reg(0x10).* != 0 or reg(0x14).* != 0) return error.Unavailable;
    const timers = ((capabilities >> 8) & 31) + 1;
    for (0..@intCast(timers)) |i| if (reg(0x100 + i * 0x20).* & ((1 << 2) | (1 << 14)) != 0) return error.Unavailable;
    // Claim only the stopped source, not comparators or legacy PIT/RTC routes.
    reg(0x10).* = 1;
    barrier();
    const origin = try counter();
    candidate = try clock.Clock.init(capabilities, origin);
    for (0..100_000) |_| {
        if (try candidate.observe(try counter()) > 0) {
            source = candidate;
            return;
        }
    }
    return error.Unavailable;
}

// Each native root receives only a supervisor device alias. Bootstrap fixes the
// table frame/permission bindings; hardware may update Accessed flags.
// No user receives MMIO or adjustment authority.
pub fn attach(high: *Table) void {
    const accessed: u64 = 1 << 5;
    const expected = pd_physical | 3;
    const previous = high[509];
    // Reattachment may follow translations through this root. Only the CPU's
    // Accessed bit may differ; the frame and every other flag must stay exact.
    std.debug.assert(source != null and (previous == 0 or previous & ~accessed == expected));
    high[509] = expected | (previous & accessed);
}

// Caller serializes observations with IF=0. Device stop/reset is not time zero.
pub fn read() clock.Error!u64 {
    const current = if (source) |*value| value else return error.Unavailable;
    if (reg(0x10).* != 1 or reg(0x14).* != 0) return error.Unavailable;
    return current.observe(try counter());
}
