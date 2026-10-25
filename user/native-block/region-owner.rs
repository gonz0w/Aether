// SPDX-License-Identifier: BSD-2-Clause
// Transport conformance only; terminal and supervision policy belong to consumers.
#![no_std]
#![no_main]
use core::arch::asm;
fn raw(op: u64, grant: u64, buffer: u64, count: u64, size: u64) -> i64 {
    let result;
    // Native interrupt ABI preserves other registers except these documented outputs.
    // Buffer lifetime spans the synchronous call; the kernel validates mappings.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") grant,
             in("rsi") buffer, inlateout("rdx") count => _, lateout("rcx") _,
             lateout("r8") _, lateout("r9") _, in("r10") size);
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

fn call(op: u64, grant: u64, buffer: u64, count: u64) -> i64 {
    raw(op, grant, buffer, count, 0)
}
fn query(grant: u64) {
    let mut info = [0u64; 4];
    check(call(0x27006, grant, info.as_mut_ptr() as u64, 32) == 0, 851);
    check(info == [512, 32768, 7, 0], 852);
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, grant: u64) -> ! {
    check(abi == 14 && factory == 0xa001 && grant == 0xf101, 850);
    query(grant);
    let mut record = [8u64, 16384, if cfg!(block_readonly) { 1 } else { 7 }];
    check(
        raw(0x27005, grant, 0, record.as_ptr() as u64, 24) == -9,
        853,
    );
    let old = call(0x20000, factory, 0, 0) as u64;
    check(wait(old) == 1, 854);
    check(
        raw(0x27005, grant, old, record.as_ptr() as u64, 24) == -9,
        855,
    );
    check(call(0x20002, old, 0, 0) == 0, 856);
    let live = call(0x20000, factory, 0, 0) as u64;
    check(
        live != old && raw(0x27005, grant, old, record.as_ptr() as u64, 24) == -9,
        857,
    );
    for invalid in [
        [0, 0, 7],
        [u64::MAX, 1, 7],
        [1, u64::MAX, 7],
        [32767, 2, 7],
        [32768, 1, 7],
        [8, 16384, 0],
        [8, 16384, 8],
    ] {
        check(
            raw(0x27005, grant, live, invalid.as_ptr() as u64, 24) == -22,
            858,
        );
        query(grant);
    }
    check(
        raw(0x27005, grant, live, record.as_ptr() as u64, 23) == -22,
        859,
    );
    for pointer in [0, u64::MAX, 0x800ff0] {
        check(raw(0x27005, grant, live, pointer, 24) == -14, 860);
        query(grant);
    }
    check(
        raw(0x27005, grant ^ 1, live, record.as_ptr() as u64, 24) == -13,
        861,
    );
    check(
        raw(0x27005, grant, live, record.as_ptr() as u64, 24) == 0,
        862,
    );
    // The kernel must have copied scalar authority, never retained this pointer.
    record = [0, 32768, 7];
    unsafe {
        core::ptr::write_volatile(&mut record, [0, 32768, 7]);
    }
    for op in 0x27000..=0x27006 {
        check(call(op, grant, 0, 0) == -13, 863);
    }
    check(wait(live) == if cfg!(block_fault) { 135 } else { 1 }, 841);
    check(call(0x20002, live, 0, 0) == 0, 843);
    let fresh = call(0x20000, factory, 0, 0) as u64;
    check(fresh != live && wait(fresh) == 1, 844);
    check(call(0x20002, fresh, 0, 0) == 0, 845);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(847)
}
