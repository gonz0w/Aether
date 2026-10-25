// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");

pub const Entry = struct { base: u64, length: u64, kind: u64 };
pub const Region = struct { physical: u64, bytes: u64 };
pub const Error = error{ Malformed, Exhausted };
pub const entry_limit = 128;
const page: u64 = 4096;
const low: u64 = 1024 * 1024;
const high: u64 = 1 << 32;

// Pure boot reservation plan: no map entry, byte or allocator state is mutated.
// Validate every range, including reserved/unknown kinds, before choosing usable
// memory. A single BSP caller must retain the returned region exclusively.
pub fn select(entries: []const Entry, bytes: u64) Error!Region {
    if (entries.len == 0 or entries.len > entry_limit or bytes == 0 or bytes % page != 0) return error.Malformed;
    for (entries, 0..) |entry, i| {
        if (entry.length == 0) return error.Malformed;
        const end = std.math.add(u64, entry.base, entry.length) catch return error.Malformed;
        for (entries[0..i]) |previous| {
            const previous_end = std.math.add(u64, previous.base, previous.length) catch return error.Malformed;
            if (entry.base < previous_end and previous.base < end) return error.Malformed;
        }
    }
    for (entries) |entry| {
        if (entry.kind != 0) continue;
        const end = @min(high, entry.base + entry.length);
        const start = @max(low, entry.base);
        const rounded = std.math.add(u64, start, page - 1) catch continue;
        const base = rounded & ~(page - 1);
        if (base >= end or bytes > end - base) continue;
        return .{ .physical = base, .bytes = bytes };
    }
    return error.Exhausted;
}

// Only the initial Limine HHDM is used by the isolated probe. Native roots must
// later install their own supervisor RW/NX aliases; this is not that binding.
pub fn bootAlias(offset: u64, region: Region) Error!usize {
    if (offset < 0xffff800000000000 or offset % page != 0 or region.physical < low or region.physical % page != 0 or
        region.bytes == 0 or region.bytes % page != 0 or region.physical >= high or
        region.bytes > high - region.physical) return error.Malformed;
    const start = std.math.add(u64, offset, region.physical) catch return error.Malformed;
    const end = std.math.add(u64, start, region.bytes) catch return error.Malformed;
    // Canonical upper-half HHDM, separate from the kernel-image alias window.
    if (start < 0xffff800000000000 or end > 0xffffffff80000000) return error.Malformed;
    return @intCast(start);
}

test "exact reservation and page rounding exclude reserved low and high memory" {
    const size = 64 * 1024 * 1024;
    const entries = [_]Entry{
        .{ .base = 0, .length = low, .kind = 1 },
        .{ .base = low, .length = size, .kind = 0 },
        .{ .base = high, .length = size, .kind = 0 },
    };
    const before = entries;
    try std.testing.expectEqualDeep(Region{ .physical = low, .bytes = size }, try select(&entries, size));
    try std.testing.expectEqualDeep(before, entries);
    try std.testing.expectError(error.Exhausted, select(&entries, size + page));
    try std.testing.expectError(error.Exhausted, select(&entries, std.math.maxInt(u64) & ~(page - 1)));
    const unaligned = [_]Entry{.{ .base = low + 1, .length = size + page - 1, .kind = 0 }};
    try std.testing.expectEqual(low + page, (try select(&unaligned, size)).physical);
    try std.testing.expectError(error.Exhausted, select(&unaligned, size + page));
    const excluded = [_]Entry{ .{ .base = 0, .length = low, .kind = 0 }, .{ .base = low, .length = size, .kind = 99 }, .{ .base = high, .length = size, .kind = 0 } };
    try std.testing.expectError(error.Exhausted, select(&excluded, page));
}

test "malformed complete map rejects before selecting otherwise valid space" {
    const valid = Entry{ .base = low, .length = 64 * 1024 * 1024, .kind = 0 };
    for ([_]Entry{
        .{ .base = low, .length = page, .kind = 1 },
        .{ .base = low + valid.length - 1, .length = page, .kind = 99 },
        .{ .base = std.math.maxInt(u64) - page, .length = 2 * page, .kind = 1 },
        .{ .base = high, .length = 0, .kind = 0 },
    }) |bad| {
        const entries = [_]Entry{ valid, bad };
        const before = entries;
        try std.testing.expectError(error.Malformed, select(&entries, page));
        try std.testing.expectEqualDeep(before, entries);
    }
    try std.testing.expectError(error.Malformed, select(&.{}, page));
    const oversized = [_]Entry{valid} ** (entry_limit + 1);
    try std.testing.expectError(error.Malformed, select(&oversized, page));
    for ([_]u64{ 0, 1, page + 1, std.math.maxInt(u64) }) |bytes|
        try std.testing.expectError(error.Malformed, select(&.{valid}, bytes));
}

test "boot alias is canonical, bounded and cannot enter the kernel window" {
    const region = Region{ .physical = low, .bytes = 64 * 1024 * 1024 };
    try std.testing.expectEqual(@as(usize, 0xffff800000100000), try bootAlias(0xffff800000000000, region));
    for ([_]u64{ 0, 1, 0xffff7ffffffff000, 0xffffffff80000000, 0xfffffffffffff000 }) |offset|
        try std.testing.expectError(error.Malformed, bootAlias(offset, region));
    for ([_]Region{
        .{ .physical = 0, .bytes = page },
        .{ .physical = low + 1, .bytes = page },
        .{ .physical = low, .bytes = 0 },
        .{ .physical = low, .bytes = page + 1 },
        .{ .physical = high, .bytes = page },
        .{ .physical = high - page, .bytes = 2 * page },
    }) |bad| try std.testing.expectError(error.Malformed, bootAlias(0xffff800000000000, bad));
}
