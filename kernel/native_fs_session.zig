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
const Profile = enum { conformance, init, owner_data, owner_stack };
fn parseSelected(raw: []const u8, comptime profile: Profile) Error!Bundle {
    const init_owner = profile != .conformance;
    const limit: usize = if (profile == .owner_stack) roles.owner_stack_code_limit else if (init_owner) 16384 else roles.controller_limit;
    const selected_magic = switch (profile) {
        .conformance => magic,
        .init => init_magic,
        .owner_data => owner_data_magic,
        .owner_stack => owner_stack_magic,
    };
    if (raw.len < 48 or !std.mem.eql(u8, raw[0..8], selected_magic)) return error.InvalidComposition;
    const engine: usize = std.mem.readInt(u32, raw[8..12], .little);
    const session: usize = std.mem.readInt(u32, raw[12..16], .little);
    if (engine == 0 or engine > elf.large_limits.file_bytes or
        session < 112 or session > 112 + 3 * 1024 * 1024 + limit or
        raw.len != 48 + engine + session) return error.InvalidComposition;
    const bytes = raw[48..][0..engine];
    const image = elf.parseWithLimits(bytes, elf.large_limits) catch return error.InvalidComposition;
    launch.layout(&image) catch return error.InvalidComposition;
    const nested = raw[48 + engine ..];
    if (!std.mem.eql(u8, nested[0..8], if (profile == .owner_stack) "AENMX010" else "AENMX009")) return error.InvalidComposition;
    const bundle = (if (profile == .owner_stack) launch.ownerStackBundle(nested) else launch.pipelineBundle(nested)) catch return error.InvalidComposition;
    if (bundle.supervisor.len > limit) return error.InvalidComposition;
    for (bundle.images) |process_bytes| {
        const process_image = elf.parse(process_bytes) catch return error.InvalidComposition;
        launch.layout(&process_image) catch return error.InvalidComposition;
    }
    return .{ .engine = bytes, .engine_entropy = raw[16..48], .session = bundle };
}
