// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
const elf = @import("native_elf.zig");
const image = @embedFile("shell.elf").*;
fn read32(b: []const u8, off: usize) u32 {
    return std.mem.readInt(u32, b[off..][0..4], .little);
}
fn read64(b: []const u8, off: usize) u64 {
    return std.mem.readInt(u64, b[off..][0..8], .little);
}
fn header(kind: u32) usize {
    const off: usize = @intCast(read64(&image, 32));
    const count = std.mem.readInt(u16, image[56..58], .little);
    for (0..count) |i| {
        const pos = off + i * 56;
        if (read32(&image, pos) == kind) return pos;
    }
    unreachable;
}
test "actual full shell with initialized TLS accepted under unchanged defaults" {
    const parsed = try elf.parse(&image);
    try std.testing.expect(parsed.count > 0);
    const h = header(7);
    const offset: usize = @intCast(read64(&image, h + 8));
    try std.testing.expectEqual(@as(u32, 4), read32(&image, h + 4));
    try std.testing.expectEqual(@as(u64, 4), read64(&image, h + 32));
    try std.testing.expectEqual(@as(u64, 4), read64(&image, h + 40));
    try std.testing.expectEqual(@as(u32, 0x73657373), read32(&image, offset));
}
test "original sealed stage without TLS still rejected" {
    try std.testing.expectError(error.InvalidImage, elf.parse(@embedFile("old-shell.elf")));
}
test "actual shell rejects malformed TLS and writable executable load" {
    const tls = header(7);
    for ([_]usize{ 4, 8, 16, 40, 48 }) |field| {
        var changed = image;
        if (field == 4) {
            std.mem.writeInt(u32, changed[tls + field ..][0..4], 6, .little);
        } else {
            std.mem.writeInt(u64, changed[tls + field ..][0..8], 0xffffffffffffffff, .little);
        }
        try std.testing.expectError(error.InvalidImage, elf.parse(&changed));
    }
    var changed = image;
    std.mem.writeInt(u32, changed[header(1) + 4 ..][0..4], 7, .little);
    try std.testing.expectError(error.InvalidImage, elf.parse(&changed));
}
