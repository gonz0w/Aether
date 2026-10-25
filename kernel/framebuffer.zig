const std = @import("std");
const limine = @import("limine.zig");

pub const Layout = struct {
    width: usize,
    height: usize,
    stride: usize,
    red: u5,
    green: u5,
    blue: u5,

    pub fn validate(fb: limine.Framebuffer) !Layout {
        const address = fb.address orelse return error.MissingFramebufferAddress;
        if (fb.memory_model != 1 or fb.bpp != 32) return error.UnsupportedPixelFormat;
        if (fb.width == 0 or fb.height == 0 or fb.width > 8192 or fb.height > 8192)
            return error.InvalidDimensions;
        if (@intFromPtr(address) % 4 != 0 or fb.pitch % 4 != 0 or fb.pitch < fb.width * 4)
            return error.InvalidPitchOrAlignment;
        const bytes = std.math.mul(u64, fb.pitch, fb.height) catch return error.SpanOverflow;
        if (bytes > 256 * 1024 * 1024) return error.FramebufferTooLarge;
        _ = std.math.add(usize, @intFromPtr(address), bytes) catch return error.SpanOverflow;
        if (fb.red_mask_size != 8 or fb.green_mask_size != 8 or fb.blue_mask_size != 8 or
            fb.red_mask_shift > 24 or fb.green_mask_shift > 24 or fb.blue_mask_shift > 24)
            return error.UnsupportedColorMasks;
        const r: u5 = @intCast(fb.red_mask_shift);
        const g: u5 = @intCast(fb.green_mask_shift);
        const b: u5 = @intCast(fb.blue_mask_shift);
        const rm = @as(u32, 255) << r;
        const gm = @as(u32, 255) << g;
        const bm = @as(u32, 255) << b;
        if (rm & gm != 0 or rm & bm != 0 or gm & bm != 0) return error.OverlappingColorMasks;
        return .{ .width = @intCast(fb.width), .height = @intCast(fb.height), .stride = @intCast(fb.pitch / 4), .red = r, .green = g, .blue = b };
    }

    pub fn pixel(self: Layout, r: u8, g: u8, b: u8) u32 {
        return (@as(u32, r) << self.red) | (@as(u32, g) << self.green) | (@as(u32, b) << self.blue);
    }
};

pub fn draw(address: [*]volatile u32, layout: Layout) void {
    for (0..layout.height) |y| {
        for (0..layout.width) |x| {
            const border = x < 8 or y < 8 or x + 8 >= layout.width or y + 8 >= layout.height;
            const color = if (border) layout.pixel(255, 255, 255) else if (y < layout.height / 3)
                layout.pixel(24, 32, 48)
            else if (y < layout.height * 2 / 3)
                switch (@min(x * 3 / layout.width, 2)) {
                    0 => layout.pixel(255, 0, 0),
                    1 => layout.pixel(0, 255, 0),
                    else => layout.pixel(0, 0, 255),
                }
            else if ((x / 32 + y / 32) % 2 == 0)
                layout.pixel(40, 180, 180)
            else
                layout.pixel(16, 70, 90);
            address[y * layout.stride + x] = color;
        }
    }
}

fn fixture() limine.Framebuffer {
    return .{ .address = @ptrFromInt(0x1000), .width = 64, .height = 64, .pitch = 272, .bpp = 32, .memory_model = 1, .red_mask_size = 8, .red_mask_shift = 16, .green_mask_size = 8, .green_mask_shift = 8, .blue_mask_size = 8, .blue_mask_shift = 0 };
}

test "stride respects row padding and drawing leaves padding untouched" {
    var data: [68 * 64]u32 = @splat(0xdeadbeef);
    var fb = fixture();
    fb.address = @ptrCast(&data);
    const layout = try Layout.validate(fb);
    draw(&data, layout);
    for (0..64) |y| for (64..68) |x| {
        try std.testing.expectEqual(@as(u32, 0xdeadbeef), data[y * 68 + x]);
    };
    try std.testing.expectEqual(@as(u32, 0xffffff), data[0]);
    try std.testing.expectEqual(@as(u32, 0xff0000), data[24 * 68 + 12]);
}
test "pixel conversion follows masks rather than assuming BGR" {
    var fb = fixture();
    fb.red_mask_shift = 0;
    fb.blue_mask_shift = 16;
    try std.testing.expectEqual(@as(u32, 0x030201), (try Layout.validate(fb)).pixel(1, 2, 3));
}
test "reject missing address, unsupported format, bad dimensions and pitch" {
    var fb = fixture();
    fb.address = null;
    try std.testing.expectError(error.MissingFramebufferAddress, Layout.validate(fb));
    fb = fixture();
    fb.bpp = 24;
    try std.testing.expectError(error.UnsupportedPixelFormat, Layout.validate(fb));
    fb = fixture();
    fb.width = 0;
    try std.testing.expectError(error.InvalidDimensions, Layout.validate(fb));
    fb = fixture();
    fb.pitch = 4;
    try std.testing.expectError(error.InvalidPitchOrAlignment, Layout.validate(fb));
}
test "reject overlapping masks and arithmetic overflow before drawing" {
    var fb = fixture();
    fb.red_mask_shift = 8;
    try std.testing.expectError(error.OverlappingColorMasks, Layout.validate(fb));
    fb = fixture();
    fb.pitch = std.math.maxInt(u64) - 3;
    try std.testing.expectError(error.SpanOverflow, Layout.validate(fb));
    fb = fixture();
    fb.address = @ptrFromInt(std.math.maxInt(usize) - 3);
    try std.testing.expectError(error.SpanOverflow, Layout.validate(fb));
}
