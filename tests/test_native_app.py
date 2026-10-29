# SPDX-License-Identifier: BSD-2-Clause
"""Issue99 shared-core and extracted production-body tests; no guest execution.

The lead must review this entry and its child commands before execution. Hardware
mapping and clock sampling are explicit substitutes; admission, ownership,
startup, history, clock validation and binding revocation use production bodies.
"""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import time
import unittest

from test_native_cleanup import block, af09_prelude, compiler_file_limit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_capture import run_capture

# MMU installation, alias flushes, device sampling, scheduler returns and
# notification/trace effects are host substitutes. State has fixed host backing.
# The real selector, byte walker, record snapshot, imagePreflight, stack writer,
# channel syscall and selected lifecycle bodies use original Channel/Execution.
# Dispatch tests extract the two production clauses with a fallback sentinel;
# copy/exec use production pre-effect prefixes, reset uses its scalar prefix,
# closeInit uses its detach/authority loop. Full MMU/scheduler execution is absent.
SCAFFOLD = r'''
const std=@import("std");
const K=@import("kernel");const App=K.App;const C=K.C;const elf=K.elf;
const launch=K.launch;const FsRoles=K.FsRoles;const Sustained=K.Sustained;
const Frame=K.Frame;const Execution=K.E.Execution;const Child=K.E.Child;
const State=struct{
 pages:[128]K.memory.Page=@splat(.{}),backing:[128][4096]u8 align(4096)=@splat(@splat(0)),
 count:usize=0,generation:u64=0,admitted:bool=false,terminal:bool=false,
 root:[1]u64=.{0},execution:Execution=.{},children:[0]Child=.{},
 app_binding:App.Binding=.{},channel_cap:u64=0,channel_reply_cap:u64=0,channel_wait:C.Wait=.{},
 memory_cap:u64=0,entropy_grant:struct{selector:u64=0}=.{},thread_cap:u64=0,
 frozen:bool=false,on_child:bool=false,freeze_sequence:u64=0,revision:u64=0,status:u64=0,terminal_kind:u64=0,
 image_commit:struct{sequence:u64=0,image:u64=0,pending:bool=false}=.{},
 fn context(s:*State)*Execution{return &s.execution;}
 fn childRecords(s:*State)[]Child{return &s.children;}
 fn records(s:*State)*[128]K.memory.Page{return &s.pages;}
 fn payload(s:*State)*align(4096) [128][4096]u8{return &s.backing;}
};
var states:[7]State=@splat(.{});var channels:[12]C.Channel=@splat(.{});
var active:usize=6;var response:i64=99;var published:usize=0;var alias_calls:usize=0;
var samples:usize=0;var sample_value:u64=42;var sample_error:?K.Clock.Error=null;
var effects:usize=0;var reclaimed:usize=0;
var combined_profile=true;var combined_init=true;var combined_owner_stack=true;
var combined_application_profile=false;var connections_profile=true;const sustained=false;
const pipeline_session=true;const pipeline_capacity=false;const session_lifecycle=true;
const program_profile=true;var launch_profile=true;const channel_profile=true;
const io_profile=false;const supervised=true;const init_profile=false;
const service_memory=false;const service_workers=false;const external_backing=false;
var service_image:elf.Image=undefined;var second_image:elf.Image=undefined;var third_image:elf.Image=undefined;
const service_bytes=[_]u8{0};const second_bytes=service_bytes;const third_bytes=service_bytes;
const service_len=1;const second_len=1;const third_len=1;const bootstrap=[_]u8{0}**80;
const serial=struct{fn write(_:[]const u8)void{}};
fn check(ok:bool,comptime marker:[]const u8)void{if(!ok){std.debug.print("{s}\n",.{marker});std.process.exit(91);}}
fn require(ok:bool)void{check(ok,"PRODUCTION_INVARIANT");}
fn backingOwner(s:*const State)usize{for(&states,0..)|*candidate,i|if(candidate==s)return i;unreachable;}
fn supervisorSlot()usize{return 6;}fn workerCount()usize{return 6;}
fn processSlot(slot:usize)bool{return FsRoles.process(slot);}fn threadedSlot(slot:usize)bool{return FsRoles.threaded(slot);}
fn lifetimeLimit()u64{return 15;}fn channelCount()usize{return 12;}
fn result(s:*State,value:i64)void{response=value;s.execution.frame.rax=@bitCast(value);}
fn select()*const Frame{return &states[active].execution.frame;}
fn legacyDispatch(_: *const Frame)*const Frame{result(&states[active],777);return select();}
fn rotate()void{}fn notifyParent(_: *State)void{}
fn publishSustained()void{published+=1;}
fn nativeCleanupTrace(_:usize,_:u8)void{}
fn aliases(_: *State,_:bool)void{alias_calls+=1;}
fn monotonicRead()K.Clock.Error!u64{samples+=1;if(sample_error)|err|return err;return sample_value;}
fn wakeAddress(_: *State,_:usize)usize{return 0;}
fn closeInit()noreturn{@panic("unexpected init close");}
fn channelWaitEnabled()bool{return true;}
fn channelInterrupted(_: *const State)bool{return false;}
fn traceStorageChannelWait(_:usize,_:[]const u8,_:i64)void{}
// MMU substitute: instantiate the already preflighted fixed stack using actual
// Page records. No test-only admission or ownership branch lives here.
fn load(s:*State,_:[]const u8,image:*const elf.Image,_:[]const u8,slot:usize)void{
 require(imagePreflight(s,image));
 for(0..16)|i|s.pages[i]=.{.address=0x08000000+i*4096,.flags=7};
 s.count=16;s.admitted=true;s.memory_cap=0x40000000|(s.generation<<8)|(slot+1);
 @memset(s.backing[14][128..144],0x6d);
}
fn reset()void{
 @memset(std.mem.asBytes(&states),0);channels=@splat(.{});
 active=6;combined_profile=true;combined_init=true;combined_owner_stack=true;combined_application_profile=false;connections_profile=true;launch_profile=true;
 response=99;published=0;alias_calls=0;samples=0;sample_value=42;sample_error=null;effects=0;reclaimed=0;
 service_image=.{.entry=0x200000,.phdr=0x200040,.phnum=1,.count=1,.segments=undefined};
 service_image.segments[0]=.{.flags=5,.address=0x200000,.offset=0,.filesz=1,.memsz=4096};
 second_image=service_image;third_image=service_image;
 for(&channels,0..)|*c,i|c.identity=i;
 for([_]usize{0,1,10,11})|i|_=channels[i].create(6);
 require(channels[10].transfer(6,channels[10].cap(0),0));
 require(channels[11].transfer(6,channels[11].cap(1),0));
 states[0].admitted=true;states[0].generation=1;
 states[0].channel_cap=channels[10].cap(0);states[0].channel_reply_cap=channels[11].cap(1);
 states[6].admitted=true;states[6].count=1;states[6].pages[0]=.{.address=0x1000,.flags=7};
 var raw:[320]u8=@splat(0);@memcpy(raw[0..8],"AENAP001");
 std.mem.writeInt(u64,raw[8..16],320,.little);raw[16]=4;raw[24]=4;
 for(0..8)|i|{raw[32+i*32]=@intCast('a'+i);}
 std.mem.writeInt(u64,raw[288..296],handle(0),.little);
 std.mem.writeInt(u64,raw[296..304],channels[11].cap(0),.little);
 std.mem.writeInt(u64,raw[304..312],channels[10].cap(1),.little);
 @memcpy(states[6].backing[0][0..320],&raw);
 @memset(std.mem.asBytes(&states[1].backing),0xa5);
}
fn launchFrame()Frame{return .{.rax=0x2300a,.rdi=0xa001,.rsi=0xc001,.rdx=1,.r10=0x1000,.r8=channels[0].cap(0),.r9=channels[1].cap(1)};}
fn put(offset:usize,value:u64)void{std.mem.writeInt(u64,states[6].backing[0][offset..][0..8],value,.little);}
fn launchApp()void{const f=launchFrame();_=appLaunchOperation(&f);check(response>0,"POSITIVE_LAUNCH");}
fn deny(f:Frame,expected:i64)void{
 const destination=states[1];const before=channels;const engine=states[0];
 const before_published=published;const before_alias=alias_calls;
 _=appLaunchOperation(&f);
 check(response==expected,"DENIAL_STATUS");
 check(std.meta.eql(destination,states[1]),"DESTINATION_SNAPSHOT");
 check(std.meta.eql(before,channels),"CHANNEL_SNAPSHOT");
 check(std.meta.eql(engine,states[0]),"ENGINE_SNAPSHOT");
 check(published==before_published and alias_calls==before_alias,"PREFLIGHT_NO_EFFECTS");
}
fn readStackWord(s:*State,address:usize)u64{
 var raw:[8]u8=undefined;for(&raw,0..)|*v,i|v.*=byte(s,address+i,false).?.*;
 return std.mem.readInt(u64,&raw,.little);
}
fn transfer(owner:usize,index:usize,reading:bool,count:u64)i64{
 active=owner;
 if(states[owner].count==0){states[owner].count=1;states[owner].pages[0]=.{.address=0x1000,.flags=7};}
 const f=Frame{.rax=if(reading)0x24001 else 0x24002,.rdi=channels[index].cap(if(reading)0 else 1),.rsi=0x1400,.rdx=count};
 _=channelOperation(&f);return response;
}
'''

CASES = r'''
fn positive()void{
 reset();for(0..32)|i|_=channels[11].stream.push(@intCast(i));
 channels[11].write_started=true;const greeting=channels[11].stream;const f=launchFrame();
 _=appLaunchOperation(&f);check(response==@as(i64,@intCast(handle(1))),"POSITIVE_HANDLE");
 check(states[1].generation==1 and states[1].admitted,"ONE_GENERATION");
 check(channels[0].owners[0]==1 and channels[0].owners[1]==6 and channels[1].owners[1]==1 and channels[1].owners[0]==6,"PROCESS_HOLDERS");
 check(channels[11].owners[0]==1 and channels[11].owners[1]==0 and channels[10].owners[1]==1 and channels[10].owners[0]==0,"NAMESPACE_HOLDERS");
 check(std.meta.eql(greeting,channels[11].stream),"GREETING_BYTES");
 check(states[1].app_binding.epoch==states[0].channel_cap,"FULL_ENGINE_CAP_EPOCH");
 check(states[1].app_binding.clock==0x3600000100000001,"DISTINCT_CLOCK_IDENTITY");
 check(readStackWord(&states[1],App.startup_address+40)==states[0].channel_cap,"STARTUP_EPOCH");
 check(alias_calls==7 and published==1,"COMMIT_COMPLETE");
 deny(f,-16);
}
fn denials()void{
 reset();var f=launchFrame();f.rdi=0;deny(f,-13);
 reset();f=launchFrame();f.rsi=0xc004;deny(f,-13);
 reset();f=launchFrame();f.rdx=6;deny(f,-22);
 reset();f=launchFrame();f.rdx=0;deny(f,-22);
 reset();f=launchFrame();f.rdx=std.math.maxInt(u64);deny(f,-22);
 reset();active=5;deny(launchFrame(),-13);
 reset();combined_init=false;deny(launchFrame(),-38);
 reset();combined_profile=false;deny(launchFrame(),-38);
 reset();combined_owner_stack=false;deny(launchFrame(),-38);
 reset();combined_application_profile=true;deny(launchFrame(),-38);
 reset();connections_profile=false;deny(launchFrame(),-38);
 reset();launch_profile=false;deny(launchFrame(),-38);
 reset();states[1].admitted=true;deny(launchFrame(),-16);
 reset();states[1].generation=15;deny(launchFrame(),-28);
 for(0..320)|readable|{reset();f=launchFrame();f.r10=0x2000-readable;deny(f,-14);}
 reset();f=launchFrame();f.r10=std.math.maxInt(u64)-100;deny(f,-14);
 for([_]usize{0,8,16,24,312})|offset|{reset();put(offset,255);deny(launchFrame(),-22);}
 reset();@memset(states[6].backing[0][32..64],'x');deny(launchFrame(),-22);
 for([_]usize{288,296,304})|offset|{reset();put(offset,0);deny(launchFrame(),-13);}
 reset();put(288,handle(0)-0x100);deny(launchFrame(),-13);
 reset();states[0].terminal=true;deny(launchFrame(),-13);
 reset();states[0].admitted=false;deny(launchFrame(),-13);
 reset();states[2].admitted=true;states[2].generation=1;put(288,handle(2));deny(launchFrame(),-13);
 reset();states[0].channel_cap=channels[11].cap(0);deny(launchFrame(),-13);
 reset();states[0].channel_reply_cap=channels[10].cap(1);deny(launchFrame(),-13);
 for([_]usize{10,11})|index|{
  reset();channels[index].owners[if(index==10)0 else 1]=5;deny(launchFrame(),-13);
  reset();channels[index].generation+=1;deny(launchFrame(),-13);
 }
 for([_]usize{0,1,10,11})|index|{
  reset();channels[index].stream.sealed=true;deny(launchFrame(),-13);
  reset();channels[index].stream.reader_closed=true;deny(launchFrame(),-13);
  reset();channels[index].owners[if(index==0 or index==11)0 else 1]=5;deny(launchFrame(),-13);
 }
 reset();f=launchFrame();f.r9=channels[0].cap(1);deny(f,-13);
 reset();f=launchFrame();f.r8=channels[0].cap(1);deny(f,-13);
 reset();f=launchFrame();f.r9=channels[1].cap(0);deny(f,-13);
 reset();put(296,channels[10].cap(1));put(304,channels[11].cap(0));deny(launchFrame(),-13);
 reset();_=channels[0].stream.push(1);deny(launchFrame(),-13);
 reset();_=channels[1].stream.push(1);deny(launchFrame(),-13);
 reset();service_image.segments[0].memsz=113*4096;deny(launchFrame(),-12);
 reset();service_image.segments[0].address=0x08000000;deny(launchFrame(),-12);
 reset();service_image.segments[0].memsz=0x04000000;deny(launchFrame(),-12);
 reset();service_image.count=16;
 for(service_image.segments[0..16],0..)|*segment,i|segment.*=.{.flags=5,.address=(i+1)*0x400000-4096,.offset=0,.filesz=1,.memsz=8192};
 deny(launchFrame(),-12); //48 pages fit;33 leaf directories do not.
}
fn history()void{
 reset();check(transfer(6,11,true,0)==0 and !channels[11].read_started,"ZERO_NO_HISTORY");
 check(transfer(6,11,true,16)==-11 and !channels[11].read_started,"EAGAIN_NO_HISTORY");
 check(transfer(0,11,false,16)==16 and transfer(0,11,false,16)==16,"ENGINE_GREETING");
 check(channels[11].write_started and !channels[11].read_started,"GREETING_HISTORY_ALLOWED");
 active=6;launchApp();
 reset();for(0..32)|_|_=channels[11].stream.push(9);
 check(transfer(6,11,true,16)==16 and transfer(6,11,true,16)==16,"READ_PROGRESS");
 check(channels[11].stream.count==0 and channels[11].stream.head==0,"READ_WRAPPED");
 check(channels[11].read_started,"READ_HISTORY");active=6;deny(launchFrame(),-13);
 reset();check(transfer(6,10,false,16)==16,"REQUEST_PROGRESS");
 check(transfer(0,10,true,16)==16,"REQUEST_DRAIN");
 check(channels[10].write_started,"WRITE_HISTORY");active=6;deny(launchFrame(),-13);
 reset();check(transfer(6,10,false,0)==0 and !channels[10].write_started,"ZERO_WRITE_NO_HISTORY");
 for(0..32)|_|_=channels[10].stream.push(1);
 check(transfer(6,10,false,1)==-11 and !channels[10].write_started,"FULL_NO_HISTORY");
}
fn clockCase()void{
 reset();launchApp();active=1;const token=states[1].app_binding.clock;
 for([_]u64{0,token^1,token^(@as(u64,1)<<32),0x3300000100000001})|bad|{
  _=appClockOperation(&.{.rdi=bad});check(response==-13 and samples==0,"CLOCK_DENIED_NO_SAMPLE");
 }
 active=2;_=appClockOperation(&.{.rdi=token});check(response==-13 and samples==0,"FOREIGN_NO_SAMPLE");active=1;
 combined_init=false;_=appClockOperation(&.{.rdi=token});check(response==-38 and samples==0,"DISABLED_PROFILE_NO_SAMPLE");combined_init=true;
 for(0..5)|i|{
  var f=Frame{.rdi=token};switch(i){0=>f.rsi=1,1=>f.rdx=1,2=>f.r10=1,3=>f.r8=1,4=>f.r9=1,else=>unreachable,}
  _=appClockOperation(&f);check(response==-22 and samples==0,"CLOCK_OPERANDS_NO_SAMPLE");
 }
 states[1].terminal=true;_=appClockOperation(&.{.rdi=token});check(response==-13 and samples==0,"DEAD_NO_SAMPLE");states[1].terminal=false;
 states[1].admitted=false;_=appClockOperation(&.{.rdi=token});check(response==-13 and samples==0,"UNADMITTED_NO_SAMPLE");states[1].admitted=true;
 const binding=states[1].app_binding;_=appClockOperation(&.{.rdi=token});check(response==42 and samples==1 and std.meta.eql(binding,states[1].app_binding),"READ_ONLY_CLOCK");
 sample_value=std.math.maxInt(i64);_=appClockOperation(&.{.rdi=token});check(response==std.math.maxInt(i64),"CLOCK_SIGNED_MAX");
 sample_value=@as(u64,std.math.maxInt(i64))+1;_=appClockOperation(&.{.rdi=token});check(response==-75,"CLOCK_SIGNED_OVERFLOW");
 for([_]K.Clock.Error{error.Unavailable,error.Regression,error.Overflow},[_]i64{-38,-5,-75})|err,code|{sample_error=err;_=appClockOperation(&.{.rdi=token});check(response==code,"REAL_CLOCK_ERROR");}
}
fn revocation()void{
 reset();launchApp();const token=states[1].app_binding.clock;
 stopContexts(&states[1]);check(!states[1].app_binding.bound(),"STOP_REVOKES_BINDING");
 active=1;_=appClockOperation(&.{.rdi=token});check(response==-13 and samples==0,"STOP_REVOKES_QUERY");
 for([_]u64{1,2})|kind|{reset();launchApp();active=1;_=finishEntry(17,kind);check(states[1].terminal and !states[1].app_binding.bound(),"TERMINAL_FAULT_REVOKES");}
 reset();launchApp();active=6;_=stopEntry(&.{.rax=0x20007});check(states[1].terminal and !states[1].app_binding.bound(),"FORCED_STOP_REVOKES");
 reset();launchApp();states[1].terminal=true;_=reclaimEntry();check(!states[1].admitted and !states[1].app_binding.bound() and states[1].generation==1,"RECLAIM_REVOKES");
 reset();launchApp();resetState(&states[1]);check(!states[1].app_binding.bound(),"RESET_REVOKES");
 reset();launchApp();closeEntry();check(!states[1].app_binding.bound() and !states[1].admitted,"CLOSE_INIT_REVOKES");
 reset();launchApp();active=6;_=stopEntry(&.{.rax=0x20007});_=reclaimEntry();
 // Replace the closed endpoints in their new generations before re-admission.
 for([_]usize{0,1,10,11})|i|{channels[i].closeOwner(6);channels[i].closeOwner(0);_=channels[i].create(6);}
 require(channels[10].transfer(6,channels[10].cap(0),0));require(channels[11].transfer(6,channels[11].cap(1),0));
 states[0].channel_cap=channels[10].cap(0);states[0].channel_reply_cap=channels[11].cap(1);
 put(296,channels[11].cap(0));put(304,channels[10].cap(1));launchApp();
 check(states[1].generation==2 and states[1].app_binding.clock!=token,"NONREUSED_LIFETIME");
 active=1;_=appClockOperation(&.{.rdi=token});check(response==-13 and samples==0,"REPLACED_TOKEN_DENIED");
}
fn mutation()void{
 reset();launchApp();active=1;const before=states[1];const endpoints=channels;const child_before=states[2];
 _=freezeOperation(&.{.rax=0x23003});check(response==-95 and states[1].freeze_sequence==before.freeze_sequence and !states[1].frozen,"BOUND_FREEZE_NO_EFFECT");
 active=6;_=copyPrefix(&.{.rax=0x23006,.rdi=0xa001,.rsi=handle(1),.rdx=2});
 check(response==-95 and effects==0 and !states[2].admitted,"BOUND_COPY_NO_EFFECT");
 for([_]u64{0x23007,0x23009})|op|{_=execPrefix(&.{.rax=op,.rdi=0xa001,.rsi=handle(1)});check(response==-95 and effects==0,"BOUND_EXEC_PUBLICATION_NO_EFFECT");}
 check(std.meta.eql(endpoints,channels) and states[1].generation==before.generation,"BOUND_METADATA_UNCHANGED");
 var observed=states[1];observed.execution.frame.rax=before.execution.frame.rax;
 check(std.meta.eql(before,observed) and std.meta.eql(child_before,states[2]),"BOUND_FULL_SNAPSHOT");
 _=execPrefix(&.{.rax=0x23008,.rdi=0xa001,.rsi=handle(1)});check(response==77 and effects==1,"RECEIPT_ALLOWED");
 states[1].app_binding=.{};active=1;_=freezeOperation(&.{.rax=0x23003});check(response==-11 and states[1].frozen,"UNBOUND_FREEZE");
 active=6;_=copyPrefix(&.{.rax=0x23006,.rdi=0xa001,.rsi=handle(1),.rdx=2,.r10=1});check(response==77,"UNBOUND_COPY_PREFIX");
 _=execPrefix(&.{.rax=0x23007,.rdi=0xa001,.rsi=handle(1)});check(response==77,"UNBOUND_EXEC_PREFIX");
}
fn disabledClockCase()void{
 reset();launchApp();active=1;_=appClockOperation(&.{.rdi=states[1].app_binding.clock});
 check(response==-38 and samples==0,"DISABLED_SOURCE_NO_SAMPLE");
}
fn lifetimeProfileCase()void{
 reset();deny(launchFrame(),-38);
 states[1].app_binding=App.Binding.init(1,1,7,8,9).?;states[1].generation=1;states[1].admitted=true;active=1;
 _=appClockOperation(&.{.rdi=states[1].app_binding.clock});check(response==-38 and samples==0,"LIFETIME_PROFILE_DENIED");
}
fn dispatchCase()void{
 reset();const f=launchFrame();_=appDispatch(&f);check(response>0 and states[1].app_binding.bound(),"DISPATCH_LAUNCH");
 active=1;_=appDispatch(&.{.rax=0x28012,.rdi=states[1].app_binding.clock});check(response==42 and samples==1,"DISPATCH_CLOCK");
 _=appDispatch(&.{.rax=0x28012,.rdi=states[1].app_binding.clock^1});check(response==-13 and samples==1,"DISPATCH_CLOCK_DENIAL");
 _=appDispatch(&.{.rax=0x28013});check(response==777,"DISPATCH_FALLTHROUGH");
}
fn stackCase()void{
 reset();launchApp();const s=&states[1];
 const base:usize=0x0800c000;const strings:usize=0x0800e100;
 const expected=[_]u64{4,strings,strings+32,strings+64,strings+96,0,strings+128,strings+160,strings+192,strings+224,0,
 3,0x200040,4,56,5,1,6,4096,9,0x200000,11,1000,12,1000,13,1000,14,1000,23,0,25,0x0800e080,31,strings,
 0xa000,s.memory_cap,0xa001,s.channel_cap,0xa002,s.channel_reply_cap,0xa003,App.startup_address,0,0};
 check(expected.len==45,"MAXIMUM_STACK_WORDS");for(expected,0..)|v,i|check(readStackWord(s,base+i*8)==v,"EXACT_STACK_WORDS");
 const startup=s.app_binding.startup();for(startup,0..)|v,i|check(byte(s,App.startup_address+i,false).?.*==v,"EXACT_STARTUP_BYTES");
 for(0..16)|i|check(byte(s,0x0800e080+i,false).?.*==0x6d,"ENTROPY_PRESERVED");
 for(0..8)|i|check(byte(s,strings+i*32,false).?.*=='a'+i,"ARG_BANK_PRESERVED");
 // The unchanged272 record and old launch body omit the new tag and bytes.
 reset();var legacy:[272]u8=undefined;@memcpy(&legacy,states[6].backing[0][16..288]);
 @memcpy(states[6].backing[0][0..272],&legacy);var f=launchFrame();f.rax=0x23002;_=launchOperation(&f);
 check(response>0 and !states[1].app_binding.bound(),"LEGACY_LAUNCH");
 for(expected[0..41],0..)|v,i|check(readStackWord(&states[1],base+i*8)==v,"LEGACY_STACK_PREFIX");
 check(readStackWord(&states[1],base+41*8)==0 and readStackWord(&states[1],base+42*8)==0,"LEGACY_NO_NEW_TAG");
 for(0..64)|i|check(byte(&states[1],App.startup_address+i,false).?.*==0,"LEGACY_NO_RECORD");
}
pub fn main(init:std.process.Init.Minimal)void{
 const args=init.args.vector;if(args.len!=2)std.process.exit(64);
 const name=std.mem.span(args[1]);
 if(std.mem.eql(u8,name,"positive"))positive() else if(std.mem.eql(u8,name,"denials"))denials()
 else if(std.mem.eql(u8,name,"history"))history() else if(std.mem.eql(u8,name,"clock"))clockCase()
 else if(std.mem.eql(u8,name,"revocation"))revocation() else if(std.mem.eql(u8,name,"mutation"))mutation()
 else if(std.mem.eql(u8,name,"stack"))stackCase()
 else if(std.mem.eql(u8,name,"clock-disabled"))disabledClockCase()
 else if(std.mem.eql(u8,name,"lifetime-profile"))lifetimeProfileCase()
 else if(std.mem.eql(u8,name,"dispatch"))dispatchCase() else std.process.exit(64);
 std.debug.print("NATIVE APP {s} PASS\n",.{name});
}
'''


class NativeApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deadline = time.monotonic() + 300
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-native-app-host-')
        cls.out = Path(cls.temporary.name)
        cls.binaries = {}
        cls.inputs = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (
            ROOT/'kernel/arch/x86_64/native_c.zig', ROOT/'kernel/native_app.zig',
            ROOT/'kernel/native_channel.zig', ROOT/'kernel/native_sustained.zig',
            ROOT/'kernel/native_launch.zig', ROOT/'kernel/native_elf.zig')}
        cls.addClassCleanup(cls.finalize)
        cls.addClassCleanup(cls.temporary.cleanup)
        compiler_file_limit(cls)

    @classmethod
    def finalize(cls):
        for path, digest in cls.inputs.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise AssertionError('native-app source changed: '+str(path))
        if time.monotonic() > cls.deadline:
            raise AssertionError('native-app focused300-second bound expired')

    def capture(self, command, seconds):
        remaining = self.deadline - time.monotonic()
        self.assertGreater(remaining, 0, 'native-app focused300-second bound')
        result = run_capture([str(x) for x in command], cwd=ROOT,
                             timeout=min(seconds, remaining), limit=4*1024*1024)
        for path in self.out.rglob('*'):
            if path.is_file():
                self.assertLessEqual(path.stat().st_size, 16*1024*1024,
                                     'native-app compiler file16MiB bound: '+str(path))
        if result.returncode:
            # Compact failure history, including expected semantic omissions;
            # generated sources/binaries/caches remain disposable.
            history = ROOT/'zig-out/native-app-host-failures'
            history.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='w', prefix='attempt-', suffix='.json',
                                             dir=history, delete=False) as receipt:
                json.dump({'command': [str(x) for x in command], 'exit': result.returncode,
                           'stdout_tail': result.stdout[-8192:], 'stderr_tail': result.stderr[-8192:],
                           'inputs': {str(k): v for k, v in self.inputs.items()}}, receipt, indent=2)
        return result

    def actual_source(self, omission=None):
        native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        names = ('ordinaryAppEnabled', 'appLaunchOperation', 'appClockOperation', 'launchOperation', 'launchStack',
                 'imagePreflight', 'byte', 'copy', 'word', 'channelBuffer', 'ownedChannel',
                 'channelOperation', 'closeChannels', 'handle', 'lookup', 'clearTid',
                 'stopContexts', 'freezeOperation')
        bodies = '\n'.join(block(native, 'fn '+name+'(') for name in names)
        bodies = block(native, 'const ChannelBuffer = struct')+';\n'+bodies
        dispatch = block(native, 'pub fn exception(')
        branches = []
        for op, name in (('0x2300a', 'appLaunchOperation'), ('0x28012', 'appClockOperation')):
            selected = [line for line in dispatch.splitlines() if 'frame.rax == '+op in line]
            self.assertEqual(len(selected), 1, 'actual dispatch branch '+op)
            self.assertIn('return '+name+'(frame);', selected[0])
            branches.append(selected[0])
        bodies += '\nfn appDispatch(frame:*const Frame)*const Frame{\n'+'\n'.join(branches)+'\nreturn legacyDispatch(frame);\n}\n'
        reset = block(native, 'fn resetState(')
        # Hardware backing rebinding is replaced with inline host-owned arrays.
        bodies += '\n'+reset[:reset.index('    if (external_backing)')]+'}\n'
        finish = block(native, 'fn finish(')
        bodies += '\n'+finish[:finish.index('    if (!states[1 - active].terminal)')].replace(
            'fn finish(', 'fn finishEntry(', 1)+'    return select();\n}\n'
        for op, name in (('0x20007', 'stopEntry'), ('0x20002', 'reclaimEntry')):
            branch = block(native, '        '+op+' => {')
            parameter = 'frame:*const Frame' if name == 'stopEntry' else ''
            switch = 'frame.rax' if name == 'stopEntry' else '@as(u64,0x20002)'
            bodies += '\nfn '+name+'('+parameter+')*const Frame{const slot:usize=1;const s=&states[slot];const caller=&states[6];switch('+switch+'){'+branch+',else=>unreachable,}return select();}\n'
        close = block(native, 'fn closeInit(')
        close_loop = block(close, '    for (&states, 0..) |*s, i|')
        bodies += '\nfn closeEntry()void{'+close_loop+'}\n'
        # Execute every effect-free production guard with a sentinel at the
        # first image/copy preparation. Existing full-body suites retain old
        # unbound copy/exec success, rollback, mapping and publication coverage.
        for name, anchor in (('copy', '    const reader = ownedChannel'),
                             ('exec', '    if (f.rax == 0x23008)')):
            body = block(native, 'fn '+name+'Operation(')
            prefix = body[:body.index(anchor)].replace('fn '+name+'Operation(', 'fn '+name+'Prefix(', 1)
            bodies += '\n'+prefix+'effects+=1;result(caller,77);return select();}\n'
        if omission == 'history':
            old = 'if (reading) selected.read_started = true else selected.write_started = true;'
            self.assertEqual(bodies.count(old), 1)
            bodies = bodies.replace(old, 'if (reading) selected.read_started = false else selected.write_started = true;')
        if omission == 'revocation':
            stop = block(bodies, 'fn stopContexts(')
            self.assertEqual(stop.count('s.app_binding = .{};'), 1)
            bodies = bodies.replace(stop, stop.replace('s.app_binding = .{};', ''))
        if omission == 'profile':
            selector = block(bodies, 'fn ordinaryAppEnabled(')
            self.assertEqual(selector.count(' and !combined_application_profile'), 1)
            bodies = bodies.replace(selector, selector.replace(' and !combined_application_profile', ''))
        if omission == 'dispatch':
            dispatch = block(bodies, 'fn appDispatch(')
            bodies = bodies.replace(dispatch, dispatch.replace('return appLaunchOperation(frame);', 'return legacyDispatch(frame);'))
        prelude = af09_prelude(native).replace('@import("af09")', 'K.Af09')
        text = SCAFFOLD + prelude + bodies + CASES
        for old, new in (('@import("../../native_channel.zig")', 'C'),
                         ('@import("../../native_clock.zig")', 'K.Clock')):
            text = text.replace(old, new)
        return text

    def test_actual_launch_four_endpoint_handoff_and_queued_greeting(self):
        self.run_case('positive')

    def test_actual_launch_denials_snapshot_all_destination_and_channel_bytes(self):
        self.run_case('denials')

    def test_actual_channel_progress_history_wrap_and_no_progress(self):
        self.run_case('history')

    def test_actual_clock_holder_type_lifetime_operands_and_source_errors(self):
        self.run_case('clock')

    def test_actual_clock_disabled_and_tick_diagnostic_do_not_sample(self):
        for selection in ('source-disabled', 'tick-diagnostic'):
            with self.subTest(selection=selection):
                binary = self.build('Debug', selection)
                result = self.capture([binary, 'clock-disabled'], 10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('NATIVE APP clock-disabled PASS', result.stderr)

    def test_actual_storage_lifetime_profile_is_not_selected(self):
        binary = self.build('Debug', 'lifetime-profile')
        result = self.capture([binary, 'lifetime-profile'], 10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('NATIVE APP lifetime-profile PASS', result.stderr)

    def test_actual_new_operation_dispatch_connections(self):
        self.run_case('dispatch')

    def test_compiling_profile_omission_is_detected(self):
        self.run_case('denials', 'profile')

    def test_compiling_dispatch_omission_is_detected(self):
        self.run_case('dispatch', 'dispatch')

    def test_actual_stop_reset_reclaim_close_revoke_binding(self):
        self.run_case('revocation')

    def test_actual_bound_freeze_copy_exec_and_publication_have_no_effects(self):
        self.run_case('mutation')

    def test_actual_stack_max_arguments_exact_record_and_legacy_bytes(self):
        self.run_case('stack')

    def test_compiling_counterpart_omission_is_detected(self):
        self.run_case('denials', 'counterpart')

    def test_compiling_history_omission_is_detected(self):
        self.run_case('history', 'history')

    def test_compiling_revocation_omission_is_detected(self):
        self.run_case('revocation', 'revocation')

    def run_case(self, case, omission=None):
        modes = ('Debug',) if omission else ('Debug', 'ReleaseSafe')
        for mode in modes:
            with self.subTest(mode=mode, omission=omission):
                key = (mode, omission)
                if key not in self.binaries:
                    self.binaries[key] = self.build(mode, omission)
                result = self.capture([self.binaries[key], case], 10)
                if omission:
                    marker = {'counterpart': 'DENIAL_STATUS', 'history': 'READ_HISTORY',
                              'revocation': 'STOP_REVOKES_BINDING', 'profile': 'DENIAL_STATUS',
                              'dispatch': 'DISPATCH_LAUNCH'}[omission]
                    self.assertEqual(result.returncode, 91, result.stderr)
                    self.assertIn(marker, result.stderr)
                else:
                    self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                    self.assertIn('NATIVE APP '+case+' PASS', result.stderr)

    def build(self, mode, omission):
        label = mode+'-'+(omission or 'actual')
        source = self.out/(label+'.zig')
        source.write_text(self.actual_source(omission))
        options = self.out/'options.zig'
        values = dict(native_memory=True,native_clock=True,native_clock_ticks=False,
                      native_service_lifetime=False,
                      native_signal_suspend=False,native_signal_actions=False,
                      native_service_channel_wait=False,native_skip_zero=False,
                      native_process_exec=True,native_exec_copy=False,
                      native_copy_signals=False,native_freeze_skip_park=False,
                      native_freeze_ignore_token=False,native_exec_token=False)
        if omission == 'source-disabled':
            values['native_clock'] = False
        if omission == 'tick-diagnostic':
            values['native_clock_ticks'] = True
        if omission == 'lifetime-profile':
            values['native_service_lifetime'] = True
        options.write_text('\n'.join('pub const '+name+'='+str(value).lower()+';'
                                     for name,value in values.items()))
        binary = self.out/label
        with tempfile.NamedTemporaryFile(mode='w', prefix='.app-host-imports-', suffix='.zig',
                                         dir=ROOT/'kernel') as facade:
            # The optional core copy is a single semantic omission over the
            # original implementation, kept in the same package import root.
            with tempfile.NamedTemporaryFile(mode='w', prefix='.app-host-core-', suffix='.zig',
                                             dir=ROOT/'kernel') as core:
                selected = 'native_app.zig'
                if omission == 'counterpart':
                    text = (ROOT/'kernel/native_app.zig').read_text()
                    old = 'if (nr.lookup(engine.slot, engine.reply) != 1 or nw.lookup(engine.slot, engine.request) != 0) return null;'
                    self.assertEqual(text.count(old), 1)
                    core.write(text.replace(old, 'if (engine.request == 0 or engine.reply == 0) return null;'))
                    core.flush()
                    selected = Path(core.name).name
                facade.write('pub const App=@import("'+selected+'");'+
                             'pub const C=@import("native_channel.zig");pub const launch=@import("native_launch.zig");'+
                             'pub const elf=@import("native_elf.zig");pub const memory=@import("native_memory.zig");'+
                             'pub const E=@import("arch/x86_64/native_execution.zig");'+
                             'pub const Frame=@import("arch/x86_64/context.zig").Frame;'+
                             'pub const FsRoles=@import("arch/x86_64/native_fs_roles.zig");'+
                             'pub const Sustained=@import("native_sustained.zig");'+
                             'pub const Clock=@import("native_clock.zig");pub const Af09=@import("native_af09_drain.zig");')
                facade.flush()
                result = self.capture(['zig','build-exe','-O'+mode,'-fstrip',
                                       '--cache-dir',self.out/'cache','--global-cache-dir',self.out/'global',
                                       '--dep','kernel','--dep','build_options','-Mroot='+str(source),
                                       '-Mkernel='+facade.name,'-Mbuild_options='+str(options),
                                       '-femit-bin='+str(binary)], 60)
                # Compilation must succeed before an omission is meaningful.
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        return binary
