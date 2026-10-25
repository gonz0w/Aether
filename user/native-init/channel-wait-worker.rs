// SPDX-License-Identifier: BSD-2-Clause
// Private ABI24 readiness witness; no libc or sys-init policy.
#![no_std]
#![no_main]
use core::arch::{asm, global_asm};
global_asm!(
    ".section .text.entry,\"ax\"",
    ".global _start",
    "_start:",
    "mov rdi, rsp",
    "and rsp, -16",
    "call worker",
    "ud2"
);
fn raw(op: u64, cap: u64, a: u64, b: u64, c: u64, d: u64, e: u64) -> i64 {
    let r;
    // Synchronous trap; buffer pointers remain valid until return. Wait has none.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => r, in("rdi") cap,
             in("rsi") a, inlateout("rdx") b => _, in("r10") c,
             inlateout("r8") d => _, in("r9") e, lateout("rcx") _, options(nostack));
    }
    r
}
fn call(op: u64, cap: u64, a: u64, b: u64) -> i64 {
    raw(op, cap, a, b, 0, 0, 0)
}
fn check(ok: bool) {
    if !ok {
        exit(77);
    }
}
fn exit(code: u64) -> ! {
    call(0x1003c, code, 0, 0);
    unsafe { asm!("ud2", options(noreturn)) }
}
#[unsafe(no_mangle)]
pub extern "C" fn worker(stack: *const u64) -> ! {
    // Kernel-created stack contains a bounded argc/argv/env/aux vector. This
    // witness reads only mapped boot words and the admitted one-byte argument.
    let (mode, reader, writer) = unsafe {
        check(*stack == 1);
        let mode = *(*stack.add(1) as *const u8);
        let mut n = 3;
        while *stack.add(n) != 0 {
            n += 1;
            check(n < 32);
        }
        n += 1;
        let (mut reader, mut writer) = (0, 0);
        while *stack.add(n) != 0 {
            check(n < 96);
            match *stack.add(n) {
                0xa001 => reader = *stack.add(n + 1),
                0xa002 => writer = *stack.add(n + 1),
                _ => (),
            }
            n += 2;
        }
        (mode, reader, writer)
    };
    check(reader != 0 && writer != 0);
    check(call(0x24004, reader ^ 3, 0, 0) == if cfg!(wrong_expectation) { 0 } else { -13 }); // foreign opposite end.
    check(call(0x24004, 0xd001, 0, 0) == -13);
    for field in 0..5 {
        check(
            raw(
                0x24004,
                reader,
                (field == 0) as u64,
                (field == 1) as u64,
                (field == 2) as u64,
                (field == 3) as u64,
                (field == 4) as u64,
            ) == -22,
        );
    }
    if mode == b'7' {
        // Queue a caught signal under a mask. No handler is injected by wait.
        let record = [
            signal_entry as *const () as u64,
            0x04000000,
            signal_entry as *const () as u64,
            0,
        ];
        check(raw(0x29001, 10, record.as_ptr() as u64, 0, 8, 0, 0) == 0);
        let mask = 1u64 << 9;
        check(raw(0x1000e, 2, &mask as *const u64 as u64, 0, 8, 0, 0) == 0);
        check(call(0x29002, 10, 0, 0) == 0);
    }
    check(call(0x20004, 0, 0, 0) == 0);
    if mode == b'3' {
        check(call(0x24004, writer, 0, 0) == 0);
        let value = b'w';
        check(call(0x24002, writer, &value as *const u8 as u64, 1) == 1);
    } else {
        check(call(0x24004, reader, 0, 0) == 0);
        let mut value = 0;
        let n = call(0x24001, reader, &mut value as *mut u8 as u64, 1);
        if mode == b'2' {
            check(n == 0 && value == 0);
        } else if mode == b'6' {
            check(n == 1 && value == b'h');
            check(call(0x24004, writer, 0, 0) == 0);
            check(call(0x24002, writer, &value as *const u8 as u64, 1) == -32);
        } else {
            check(n == 1 && value == b'h');
            if mode == b'7' {
                let mask = 0u64;
                check(raw(0x1000e, 2, &mask as *const u64 as u64, 0, 8, 0, 0) == 0);
                // EINTR preserves pending state; repeated waits see it again.
                for _ in 0..2 {
                    check(call(0x24004, reader, 0, 0) == -4);
                }
                let ignore = [1u64, 0, 0, 0];
                check(raw(0x29001, 10, ignore.as_ptr() as u64, 0, 8, 0, 0) == 0);
            }
            check(call(0x24004, writer, 0, 0) == 0);
            check(call(0x24002, writer, &value as *const u8 as u64, 1) == 1);
        }
    }
    exit(0)
}
extern "C" fn signal_entry() {
    exit(79); // Explicit delivery is deliberately not invoked by this witness.
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    exit(78)
}
