// SPDX-License-Identifier: BSD-2-Clause
// Owner-local state for the selected sustained-init contract. Native wiring is separate.
const std = @import("std");

pub const generation_limit: u32 = 0x0fffffff;
pub const Kind = enum(u8) { instance = 0x31, memory = 0x32, thread = 0x33, reader = 0x34, writer = 0x35, clock = 0x36 };

// The caller must enforce holder authority and object liveness before using this identity.
pub fn identity(kind: Kind, object: u8, generation: u32) error{InvalidGeneration}!u64 {
    if (generation == 0 or generation > generation_limit) return error.InvalidGeneration;
    return (@as(u64, @intFromEnum(kind)) << 56) | (@as(u64, object) << 32) | generation;
}

pub fn nextGeneration(current: u32) ?u32 {
    return if (current >= generation_limit) null else current + 1;
}

pub const Outcome = enum { event, deadline, cancelled };
pub const Completion = struct { outcome: Outcome, sequence: u64, tick: u64 };
pub const Error = error{ Busy, FutureSequence, Exhausted };

// One supervisor owns this state. Compare/park, poll and publish must be serialized
// by the enforcing boundary; the pure core does not mask interrupts or wake a CPU.
pub const Events = struct {
    sequence: u64 = 0,
    occupied: bool = false,
    expected: u64 = 0,
    deadline: ?u64 = null,
    completion: ?Completion = null,

    pub fn parked(self: *const Events) bool {
        return self.occupied and self.completion == null;
    }

    pub fn park(self: *Events, expected: u64, now: u64, deadline: ?u64, serial_ready: bool) Error!void {
        if (self.occupied) return error.Busy;
        if (expected > self.sequence) return error.FutureSequence;
        // An exhausted sequence cannot protect a new observation/park cycle.
        if (self.sequence == std.math.maxInt(u64)) return error.Exhausted;
        self.occupied = true;
        self.expected = expected;
        self.deadline = deadline;
        self.poll(now, serial_ready);
    }

    pub fn publish(self: *Events, now: u64) Error!void {
        if (self.sequence == std.math.maxInt(u64)) return error.Exhausted;
        self.sequence += 1;
        self.poll(now, false);
    }

    pub fn poll(self: *Events, now: u64, serial_ready: bool) void {
        if (!self.parked()) return;
        if (self.deadline) |deadline| {
            if (now >= deadline) {
                self.complete(.deadline, now);
                return;
            }
        }
        if (self.sequence != self.expected or serial_ready) self.complete(.event, now);
    }

    pub fn cancel(self: *Events, now: u64) void {
        if (self.parked()) self.complete(.cancelled, now);
    }

    fn complete(self: *Events, outcome: Outcome, now: u64) void {
        self.completion = .{ .outcome = outcome, .sequence = self.sequence, .tick = now };
    }

    pub fn take(self: *Events) ?Completion {
        const result = self.completion orelse return null;
        self.occupied = false;
        self.expected = 0;
        self.deadline = null;
        self.completion = null;
        return result;
    }
};

test "sustained identities separate kind object and lifetime at boundaries" {
    const kinds = [_]Kind{ .instance, .memory, .thread, .reader, .writer, .clock };
    const generations = [_]u32{ 1, 3, 15, 255, 256, 65535, 65536, generation_limit };
    for (kinds) |kind| for ([_]u8{ 0, 1, 5, 255 }) |object| for (generations) |generation| {
        const value = try identity(kind, object, generation);
        try std.testing.expect(value <= std.math.maxInt(i64));
        try std.testing.expectEqual(@as(u64, @intFromEnum(kind)), value >> 56);
        try std.testing.expectEqual(@as(u64, object), (value >> 32) & 0xff);
        try std.testing.expectEqual(@as(u64, generation), value & generation_limit);
        try std.testing.expectEqual(@as(u64, 0), value & 0x00ffff00f0000000);
        for (kinds) |other| if (other != kind) try std.testing.expect(value != try identity(other, object, generation));
        if (generation < generation_limit) try std.testing.expect(value != try identity(kind, object, generation + 1));
        if (object < 255) try std.testing.expect(value != try identity(kind, object + 1, generation));
    };
    try std.testing.expectError(error.InvalidGeneration, identity(.instance, 0, 0));
    try std.testing.expectError(error.InvalidGeneration, identity(.reader, 0, generation_limit + 1));
    try std.testing.expectEqual(@as(?u32, 1), nextGeneration(0));
    try std.testing.expectEqual(@as(?u32, generation_limit), nextGeneration(generation_limit - 1));
    try std.testing.expectEqual(@as(?u32, null), nextGeneration(generation_limit));
    try std.testing.expectEqual(@as(?u32, null), nextGeneration(std.math.maxInt(u32)));
    try std.testing.expect(@as(u64, generation_limit) * 4 + 4 <= std.math.maxInt(i32));
}

test "event before registration and event after park are both retained" {
    var events: Events = .{};
    try events.publish(10);
    try events.park(0, 11, null, false);
    try std.testing.expectEqual(Completion{ .outcome = .event, .sequence = 1, .tick = 11 }, events.take().?);
    try events.park(1, 12, null, false);
    try std.testing.expect(events.parked());
    events.poll(3001, false);
    try std.testing.expect(events.parked()); // Healthy lifetime is not a fixture timeout.
    try std.testing.expectEqual(@as(?Completion, null), events.take());
    try events.publish(3002);
    const retained = events.completion;
    events.cancel(3003);
    events.poll(3004, true);
    try events.publish(3005);
    try std.testing.expectEqualDeep(retained, events.completion);
    try std.testing.expectError(error.Busy, events.park(2, 3006, null, false));
    try std.testing.expectEqualDeep(retained, events.take());
    try events.park(1, 3007, null, false); // An event while completion was retained is not lost.
    try std.testing.expectEqual(@as(u64, 3), events.take().?.sequence);
}

test "serial readiness is level checked before and during park" {
    var events: Events = .{};
    try events.park(0, 1, null, true);
    try std.testing.expectEqual(Outcome.event, events.take().?.outcome);
    try events.park(0, 2, null, false);
    events.poll(3, false);
    try std.testing.expect(events.parked());
    events.poll(4, true);
    try std.testing.expectEqual(Completion{ .outcome = .event, .sequence = 0, .tick = 4 }, events.take().?);
    try events.park(0, 5, null, false);
    try std.testing.expect(events.parked());
}

test "deadline wins ties and completion cannot be overwritten by cancel" {
    var events: Events = .{};
    try events.park(0, 10, 10, true);
    try std.testing.expectEqual(Outcome.deadline, events.take().?.outcome);
    try events.park(0, 11, 20, false);
    try events.publish(20);
    events.cancel(21);
    try std.testing.expectEqual(Completion{ .outcome = .deadline, .sequence = 1, .tick = 20 }, events.take().?);
    try events.park(1, 22, null, false);
    events.cancel(23);
    try events.publish(24);
    try std.testing.expectEqual(Completion{ .outcome = .cancelled, .sequence = 1, .tick = 23 }, events.take().?);
    events.cancel(25);
    try std.testing.expect(!events.occupied);
}

test "invalid observation and exhausted sequence fail without mutation" {
    var events: Events = .{};
    const empty = events;
    try std.testing.expectError(error.FutureSequence, events.park(1, 0, null, false));
    try std.testing.expectEqualDeep(empty, events);
    events.sequence = std.math.maxInt(u64) - 1;
    try events.park(events.sequence, 1, null, false);
    try events.publish(2);
    try std.testing.expectEqual(Outcome.event, events.take().?.outcome);
    const exhausted = events;
    try std.testing.expectError(error.Exhausted, events.publish(3));
    try std.testing.expectError(error.Exhausted, events.park(events.sequence, 3, null, true));
    try std.testing.expectEqualDeep(exhausted, events);
}

// Reading a UART line-status register may clear its error bits. Once readiness
// monitoring is enabled, retain those errors across receive/transmit polls until
// the actual reader consumes the error outcome. This owns no receive bytes.
pub const SerialStatus = struct {
    enabled: bool = false,
    errors: u8 = 0,
    pub fn observe(self: *SerialStatus, status: u8) u8 {
        if (self.enabled) self.errors |= status & 0x1e;
        return status;
    }
    // Source exposes only a line-status read, never the receive-data register.
    pub fn transmitterEmpty(self: *SerialStatus, source: anytype) i64 {
        self.enabled = true;
        const status = self.observe(source.read());
        if (status == 0xff or (status & 0x40 != 0 and status & 0x20 == 0)) return -5;
        return if (status & 0x40 != 0) 0 else -11;
    }
    pub fn ready(self: *SerialStatus, status: u8) bool {
        self.enabled = true;
        _ = self.observe(status);
        return status & 1 != 0 or self.errors != 0;
    }
    pub fn takeError(self: *SerialStatus, status: u8) bool {
        _ = self.observe(status);
        const failed = status & 0x1e != 0 or self.errors != 0;
        self.errors = 0;
        return failed;
    }
};

test "serial status retains read-cleared errors across readiness and transmit polls" {
    var status: SerialStatus = .{};
    _ = status.observe(0x02); // Legacy non-monitoring mode has no retained state.
    try std.testing.expect(!status.takeError(0x20));
    for ([_]u8{ 0x02, 0x04, 0x08, 0x10 }) |error_bit| {
        try std.testing.expect(status.ready(error_bit));
        _ = status.observe(0x60); // A later transmit-ready read no longer contains the error.
        try std.testing.expect(status.ready(0));
        try std.testing.expect(status.takeError(0));
        try std.testing.expect(!status.ready(0));
        try std.testing.expect(!status.takeError(0));
    }
    try std.testing.expect(status.ready(1));
    try std.testing.expect(!status.takeError(1));
    _ = status.observe(0x22); // Error first observed while polling for transmit readiness.
    try std.testing.expect(status.ready(0));
    try std.testing.expect(status.takeError(0));
}

test "transmitter empty requires TEMT with THRE and observes one status without consuming RX" {
    const Source = struct {
        status: u8,
        reads: usize = 0,
        receive: [3]u8 = .{ 0, 13, 255 },
        pub fn read(self: *@This()) u8 {
            self.reads += 1;
            return self.status;
        }
    };
    for ([_]u8{ 0, 1, 0x20, 0x21, 0x40, 0x41, 0x60, 0x61, 0xff }) |sample| {
        var status: SerialStatus = .{};
        var source: Source = .{ .status = sample };
        const expected: i64 = switch (sample) {
            0x40, 0x41, 0xff => -5,
            0x60, 0x61 => 0,
            else => -11,
        };
        try std.testing.expectEqual(expected, status.transmitterEmpty(&source));
        try std.testing.expectEqual(@as(usize, 1), source.reads);
        try std.testing.expectEqualSlices(u8, &.{ 0, 13, 255 }, &source.receive);
        try std.testing.expect(status.enabled);
    }
}

test "first transmitter observation retains RX errors through later polls and reader consumption" {
    const Source = struct {
        status: u8,
        pub fn read(self: *@This()) u8 {
            return self.status;
        }
    };
    for ([_]u8{ 0x02, 0x04, 0x08, 0x10 }) |error_bit| {
        var status: SerialStatus = .{};
        var source: Source = .{ .status = 0x20 | error_bit };
        try std.testing.expectEqual(@as(i64, -11), status.transmitterEmpty(&source));
        try std.testing.expectEqual(error_bit, status.errors);
        source.status = 0x60;
        try std.testing.expectEqual(@as(i64, 0), status.transmitterEmpty(&source));
        _ = status.observe(0x60); // Ordinary transmit polling must not erase it.
        try std.testing.expectEqual(error_bit, status.errors);
        try std.testing.expect(status.takeError(0));
        try std.testing.expect(!status.takeError(0));
        try std.testing.expect(!status.ready(0));
    }
    var pending: SerialStatus = .{};
    try std.testing.expect(pending.ready(0x02));
    var source: Source = .{ .status = 0x64 };
    try std.testing.expectEqual(@as(i64, 0), pending.transmitterEmpty(&source));
    try std.testing.expectEqual(@as(u8, 0x06), pending.errors);
    try std.testing.expect(pending.takeError(0));
}
