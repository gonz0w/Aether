const std = @import("std");
pub const send_right = 1;
pub const receive_right = 2;
pub const derive_right = 4;
pub const revoke_right = 8;
pub const destroy_right = 16;
pub const Error = error{ Invalid, Denied, Exhausted, Full, Empty, Busy };
const Slot = struct { generation: u32 = 1, node: ?usize = null, retired: bool = false };
pub const Object = enum { endpoint, factory, task, memory };
const Node = struct { holder: usize, slot: usize, rights: u8, parent: ?usize, object: Object };

// Owned by one CPU, entered only with interrupts disabled. No remote access.
pub const Owner = struct {
    slots: [12][8]Slot = @splat(@splat(.{})),
    nodes: [32]?Node = @splat(null),
    queue: [4]u64 = @splat(0),
    head: usize = 0,
    count: usize = 0,
    live: bool = true,

    fn allocate(self: *Owner, holder: usize, rights: u8, parent: ?usize, object: Object) Error!u64 {
        if ((object == .endpoint and !self.live) or holder >= self.slots.len) return error.Invalid;
        const slot = for (self.slots[holder], 0..) |entry, i| {
            if (entry.node == null and !entry.retired) break i;
        } else return error.Exhausted;
        const node = for (self.nodes, 0..) |entry, i| {
            if (entry == null) break i;
        } else return error.Exhausted;
        self.nodes[node] = .{ .holder = holder, .slot = slot, .rights = rights, .parent = parent, .object = object };
        self.slots[holder][slot].node = node;
        return (@as(u64, self.slots[holder][slot].generation) << 32) | slot;
    }
    // Trusted bootstrap only; no syscall exposes this operation.
    pub fn grant(self: *Owner, holder: usize, rights: u8) Error!u64 {
        if (rights == 0 or rights & ~@as(u8, 31) != 0) return error.Denied;
        return self.grantObject(holder, rights, .endpoint);
    }
    pub fn grantObject(self: *Owner, holder: usize, rights: u8, object: Object) Error!u64 {
        const allowed: u8 = if (object == .factory) 63 else 31;
        if (rights == 0 or rights & ~allowed != 0) return error.Denied;
        return self.allocate(holder, rights, null, object);
    }
    pub fn require(self: *Owner, holder: usize, handle: u64, object: Object, rights: u8) Error!void {
        const node = try self.resolve(holder, handle, 0);
        if (self.nodes[node].?.object != object) return error.Invalid;
        if (self.nodes[node].?.rights & rights != rights) return error.Denied;
    }
    // Kernel-only: invalidate every reference before reusing a local object.
    pub fn invalidate(self: *Owner, object: Object) void {
        for (self.nodes, 0..) |entry, i| if (entry) |node| {
            if (node.object == object) self.remove(i);
        };
    }
    fn resolve(self: *Owner, holder: usize, handle: u64, rights: u8) Error!usize {
        const slot: u32 = @truncate(handle);
        if (holder >= self.slots.len or slot >= 8) return error.Invalid;
        const entry = self.slots[holder][slot];
        if (entry.generation != handle >> 32) return error.Invalid;
        const node = entry.node orelse return error.Invalid;
        if (self.nodes[node].?.rights & rights != rights) return error.Denied;
        return node;
    }
    pub fn send(self: *Owner, holder: usize, handle: u64, value: u64) Error!void {
        try self.require(holder, handle, .endpoint, send_right);
        if (self.count == self.queue.len) return error.Full;
        self.queue[(self.head + self.count) % self.queue.len] = value;
        self.count += 1;
    }
    pub fn receive(self: *Owner, holder: usize, handle: u64) Error!u64 {
        try self.require(holder, handle, .endpoint, receive_right);
        if (self.count == 0) return error.Empty;
        const value = self.queue[self.head];
        self.queue[self.head] = 0;
        self.head = (self.head + 1) % self.queue.len;
        self.count -= 1;
        return value;
    }
    pub fn derive(self: *Owner, holder: usize, handle: u64, rights: u64) Error!u64 {
        const parent = try self.resolve(holder, handle, derive_right);
        if (rights == 0 or rights & ~@as(u64, self.nodes[parent].?.rights) != 0) return error.Denied;
        return self.allocate(holder, @intCast(rights), parent, self.nodes[parent].?.object);
    }
    fn remove(self: *Owner, node: usize) void {
        const entry = self.nodes[node].?;
        const slot = &self.slots[entry.holder][entry.slot];
        slot.node = null;
        if (slot.generation == std.math.maxInt(u32)) slot.retired = true else slot.generation += 1;
        self.nodes[node] = null;
    }
    pub fn revoke(self: *Owner, holder: usize, handle: u64) Error!void {
        const root = try self.resolve(holder, handle, revoke_right);
        var removed: [32]bool = @splat(false);
        for (self.nodes, 0..) |entry, i| {
            var parent = if (entry) |node| node.parent else null;
            while (parent) |p| {
                if (p == root) {
                    removed[i] = true;
                    break;
                }
                parent = self.nodes[p].?.parent;
            }
        }
        for (removed, 0..) |yes, i| if (yes) {
            self.remove(i);
        };
    }
    pub fn close(self: *Owner, holder: usize, handle: u64) Error!void {
        const node = try self.resolve(holder, handle, 0);
        for (self.nodes) |entry| if (entry) |child| {
            if (child.parent == node) return error.Busy;
        };
        self.remove(node);
    }
    pub fn destroy(self: *Owner, holder: usize, handle: u64) Error!void {
        try self.require(holder, handle, .endpoint, destroy_right);
        self.invalidate(.endpoint);
        self.queue = @splat(0);
        self.count = 0;
        self.head = 0;
        self.live = false;
    }
};

test "rights, FIFO backpressure, and empty receive are atomic" {
    var owner = Owner{};
    const send = try owner.grant(0, send_right);
    const recv = try owner.grant(1, receive_right);
    try std.testing.expectError(error.Invalid, owner.send(2, send, 1));
    try std.testing.expectError(error.Denied, owner.send(1, recv, 1));
    for (0..4) |i| try owner.send(0, send, i);
    try std.testing.expectError(error.Full, owner.send(0, send, 99));
    for (0..4) |i| try std.testing.expectEqual(i, try owner.receive(1, recv));
    try std.testing.expectError(error.Empty, owner.receive(1, recv));
}

test "descendant revocation, leaf close, stale slots and exhaustion" {
    var owner = Owner{};
    const root = try owner.grant(0, 31);
    const child = try owner.derive(0, root, 13);
    const grandchild = try owner.derive(0, child, 1);
    try std.testing.expectError(error.Denied, owner.derive(0, child, 2));
    try std.testing.expectError(error.Busy, owner.close(0, child));
    try owner.revoke(0, root);
    try std.testing.expectError(error.Invalid, owner.send(0, grandchild, 1));
    try std.testing.expectError(error.Invalid, owner.send(0, child, 1));
    const fresh = try owner.derive(0, root, 1);
    try std.testing.expect(fresh != child);
    for (0..6) |_| _ = try owner.derive(0, root, 1);
    try std.testing.expectError(error.Exhausted, owner.derive(0, root, 1));
    try owner.revoke(0, root);
    try owner.close(0, root);
}

test "generation retirement, node exhaustion, and endpoint destruction" {
    var owner = Owner{};
    owner.slots[0][0].generation = std.math.maxInt(u32);
    const last = try owner.grant(0, 31);
    try owner.close(0, last);
    try std.testing.expect(owner.slots[0][0].retired);
    const fresh = try owner.grant(0, 31);
    try std.testing.expectEqual(@as(u32, 1), @as(u32, @truncate(fresh)));
    try std.testing.expectError(error.Invalid, owner.send(0, last, 1));
    for (1..5) |holder| for (0..if (holder == 4) @as(usize, 7) else 8) |_| {
        _ = try owner.grant(holder, 1);
    };
    try std.testing.expectError(error.Exhausted, owner.grant(5, 1));
    try std.testing.expectEqual(null, owner.slots[5][0].node);
    try owner.send(0, fresh, 99);
    try owner.destroy(0, fresh);
    try std.testing.expectEqual(@as(usize, 0), owner.count);
    try std.testing.expectEqual(@as(u64, 0), owner.queue[0]);
    try std.testing.expectError(error.Invalid, owner.send(0, fresh, 1));
    try std.testing.expectError(error.Invalid, owner.grant(0, 1));
}

test "typed authority cannot be confused and destruction is object-scoped" {
    var owner = Owner{};
    const endpoint = try owner.grant(0, 31);
    const factory = try owner.grantObject(0, 3, .factory);
    const task = try owner.grantObject(0, 31, .task);
    const child = try owner.derive(0, task, 1);
    try std.testing.expectError(error.Invalid, owner.send(0, factory, 1));
    try std.testing.expectError(error.Invalid, owner.require(0, endpoint, .task, 1));
    try owner.destroy(0, endpoint);
    try owner.require(0, factory, .factory, 3);
    owner.invalidate(.task);
    try std.testing.expectError(error.Invalid, owner.require(0, child, .task, 1));
    const fresh = try owner.grantObject(0, 3, .task);
    try std.testing.expect(fresh != task);
    try std.testing.expectError(error.Invalid, owner.require(0, task, .task, 1));
}

test "acknowledgment right is confined to factory bootstrap and attenuates" {
    var owner = Owner{};
    try std.testing.expectError(error.Denied, owner.grantObject(10, 32, .task));
    const factory = try owner.grantObject(10, 63, .factory);
    const observer = try owner.derive(10, factory, 16);
    try owner.require(10, factory, .factory, 32);
    try std.testing.expectError(error.Denied, owner.require(10, observer, .factory, 32));
    try std.testing.expectError(error.Invalid, owner.require(11, factory, .factory, 32));
}
