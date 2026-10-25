// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
const geometry = @import("backing_geometry.zig");
const Table = [512]u64;
const nx: u64 = 1 << 63;
const kernel_base: u64 = 0xffffffff80000000;
extern const kernel_end: u8;

pub const Partition = struct {
    first: usize,
    count: usize,
    pub fn init(owner: usize, owners: usize, quota: usize) geometry.Error!Partition {
        if (owners != 4 or owner >= owners or (quota != 128 and quota != 2048) or
            owners * quota > geometry.pages) return error.Invalid;
        return .{ .first = owner * quota, .count = quota };
    }
    pub fn service(owner: usize, owners: usize) geometry.Error!Partition {
        if (owners != 4 or owner >= owners) return error.Invalid;
        return if (owner == 0) .{ .first = 0, .count = 8192 } else .{ .first = 8192 + (owner - 1) * 128, .count = 128 };
    }
    // Explicit selection; service() continues to reject anything but four owners.
    pub fn filesystemSession(owner: usize, owners: usize) geometry.Error!Partition {
        const roles = @import("native_fs_roles.zig");
        if (owners != roles.domain_count) return error.Invalid;
        return .{ .first = roles.firstPage(owner) catch return error.Invalid, .count = roles.pages(owner) catch return error.Invalid };
    }
    pub fn filesystemApplication(owner: usize, owners: usize) geometry.Error!Partition {
        const roles = @import("native_fs_roles.zig");
        if (owners != roles.domain_count) return error.Invalid;
        return .{ .first = roles.applicationFirstPage(owner) catch return error.Invalid, .count = roles.applicationPages(owner) catch return error.Invalid };
    }
    pub fn frame(p: Partition, plan: geometry.Plan, index: usize) geometry.Error!u64 {
        if (index >= p.count) return error.Invalid;
        return plan.frame(p.first + index);
    }
    pub fn alias(p: Partition) usize {
        return geometry.base + p.first * geometry.page;
    }
};

// One kernel-instance-owned table object. The isolated BSP lab and private
// native binding use separate instances; no allocator or global cap table.
pub const Pool = struct {
    pdpt: Table align(4096) = @splat(0),
    pd: Table align(4096) = @splat(0),
    pts: [geometry.leaves]Table align(4096) = @splat(@splat(0)),
    plan: geometry.Plan = undefined,
    ready: bool = false,

    pub fn initialize(pool: *Pool, plan: geometry.Plan, pbase: u64) void {
        std.debug.assert(!pool.ready);
        pool.plan = plan;
        pool.pdpt[0] = imageFrame(&pool.pd, pbase) | 3;
        for (&pool.pts, 0..) |*pt, i| pool.pd[i] = imageFrame(pt, pbase) | 3;
        for (0..geometry.pages) |i| pool.pts[i / 512][i % 512] = (plan.frame(i) catch unreachable) | 3 | nx;
        pool.ready = true;
    }
    pub fn attach(pool: *const Pool, root: *Table, pbase: u64) void {
        std.debug.assert(pool.ready);
        const value = imageFrame(&pool.pdpt, pbase) | 3;
        const previous = root[geometry.base >> 39 & 511];
        std.debug.assert(previous == 0 or previous & ~@as(u64, 1 << 5) == value);
        root[geometry.base >> 39 & 511] = value;
    }
    pub fn entry(pool: *const Pool, index: usize) u64 {
        std.debug.assert(pool.ready and index < geometry.pages);
        return pool.pts[index / 512][index % 512];
    }
    // Caller owns the reference/mapping transition and required TLB flush.
    pub fn writable(pool: *Pool, index: usize, enabled: bool) void {
        std.debug.assert(pool.ready and index < geometry.pages);
        pool.pts[index / 512][index % 512] = (pool.plan.frame(index) catch unreachable) |
            (if (enabled) @as(u64, 3) else 1) | nx;
    }
};

fn imageFrame(pointer: anytype, pbase: u64) u64 {
    const address = @intFromPtr(pointer);
    std.debug.assert(address >= kernel_base and address < @intFromPtr(&kernel_end));
    return pbase + (address - kernel_base);
}

test "partitions stay disjoint at existing quotas and never expose retained tail" {
    const plan = try geometry.Plan.init(0x123000, geometry.bytes, 0xffff800000123000);
    for ([_]usize{ 128, 2048 }) |quota| {
        for (0..4) |owner| {
            const p = try Partition.init(owner, 4, quota);
            try std.testing.expectEqual(owner * quota, p.first);
            try std.testing.expectEqual(quota, p.count);
            try std.testing.expectEqual(@as(u64, 0x123000) + owner * quota * 4096, try p.frame(plan, 0));
            try std.testing.expectEqual(geometry.base + owner * quota * 4096, p.alias());
            _ = try p.frame(plan, quota - 1);
            try std.testing.expectError(error.Invalid, p.frame(plan, quota));
            if (owner != 0) {
                const previous = try Partition.init(owner - 1, 4, quota);
                try std.testing.expectEqual(try previous.frame(plan, quota - 1) + 4096, try p.frame(plan, 0));
            }
        }
    }
    for ([_][3]usize{ .{ 0, 0, 128 }, .{ 4, 4, 128 }, .{ 0, 7, 128 }, .{ 0, 4, 0 }, .{ 0, 4, 16384 } }) |args|
        try std.testing.expectError(error.Invalid, Partition.init(args[0], args[1], args[2]));
}

test "one service partition leaves three small disjoint owners and retained tail" {
    const plan = try geometry.Plan.init(0x123000, geometry.bytes, 0xffff800000123000);
    var stop: usize = 0;
    for (0..4) |owner| {
        const p = try Partition.service(owner, 4);
        try std.testing.expectEqual(stop, p.first);
        try std.testing.expectEqual(@as(usize, if (owner == 0) 8192 else 128), p.count);
        try std.testing.expectEqual(plan.physical + stop * 4096, try p.frame(plan, 0));
        try std.testing.expectError(error.Invalid, p.frame(plan, p.count));
        stop += p.count;
    }
    try std.testing.expect(stop < geometry.pages);
    try std.testing.expectError(error.Invalid, Partition.service(4, 4));
    try std.testing.expectError(error.Invalid, Partition.service(0, 6));
}

test "filesystem SESSION partitions expose exactly 35 MiB without changing old quotas" {
    const plan = try geometry.Plan.init(0x123000, geometry.bytes, 0xffff800000123000);
    var stop: usize = 0;
    for (0..7) |owner| {
        const p = try Partition.filesystemSession(owner, 7);
        try std.testing.expectEqual(stop, p.first);
        try std.testing.expectEqual(@as(usize, if (owner == 0) 8192 else 128), p.count);
        try std.testing.expectEqual(plan.physical + stop * 4096, try p.frame(plan, 0));
        try std.testing.expectEqual(geometry.base + stop * 4096, p.alias());
        try std.testing.expectEqual(plan.physical + (stop + p.count - 1) * 4096, try p.frame(plan, p.count - 1));
        try std.testing.expectError(error.Invalid, p.frame(plan, p.count));
        stop += p.count;
    }
    try std.testing.expectEqual(@as(usize, 8960), stop);
    try std.testing.expect(stop < geometry.pages);
    try std.testing.expectError(error.Invalid, Partition.filesystemSession(7, 7));
    try std.testing.expectError(error.Invalid, Partition.filesystemSession(0, 4));
    try std.testing.expectError(error.Invalid, Partition.service(0, 7));
    try std.testing.expectError(error.Invalid, Partition.init(0, 7, 128));
}

test "selected application partitions cannot borrow engine owner or ungranted tail" {
    const plan = try geometry.Plan.init(0x123000, geometry.bytes, 0xffff800000123000);
    var stop: usize = 0;
    for (0..7) |owner| {
        const p = try Partition.filesystemApplication(owner, 7);
        try std.testing.expectEqual(stop, p.first);
        try std.testing.expectEqual(plan.physical + stop * 4096, try p.frame(plan, 0));
        try std.testing.expectEqual(plan.physical + (stop + p.count - 1) * 4096, try p.frame(plan, p.count - 1));
        try std.testing.expectError(error.Invalid, p.frame(plan, p.count));
        try std.testing.expectEqual(geometry.base + stop * 4096, p.alias());
        stop += p.count;
    }
    try std.testing.expectEqual(@as(usize, 11520), stop);
    try std.testing.expectEqual(@as(usize, 4864), geometry.pages - stop);
    try std.testing.expectError(error.Invalid, Partition.filesystemApplication(7, 7));
    try std.testing.expectError(error.Invalid, Partition.filesystemApplication(0, 4));
    try std.testing.expectError(error.Invalid, Partition.service(0, 7));
    try std.testing.expectError(error.Invalid, Partition.init(0, 7, 640));
}
