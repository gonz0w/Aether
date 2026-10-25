// SPDX-License-Identifier: BSD-2-Clause
// COM1 remains kernel-owned; native console access requires a scoped grant.
pub fn out(port: u16, value: u8) void {
    asm volatile ("outb %[value], %[port]"
        :
        : [value] "{al}" (value),
          [port] "{dx}" (port),
    );
}

fn in(port: u16) u8 {
    return asm volatile ("inb %[port], %[value]"
        : [value] "={al}" (-> u8),
        : [port] "{dx}" (port),
    );
}

var input_status: @import("../../native_sustained.zig").SerialStatus = .{};
fn lineStatus() u8 {
    return input_status.observe(in(0x3fd));
}

pub fn init() void {
    out(0x3f9, 0); // Interrupts disabled.
    out(0x3fb, 0x80);
    out(0x3f8, 1); // 115200 baud.
    out(0x3f9, 0);
    out(0x3fb, 3); // 8N1.
    out(0x3fa, 0xc7);
    out(0x3fc, 3);
}

pub fn write(bytes: []const u8) void {
    for (bytes) |byte| {
        // A missing UART must not hang panic handling indefinitely.
        var remaining: usize = 100_000;
        while (lineStatus() & 0x20 == 0 and remaining > 0) : (remaining -= 1) {}
        if (remaining == 0) return;
        out(0x3f8, byte);
    }
}

pub fn halt() noreturn {
    while (true) asm volatile ("cli; hlt");
}

// Nonblocking primitives: caller serializes access and validates user buffers.
pub fn readByte() error{LineError}!?u8 {
    const status = lineStatus();
    if (input_status.takeError(status)) {
        if (status & 1 != 0) _ = in(0x3f8);
        return error.LineError;
    }
    if (status & 1 == 0) return null;
    return in(0x3f8);
}

pub fn writeByte(value: u8) bool {
    if (lineStatus() & 0x20 == 0) return false;
    out(0x3f8, value);
    return true;
}

// Level observation only: preserve receive bytes and line errors for the grant holder.
pub fn inputReady() bool {
    return input_status.ready(lineStatus());
}
