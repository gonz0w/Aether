// SPDX-License-Identifier: BSD-2-Clause
//! Fixed engine/process mechanism witness. Init and POSIX policy stay in owners.
#![no_std]
#![no_main]
use core::arch::asm;
#[path = "../service-runtime/fs-activation-client.rs"]
mod activation;
#[path = "service-client.rs"]
mod service;
#[cfg(fs_owner_16k)]
#[path = "wide.rs"]
mod wide;

#[inline(never)]
fn call(op: u64, a: u64, b: u64, c: u64, d: u64, e: u64) -> (i64, u64, u64) {
    let result: i64;
    let second: u64;
    let third: u64;
    // SAFETY: scalar labels/handles or synchronous borrows validated by kernel;
    // no pointer retained, and all native volatile output registers declared.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") a,
            in("rsi") b, inlateout("rdx") c => second, in("r10") d,
            inlateout("r8") e => third, in("r9") 0u64,
            lateout("rcx") _, lateout("r11") _);
    }
    (result, second, third)
}
fn ctl(op: u64, handle: u64) -> (i64, u64, u64) {
    call(op, handle, 0, 0, 0, 0)
}
fn check(ok: bool) {
    if !ok {
        // Retain failed/unknown resources; do not normalize failure into cleanup.
        unsafe { asm!("ud2", options(noreturn)) }
    }
}
fn observe(value: u8) {
    let raw = [value; 8];
    check(call(0x10001, 1, raw.as_ptr() as u64, 8, 0, 0).0 == 8);
}
fn witness(txg: u64) {
    observe(b'T');
    for value in txg.to_le_bytes() {
        observe(value);
    }
}
fn poll(remaining: &mut u32) {
    check(*remaining != 0);
    *remaining -= 1;
    ctl(0x1fffe, 0);
}
fn terminal(handle: u64, remaining: &mut u32) {
    loop {
        poll(remaining);
        let state = ctl(0x20001, handle);
        if state.0 != 0 {
            check(state.0 == 1 && state.2 == 1);
            break;
        }
    }
}
fn arguments() -> [u8; 272] {
    let mut raw = [0; 272];
    raw[0] = 1;
    raw[16] = b'p';
    raw
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, block: u64) -> ! {
    check((abi, factory, block) == (if cfg!(fs_owner_16k) { 29 } else { 28 }, 0xa001, 0xf101));
    #[cfg(fs_owner_16k)]
    {
        check(wide::verify());
        observe(b'W');
    }
    let connection = service::Connection::new();
    let engine = connection.admit(factory) as u64;
    let region = [8u64, 2097152, 7];
    check(call(0x27005, block, engine, region.as_ptr() as u64, 24, 0).0 == 0);
    let mut remaining = 1_000_000;
    check(activation::ready(engine, &mut remaining));
    observe(b'R');
    // Engine helpers cannot become process freeze/copy/exec targets. These
    // denials happen before effects; the ready engine remains usable afterward.
    check(ctl(0x23004, engine).0 == -13);
    check(call(0x23008, factory, engine, 0, 0, 0).0 == -13);
    check(call(0x23000, factory, 0xc001, 0, 0, 0).0 == -13);
    let args = arguments();
    let process = call(0x23000, factory, 0xc001, 1, args.as_ptr() as u64, 0).0;
    check(process > 0);
    let process = process as u64;
    loop {
        poll(&mut remaining);
        let sequence = ctl(0x23004, process).0;
        check(sequence == 0 || sequence == 1);
        if sequence == 1 {
            break;
        }
    }
    check(ctl(0x20001, engine).0 == 0);
    check(call(0x23007, factory, process, 0xc002, 1, args.as_ptr() as u64).0 == 0);
    check(call(0x23008, factory, process, 0, 0, 0) == (1, 0xc002, 1));
    check(call(0x23009, factory, process, 1, 0, 0).0 == 0);
    terminal(process, &mut remaining);
    check(call(0x20003, process, 0, 0, 0, 0).0 == b'P' as i64);
    check(call(0x20003, process, 1, 0, 0, 0).0 == -11);
    check(ctl(0x20002, process).0 == 0 && ctl(0x20001, process).0 == -9);
    observe(b'P');
    connection.exercise(); // Exact AF06 nine-mutation/96-request transcript.
    terminal(engine, &mut remaining);
    connection.finish(true);
    check(ctl(0x20002, engine).0 == 0 && ctl(0x20001, engine).0 == -9);
    observe(b'C');
    check(ctl(0x26002, 0xf001).0 == 0);
    ctl(0x2a002, 0xf002);
    check(false);
    loop {
        core::hint::spin_loop();
    }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    check(false);
    loop {
        core::hint::spin_loop();
    }
}
