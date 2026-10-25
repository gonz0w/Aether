const std = @import("std");
pub const Error = error{ Busy, Exhausted, Invalid };

pub const Terminal = struct { generation: u32, reason: u64, detail: u64 };

// One boot-CPU factory quota. Architecture code owns the actual page tables
// and must complete flush/zero operations before finishing these transitions.
pub const Pool = struct {
    memory: enum { free, allocated, attached, detached, clearing } = .free,
    task: enum { free, created, running, finished, stopping } = .free,
    result: u64 = 0,
    generation: u32 = 0,
    terminal: ?Terminal = null,

    pub fn canAllocate(self: *const Pool) Error!void {
        if (self.memory != .free or self.generation == std.math.maxInt(u32)) return error.Exhausted;
        if (self.terminal != null) return error.Busy;
    }
    pub fn allocate(self: *Pool) Error!void {
        try self.canAllocate();
        self.memory = .allocated;
        self.generation += 1;
    }
    pub fn canCreate(self: *const Pool) Error!void {
        if (self.task != .free) return error.Exhausted;
        if (self.memory != .allocated) return error.Busy;
    }
    pub fn create(self: *Pool) Error!void {
        try self.canCreate();
        self.memory = .attached;
        self.task = .created;
        self.result = 0;
    }
    pub fn start(self: *Pool) Error!void {
        if (self.task != .created) return error.Busy;
        self.task = .running;
    }
    pub fn finish(self: *Pool, result: u64, detail: u64) void {
        std.debug.assert(self.task == .running);
        self.task = .finished;
        self.result = result;
        std.debug.assert(self.terminal == null);
        self.terminal = .{ .generation = self.generation, .reason = result, .detail = detail };
    }
    pub fn beginStop(self: *Pool) Error!void {
        if (self.task == .free or self.task == .stopping) return error.Busy;
        if (self.terminal == null) self.terminal = .{ .generation = self.generation, .reason = 3, .detail = 0 };
        self.task = .stopping;
    }
    pub fn completeStop(self: *Pool) void {
        std.debug.assert(self.task == .stopping);
        self.task = .free;
        self.memory = .detached;
        self.result = 0;
    }
    pub fn beginRelease(self: *Pool) Error!void {
        if (self.memory != .allocated and self.memory != .detached) return error.Busy;
        self.memory = .clearing;
    }
    pub fn acknowledge(self: *Pool, generation: u64) Error!void {
        const record = self.terminal orelse return error.Invalid;
        if (record.generation != generation) return error.Invalid;
        if (self.task != .free or self.memory != .free) return error.Busy;
        self.terminal = null;
    }
    pub fn completeRelease(self: *Pool) void {
        std.debug.assert(self.memory == .clearing);
        self.memory = .free;
    }
};

test "backing remains unavailable during task destruction and zeroing" {
    var pool = Pool{};
    try pool.allocate();
    try std.testing.expectError(error.Exhausted, pool.allocate());
    try pool.create();
    try std.testing.expectError(error.Exhausted, pool.create());
    try std.testing.expectError(error.Busy, pool.beginRelease());
    try pool.start();
    try std.testing.expectError(error.Busy, pool.start());
    pool.finish(2, 14);
    try std.testing.expectError(error.Busy, pool.start());
    try pool.beginStop();
    try std.testing.expectError(error.Busy, pool.beginRelease());
    try std.testing.expectError(error.Exhausted, pool.allocate());
    pool.completeStop();
    try std.testing.expectError(error.Busy, pool.create());
    try pool.beginRelease();
    try std.testing.expectError(error.Exhausted, pool.allocate());
    pool.completeRelease();
    try std.testing.expectError(error.Busy, pool.allocate());
    try pool.acknowledge(1);
    try pool.allocate();
    try std.testing.expectEqual(@as(u32, 2), pool.generation);
}

test "live task can be stopped and pool generation never wraps" {
    var pool = Pool{};
    try pool.allocate();
    try pool.create();
    try pool.start();
    try pool.beginStop();
    pool.completeStop();
    try std.testing.expectError(error.Busy, pool.create());
    try pool.beginRelease();
    pool.completeRelease();
    pool.generation = std.math.maxInt(u32);
    try std.testing.expectError(error.Exhausted, pool.allocate());
    try std.testing.expectEqual(.free, pool.memory);
}

test "terminal result survives destruction and release until matching acknowledgment" {
    var pool = Pool{};
    try pool.allocate();
    try pool.create();
    try pool.start();
    pool.finish(1, 110);
    try std.testing.expectError(error.Busy, pool.acknowledge(1));
    try pool.beginStop();
    pool.completeStop();
    try std.testing.expectEqual(@as(u64, 1), pool.terminal.?.reason);
    try std.testing.expectEqual(@as(u64, 110), pool.terminal.?.detail);
    try std.testing.expectError(error.Busy, pool.acknowledge(1));
    try pool.beginRelease();
    pool.completeRelease();
    try std.testing.expectError(error.Invalid, pool.acknowledge(2));
    try std.testing.expectError(error.Busy, pool.allocate());
    try pool.acknowledge(1);
    try std.testing.expectError(error.Invalid, pool.acknowledge(1));
    try pool.allocate();
    try pool.create();
    try pool.start();
    try pool.beginStop();
    pool.completeStop();
    try std.testing.expectEqual(@as(u64, 3), pool.terminal.?.reason);
    try std.testing.expectEqual(@as(u32, 2), pool.terminal.?.generation);
}
