const std = @import("std");
pub const generation_limit: u32 = 5;
pub const Phase = enum(u32) { running = 1, checkpoint = 2, stopped = 3, reclaimed = 4 };
pub const Error = error{ Invalid, Denied, Busy, Exhausted };
// AP-owned state. Published snapshots never transfer ownership to the BSP.
pub const Owner = struct {
    generation: u32 = 1,
    phase: Phase = .running,
    terminal: u64 = 0,
    pub fn snapshot(self: Owner) u64 {
        return (@as(u64, self.generation) << 32) | @intFromEnum(self.phase);
    }
    pub fn require(self: Owner, generation: u32, operation: u64) Error!void {
        if (generation != self.generation) return error.Invalid;
        const expected: Phase = switch (operation) {
            50 => .checkpoint,
            52 => .stopped,
            53 => .reclaimed,
            else => return error.Invalid,
        };
        if (self.phase != expected) return error.Busy;
        if (operation == 53 and self.generation >= generation_limit) return error.Exhausted;
    }
    pub fn terminate(self: *Owner, reason: u32, detail: u32) Error!void {
        if ((self.phase != .running and self.phase != .checkpoint) or self.terminal != 0) return error.Busy;
        self.terminal = (@as(u64, reason) << 32) | detail;
        self.phase = .stopped;
    }
    // Called only after the owner has completed the associated hardware work.
    pub fn commit(self: *Owner, operation: u64) void {
        switch (operation) {
            50 => self.terminate(3, 0) catch unreachable,
            52 => self.phase = .reclaimed,
            53 => {
                self.generation += 1;
                self.terminal = 0;
                self.phase = .running;
            },
            else => unreachable,
        }
    }
};
pub fn handle(generation: u32, observe_only: bool) u64 {
    return (@as(u64, generation) << 32) | 0x100 | @intFromBool(observe_only);
}
pub fn requireHandle(reference: u64, generation: u32, mutate: bool) Error!void {
    if (reference != handle(generation, false) and reference != handle(generation, true)) return error.Invalid;
    if (mutate and reference == handle(generation, true)) return error.Denied;
}
test "remote lifetime gates reuse on cleanup and retires exhausted generations" {
    var owner = Owner{};
    try std.testing.expectError(error.Busy, owner.require(1, 52));
    try std.testing.expectError(error.Busy, owner.require(1, 53));
    owner.phase = .checkpoint;
    try owner.require(1, 50);
    owner.commit(50);
    try std.testing.expectError(error.Busy, owner.require(1, 53));
    try owner.require(1, 52);
    owner.commit(52);
    try owner.require(1, 53);
    owner.commit(53);
    try std.testing.expectEqual(@as(u32, 2), owner.generation);
    try std.testing.expectError(error.Invalid, owner.require(1, 50));
    try std.testing.expectError(error.Invalid, requireHandle(handle(1, false), 2, true));
    try std.testing.expectError(error.Denied, requireHandle(handle(2, true), 2, true));
    try std.testing.expectError(error.Invalid, requireHandle(0, 2, false));
    owner.phase = .reclaimed;
    owner.generation = generation_limit;
    try std.testing.expectError(error.Exhausted, owner.require(generation_limit, 53));
    owner.generation = std.math.maxInt(u32);
    owner.phase = .reclaimed;
    try std.testing.expectError(error.Exhausted, owner.require(owner.generation, 53));
}

test "fault and forced-stop records survive reclaim across the bounded pool lifetime" {
    var owner = Owner{};
    for (1..generation_limit + 1) |generation| {
        const fault = generation % 2 == 0;
        try owner.terminate(if (fault) 2 else 3, if (fault) 6 else 0);
        const terminal = owner.terminal;
        try std.testing.expectError(error.Busy, owner.terminate(2, 14));
        try std.testing.expectEqual(terminal, owner.terminal);
        try owner.require(@intCast(generation), 52);
        owner.commit(52);
        try std.testing.expectEqual(terminal, owner.terminal);
        if (generation < generation_limit) {
            try owner.require(@intCast(generation), 53);
            owner.commit(53);
            try std.testing.expectEqual(@as(u64, 0), owner.terminal);
            try std.testing.expectError(error.Invalid, owner.require(@intCast(generation), 52));
        }
    }
    try std.testing.expectError(error.Exhausted, owner.require(generation_limit, 53));
}
