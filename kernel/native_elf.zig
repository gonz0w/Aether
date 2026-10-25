const std = @import("std");
pub const Error = error{InvalidImage};
pub const Segment = struct { flags: u32, offset: usize, address: usize, filesz: usize, memsz: usize };
pub const Image = struct { entry: usize, phdr: usize, phnum: usize, count: usize, segments: [16]Segment };
fn readu16(b: []const u8, o: usize) u16 {
    return std.mem.readInt(u16, b[o..][0..2], .little);
}
fn readu32(b: []const u8, o: usize) u32 {
    return std.mem.readInt(u32, b[o..][0..4], .little);
}
fn readu64(b: []const u8, o: usize) u64 {
    return std.mem.readInt(u64, b[o..][0..8], .little);
}
fn valid(ok: bool) Error!void {
    if (!ok) return error.InvalidImage;
}
fn inside(offset: usize, length: usize, total: usize) bool {
    return offset <= total and length <= total - offset;
}
pub const Limits = struct { file_bytes: usize = 1024 * 1024, pages: usize = 128 };
pub const large_limits = Limits{ .file_bytes = 8 * 1024 * 1024, .pages = 2048 };
pub fn parse(b: []const u8) Error!Image {
    return parseWithLimits(b, .{});
}
pub fn parseWithLimits(b: []const u8, limits: Limits) Error!Image {
    try valid(limits.file_bytes <= large_limits.file_bytes and limits.pages >= 16 and limits.pages <= large_limits.pages);
    try valid(b.len >= 64 and b.len <= limits.file_bytes);
    try valid(std.mem.eql(u8, b[0..8], "\x7fELF\x02\x01\x01\x00"));
    try valid(readu16(b, 16) == 2 and readu16(b, 18) == 62 and readu32(b, 20) == 1 and readu16(b, 52) == 64 and readu16(b, 54) == 56);
    const offset: usize = @intCast(readu64(b, 32));
    const count: usize = readu16(b, 56);
    try valid(count > 0 and count <= 16 and inside(offset, count * 56, b.len));
    var result = Image{ .entry = @intCast(readu64(b, 24)), .phdr = 0, .phnum = count, .count = 0, .segments = undefined };
    var stack = false;
    var tls = false;
    var phdr = false;
    for (0..count) |i| {
        const o = offset + i * 56;
        const kind = readu32(b, o);
        const flags = readu32(b, o + 4);
        const off: usize = @intCast(readu64(b, o + 8));
        const addr: usize = @intCast(readu64(b, o + 16));
        const filesz: usize = @intCast(readu64(b, o + 32));
        const memsz: usize = @intCast(readu64(b, o + 40));
        const alignment = readu64(b, o + 48);
        try valid(filesz <= memsz and inside(off, filesz, b.len));
        try valid(alignment <= 4096 and (alignment <= 1 or std.math.isPowerOfTwo(alignment)));
        switch (kind) {
            1 => {
                try valid(flags == 4 or flags == 5 or flags == 6);
                try valid(memsz > 0 and addr >= 0x200000 and addr < 0x40000000 and memsz <= 0x40000000 - addr and off % 4096 == addr % 4096);
                const lo = addr & ~@as(usize, 4095);
                const hi = (addr + memsz + 4095) & ~@as(usize, 4095);
                for (result.segments[0..result.count]) |s| {
                    const sl = s.address & ~@as(usize, 4095);
                    const sh = (s.address + s.memsz + 4095) & ~@as(usize, 4095);
                    try valid(hi <= sl or lo >= sh);
                }
                result.segments[result.count] = .{ .flags = flags, .offset = off, .address = addr, .filesz = filesz, .memsz = memsz };
                result.count += 1;
            },
            6 => {
                try valid(!phdr and off == offset and filesz == count * 56 and memsz == filesz and flags == 4);
                phdr = true;
                result.phdr = addr;
            },
            7 => {
                try valid(!tls and flags == 4 and memsz > 0 and memsz <= 4096);
                tls = true;
            },
            0x6474e551 => {
                try valid(!stack and flags == 6);
                stack = true;
            },
            0x6474e550, 0x6474e552 => {
                try valid(flags == 4);
            },
            else => return error.InvalidImage,
        }
    }
    try valid(stack and tls and phdr and result.count > 0);
    var entry = false;
    var ph = false;
    var pages: usize = 16;
    for (result.segments[0..result.count]) |s| {
        if (s.flags == 5 and result.entry >= s.address and result.entry - s.address < s.filesz) entry = true;
        if (result.phdr >= s.address and inside(result.phdr - s.address, count * 56, s.filesz) and s.offset + result.phdr - s.address == offset) ph = true;
        pages += (s.address % 4096 + s.memsz + 4095) / 4096;
    }
    try valid(entry and ph and pages <= limits.pages);
    // Every TLS/RELRO/metadata view must bind bytes in exactly one load segment.
    for (0..count) |i| {
        const o = offset + i * 56;
        const kind = readu32(b, o);
        if (kind != 7 and kind != 0x6474e552 and kind != 0x6474e550) continue;
        const addr: usize = @intCast(readu64(b, o + 16));
        const off: usize = @intCast(readu64(b, o + 8));
        const filesz: usize = @intCast(readu64(b, o + 32));
        const memsz: usize = @intCast(readu64(b, o + 40));
        var matches: usize = 0;
        for (result.segments[0..result.count]) |s| {
            if (addr >= s.address and inside(addr - s.address, memsz, s.memsz) and inside(addr - s.address, filesz, s.filesz) and s.offset + addr - s.address == off) {
                if (kind == 0x6474e552) try valid((addr & ~@as(usize, 4095)) == (s.address & ~@as(usize, 4095)) and addr + memsz >= s.address + s.memsz);
                matches += 1;
            }
        }
        try valid(matches == 1);
    }
    return result;
}
test "reject malformed native ELF" {
    try std.testing.expectError(error.InvalidImage, parse("bad"));
    const b = [_]u8{0} ** 64;
    try std.testing.expectError(error.InvalidImage, parse(&b));
}

fn putHeader(b: []u8, index: usize, kind: u32, flags: u32, offset: u64, address: u64, filesz: u64, memsz: u64) void {
    const h = b[64 + index * 56 ..][0..56];
    std.mem.writeInt(u32, h[0..4], kind, .little);
    std.mem.writeInt(u32, h[4..8], flags, .little);
    std.mem.writeInt(u64, h[8..16], offset, .little);
    std.mem.writeInt(u64, h[16..24], address, .little);
    std.mem.writeInt(u64, h[32..40], filesz, .little);
    std.mem.writeInt(u64, h[40..48], memsz, .little);
    std.mem.writeInt(u64, h[48..56], 1, .little);
}
fn fixture() [8196]u8 {
    var b = [_]u8{0} ** 8196;
    @memcpy(b[0..8], "\x7fELF\x02\x01\x01\x00");
    std.mem.writeInt(u16, b[16..18], 2, .little);
    std.mem.writeInt(u16, b[18..20], 62, .little);
    std.mem.writeInt(u32, b[20..24], 1, .little);
    std.mem.writeInt(u64, b[24..32], 0x201000, .little);
    std.mem.writeInt(u64, b[32..40], 64, .little);
    std.mem.writeInt(u16, b[52..54], 64, .little);
    std.mem.writeInt(u16, b[54..56], 56, .little);
    std.mem.writeInt(u16, b[56..58], 7, .little);
    putHeader(&b, 0, 6, 4, 64, 0x200040, 7 * 56, 7 * 56);
    putHeader(&b, 1, 1, 4, 0, 0x200000, 4096, 4096);
    putHeader(&b, 2, 1, 5, 4096, 0x201000, 1, 1);
    putHeader(&b, 3, 1, 6, 8192, 0x202000, 4, 8);
    putHeader(&b, 4, 7, 4, 8192, 0x202000, 4, 8);
    putHeader(&b, 5, 0x6474e551, 6, 0, 0, 0, 0);
    putHeader(&b, 6, 0x6474e550, 4, 512, 0x200200, 8, 8);
    b[4096] = 0xc3; // Header-shaped fixture, never executed.
    return b;
}
test "bounded native ELF accepts layout and rejects authority and range changes" {
    const base = fixture();
    const parsed = try parse(&base);
    try std.testing.expectEqual(@as(usize, 0x201000), parsed.entry);
    try std.testing.expectEqual(@as(usize, 3), parsed.count);
    for ([_]usize{ 0, 4, 5, 7, 16, 18, 20, 52, 54, 56 }) |offset| {
        var b = base;
        b[offset] = 0xff;
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        std.mem.writeInt(u64, b[24..32], 0x202000, .little);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        putHeader(&b, 2, 1, 7, 4096, 0x201000, 1, 1);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        putHeader(&b, 2, 1, 5, 4096, 0x200000, 1, 1);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        putHeader(&b, 3, 1, 6, 8192, 0x202000, 4096, 4096);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        putHeader(&b, 3, 1, 6, 8192, 0x202000, 4, 512 * 4096);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    for ([_]u32{ 2, 3, 0xffffffff }) |kind| {
        var b = base;
        putHeader(&b, 6, kind, 4, 512, 0x200200, 8, 8);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        putHeader(&b, 4, 7, 4, 8192, 0x203000, 4, 8);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
    {
        var b = base;
        putHeader(&b, 5, 0x6474e551, 7, 0, 0, 0, 0);
        try std.testing.expectError(error.InvalidImage, parse(&b));
    }
}

test "explicit large limits accept exact mapping budget and reject one page more" {
    var b = fixture();
    putHeader(&b, 3, 1, 6, 8192, 0x202000, 4, 2030 * 4096);
    _ = try parseWithLimits(&b, large_limits);
    try std.testing.expectError(error.InvalidImage, parse(&b));
    putHeader(&b, 3, 1, 6, 8192, 0x202000, 4, 2031 * 4096);
    try std.testing.expectError(error.InvalidImage, parseWithLimits(&b, large_limits));
    try std.testing.expectError(error.InvalidImage, parseWithLimits(&b, .{ .pages = 2049 }));
    try std.testing.expectError(error.InvalidImage, parseWithLimits(&b, .{ .file_bytes = 8 * 1024 * 1024 + 1 }));
}
test "large file limit preserves static and permission rejection" {
    const b = try std.testing.allocator.alloc(u8, 2 * 1024 * 1024);
    defer std.testing.allocator.free(b);
    @memset(b, 0);
    const small = fixture();
    @memcpy(b[0..small.len], &small);
    _ = try parseWithLimits(b, large_limits);
    try std.testing.expectError(error.InvalidImage, parse(b));
    std.mem.writeInt(u16, b[16..18], 3, .little);
    try std.testing.expectError(error.InvalidImage, parseWithLimits(b, large_limits));
    std.mem.writeInt(u16, b[16..18], 2, .little);
    putHeader(b, 2, 1, 7, 4096, 0x201000, 1, 1);
    try std.testing.expectError(error.InvalidImage, parseWithLimits(b, large_limits));
}
