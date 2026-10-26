// SPDX-License-Identifier: BSD-2-Clause
// Immutable local profile geometry; numeric labels alone never authorize.
const std = @import("std");
pub const domain_count = 7;
pub const engine_slot = 0;
pub const owner_slot = 6;
pub const process_count = 5;
pub const backing_pages = 8960;
pub const channel_count = 12;
pub const process_channels = 10;
pub const controller_limit = 8192;
// Selected only by the separate ABI30 boot owner; no dynamic allocation grant.
pub const owner_data_base = 0x900000;
pub const owner_data_bytes = 8192;
// Complete ABI31 owner measured at39,376 bytes; twelve RX pages give about25% headroom.
// Old profile limits remain in their exact selectors.
pub const owner_stack_code_limit = 49152;
pub const Error = error{InvalidComposition};

pub fn process(slot: usize) bool {
    return slot > engine_slot and slot < owner_slot;
}
pub fn threaded(slot: usize) bool {
    return slot == engine_slot;
}
pub fn pages(slot: usize) Error!usize {
    if (slot >= domain_count) return error.InvalidComposition;
    return if (slot == engine_slot) 8192 else 128;
}
pub fn firstPage(slot: usize) Error!usize {
    _ = try pages(slot);
    return if (slot == engine_slot) 0 else 8192 + (slot - 1) * 128;
}
// One selected composition, not a global ordinary-process quota change.
pub const application_pages = 640;
pub const application_backing_pages = 8192 + process_count * application_pages + 128;
pub fn applicationPages(slot: usize) Error!usize {
    _ = try pages(slot);
    return if (process(slot)) application_pages else try pages(slot);
}
pub fn applicationFirstPage(slot: usize) Error!usize {
    _ = try applicationPages(slot);
    return if (slot == engine_slot) 0 else if (slot == owner_slot) 8192 + process_count * application_pages else 8192 + (slot - 1) * application_pages;
}
pub const ChannelRange = struct { first: usize, end: usize };
// A format/role restriction only: the enforcing operation must also check the
// current owner, live generation and actual endpoint holder/direction.
pub fn channelRange(factory: u64) ?ChannelRange {
    return switch (factory) {
        0xd001 => .{ .first = 0, .end = process_channels },
        0xd002 => .{ .first = process_channels, .end = channel_count },
        else => null,
    };
}
test "fixed role and disjoint backing geometry" {
    var stop: usize = 0;
    for (0..domain_count) |slot| {
        try std.testing.expectEqual(stop, try firstPage(slot));
        try std.testing.expectEqual(slot > 0 and slot < 6, process(slot));
        try std.testing.expectEqual(slot == 0, threaded(slot));
        stop += try pages(slot);
    }
    try std.testing.expectEqual(@as(usize, backing_pages), stop);
    try std.testing.expectError(error.InvalidComposition, pages(domain_count));
    try std.testing.expectError(error.InvalidComposition, firstPage(std.math.maxInt(usize)));
    try std.testing.expect(!process(std.math.maxInt(usize)) and !threaded(domain_count));
}
test "channel factories preserve exact disjoint ranges" {
    const p = channelRange(0xd001).?;
    const s = channelRange(0xd002).?;
    try std.testing.expectEqual(@as(usize, 0), p.first);
    try std.testing.expectEqual(p.end, s.first);
    try std.testing.expectEqual(@as(usize, channel_count), s.end);
    try std.testing.expect(channelRange(0) == null and channelRange(0xd003) == null);
}

test "application trial assigns exactly 45 MiB without changing roles or old geometry" {
    var next: usize = 0;
    for (0..domain_count) |slot| {
        try std.testing.expectEqual(next, try applicationFirstPage(slot));
        const count = try applicationPages(slot);
        try std.testing.expectEqual(@as(usize, if (slot == 0) 8192 else if (slot == 6) 128 else 640), count);
        try std.testing.expectEqual(@as(usize, if (slot == 0) 8192 else 128), try pages(slot));
        next += count;
    }
    try std.testing.expectEqual(@as(usize, 11520), next);
    try std.testing.expectEqual(@as(usize, application_backing_pages), next);
    try std.testing.expectEqual(@as(usize, 45 * 1024 * 1024), next * 4096);
    try std.testing.expectError(error.InvalidComposition, applicationPages(domain_count));
    try std.testing.expectError(error.InvalidComposition, applicationFirstPage(std.math.maxInt(usize)));
    try std.testing.expect(!process(engine_slot) and !process(owner_slot) and !threaded(1));
}
