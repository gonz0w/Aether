// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
const Stream = @import("byte_stream.zig").Stream;

// Admission preflight only. The local kernel must keep interrupts disabled
// through validation, image load and transfer; these pointers are never retained.
pub fn connectionPair(channels: []Channel, owner: usize, reader: u64, writer: u64) ?struct { request: *Channel, reply: *Channel } {
    var request: ?*Channel = null;
    var reply: ?*Channel = null;
    for (channels) |*c| {
        if (c.lookup(owner, reader) == 0) request = c;
        if (c.lookup(owner, writer) == 1) reply = c;
    }
    const a = request orelse return null;
    const b = reply orelse return null;
    if (a == b) return null;
    for ([_]*Channel{ a, b }) |c| {
        if (c.owners[0] != owner or c.owners[1] != owner or
            c.stream.count != 0 or c.stream.sealed or c.stream.reader_closed) return null;
    }
    return .{ .request = a, .reply = b };
}

pub const Channel = struct {
    identity: u64 = 0,
    sustained: bool = false,
    stream: Stream = .{},
    generation: u64 = 0,
    owners: [2]?usize = .{ null, null },
    pub fn cap(c: *const Channel, end: usize) u64 {
        if (c.sustained) return @import("native_sustained.zig").identity(if (end == 0) .reader else .writer, @intCast(c.identity), @intCast(c.generation)) catch unreachable;
        return 0xd1000000 | (c.identity << 16) | (c.generation << 8) | (end + 1);
    }
    pub fn lookup(c: *const Channel, owner: usize, value: u64) ?usize {
        for (c.owners, 0..) |holder, i| if (holder != null and holder.? == owner and value == c.cap(i)) return i;
        return null;
    }
    // A hint only: closure must wake the holder to observe EOF/EPIPE itself.
    pub fn waitStatus(c: *const Channel, owner: usize, value: u64) ?i64 {
        const end = c.lookup(owner, value) orelse return -13;
        const ready = if (end == 0) c.stream.count != 0 or c.stream.sealed else c.stream.count < c.stream.bytes.len or c.stream.reader_closed;
        return if (ready) 0 else null;
    }
    pub fn create(c: *Channel, owner: usize) i64 {
        if (c.sustained) return -22;
        return c.createBounded(owner, 3);
    }
    // Kernel-profile selection only; no wire request may choose its lifetime cap.
    // Not reachable from native admission until the session profile is enabled.
    pub fn createSession(c: *Channel, owner: usize) i64 {
        if (c.sustained) return -22;
        return c.createBounded(owner, 15);
    }
    pub fn createSustained(c: *Channel, owner: usize) i64 {
        if (!c.sustained) return -22;
        return c.createBounded(owner, @import("native_sustained.zig").generation_limit);
    }
    fn createBounded(c: *Channel, owner: usize, comptime limit: u64) i64 {
        if (c.owners[0] != null or c.owners[1] != null) return -16;
        if (c.generation >= limit) return -28;
        c.generation += 1;
        c.stream = .{};
        c.owners = .{ owner, owner };
        return @intCast(c.cap(0));
    }
    pub fn transfer(c: *Channel, owner: usize, value: u64, child: usize) bool {
        const end = c.lookup(owner, value) orelse return false;
        c.owners[end] = child;
        return true;
    }
    pub fn close(c: *Channel, owner: usize, value: u64) i64 {
        const end = c.lookup(owner, value) orelse return -13;
        c.owners[end] = null;
        if (end == 0) c.stream.reader_closed = true else c.stream.sealed = true;
        if (c.owners[0] == null and c.owners[1] == null) c.stream = .{};
        return 0;
    }
    pub fn closeOwner(c: *Channel, owner: usize) void {
        for (0..2) |i| if (c.owners[i] == owner) {
            _ = c.close(owner, c.cap(i));
        };
    }
};
// One single-context domain registration. The kernel serializes begin/poll with
// channel ownership and stream mutation; no pointer or borrowed grant is stored.
pub const Wait = struct {
    endpoint: u64 = 0,
    pub fn begin(w: *Wait, c: *const Channel, owner: usize, value: u64, interrupted: bool) ?i64 {
        if (w.endpoint != 0) return -16;
        const status = c.waitStatus(owner, value);
        if (status == -13) return -13;
        if (interrupted) return -4;
        if (status) |ready| return ready;
        w.endpoint = value;
        return null;
    }
    pub fn poll(w: *Wait, c: ?*const Channel, owner: usize, interrupted: bool) ?i64 {
        if (w.endpoint == 0) return null;
        const status = if (c) |channel| channel.waitStatus(owner, w.endpoint) else @as(?i64, -13);
        const done = if (status == -13) @as(?i64, -13) else if (interrupted) @as(?i64, -4) else status;
        if (done != null) w.endpoint = 0;
        return done;
    }
};
test "channel transfer, last close, zeroing and generation retirement" {
    var c: Channel = .{};
    const read: u64 = @intCast(c.create(2));
    const write = c.cap(1);
    try std.testing.expectEqual(-16, c.create(2));
    try std.testing.expect(!c.transfer(0, read, 1));
    try std.testing.expect(c.transfer(2, write, 0));
    try std.testing.expect(c.lookup(2, write) == null);
    try std.testing.expectEqual(0, c.stream.push(42));
    c.closeOwner(0);
    try std.testing.expectEqual(42, c.stream.pop());
    try std.testing.expectEqual(256, c.stream.pop());
    try std.testing.expectEqual(0, c.close(2, read));
    for (c.stream.bytes) |v| try std.testing.expectEqual(0, v);
    _ = c.create(2);
    try std.testing.expect(c.lookup(2, read) == null);
    try std.testing.expectEqual(-13, c.close(2, write));
    _ = c.stream.push(99);
    c.closeOwner(2);
    for (c.stream.bytes) |v| try std.testing.expectEqual(0, v);
    _ = c.create(2);
    c.closeOwner(2);
    try std.testing.expectEqual(-28, c.create(2));
}

test "equal generations in distinct channel slots cannot substitute grants" {
    var request: Channel = .{};
    var reply: Channel = .{ .identity = 1 };
    const a: u64 = @intCast(request.create(2));
    const b: u64 = @intCast(reply.create(2));
    try std.testing.expect(a != b);
    try std.testing.expect(request.lookup(2, b) == null and reply.lookup(2, a) == null);
    try std.testing.expect(!reply.transfer(2, a, 0));
    try std.testing.expectEqual(-13, request.close(2, b));
    try std.testing.expect(request.lookup(2, a) != null and reply.lookup(2, b) != null);
}

test "four channel identities retain independent holder and generation scope" {
    var channels: [4]Channel = .{ .{}, .{ .identity = 1 }, .{ .identity = 2 }, .{ .identity = 3 } };
    var readers: [4]u64 = undefined;
    for (&channels, 0..) |*c, i| {
        readers[i] = @intCast(c.create(2));
        try std.testing.expect(c.transfer(2, c.cap(1), 0));
        try std.testing.expect(c.lookup(2, c.cap(1)) == null);
        try std.testing.expect(c.lookup(1, c.cap(1)) == null);
        try std.testing.expectEqual(0, c.stream.push(@intCast(10 + i)));
    }
    for (&channels, 0..) |*c, i| {
        for (readers, 0..) |reader, j| try std.testing.expect((c.lookup(2, reader) != null) == (i == j));
        c.closeOwner(0);
        try std.testing.expectEqual(@as(i64, @intCast(10 + i)), c.stream.pop());
        try std.testing.expectEqual(256, c.stream.pop());
        c.closeOwner(2);
        _ = c.create(2);
        try std.testing.expect(c.lookup(2, readers[i]) == null);
        for (c.stream.bytes) |value| try std.testing.expectEqual(0, value);
    }
}

test "session channel retains authority and rejects every stale lifetime through exhaustion" {
    var c: Channel = .{ .identity = 9 };
    var old: [15][2]u64 = undefined;
    for (0..15) |i| {
        const reader: u64 = @intCast(c.createSession(5));
        const writer = c.cap(1);
        old[i] = .{ reader, writer };
        try std.testing.expectEqual(i + 1, c.generation);
        for (old[0..i]) |pair| {
            const before = c;
            for (pair) |stale| {
                try std.testing.expect(c.lookup(5, stale) == null);
                try std.testing.expect(!c.transfer(5, stale, 2));
                try std.testing.expectEqual(-13, c.close(5, stale));
            }
            try std.testing.expectEqualDeep(before, c);
        }
        try std.testing.expect(c.transfer(5, reader, 2));
        try std.testing.expect(c.lookup(5, reader) == null);
        try std.testing.expect(c.lookup(2, reader) != null);
        const live = c;
        try std.testing.expectEqual(-16, c.createSession(5));
        try std.testing.expectEqual(-13, c.close(5, reader));
        try std.testing.expect(!c.transfer(5, reader, 3));
        try std.testing.expectEqualDeep(live, c);
        try std.testing.expectEqual(0, c.stream.push(@intCast(i + 1)));
        try std.testing.expectEqual(0, c.close(5, writer));
        const half_closed = c;
        try std.testing.expectEqual(-16, c.createSession(5));
        try std.testing.expectEqualDeep(half_closed, c);
        try std.testing.expectEqual(@as(i64, @intCast(i + 1)), c.stream.pop());
        try std.testing.expectEqual(256, c.stream.pop());
        try std.testing.expectEqual(0, c.close(2, reader));
        try std.testing.expectEqualDeep(Stream{}, c.stream);
        try std.testing.expect(c.lookup(2, reader) == null);
    }
    const retired = c;
    try std.testing.expectEqual(-28, c.createSession(5));
    try std.testing.expectEqual(-28, c.create(5));
    try std.testing.expectEqualDeep(retired, c);
}

test "session last-close zeroes unread bytes and preserves distinct object authority" {
    var a: Channel = .{};
    var b: Channel = .{ .identity = 1 };
    for (0..15) |_| {
        const ar: u64 = @intCast(a.createSession(5));
        const br: u64 = @intCast(b.createSession(5));
        try std.testing.expect(ar != br);
        const before = b;
        try std.testing.expectEqual(-13, b.close(5, ar));
        try std.testing.expect(!b.transfer(5, ar, 0));
        try std.testing.expectEqualDeep(before, b);
        try std.testing.expect(a.transfer(5, ar, 0));
        try std.testing.expect(b.transfer(5, br, 0));
        try std.testing.expectEqual(0, a.stream.push(42));
        try std.testing.expectEqual(0, b.stream.push(99));
        a.closeOwner(0);
        a.closeOwner(5);
        try std.testing.expectEqualDeep(Stream{}, a.stream);
        try std.testing.expectEqual(99, b.stream.pop());
        b.closeOwner(0);
        b.closeOwner(5);
        try std.testing.expectEqualDeep(Stream{}, b.stream);
    }
    try std.testing.expectEqual(-28, a.createSession(5));
    try std.testing.expectEqual(-28, b.createSession(5));
    // Session use of other objects does not broaden legacy creation.
    var legacy: Channel = .{ .identity = 2 };
    for (0..3) |_| {
        try std.testing.expect(legacy.create(5) > 0);
        legacy.closeOwner(5);
    }
    const retired = legacy;
    try std.testing.expectEqual(-28, legacy.create(5));
    try std.testing.expectEqualDeep(retired, legacy);
}

test "sustained channel retirement preserves ownership and disjoint high generations" {
    const limit = @import("native_sustained.zig").generation_limit;
    var channel: Channel = .{ .identity = 5, .sustained = true };
    try std.testing.expectEqual(-22, channel.create(3));
    try std.testing.expectEqual(-22, channel.createSession(3));
    channel.generation = 255;
    const reader: u64 = @intCast(channel.createSustained(3));
    const writer = channel.cap(1);
    try std.testing.expect(channel.transfer(3, reader, 0));
    try std.testing.expect(channel.lookup(3, reader) == null);
    try std.testing.expectEqual(-13, channel.close(1, writer));
    try std.testing.expectEqual(0, channel.stream.push(99));
    channel.closeOwner(0);
    try std.testing.expectEqual(-16, channel.createSustained(3));
    channel.closeOwner(3);
    for (channel.stream.bytes) |value| try std.testing.expectEqual(0, value);
    channel.generation = limit - 1;
    _ = channel.createSustained(3);
    try std.testing.expectEqual(@as(u64, limit), channel.generation);
    try std.testing.expect(channel.lookup(0, reader) == null);
    try std.testing.expect(channel.lookup(3, writer) == null);
    channel.closeOwner(3);
    const retired = channel;
    try std.testing.expectEqual(-28, channel.createSustained(3));
    try std.testing.expectEqualDeep(retired, channel);
}

test "channel wait atomically observes readiness and completes once without transferring bytes" {
    var c: Channel = .{};
    const reader: u64 = @intCast(c.createSession(5));
    const writer = c.cap(1);
    var wait: Wait = .{};
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 5, reader, false));
    try std.testing.expectEqual(@as(?i64, -16), wait.begin(&c, 5, writer, false));
    for (0..5) |_| try std.testing.expectEqual(@as(?i64, null), wait.poll(&c, 5, false));
    try std.testing.expectEqual(0, c.stream.push(42));
    const before = c;
    try std.testing.expectEqual(@as(?i64, 0), wait.poll(&c, 5, false));
    try std.testing.expectEqualDeep(before, c);
    try std.testing.expectEqual(@as(?i64, null), wait.poll(&c, 5, false));
    try std.testing.expectEqual(@as(?i64, 0), wait.begin(&c, 5, reader, false));
    try std.testing.expectEqual(@as(u64, 0), wait.endpoint);
    try std.testing.expectEqual(42, c.stream.pop());
    for (0..32) |_| try std.testing.expectEqual(0, c.stream.push(99));
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 5, writer, false));
    _ = c.stream.pop();
    try std.testing.expectEqual(@as(?i64, 0), wait.poll(&c, 5, false));
    try std.testing.expectEqual(@as(usize, 31), c.stream.count);
}

test "channel wait peer closure wakes EOF and EPIPE without claiming a transfer" {
    var c: Channel = .{};
    var wait: Wait = .{};
    const reader: u64 = @intCast(c.createSession(5));
    const writer = c.cap(1);
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 5, reader, false));
    _ = c.close(5, writer);
    try std.testing.expectEqual(@as(?i64, 0), wait.poll(&c, 5, false));
    try std.testing.expectEqual(256, c.stream.pop());
    c.closeOwner(5);
    _ = c.createSession(5);
    for (0..32) |_| _ = c.stream.push(1);
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 5, c.cap(1), false));
    _ = c.close(5, c.cap(0));
    try std.testing.expectEqual(@as(?i64, 0), wait.poll(&c, 5, false));
    try std.testing.expectEqual(-32, c.stream.push(1));
}

test "channel wait ownership generation interruption and teardown cannot replay completion" {
    var c: Channel = .{};
    var wait: Wait = .{};
    const reader: u64 = @intCast(c.createSession(5));
    try std.testing.expectEqual(@as(?i64, -13), wait.begin(&c, 0, reader, true));
    try std.testing.expectEqual(@as(?i64, -4), wait.begin(&c, 5, reader, true));
    try std.testing.expectEqual(@as(u64, 0), wait.endpoint);
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 5, reader, false));
    try std.testing.expect(c.transfer(5, reader, 0));
    try std.testing.expectEqual(@as(?i64, -13), wait.poll(&c, 5, true));
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 0, reader, false));
    try std.testing.expectEqual(@as(?i64, -4), wait.poll(&c, 0, true));
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 0, reader, false));
    c.closeOwner(0);
    c.closeOwner(5);
    _ = c.createSession(0);
    try std.testing.expectEqual(@as(?i64, -13), wait.poll(&c, 0, false));
    try std.testing.expectEqual(@as(?i64, -13), wait.begin(&c, 0, reader, false));
    try std.testing.expectEqual(@as(?i64, null), wait.begin(&c, 0, c.cap(0), false));
    wait = .{}; // stop/terminal discards the registration before reuse.
    _ = c.stream.push(7);
    try std.testing.expectEqual(@as(?i64, null), wait.poll(&c, 0, false));
    try std.testing.expectEqual(@as(?i64, 0), wait.begin(&c, 0, c.cap(0), false));
    try std.testing.expectEqual(@as(?i64, -4), wait.begin(&c, 0, c.cap(0), true));
    try std.testing.expectEqual(@as(u64, 0), wait.endpoint);
}

test "service connection preflight preserves every rejected endpoint" {
    var channels: [2]Channel = .{ .{}, .{ .identity = 1 } };
    for (0..3) |generation| {
        const reader: u64 = @intCast(channels[0].create(2));
        const writer: u64 = @intCast(channels[1].create(2));
        _ = writer; // Both channel creations return their reader.
        const reply = channels[1].cap(1);
        const before = channels;
        const invalid = [_][3]u64{
            .{ 0, reader, reply },             .{ 2, reader, channels[0].cap(1) },
            .{ 2, channels[0].cap(1), reply }, .{ 2, reader, channels[1].cap(0) },
            .{ 2, reader - 0x100, reply },     .{ 2, reader, reply - 0x100 },
        };
        for (invalid) |args| {
            try std.testing.expect(connectionPair(&channels, @intCast(args[0]), args[1], args[2]) == null);
            try std.testing.expectEqualDeep(before, channels);
        }
        for (0..2) |i| {
            _ = channels[i].stream.push(0xa5);
            const queued = channels;
            try std.testing.expect(connectionPair(&channels, 2, reader, reply) == null);
            try std.testing.expectEqualDeep(queued, channels);
            channels = before;
            channels[i].stream.sealed = true;
            try std.testing.expect(connectionPair(&channels, 2, reader, reply) == null);
            channels = before;
            channels[i].stream.reader_closed = true;
            try std.testing.expect(connectionPair(&channels, 2, reader, reply) == null);
            channels = before;
            for (0..2) |end| {
                try std.testing.expect(channels[i].transfer(2, channels[i].cap(end), 1));
                const foreign = channels;
                try std.testing.expect(connectionPair(&channels, 2, reader, reply) == null);
                try std.testing.expectEqualDeep(foreign, channels);
                channels = before;
            }
        }
        const pair = connectionPair(&channels, 2, reader, reply).?;
        try std.testing.expect(pair.request.transfer(2, reader, 0));
        try std.testing.expect(pair.reply.transfer(2, reply, 0));
        try std.testing.expect(connectionPair(&channels, 2, reader, reply) == null);
        try std.testing.expect(pair.request.lookup(0, reader) == 0);
        try std.testing.expect(pair.reply.lookup(0, reply) == 1);
        // Worker closure precedes supervisor observation/reuse. Unread bytes
        // survive only until the last holder closes, then are zeroed.
        _ = pair.reply.stream.push(42);
        for (&channels) |*c| c.closeOwner(0);
        try std.testing.expectEqual(-16, channels[0].create(2));
        try std.testing.expectEqual(42, pair.reply.stream.pop());
        try std.testing.expectEqual(256, pair.reply.stream.pop());
        for (&channels) |*c| {
            c.closeOwner(2);
            try std.testing.expectEqualDeep(Stream{}, c.stream);
            try std.testing.expectEqual(generation + 1, c.generation);
        }
        try std.testing.expect(connectionPair(&channels, 2, reader, reply) == null);
    }
    const retired = channels;
    for (&channels) |*c| try std.testing.expectEqual(-28, c.create(2));
    try std.testing.expectEqualDeep(retired, channels);
}
