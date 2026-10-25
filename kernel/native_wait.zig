// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
pub const Wait = struct {
    generation: u64 = 0,
    occupied: bool = false,
    target: u64 = 0,
    revision: u64 = 0,
    deadline: u64 = 0,
    status: u64 = 0,
    completed: u64 = 0,
    pub fn token(w: *const Wait) u64 {
        return 0xe1000000 | w.generation;
    }
    pub fn valid(w: *const Wait, value: u64) bool {
        return w.occupied and value == w.token();
    }
    pub fn refresh(w: *Wait, now: u64, revision: ?u64) void {
        if (!w.occupied or w.status != 0) return;
        if (now >= w.deadline) w.status = 2 else if (revision == null) w.status = 4 else if (revision.? != w.revision) w.status = 1;
        if (w.status != 0) {
            if (revision) |r| w.revision = r;
            w.completed = now;
        }
    }
    pub fn register(w: *Wait, target: u64, revision: u64, deadline: u64, now: u64, current: u64) i64 {
        if (revision > current) return -22;
        if (w.occupied) return -16;
        if (w.generation == 64) return -28;
        w.* = .{ .generation = w.generation + 1, .occupied = true, .target = target, .revision = revision, .deadline = deadline };
        w.refresh(now, current);
        return @intCast(w.token());
    }
    pub fn cancel(w: *Wait, now: u64) void {
        if (w.status == 0) {
            w.status = 3;
            w.completed = now;
        }
    }
};
test "registration ordering, retained event, deadline tie, cancel and reclaim" {
    var w: Wait = .{};
    _ = w.register(1, 0, 10, 2, 1); // event before registration
    try std.testing.expectEqual(1, w.status);
    w.refresh(11, null);
    try std.testing.expectEqual(1, w.status);
    w.occupied = false;
    _ = w.register(1, 1, 10, 2, 1); // event after atomic registration
    w.refresh(3, 2);
    try std.testing.expectEqual(1, w.status);
    w.occupied = false;
    _ = w.register(1, 0, 10, 10, 1);
    try std.testing.expectEqual(2, w.status);
    w.occupied = false;
    _ = w.register(1, 1, 20, 10, 1);
    w.cancel(11);
    w.refresh(12, 2);
    try std.testing.expectEqual(3, w.status);
    w.occupied = false;
    _ = w.register(1, 1, 20, 10, 1);
    w.refresh(11, null);
    try std.testing.expectEqual(4, w.status);
}
test "bounded slots retire without token aliasing" {
    var w: Wait = .{};
    for (0..64) |_| {
        const old = w.token();
        const t = w.register(1, 0, 9, 0, 0);
        try std.testing.expect(t > 0 and !w.valid(old));
        try std.testing.expectEqual(-16, w.register(1, 0, 9, 0, 0));
        w.occupied = false;
        try std.testing.expect(!w.valid(@intCast(t)));
    }
    try std.testing.expectEqual(-28, w.register(1, 0, 9, 0, 0));
}
