// SPDX-License-Identifier: BSD-2-Clause
// Private ABI24 channel wait witness, not init or shell policy.
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
        write(b"CHANNEL wait failed\n");
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
    let mut stale = 0;
    for mode in b'1'..=b'7' {
        let input = call(0x24000, channels, 0, 0);
        let output = call(0x24000, channels, 0, 0);
        check(input.0 > 0 && output.0 > 0);
        if stale != 0 {
            check(call(0x24004, stale, 0, 0).0 == -13);
        }
        let mut args = [0u8; 272];
        args[0] = 1;
        args[16] = mode;
        let bytes = [b'x'; 32];
        if mode == b'3' || mode == b'6' {
            for offset in [0, 16] {
                check(call(0x24002, output.1, bytes[offset..].as_ptr() as u64, 16).0 == 16);
            }
        }
        let task = raw(
            0x23002,
            factory,
            0xc001,
            0,
            args.as_ptr() as u64,
            input.0 as u64,
            output.1,
        )
        .0;
        check(task > 0);
        loop {
            let observed = call(0x2a000, 0xe002, 0, 0);
            let state = call(0x20001, task as u64, 0, 0);
            check(state.0 == 0);
            if state.1 != 0 {
                break;
            }
            check(call(0x2a001, 0xe002, observed.1, observed.2 + 100).0 == 0);
        }
        // Neither owner nor worker is runnable during this interval. A fake
        // immediate wait return makes the worker fault or finish before wake.
        pause(if mode == b'1' { 3005 } else { 3 });
        check(call(0x20001, task as u64, 0, 0).0 == 0);
        if mode == b'2' {
            check(call(0x24003, input.1, 0, 0).0 == 0);
        } else if mode == b'3' {
            let mut value = 0;
            check(
                call(0x24001, output.0 as u64, &mut value as *mut u8 as u64, 1).0 == 1
                    && value == b'x',
            );
        } else if mode == b'4' {
            check(call(0x20007, task as u64, 0, 0).0 == 0);
        } else {
            if mode == b'6' {
                check(call(0x24003, output.0 as u64, 0, 0).0 == 0);
            }
            let value = b'h';
            check(call(0x24002, input.1, &value as *const u8 as u64, 1).0 == 1);
            if mode != b'6' {
                check(call(0x24004, output.0 as u64, 0, 0).0 == 0);
                let mut reply = 0;
                check(
                    call(0x24001, output.0 as u64, &mut reply as *mut u8 as u64, 1).0 == 1
                        && reply == value,
                );
            }
        }
        loop {
            let observed = call(0x2a000, 0xe002, 0, 0);
            let state = call(0x20001, task as u64, 0, 0);
            if state.0 != 0 {
                check(state.0 == if mode == b'4' { 144 } else { 1 });
                break;
            }
            let r = call(0x2a001, 0xe002, observed.1, observed.2 + 100).0;
            check(r == 0);
        }
        check(call(0x20002, task as u64, 0, 0).0 == 0);
        check(call(0x24003, input.1, 0, 0).0 == if mode == b'2' { -13 } else { 0 });
        check(call(0x24003, output.0 as u64, 0, 0).0 == if mode == b'6' { -13 } else { 0 });
        stale = input.0 as u64;
        check(call(0x24004, stale, 0, 0).0 == -13);
    }
    write(b"CHANNEL wait checked\n");
    check(call(0x26002, 0xf001, 0, 0).0 == 0);
    call(0x2a002, 0xf002, 0, 0);
    unsafe { asm!("ud2", options(noreturn)) }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { asm!("ud2", options(noreturn)) }
}
