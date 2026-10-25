// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");

pub const page: u64 = 4096;
pub const bytes: u64 = 64 * 1024 * 1024;
pub const base: u64 = 0xffff900000000000;
pub const pages: usize = bytes / page;
pub const leaves: usize = pages / 512;
pub const Error = error{Invalid};

// Internal x86 alias geometry only. The boot owner separately proves exclusive
// usable-RAM reservation. A physical address or this plan conveys no authority.
pub const Plan = struct {
    physical: u64,
    pub fn init(physical: u64, size: u64, boot_alias: u64) Error!Plan {
        if (physical < 1024 * 1024 or physical % page != 0 or size != bytes or
            physical >= 1 << 32 or size > (1 << 32) - physical or
            boot_alias < 0xffff800000000000 or boot_alias % page != 0)
            return error.Invalid;
        const stop = std.math.add(u64, boot_alias, size) catch return error.Invalid;
        if (stop > 0xffffffff80000000 or (boot_alias < base + bytes and base < stop))
            return error.Invalid;
        return .{ .physical = physical };
    }
    pub fn frame(self: Plan, index: usize) Error!u64 {
        if (index >= pages) return error.Invalid;
        return self.physical + index * page;
    }
    pub fn slot(address: u64) Error!usize {
        if (address < base or address >= base + bytes or address % page != 0) return error.Invalid;
        return @intCast((address - base) / page);
    }
};

comptime {
    if (base % (2 * 1024 * 1024) != 0 or (base >> 39) & 511 == 511 or
        (base >> 30) & 511 != 0 or (base >> 21) & 511 != 0 or leaves != 32)
        @compileError("private backing alias geometry mismatch");
}

test "reserved-frame translation covers first last and rejects out of bounds" {
    const p = try Plan.init(0x123000, bytes, 0xffff800000123000);
    try std.testing.expectEqual(@as(u64, 0x123000), try p.frame(0));
    try std.testing.expectEqual(@as(u64, 0x123000 + bytes - page), try p.frame(pages - 1));
    try std.testing.expectError(error.Invalid, p.frame(pages));
    try std.testing.expectError(error.Invalid, p.frame(std.math.maxInt(usize)));
    try std.testing.expectEqual(@as(usize, 0), try Plan.slot(base));
    try std.testing.expectEqual(pages - 1, try Plan.slot(base + bytes - page));
    for ([_]u64{ base - page, base + 1, base + bytes, std.math.maxInt(u64) }) |address|
        try std.testing.expectError(error.Invalid, Plan.slot(address));
}

test "alias preflight rejects wrap alignment reserved and alternate window overlap" {
    for ([_]u64{ 0, 0x123001, (1 << 32) - page, 1 << 32, std.math.maxInt(u64) }) |physical|
        try std.testing.expectError(error.Invalid, Plan.init(physical, bytes, 0xffff800000123000));
    for ([_]u64{ 0, page, bytes - page, bytes + page, std.math.maxInt(u64) }) |size|
        try std.testing.expectError(error.Invalid, Plan.init(0x123000, size, 0xffff800000123000));
    for ([_]u64{ 0, 0xffff7ffffffff000, 0xffff800000000001, base - bytes + page, base, base + bytes - page, 0xffffffff80000000, 0xfffffffffffff000 }) |alias|
        try std.testing.expectError(error.Invalid, Plan.init(0x123000, bytes, alias));
    _ = try Plan.init(0x123000, bytes, base - bytes);
    _ = try Plan.init(0x123000, bytes, base + bytes);
}
