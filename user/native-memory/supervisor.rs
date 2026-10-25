// SPDX-License-Identifier: BSD-2-Clause
// Fixed conformance sequence only; production supervision belongs to sys-init.
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, handle: u64, value: u64) -> (i64, u64, u64, u64) {
    let result: i64;
    let kind: u64;
    let ready: u64;
    let yields: u64;
    unsafe { asm!("int 0x81", inlateout("rax") op => result, in("rdi") handle,
                  in("rsi") value, lateout("r8") kind, lateout("rcx") yields, lateout("rdx") ready); }
    (result, kind, ready, yields)
}
fn end(code: u64) -> ! { call(0x20006, code, 0); loop { core::hint::spin_loop(); } }
fn check(ok: bool) { if !ok { end(301); } }
// The no-deadline witness deliberately spans 200 native timer ticks.
const POLL_LIMIT: usize = if cfg!(long_wait) { 1_000_000 } else { 100000 };
fn terminal(h: u64) {
    for _ in 0..POLL_LIMIT {
        let value = call(0x20001, h, 0);
        if value.0 > 0 {
            #[cfg(taskq_allocation_failure)]
            check(value.0 == 303 && value.1 == 1);
            #[cfg(not(taskq_allocation_failure))]
            check(value.0 == 1 && value.1 == 1 && value.3 == 64);
            return;
        }
        check(value.0 == 0); call(0x1fffe, 0, 0);
    }
    end(302)
}
#[unsafe(no_mangle)]
#[unsafe(link_section=".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64) -> ! {
    check(abi == 1 && factory == 0xa001);
    let a = call(0x20000, factory, 0).0 as u64;
    #[cfg(stop_live)]
    {
        let mut ready = false;
        for _ in 0..POLL_LIMIT {
            let state = call(0x20001, a, 0);
            check(state.0 == 0);
            if state.2 == 1 { ready = true; break; }
            call(0x1fffe, 0, 0);
        }
        check(ready && call(0x20002, a, 0).0 == -16);
    }
    let b = call(0x20000, factory, 1).0 as u64;
    #[cfg(stop_live)]
    {
        check(call(0x20007, a, 0).0 == 0);
        let state = call(0x20001, a, 0);
        check(state.0 == 144 && state.1 == 3 && state.2 == 1);
        // Deliberately wrong terminal expectation must reject at this point.
        #[cfg(bad_stop)]
        if state.1 != 1 { end(304); }
        check(call(0x20007, a, 0).0 == 0);
        check(call(0x20001, a, 0) == state);
        let peer = call(0x20001, b, 0);
        check(peer.0 == 0 && peer.3 < 64); // Must still make progress after stop.
    }
    #[cfg(not(stop_live))]
    terminal(a);
    terminal(b);
    check(call(0x20002, a, 0).0 == 0);
    check(call(0x20001, a, 0).0 == -9);
    check(call(0x20007, a, 0).0 == -9 && call(0x20002, a, 0).0 == -9);
    let fresh = call(0x20000, factory, 0).0 as u64;
    check(fresh != a && call(0x20001, a, 0).0 == -9);
    terminal(fresh);
    check(call(0x20002, fresh, 0).0 == 0);
    check(call(0x20002, b, 0).0 == 0);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { end(303) }
