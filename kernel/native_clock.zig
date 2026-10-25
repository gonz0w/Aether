// SPDX-License-Identifier: BSD-2-Clause
// A source observation is elapsed counter time, never delivered interrupts or UTC.
const std = @import("std");

pub const Error = error{ Unavailable, Regression, Overflow };
pub const Clock = struct {
    period_fs: u32,
    origin: u64,
    last: u64,

    pub fn init(capabilities: u64, counter: u64) Error!Clock {
        const period: u32 = @truncate(capabilities >> 32);
        if (capabilities & (1 << 13) == 0 or period == 0 or period > 100_000_000)
            return error.Unavailable;
        return .{ .period_fs = period, .origin = counter, .last = counter };
    }

    pub fn observe(self: *Clock, counter: u64) Error!u64 {
        if (counter < self.last) return error.Regression;
        const ns = (@as(u128, counter - self.origin) * self.period_fs) / 1_000_000;
        if (ns > std.math.maxInt(i64)) return error.Overflow;
        self.last = counter;
        return @intCast(ns);
    }
};

// Reading high-low-high avoids torn MMIO reads on platforms splitting 64-bit loads.
pub fn sample(high_before: u32, low: u32, high_after: u32) ?u64 {
    if (high_before != high_after) return null;
    return (@as(u64, high_before) << 32) | low;
}

test "reported period and width must support a bounded clock" {
    for ([_]u64{ 0, @as(u64, 10_000_000) << 32, 1 << 13, (@as(u64, 100_000_001) << 32) | (1 << 13) }) |cap|
        try std.testing.expectError(error.Unavailable, Clock.init(cap, 0));
}

test "elapsed conversion retains subnanosecond remainder and original epoch" {
    var clock = try Clock.init((@as(u64, 1_500_000) << 32) | (1 << 13), 17);
    try std.testing.expectEqual(0, try clock.observe(17));
    try std.testing.expectEqual(1, try clock.observe(18));
    try std.testing.expectEqual(3, try clock.observe(19));
    try std.testing.expectEqual(6, try clock.observe(21));
    try std.testing.expectEqual(6, try clock.observe(21));
}

test "regression and full counter wrap leave last observation unchanged" {
    var clock = try Clock.init((@as(u64, 10_000_000) << 32) | (1 << 13), std.math.maxInt(u64) - 1);
    try std.testing.expectEqual(10, try clock.observe(std.math.maxInt(u64)));
    const saved = clock;
    try std.testing.expectError(error.Regression, clock.observe(0));
    try std.testing.expectEqualDeep(saved, clock);
}

test "signed nanosecond exhaustion rejects before publication" {
    var clock = try Clock.init((@as(u64, 10_000_000) << 32) | (1 << 13), 0);
    const boundary = @as(u64, std.math.maxInt(i64)) / 10;
    try std.testing.expectEqual(boundary * 10, try clock.observe(boundary));
    const saved = clock;
    try std.testing.expectError(error.Overflow, clock.observe(boundary + 1));
    try std.testing.expectEqualDeep(saved, clock);
}

test "split low-word rollover requires a fresh coherent sample" {
    try std.testing.expect(sample(1, 0, 2) == null);
    try std.testing.expectEqual(0x200000001, sample(2, 1, 2).?);
    try std.testing.expectEqual(std.math.maxInt(u64), sample(0xffffffff, 0xffffffff, 0xffffffff).?);
}
