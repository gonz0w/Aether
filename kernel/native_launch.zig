// SPDX-License-Identifier: BSD-2-Clause
const std = @import("std");
const elf = @import("native_elf.zig");
pub const record_size = 272;
pub const Arguments = struct { argc: usize, envc: usize, strings: [8][32]u8 };
pub const Error = error{InvalidLaunch};
pub fn arguments(raw: *const [record_size]u8) Error!Arguments {
    const argc = std.mem.readInt(u64, raw[0..8], .little);
    const envc = std.mem.readInt(u64, raw[8..16], .little);
    if (argc == 0 or argc > 4 or envc > 4) return error.InvalidLaunch;
    var result = Arguments{ .argc = @intCast(argc), .envc = @intCast(envc), .strings = undefined };
    for (&result.strings, 0..) |*s, i| {
        @memcpy(s, raw[16 + i * 32 ..][0..32]);
        if ((i < argc or (i >= 4 and i - 4 < envc)) and std.mem.indexOfScalar(u8, s, 0) == null) return error.InvalidLaunch;
    }
    return result;
}
pub const Bundle = struct { images: [3][]const u8, supervisor: []const u8, entropy: []const u8 };
pub fn bundle(raw: []const u8) Error!Bundle {
    if (raw.len >= 8 and (std.mem.eql(u8, raw[0..8], "AENSI001") or std.mem.eql(u8, raw[0..8], "AENPG001") or std.mem.eql(u8, raw[0..8], "AENMX001") or std.mem.eql(u8, raw[0..8], "AENMX002") or std.mem.eql(u8, raw[0..8], "AENMX003"))) {
        return threeImageBundle(raw, 80);
    }
    if (raw.len < 56 or (!std.mem.eql(u8, raw[0..8], "AENEX001") and !std.mem.eql(u8, raw[0..8], "AENCH001") and !std.mem.eql(u8, raw[0..8], "AENFS001") and !std.mem.eql(u8, raw[0..8], "AENIN001") and !std.mem.eql(u8, raw[0..8], "AENIN002") and !std.mem.eql(u8, raw[0..8], "AENIN003") and !std.mem.eql(u8, raw[0..8], "AENCO001") and !std.mem.eql(u8, raw[0..8], "AENSC003"))) return error.InvalidLaunch;
    const a: usize = std.mem.readInt(u32, raw[8..12], .little);
    const b: usize = std.mem.readInt(u32, raw[12..16], .little);
    const c: usize = std.mem.readInt(u32, raw[16..20], .little);
    if (a == 0 or a > 1024 * 1024 or b == 0 or b > 1024 * 1024 or c == 0 or c > (if (std.mem.eql(u8, raw[0..8], "AENIN003")) @as(usize, 16384) else if (std.mem.eql(u8, raw[0..8], "AENIN002")) @as(usize, 8192) else 4096) or std.mem.readInt(u32, raw[20..24], .little) != 0 or raw.len != 56 + a + b + c) return error.InvalidLaunch;
    return .{ .images = .{ raw[56..][0..a], raw[56 + a ..][0..b], &.{} }, .supervisor = raw[56 + a + b ..], .entropy = raw[24..56] };
}
/// Candidate five-worker envelope only. The normal bundle/start path continues
/// to reject this magic until the separate native capacity profile is qualified.
pub fn pipelineBundle(raw: []const u8) Error!Bundle {
    if (raw.len < 8 or (!std.mem.eql(u8, raw[0..8], "AENMX004") and !std.mem.eql(u8, raw[0..8], "AENMX005") and !std.mem.eql(u8, raw[0..8], "AENMX006") and !std.mem.eql(u8, raw[0..8], "AENMX007") and !std.mem.eql(u8, raw[0..8], "AENMX008") and !std.mem.eql(u8, raw[0..8], "AENMX009"))) return error.InvalidLaunch;
    return threeImageBundle(raw, 112);
}

fn threeImageBundle(raw: []const u8, header: usize) Error!Bundle {
    const limit: usize = if (raw.len >= 8 and (std.mem.eql(u8, raw[0..8], "AENMX005") or std.mem.eql(u8, raw[0..8], "AENMX006") or std.mem.eql(u8, raw[0..8], "AENMX007") or std.mem.eql(u8, raw[0..8], "AENMX008") or std.mem.eql(u8, raw[0..8], "AENMX009"))) 24576 else if (raw.len >= 8 and !std.mem.eql(u8, raw[0..8], "AENMX001") and !std.mem.eql(u8, raw[0..8], "AENPG001")) 16384 else 8192;
    return threeImageBundleLimit(raw, header, limit);
}
/// Only the separately selected ABI31 filesystem owner accepts this nested wire.
pub fn ownerStackBundle(raw: []const u8) Error!Bundle {
    if (raw.len < 8 or !std.mem.eql(u8, raw[0..8], "AENMX010")) return error.InvalidLaunch;
    return threeImageBundleLimit(raw, 112, @import("arch/x86_64/native_fs_roles.zig").owner_stack_code_limit);
}
fn threeImageBundleLimit(raw: []const u8, header: usize, limit: usize) Error!Bundle {
    if (raw.len < header) return error.InvalidLaunch;
    const a: usize = std.mem.readInt(u32, raw[8..12], .little);
    const b: usize = std.mem.readInt(u32, raw[12..16], .little);
    const c: usize = std.mem.readInt(u32, raw[16..20], .little);
    const d: usize = std.mem.readInt(u32, raw[20..24], .little);
    if (a == 0 or a > 1024 * 1024 or b == 0 or b > 1024 * 1024 or c == 0 or c > 1024 * 1024 or d == 0 or d > limit or std.mem.readInt(u64, raw[24..32], .little) != 0 or raw.len != header + a + b + c + d) return error.InvalidLaunch;
    return .{ .images = .{ raw[header..][0..a], raw[header + a ..][0..b], raw[header + a + b ..][0..c] }, .supervisor = raw[header + a + b + c ..], .entropy = raw[32..header] };
}

// Actual loader backing includes the fixed sixteen-page main stack. The parser
// separately checks flags/overlap/layout; this checks a selected owner's budget.
pub fn backingPages(image: *const elf.Image) Error!usize {
    if (image.count > image.segments.len) return error.InvalidLaunch;
    var count: usize = 16;
    for (image.segments[0..image.count]) |segment| {
        const bytes = std.math.add(usize, segment.address % 4096, segment.memsz) catch return error.InvalidLaunch;
        const rounded = std.math.add(usize, bytes, 4095) catch return error.InvalidLaunch;
        count = std.math.add(usize, count, rounded / 4096) catch return error.InvalidLaunch;
    }
    return count;
}

// Preflight actual loader limits, beyond generic ELF syntax. No runtime reparse.
pub fn layout(image: *const elf.Image) Error!void {
    var tables: [32]usize = undefined;
    tables[0] = 0x08000000 / (2 * 1024 * 1024);
    var count: usize = 1;
    for (image.segments[0..image.count]) |s| {
        const end = s.address + s.memsz; // Generic parser already bounds arithmetic.
        if (end >= 0x10000000 or (s.address < 0x08010000 and end > 0x08000000)) return error.InvalidLaunch;
        var page = s.address & ~@as(usize, 4095);
        while (page < end) : (page += 4096) {
            const index = page / (2 * 1024 * 1024);
            if (std.mem.indexOfScalar(usize, tables[0..count], index) == null) {
                if (count == tables.len) return error.InvalidLaunch;
                tables[count] = index;
                count += 1;
            }
        }
    }
}
test "launch arguments validate counts and active terminators" {
    var raw = [_]u8{0} ** record_size;
    try std.testing.expectError(error.InvalidLaunch, arguments(&raw));
    raw[0] = 4;
    raw[8] = 4;
    _ = try arguments(&raw);
    @memset(raw[16..48], 'x');
    try std.testing.expectError(error.InvalidLaunch, arguments(&raw));
    raw[47] = 0;
    _ = try arguments(&raw);
    raw[8] = 5;
    try std.testing.expectError(error.InvalidLaunch, arguments(&raw));
}
test "launch bundle rejects truncation, excess, reserved and huge lengths" {
    var raw = [_]u8{0} ** 59;
    @memcpy(raw[0..8], "AENEX001");
    raw[8] = 1;
    raw[12] = 1;
    raw[16] = 1;
    for ([_][]const u8{ "AENEX001", "AENCH001", "AENFS001", "AENIN001", "AENCO001", "AENSC003" }) |magic| {
        @memcpy(raw[0..8], magic);
        _ = try bundle(&raw);
    }
    try std.testing.expectError(error.InvalidLaunch, bundle(raw[0..58]));
    raw[20] = 1;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[20] = 0;
    @memset(raw[8..12], 255);
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
}

test "loader preflight excludes stack, upper arena and excess leaf tables" {
    var image = elf.Image{ .entry = 0, .phdr = 0, .phnum = 0, .count = 1, .segments = undefined };
    image.segments[0] = .{ .flags = 6, .offset = 0, .address = 0x08000000, .filesz = 1, .memsz = 4096 };
    try std.testing.expectError(error.InvalidLaunch, layout(&image));
    image.segments[0].address = 0x10000000;
    try std.testing.expectError(error.InvalidLaunch, layout(&image));
    for (&image.segments, 0..) |*s, i| s.* = .{ .flags = 6, .offset = 0, .address = (i * 2 + 2) * 0x200000 - 4096, .filesz = 1, .memsz = 8192 };
    image.count = 15;
    try layout(&image);
    image.count = 16;
    try std.testing.expectError(error.InvalidLaunch, layout(&image));
}

test "program envelope validates third image, entropy, reserved words and exact size" {
    var raw = [_]u8{0} ** 84;
    @memcpy(raw[0..8], "AENPG001");
    for ([_]usize{ 8, 12, 16, 20 }) |i| raw[i] = 1;
    const parsed = try bundle(&raw);
    try std.testing.expectEqual(48, parsed.entropy.len);
    try std.testing.expectEqual(1, parsed.images[2].len);
    try std.testing.expectEqual(1, parsed.supervisor.len);
    try std.testing.expectError(error.InvalidLaunch, bundle(raw[0..83]));
    raw[28] = 1;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[28] = 0;
    raw[24] = 1;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[24] = 0;
    raw[16] = 0;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[16] = 1;
    std.mem.writeInt(u32, raw[20..24], 8193, .little);
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    std.mem.writeInt(u32, raw[20..24], 1, .little);
    @memcpy(raw[0..8], "AENCO001");
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
}

test "connections envelope selects the bounded three-image header" {
    var raw = [_]u8{0} ** 84;
    @memcpy(raw[0..8], "AENMX001");
    for ([_]usize{ 8, 12, 16, 20 }) |i| raw[i] = 1;
    const parsed = try bundle(&raw);
    try std.testing.expectEqual(3, parsed.images.len);
    try std.testing.expectEqual(48, parsed.entropy.len);
    try std.testing.expectError(error.InvalidLaunch, bundle(raw[0..79]));
    raw[24] = 1;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[24] = 0;
    raw[28] = 1;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[28] = 0;
    raw[16] = 0;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[16] = 1;
    std.mem.writeInt(u32, raw[20..24], 8193, .little);
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
}

test "init v3 capacity preserves v1/v2 and rejects malformed bounds" {
    var raw = [_]u8{0} ** (58 + 16385);
    raw[8] = 1;
    raw[12] = 1;
    for ([_][]const u8{ "AENIN001", "AENIN002", "AENIN003" }) |magic| {
        @memcpy(raw[0..8], magic);
        const limit: usize = if (std.mem.eql(u8, magic, "AENIN003")) 16384 else if (std.mem.eql(u8, magic, "AENIN002")) 8192 else 4096;
        for ([_]usize{ 1, 4095, 4096, 8191, 8192, 8193, 12287, 12288, 16383, 16384, 16385 }) |n| {
            std.mem.writeInt(u32, raw[16..20], @intCast(n), .little);
            if (n <= limit) {
                const parsed = try bundle(raw[0 .. 58 + n]);
                try std.testing.expectEqual(n, parsed.supervisor.len);
            } else try std.testing.expectError(error.InvalidLaunch, bundle(raw[0 .. 58 + n]));
        }
        for ([_]u32{ 0, std.math.maxInt(u32) }) |n| {
            std.mem.writeInt(u32, raw[16..20], n, .little);
            try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
        }
        std.mem.writeInt(u32, raw[16..20], @intCast(limit), .little);
        try std.testing.expectError(error.InvalidLaunch, bundle(raw[0 .. 57 + limit]));
        try std.testing.expectError(error.InvalidLaunch, bundle(raw[0 .. 59 + limit]));
        raw[20] = 1;
        try std.testing.expectError(error.InvalidLaunch, bundle(raw[0 .. 58 + limit]));
        raw[20] = 0;
    }
}

test "large connections preserves version bounds and canonical framing" {
    var raw = [_]u8{0} ** (80 + 3 + 16385);
    for ([_][]const u8{ "AENMX001", "AENMX002", "AENMX003" }) |magic| {
        @memcpy(raw[0..8], magic);
        for ([_]usize{ 8, 12, 16 }) |i| raw[i] = 1;
        const limit: usize = if (std.mem.eql(u8, magic, "AENMX001")) 8192 else 16384;
        for ([_]usize{ 0, 1, 4095, 4096, 8192, 8193, 12288, 16383, 16384, 16385 }) |n| {
            std.mem.writeInt(u32, raw[20..24], @intCast(n), .little);
            const input = raw[0 .. 83 + n];
            if (n == 0 or n > limit) {
                try std.testing.expectError(error.InvalidLaunch, bundle(input));
                continue;
            }
            const result = try bundle(input);
            try std.testing.expectEqual(n, result.supervisor.len);
            try std.testing.expectEqual(48, result.entropy.len);
            try std.testing.expectError(error.InvalidLaunch, bundle(input[0 .. input.len - 1]));
            raw[28] = 1;
            try std.testing.expectError(error.InvalidLaunch, bundle(input));
            raw[28] = 0;
        }
    }
}

test "candidate five-worker bundle keeps entropy and payloads separate" {
    var raw = [_]u8{0} ** 122;
    @memcpy(raw[0..8], "AENMX004");
    for ([_]usize{ 8, 12, 16, 20 }, 1..) |offset, size| {
        std.mem.writeInt(u32, raw[offset..][0..4], @intCast(size), .little);
    }
    for (0..5) |slot| @memset(raw[32 + slot * 16 ..][0..16], @intCast(slot + 1));
    @memcpy(raw[112..], "abbcccdddd");
    const parsed = try pipelineBundle(&raw);
    try std.testing.expectEqual(80, parsed.entropy.len);
    for (0..5) |slot| {
        for (parsed.entropy[slot * 16 ..][0..16]) |byte| try std.testing.expectEqual(slot + 1, byte);
    }
    try std.testing.expectEqualStrings("a", parsed.images[0]);
    try std.testing.expectEqualStrings("bb", parsed.images[1]);
    try std.testing.expectEqualStrings("ccc", parsed.images[2]);
    try std.testing.expectEqualStrings("dddd", parsed.supervisor);
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
}

test "candidate five-worker header rejects malformed framing and old versions" {
    var raw = [_]u8{0} ** 117;
    @memcpy(raw[0..8], "AENMX004");
    for ([_]usize{ 8, 12, 16, 20 }) |offset| raw[offset] = 1;
    for (0..116) |length| try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw[0..length]));
    _ = try pipelineBundle(raw[0..116]);
    try std.testing.expectError(error.InvalidLaunch, pipelineBundle(&raw));
    for (24..32) |offset| {
        raw[offset] = 1;
        try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw[0..116]));
        raw[offset] = 0;
    }
    for ([_]usize{ 8, 12, 16, 20 }) |offset| {
        for ([_]u32{ 0, 1024 * 1024 + 1, std.math.maxInt(u32) }) |length| {
            std.mem.writeInt(u32, raw[offset..][0..4], length, .little);
            try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw[0..116]));
        }
        std.mem.writeInt(u32, raw[offset..][0..4], 1, .little);
    }
    for ([_][]const u8{ "AENMX001", "AENMX002", "AENMX003", "AENPG001", "AENMX010" }) |magic| {
        @memcpy(raw[0..8], magic);
        try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw[0..116]));
    }
}

test "candidate five-worker section limits preserve legacy rejection" {
    const image_limit = 1024 * 1024;
    const supervisor_limit = 16384;
    const raw = try std.testing.allocator.alloc(u8, 112 + 3 * image_limit + supervisor_limit + 1);
    defer std.testing.allocator.free(raw);
    @memset(raw, 0);
    @memcpy(raw[0..8], "AENMX004");
    for ([_]usize{ 8, 12, 16 }) |offset| std.mem.writeInt(u32, raw[offset..][0..4], image_limit, .little);
    std.mem.writeInt(u32, raw[20..24], supervisor_limit, .little);
    const valid = raw[0 .. raw.len - 1];
    const parsed = try pipelineBundle(valid);
    for (parsed.images) |image| try std.testing.expectEqual(image_limit, image.len);
    try std.testing.expectEqual(supervisor_limit, parsed.supervisor.len);
    try std.testing.expectError(error.InvalidLaunch, bundle(valid));
    std.mem.writeInt(u32, raw[20..24], supervisor_limit + 1, .little);
    try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw));
    std.mem.writeInt(u32, raw[20..24], supervisor_limit, .little);
    for ([_]usize{ 8, 12, 16 }) |offset| {
        std.mem.writeInt(u32, raw[offset..][0..4], image_limit + 1, .little);
        try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw));
        std.mem.writeInt(u32, raw[offset..][0..4], image_limit, .little);
    }
}

test "wide private supervisor limit preserves version and framing boundaries" {
    const raw = try std.testing.allocator.alloc(u8, 112 + 3 + 24577);
    defer std.testing.allocator.free(raw);
    for ([_][]const u8{ "AENMX004", "AENMX005", "AENMX006", "AENMX007", "AENMX008", "AENMX009" }) |magic| {
        const limit: usize = if (!std.mem.eql(u8, magic, "AENMX004")) 24576 else 16384;
        for ([_]usize{ 0, 1, 4096, 16384, 16385, 20480, 20481, 24575, 24576, 24577 }) |length| {
            @memset(raw, 0);
            @memcpy(raw[0..8], magic);
            for ([_]usize{ 8, 12, 16 }) |offset| std.mem.writeInt(u32, raw[offset..][0..4], 1, .little);
            std.mem.writeInt(u32, raw[20..24], @intCast(length), .little);
            const input = raw[0 .. 115 + length];
            try std.testing.expectError(error.InvalidLaunch, bundle(input));
            if (length == 0 or length > limit) {
                try std.testing.expectError(error.InvalidLaunch, pipelineBundle(input));
                continue;
            }
            const parsed = try pipelineBundle(input);
            try std.testing.expectEqual(length, parsed.supervisor.len);
            try std.testing.expectEqual(80, parsed.entropy.len);
            try std.testing.expectError(error.InvalidLaunch, pipelineBundle(input[0 .. input.len - 1]));
            try std.testing.expectError(error.InvalidLaunch, pipelineBundle(raw[0 .. input.len + 1]));
            for (24..32) |offset| {
                raw[offset] = 1;
                try std.testing.expectError(error.InvalidLaunch, pipelineBundle(input));
                raw[offset] = 0;
            }
        }
    }
}

test "sustained three-image envelope retains bounds and rejects five-worker routing" {
    var raw = [_]u8{0} ** 84;
    @memcpy(raw[0..8], "AENSI001");
    for (0..4) |i| std.mem.writeInt(u32, raw[8 + i * 4 ..][0..4], 1, .little);
    const decoded = try bundle(&raw);
    try std.testing.expectEqual(@as(usize, 1), decoded.supervisor.len);
    try std.testing.expectError(error.InvalidLaunch, pipelineBundle(&raw));
    raw[24] = 1;
    try std.testing.expectError(error.InvalidLaunch, bundle(&raw));
    raw[24] = 0;
    try std.testing.expectError(error.InvalidLaunch, bundle(raw[0..83]));
}

test "image backing preflight includes stack and separates large from small owners" {
    var image = elf.Image{ .entry = 0, .phdr = 0, .phnum = 0, .count = 1, .segments = undefined };
    image.segments[0] = .{ .address = 0x200000, .memsz = 2 * 1024 * 1024, .filesz = 1, .offset = 0, .flags = 5 };
    try std.testing.expectEqual(@as(usize, 528), try backingPages(&image));
    try std.testing.expect((try backingPages(&image)) > 128);
    try std.testing.expect((try backingPages(&image)) < 8192);
    image.segments[0].memsz = std.math.maxInt(usize);
    try std.testing.expectError(error.InvalidLaunch, backingPages(&image));
    image.count = image.segments.len + 1;
    try std.testing.expectError(error.InvalidLaunch, backingPages(&image));
}
