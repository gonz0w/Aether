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
             lateout("r8") _, lateout("r9") _, in("r10") 0u64);
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
    end(840)
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, grant: u64) -> ! {
    check(abi == 13 && factory == 0xa001 && grant == 0xf101, 830);
    check(call(0x27003, grant, 0, 7) == -9, 831);
    let old = call(0x20000, factory, 0, 0) as u64;
    check(wait(old) == 1, 832);
    check(call(0x27003, grant, old, 7) == -9, 833);
    check(call(0x20002, old, 0, 0) == 0, 834);
    let live = call(0x20000, factory, 0, 0) as u64;
    check(live != old && call(0x27003, grant, old, 7) == -9, 835);
    check(call(0x27003, grant ^ 1, live, 7) == -13, 836);
    check(call(0x27003, grant, live, 8) == -22, 837);
    check(call(0x27002, grant, 0, 0) == 0, 838);
    check(
        call(
            0x27003,
            grant,
            live,
            if cfg!(block_readonly) { 1 } else { 7 },
        ) == 0,
        839,
    );
    for op in 0x27000..=0x27004 {
        check(call(op, grant, 0, 0) == -13, 842);
    }
    let expected = if cfg!(block_fault) { 135 } else { 1 };
    check(wait(live) == expected, 841);
    check(call(0x20002, live, 0, 0) == 0, 843);
    let fresh = call(0x20000, factory, 0, 0) as u64;
    check(fresh != live && wait(fresh) == 1, 844);
    check(call(0x20002, fresh, 0, 0) == 0, 845);
    check(call(0x27003, grant, fresh, 0) == -13, 846);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(847)
}
