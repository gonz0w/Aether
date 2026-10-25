// SPDX-License-Identifier: BSD-2-Clause
// Bounded intake witness only; sys-init retains supervision policy.
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, handle: u64, value: u64) -> (i64, u64, u64) {
    let result: i64;
    let kind: u64;
    let ready: u64;
    // Scalar owner-local handles; native ABI supplies the clobbered registers.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") handle,
             in("rsi") value, lateout("r8") kind, lateout("rdx") ready,
             lateout("rcx") _, lateout("r9") _, lateout("r10") _, lateout("r11") _);
    }
    (result, kind, ready)
}
fn end(code: u64) -> ! {
    call(0x20006, code, 0);
    loop {
        core::hint::spin_loop();
    }
}
fn check(ok: bool) {
    if !ok {
        end(401);
    }
}
fn terminal(handle: u64, expected: (i64, u64)) {
    for _ in 0..1000000 {
        let state = call(0x20001, handle, 0);
        if state.0 > 0 {
            check((state.0, state.1) == expected);
            return;
        }
        check(state.0 == 0);
        call(0x1fffe, 0, 0);
    }
    end(402)
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64) -> ! {
    check(abi == 1 && factory == 0xa001);
    let a = call(0x20000, factory, 0).0;
    check(a > 0);
    #[cfg(stop_live)]
    {
        let mut ready = false;
        for _ in 0..1000000 {
            let state = call(0x20001, a as u64, 0);
            check(state.0 == 0);
            if state.2 == 1 {
                ready = true;
                break;
            }
            call(0x1fffe, 0, 0);
        }
        check(ready && call(0x20002, a as u64, 0).0 == -16);
    }
    let b = call(0x20000, factory, 1).0;
    check(b > 0);
    #[cfg(stop_live)]
    {
        check(call(0x20007, a as u64, 0).0 == 0);
        terminal(a as u64, (144, 3));
    }
    #[cfg(not(stop_live))]
    terminal(a as u64, (1, 1));
    terminal(b as u64, (1, 1));
    check(call(0x20002, a as u64, 0).0 == 0);
    check(call(0x20001, a as u64, 0).0 == -9);
    let fresh = call(0x20000, factory, 0).0;
    check(fresh > 0 && fresh != a);
    check(call(0x20001, a as u64, 0).0 == -9 && call(0x20002, a as u64, 0).0 == -9);
    terminal(fresh as u64, (1, 1));
    check(call(0x20002, fresh as u64, 0).0 == 0 && call(0x20002, b as u64, 0).0 == 0);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(403)
}
