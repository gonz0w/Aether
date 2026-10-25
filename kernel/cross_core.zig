const std = @import("std");
pub const Route = enum(u2) { request, reply, readiness };
pub const Right = enum { send, receive };
pub const Error = error{ Invalid, Denied };
const Entry = struct { route: Route, right: Right };

// One table per pinned worker. No slot reuse, transfer, or user-provided routing.
pub const Table = struct {
    namespace: u64,
    entries: [3]Entry,
    live: bool = true,
    count: usize = 3,

    pub fn bootstrap(boot: bool) Table {
        return .{
            .namespace = @as(u64, if (boot) 1 else 2) << 32,
            .entries = .{
                .{ .route = .request, .right = if (boot) .send else .receive },
                .{ .route = .reply, .right = if (boot) .receive else .send },
                .{ .route = .readiness, .right = if (boot) .receive else .send },
            },
        };
    }
    pub fn display(boot: bool) Table {
        var table = bootstrap(boot);
        table.namespace = @as(u64, if (boot) 4 else 5) << 32;
        table.count = 2;
        return table;
    }
    pub fn handle(self: *const Table, slot: usize) u64 {
        std.debug.assert(slot < self.count);
        return self.namespace | slot;
    }
    pub fn require(self: *const Table, reference: u64, right: Right) Error!Route {
        const slot = reference & 0xffffffff;
        if (!self.live or reference & 0xffffffff00000000 != self.namespace or slot >= self.count)
            return error.Invalid;
        const entry = self.entries[@intCast(slot)];
        if (entry.right != right) return error.Denied;
        return entry.route;
    }
};

test "bootstrap grants bind direction and reject foreign or forged handles" {
    var boot = Table.bootstrap(true);
    const peer = Table.bootstrap(false);
    try std.testing.expectEqual(Route.request, try boot.require(boot.handle(0), .send));
    try std.testing.expectEqual(Route.reply, try peer.require(peer.handle(1), .send));
    try std.testing.expectEqual(Route.readiness, try boot.require(boot.handle(2), .receive));
    try std.testing.expectError(error.Denied, boot.require(boot.handle(0), .receive));
    try std.testing.expectError(error.Denied, peer.require(peer.handle(1), .receive));
    try std.testing.expectError(error.Invalid, boot.require(peer.handle(0), .send));
    try std.testing.expectError(error.Invalid, boot.require(0, .send));
    try std.testing.expectError(error.Invalid, boot.require(boot.namespace | 3, .send));
    try std.testing.expectError(error.Invalid, boot.require(boot.namespace | (1 << 63), .send));
    boot.live = false;
    try std.testing.expectError(error.Invalid, boot.require(boot.handle(0), .send));
}

test "display grants cannot reuse M3 handles or access unused readiness route" {
    const table = Table.display(true);
    const old = Table.bootstrap(true);
    try std.testing.expectEqual(Route.request, try table.require(table.handle(0), .send));
    try std.testing.expectEqual(Route.reply, try table.require(table.handle(1), .receive));
    try std.testing.expectError(error.Invalid, table.require(old.handle(0), .send));
    try std.testing.expectError(error.Invalid, table.require(table.namespace | 2, .receive));
    try std.testing.expectError(error.Denied, table.require(table.handle(1), .send));
}
