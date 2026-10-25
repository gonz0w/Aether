// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;
fn call(op: u64, h: u64, v: u64) -> (i64, u64, u64) {
    let result: i64; let ready: u64; let kind: u64;
    unsafe { asm!("int 0x81", inlateout("rax") op => result, in("rdi") h,
        in("rsi") v, lateout("rdx") ready, lateout("rcx") _, lateout("r8") kind); }
    (result, ready, kind)
}
fn end(code: u64) -> ! { call(0x20006, code, 0); loop { core::hint::spin_loop(); } }
fn check(ok: bool, code: u64) { if !ok { end(code); } }
fn yield_now() { call(0x1fffe, 0, 0); }
fn output(h: u64, generation: u8, eof: bool) {
    for stream in 1..=2 {
        let bytes = if stream == 1 { [b'o', b'u', b't', b':', b'0'+generation, b'\n'] }
                    else { [b'e', b'r', b'r', b':', b'0'+generation, b'\n'] };
        for (offset, byte) in bytes.iter().enumerate() {
            check(call(0x20009, h, (stream<<32) | offset as u64).0 == *byte as i64, 301);
        }
        check(call(0x20009, h, (stream<<32) | 6).0 == if eof {256} else {-11}, 302);
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64) -> ! {
    check(abi == 2 && factory == 0xa001, 300);
    let mut previous = 0;
    for generation in 1..=2 {
        let value = call(0x20000, factory, 0).0;
        check(value > 0 && value as u64 != previous, 303);
        let h = value as u64;
        let mut ready = false;
        for _ in 0..100000 {
            let s = call(0x20001, h, 0);
            check(s.0 == 0 && s.2 == 0, 304);
            if s.1 == 1 { ready = true; break; }
            yield_now();
        }
        check(ready, 305);
        output(h, generation, false);
        let fault = generation == 1 && cfg!(fault_first);
        let stopped = generation == 1 && !fault;
        if stopped { check(call(0x20007, h, 0).0 == 0, 306); }
        else { check(call(0x20008, h, if fault { b'F' } else { b'X' } as u64).0 == 0, 306); }
        let expected_kind = if stopped {3} else if fault {if cfg!(wrong_kind) {1} else {2}} else {1};
        let expected_status = if stopped {144} else if fault {135} else {1};
        let mut terminal = false;
        for _ in 0..100000 {
            let s = call(0x20001, h, 0);
            if s.0 != 0 {
                check(s.0 == expected_status && s.2 == expected_kind && s.1 == 1, 307);
                terminal = true; break;
            }
            yield_now();
        }
        check(terminal, 308);
        output(h, generation, true);
        check(call(0x20008, h, 65).0 == -32 && call(0x20008, h, 256).0 == -32, 309);
        check(call(0x20002, h, 0).0 == 0, 310);
        for (op,arg) in [(0x20001,0),(0x20007,0),(0x20008,65),
                         (0x20009,1<<32),(0x20009,2<<32),(0x20002,0)] {
            check(call(op,h,arg).0 == -9,311);
        }
        previous = h;
    }
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { end(399) }
