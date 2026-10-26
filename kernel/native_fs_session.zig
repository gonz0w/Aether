// SPDX-License-Identifier: BSD-2-Clause
// Fixed private composition, not a general role table or an authority issuer.
const std = @import("std");
const elf = @import("native_elf.zig");
const launch = @import("native_launch.zig");
const roles = @import("arch/x86_64/native_fs_roles.zig");
pub const magic = "AENFS002";
pub const init_magic = "AENFS003";
pub const owner_data_magic = "AENFS004";
pub const owner_stack_magic = "AENFS005";
pub const application_magic = "AENFS006";
pub const Error = roles.Error;
pub const Bundle = struct {
    engine: []const u8,
    engine_entropy: []const u8,
    session: launch.Bundle,
};
pub fn parse(raw: []const u8) Error!Bundle {
    return parseProfile(raw, false);
}
// Kernel selection only. The input cannot choose its own code allowance.
pub fn parseProfile(raw: []const u8, comptime init_owner: bool) Error!Bundle {
    return parseSelected(raw, if (init_owner) .init else .conformance);
}
pub fn parseOwnerData(raw: []const u8) Error!Bundle {
    return parseSelected(raw, .owner_data);
}
pub fn parseOwnerStack(raw: []const u8) Error!Bundle {
    return parseSelected(raw, .owner_stack);
}
pub fn parseApplication(raw: []const u8) Error!Bundle {
    return parseSelected(raw, .application);
}
const Profile = enum { conformance, init, owner_data, owner_stack, application };
fn parseSelected(raw: []const u8, comptime profile: Profile) Error!Bundle {
    const init_owner = profile != .conformance;
    const limit: usize = if (profile == .owner_stack or profile == .application) roles.owner_stack_code_limit else if (init_owner) 16384 else roles.controller_limit;
    const selected_magic = switch (profile) {
        .conformance => magic,
        .init => init_magic,
        .owner_data => owner_data_magic,
        .owner_stack => owner_stack_magic,
        .application => application_magic,
    };
    if (raw.len < 48 or !std.mem.eql(u8, raw[0..8], selected_magic)) return error.InvalidComposition;
    const engine: usize = std.mem.readInt(u32, raw[8..12], .little);
    const session: usize = std.mem.readInt(u32, raw[12..16], .little);
    const image_limit: usize = if (profile == .application) elf.application_limits.file_bytes else 1024 * 1024;
    if (engine == 0 or engine > elf.large_limits.file_bytes or
        session < 112 or session > 112 + 3 * image_limit + limit or
        raw.len != 48 + engine + session) return error.InvalidComposition;
    const bytes = raw[48..][0..engine];
    const image = elf.parseWithLimits(bytes, elf.large_limits) catch return error.InvalidComposition;
    launch.layout(&image) catch return error.InvalidComposition;
    const nested = raw[48 + engine ..];
    if (!std.mem.eql(u8, nested[0..8], if (profile == .application) "AENMX011" else if (profile == .owner_stack) "AENMX010" else "AENMX009")) return error.InvalidComposition;
    const bundle = (if (profile == .application) launch.applicationBundle(nested) else if (profile == .owner_stack) launch.ownerStackBundle(nested) else launch.pipelineBundle(nested)) catch return error.InvalidComposition;
    if (bundle.supervisor.len > limit) return error.InvalidComposition;
    for (bundle.images) |process_bytes| {
        const process_image = (if (profile == .application) elf.parseApplication(process_bytes) else elf.parse(process_bytes)) catch return error.InvalidComposition;
        launch.layout(&process_image) catch return error.InvalidComposition;
    }
    return .{ .engine = bytes, .engine_entropy = raw[16..48], .session = bundle };
}

test "selected outer and nested application admission parses all three image roles" {
    const Fixture = struct {
        fn image(address: u64, memsz: u64) [4096]u8 {
            var bytes = [_]u8{0} ** 4096;
            @memcpy(bytes[0..8], "\x7fELF\x02\x01\x01\x00");
            std.mem.writeInt(u16, bytes[16..18], 2, .little);
            std.mem.writeInt(u16, bytes[18..20], 62, .little);
            std.mem.writeInt(u32, bytes[20..24], 1, .little);
            std.mem.writeInt(u64, bytes[24..32], address + 512, .little);
            std.mem.writeInt(u64, bytes[32..40], 64, .little);
            std.mem.writeInt(u16, bytes[52..54], 64, .little);
            std.mem.writeInt(u16, bytes[54..56], 56, .little);
            std.mem.writeInt(u16, bytes[56..58], 4, .little);
            const headers = [_][8]u64{
                .{ 6, 4, 64, address + 64, address + 64, 224, 224, 8 },
                .{ 1, 5, 0, address, address, 4096, memsz, 4096 },
                .{ 7, 4, 768, address + 768, address + 768, 4, 4, 4 },
                .{ 0x6474e551, 6, 0, 0, 0, 0, 0, 16 },
            };
            for (headers, 0..) |header, i| {
                const offset = 64 + i * 56;
                std.mem.writeInt(u32, bytes[offset..][0..4], @intCast(header[0]), .little);
                std.mem.writeInt(u32, bytes[offset + 4 ..][0..4], @intCast(header[1]), .little);
                for (header[2..], 0..) |value, j| std.mem.writeInt(u64, bytes[offset + 8 + j * 8 ..][0..8], value, .little);
            }
            return bytes;
        }
    };
    var raw = [_]u8{0} ** (48 + 4096 + 112 + 3 * 4096 + 1);
    @memcpy(raw[0..8], application_magic);
    std.mem.writeInt(u32, raw[8..12], 4096, .little);
    std.mem.writeInt(u32, raw[12..16], 112 + 3 * 4096 + 1, .little);
    const small = Fixture.image(0x200000, 4096);
    @memcpy(raw[48..][0..4096], &small);
    const nested = raw[48 + 4096 ..];
    @memcpy(nested[0..8], "AENMX011");
    for (0..3) |i| std.mem.writeInt(u32, nested[8 + i * 4 ..][0..4], 4096, .little);
    nested[20] = 1;
    for (0..3) |i| @memcpy(nested[112 + i * 4096 ..][0..4096], &small);
    _ = try parseApplication(&raw);
    try std.testing.expectError(error.InvalidComposition, parseOwnerStack(&raw));
    for (0..3) |i| {
        const process_bytes = nested[112 + i * 4096 ..][0..4096];
        @memcpy(process_bytes, &Fixture.image(0x200000, 368 * 4096));
        _ = try parseApplication(&raw); // 368 image pages plus sixteen stack pages.
        @memcpy(raw[0..8], owner_stack_magic);
        @memcpy(nested[0..8], "AENMX010");
        try std.testing.expectError(error.InvalidComposition, parseOwnerStack(&raw));
        @memcpy(raw[0..8], application_magic);
        @memcpy(nested[0..8], "AENMX011");
        @memcpy(process_bytes, &Fixture.image(0x200000, 369 * 4096));
        try std.testing.expectError(error.InvalidComposition, parseApplication(&raw));
        @memcpy(process_bytes, &Fixture.image(0x400000, 4096));
        try std.testing.expectError(error.InvalidComposition, parseApplication(&raw));
        @memcpy(process_bytes, &small);
        process_bytes[124] = 7; // W+X on the actual process LOAD.
        try std.testing.expectError(error.InvalidComposition, parseApplication(&raw));
        @memcpy(process_bytes, &small);
    }
    @memcpy(nested[0..8], "AENMX010");
    try std.testing.expectError(error.InvalidComposition, parseApplication(&raw));
    @memcpy(raw[0..8], owner_stack_magic);
    _ = try parseOwnerStack(&raw); // Original selector still accepts its small closure.
}
