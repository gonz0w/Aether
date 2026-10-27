// SPDX-License-Identifier: BSD-2-Clause
// Private diagnostic scalars only. The native boundary owns validation/effects.
const std = @import("std");
pub const Mode = enum(u8) {
    none,
    file_prefix,
    exec_prefix,
    fork_prefix,
    stream,
    no_ack,
    partial_ack,
    exit_deadline,
    pending_fragment,
    pub fn parse(comptime text: []const u8) Mode {
        inline for (std.meta.fields(Mode)) |field| {
            if (comptime std.mem.eql(u8, text, field.name)) return @enumFromInt(field.value);
        }
        @compileError("unknown native-af09-drain case");
    }
    pub fn negative(self: Mode) bool {
        return @intFromEnum(self) >= @intFromEnum(Mode.no_ack);
    }
};
pub const Object = struct { index: usize = 0, generation: u64 = 0 };
pub const Hold = enum(u8) { none, ready, counter, ack, exit };
pub const State = struct {
    bound: bool = false,
    engine_bound: bool = false,
    invalid: bool = false,
    generations: [7]u64 = @splat(0),
    // Child request/reply, parent request/reply, engine request/reply.
    objects: [6]Object = @splat(.{}),
    startup_written: u64 = 0,
    startup_read: u64 = 0,
    ready_written: u64 = 0,
    ready_read: u64 = 0,
    parent_written: u64 = 0,
    late_written: u64 = 0,
    late_read: u64 = 0,
    copies: u64 = 0,
    child_ready: bool = false,
    query_pending: bool = false,
    query_positive: bool = false,
    child_hold: Hold = .none,
    engine_hold: Hold = .none,
    release_tick: u64 = 0,
    observed: bool = false,
    t0: u64 = 0,
    deadline: u64 = 0,
    counter_seen: bool = false,
    engine_requests: u64 = 0,
    engine_replies: u64 = 0,
    ack_written: u64 = 0,
    ack_read: u64 = 0,
    ack_eagain: bool = false,
    source_closes: u8 = 0,
    deferred_park: bool = false,
    saved_sequence: u64 = 0,
    row: u64 = 0,
    bytes: usize = 0,
    overflow: bool = false,

    pub fn blocked(self: *const State, slot: usize, generation: u64) bool {
        if (!self.bound or self.generations[slot] != generation) return false;
        return switch (slot) {
            0 => self.engine_hold != .none,
            2 => self.child_hold != .none,
            6 => self.query_pending or self.deferred_park,
            else => false,
        };
    }
    pub fn beginDrain(self: *State, now: u64) bool {
        if (self.observed) return true;
        if (!self.query_positive or now > 5400) return false;
        self.t0 = now;
        self.deadline = std.math.add(u64, now, 500) catch return false;
        if (self.deadline > 5900) return false;
        self.observed = true;
        return true;
    }
    pub fn cancel(self: *State, slot: usize, generation: u64) void {
        if (!self.bound or self.generations[slot] != generation) return;
        if (slot == 0) self.engine_hold = .none;
        if (slot == 2) self.child_hold = .none;
        if (slot == 6) {
            self.query_pending = false;
            self.deferred_park = false;
        }
    }
};
pub const Row = struct {
    phase: u8,
    slot: usize = 0,
    gen: u64 = 0,
    seq: u64 = 0,
    tick: u64 = 0,
    deadline: u64 = 0,
    status: i64 = 0,
    count: u64 = 0,
    aux: u64 = 0,
};
fn encode(buffer: *[256]u8, mode: Mode, ordinal: u64, row: Row) ![]const u8 {
    return std.fmt.bufPrint(buffer, "AF09-DRAIN v=1 case={d} row={d} phase={d} slot={d} gen={d} seq={d} tick={d} deadline={d} status={d} count={d} aux={d}\n", .{ @intFromEnum(mode), ordinal, row.phase, row.slot, row.gen, row.seq, row.tick, row.deadline, row.status, row.count, row.aux });
}
// Reserve a complete worst-case row for overflow; no truncation or allocation.
pub fn trace(state: *State, buffer: *[256]u8, mode: Mode, row: Row) ?[]const u8 {
    if (state.overflow) return null;
    var line = encode(buffer, mode, state.row, row) catch {
        state.invalid = true;
        return null;
    };
    if (line.len > 32768 - 256 - state.bytes) {
        state.invalid = true;
        state.overflow = true;
        line = encode(buffer, mode, state.row, .{ .phase = 255 }) catch unreachable;
    }
    state.row += 1;
    state.bytes += line.len;
    return line;
}

test "closed modes, fixed window, generation cancellation and bounded rows" {
    try std.testing.expectEqual(Mode.none, Mode.parse("none"));
    try std.testing.expectEqual(Mode.pending_fragment, Mode.parse("pending_fragment"));
    var s: State = .{ .query_positive = true };
    try std.testing.expect(s.beginDrain(5400));
    try std.testing.expectEqual(@as(u64, 5900), s.deadline);
    try std.testing.expect(s.beginDrain(5500));
    try std.testing.expectEqual(@as(u64, 5400), s.t0);
    var missed: State = .{ .query_positive = true };
    try std.testing.expect(!missed.beginDrain(5401));
    s.bound = true;
    s.generations[0] = 4;
    s.engine_hold = .ack;
    s.cancel(0, 3);
    try std.testing.expect(s.blocked(0, 4));
    s.cancel(0, 4);
    try std.testing.expect(!s.blocked(0, 4));
    var buffer: [256]u8 = undefined;
    var count: usize = 0;
    while (trace(&s, &buffer, .pending_fragment, .{ .phase = 17, .seq = std.math.maxInt(u64), .tick = std.math.maxInt(u64), .deadline = std.math.maxInt(u64), .status = std.math.minInt(i64), .count = std.math.maxInt(u64), .aux = std.math.maxInt(u64) })) |line| {
        try std.testing.expect(line.len <= 256);
        count += 1;
    }
    try std.testing.expect(count > 1 and s.overflow and s.invalid and s.bytes <= 32768);
}
