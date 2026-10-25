#![no_std]
#![no_main]
use core::arch::asm;
fn call(op:u64,h:u64,v:u64)->(i64,u64,u64,u64) {
    let result:i64; let ready:u64; let progress:u64; let kind:u64;
    unsafe {asm!("int 0x81",inlateout("rax") op=>result,in("rdi") h,in("rsi") v,lateout("rdx") ready,lateout("rcx") progress,lateout("r8") kind);}
    (result,ready,progress,kind)
}
fn end(code:u64)->! {call(0x20006,code,0);loop {core::hint::spin_loop();}}
fn check(ok:bool,code:u64) {if !ok {end(code);}}
fn yield_now() {call(0x1fffe,0,0);}
fn observe(h:u64)->(i64,u64,u64,u64) {let s=call(0x20001,h,0);check(s.0>=0,201);s}
fn terminal(h:u64)->(i64,u64,u64,u64) {for _ in 0..100000 {let s=observe(h);if s.0>0 {return s;}yield_now();}end(202)}
fn output(h:u64) {for (i,b) in b"AETHER MUSL NATIVE PASS\n".iter().enumerate(){check(call(0x20003,h,i as u64).0==*b as i64,203);}check(call(0x20003,h,24).0==-11,204);}
#[unsafe(no_mangle)]
#[unsafe(link_section=".text.entry")]
pub extern "C" fn _start(abi:u64,factory:u64)->! {
    if cfg!(fault_entry) {unsafe {asm!("ud2",options(noreturn));}}
    check(abi==1&&factory==0xa001,210);
    check(call(0x20000,0,0).0==-13,211);
    let first=call(0x20000,factory,0).0 as u64;
    let peer=call(0x20000,factory,1).0 as u64;
    check(call(0x20000,factory,0).0==-16,212);
    check(call(0x20002,peer,0).0==-16,213);
    let failed=terminal(first);
    check(failed.0==135 && failed.1==1 && failed.3==2,214); // #UD: status 134 + terminal tag.
    if cfg!(wrong_detail) {check(failed.0==999,215);}
    output(first);
    let before=observe(peer).2;
    for _ in 0..8 {yield_now();}
    let after=observe(peer);
    check(after.0==0&&after.1==1&&after.2>before,216);
    output(peer);
    check(call(0x20002,first,0).0==0,217);
    check(call(0x20001,first,0).0==-9,218);
    // Policy allows exactly one replacement of the failed primary.
    let replacement=call(0x20000,factory,0).0 as u64;
    check(replacement!=first&&call(0x20001,first,0).0==-9,219);
    let done=terminal(replacement);check(done.0==1&&done.1==1&&done.3==1,220);output(replacement);
    check(call(0x20002,replacement,0).0==0,221);
    check(call(0x20007,peer,0).0==0,222);
    let stopped=observe(peer);check(stopped.0==144&&stopped.3==3,223);
    check(call(0x20002,peer,0).0==0,224);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo)->! {end(299)}
