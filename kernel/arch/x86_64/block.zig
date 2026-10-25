// SPDX-License-Identifier: BSD-2-Clause
// BSP-only legacy virtio-blk bring-up. All DMA storage stays reserved until reboot.
const std = @import("std");
const serial = @import("serial.zig");
var queue: [12288]u8 align(4096) = @splat(0);
var header: [16]u8 align(16) = @splat(0);
var data: [512]u8 align(512) = @splat(0);
var status: u8 = 0;
var physical: u64 = 0;
var virtual: u64 = 0;
var port: u16 = 0;
var size: u16 = 0;
var avail: usize = 0;
var used: usize = 0;
var sequence: u16 = 0;
var capacity: u64 = 0;
fn read32(p: u16) u32 {
    return asm volatile ("inl %[p], %[v]"
        : [v] "={eax}" (-> u32),
        : [p] "{dx}" (p),
    );
}
fn read16(p: u16) u16 {
    return asm volatile ("inw %[p], %[v]"
        : [v] "={ax}" (-> u16),
        : [p] "{dx}" (p),
    );
}
fn read8(p: u16) u8 {
    return asm volatile ("inb %[p], %[v]"
        : [v] "={al}" (-> u8),
        : [p] "{dx}" (p),
    );
}
fn write32(p: u16, v: u32) void {
    asm volatile ("outl %[v], %[p]"
        :
        : [v] "{eax}" (v),
          [p] "{dx}" (p),
    );
}
fn write16(p: u16, v: u16) void {
    asm volatile ("outw %[v], %[p]"
        :
        : [v] "{ax}" (v),
          [p] "{dx}" (p),
    );
}
fn config(device: u32, offset: u8) u32 {
    write32(0xcf8, device | offset);
    return read32(0xcfc);
}
fn phys(p: anytype) u64 {
    return physical + (@intFromPtr(p) - virtual);
}
fn q16(offset: usize) *volatile u16 {
    return @ptrCast(@alignCast(&queue[offset]));
}
fn q32(offset: usize) *volatile u32 {
    return @ptrCast(@alignCast(&queue[offset]));
}
fn barrier() void {
    asm volatile ("mfence" ::: .{ .memory = true });
}
fn init() void {
    var found: ?u32 = null;
    // Deliberately bounded to bus zero in the documented QEMU topology.
    for (0..256) |function| {
        const device: u32 = 0x80000000 | (@as(u32, @intCast(function)) << 8);
        if (config(device, 0) != 0x10011af4) continue;
        if (found != null) @panic("block duplicate device");
        found = device;
    }
    const device = found orelse @panic("block device absent");
    const bar = config(device, 0x10);
    if (bar & 1 == 0 or bar & 0xfffffffc > 65500 or bar & 0xfffffffc == 0) @panic("block unsupported BAR");
    port = @intCast(bar & 0xfffffffc);
    // MSI-X is not used; reject firmware-enabled MSI-X rather than guessing
    // the legacy device configuration offset. INTx is disabled below.
    var cap: u8 = @truncate(config(device, 0x34));
    var remaining: usize = 48;
    while (cap != 0 and remaining > 0) : (remaining -= 1) {
        if (cap < 0x40 or cap & 3 != 0) @panic("block invalid PCI capability");
        const entry = config(device, cap);
        if (entry & 255 == 0x11 and entry & 0x80000000 != 0) @panic("block MSI-X unsupported");
        cap = @truncate(entry >> 8);
    }
    if (cap != 0) @panic("block PCI capability cycle");
    const command: u16 = @truncate(config(device, 4));
    write16(0xcfc, command | 5 | 0x400); // I/O, bus master; disable INTx.
    serial.out(port + 18, 0);
    if (read8(port + 18) != 0) @panic("block reset failed");
    serial.out(port + 18, 1);
    serial.out(port + 18, 3);
    const features = read32(port);
    if (features & (1 << 5) != 0) @panic("block read-only device");
    if (features & (1 << 9) == 0) @panic("block flush unsupported");
    write32(port + 4, 1 << 9);
    const first = @as(u64, read32(port + 20)) | (@as(u64, read32(port + 24)) << 32);
    const second = @as(u64, read32(port + 20)) | (@as(u64, read32(port + 24)) << 32);
    if (first != second or first < 9) @panic("block invalid capacity");
    capacity = first;
    write16(port + 14, 0);
    size = read16(port + 12);
    if (size < 4 or size > 256 or !std.math.isPowerOfTwo(size)) @panic("block unsupported queue");
    avail = 16 * @as(usize, size);
    used = (avail + 6 + 2 * @as(usize, size) + 4095) & ~@as(usize, 4095);
    q16(avail).* = 1; // Suppress interrupts; poll used ring.
    const address = phys(&queue);
    if (address & 4095 != 0 or address >> 12 > std.math.maxInt(u32)) @panic("block invalid DMA address");
    write32(port + 8, @intCast(address >> 12));
    serial.out(port + 18, 7);
}
fn descriptor(index: usize, address: u64, len: u32, flags: u16, next: u16) void {
    const bytes = queue[index * 16 ..][0..16];
    std.mem.writeInt(u64, bytes[0..8], address, .little);
    std.mem.writeInt(u32, bytes[8..12], len, .little);
    std.mem.writeInt(u16, bytes[12..14], flags, .little);
    std.mem.writeInt(u16, bytes[14..16], next, .little);
}
fn request(kind: u32, sector: u64) error{OutOfRange}!void {
    if (kind != 4 and sector >= capacity) return error.OutOfRange;
    std.mem.writeInt(u32, header[0..4], kind, .little);
    std.mem.writeInt(u64, header[8..16], sector, .little);
    const result: *volatile u8 = &status;
    result.* = 255;
    descriptor(0, phys(&header), 16, 1, if (kind == 4) 2 else 1);
    descriptor(1, phys(&data), 512, if (kind == 0) 3 else 1, 2);
    descriptor(2, phys(&status), 1, 2, 0);
    q16(avail + 4 + 2 * @as(usize, sequence % size)).* = 0;
    barrier();
    q16(avail + 2).* = sequence +% 1;
    barrier();
    write16(port + 16, 0);
    var remaining: usize = 10_000_000;
    while (q16(used + 2).* == sequence and remaining > 0) : (remaining -= 1) asm volatile ("pause");
    if (remaining == 0) @panic("block timeout; DMA retained");
    barrier();
    if (q16(used + 2).* != sequence +% 1 or q32(used + 4 + 8 * @as(usize, sequence % size)).* != 0) @panic("block invalid completion; DMA retained");
    if (result.* != 0) @panic("block device I/O failed");
    sequence +%= 1;
}
// Only kernel-owned buffers are accepted here. Caller serializes all operations.
pub fn initialize(pbase: u64, vbase: u64) void {
    physical = pbase;
    virtual = vbase;
    init();
}
pub fn sectorCount() u64 {
    return capacity;
}
pub fn readSector(sector: u64, destination: *[512]u8) error{OutOfRange}!void {
    try request(0, sector);
    @memcpy(destination, &data);
}
pub fn writeSector(sector: u64, source: *const [512]u8) error{OutOfRange}!void {
    if (sector >= capacity) return error.OutOfRange;
    @memcpy(&data, source);
    try request(1, sector);
}
pub fn flush() void {
    request(4, 0) catch unreachable;
}
pub fn experiment(pbase: u64, vbase: u64, verify: bool) noreturn {
    asm volatile ("cli");
    physical = pbase;
    virtual = vbase;
    init();
    request(0, capacity) catch |err| {
        if (err != error.OutOfRange or sequence != 0) @panic("block range guard failed");
    };
    for (0..300) |_| request(0, 7) catch unreachable; // Wrap queue positions.
    for (data, 0..) |value, i| {
        const expected: u8 = @truncate(i * 17 + (if (verify) @as(usize, 91) else 3));
        if (value != expected) @panic("block seed mismatch");
    }
    if (!verify) {
        for (&data, 0..) |*value, i| value.* = @truncate(i * 17 + 91);
        request(1, 7) catch unreachable;
        request(4, 0) catch unreachable;
        serial.write("AETHER BLOCK WRITE PASS\n");
    } else serial.write("AETHER BLOCK VERIFY PASS\n");
    // No DMA backing is reclaimed. VM teardown is the quiescence boundary.
    serial.halt();
}
