// SPDX-License-Identifier: BSD-2-Clause
// Private BSP q35/TCG CMOS owner, never a physical RTC/NMI policy implementation.
const rtc = @import("../../native_rtc.zig");
fn tcg() bool {
    var ebx: u32 = undefined;
    var ecx: u32 = undefined;
    var edx: u32 = undefined;
    asm volatile ("cpuid"
        : [b] "={ebx}" (ebx),
          [c] "={ecx}" (ecx),
          [d] "={edx}" (edx),
        : [a] "{eax}" (@as(u32, 0x40000000)),
        : .{ .eax = true });
    // Hypervisor leaf uses EBX, ECX, EDX order: "TCGTCGTCGTCG".
    return ebx == 0x54474354 and ecx == 0x43544743 and edx == 0x47435447;
}
const Reader = struct {
    pub fn read(_: *@This(), index: u8) u8 {
        // TCG RTC ignores selector bit7. No CMOS data or register C access.
        @import("serial.zig").out(0x70, index);
        return asm volatile ("inb %[port], %[value]"
            : [value] "={al}" (-> u8),
            : [port] "{dx}" (@as(u16, 0x71)),
        );
    }
    pub fn now(_: *@This()) rtc.Error!u64 {
        return @import("clock.zig").read();
    }
};
pub fn observe() rtc.Error!rtc.Observation {
    const flags = asm volatile ("pushfq; popq %[v]"
        : [v] "=r" (-> u64),
    );
    if (flags & (1 << 9) != 0 or !tcg()) return error.Unavailable;
    var reader: Reader = .{};
    return rtc.observe(&reader);
}
