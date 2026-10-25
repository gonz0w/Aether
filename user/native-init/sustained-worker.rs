// SPDX-License-Identifier: BSD-2-Clause
// Unprivileged ABI22 enforcement probe, not a userland protocol implementation.
#![no_std]
#![no_main]
use core::arch::{asm, global_asm};
// Native ELF entry receives an initial stack, not a C return address. Calling
// Rust from its aligned initial RSP supplies the SysV entry alignment.
global_asm!(
    ".section .text.entry,\"ax\"",
    ".global _start",
    "_start:",
    "and rsp, -16",
    "call sustained_worker",
    "ud2"
);
fn call(op: u64, grant: u64) -> i64 {
    let result;
    // Scalar-only denied requests; no pointer is borrowed or dereferenced here.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") grant,
             in("rsi") 0u64, inlateout("rdx") 0u64 => _, in("r10") 0u64,
             lateout("rcx") _, inlateout("r8") 0u64 => _, in("r9") 0u64,
             options(nostack));
    }
    result
}
fn exit(code: u64) -> ! {
    call(0x1003c, code);
    unsafe { asm!("ud2", options(noreturn)) }
}
#[unsafe(no_mangle)]
pub extern "C" fn sustained_worker() -> ! {
    for (op, grant) in [
        (0x2a000, 0xe002),
        (0x2a001, 0xe002),
        (0x2a002, 0xf002),
        (0x26000, 0xf001),
        (0x26001, 0xf001),
        (0x26002, 0xf001),
        (0x24000, 0xd001),
    ] {
        let expected = if cfg!(wrong_expectation) { 0 } else { -13 };
        if call(op, grant) != expected {
            exit(77);
        }
    }
    exit(0)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    exit(78)
}
