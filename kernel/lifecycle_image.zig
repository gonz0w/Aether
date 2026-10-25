const std = @import("std");
pub fn parse(bytes: []const u8) ![]const u8 {
    if (bytes.len < 32 or !std.mem.eql(u8, bytes[0..8], "AELIFE01")) return error.InvalidImage;
    if (std.mem.readInt(u32, bytes[8..12], .little) != 1 or
        std.mem.readInt(u32, bytes[12..16], .little) != 1 or
        std.mem.readInt(u64, bytes[16..24], .little) != 0x400000 or
        std.mem.readInt(u32, bytes[28..32], .little) != 0) return error.InvalidImage;
    const length = std.mem.readInt(u32, bytes[24..28], .little);
    if (length == 0 or length > 4096 or bytes.len != 32 + @as(usize, length)) return error.InvalidImage;
    return bytes[32..];
}
test "supervisor envelope rejects unsupported ABI and ambiguous image boundaries" {
    var bytes: [33]u8 = @splat(0);
    @memcpy(bytes[0..8], "AELIFE01");
    std.mem.writeInt(u32, bytes[8..12], 1, .little);
    std.mem.writeInt(u32, bytes[12..16], 1, .little);
    std.mem.writeInt(u64, bytes[16..24], 0x400000, .little);
    std.mem.writeInt(u32, bytes[24..28], 1, .little);
    bytes[32] = 0xcc;
    try std.testing.expectEqualSlices(u8, &.{0xcc}, try parse(&bytes));
    for ([_]usize{ 0, 8, 12, 16, 28 }) |offset| {
        bytes[offset] ^= 2;
        try std.testing.expectError(error.InvalidImage, parse(&bytes));
        bytes[offset] ^= 2;
    }
    try std.testing.expectError(error.InvalidImage, parse(bytes[0..32]));
    bytes[24] = 0;
    try std.testing.expectError(error.InvalidImage, parse(&bytes));
}
