const std = @import("std");

// One CPU's fixed runnable set. Task lifetime and backing remain separate.
pub const RunQueue = struct {
    runnable: [12]bool = @splat(false),

    pub fn next(self: *const RunQueue, after: usize) ?usize {
        for (1..self.runnable.len + 1) |offset| {
            const slot = (after + offset) % self.runnable.len;
            if (self.runnable[slot]) return slot;
        }
        return null;
    }
};

test "round robin wraps, skips stopped tasks, and reports an empty set" {
    var queue = RunQueue{};
    try std.testing.expectEqual(null, queue.next(0));
    queue.runnable[1] = true;
    queue.runnable[6] = true;
    try std.testing.expectEqual(@as(?usize, 6), queue.next(1));
    try std.testing.expectEqual(@as(?usize, 1), queue.next(6));
    queue.runnable[1] = false;
    try std.testing.expectEqual(@as(?usize, 6), queue.next(6));
    queue.runnable[6] = false;
    try std.testing.expectEqual(null, queue.next(6));
}
