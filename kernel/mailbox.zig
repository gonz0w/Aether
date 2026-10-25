const std = @import("std");

// Exactly one producer and one consumer. Four usable entries; one ring slot
// distinguishes full from empty. No user may write these control fields.
pub const Mailbox = struct {
    head: u32 align(64) = 0,
    tail: u32 align(64) = 0,
    data: [5]u64 = @splat(0),

    pub fn empty(self: *const Mailbox) bool {
        return @atomicLoad(u32, &self.head, .acquire) == @atomicLoad(u32, &self.tail, .acquire);
    }
    pub fn push(self: *Mailbox, value: u64) bool {
        const tail = @atomicLoad(u32, &self.tail, .monotonic);
        const next = (tail + 1) % 5;
        if (next == @atomicLoad(u32, &self.head, .acquire)) return false;
        self.data[tail] = value;
        @atomicStore(u32, &self.tail, next, .release);
        return true;
    }
    pub fn pop(self: *Mailbox) ?u64 {
        const head = @atomicLoad(u32, &self.head, .monotonic);
        if (head == @atomicLoad(u32, &self.tail, .acquire)) return null;
        const value = self.data[head];
        self.data[head] = 0;
        @atomicStore(u32, &self.head, (head + 1) % 5, .release);
        return value;
    }
};

test "bounded FIFO preserves queued data through full and wraparound" {
    var mailbox = Mailbox{};
    try std.testing.expectEqual(null, mailbox.pop());
    for (0..20) |round| {
        for (0..4) |i| try std.testing.expect(mailbox.push(round * 4 + i));
        try std.testing.expect(!mailbox.push(999));
        for (0..4) |i| try std.testing.expectEqual(@as(?u64, round * 4 + i), mailbox.pop());
        try std.testing.expectEqual(null, mailbox.pop());
    }
}
fn produce(mailbox: *Mailbox) void {
    for (0..10_000) |value| while (!mailbox.push(value)) std.atomic.spinLoopHint();
}
test "producer and consumer publish data across host threads" {
    var mailbox = Mailbox{};
    const thread = try std.Thread.spawn(.{}, produce, .{&mailbox});
    defer thread.join();
    var matched = true;
    for (0..10_000) |expected| {
        const received = while (true) {
            if (mailbox.pop()) |value| break value;
            std.atomic.spinLoopHint();
        };
        matched = matched and received == expected;
    }
    try std.testing.expect(matched);
}
