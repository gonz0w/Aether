const std = @import("std");
pub const base = 0x02000000;
pub const root: u64 = 3 << 32;
pub const Grant = struct {
    physical: u64,
    bytes: u64,
    pages: usize,
    map_right: bool = true,
    pub fn init(physical: u64, bytes: u64) !Grant {
        if (physical % 4096 != 0 or bytes == 0 or bytes > 2 * 1024 * 1024) return error.InvalidSpan;
        const rounded = (bytes + 4095) & ~@as(u64, 4095);
        _ = std.math.add(u64, physical, rounded) catch return error.InvalidSpan;
        return .{ .physical = physical, .bytes = bytes, .pages = @intCast(rounded / 4096) };
    }
    pub fn require(self: Grant, handle: u64, map: bool) !void {
        if (handle != root and handle != root | 1) return error.Invalid;
        if (map and (handle != root or !self.map_right)) return error.Denied;
    }
};
test "framebuffer grants bound pages and attenuate map authority" {
    var grant = try Grant.init(0x80000000, 1920000);
    try std.testing.expectEqual(@as(usize, 469), grant.pages);
    try grant.require(root, true);
    try grant.require(root | 1, false);
    try std.testing.expectError(error.Denied, grant.require(root | 1, true));
    try std.testing.expectError(error.Invalid, grant.require(1 << 32, true));
    grant.map_right = false;
    try std.testing.expectError(error.Denied, grant.require(root, true));
    try std.testing.expectError(error.InvalidSpan, Grant.init(1, 4096));
    try std.testing.expectError(error.InvalidSpan, Grant.init(0, 0));
    try std.testing.expectError(error.InvalidSpan, Grant.init(0, 2 * 1024 * 1024 + 1));
    try std.testing.expectError(error.InvalidSpan, Grant.init(0xfffffffffffff000, 8192));
}
