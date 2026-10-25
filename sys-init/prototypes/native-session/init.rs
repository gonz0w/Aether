// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
#[cfg(not(all(pipeline_dash_parent, session_serial, session_lifecycle)))]
compile_error!("sys-init serial entry requires the matched ABI24 lifecycle profile");
#[path = "dispatch/user/native-capacity/session-owner.rs"]
mod dispatch;
use core::arch::asm;

// One session, no automatic replay, final action only after confirmed settlement.
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, first: u64, second: u64,
                        channels: u64, third: u64) -> ! {
    let expected_abi = if cfg!(session_test_wrong_abi) { 23 } else { 24 };
    if (abi, factory, first, second, channels, third)
        != (expected_abi, 0xa001, 0xc001, 0xc002, 0xd001, 0xc003) {
        dispatch::fail();
    }
    dispatch::run_to_settlement();
    let result: i64;
    // Scalar arguments only; kernel checks owner/grant and complete quiescence.
    unsafe {
        asm!("int 0x81", inlateout("rax") 0x2a002_u64 => result,
             in("rdi") 0xf002_u64, in("rsi") 0_u64, in("rdx") 0_u64,
             in("r10") 0_u64, in("r8") 0_u64, in("r9") 0_u64,
             lateout("rcx") _, options(nostack));
    }
    // A successful halt never returns. Any rejection retains the failed state.
    #[cfg(session_test_leave_console)]
    if result != -16 { unsafe { asm!("ud2", options(noreturn)) } }
    let _ = result;
    dispatch::fail()
}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { dispatch::fail() }
