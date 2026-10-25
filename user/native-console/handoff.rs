// SPDX-License-Identifier: BSD-2-Clause
// Transport conformance only; terminal and supervision policy belong to consumers.
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, grant: u64, buffer: u64, count: u64) -> i64 {
    let result;
    // Native interrupt ABI preserves other registers except these documented outputs.
    // Buffer lifetime spans the synchronous call; the kernel validates mappings.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") grant,
             in("rsi") buffer, inlateout("rdx") count => _, lateout("rcx") _,
             lateout("r8") _, lateout("r9") _);
    }
    result
}
fn end(code: u64) -> ! {
    call(0x20006, code, 0, 0);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool, code: u64) {
    if !ok {
        end(code);
    }
}
fn wait(h: u64) -> i64 {
    for _ in 0..1000000 {
        let status = call(0x20001, h, 0, 0);
        if status != 0 {
            return status;
        }
        call(0x1fffe, 0, 0, 0);
    }
    end(940)
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, grant: u64) -> ! {
    check(abi == 11 && factory == 0xa001 && grant == 0xf001, 930);
    check(call(0x26003, grant, 0, 0) == -9, 931);
    let old = call(0x20000, factory, 0, 0) as u64;
    check(wait(old) == 1, 932);
    check(call(0x26003, grant, old, 0) == -9, 933);
    check(call(0x20002, old, 0, 0) == 0, 934);
    let live = call(0x20000, factory, 0, 0) as u64;
    check(live != old && call(0x26003, grant, old, 0) == -9, 935);
    check(call(0x26003, grant ^ 1, live, 0) == -13, 936);
    check(call(0x26003, grant, live, 1) == -22, 937);
    check(call(0x26000, grant, 0, 0) == 0, 938);
    check(call(0x26003, grant, live, 0) == 0, 939);
    for op in 0x26000..=0x26003 {
        check(call(op, grant, 0, 0) == -13, 942);
    }
    let expected = if cfg!(handoff_fault) { 135 } else { 1 };
    check(wait(live) == expected, 941);
    check(call(0x20002, live, 0, 0) == 0, 943);
    let fresh = call(0x20000, factory, 0, 0) as u64;
    check(fresh != live && wait(fresh) == 1, 944);
    check(call(0x20002, fresh, 0, 0) == 0, 945);
    check(call(0x26003, grant, fresh, 0) == -13, 946);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(947)
}
