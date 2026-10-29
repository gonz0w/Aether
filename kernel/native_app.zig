// SPDX-License-Identifier: BSD-2-Clause
// Ordinary one-app admission. Borrowed channel pointers live only under IF=0.
const std = @import("std");
const launch = @import("native_launch.zig");
const Sustained = @import("native_sustained.zig");
const Channel = @import("native_channel.zig").Channel;
pub const record_size = 320;
pub const startup_size = 64;
pub const startup_tag = 0xa003;
pub const startup_address = 0x0800e200;
comptime {
    // args bank ends at data+512; entropy is data+128. At most45 words
    // (argc/envc4, existing auxv and new tag) fit below data without another page.
    std.debug.assert(startup_address == 0x0800e000 + 256 + 8 * 32);
    std.debug.assert(startup_address + startup_size <= 0x08010000);
    std.debug.assert(0x0800c000 + 45 * 8 <= 0x0800e000);
}
pub const Error = error{InvalidLaunch};
pub const Record = struct { args: launch.Arguments, engine: u64, reader: u64, writer: u64 };

pub fn decode(raw: *const [record_size]u8) Error!Record {
    if (!std.mem.eql(u8, raw[0..8], "AENAP001") or
        std.mem.readInt(u64, raw[8..16], .little) != record_size or
        std.mem.readInt(u64, raw[312..320], .little) != 0) return error.InvalidLaunch;
    return .{
        .args = launch.arguments(raw[16..288]) catch return error.InvalidLaunch,
        .engine = std.mem.readInt(u64, raw[288..296], .little),
        .reader = std.mem.readInt(u64, raw[296..304], .little),
        .writer = std.mem.readInt(u64, raw[304..312], .little),
    };
}

// Exactly one local binding per app lifetime. No global registry or retained view.
pub const Binding = struct {
    clock: u64 = 0,
    reader: u64 = 0,
    writer: u64 = 0,
    epoch: u64 = 0,

    pub fn init(slot: usize, generation: u64, reader: u64, writer: u64, epoch: u64) ?Binding {
        if (slot == 0 or slot >= 6 or generation == 0 or generation > 15 or reader == 0 or writer == 0 or epoch == 0) return null;
        return .{ .clock = Sustained.identity(.clock, @intCast(slot), @intCast(generation)) catch return null, .reader = reader, .writer = writer, .epoch = epoch };
    }
    pub fn bound(b: *const Binding) bool {
        return b.clock != 0;
    }
    pub fn valid(b: *const Binding, slot: usize, generation: u64, admitted: bool, terminal: bool, value: u64) bool {
        if (!admitted or terminal or !b.bound() or value != b.clock) return false;
        const expected = init(slot, generation, b.reader, b.writer, b.epoch) orelse return false;
        return value == expected.clock;
    }
    pub fn revoke(b: *Binding) void {
        b.* = .{};
    }
    pub fn startup(b: *const Binding) [startup_size]u8 {
        var raw: [startup_size]u8 = @splat(0);
        @memcpy(raw[0..8], "AENAP001");
        std.mem.writeInt(u64, raw[8..16], startup_size, .little);
        std.mem.writeInt(u64, raw[16..24], b.clock, .little);
        std.mem.writeInt(u64, raw[24..32], b.reader, .little);
        std.mem.writeInt(u64, raw[32..40], b.writer, .little);
        std.mem.writeInt(u64, raw[40..48], b.epoch, .little);
        @memcpy(raw[48..56], "/home/\x00\x00");
        return raw;
    }
};

pub const Engine = struct { slot: usize, admitted: bool, terminal: bool, request: u64, reply: u64 };
pub const Plan = struct {
    process_reader: *Channel,
    process_writer: *Channel,
    namespace_reader: *Channel,
    namespace_writer: *Channel,
    epoch: u64,
};
fn endpoint(channels: []Channel, first: usize, end: usize, owner: usize, value: u64, direction: usize) ?*Channel {
    if (end > channels.len) return null;
    for (channels[first..end]) |*c| if (c.lookup(owner, value) == direction) return c;
    return null;
}
fn open(c: *const Channel) bool {
    return !c.stream.reader_closed and !c.stream.sealed;
}

// Caller resolves the exact retained engine handle first. Validate the actual
// engine counterparts too; token equality alone cannot establish their holder.
pub fn preflight(channels: []Channel, owner: usize, engine: Engine, reader: u64, writer: u64, ns_reader: u64, ns_writer: u64) ?Plan {
    if (owner != 6 or engine.slot != 0 or !engine.admitted or engine.terminal) return null;
    const pr = endpoint(channels, 0, 10, owner, reader, 0) orelse return null;
    const pw = endpoint(channels, 0, 10, owner, writer, 1) orelse return null;
    const nr = endpoint(channels, 10, 12, owner, ns_reader, 0) orelse return null;
    const nw = endpoint(channels, 10, 12, owner, ns_writer, 1) orelse return null;
    const all = [_]*Channel{ pr, pw, nr, nw };
    for (all, 0..) |c, i| {
        if (!open(c)) return null;
        for (all[0..i]) |prior| if (prior == c) return null;
    }
    for ([_]*Channel{ pr, pw }) |c| {
        if (c.owners[0] != owner or c.owners[1] != owner or c.stream.count != 0) return null;
    }
    if (nr.lookup(engine.slot, engine.reply) != 1 or nw.lookup(engine.slot, engine.request) != 0) return null;
    if (nr.read_started or nw.write_started) return null;
    return .{ .process_reader = pr, .process_writer = pw, .namespace_reader = nr, .namespace_writer = nw, .epoch = engine.request };
}

test "ordinary record exact wrapper preserves argument semantics" {
    var raw: [record_size]u8 = @splat(0);
    @memcpy(raw[0..8], "AENAP001");
    std.mem.writeInt(u64, raw[8..16], record_size, .little);
    raw[16] = 4;
    raw[24] = 4;
    const decoded = try decode(&raw);
    try std.testing.expectEqual(@as(usize, 4), decoded.args.argc);
    try std.testing.expectEqual(@as(usize, 4), decoded.args.envc);
    for ([_]usize{ 0, 8, 16, 24, 312 }) |offset| {
        const before = raw;
        raw[offset] = 255;
        try std.testing.expectError(error.InvalidLaunch, decode(&raw));
        raw = before;
    }
    @memset(raw[32..64], 'x');
    try std.testing.expectError(error.InvalidLaunch, decode(&raw));
}

test "ordinary binding exact startup lifetime and type separation" {
    var binding = Binding.init(1, 1, 7, 8, 0xd10a0101).?;
    const raw = binding.startup();
    try std.testing.expectEqual(@as(usize, 32), @sizeOf(Binding));
    try std.testing.expectEqual(@as(usize, 64), raw.len);
    try std.testing.expectEqualSlices(u8, "AENAP001", raw[0..8]);
    try std.testing.expectEqualSlices(u8, "/home/\x00\x00", raw[48..56]);
    try std.testing.expect(std.mem.allEqual(u8, raw[56..64], 0));
    for (1..6) |slot| for (1..16) |generation| {
        try std.testing.expect(binding.valid(slot, generation, true, false, binding.clock) == (slot == 1 and generation == 1));
    };
    try std.testing.expect(!binding.valid(1, 1, false, false, binding.clock));
    try std.testing.expect(!binding.valid(1, 1, true, true, binding.clock));
    for ([_]Sustained.Kind{ .instance, .memory, .thread, .reader, .writer }) |kind| {
        try std.testing.expect(!binding.valid(1, 1, true, false, try Sustained.identity(kind, 1, 1)));
    }
    const token = binding.clock;
    binding.revoke();
    try std.testing.expectEqualDeep(Binding{}, binding);
    try std.testing.expect(!binding.valid(1, 1, true, false, token));
}

test "ordinary admission snapshots holders counterparts queues and history" {
    var channels: [12]Channel = @splat(.{});
    for (&channels, 0..) |*c, i| {
        c.identity = i;
        _ = c.create(6);
    }
    const reader = channels[0].cap(0);
    const writer = channels[1].cap(1);
    const nr = channels[11].cap(0);
    const nw = channels[10].cap(1);
    const engine = Engine{ .slot = 0, .admitted = true, .terminal = false, .request = channels[10].cap(0), .reply = channels[11].cap(1) };
    try std.testing.expect(channels[10].transfer(6, engine.request, 0));
    try std.testing.expect(channels[11].transfer(6, engine.reply, 0));
    for (0..32) |i| _ = channels[11].stream.push(@intCast(i));
    channels[11].write_started = true; // The engine's queued greeting is allowed.
    const before = channels;
    const plan = preflight(&channels, 6, engine, reader, writer, nr, nw).?;
    try std.testing.expectEqual(engine.request, plan.epoch);
    try std.testing.expectEqualDeep(before, channels);
    for (0..4) |which| {
        channels = before;
        const at = ([_]usize{ 0, 1, 11, 10 })[which];
        channels[at].stream.sealed = true;
        const snapshot = channels;
        try std.testing.expect(preflight(&channels, 6, engine, reader, writer, nr, nw) == null);
        try std.testing.expectEqualDeep(snapshot, channels);
    }
    channels = before;
    channels[11].owners[1] = 5;
    try std.testing.expect(preflight(&channels, 6, engine, reader, writer, nr, nw) == null);
    channels = before;
    channels[11].read_started = true;
    try std.testing.expect(preflight(&channels, 6, engine, reader, writer, nr, nw) == null);
    channels = before;
    channels[10].write_started = true;
    try std.testing.expect(preflight(&channels, 6, engine, reader, writer, nr, nw) == null);
    channels = before;
    try std.testing.expect(preflight(&channels, 5, engine, reader, writer, nr, nw) == null);
    try std.testing.expect(preflight(&channels, 6, engine, reader, writer, nw, nr) == null);
    try std.testing.expect(preflight(&channels, 6, engine, reader, writer, nr - 0x100, nw) == null);
    try std.testing.expect(preflight(&channels, 6, engine, reader, channels[0].cap(1), nr, nw) == null);
}
