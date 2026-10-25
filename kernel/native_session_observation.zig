// SPDX-License-Identifier: BSD-2-Clause
//! Inert private fixture record. Caller authority and cleanup are checked by the
//! native runtime before emitting; returned slices borrow the copied record.
const std = @import("std");
pub const size = 176;
pub const Record = struct { stdout: []const u8, stderr: []const u8, copies: u32, execs: u32 };
pub fn parse(raw: *const [size]u8) error{Invalid}!Record {
    const out = std.mem.readInt(u32, raw[0..4], .little);
    const err = std.mem.readInt(u32, raw[4..8], .little);
    const copies = std.mem.readInt(u32, raw[8..12], .little);
    const execs = std.mem.readInt(u32, raw[12..16], .little);
    if (out > 128 or err > 32 or copies > 9 or execs > copies) return error.Invalid;
    for (raw[16 + out .. 144]) |b| if (b != 0) return error.Invalid;
    for (raw[144 + err ..]) |b| if (b != 0) return error.Invalid;
    return .{ .stdout = raw[16..][0..out], .stderr = raw[144..][0..err], .copies = copies, .execs = execs };
}
test "observation preserves separated bytes including marker-shaped input" {
    var raw = [_]u8{0} ** size;
    const text = "NATIVE SESSION\n\x00";
    std.mem.writeInt(u32, raw[0..4], text.len, .little);
    raw[4] = 3;
    raw[8] = 9;
    raw[12] = 7;
    @memcpy(raw[16..][0..text.len], text);
    @memcpy(raw[144..][0..3], "err");
    const r = try parse(&raw);
    try std.testing.expectEqualSlices(u8, text, r.stdout);
    try std.testing.expectEqualSlices(u8, "err", r.stderr);
    try std.testing.expectEqual(@as(u32, 9), r.copies);
}
test "observation rejects hidden bytes counts and lengths" {
    for ([_]struct { at: usize, value: u32 }{ .{ .at = 0, .value = 129 }, .{ .at = 4, .value = 33 }, .{ .at = 8, .value = 10 }, .{ .at = 12, .value = 1 }, .{ .at = 0, .value = 0xffffffff } }) |bad| {
        var raw = [_]u8{0} ** size;
        std.mem.writeInt(u32, raw[bad.at..][0..4], bad.value, .little);
        try std.testing.expectError(error.Invalid, parse(&raw));
    }
    for (16..size) |at| {
        var raw = [_]u8{0} ** size;
        raw[at] = 1;
        try std.testing.expectError(error.Invalid, parse(&raw));
    }
}

// Fixture completion only: the caller separately enforces empty worker/channel
// ownership. Each observation has already checked its actual reclaim delta.
pub fn finished(observations: u8, reported: usize, reclaimed: usize) bool {
    return switch (observations) {
        0 => reported == 0 and reclaimed == 30, // unchanged resource-only probe
        3 => reported >= 3 and reported <= 30 and reclaimed == reported,
        else => false,
    };
}
test "completion requires three reconciled observations or legacy resource total" {
    try std.testing.expect(finished(0, 0, 30));
    try std.testing.expect(finished(3, 24, 24));
    try std.testing.expect(finished(3, 30, 30));
    for ([_][3]usize{ .{ 0, 0, 24 }, .{ 0, 1, 30 }, .{ 1, 8, 8 }, .{ 2, 16, 16 }, .{ 3, 24, 23 }, .{ 3, 24, 25 }, .{ 3, 0, 0 }, .{ 3, 31, 31 }, .{ 4, 24, 24 } }) |v| {
        try std.testing.expect(!finished(@intCast(v[0]), v[1], v[2]));
    }
}
