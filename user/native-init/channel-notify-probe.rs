// SPDX-License-Identifier: BSD-2-Clause
// Private ABI24 asynchronous child-notification witness, not init or shell policy.
#![no_std]
#![no_main]
use core::arch::asm;
fn raw(op: u64, cap: u64, a: u64, b: u64, c: u64, d: u64, e: u64) -> (i64, u64, u64) {
    let (r, x, y);
    // Trap copies synchronously; pointer arguments borrow live local storage.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => r, in("rdi") cap,
             in("rsi") a, inlateout("rdx") b => x, in("r10") c,
             inlateout("r8") d => y, in("r9") e, lateout("rcx") _, options(nostack));
    }
    (r, x, y)
}
fn call(op: u64, cap: u64, a: u64, b: u64) -> (i64, u64, u64) {
    raw(op, cap, a, b, 0, 0, 0)
}
fn write(bytes: &[u8]) {
    for byte in bytes {
        while call(0x26001, 0xf001, byte as *const u8 as u64, 1).0 == -11 {}
    }
}
fn check(ok: bool) {
    if !ok {
        write(b"CHANNEL notification failed\n");
        unsafe { asm!("ud2", options(noreturn)) }
    }
}
fn pause(ticks: u64) {
    let deadline = call(0x2a000, 0xe002, 0, 0).2 + ticks;
    loop {
        let observed = call(0x2a000, 0xe002, 0, 0);
        if observed.2 >= deadline {
            return;
        }
        let result = call(0x2a001, 0xe002, observed.1, deadline).0;
        check(result == 0 || result == -110);
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, _: u64, _: u64, channels: u64, _: u64) -> ! {
    check(abi == 24 && factory == 0xa001 && channels == 0xd001);
    for mode in b'1'..=b'2' {
        let input = call(0x24000, channels, 0, 0);
        let output = call(0x24000, channels, 0, 0);
        let child_input = call(0x24000, channels, 0, 0);
        let child_output = call(0x24000, channels, 0, 0);
        check(
            [input.0, output.0, child_input.0, child_output.0]
                .iter()
                .all(|c| *c > 0),
        );
        let mut args = [0u8; 272];
        args[0] = 1;
        args[16] = mode;
        let parent = raw(
            0x23002,
            factory,
            0xc001,
            0,
            args.as_ptr() as u64,
            input.0 as u64,
            output.1,
        )
        .0;
        check(parent > 0);
        loop {
            let observed = call(0x2a000, 0xe002, 0, 0);
            let frozen = call(0x23004, parent as u64, 0, 0).0;
            if frozen == 1 {
                break;
            }
            check(frozen == 0);
            check(call(0x2a001, 0xe002, observed.1, observed.2 + 100).0 == 0);
        }
        let child = raw(
            0x23006,
            factory,
            parent as u64,
            1,
            1,
            child_input.0 as u64,
            child_output.1,
        )
        .0;
        check(child > 0);
        check(call(0x24004, output.0 as u64, 0, 0).0 == 0);
        let mut ready = 0;
        check(
            call(0x24001, output.0 as u64, &mut ready as *mut u8 as u64, 1).0 == 1 && ready == b'p',
        );
        // Both peers have empty inputs. Delay allows the parent to park after
        // its readiness publication; premature return would terminate it77.
        pause(100);
        check(call(0x20001, parent as u64, 0, 0).0 == 0);
        check(call(0x20001, child as u64, 0, 0).0 == 0);
        let release = b'c';
        check(call(0x24002, child_input.1, &release as *const u8 as u64, 1).0 == 1);
        terminal(child as u64, 18);
        if mode == b'2' {
            // Child is terminal, but a masked notification must not finish wait.
            pause(100);
            check(call(0x20001, parent as u64, 0, 0).0 == 0);
            let release = b'h';
            check(call(0x24002, input.1, &release as *const u8 as u64, 1).0 == 1);
        }
        check(call(0x24004, output.0 as u64, 0, 0).0 == 0);
        let mut reply = 0;
        check(
            call(0x24001, output.0 as u64, &mut reply as *mut u8 as u64, 1).0 == 1 && reply == b'w',
        );
        terminal(parent as u64, 1);
        for task in [child, parent] {
            check(call(0x20002, task as u64, 0, 0).0 == 0);
            check(call(0x20001, task as u64, 0, 0).0 == -9);
        }
        for cap in [
            input.1,
            output.0 as u64,
            child_input.1,
            child_output.0 as u64,
        ] {
            check(call(0x24003, cap, 0, 0).0 == 0);
            check(call(0x24004, cap, 0, 0).0 == -13);
        }
    }
    write(b"CHANNEL notification checked\n");
    check(call(0x26002, 0xf001, 0, 0).0 == 0);
    call(0x2a002, 0xf002, 0, 0);
    unsafe { asm!("ud2", options(noreturn)) }
}
fn terminal(task: u64, expected: i64) {
    loop {
        let observed = call(0x2a000, 0xe002, 0, 0);
        let status = call(0x20001, task, 0, 0).0;
        if status != 0 {
            check(status == expected);
            return;
        }
        check(call(0x2a001, 0xe002, observed.1, observed.2 + 100).0 == 0);
    }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { asm!("ud2", options(noreturn)) }
}
