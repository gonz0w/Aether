#![no_std]
#![no_main]
use core::arch::asm;
fn call(op:u64,h:u64,v:u64)->(i64,u64,u64) {
 let result:i64;let ready:u64;let kind:u64;
 unsafe{asm!("int 0x81",inlateout("rax") op=>result,in("rdi") h,in("rsi") v,lateout("rdx") ready,lateout("rcx") _,lateout("r8") kind);}
 (result,ready,kind)
}
fn end(code:u64)->!{call(0x20006,code,0);loop{core::hint::spin_loop();}}
fn check(ok:bool,code:u64){if !ok{end(code);}}
fn yield_now(){call(0x1fffe,0,0);}
fn output(h:u64,stream:u64,expected:&[u8]) {
 for (i,b) in expected.iter().enumerate(){check(call(0x20009,h,(stream<<32)|i as u64).0==*b as i64,230);}
 check(call(0x20009,h,(stream<<32)|expected.len() as u64).0==256,231);
}
#[unsafe(no_mangle)]
#[unsafe(link_section=".text.entry")]
pub extern "C" fn _start(abi:u64,factory:u64)->! {
 check(abi==2&&factory==0xa001,210);
 for _ in 0..2 {
 let h=call(0x20000,factory,0).0 as u64;
 let mut ready=false;
 for _ in 0..100000 {let s=call(0x20001,h,0);check(s.0==0,211);if s.1==1{ready=true;break;}yield_now();}
 check(ready,212);
 for b in b"0123456789abcdefghijklmnopqrstuv" {check(call(0x20008,h,*b as u64).0==0,213);}
 check(call(0x20008,h,99).0==-11,214);
 check(call(0x20008,h,256).0==0,215);
 check(call(0x20008,h,99).0==-32,216);
 let mut done=false;
 for _ in 0..100000 {let s=call(0x20001,h,0);if s.0!=0{check(s.0==1&&s.2==1,217);done=true;break;}yield_now();}
 check(done,218);
 output(h,1,b"native descriptors ok\n");output(h,2,b"native error stream\n");
 check(call(0x20008,h,65).0==-32,219);
 check(call(0x20002,h,0).0==0,220);
 check(call(0x20009,h,1<<32).0==-9,221);
 }
 end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo)->!{end(299)}
