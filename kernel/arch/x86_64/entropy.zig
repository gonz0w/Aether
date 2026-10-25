// SPDX-License-Identifier: BSD-2-Clause
// Opt-in BSP-only virtio-rng experiment. All DMA backing stays reserved.
const std = @import("std");
const serial = @import("serial.zig");
const completion = @import("../../entropy_completion.zig");
pub const Mode = enum { draw, partial, head, length, index, timeout, accept_length };
var queue: [12288]u8 align(4096) = @splat(0);
var data: [256]u8 align(256) = @splat(0);
var physical: u64 = 0;
var virtual: u64 = 0;
var port: u16 = 0;
var size: u16 = 0;
var avail: usize = 0;
var used: usize = 0;
var sequence: u16 = 0;
var partial_count: usize = 0;
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
        const identity = config(device, 0);
        if (identity == 0x10441af4) @panic("entropy modern device unsupported");
        if (identity != 0x10051af4) continue;
        if (found != null) @panic("entropy duplicate device");
        found = device;
    }
    const device = found orelse @panic("entropy device absent");
    const bar = config(device, 0x10);
    if (bar & 1 == 0 or bar & 0xfffffffc > 65500 or bar & 0xfffffffc == 0) @panic("entropy unsupported BAR");
    port = @intCast(bar & 0xfffffffc);
    // MSI-X is not used; reject firmware-enabled MSI-X rather than guessing
    // the legacy device configuration offset. INTx is disabled below.
    var cap: u8 = @truncate(config(device, 0x34));
    var remaining: usize = 48;
    while (cap != 0 and remaining > 0) : (remaining -= 1) {
        if (cap < 0x40 or cap & 3 != 0) @panic("entropy invalid PCI capability");
        const entry = config(device, cap);
        if (entry & 255 == 0x11 and entry & 0x80000000 != 0) @panic("entropy MSI-X unsupported");
        cap = @truncate(entry >> 8);
    }
    if (cap != 0) @panic("entropy PCI capability cycle");
    const command: u16 = @truncate(config(device, 4));
    write16(0xcfc, command | 5 | 0x400); // I/O, bus master; disable INTx.
    serial.out(port + 18, 0);
    if (read8(port + 18) != 0) @panic("entropy reset failed");
    serial.out(port + 18, 1);
    serial.out(port + 18, 3);
    // Entropy has no device-specific feature bits; use a plain split queue.
    write32(port + 4, 0);
    write16(port + 14, 0);
    size = read16(port + 12);
    if (size == 0 or size > 256 or !std.math.isPowerOfTwo(size)) @panic("entropy unsupported queue");
    avail = 16 * @as(usize, size);
    used = (avail + 6 + 2 * @as(usize, size) + 4095) & ~@as(usize, 4095);
    q16(avail).* = 1; // Suppress interrupts; poll used ring.
    const address = phys(&queue);
    if (address & 4095 != 0 or address >> 12 > std.math.maxInt(u32)) @panic("entropy invalid DMA address");
    write32(port + 8, @intCast(address >> 12));
    barrier();
    serial.out(port + 18, 7);
    if (read8(port + 18) != 7) @panic("entropy device status rejected");
}

pub fn clear(bytes: []u8) void {
    for (bytes) |*byte| {
        const value: *volatile u8 = byte;
        value.* = 0;
    }
}
// Caller owns destination and serializes; it is never the DMA destination.
fn fill(destination: []u8, mode: Mode) void {
    var filled: usize = 0;
    while (filled < destination.len) {
        const requested = destination.len - filled;
        std.mem.writeInt(u64, queue[0..8], phys(&data), .little);
        std.mem.writeInt(u32, queue[8..12], @intCast(requested), .little);
        std.mem.writeInt(u16, queue[12..14], 2, .little); // Device-writable only.
        std.mem.writeInt(u16, queue[14..16], 0, .little);
        q16(avail + 4 + 2 * @as(usize, sequence % size)).* = 0;
        barrier();
        q16(avail + 2).* = sequence +% 1;
        barrier();
        write16(port + 16, 0);
        var remaining: usize = 10_000_000;
        while (q16(used + 2).* == sequence and remaining > 0) : (remaining -= 1) asm volatile ("pause");
        if (remaining == 0 or mode == .timeout) @panic("entropy timeout; DMA retained");
        barrier();
        const offset = used + 4 + 8 * @as(usize, sequence % size);
        const index = if (mode == .index) sequence +% 2 else q16(used + 2).*;
        const head = if (mode == .head) @as(u32, 1) else q32(offset).*;
        const written = if (mode == .length or mode == .accept_length) @as(u32, @intCast(requested + 1)) else q32(offset + 4).*;
        // Private deliberately broken validator must fail the length oracle.
        const received = if (mode == .accept_length) requested else completion.validate(sequence, index, head, written, requested) catch |err| switch (err) {
            error.Index => @panic("entropy invalid index; DMA retained"),
            error.Head => @panic("entropy invalid head; DMA retained"),
            error.Length => @panic("entropy invalid length; DMA retained"),
        };
        sequence +%= 1;
        if (received < requested) partial_count += 1;
        @memcpy(destination[filled..][0..received], data[0..received]);
        clear(&data);
        for (data) |value| if (value != 0) @panic("entropy DMA clearing failed");
        filled += received;
    }
}
// Only the explicit BSP native profile may initialize/use this transport.
pub fn initialize(pbase: u64, vbase: u64) void {
    physical = pbase;
    virtual = vbase;
    init();
}
pub fn draw(destination: []u8) void {
    std.debug.assert(destination.len > 0 and destination.len <= 256);
    fill(destination, .draw);
}
pub fn experiment(pbase: u64, vbase: u64, mode: Mode) noreturn {
    asm volatile ("cli");
    physical = pbase;
    virtual = vbase;
    init();
    serial.write("ENTROPY queue ready\n");
    var sample: [256]u8 = undefined;
    for (0..(if (mode == .partial) @as(usize, 12) else 300)) |_| {
        fill(&sample, mode);
        clear(&sample);
        for (sample) |value| if (value != 0) @panic("entropy destination clearing failed");
    }
    if (mode == .partial) {
        if (partial_count == 0) @panic("entropy partial witness missing");
        serial.write("ENTROPY partial completion checked\n");
    }
    serial.write("AETHER ENTROPY PASS\n");
    // Unknown or completed DMA backing is never reclaimed; teardown is quiescence.
    serial.halt();
}
