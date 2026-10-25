// SPDX-License-Identifier: BSD-2-Clause
// Raw source coherence only. Calendar interpretation and trust belong to userland.
const std = @import("std");
pub const Error = @import("native_clock.zig").Error || error{Busy};
pub const Observation = extern struct {
    version: u32 = 1,
    bytes: u32 = 64,
    source: u32 = 1,
    flags: u32 = 0,
    before: u64,
    after: u64,
    raw: [10]u8,
    reserved: [22]u8 = @splat(0),
};
comptime {
    std.debug.assert(@sizeOf(Observation) == 64 and @offsetOf(Observation, "raw") == 32);
}
const indices = [_]u8{ 0, 2, 4, 7, 8, 9, 0x32, 10, 11, 13 };
const budget = 2_000_000;

fn sample(reader: anytype) Error!?[10]u8 {
    const before = reader.read(10);
    if (before & 0x80 != 0) return null;
    var raw: [10]u8 = undefined;
    for (indices, &raw) |index, *value| value.* = reader.read(index);
    const after = reader.read(10);
    if (before != raw[7] or before != after or after & 0x80 != 0) return null;
    if (raw[7] & 0x70 != 0x20 or raw[8] & 0x80 != 0 or raw[9] & 0x80 == 0) return error.Unavailable;
    return raw;
}

pub fn observe(reader: anytype) Error!Observation {
    const start = try reader.now();
    var last = start;
    for (0..8) |_| {
        const first = try sample(reader);
        const second = try sample(reader);
        const end = try reader.now();
        if (end < last) return error.Regression;
        last = end;
        if (end - start > budget) return error.Busy;
        if (first != null and second != null and std.mem.eql(u8, &first.?, &second.?)) {
            return .{ .before = start, .after = end, .raw = second.? };
        }
    }
    return error.Busy;
}

const Fake = struct {
    raw: [10]u8 = .{ 0x12, 0x34, 0x15, 0x06, 0x10, 0x26, 0x20, 0x26, 0x02, 0x80 },
    reads: usize = 0,
    calls: u64 = 0,
    step: u64 = 100,
    mode: enum { stable, uip, rollover, mode_change, reg_change, clock_fail } = .stable,
    fn read(self: *@This(), index: u8) u8 {
        self.reads += 1;
        if (self.mode == .uip and index == 10) return 0xa6;
        for (indices, 0..) |value, i| if (value == index) {
            const half = (self.reads - 1) / 12;
            if (self.mode == .rollover and index == 0) return @truncate(half);
            if (self.mode == .mode_change and index == 11) return @as(u8, @truncate(half % 2)) << 2;
            if (self.mode == .reg_change and index == 10 and self.reads % 12 == 0) return 0xa6;
            return self.raw[i];
        };
        unreachable;
    }
    fn now(self: *@This()) Error!u64 {
        if (self.mode == .clock_fail) return error.Overflow;
        defer self.calls += 1;
        return 1000 + self.calls * self.step;
    }
};
test "raw modes are preserved and every reserved byte is initialized" {
    for ([_]u8{ 0, 2, 4, 6 }) |mode| {
        var reader: Fake = .{};
        reader.raw[8] = mode;
        const value = try observe(&reader);
        try std.testing.expectEqualSlices(u8, &reader.raw, &value.raw);
        try std.testing.expectEqualSlices(u8, &@as([22]u8, @splat(0)), &value.reserved);
        try std.testing.expectEqual(@as(u64, 1000), value.before);
        try std.testing.expectEqual(@as(u64, 1100), value.after);
        try std.testing.expectEqual(@as(usize, 24), reader.reads);
    }
}
test "unstable and updating hardware is bounded and never publishes a sample" {
    for ([_]@TypeOf(@as(Fake, .{}).mode){ .uip, .rollover, .mode_change, .reg_change }) |mode| {
        var reader: Fake = .{ .mode = mode };
        try std.testing.expectError(error.Busy, observe(&reader));
        try std.testing.expect(reader.reads <= 192);
        try std.testing.expectEqual(@as(u64, 9), reader.calls);
    }
}
test "invalid stopped or battery-invalid source rejects" {
    for ([_]usize{ 7, 8, 9 }) |field| {
        var reader: Fake = .{};
        reader.raw[field] = switch (field) {
            7 => 0x66,
            8 => 0x82,
            else => 0,
        };
        try std.testing.expectError(error.Unavailable, observe(&reader));
    }
}
test "elapsed budget and clock error never become valid calendar data" {
    var slow: Fake = .{ .step = budget + 1 };
    try std.testing.expectError(error.Busy, observe(&slow));
    var failed: Fake = .{ .mode = .clock_fail };
    try std.testing.expectError(error.Overflow, observe(&failed));
    try std.testing.expectEqual(@as(usize, 0), failed.reads);
}
