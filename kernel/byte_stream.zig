const std = @import("std");
pub const Stream = struct {
    bytes: [32]u8 = @splat(0),
    head: usize = 0,
    count: usize = 0,
    sealed: bool = false,
    reader_closed: bool = false,
    pub fn push(s: *Stream, value: u8) i64 {
        if (s.reader_closed or s.sealed) return -32;
        if (s.count == s.bytes.len) return -11;
        s.bytes[(s.head + s.count) % s.bytes.len] = value;
        s.count += 1;
        return 0;
    }
    pub fn pop(s: *Stream) i64 {
        if (s.reader_closed) return -9;
        if (s.count == 0) return if (s.sealed) 256 else -11;
        const value = s.bytes[s.head];
        s.bytes[s.head] = 0;
        s.head = (s.head + 1) % s.bytes.len;
        s.count -= 1;
        return value;
    }
};
test "stream preserves order under backpressure, wrap and sealed drain" {
    var s: Stream = .{};
    try std.testing.expectEqual(-11, s.pop());
    for (0..32) |i| try std.testing.expectEqual(0, s.push(@intCast(i)));
    try std.testing.expectEqual(-11, s.push(99));
    for (0..16) |i| try std.testing.expectEqual(@as(i64, @intCast(i)), s.pop());
    for (32..48) |i| try std.testing.expectEqual(0, s.push(@intCast(i)));
    s.sealed = true;
    try std.testing.expectEqual(-32, s.push(0));
    for (16..48) |i| try std.testing.expectEqual(@as(i64, @intCast(i)), s.pop());
    try std.testing.expectEqual(256, s.pop());
    s.reader_closed = true;
    try std.testing.expectEqual(-9, s.pop());
    try std.testing.expectEqual(-32, s.push(1));
}
