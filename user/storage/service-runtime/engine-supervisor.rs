// SPDX-License-Identifier: BSD-2-Clause
// Private admission witness; production launch/recovery policy belongs to sys-init.
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, handle: u64, value: u64) -> (i64, u64) {
    let result: i64;
    let kind: u64;
    // Scalar owner-local handles; no user pointer or shared authority is retained.
    unsafe {
        asm!("int 0x81", inlateout("rax") op => result, in("rdi") handle,
             in("rsi") value, lateout("r8") kind, lateout("rdx") _,
             lateout("rcx") _, lateout("r9") _, lateout("r10") _, lateout("r11") _);
    }
    (result, kind)
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
fn byte(handle: u64, offset: u64) -> u8 {
    let value = call(0x20003, handle, offset).0;
    check((0..=255).contains(&value));
    value as u8
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64) -> ! {
    check(abi == 1 && factory == 0xa001);
    // The same engine image is explicitly denied in the small peer partition.
    check(call(0x20000, factory, 1).0 == -12);
    let mut stale = 0;
    for _ in 0..3 {
        let owner = call(0x20000, factory, 0).0;
        check(owner > 0 && owner != stale);
        if stale != 0 {
            check(call(0x20001, stale as u64, 0).0 == -9);
            check(call(0x20002, stale as u64, 0).0 == -9);
        }
        let owner = owner as u64;
        let mut completed = false;
        for _ in 0..1000000 {
            let state = call(0x20001, owner, 0);
            if state.0 > 0 {
                check(state == (1, 1));
                completed = true;
                break;
            }
            check(state.0 == 0);
            call(0x1fffe, 0, 0);
        }
        check(completed);
        for (stage, tag) in b"BIFR".iter().enumerate() {
            let offset = stage as u64 * 8;
            check(byte(owner, offset) == *tag);
            let live = byte(owner, offset + 1);
            let admissions = byte(owner, offset + 2) as u16 | (byte(owner, offset + 3) as u16) << 8;
            let free = byte(owner, offset + 4) as u16 | (byte(owner, offset + 5) as u16) << 8;
            let total = byte(owner, offset + 6) as u16 | (byte(owner, offset + 7) as u16) << 8;
            check(total == 8192 && free <= total && admissions > 0 && admissions <= 512);
            check(match stage {
                0 => live == 1 && admissions == 1,
                1 => live > 1 && live <= 82 && admissions > 1,
                2 => live <= 82,
                _ => live == 0,
            });
        }
        check(call(0x20003, owner, 32).0 == -11);
        check(call(0x20002, owner, 0).0 == 0);
        check(call(0x20001, owner, 0).0 == -9);
        stale = owner as i64;
    }
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    end(403)
}
