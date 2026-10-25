// SPDX-License-Identifier: BSD-2-Clause
// Mechanism witness only: this is not sys-init or its sustained command policy.
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, cap: u64, a: u64, b: u64) -> (i64, u64, u64) {
    raw(op, cap, a, b, 0, 0, 0)
}
fn raw(op: u64, cap: u64, a: u64, b: u64, c: u64, d: u64, e: u64) -> (i64, u64, u64) {
    let (r, x, y);
    unsafe {
        asm!("int 0x81", inlateout("rax") op => r, in("rdi") cap,
             in("rsi") a, inlateout("rdx") b => x, in("r10") c,
             inlateout("r8") d => y, in("r9") e, lateout("rcx") _, options(nostack));
    }
    (r, x, y)
}
fn write(bytes: &[u8]) {
    for byte in bytes {
        while call(0x26001, 0xf001, byte as *const u8 as u64, 1).0 == -11 {}
    }
}
fn check(ok: bool) {
    if !ok {
        write(b"SI07 probe failed\n");
        unsafe { asm!("ud2", options(noreturn)) }
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, _: u64, _: u64, channels: u64, _: u64) -> ! {
    check(abi == 22 && factory == 0xa001 && channels == 0xd001);
    check(call(0x2a000, 0xe001, 0, 0).0 == -13);
    check(call(0x2a002, 0xe002, 0, 0).0 == -13);
    check(call(0x2a002, 0xf002, 1, 0).0 == -38);
    check(call(0x2a002, 0xf002, 0, 0).0 == -16); // UART still owned.
    check(call(0x20006, 100, 0, 0).0 == -38);
    let initial = call(0x2a000, 0xe002, 0, 0);
    for op in 0x2a000..=0x2a002 {
        let grant = if op == 0x2a002 { 0xf002 } else { 0xe002 };
        for reserved in 0..3 {
            check(
                raw(
                    op,
                    grant,
                    0,
                    0,
                    (reserved == 0) as u64,
                    (reserved == 1) as u64,
                    (reserved == 2) as u64,
                )
                .0 == -22,
            );
        }
    }
    check(call(0x2a000, 0xe002, 1, 0).0 == -22);
    check(call(0x2a000, 0xe002, 0, 1).0 == -22);
    check(call(0x2a002, 0xf002, 0, 1).0 == -22);
    check(call(0x2a000, 0xe002, 0, 0).1 == initial.1);
    // Publish a real channel event between observation and registration.
    let pair = call(0x24000, channels, 0, 0);
    check(pair.0 > 0);
    let event = call(0x2a001, 0xe002, initial.1, initial.2 + 100);
    check(event.0 == 0 && event.1 > initial.1);
    check(call(0x24003, pair.0 as u64, 0, 0).0 == 0);
    check(call(0x24003, pair.1, 0, 0).0 == 0);
    let mut stale_task = 0;
    for generation in 1..=6 {
        let mut args = [0u8; 272];
        args[0] = 1;
        args[16..22].copy_from_slice(b"worker");
        let task = raw(0x23000, factory, 0xc001, 0, args.as_ptr() as u64, 0, 0).0;
        check(task as u64 == (0x3100000000000000 | generation));
        if stale_task != 0 {
            check(call(0x20001, stale_task, 0, 0).0 == -9);
        }
        loop {
            let observed = call(0x2a000, 0xe002, 0, 0);
            let terminal = call(0x20001, task as u64, 0, 0);
            if terminal.0 != 0 {
                if terminal.0 != 1 || terminal.2 != 1 {
                    check(call(0x20002, task as u64, 0, 0).0 == 0);
                    check(call(0x20001, task as u64, 0, 0).0 == -9);
                    write(b"SI07 worker-rejected\n");
                    check(false);
                }
                break;
            }
            check(call(0x2a001, 0xe002, observed.1, observed.2 + 100).0 == 0);
        }
        check(call(0x20002, task as u64, 0, 0).0 == 0);
        stale_task = task as u64;
        check(call(0x20001, stale_task, 0, 0).0 == -9);
    }
    write(b"SI07 authority-checked\n");
    let mut stale = 0;
    for _ in 0..6 {
        let pair = call(0x24000, channels, 0, 0);
        check(pair.0 > 0 && pair.1 > 0 && pair.0 as u64 != stale);
        if stale != 0 {
            check(call(0x24003, stale, 0, 0).0 == -13);
        }
        stale = pair.0 as u64;
        check(call(0x24003, pair.0 as u64, 0, 0).0 == 0);
        check(call(0x24003, pair.1, 0, 0).0 == 0);
    }
    let before = call(0x2a000, 0xe002, 0, 0);
    check(before.0 == 0);
    check(call(0x2a001, 0xe002, before.1 + 1, 0).0 == -22);
    write(b"SI07 idle-ready\n");
    let deadline = before.2 + 3005;
    let expired = call(0x2a001, 0xe002, before.1, deadline);
    check(expired.0 == -110 && expired.2 >= deadline);
    write(b"SI07 input-ready\n");
    let before = call(0x2a000, 0xe002, 0, 0);
    let woke = call(0x2a001, 0xe002, before.1, 0);
    check(woke.0 == 0 && woke.2 >= 3005);
    // Do not consume input yet: registration must see the same ready byte.
    let still_ready = call(0x2a000, 0xe002, 0, 0);
    check(call(0x2a001, 0xe002, still_ready.1, still_ready.2 + 100).0 == 0);
    let mut byte = 0u8;
    check(call(0x26000, 0xf001, &mut byte as *mut u8 as u64, 1).0 == 1 && byte == b'h');
    let consumed = call(0x2a000, 0xe002, 0, 0);
    check(call(0x2a001, 0xe002, consumed.1, consumed.2 + 2).0 == -110);
    write(b"SI07 input-received\n");
    check(call(0x26002, 0xf001, 0, 0).0 == 0);
    call(0x2a002, 0xf002, 0, 0);
    unsafe { asm!("ud2", options(noreturn)) }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { asm!("ud2", options(noreturn)) }
}
