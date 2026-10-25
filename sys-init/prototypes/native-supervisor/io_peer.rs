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

fn output(h: u64, ack: bool, eof: bool) {
    for stream in 1..=2 {
        let bytes = if stream == 1 { b"out:1\n" } else { b"err:1\n" };
        for (offset, byte) in bytes.iter().enumerate() {
            check(call(0x20009,h,(stream<<32)|offset as u64).0 == *byte as i64, 601);
        }
        let length = if stream == 1 && ack {
            check(call(0x20009,h,(stream<<32)|6).0 == 80, 602); 7
        } else {6};
        check(call(0x20009,h,(stream<<32)|length).0 == if eof {256} else {-11}, 603);
    }
}
fn stage(h: u64, ack: bool) {
    for _ in 0..100000 {
        check(call(0x20001,h,0).0 == 0, 604);
        if call(0x20009,h,if ack {(1<<32)|6} else {(2<<32)|5}).0 == if ack {80} else {10} {return;}
        yield_now();
    }
    end(605)
}
fn send(h: u64, byte: u64) { check(call(0x20008,h,byte).0 == 0, 606); }
fn reclaim(h: u64) {
    check(call(0x20002,h,0).0 == 0, 610);
    for (op,arg) in [(0x20001,0),(0x20007,0),(0x20008,65),
                    (0x20009,1<<32),(0x20009,2<<32),(0x20002,0)] {
        check(call(op,h,arg).0 == -9, 611);
    }
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64) -> ! {
    check(abi == 2 && factory == 0xa001, 600);
    let a = call(0x20000,factory,0).0;
    let b = call(0x20000,factory,1).0;
    check(a > 0 && b > 0 && a != b, 600);
    let handles = if cfg!(reverse) {[b as u64,a as u64]} else {[a as u64,b as u64]};
    for h in handles {stage(h,false); check(call(0x20001,h,0) == (0,0,0),604); output(h,false,false);}
    for i in 0..2 {
        for shift in 0..8 {send(handles[i], (handles[1-i]>>(shift*8))&255);}
    }
    send(handles[0], b'P' as u64);
    stage(handles[0],true);
    check(call(0x20001,handles[0],0) == (0,1,0),607);
    check(call(0x20001,handles[1],0) == (0,if cfg!(peer_ready) {1} else {0},0),607);
    output(handles[0],true,false); output(handles[1],false,false);
    send(handles[1],b'P' as u64); stage(handles[1],true);
    for h in handles {check(call(0x20001,h,0) == (0,1,0),608); output(h,true,false);}
    check(call(0x20007,handles[0],0).0 == 0,609);
    check(call(0x20001,handles[0],0) == (144,1,3),609);
    output(handles[0],true,true);
    check(call(0x20008,handles[0],256).0 == -32,609);
    reclaim(handles[0]);
    check(call(0x20001,handles[1],0) == (0,1,0),609);
    output(handles[1],true,false); send(handles[1],b'X' as u64);
    let mut terminal = false;
    for _ in 0..100000 {
        let s = call(0x20001,handles[1],0);
        if s.0 != 0 {check(s == (1,1,1),609); terminal = true; break;}
        yield_now();
    }
    check(terminal,609); output(handles[1],true,true);
    check(call(0x20008,handles[1],256).0 == -32,609); reclaim(handles[1]);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {end(699)}
