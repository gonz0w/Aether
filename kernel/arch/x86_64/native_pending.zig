// SPDX-License-Identifier: BSD-2-Clause
// Domain-owned signal records: native copies are opt-in; explicit self-delivery is private and opt-in.
const std = @import("std");
const unmaskable: u64 = (1 << 8) | (1 << 18);

pub const Handler = struct { entry: u64, restorer: u64, mask: u64 };
pub const Action = union(enum) { default, ignore, handler: Handler };
pub const Selection = struct { signal: u8, action: Action };

// Proposed bounded self-delivery policy, not enabled native lifecycle behavior.
// Termination implies no core-file service. Stop/resume require future admission
// and lifecycle work; callers must not treat them as ignored or normal exits.
pub const DefaultEffect = enum { ignore, terminate, stop, continue_execution };

pub fn defaultEffect(signal: u8) error{Invalid}!DefaultEffect {
    _ = try bit(signal);
    return switch (signal) {
        17, 23, 28 => .ignore,
        18 => .continue_execution,
        20, 21, 22 => .stop,
        else => .terminate,
    };
}

// Candidate only: legacy native profiles and consumers accept kinds 1..3.
// No runtime may publish this before matching profile/consumer qualification.
pub const SignalTerminal = struct { kind: u64 = 4, detail: u64 };

pub fn defaultTermination(signal: u8) error{Invalid}!SignalTerminal {
    if (try defaultEffect(signal) != .terminate) return error.Invalid;
    return .{ .detail = signal };
}

fn discarded(signal: u8, selected: Action) bool {
    return selected == .ignore or
        (selected == .default and (defaultEffect(signal) catch unreachable) == .ignore);
}

fn bit(signal: u8) error{Invalid}!u32 {
    if (signal == 0 or signal > 31 or signal == 9 or signal == 19) return error.Invalid;
    return @as(u32, 1) << @as(u5, @intCast(signal - 1));
}

pub const restorer_flag: u64 = 0x04000000;
pub const restart_flag: u64 = 0x10000000;

// Pinned x86_64 musl field order. No borrowed user pointer is retained.
pub const Record = extern struct {
    entry: u64 = 0,
    flags: u64 = 0,
    restorer: u64 = 0,
    mask: u64 = 0,

    pub fn action(self: Record) Action {
        return switch (self.entry) {
            0 => .default,
            1 => .ignore,
            else => .{ .handler = .{ .entry = self.entry, .restorer = self.restorer, .mask = self.mask } },
        };
    }
};

fn queryable(signal: u8) error{Invalid}!void {
    if (signal == 0 or signal > 64 or (signal >= 32 and signal <= 34)) return error.Invalid;
}

pub const State = struct {
    records: [64]Record = @splat(.{}),
    pending: u32 = 0,

    pub fn query(self: *const State, signal: u8) error{Invalid}!Record {
        try queryable(signal);
        return self.records[signal - 1];
    }

    // Caller snapshots the input and validates mapped RX targets and all output
    // copies before mutation. Delivery must validate mappings again.
    pub fn installRecord(self: *State, signal: u8, requested: Record) error{ Invalid, NotSupported }!Record {
        return self.installChecked(signal, requested, restorer_flag);
    }

    // Restart is inert for DFL/IGN: neither disposition enters a handler.
    // Custom handler restart remains unsupported; retain flags for queries.
    pub fn installPublicRecord(self: *State, signal: u8, requested: Record) error{ Invalid, NotSupported }!Record {
        const allowed = restorer_flag | (if (requested.entry <= 1) restart_flag else @as(u64, 0));
        return self.installChecked(signal, requested, allowed);
    }

    fn installChecked(self: *State, signal: u8, requested: Record, allowed: u64) error{ Invalid, NotSupported }!Record {
        try queryable(signal);
        if (signal == 9 or signal == 19) return error.Invalid;
        if (requested.flags & ~allowed != 0) return error.NotSupported;
        if (requested.entry > 1) {
            if (signal > 31) return error.NotSupported;
            if (requested.flags != restorer_flag) return error.Invalid;
            if (requested.entry >= (1 << 47) or requested.restorer == 0 or requested.restorer >= (1 << 47)) return error.Invalid;
        }
        var next = requested;
        next.mask &= ~unmaskable;
        const previous = self.records[signal - 1];
        self.records[signal - 1] = next;
        if (signal <= 31 and discarded(signal, next.action())) self.pending &= ~(try bit(signal));
        return previous;
    }

    pub fn action(self: *const State, signal: u8) error{Invalid}!Action {
        _ = try bit(signal);
        return self.records[signal - 1].action();
    }

    // Semantic helper for the existing owner/frame experiments, not a syscall.
    pub fn install(self: *State, signal: u8, requested: Action) error{Invalid}!Action {
        _ = try bit(signal);
        const record: Record = switch (requested) {
            .default => .{},
            .ignore => .{ .entry = 1 },
            .handler => |h| blk: {
                if (h.entry <= 1) return error.Invalid;
                break :blk .{ .entry = h.entry, .flags = restorer_flag, .restorer = h.restorer, .mask = h.mask };
            },
        };
        const previous = self.installRecord(signal, record) catch return error.Invalid;
        return previous.action();
    }

    pub fn post(self: *State, signal: u8) error{Invalid}!void {
        const selected = try bit(signal);
        if (!discarded(signal, self.records[signal - 1].action())) self.pending |= selected;
    }

    // No dequeue on selection: a failed mapping/copy check must not lose a post.
    pub fn peek(self: *const State, mask: u64) ?Selection {
        const eligible = self.pending & ~@as(u32, @truncate(mask));
        if (eligible == 0) return null;
        const signal: u8 = @intCast(@ctz(eligible) + 1);
        return .{ .signal = signal, .action = self.records[signal - 1].action() };
    }

    // Exec can retain a queued occurrence whose new disposition ignores it.
    // Readiness waits must not dequeue it or turn ignored work into EINTR.
    pub fn interrupts(self: *const State, mask: u64) bool {
        var excluded = mask;
        while (self.peek(excluded)) |selected| {
            if (!discarded(selected.signal, selected.action)) return true;
            excluded |= @as(u64, 1) << @as(u6, @intCast(selected.signal - 1));
        }
        return false;
    }

    // Caller holds owner serialization continuously from peek through checked
    // preparation and publication. This is not a token valid across yielding.
    pub fn commit(self: *State, signal: u8) error{Invalid}!void {
        const selected = try bit(signal);
        if (self.pending & selected == 0) return error.Invalid;
        self.pending &= ~selected;
    }

    // Distinct serialized domains; destination is not published. Source records
    // were validated at installation. Pending occurrences belong to the source,
    // including when its execution mask blocks delivery across the copy.
    pub fn inheritFrom(self: *State, source: *const State) void {
        self.records = source.records;
        self.pending = 0;
    }

    // Candidate only: exec preserves pending occurrences, unlike fork. Caught
    // actions become default; ignored dispositions retain no old-image pointers.
    // The caller publishes only after old execution is stopped and replacement
    // admission succeeds. Constructing this value cannot alter the old image.
    pub fn forImage(self: *const State) State {
        var next = State{ .pending = self.pending };
        for (self.records, &next.records) |old, *record| {
            if (old.entry == 1) record.* = .{ .entry = 1 };
        }
        return next;
    }

    // Called only after domain execution has stopped; no handler-active state.
    pub fn reset(self: *State) void {
        self.* = .{};
    }
};

const handler: Action = .{ .handler = .{ .entry = 0x201000, .restorer = 0x202000, .mask = 4 } };

test "masked duplicates coalesce and selection survives failed preparation" {
    var s: State = .{};
    _ = try s.install(12, handler);
    try s.post(12);
    try s.post(10);
    try s.post(12);
    const before = s;
    try std.testing.expect(s.peek((1 << 9) | (1 << 11)) == null);
    const selected = s.peek(1 << 9).?;
    try std.testing.expectEqual(@as(u8, 12), selected.signal);
    try std.testing.expectEqualDeep(handler, selected.action);
    // Frame validation may fail after peek: neither post can be consumed yet.
    try std.testing.expectEqualDeep(before, s);
    try std.testing.expectEqualDeep(selected, s.peek(1 << 9).?);
    try s.commit(12);
    try std.testing.expect(s.peek(1 << 9) == null);
    try std.testing.expectEqual(@as(u8, 10), s.peek(0).?.signal);
    try std.testing.expect(s.peek(0).?.action == .default);
    try s.commit(10);
    try std.testing.expect(s.peek(0) == null);
    try std.testing.expectError(error.Invalid, s.commit(12));
}

test "ignore drops queued and future posts; replacement keeps pending selection current" {
    var s: State = .{};
    try s.post(2);
    try std.testing.expectEqualDeep(Action.default, try s.install(2, handler));
    try std.testing.expectEqualDeep(handler, s.peek(0).?.action);
    try std.testing.expectEqualDeep(handler, try s.install(2, .ignore));
    try std.testing.expect(s.peek(0) == null);
    try s.post(2);
    _ = try s.install(2, .default);
    try std.testing.expect(s.peek(0) == null);
    try s.post(2);
    try std.testing.expect(s.peek(0).?.action == .default);
    var masked = handler;
    masked.handler.mask = std.math.maxInt(u64);
    _ = try s.install(2, masked);
    try std.testing.expectEqual(std.math.maxInt(u64) & ~unmaskable, (try s.action(2)).handler.mask);
}

test "invalid updates leave complete owner state unchanged" {
    var s: State = .{};
    _ = try s.install(10, handler);
    try s.post(10);
    const before = s;
    for ([_]u8{ 0, 9, 19, 32, 255 }) |signal| {
        try std.testing.expectError(error.Invalid, s.install(signal, .ignore));
        try std.testing.expectError(error.Invalid, s.post(signal));
        try std.testing.expectError(error.Invalid, s.commit(signal));
        try std.testing.expectError(error.Invalid, s.action(signal));
    }
    for ([_]u64{ 0, 1 << 47, std.math.maxInt(u64) }) |bad| {
        var invalid = handler;
        invalid.handler.entry = bad;
        try std.testing.expectError(error.Invalid, s.install(10, invalid));
        invalid = handler;
        invalid.handler.restorer = bad;
        try std.testing.expectError(error.Invalid, s.install(10, invalid));
    }
    try std.testing.expectEqualDeep(before, s);
}

test "all supported posts fit; owner reset leaves peer and masks independent" {
    var owners: [2]State = @splat(.{});
    _ = try owners[1].install(12, handler);
    try owners[1].post(12);
    const peer = owners[1];
    var expected: u32 = 0;
    for (1..32) |n| {
        const signal: u8 = @intCast(n);
        if (signal == 9 or signal == 19) continue;
        try owners[0].post(signal);
        if (try defaultEffect(signal) != .ignore) expected |= try bit(signal);
    }
    try std.testing.expectEqual(expected, owners[0].pending);
    var last: u8 = 0;
    while (owners[0].peek(0)) |selected| {
        try std.testing.expect(selected.signal > last);
        last = selected.signal;
        try owners[0].commit(selected.signal);
    }
    _ = try owners[0].install(2, handler);
    try owners[0].post(2);
    owners[0].reset();
    try std.testing.expectEqualDeep(State{}, owners[0]);
    try std.testing.expectEqualDeep(peer, owners[1]);
    try std.testing.expect(owners[1].peek(1 << 11) == null);
    try std.testing.expectEqual(@as(u8, 12), owners[1].peek(0).?.signal);
    try std.testing.expect(@sizeOf(State) <= 3072);
}

test "checked frame failure retains post; committed delivery permits a later occurrence" {
    const frames = @import("native_signal.zig");
    const nx: u64 = 1 << 63;
    var pages = [_]struct { address: usize, flags: u64 }{
        .{ .address = 0x200000, .flags = 5 | nx },
        .{ .address = 0x800000, .flags = 7 | nx },
        .{ .address = 0x801000, .flags = 7 | nx },
    };
    var backing: [3][4096]u8 = @splat(@splat(0));
    var s: State = .{};
    _ = try s.install(10, .{ .handler = .{ .entry = 0x200010, .restorer = 0x200020, .mask = 8 } });
    try s.post(10);
    const selected = s.peek(4).?;
    const h = selected.action.handler;
    var request: frames.Entry = .{
        .cpu = .{ .rip = 0x200030, .rsp = 0x802000, .cs = 0x23, .ss = 0x1b, .flags = 0x202 },
        .fp = @splat(0),
        .mask = 4,
        .action_mask = h.mask,
        .handler = h.entry,
        .restorer = h.restorer,
        .signal = @intCast(selected.signal),
        .stack_low = 0x800000,
        .stack_high = 0x802000,
    };
    std.mem.writeInt(u32, request.fp[24..28], 0x1f80, .little);
    var candidate: frames.Candidate = undefined;
    const before = s;
    try std.testing.expectError(error.Invalid, frames.prepareEntryInto(&pages, &backing, &request, 0xffbf, &candidate));
    try std.testing.expectEqualDeep(before, s);
    pages[0].flags = 5;
    try frames.prepareEntryInto(&pages, &backing, &request, 0xffbf, &candidate);
    try s.commit(selected.signal);
    try std.testing.expect(s.peek(0) == null);
    try std.testing.expectEqual(@as(u64, 4 | 8 | 512), candidate.mask);
    // Another occurrence during this handler remains pending under its mask.
    try s.post(10);
    try std.testing.expect(s.peek(candidate.mask) == null);
    const layout = try frames.place(request.cpu.rsp, request.stack_low, request.stack_high);
    try frames.readReturnInto(&pages, &backing, layout.payload, 0xffbf, &candidate);
    try std.testing.expectEqual(@as(u64, 4), candidate.mask);
    try std.testing.expectEqual(selected.signal, s.peek(candidate.mask).?.signal);
}

test "default effects distinguish ignored termination and unsupported job control" {
    const expected = [_]DefaultEffect{
        .terminate, .terminate, .terminate, .terminate, .terminate, .terminate,
        .terminate, .terminate, .terminate, .terminate, .terminate, .terminate,
        .terminate, .terminate, .terminate, .terminate, .ignore,    .continue_execution,
        .stop,      .stop,      .stop,      .stop,      .ignore,    .terminate,
        .terminate, .terminate, .terminate, .ignore,    .terminate, .terminate,
        .terminate,
    };
    for (expected, 1..) |effect, n| {
        const signal: u8 = @intCast(n);
        if (signal == 9 or signal == 19) {
            try std.testing.expectError(error.Invalid, defaultEffect(signal));
        } else {
            try std.testing.expectEqual(effect, try defaultEffect(signal));
        }
    }
    for ([_]u8{ 0, 32, 255 }) |signal|
        try std.testing.expectError(error.Invalid, defaultEffect(signal));
}

test "default ignore drops queued occurrences without dropping another signal" {
    for ([_]u8{ 17, 23, 28 }) |signal| {
        var s: State = .{};
        try s.post(signal);
        try std.testing.expect(s.peek(0) == null);
        _ = try s.install(signal, handler);
        try std.testing.expect(s.peek(0) == null);
        try s.post(signal);
        try s.post(10);
        try std.testing.expectEqualDeep(handler, try s.install(signal, .default));
        try std.testing.expectEqual(@as(u8, 10), s.peek(0).?.signal);
        try s.commit(10);
        try std.testing.expect(s.peek(0) == null);
        _ = try s.install(signal, handler);
        try s.post(signal);
        try std.testing.expectEqualDeep(handler, s.peek(0).?.action);
        try s.commit(signal);
        try std.testing.expect(s.peek(0) == null);
    }
}

test "raw query retains flags mask and restorer across semantic changes" {
    var s: State = .{};
    try std.testing.expectEqual(@as(usize, 32), @sizeOf(Record));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(Record, "flags"));
    try std.testing.expectEqual(@as(usize, 16), @offsetOf(Record, "restorer"));
    try std.testing.expectEqual(@as(usize, 24), @offsetOf(Record, "mask"));
    var requested: Record = .{ .entry = 1, .flags = restorer_flag, .restorer = 0x202000, .mask = std.math.maxInt(u64) };
    try std.testing.expectEqualDeep(Record{}, try s.installRecord(10, requested));
    requested.mask &= ~unmaskable;
    try std.testing.expectEqualDeep(requested, try s.query(10));
    var replacement = requested;
    replacement.entry = 0;
    replacement.mask = 4;
    try std.testing.expectEqualDeep(requested, try s.installRecord(10, replacement));
    try std.testing.expectEqualDeep(replacement, try s.query(10));
    replacement.entry = 0x201000;
    _ = try s.installRecord(10, replacement);
    try s.post(10);
    try std.testing.expectEqualDeep(handler, s.peek(0).?.action);
    try std.testing.expectEqualDeep(replacement, try s.query(10));
}

test "query compatibility does not authorize additional delivery" {
    var s: State = .{};
    for ([_]u8{ 9, 19 }) |signal| {
        try std.testing.expectEqualDeep(Record{}, try s.query(signal));
        try std.testing.expectError(error.Invalid, s.installRecord(signal, .{}));
    }
    for (35..65) |n| {
        const signal: u8 = @intCast(n);
        const requested: Record = .{ .entry = 1, .mask = 4, .flags = restorer_flag, .restorer = 0x202000 };
        _ = try s.installRecord(signal, requested);
        try std.testing.expectEqualDeep(requested, try s.query(signal));
        try std.testing.expectError(error.Invalid, s.post(signal));
        try std.testing.expectError(error.NotSupported, s.installRecord(signal, .{ .entry = 0x201000, .flags = restorer_flag, .restorer = 0x202000 }));
        try std.testing.expectEqualDeep(requested, try s.installRecord(signal, .{}));
    }
    for ([_]u8{ 0, 32, 33, 34, 65, 255 }) |signal| {
        try std.testing.expectError(error.Invalid, s.query(signal));
        try std.testing.expectError(error.Invalid, s.installRecord(signal, .{}));
    }
    try std.testing.expectEqual(@as(u32, 0), s.pending);
}

test "rejected records preserve full table and queued occurrences" {
    var s: State = .{};
    _ = try s.install(10, handler);
    try s.post(10);
    const before = s;
    for (0..64) |n| {
        const flag = @as(u64, 1) << @as(u6, @intCast(n));
        if (flag == restorer_flag) continue;
        for ([_]u64{ 0, 1, 0x201000 }) |entry| {
            try std.testing.expectError(error.NotSupported, s.installRecord(10, .{ .entry = entry, .flags = restorer_flag | flag, .restorer = 0x202000 }));
        }
    }
    try std.testing.expectError(error.Invalid, s.installRecord(10, .{ .entry = 0x201000, .restorer = 0x202000 }));
    for ([_]u64{ 1 << 47, std.math.maxInt(u64) }) |bad| {
        try std.testing.expectError(error.Invalid, s.installRecord(10, .{ .entry = bad, .flags = restorer_flag, .restorer = 0x202000 }));
        try std.testing.expectError(error.Invalid, s.installRecord(10, .{ .entry = 0x201000, .flags = restorer_flag, .restorer = bad }));
    }
    try std.testing.expectError(error.Invalid, s.installRecord(10, .{ .entry = 0x201000, .flags = restorer_flag }));
    try std.testing.expectEqualDeep(before, s);
    s.reset();
    try std.testing.expectEqualDeep(State{}, s);
}

test "candidate signal terminal never aliases exit fault or stop" {
    for (1..32) |n| {
        const signal: u8 = @intCast(n);
        if (signal == 9 or signal == 19) {
            try std.testing.expectError(error.Invalid, defaultTermination(signal));
            continue;
        }
        if (try defaultEffect(signal) == .terminate) {
            const terminal = try defaultTermination(signal);
            try std.testing.expectEqual(@as(u64, 4), terminal.kind);
            try std.testing.expectEqual(@as(u64, signal), terminal.detail);
        } else {
            try std.testing.expectError(error.Invalid, defaultTermination(signal));
        }
    }
    for ([_]u8{ 0, 32, 64, 255 }) |signal|
        try std.testing.expectError(error.Invalid, defaultTermination(signal));
    const interrupt = try defaultTermination(2);
    const segmentation = try defaultTermination(11);
    try std.testing.expectEqual(@as(u64, 2), interrupt.detail);
    try std.testing.expectEqual(@as(u64, 11), segmentation.detail);
}

test "public restart flags are inert only for default and ignore" {
    var s: State = .{};
    _ = try s.install(10, handler);
    try s.post(10);
    for ([_]u64{ 1, 0 }) |entry| {
        const record: Record = .{ .entry = entry, .flags = restorer_flag | restart_flag, .restorer = 0x202000, .mask = 4 };
        _ = try s.installPublicRecord(10, record);
        try std.testing.expectEqualDeep(record, try s.query(10));
        try std.testing.expect(s.peek(0) == null);
        const before = s;
        try std.testing.expectError(error.NotSupported, s.installRecord(10, record));
        for (0..64) |shift| {
            const flag = @as(u64, 1) << @intCast(shift);
            if (flag == restorer_flag or flag == restart_flag) continue;
            var bad = record;
            bad.flags |= flag;
            try std.testing.expectError(error.NotSupported, s.installPublicRecord(10, bad));
        }
        var custom = record;
        custom.entry = 0x201000;
        try std.testing.expectError(error.NotSupported, s.installPublicRecord(10, custom));
        try std.testing.expectEqualDeep(before, s);
    }
}

test "copy inherits exact dispositions but no pending occurrences" {
    var parent: State = .{};
    _ = try parent.install(10, handler);
    _ = try parent.installPublicRecord(12, .{ .entry = 1, .flags = restart_flag, .mask = 4 });
    _ = try parent.installRecord(64, .{ .entry = 1, .mask = 16 });
    try parent.post(10);
    try parent.post(10);
    try parent.post(2);
    const before = parent;
    var child: State = .{};
    child.inheritFrom(&parent);
    try std.testing.expectEqualDeep(before, parent);
    for (parent.records, child.records) |expected, observed| {
        try std.testing.expectEqualDeep(expected, observed);
    }
    try std.testing.expectEqual(@as(u32, 0), child.pending);
    try std.testing.expect(child.peek(0) == null);
    try std.testing.expect(parent.peek((1 << 9) | (1 << 1)) == null);
    try std.testing.expectEqual(@as(u8, 2), parent.peek(0).?.signal);
    try parent.commit(2);
    try std.testing.expectEqualDeep(handler, parent.peek(0).?.action);
    try parent.commit(10);
    try std.testing.expect(parent.peek(0) == null);
}

test "copied action mutations and delivery commits remain private" {
    var parent: State = .{};
    _ = try parent.install(10, handler);
    try parent.post(10);
    var child: State = .{};
    child.inheritFrom(&parent);
    const before = parent;
    _ = try child.install(10, .ignore);
    try child.post(10);
    try std.testing.expect(child.peek(0) == null);
    _ = try child.install(12, handler);
    try child.post(12);
    try std.testing.expectEqual(@as(u8, 12), child.peek(0).?.signal);
    try child.commit(12);
    try std.testing.expectEqualDeep(before, parent);
    const child_before = child;
    try parent.commit(10);
    _ = try parent.install(12, .ignore);
    try std.testing.expectEqualDeep(child_before, child);
    parent.reset();
    try std.testing.expectEqualDeep(child_before, child);
}

test "inheritance overwrites previous destination records and pending state" {
    var parent: State = .{};
    var child: State = .{};
    _ = try child.install(12, handler);
    try child.post(12);
    child.inheritFrom(&parent);
    try std.testing.expectEqualDeep(State{}, child);
    _ = try parent.install(10, handler);
    try parent.post(10);
    child.inheritFrom(&parent);
    const parent_before = parent;
    child.reset();
    try std.testing.expectEqualDeep(parent_before, parent);
    child.inheritFrom(&parent);
    try std.testing.expectEqualDeep(try parent.query(10), try child.query(10));
    try std.testing.expect(child.peek(0) == null);
}

test "image candidate preserves pending and ignored dispositions without old pointers" {
    var source = State{};
    _ = try source.install(12, handler);
    _ = try source.install(17, handler);
    _ = try source.installPublicRecord(15, .{ .entry = 1, .flags = restart_flag, .restorer = 0x203000, .mask = 4 });
    try source.post(12);
    try source.post(17);
    try source.post(10);
    const before = source;
    var candidate = source.forImage();
    try std.testing.expectEqualDeep(before, source);
    try std.testing.expectEqual(source.pending, candidate.pending);
    for (candidate.records, 0..) |record, i| {
        try std.testing.expectEqualDeep(Record{ .entry = if (i == 14) 1 else 0 }, record);
    }
    // A queued occurrence is retained even if its new default will ignore it.
    const selected = candidate.peek((1 << 9) | (1 << 11)).?;
    try std.testing.expectEqual(@as(u8, 17), selected.signal);
    try std.testing.expectEqual(Action.default, selected.action);
    try std.testing.expectEqual(DefaultEffect.ignore, try defaultEffect(selected.signal));
    try std.testing.expectEqualDeep(candidate, candidate.forImage());
    try candidate.commit(12);
    _ = try candidate.install(10, handler);
    try std.testing.expectEqualDeep(before, source);
}

test "readiness interruption excludes masks and retained ignored occurrences without dequeue" {
    var s: State = .{};
    _ = try s.install(17, handler);
    try s.post(17);
    s = s.forImage(); // Exec preserves pending; default SIGCHLD now ignores it.
    const ignored = s;
    try std.testing.expect(!s.interrupts(0));
    try std.testing.expectEqualDeep(ignored, s);
    _ = try s.install(10, handler);
    try s.post(10);
    const pending = s;
    try std.testing.expect(!s.interrupts(1 << 9));
    try std.testing.expect(s.interrupts(0));
    try std.testing.expect(s.interrupts(0));
    try std.testing.expectEqualDeep(pending, s);
    _ = try s.install(10, .ignore);
    try std.testing.expect(!s.interrupts(0));
}
