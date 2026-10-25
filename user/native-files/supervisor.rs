// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;
#[repr(C)]struct Args{argc:u64,envc:u64,strings:[[u8;32];8]}
fn args(probe:bool)->Args{let mut a=Args{argc:2,envc:0,strings:[[0;32];8]};a.strings[0][0]=b'h';let word=if probe{b"probe" as &[u8]}else{b"files"};for(i,b)in word.iter().enumerate(){a.strings[1][i]=*b;}a}
fn call(op:u64,a:u64,b:u64,c:u64,d:u64,e:u64,f:u64)->(i64,u64,u64){let r:i64;let x:u64;let k:u64;unsafe{asm!("int 0x81",inlateout("rax")op=>r,in("rdi")a,in("rsi")b,inlateout("rdx")c=>x,in("r10")d,inlateout("r8")e=>k,in("r9")f,lateout("rcx")_,options(nostack));}(r,x,k)}
fn ctl(op:u64,h:u64)->(i64,u64,u64){call(op,h,0,0,0,0,0)}
fn end(n:u64)->!{ctl(0x20006,n);loop{core::hint::spin_loop();}}
fn check(ok:bool,n:u64){if !ok{end(n);}}
fn terminal(h:u64,want:i64){for _ in 0..100000{let s=ctl(0x20001,h);if s.0!=0{check(s.0==want+1&&s.2==1,611);return;}ctl(0x1fffe,0);}end(612)}
#[unsafe(no_mangle)]#[unsafe(link_section=".text.entry")]
pub extern "C" fn _start(abi:u64,factory:u64,service:u64,client:u64,channels:u64)->!{
    check(abi==5&&factory==0xa001&&service==0xc001&&client==0xc002&&channels==0xd001,601);
    let request=ctl(0x24000,channels);let response=ctl(0x24000,channels);
    check(request.0>0&&response.0>0&&request.0!=response.0&&ctl(0x24000,channels).0 == -16,602);
    let mut a=args(false);a.argc=5;let ptr=&a as *const Args as u64;
    check(call(0x23002,factory,service,0,ptr,request.0 as u64,response.1).0 == -22,603);
    check(call(0x24001,request.0 as u64,0,0,0,0,0).0==0&&call(0x24002,response.1,0,0,0,0,0).0==0,604);
    a.argc=2;
    check(call(0x23002,factory,service,0,&a as *const Args as u64,request.0 as u64,request.0 as u64).0 == -13,605);
    let server=call(0x23002,factory,service,0,&a as *const Args as u64,request.0 as u64,response.1).0 as u64;
    check(server==0xb0000101&&ctl(0x24003,request.0 as u64).0 == -13&&ctl(0x24003,response.1).0 == -13,606);
    let user=call(0x23002,factory,client,1,&a as *const Args as u64,response.0 as u64,request.1).0 as u64;
    check(user==0xb0000102&&ctl(0x24003,response.0 as u64).0 == -13&&ctl(0x24003,request.1).0 == -13,607);
    terminal(user,29);terminal(server,17);
    check(ctl(0x20002,user).0==0&&ctl(0x20002,server).0==0,608);
    let probe=args(true);let third=call(0x23000,factory,client,0,&probe as *const Args as u64,0,0).0 as u64;
    check(third==0xb0000201,609);terminal(third,33);check(ctl(0x20002,third).0==0,610);
    end(100)
}
#[panic_handler]fn panic(_: &core::panic::PanicInfo)->!{end(699)}
