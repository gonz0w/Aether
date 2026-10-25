// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
use core::arch::asm;
#[repr(C)]
struct Args { argc:u64,envc:u64,strings:[[u8;32];8] }
fn args(mode:&[u8])->Args {
    let mut a=Args{argc:2,envc:0,strings:[[0;32];8]};
    a.strings[0][0]=b'h';
    for(i,b)in mode.iter().enumerate(){a.strings[1][i]=*b;}a
}
fn call(op:u64,a:u64,b:u64,c:u64,d:u64,e:u64)->(i64,u64,u64){
    let r:i64;let extra:u64;let kind:u64;
    unsafe{asm!("int 0x81",inlateout("rax")op=>r,in("rdi")a,in("rsi")b,inlateout("rdx")c=>extra,
        in("r10")d,inlateout("r8")e=>kind,in("r9")0u64,lateout("rcx")_,options(nostack));}(r,extra,kind)
}
fn ctl(op:u64,h:u64)->(i64,u64,u64){call(op,h,0,0,0,0)}
fn end(n:u64)->!{ctl(0x20006,n);loop{core::hint::spin_loop();}}
fn check(ok:bool,n:u64){if !ok{end(n);}}
fn terminal(h:u64,detail:i64,kind:u64){for _ in 0..100000{
    let s=ctl(0x20001,h);if s.0!=0{check(s.0==detail+1&&s.2==kind,511);return;}
    ctl(0x1fffe,0);
}end(512)}
#[unsafe(no_mangle)]
#[unsafe(link_section=".text.entry")]
pub extern "C" fn _start(abi:u64,factory:u64,first:u64,second:u64,stream_factory:u64)->!{
    check(abi==4&&factory==0xa001&&first==0xc001&&second==0xc002&&stream_factory==0xd001,501);
    check(ctl(0x24000,0).0 == -13,502);
    let old=ctl(0x24000,stream_factory);let read=old.0 as u64;let write=old.1;
    check(old.0>0&&ctl(0x24000,stream_factory).0 == -16,503);
    let mut data=[7u8;16];let ptr=data.as_mut_ptr() as u64;
    check(call(0x24001,read,ptr,16,0,0).0 == -11,504);
    check(call(0x24002,write,u64::MAX,16,0,0).0 == -14,505);
    check(call(0x24001,read,ptr,16,0,0).0 == -11,506);
    check(call(0x24002,write,ptr,16,0,0).0==16&&call(0x24002,write,ptr,16,0,0).0==16,507);
    check(call(0x24002,write,ptr,1,0,0).0 == -11,508);
    check(call(0x24001,read,0x800ff8,16,0,0).0 == -14,527);
    check(call(0x24001,read,0x400000,16,0,0).0 == -14,528);
    check(call(0x24001,read,ptr,16,0,0).0==16,529);
    for value in data {check(value==7,530);}
    check(ctl(0x24003,read).0==0&&call(0x24002,write,ptr,1,0,0).0 == -32,509);
    check(ctl(0x24003,write).0==0&&ctl(0x24003,write).0 == -13,510);
    let fresh=ctl(0x24000,stream_factory);let read2=fresh.0 as u64;let write2=fresh.1;
    check(fresh.0>0&&read2!=read&&call(0x24001,read,ptr,1,0,0).0 == -13,513);
    check(call(0x24001,read2,ptr,1,0,0).0 == -11,514);
    let mode: &[u8]=if cfg!(stop_writer){b"stop" as &[u8]}else if cfg!(fault_writer){b"fault"}else{b"normal"};
    let mut a=args(mode);a.argc=5;
    check(call(0x23001,factory,first,0,&a as *const Args as u64,write2).0 == -22,515);
    check(call(0x24002,write2,ptr,0,0,0).0==0,516);
    a.argc=2;
    let producer=call(0x23001,factory,first,0,&a as *const Args as u64,write2).0 as u64;
    check(producer==0xb0000101&&ctl(0x24003,write2).0 == -13,517);
    check(call(0x23001,factory,second,0,&a as *const Args as u64,read2).0 == -16,531);
    let b=args(if cfg!(bad_count){b"short"}else{mode});
    let consumer=call(0x23001,factory,second,1,&b as *const Args as u64,read2).0 as u64;
    check(consumer==0xb0000102&&ctl(0x24003,read2).0 == -13,518);
    if cfg!(stop_writer){
        let mut ready=false;
        for _ in 0..100000{let s=ctl(0x20001,producer);check(s.0==0,519);if s.1==1{ready=true;break;}ctl(0x1fffe,0);}
        check(ready&&ctl(0x20007,producer).0==0,520);
    }
    terminal(producer,if cfg!(stop_writer){143}else if cfg!(fault_writer){134}else{17},if cfg!(stop_writer){3}else if cfg!(fault_writer){2}else{1});
    terminal(consumer,29,1);
    check(ctl(0x20002,producer).0==0&&ctl(0x20002,consumer).0==0,521);
    let third=ctl(0x24000,stream_factory);check(third.0>0,522);
    check(ctl(0x24003,third.0 as u64).0==0,523);
    let c=args(b"broken");
    let child=call(0x23001,factory,first,0,&c as *const Args as u64,third.1).0 as u64;
    check(child==0xb0000201,524);terminal(child,33,1);
    check(ctl(0x20002,child).0==0&&ctl(0x24000,stream_factory).0 == -28,525);
    check(ctl(0x24003,third.1).0 == -13,526);
    end(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo)->!{end(599)}
