// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
const planner = @import("../../boot_backing.zig");
const limine = @import("../../limine.zig");
const serial = @import("serial.zig");

pub const Mode = enum { reserve, overlap, corrupt, skip_clear, alias, alias_ro, alias_nx, alias_user, alias_detach, alias_skip_ro, alias_skip_nx, alias_skip_user, alias_skip_detach };
const bytes: u64 = 64 * 1024 * 1024;

// Isolated BSP boot experiment. No other allocator/user/AP/device is admitted;
// the chosen usable region remains exclusively reserved until VM teardown.
pub fn experiment(hhdm: u64, map: *const limine.MemoryResponse, pbase: u64, vbase: u64, mode: Mode) noreturn {
    if (map.count == 0 or map.count > planner.entry_limit) @panic("backing map count rejected");
    const source = map.entries orelse @panic("backing map entries absent");
    var entries: [planner.entry_limit]planner.Entry = undefined;
    const count: usize = @intCast(map.count);
    for (source[0..count], 0..) |entry, i| entries[i] = .{ .base = entry.base, .length = entry.length, .kind = entry.kind };
    if (mode == .overlap) {
        if (count < 2) @panic("backing overlap fixture needs two entries");
        entries[1] = entries[0];
    }
    const region = planner.select(entries[0..count], bytes) catch |err| switch (err) {
        error.Malformed => @panic("backing map malformed"),
        error.Exhausted => @panic("backing contiguous budget unavailable"),
    };
    const alias = planner.bootAlias(hhdm, region) catch @panic("backing boot alias rejected");
    if (@import("build_options").backing_alias) {
        const geometry = @import("backing_geometry.zig");
        const plan = geometry.Plan.init(region.physical, region.bytes, alias) catch @panic("backing native alias geometry rejected");
        const alias_mode = std.meta.stringToEnum(@import("backing_alias.zig").Mode, @tagName(mode)) orelse @panic("backing alias mode mismatch");
        @import("backing_alias.zig").start(plan, alias, pbase, vbase, alias_mode);
    }
    const backing: [*]u8 = @ptrFromInt(alias);
    // Controlled dirty backing makes omission of clearing observable. This is
    // our reserved usable memory only; no reclaimable/firmware bytes are touched.
    @memset(backing[0..bytes], 0xa5);
    if (mode != .skip_clear) @memset(backing[0..bytes], 0);
    if (mode == .corrupt) backing[bytes - 1] = 0xa5;
    const words: [*]const volatile u64 = @ptrFromInt(alias);
    for (0..bytes / 8) |i| if (words[i] != 0) @panic("backing region not zero");
    serial.write("AETHER BACKING RESERVATION PASS\n");
    while (true) asm volatile ("hlt");
}
