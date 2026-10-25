// SPDX-License-Identifier: BSD-2-Clause
// Pure validation/reservation for the bounded caller-local native memory profile.
const std = @import("std");
pub const base: usize = 0x10000000;
pub const page_size: usize = 4096;
pub const nx = @as(u64, 1) << 63;
pub const Page = struct { address: usize = 0, flags: u64 = 0, anonymous: bool = false };
pub const Error = error{ Invalid, Denied, Exhausted };
pub const leaf_span = 512 * page_size;
pub const table_capacity = 32;
pub const vacant_table = std.math.maxInt(usize);
pub const TableReservation = struct { directory: usize, slot: usize, fresh: bool };
pub const TablePlan = struct {
    count: usize = 0,
    entries: [table_capacity]TableReservation = undefined,

    pub fn slot(self: *const TablePlan, address: usize) usize {
        const directory = address / leaf_span;
        for (self.entries[0..self.count]) |entry| {
            if (entry.directory == directory) return entry.slot;
        }
        unreachable; // Only addresses in the successfully reserved range are used.
    }
};

// Borrowed owner-local metadata only. The caller commits the returned plan while
// mutation/dispatch remains excluded; no table or backing bytes change here.
pub fn tables(indices: []const usize, total: usize, address: usize, count: usize, create: bool) Error!TablePlan {
    if (total > table_capacity or indices.len > total or count == 0 or
        address % page_size != 0 or address >= 512 * leaf_span or
        count > (512 * leaf_span - address) / page_size) return error.Invalid;
    for (indices, 0..) |directory, i| {
        if (directory == vacant_table) continue;
        if (directory >= 512) return error.Invalid;
        for (indices[0..i]) |prior| if (prior == directory) return error.Invalid;
    }
    const first = address / leaf_span;
    const last = (address + count * page_size - 1) / leaf_span;
    if (last - first + 1 > total) return error.Exhausted;
    var plan = TablePlan{};
    var reserved = [_]bool{false} ** table_capacity;
    for (first..last + 1) |directory| {
        var selected: ?usize = null;
        for (indices, 0..) |existing, i| {
            if (existing == directory) selected = i;
        }
        const fresh = selected == null;
        if (fresh) {
            if (!create) return error.Exhausted;
            for (0..total) |i| {
                if (!reserved[i] and (i >= indices.len or indices[i] == vacant_table)) {
                    selected = i;
                    break;
                }
            }
        }
        const chosen = selected orelse return error.Exhausted;
        reserved[chosen] = true;
        plan.entries[plan.count] = .{ .directory = directory, .slot = chosen, .fresh = fresh };
        plan.count += 1;
    }
    return plan;
}
pub fn flags(prot: u64) Error!u64 {
    if (prot & ~@as(u64, 7) != 0) return error.Invalid;
    if (prot & 4 != 0 or prot == 2) return error.Denied;
    return switch (prot) {
        0 => nx,
        1 => 5 | nx,
        3 => 7 | nx,
        else => error.Invalid,
    };
}
pub fn length(bytes: u64) Error!usize {
    if (bytes == 0 or bytes > std.math.maxInt(usize) - (page_size - 1)) return error.Invalid;
    return (@as(usize, @intCast(bytes)) + (page_size - 1)) / page_size;
}
pub fn Arena(comptime quota: usize) type {
    if (quota == 0 or quota > 8192) @compileError("unsupported native memory quota");
    return struct {
        const Records = if (quota == 8192) []const Page else *const [quota]Page;
        pub const page_count = quota;
        pub const arena_end = base + quota * page_size;
        // Only successful constructors issue plans. The authoritative owner keeps
        // metadata stable through preflight/commit; visited records may change.
        pub const Plan = struct {
            address: usize,
            count: usize,

            // A range constructor already checked bounds and coverage. Under
            // the same owner serialization, only context pins differ; do not
            // rescan unchanged mappings for each live child. No pointer retained.
            pub fn checkPins(self: Plan, fs: u64, clear_tid: usize) Error!void {
                const stop = self.address + self.count * page_size;
                // FS may use negative TLS offsets: pin its preceding page too.
                const fs_start = if (fs >= page_size) (fs & ~@as(u64, page_size - 1)) - page_size else 0;
                const fs_end = (fs & ~@as(u64, page_size - 1)) + page_size;
                if (fs != 0 and self.address < fs_end and stop > fs_start) return error.Denied;
                if (clear_tid != 0 and self.address < clear_tid + 4 and stop > clear_tid) return error.Denied;
            }

            // Range order remains virtual-address order even when backing records
            // are fragmented. No quota-sized snapshot is placed on the stack.
            pub fn slot(self: Plan, pages: Records, offset: usize) usize {
                std.debug.assert(offset < self.count);
                const address = self.address + offset * page_size;
                for (pages, 0..) |record, index| if (record.address == address and record.anonymous) return index;
                @panic("native range plan metadata changed");
            }

            // Map only: preflight already proved count free records. Advancing
            // before returning permits the caller to publish each visited record.
            pub fn freeSlots(self: Plan, pages: Records) FreeSlots {
                return .{ .pages = pages, .remaining = self.count };
            }

            // Range only: the owner guarantees unique addresses and excludes
            // mutation/dispatch except for already visited records during commit.
            pub fn rangeSlots(self: Plan, pages: Records) RangeSlots {
                return .{ .pages = pages, .plan = self, .remaining = self.count };
            }
        };
        pub const RangeSlots = struct {
            pages: Records,
            plan: Plan,
            remaining: usize,
            cursor: usize = 0,
            pub fn next(self: *RangeSlots) ?usize {
                if (self.remaining == 0) return null;
                while (self.cursor < self.pages.len) {
                    const index = self.cursor;
                    self.cursor += 1;
                    const record = self.pages[index];
                    if (record.anonymous and record.address >= self.plan.address and
                        record.address < self.plan.address + self.plan.count * page_size)
                    {
                        self.remaining -= 1;
                        return index;
                    }
                }
                @panic("native range plan metadata changed");
            }
        };
        pub const FreeSlots = struct {
            pages: Records,
            remaining: usize,
            cursor: usize = 0,
            pub fn next(self: *FreeSlots) ?usize {
                if (self.remaining == 0) return null;
                while (self.cursor < self.pages.len) {
                    const index = self.cursor;
                    self.cursor += 1;
                    if (self.pages[index].address == 0) {
                        self.remaining -= 1;
                        return index;
                    }
                }
                @panic("native map plan metadata changed");
            }
        };
        pub const Limits = struct { backing: usize = quota, records: usize = quota, arena: usize = quota, table_available: bool = true, fail_after: ?usize = null };
        pub fn used(pages: Records) usize {
            var n: usize = 0;
            for (pages) |p| if (p.address != 0) {
                n += 1;
            };
            return n;
        }
        pub fn map(pages: Records, bytes: u64, prot: u64, limits: Limits) Error!Plan {
            if (pages.len == 0 or pages.len > quota) return error.Invalid;
            _ = try flags(prot);
            const n = try length(bytes);
            const live = @This().used(pages);
            if (n > limits.arena or live > @min(limits.backing, pages.len) or n > @min(limits.backing, pages.len) - live or
                live > @min(limits.records, pages.len) or n > @min(limits.records, pages.len) - live or !limits.table_available) return error.Exhausted;
            var start: usize = 0;
            var run: usize = 0;
            if (quota == 8192) {
                var occupied = std.StaticBitSet(quota).initEmpty();
                for (pages) |p| {
                    if (p.address >= base and p.address < base + pages.len * page_size and p.address % page_size == 0)
                        occupied.set((p.address - base) / page_size);
                }
                for (0..@min(limits.arena, pages.len)) |a| {
                    if (occupied.isSet(a)) {
                        run = 0;
                    } else {
                        if (run == 0) start = a;
                        run += 1;
                        if (run == n) break;
                    }
                }
            } else {
                for (0..@min(limits.arena, pages.len)) |a| {
                    var occupied = false;
                    for (pages) |p| if (p.address == base + a * page_size) {
                        occupied = true;
                        break;
                    };
                    if (occupied) {
                        run = 0;
                    } else {
                        if (run == 0) start = a;
                        run += 1;
                        if (run == n) break;
                    }
                }
            }
            if (run != n) return error.Exhausted;
            const plan = Plan{ .address = base + start * page_size, .count = n };
            var selected: usize = 0;
            for (pages) |p| if (p.address == 0) {
                if (limits.fail_after == selected) return error.Exhausted;
                selected += 1;
                if (selected == n) return plan;
            };
            return error.Exhausted;
        }
        pub fn range(pages: Records, address: u64, bytes: u64, fs: u64, clear_tid: usize) Error!Plan {
            if (pages.len == 0 or pages.len > quota) return error.Invalid;
            const n = try length(bytes);
            if (address % page_size != 0 or address > std.math.maxInt(usize) - n * page_size) return error.Invalid;
            const stop = address + n * page_size;
            // Immutable image/stack and other regions are outside the granted arena.
            if (address < base or stop > base + pages.len * page_size) return error.Denied;
            const plan = Plan{ .address = @intCast(address), .count = n };
            try plan.checkPins(fs, clear_tid);
            if (quota == 8192) {
                var covered = std.StaticBitSet(quota).initEmpty();
                for (pages) |p| {
                    if (p.anonymous and p.address >= address and p.address < stop and p.address % page_size == 0)
                        covered.set((p.address - @as(usize, @intCast(address))) / page_size);
                }
                for (0..n) |i| if (!covered.isSet(i)) return error.Exhausted;
            } else {
                for (0..n) |i| {
                    var found = false;
                    for (pages) |p| if (p.address == address + i * page_size and p.anonymous) {
                        found = true;
                        break;
                    };
                    if (!found) return error.Exhausted;
                }
            }
            return plan;
        }
    };
}
pub const Default = Arena(128);
pub const capacity = Default.page_count;
pub const end = Default.arena_end;
pub const used = Default.used;
pub const map = Default.map;
pub const range = Default.range;

test "reservations are atomic under isolated resource and reservation failures" {
    var pages = [_]Page{.{}} ** capacity;
    pages[0] = .{ .address = 0x200000 };
    const before = pages;
    for ([_]Default.Limits{ .{ .backing = 2 }, .{ .records = 2 }, .{ .arena = 1 }, .{ .table_available = false }, .{ .fail_after = 0 }, .{ .fail_after = 1 } }) |limits| {
        try std.testing.expectError(error.Exhausted, map(&pages, 8192, 3, limits));
        try std.testing.expectEqualDeep(before, pages);
    }
    const p = try map(&pages, 8192, 0, .{});
    try std.testing.expectEqual(@as(usize, 2), p.count);
    var slots = p.freeSlots(&pages);
    try std.testing.expectEqual(@as(usize, 1), slots.next().?);
    try std.testing.expectEqualDeep(before, pages);
}
test "subranges holes fragmentation and pinned ranges" {
    var pages = [_]Page{.{}} ** capacity;
    for (0..4) |i| pages[i] = .{ .address = base + i * page_size, .anonymous = true };
    const p = try range(&pages, base + page_size, page_size, 0, 0);
    try std.testing.expectEqual(@as(usize, 1), p.slot(&pages, 0));
    try std.testing.expectError(error.Denied, range(&pages, base, page_size, base + page_size + 8, 0));
    try std.testing.expectError(error.Denied, range(&pages, base, page_size, 0, base + 100));
    pages[1] = .{};
    try std.testing.expectError(error.Exhausted, range(&pages, base, 3 * page_size, 0, 0));
    try std.testing.expectError(error.Exhausted, map(&pages, 2 * page_size, 3, .{ .arena = 4 }));
    const reuse = try map(&pages, page_size, 3, .{});
    try std.testing.expectEqual(base + page_size, reuse.address);
}
test "invalid arithmetic permissions and immutable ranges" {
    const pages = [_]Page{.{}} ** capacity;
    try std.testing.expectError(error.Invalid, map(&pages, 0, 3, .{}));
    try std.testing.expectError(error.Invalid, map(&pages, std.math.maxInt(u64), 3, .{}));
    for ([_]u64{ 2, 4, 5, 6, 7 }) |p| try std.testing.expectError(error.Denied, flags(p));
    try std.testing.expectError(error.Invalid, flags(8));
    try std.testing.expectError(error.Invalid, range(&pages, std.math.maxInt(u64) - 4095, 4096, 0, 0));
    try std.testing.expectError(error.Denied, range(&pages, 0x8000000, 4096, 0, 0));
}

test "table reservation spans boundaries and reuses holes before growth" {
    const indices = [_]usize{ 7, vacant_table, 3 };
    const before = indices;
    // One page in directory 2, all of 3, one page in 4.
    const p = try tables(&indices, 4, 3 * leaf_span - page_size, 514, true);
    try std.testing.expectEqual(@as(usize, 3), p.count);
    try std.testing.expectEqualDeep(TableReservation{ .directory = 2, .slot = 1, .fresh = true }, p.entries[0]);
    try std.testing.expectEqualDeep(TableReservation{ .directory = 3, .slot = 2, .fresh = false }, p.entries[1]);
    try std.testing.expectEqualDeep(TableReservation{ .directory = 4, .slot = 3, .fresh = true }, p.entries[2]);
    try std.testing.expectEqual(@as(usize, 1), p.slot(3 * leaf_span - page_size));
    try std.testing.expectEqual(@as(usize, 2), p.slot(3 * leaf_span));
    try std.testing.expectEqual(@as(usize, 3), p.slot(4 * leaf_span));
    try std.testing.expectEqualDeep(before, indices);
    const exact = try tables(&.{3}, 1, 3 * leaf_span, 512, false);
    try std.testing.expectEqual(@as(usize, 1), exact.count);
    try std.testing.expect(!exact.entries[0].fresh);
}

test "late table exhaustion and missing existing table leave metadata unchanged" {
    const indices = [_]usize{ 7, vacant_table, 3 };
    const before = indices;
    // Total count alone fits, but directory 7 consumes a slot outside the range.
    try std.testing.expectError(error.Exhausted, tables(&indices, 3, 2 * leaf_span, 1025, true));
    try std.testing.expectError(error.Exhausted, tables(&indices, 4, 3 * leaf_span, 513, false));
    try std.testing.expectEqualDeep(before, indices);
    const retry = try tables(&indices, 3, 2 * leaf_span, 513, true);
    try std.testing.expectEqual(@as(usize, 1), retry.entries[0].slot);
    try std.testing.expectEqual(@as(usize, 2), retry.entries[1].slot);
}

test "table reservation rejects invalid geometry and respects fixed bounds" {
    try std.testing.expectError(error.Invalid, tables(&.{}, 33, 0, 1, true));
    try std.testing.expectError(error.Invalid, tables(&.{1}, 0, 0, 1, true));
    try std.testing.expectError(error.Invalid, tables(&.{ 1, 1 }, 2, 0, 1, true));
    try std.testing.expectError(error.Invalid, tables(&.{512}, 1, 0, 1, true));
    try std.testing.expectError(error.Invalid, tables(&.{}, 1, 1, 1, true));
    try std.testing.expectError(error.Invalid, tables(&.{}, 1, 0, 0, true));
    try std.testing.expectError(error.Invalid, tables(&.{}, 1, 0, std.math.maxInt(usize), true));
    try std.testing.expectError(error.Invalid, tables(&.{}, 1, 512 * leaf_span, 1, true));
    try std.testing.expectError(error.Invalid, tables(&.{}, 1, 512 * leaf_span - page_size, 2, true));
    try std.testing.expectError(error.Exhausted, tables(&.{}, 0, 0, 1, true));
    try std.testing.expectError(error.Exhausted, tables(&.{}, 32, 0, 32 * 512 + 1, true));
    const full = try tables(&.{}, 32, 0, 32 * 512, true);
    for (full.entries, 0..) |entry, i| {
        try std.testing.expectEqual(i, entry.slot);
        try std.testing.expectEqual(i, entry.directory);
        try std.testing.expect(entry.fresh);
    }
    const last = try tables(&.{}, 1, 512 * leaf_span - page_size, 1, true);
    try std.testing.expectEqual(@as(usize, 511), last.entries[0].directory);
}

test "large arena preserves wide backing slots and exact quota" {
    const Large = Arena(2048);
    var pages = [_]Page{.{}} ** Large.page_count;
    for (0..24) |i| pages[i] = .{ .address = 0x200000 + i * page_size };
    const before = pages;
    const p = try Large.map(&pages, 2024 * page_size, 3, .{});
    var last_slots = p.freeSlots(&pages);
    var last_slot: usize = 0;
    while (last_slots.next()) |slot| last_slot = slot;
    try std.testing.expectEqual(@as(usize, 2047), last_slot);
    try std.testing.expectError(error.Exhausted, Large.map(&pages, 2025 * page_size, 3, .{}));
    try std.testing.expectEqualDeep(before, pages);
    var selected = p.freeSlots(&pages);
    for (0..p.count) |i| pages[selected.next().?] = .{ .address = base + i * page_size, .anonymous = true };
    try std.testing.expect(selected.next() == null);
    const r = try Large.range(&pages, base + 511 * page_size, 2 * page_size, 0, 0);
    try std.testing.expectEqual(@as(usize, 535), r.slot(&pages, 0));
    try std.testing.expectEqual(@as(usize, 536), r.slot(&pages, 1));
    try std.testing.expectError(error.Exhausted, Large.map(&pages, page_size, 3, .{}));
}

test "extreme lengths and adjacent pin boundaries preserve metadata" {
    const maximum = std.math.maxInt(u64) - (page_size - 1);
    try std.testing.expectEqual(maximum / page_size, try length(maximum));
    try std.testing.expectError(error.Invalid, length(maximum + 1));
    var pages = [_]Page{.{}} ** capacity;
    for (0..3) |i| pages[i] = .{ .address = base + i * page_size, .flags = 7 | nx, .anonymous = true };
    pages[3] = .{ .address = end - page_size, .flags = nx, .anonymous = true };
    const before = pages;
    const last = try range(&pages, end - page_size, page_size, 0, 0);
    try std.testing.expectEqual(@as(usize, 3), last.slot(&pages, 0));
    try std.testing.expectError(error.Denied, range(&pages, end - page_size, page_size + 1, 0, 0));
    try std.testing.expectError(error.Invalid, range(&pages, base, maximum, 0, 0));
    // A legacy clear-TID word may straddle pages; both remain pinned.
    for (0..2) |i| try std.testing.expectError(error.Denied, range(&pages, base + i * page_size, page_size, 0, base + page_size - 2));
    _ = try range(&pages, base + 2 * page_size, page_size, 0, base + page_size - 2);
    // FS pins its own page and the previous page, but not the following page.
    for (0..2) |i| try std.testing.expectError(error.Denied, range(&pages, base + i * page_size, page_size, base + page_size, 0));
    _ = try range(&pages, base + 2 * page_size, page_size, base + page_size, 0);
    try std.testing.expectEqualDeep(before, pages);
}

test "plan and free cursor sizes stay constant across supported quotas" {
    try std.testing.expectEqual(@as(usize, 2 * @sizeOf(usize)), @sizeOf(Default.Plan));
    try std.testing.expectEqual(@sizeOf(Default.Plan), @sizeOf(Arena(2048).Plan));
    try std.testing.expectEqual(@sizeOf(Default.FreeSlots), @sizeOf(Arena(2048).FreeSlots));
    try std.testing.expect(@sizeOf(Arena(2048).FreeSlots) <= 32);
}

test "range order survives permuted backing and committed clearing" {
    var pages = [_]Page{.{}} ** capacity;
    pages[9] = .{ .address = base, .anonymous = true };
    pages[3] = .{ .address = base + page_size, .anonymous = true };
    pages[7] = .{ .address = base + 2 * page_size, .anonymous = true };
    const before = pages;
    const plan = try range(&pages, base, 3 * page_size, 0, 0);
    try std.testing.expectEqualDeep(before, pages);
    for ([_]usize{ 9, 3, 7 }, 0..) |expected, offset| {
        const slot = plan.slot(&pages, offset);
        try std.testing.expectEqual(expected, slot);
        pages[slot] = .{};
    }
    try std.testing.expectEqual(@as(usize, 0), used(&pages));
    try std.testing.expectError(error.Exhausted, range(&pages, base, 3 * page_size, 0, 0));
}

test "service view clamps arena and records to its actual small owner" {
    const Service = Arena(8192);
    var pages = [_]Page{.{}} ** 128;
    pages[0] = .{ .address = 0x200000 };
    const before = pages;
    try std.testing.expectError(error.Exhausted, Service.map(&pages, 128 * page_size, 3, .{}));
    try std.testing.expectEqualDeep(before, pages);
    const plan = try Service.map(&pages, 127 * page_size, 3, .{});
    try std.testing.expectEqual(@as(usize, 127), plan.count);
    var cursor = plan.freeSlots(&pages);
    var visited: usize = 0;
    while (cursor.next()) |slot| {
        try std.testing.expect(slot < pages.len);
        pages[slot] = .{ .address = base + visited * page_size, .anonymous = true };
        visited += 1;
    }
    try std.testing.expectEqual(@as(usize, 127), visited);
    try std.testing.expectEqual(@as(usize, 128), Service.used(&pages));
    try std.testing.expectError(error.Exhausted, Service.map(&pages, page_size, 3, .{}));
    try std.testing.expectError(error.Denied, Service.range(&pages, base + 128 * page_size, page_size, 0, 0));
}

test "service plans cover a full larger owner without stack-sized slot snapshots" {
    const Service = Arena(8192);
    const pages = try std.testing.allocator.create([8192]Page);
    defer std.testing.allocator.destroy(pages);
    @memset(pages, .{});
    pages[0] = .{ .address = 0x200000 };
    const plan = try Service.map(pages, 8191 * page_size, 3, .{});
    var cursor = plan.freeSlots(pages);
    for (0..plan.count) |offset| {
        const slot = cursor.next().?;
        pages[slot] = .{ .address = plan.address + offset * page_size, .flags = 7 | nx, .anonymous = true };
    }
    try std.testing.expect(cursor.next() == null);
    try std.testing.expectEqual(@as(usize, 8192), Service.used(pages));
    const last = try Service.range(pages, base + 8190 * page_size, page_size, 0, 0);
    try std.testing.expectEqual(@as(usize, 8191), last.slot(pages, 0));
    const tables_plan = try tables(&.{}, table_capacity, plan.address, plan.count, true);
    try std.testing.expectEqual(@as(usize, 16), tables_plan.count);
    try std.testing.expectEqual(@sizeOf(Default.Plan), @sizeOf(Service.Plan));
    try std.testing.expect(@sizeOf(Service.FreeSlots) <= 40);
    try std.testing.expectError(error.Exhausted, Service.map(pages, page_size, 3, .{}));
}

test "invalid borrowed metadata extent rejects before resource access" {
    const Service = Arena(8192);
    const pages = try std.testing.allocator.create([8193]Page);
    defer std.testing.allocator.destroy(pages);
    @memset(pages, .{});
    for ([_][]const Page{ pages[0..0], pages[0..8193] }) |view| {
        try std.testing.expectError(error.Invalid, Service.map(view, page_size, 3, .{}));
        try std.testing.expectError(error.Invalid, Service.range(view, base, page_size, 0, 0));
    }
}

fn expectSamePlan(expected: anytype, actual: anytype) !void {
    if (expected) |p| {
        const q = try actual;
        try std.testing.expectEqual(p.address, q.address);
        try std.testing.expectEqual(p.count, q.count);
    } else |err| try std.testing.expectError(err, actual);
}

test "sliced scans preserve legacy small-owner results on fragmented layouts" {
    const Service = Arena(8192);
    var records: [128]Page = undefined;
    for (0..32) |layout| {
        for (&records, 0..) |*p, i| {
            const index = (i * 37 + layout * 13) % 128;
            p.* = if ((index + layout) % 5 == 0) .{} else .{
                .address = if (index % 7 == 0) 0x200000 + index * page_size else base + index * page_size,
                .flags = 7 | nx,
                .anonymous = index % 11 != 0,
            };
        }
        const before = records;
        for ([_]u64{ 0, 1, 3, 4, 8 }) |prot| {
            for ([_]usize{ 0, 1, 2, 5, 127, 128, 129 }) |count| {
                try expectSamePlan(Default.map(&records, count * page_size, prot, .{}), Service.map(&records, count * page_size, prot, .{}));
                try expectSamePlan(Default.map(&records, count * page_size, prot, .{ .arena = 16, .fail_after = 1 }), Service.map(&records, count * page_size, prot, .{ .arena = 16, .fail_after = 1 }));
            }
        }
        for (0..128) |index| {
            for ([_]usize{ 1, 2, 7 }) |count| {
                const addr = base + index * page_size;
                try expectSamePlan(Default.range(&records, addr, count * page_size, 0, 0), Service.range(&records, addr, count * page_size, 0, 0));
                try expectSamePlan(Default.range(&records, addr, count * page_size, base + 10 * page_size, 0), Service.range(&records, addr, count * page_size, base + 10 * page_size, 0));
            }
        }
        try std.testing.expectEqualDeep(before, records);
    }
}

test "service range cursor covers permuted whole-owner records and permits clearing" {
    const Service = Arena(8192);
    const records = try std.testing.allocator.create([8192]Page);
    defer std.testing.allocator.destroy(records);
    for (records, 0..) |*p, index| p.* = .{ .address = base + ((index * 37) % 8192) * page_size, .flags = 7 | nx, .anonymous = true };
    const original = records[4097];
    records[4097].anonymous = false;
    try std.testing.expectError(error.Exhausted, Service.range(records, base, 8192 * page_size, 0, 0));
    records[4097] = .{};
    try std.testing.expectError(error.Exhausted, Service.range(records, base, 8192 * page_size, 0, 0));
    records[4097] = original;
    try std.testing.expectError(error.Denied, Service.range(records, base, 8192 * page_size, base + 4096, 0));
    try std.testing.expectError(error.Denied, Service.range(records, base, 8192 * page_size, 0, base + 100));
    const plan = try Service.range(records, base, 8192 * page_size, 0, 0);
    var slots = plan.rangeSlots(records);
    for (0..8192) |i| {
        try std.testing.expectEqual(i, slots.next().?);
        records[i] = .{};
    }
    try std.testing.expect(slots.next() == null);
    try std.testing.expectEqual(@as(usize, 0), Service.used(records));
    try std.testing.expectEqual(@as(usize, 1024), @sizeOf(std.StaticBitSet(8192)));
    try std.testing.expect(@sizeOf(Service.RangeSlots) <= 48);
    try std.testing.expectEqual(@as(usize, 16), @sizeOf(Service.Plan));
}

test "validated ranges retain context pin boundaries and pin-before-hole errors" {
    var pages = [_]Page{.{}} ** capacity;
    for (0..4) |i| pages[i] = .{ .address = base + i * page_size, .anonymous = true };
    const plan = try range(&pages, base + page_size, 2 * page_size, 0, 0);
    for ([_]u64{ 0, base, base + 4 * page_size }) |fs| try plan.checkPins(fs, 0);
    for ([_]u64{ base + page_size, base + 2 * page_size, base + 3 * page_size }) |fs|
        try std.testing.expectError(error.Denied, plan.checkPins(fs, 0));
    for ([_]usize{ 0, base + page_size - 4, base + 3 * page_size }) |tid| try plan.checkPins(0, tid);
    for ([_]usize{ base + page_size - 2, base + page_size, base + 3 * page_size - 2 }) |tid|
        try std.testing.expectError(error.Denied, plan.checkPins(0, tid));
    pages[2] = .{};
    const before = pages;
    try std.testing.expectError(error.Denied, range(&pages, plan.address, 2 * page_size, base + 2 * page_size, 0));
    try std.testing.expectError(error.Denied, range(&pages, plan.address, 2 * page_size, 0, base + 2 * page_size));
    try std.testing.expectError(error.Exhausted, range(&pages, plan.address, 2 * page_size, 0, 0));
    try std.testing.expectEqualDeep(before, pages);
}

test "640-record application view clamps defaults exhaustion ranges and pins" {
    const Service = Arena(8192);
    var pages = [_]Page{.{}} ** 640;
    // Image and existing stack consume records even outside the anonymous arena.
    for (pages[0..384], 0..) |*p, i| p.* = .{ .address = 0x200000 + i * page_size, .flags = 5 | nx };
    const before = pages;
    try std.testing.expectEqual(@as(usize, 384), Service.used(&pages));
    try std.testing.expectError(error.Exhausted, Service.map(&pages, 257 * page_size, 3, .{}));
    for ([_]Service.Limits{ .{ .backing = 384 }, .{ .records = 384 }, .{ .arena = 0 }, .{ .table_available = false }, .{ .fail_after = 255 } }) |limits| {
        try std.testing.expectError(error.Exhausted, Service.map(&pages, 256 * page_size, 3, limits));
        try std.testing.expectEqualDeep(before, pages);
    }
    const plan = try Service.map(&pages, 256 * page_size, 3, .{});
    var slots = plan.freeSlots(&pages);
    for (0..256) |i| pages[slots.next().?] = .{ .address = plan.address + i * page_size, .flags = 7 | nx, .anonymous = true };
    try std.testing.expectEqual(@as(usize, 640), Service.used(&pages));
    try std.testing.expectError(error.Exhausted, Service.map(&pages, page_size, 0, .{}));
    _ = try Service.range(&pages, base, 256 * page_size, 0, 0);
    try std.testing.expectError(error.Denied, Service.range(&pages, base + 640 * page_size, page_size, 0, 0));
    try std.testing.expectError(error.Denied, Service.range(&pages, base, page_size, base + page_size, 0));
    try std.testing.expectError(error.Denied, Service.range(&pages, base, page_size, 0, base + 16));
    try std.testing.expectError(error.Denied, Service.range(&pages, 0x200000, page_size, 0, 0));
    try std.testing.expectError(error.Denied, Service.map(&pages, page_size, 7, .{}));
}
