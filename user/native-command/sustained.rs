// SPDX-License-Identifier: BSD-2-Clause
// Private producer witness commands; sys-init/userland own the real input policy.
use super::*;
fn op(number: u64, cap: u64, a: u64, b: u64) -> (i64, u64, u64) {
    call(number, cap, a, b, 0, 0, 0)
}
pub fn write(bytes: &[u8]) {
    for byte in bytes {
        loop {
            let result = op(0x26001, 0xf001, byte as *const u8 as u64, 1).0;
            if result == 1 {
                break;
            }
            check(result == -11, 2805);
            ctl(0x1fffe, 0);
        }
    }
}
pub fn begin() {
    check(op(0x2a000, 0xe001, 0, 0).0 == -13, 2805);
    check(op(0x2a002, 0xe002, 0, 0).0 == -13, 2805);
    check(op(0x2a002, 0xf002, 1, 0).0 == -38, 2805);
    check(op(0x2a002, 0xf002, 0, 0).0 == -16, 2805);
    let before = op(0x2a000, 0xe002, 0, 0);
    write(b"SI07 idle-ready\n");
    let done = op(0x2a001, 0xe002, before.1, 3005);
    check(done.0 == -110 && done.2 >= 3005, 2805);
}
pub fn input(prompt: &[u8], expected: u8) {
    write(prompt);
    loop {
        let before = op(0x2a000, 0xe002, 0, 0);
        check(before.0 == 0, 2805);
        let mut byte = 0u8;
        let result = op(0x26000, 0xf001, &mut byte as *mut u8 as u64, 1).0;
        if result == 1 {
            check(byte == expected, 2805);
            return;
        }
        check(result == -11, 2805);
        check(op(0x2a001, 0xe002, before.1, 0).0 == 0, 2805);
    }
}
pub fn halt() -> ! {
    input(b"SI07 halt-ready\n", b'h');
    check(op(0x26002, 0xf001, 0, 0).0 == 0, 2805);
    op(0x2a002, 0xf002, 0, 0);
    unsafe { core::arch::asm!("ud2", options(noreturn)) }
}

// Handles here are successful kernel launch results owned by this supervisor.
// Equality is a cohort check, not a capability grant or generation truncation.
#[cfg(init_sustained_v2)]
pub fn cohort(owned: &[(Connection, u64)], epoch: u32) {
    if (1..=65535).contains(&epoch)
        && owned
            .iter()
            .all(|(c, slot)| c.child == ((0x31u64 << 56) | (*slot << 32) | epoch as u64))
    {
        return;
    }
    // Reject before carrier/bootstrap/receipt publication; settle every owned peer.
    for (c, _) in owned {
        check(ctl(0x20007, c.child).0 == 0, 2806);
        check(terminal(c.child) == (143, 3), 2806);
        check(
            ctl(0x24003, c.writer).0 == 0 && ctl(0x24003, c.reader).0 == 0,
            2806,
        );
        check(ctl(0x20002, c.child).0 == 0, 2806);
        check(ctl(0x20001, c.child).0 == -9, 2806);
    }
    write(b"SI07 cohort rejected after reclaim\n");
    end(2806)
}
