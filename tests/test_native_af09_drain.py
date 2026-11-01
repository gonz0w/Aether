# SPDX-License-Identifier: BSD-2-Clause
"""Execute AF09 hooks and actual native syscall/scheduler bodies on host storage.

No IRQ, CR3, guest timing or native qualification is implied by this harness.
"""
from pathlib import Path
import sys
import time
import tempfile
import unittest
from test_native_cleanup import block, compiler_file_limit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"sys-init/scripts"))
from bounded_capture import run_capture
SCAFFOLD = r'''
const std = @import("std");
const K = @import("kernel");
const C = K.C;
const Sustained = K.Sustained;
const FsRoles = K.FsRoles;
const E = K.E;
const Frame = K.Frame;
const Execution = E.Execution;
const Child = E.Child;
const Page = struct {address:usize=0,flags:u64=0};
const State = struct {
 app_binding:struct{clock:u64=0}=.{},
 generation:u64=1, admitted:bool=false,terminal:bool=false,terminal_kind:u64=0,status:u64=0,ready:bool=false,revision:u64=0,yields:usize=0,
 frozen:bool=false,on_child:bool=false,selected_child:usize=0,execution:Execution=.{},children:[1]Child=@splat(.{}),
 channel_cap:u64=0,channel_reply_cap:u64=0,channel_wait:C.Wait=.{},
 pages:[2]Page=.{.{.address=0x1000,.flags=7},.{.address=0x2000,.flags=7}},count:usize=2,backing:[2][4096]u8 align(4096)=@splat(@splat(0)),
 root:[1]u64=.{1},memory_cap:u64=0,entropy_grant:struct{selector:u64=0}=.{},
 output:[256]u8=@splat(0),output_count:usize=0,
 fn payload(s:*State)*align(4096) [2][4096]u8{return &s.backing;}
 fn records(s:*State)*[2]Page{return &s.pages;}
 fn context(s:*State)*Execution{return if(s.on_child)&s.children[s.selected_child].execution else &s.execution;}
 fn childRecords(s:*State)[]Child{return &s.children;}
 fn contexts(s:*State)[2]*Execution{return .{&s.execution,&s.children[0].execution};}
};
var states:[7]State=@splat(.{});
var channels:[12]C.Channel=@splat(.{});
var active:usize=6;var idle=false;var idle_ticks:usize=0;var total_ticks:usize=0;var sustained_events:Sustained.Events=.{};
var console_closed=true;var block_closed=true;var reclaimed:usize=0;
const supervised=true;const session_lifecycle=true;const combined_profile=true;const sustained=false;const pipeline_session=true;
const native_tick_limit:usize=6000;const io_profile=false;const channel_profile=true;
const mktemp_reader=false; // AF09 keeps its legacy256-byte output capture.
var capture:[32768]u8=undefined;var captured:usize=0;
const serial=struct {
 fn write(text:[]const u8)void{if(text.len>capture.len-captured)@panic("CAPTURE");@memcpy(capture[captured..][0..text.len],text);captured+=text.len;}
 fn inputReady()bool{return false;}
 fn out(_:u16,_:u8)void{}
 fn halt()noreturn{@panic("HALT");}
};
fn require(ok:bool)void{if(!ok)@panic("INVARIANT");}
fn contextView(list:*const [2]*Execution)[]const *Execution{return list;}
fn supervisorSlot()usize{return 6;}
fn channelCount()usize{return channels.len;}
fn storageLifetime()bool{return false;}
fn lifecycleEnabled()bool{return true;}
fn ownerEventsEnabled()bool{return true;}
fn workerCount()usize{return 6;}
fn lifetimeLimit()u64{return 15;}
fn channelInterrupted(_: *const State)bool{return false;}
fn storagePrimaryWaiting(s:*const State)bool{return s.channel_wait.endpoint!=0;}
fn channelWaitEnabled()bool{return true;}
fn refreshWait()void{}
fn stopContexts(s:*State)void{s.execution.wait=.{};s.channel_wait=.{};for(&s.children)|*c|c.reset();}
fn notifyParent(_: *State)void{}
fn aliases(s:*State,writable:bool)void{tryCheck(s.root[0]==0 and writable,"RECLAIM_ALIAS");}
fn nativeCleanupTrace(_:usize,_:u8)void{}
fn refreshChannelWaits()void{}
fn resumeSuspended(_: *State)void{}
fn traceStorageChannelWait(_:usize,_:[]const u8,_:i64)void{}
fn result(s:*State,value:i64)void{s.context().frame.rax=@bitCast(value);}
fn reset()void{
 states=@splat(.{});channels=@splat(.{});active=6;idle=false;reclaimed=0;idle_ticks=0;total_ticks=10;sustained_events=.{};af09=.{};captured=0;
 for(&channels,0..) |*c,i|{c.identity=i;_=c.createSession(6);}
 for([_]usize{0,1,2,6}) |i|{states[i].admitted=i!=2;states[i].execution.fs=100+i;@memset(&states[i].execution.fp,@intCast(i+40));states[i].execution.frame.rip=200+i;}
 for([_]usize{2,1,0},0..) |slot,i|{
  const req=&channels[2*i];const reply=&channels[2*i+1];
  if(slot==0){require(req.transfer(6,req.cap(0),slot));require(reply.transfer(6,reply.cap(1),slot));states[slot].channel_cap=req.cap(0);states[slot].channel_reply_cap=reply.cap(1);}
  else {if(slot!=2){require(req.transfer(6,req.cap(1),slot));require(reply.transfer(6,reply.cap(0),slot));}states[slot].channel_cap=reply.cap(0);states[slot].channel_reply_cap=req.cap(1);}
 }
 af09EngineAdmitted();_=copyPublication();
}
fn transfer(slot:usize,index:usize,reading:bool,bytes:[]const u8,length:usize)i64{
 active=slot;states[slot].on_child=false;
 if(!reading)@memcpy(states[slot].backing[0][0..bytes.len],bytes);
 const f=Frame{.rax=if(reading)0x24001 else 0x24002,.rdi=channels[index].cap(if(reading)0 else 1),.rsi=0x1000,.rdx=length};
 _=channelOperation(&f);return @bitCast(states[slot].execution.frame.rax);
}
fn startupBytes()void{
 const bytes=[_]u8{0}**16;
 for(0..19) |_|{_=transfer(6,1,false,&bytes,16);_=transfer(2,1,true,&bytes,16);}
}
fn readyWireSend()void{const bytes=[_]u8{0}**16;for(0..2) |_|{_=transfer(2,0,false,&bytes,16);}}
fn readyWireReceive()void{const bytes=[_]u8{0}**16;for(0..2) |_|{_=transfer(6,0,true,&bytes,16);}}
fn parentDisposition()void{const bytes=[_]u8{0}**16;
 for(0..2) |_|{_=transfer(6,3,false,&bytes,16);_=transfer(1,3,true,&bytes,16);}
}
fn startup()void{startupBytes();readyWireSend();readyWireReceive();parentDisposition();}
fn ready()void{active=2;const f=Frame{.rax=0x20004};_=readyEntry(&f);}
fn query()void{active=6;const f=Frame{.rax=0x20001,.rdi=handle(1)};_=queryEntry(&f);}
fn parentExit()void{states[1].terminal=true;states[1].terminal_kind=1;states[1].status=0;for(&channels)|*c|c.closeOwner(1);af09Row(7,1,0,0,0);}
fn late()void{
 var bytes:[32]u8=@splat(0);
 if(af09_mode==.stream){std.mem.writeInt(u32,bytes[0..4],2,.little);std.mem.writeInt(u32,bytes[4..8],7,.little);std.mem.writeInt(u32,bytes[8..12],4,.little);std.mem.writeInt(u32,bytes[12..16],16,.little);@memcpy(bytes[16..32],"AF09-HOME-WRITE\n");}
 else if(af09_mode==.exec_prefix or af09_mode==.fork_prefix){@memcpy(bytes[0..8],if(af09_mode==.exec_prefix)"AEEXEC02" else "AEFORK02");std.mem.writeInt(u32,bytes[8..12],1,.little);std.mem.writeInt(u32,bytes[12..16],if(af09_mode==.exec_prefix)608 else 304,.little);@memcpy(bytes[16..24],"AEFSH001");std.mem.writeInt(u32,bytes[24..28],29,.little);std.mem.writeInt(u32,bytes[28..32],7,.little);}
 else {@memcpy(bytes[0..8],"AEFW0001");std.mem.writeInt(u64,bytes[8..16],11,.little);std.mem.writeInt(u64,bytes[16..24],1,.little);std.mem.writeInt(u64,bytes[24..32],3,.little);}
 require(transfer(2,0,false,bytes[0..16],16)==16);require(transfer(2,0,false,bytes[16..32],16)==16);
}
fn rendezvous(child_first:bool)void{
 reset();startup();
 if(child_first){ready();tryCheck(af09Blocked(2),"READY_HOLD");query();}else{query();tryCheck(af09Blocked(6),"QUERY_HOLD");ready();}
 tryCheck(!af09Blocked(2) and af09Blocked(6),"QUERY_RELEASE");
 parentExit();late();af09Refresh();
 tryCheck(af09.query_positive and !af09.query_pending and states[6].execution.frame.rax==1 and states[6].execution.frame.r8==1,"QUERY_RESULT");
 tryCheck(!af09.invalid,"RENDEZVOUS_VALID");
 active=6;const f=Frame{.rax=0x2a000,.rdi=0xe002};_=sustainedOperation(&f);
 tryCheck(af09.observed and af09.deadline==510,"FIXED_DEADLINE");
}
fn tryCheck(ok:bool,comptime message:[]const u8)void{if(!ok)@panic(message);}
fn settle()void{
 active=6;var f=Frame{.rax=0x20007};_=stopEntry(&f);
 for(0..4) |index|{active=6;f=.{.rax=0x24003,.rdi=channels[index].cap(if(index%2==0)0 else 1)};_=channelOperation(&f);tryCheck(states[6].execution.frame.rax==0,"PEER_CLOSE");}
 active=6;_=reclaimEntry(2);active=6;_=reclaimEntry(1);
 tryCheck(af09Settled() and reclaimed==2,"ACTUAL_SETTLEMENT");
}
fn counterTransfers()void{
 settle();
 // These ledger values are driven by actual checked transfers, rather than
 // assigning progress counters or invoking hook-only transfer stand-ins.
 const bytes=[_]u8{0}**16;
 for(0..16) |_|{_=transfer(6,4,false,&bytes,16);_=transfer(0,4,true,&bytes,16);_=transfer(0,5,false,&bytes,16);_=transfer(6,5,true,&bytes,16);}
}
fn counterOutput()void{
 states[0].backing[0][0..8].*=.{1,1,2,0,3,0,0,0};active=0;
 const f=Frame{.rax=0x10001,.rdi=1,.rsi=0x1000,.rdx=8};_=outputEntry(&f);
}
fn counts()void{counterTransfers();counterOutput();}
'''
CASES = r'''
test "both checkpoint arrival orders preserve saved primary FS FP and wait state" {
 std.debug.print("AF09_STATE_BYTES={d}\n",.{@sizeOf(Af09.State)});
 for([_]bool{true,false}) |first|{
  rendezvous(first);
  tryCheck(states[2].execution.fs==102 and states[2].execution.fp[33]==42 and states[2].execution.frame.rip==202,"CPU_STATE");
  tryCheck(states[2].execution.wait.address==0 and states[6].execution.fs==106,"WAIT_STATE");
 }
}
test "only exact 32 byte prefix and complete publication release query" {
 reset();startup();ready();query();parentExit();
 const bytes=[_]u8{0}**16;
 _=transfer(2,0,false,&bytes,16);af09Refresh();tryCheck(af09.query_pending,"NO_EARLY_QUERY");
 channels[0].stream.count=31;af09.late_written=31;af09Refresh();tryCheck(af09.query_pending,"NO_31_QUERY");
 reset();startup();af09.startup_read=303;ready();tryCheck(af09.invalid and !af09.child_ready,"INCOMPLETE_PUBLICATION");
 reset();startup();channels[0].generation+=1;ready();tryCheck(af09.invalid,"STALE_ENDPOINT");
 reset();startup();states[2].generation+=1;ready();tryCheck(af09.invalid,"STALE_CHILD");
 reset();startup();ready();query();parentExit();_=transfer(2,0,false,&bytes,16);_=transfer(2,0,false,&bytes,16);tryCheck(af09.invalid and !af09.query_positive,"WRONG_PREFIX");
}
test "scheduler permits engine helper and idle excludes held primary" {
 rendezvous(true);counts();
 if(af09_mode==.no_ack or af09_mode==.pending_fragment){
  tryCheck(af09.engine_hold==.counter and states[0].execution.frame.rax==8,"COUNTER_HOLD");
  for(&states) |*s|s.admitted=false;
  states[0].admitted=true;states[0].children[0].used=true;states[0].children[0].running=true;
  active=6;rotate();tryCheck(active==0 and states[0].on_child and !idle,"HELPER_RUNNABLE");
  states[0].children[0].running=false;rotate();tryCheck(idle,"HELD_PRIMARY_IDLE");
 }
}
test "counter packet offset reserved duplicate and counts fail closed" {
 rendezvous(true);counts();tryCheck(af09.counter_seen and !af09.invalid,"COUNTER_VALID");
 active=0;const f=Frame{.rdi=1,.rdx=8};af09Output(&f,0,8);tryCheck(af09.invalid,"DUPLICATE_COUNTER");
 rendezvous(true);settle();active=0;states[0].output[0..8].*=.{1,1,2,0,3,0,0,1};states[0].output_count=8;af09Output(&f,0,8);tryCheck(af09.invalid,"RESERVED_COUNTER");
}
test "fixed timing and pending fragment use actual Events deadline precedence" {
 rendezvous(true);counts();const bytes=[_]u8{0}**16;
 if(af09_mode==.pending_fragment){
  tryCheck(transfer(6,5,true,&bytes,16)==-11,"ACK_EAGAIN");
  active=6;const f=Frame{.rax=0x2a001,.rdi=0xe002,.rsi=sustained_events.sequence,.rdx=af09.deadline};_=sustainedOperation(&f);
  tryCheck(af09.deferred_park and !sustained_events.occupied and af09.engine_hold==.none,"DEFER_BEFORE_EVENTS");
  tryCheck(transfer(0,5,false,&bytes,16)==16,"REAL_ACK_FRAGMENT");
  tryCheck(af09.engine_hold==.ack and af09.ack_written==16 and af09.saved_sequence<sustained_events.sequence,"FRAGMENT_HOLD");
  while(total_ticks<af09.deadline){idle=true;const irq=Frame{.cs=8,.vector=32};_=idleIrq(&irq);}
  tryCheck(idle_ticks==500,"IDLE_TICK_PROGRESS");
  tryCheck(!af09.deferred_park and !sustained_events.occupied and @as(i64,@bitCast(states[6].execution.frame.rax))==-110 and states[6].execution.frame.r8==af09.deadline,"ORDINARY_TIMEOUT");
  tryCheck(channels[5].stream.count==16 and af09.ack_read==0 and !af09.invalid,"NO_FRAGMENT_CONSUMPTION");
 }else if(af09_mode==.partial_ack){
  _=transfer(0,5,false,&bytes,16);tryCheck(af09.engine_hold==.ack,"FIRST_ACK_HOLD");
  while(total_ticks<af09.t0+100)nativeTick();tryCheck(af09.engine_hold==.none,"FIRST_ACK_RELEASE");
  _=transfer(6,5,true,&bytes,16);_=transfer(0,5,false,&bytes,16);
  while(total_ticks<af09.t0+200)nativeTick();tryCheck(af09.engine_hold==.none,"SECOND_ACK_RELEASE");
  _=transfer(6,5,true,&bytes,16);_=transfer(0,5,false,&bytes,16);
  while(total_ticks<af09.deadline)nativeTick();tryCheck(af09.engine_hold==.ack and af09.ack_written==48 and !af09.invalid,"THIRD_ACK_HELD");
 }else if(af09_mode==.exit_deadline){
  for(0..4) |_|{_=transfer(0,5,false,&bytes,16);_=transfer(6,5,true,&bytes,16);}
  active=0;tryCheck(af09BeforeExit(0,1) and !states[0].terminal,"EXIT_PRETERMINAL");
 }
}
test "pending counter arrival orders wake ordinary Events before deferred ACK" {
 if(af09_mode!=.pending_fragment)return;
 for([_]bool{true,false}) |owner_first|{
  rendezvous(true);counterTransfers();const bytes=[_]u8{0}**16;
  tryCheck(!af09.counter_seen and af09.engine_hold==.none,"COUNTER_NOT_PRESEEDED");
  if(owner_first){
   tryCheck(transfer(6,5,true,&bytes,16)==-11 and !af09.ack_eagain,"PRECOUNTER_EAGAIN");
   active=6;const park=Frame{.rax=0x2a001,.rdi=0xe002,.rsi=sustained_events.sequence,.rdx=af09.deadline};_=sustainedOperation(&park);
   tryCheck(sustained_events.parked() and !af09.deferred_park,"ORDINARY_OWNER_PARK");
   const expected=sustained_events.sequence;counterOutput();
   tryCheck(!sustained_events.occupied and states[6].execution.frame.rax==0 and states[6].execution.frame.rdx>expected,"COUNTER_EVENT_WAKE");
  }else{counterOutput();}
  tryCheck(af09.counter_seen and af09.engine_hold==.counter and af09.ack_written==0 and !af09.invalid,"COUNTER_STILL_HELD");
  active=6;const observe=Frame{.rax=0x2a000,.rdi=0xe002};_=sustainedOperation(&observe);
  const saved=states[6].execution.frame.rdx;
  tryCheck(transfer(6,5,true,&bytes,16)==-11 and af09.ack_eagain,"POSTCOUNTER_EAGAIN");
  active=6;const park=Frame{.rax=0x2a001,.rdi=0xe002,.rsi=saved,.rdx=af09.deadline};_=sustainedOperation(&park);
  tryCheck(af09.deferred_park and !sustained_events.occupied and af09.engine_hold==.none,"ORDER_DEFERRED_RELEASE");
  tryCheck(transfer(0,5,false,&bytes,16)==16 and af09.ack_written==16 and af09.ack_read==0 and af09.engine_hold==.ack,"ORDER_REAL_ACK_FRAGMENT");
  while(total_ticks<af09.deadline){idle=true;const irq=Frame{.cs=8,.vector=32};_=idleIrq(&irq);}
  tryCheck(@as(i64,@bitCast(states[6].execution.frame.rax))==-110 and states[6].execution.frame.r8==510 and af09.deadline==510,"ORDER_FIXED_DEADLINE");
  tryCheck(channels[5].stream.count==16 and af09.ack_read==0 and !af09.invalid,"ORDER_FRAGMENT_UNCONSUMED");
  var rows=std.mem.splitScalar(u8,capture[0..captured],'\n');var deferred:usize=0;var counter_wake:usize=0;
  while(rows.next()) |line|{
   if(std.mem.indexOf(u8,line," phase=26 ")!=null)deferred+=1;
   if(std.mem.indexOf(u8,line," phase=11 ")!=null and std.mem.indexOf(u8,line," status=0 ")!=null)counter_wake+=1;
  }
  tryCheck(deferred==2 and counter_wake==@intFromBool(owner_first),"ORDER_EVENT_AND_TWO_REGISTRATIONS");
 }
}
test "pending notification requires validated counter and successful hold" {
 if(af09_mode!=.pending_fragment)return;
 for(0..5) |bad|{
  rendezvous(true);counterTransfers();const sequence=sustained_events.sequence;
  switch(bad){
   0=>states[0].generation+=1,
   1=>channels[5].generation+=1,
   2=>states[0].execution.wait.address=0x1000,
   3=>states[0].on_child=true,
   4=>states[0].output_count=1,
   else=>unreachable,
  }
  counterOutput();
  tryCheck(af09.invalid and sustained_events.sequence==sequence and af09.engine_hold==.none,"NO_INVALID_COUNTER_WAKE");
 }
 rendezvous(true);counts();const sequence=sustained_events.sequence;counterOutput();
 tryCheck(af09.invalid and sustained_events.sequence==sequence,"NO_DUPLICATE_WAKE");
 rendezvous(true);counterTransfers();active=0;states[0].backing[0][0..8].*=.{1,1,2,0,3,0,0,1};
 const bad=Frame{.rax=0x10001,.rdi=1,.rsi=0x1000,.rdx=8};const before=sustained_events.sequence;_=outputEntry(&bad);
 tryCheck(af09.invalid and !af09.counter_seen and sustained_events.sequence==before,"NO_MALFORMED_COUNTER_WAKE");
}
test "pending repark rejects missing postcounter EAGAIN future and exhausted sequence" {
 if(af09_mode!=.pending_fragment)return;
 const bytes=[_]u8{0}**16;
 for(0..3) |bad|{
  rendezvous(true);counterTransfers();
  tryCheck(transfer(6,5,true,&bytes,16)==-11 and !af09.ack_eagain,"EARLY_EAGAIN_NOT_ARMED");
  counterOutput();
  if(bad!=0)tryCheck(transfer(6,5,true,&bytes,16)==-11,"DENIAL_POSTCOUNTER_EAGAIN");
  if(bad==2)sustained_events.sequence=std.math.maxInt(u64);
  active=6;const park=Frame{.rax=0x2a001,.rdi=0xe002,.rsi=sustained_events.sequence+@as(u64,if(bad==1)1 else 0),.rdx=af09.deadline};_=sustainedOperation(&park);
  tryCheck(af09.invalid and !af09.deferred_park and af09.engine_hold==.counter and af09.ack_written==0,"INVALID_REPARK_KEEPS_ENGINE_HELD");
 }
}
test "counter notification remains limited to pending fragment" {
 rendezvous(true);counterTransfers();const sequence=sustained_events.sequence;counterOutput();
 tryCheck(sustained_events.sequence==sequence+@as(u64,@intFromBool(af09_mode==.pending_fragment)),"ONLY_PENDING_COUNTER_EVENT");
}
test "pending actual channel rejects short extra ACK and resumed deadline" {
 if(af09_mode!=.pending_fragment)return;
 const bytes=[_]u8{0}**16;
 for(0..4) |bad|{
  rendezvous(true);counts();
  if(bad==0){
   _=transfer(0,5,false,&bytes,16);
   tryCheck(af09.invalid and !af09.deferred_park,"NO_ACK_BEFORE_DEFERRED_PARK");
   continue;
  }
  tryCheck(transfer(6,5,true,&bytes,16)==-11,"ACK_SIZE_EAGAIN");
  active=6;const park=Frame{.rax=0x2a001,.rdi=0xe002,.rsi=sustained_events.sequence,.rdx=af09.deadline};_=sustainedOperation(&park);
  tryCheck(af09.deferred_park and af09.engine_hold==.none,"ACK_SIZE_DEFERRED");
  if(bad==1){
   _=transfer(0,5,false,bytes[0..8],8);
   tryCheck(af09.invalid and af09.ack_written==8 and af09.ack_read==0,"NO_SHORT_ACK");
  }else{
   _=transfer(0,5,false,&bytes,16);
   tryCheck(!af09.invalid and af09.engine_hold==.ack,"ACK_SIZE_FIRST_FRAGMENT");
   if(bad==2){
    _=transfer(0,5,false,&bytes,16);
    tryCheck(af09.invalid and af09.ack_written==32 and af09.ack_read==0,"NO_EXTRA_ACK");
   }else{
    total_ticks=af09.deadline+1;af09Refresh();
    tryCheck(af09.invalid and af09.deferred_park and !sustained_events.occupied and af09.deadline==510,"NO_RESUMED_DEADLINE");
   }
  }
 }
}
test "cancel only matching generations and never renew a missed window" {
 rendezvous(true);counts();const generation=af09.generations[0];af09.cancel(0,generation+1);
 if(af09_mode==.no_ack or af09_mode==.pending_fragment)tryCheck(af09Blocked(0),"WRONG_CANCEL");
 af09.cancel(0,generation);tryCheck(!af09Blocked(0),"MATCH_CANCEL");
 reset();af09.query_positive=true;total_ticks=5401;active=6;const f=Frame{.rax=0x2a000,.rdi=0xe002};_=sustainedOperation(&f);tryCheck(af09.invalid and !af09.observed,"MISSED_WINDOW");
}
test "authenticated query and channel scalar pointer direction precedence remain" {
 reset();startup();active=1;var f=Frame{.rax=0x20001,.rdi=handle(1)};_=queryEntry(&f);tryCheck(@as(i64,@bitCast(states[1].execution.frame.rax))==-13 and !af09.query_pending,"QUERY_AUTHORITY");
 active=6;f.rdi=handle(1)+0x100;_=queryEntry(&f);tryCheck(@as(i64,@bitCast(states[6].execution.frame.rax))==-9 and !af09.query_pending,"QUERY_HANDLE");
 active=2;f=.{.rax=0x24002,.rdi=channels[0].cap(1),.rsi=0,.rdx=16,.r10=1};_=channelOperation(&f);tryCheck(@as(i64,@bitCast(states[2].execution.frame.rax))==-22 and channels[0].stream.count==0,"RESERVED_PRECEDENCE");
 f.r10=0;_=channelOperation(&f);tryCheck(@as(i64,@bitCast(states[2].execution.frame.rax))==-14 and channels[0].stream.count==0,"POINTER_PREFLIGHT");
 f.rdi=channels[1].cap(0);_=channelOperation(&f);tryCheck(@as(i64,@bitCast(states[2].execution.frame.rax))==-9,"DIRECTION_PRECEDENCE");
 f.rdi+=0x100;_=channelOperation(&f);tryCheck(@as(i64,@bitCast(states[2].execution.frame.rax))==-13,"HOLDER_PRECEDENCE");
}
test "real source closes disposal late reads and false clean halt remain observable" {
 rendezvous(true);tryCheck(channels[0].stream.count==32,"ACTUAL_QUEUE");
 const bytes=[_]u8{0}**16;_=transfer(6,0,true,&bytes,16);tryCheck(af09.late_read==16 and af09.invalid,"LATE_CONSUMPTION");
 rendezvous(true);active=2;for(&channels)|*c|c.closeOwner(2);
 active=6;var f=Frame{.rax=0x24003,.rdi=channels[0].cap(0)};_=channelOperation(&f);tryCheck(channels[0].stream.count==0,"DISPOSAL");
 // Actual Endpoints.close() releases its reply reader before request writer.
 for([_]usize{5,4}) |index|{active=6;const side:usize=if(index==5)0 else 1;f=.{.rax=0x24003,.rdi=channels[index].cap(side)};_=channelOperation(&f);tryCheck(states[6].execution.frame.rax==0 and channels[index].owners[side]==null,"SOURCE_CLOSE_EFFECT");}
 var close_rows=std.mem.splitScalar(u8,capture[0..captured],'\n');var close_count:usize=0;
 while(close_rows.next()) |line|{if(std.mem.indexOf(u8,line," phase=19 ")!=null){
  tryCheck(close_count<2,"SOURCE_CLOSE_ORDER");
  tryCheck(std.mem.endsWith(u8,line,if(close_count==0)" aux=1" else " aux=0"),"SOURCE_CLOSE_ORDER");close_count+=1;
 }}
 tryCheck(close_count==2,"SOURCE_CLOSE_ORDER");
 tryCheck(af09.source_closes==3,"BOTH_SOURCE_CLOSES");
 for(&channels)|*c|{c.closeOwner(0);c.closeOwner(6);}
 states[1].admitted=false;states[2].admitted=false;states[0].admitted=true;
 active=6;f=.{.rax=0x2a002,.rdi=0xf002};_=sustainedOperation(&f);tryCheck(@as(i64,@bitCast(states[6].execution.frame.rax))==-16,"NO_FALSE_CLEAN");
}
test "renewed deadline and late setup fail without moving the original window" {
 rendezvous(true);const deadline=af09.deadline;active=6;const f=Frame{.rax=0x2a001,.rdi=0xe002,.rsi=sustained_events.sequence,.rdx=deadline+1};_=sustainedOperation(&f);tryCheck(af09.invalid and af09.deadline==deadline,"NO_RENEWAL");
}

test "child native READY before owner wire READY consumption holds through publication" {
 reset();startupBytes();readyWireSend();ready();tryCheck(af09.child_ready and af09.child_hold==.ready and af09.ready_read==0 and af09.parent_written==0 and !af09.invalid,"EARLY_NATIVE_READY");
 readyWireReceive();parentDisposition();tryCheck(af09.child_hold==.ready and !af09.invalid,"HOLD_THROUGH_PUBLICATION");
 query();tryCheck(af09.query_pending and af09.child_hold==.none,"RELEASE_AFTER_PUBLICATION");parentExit();late();af09Refresh();tryCheck(af09.query_positive and !af09.invalid,"EARLY_READY_RENDEZVOUS");
 reset();startupBytes();readyWireSend();ready();query();tryCheck(af09.invalid and !af09.query_pending and states[6].execution.frame.rax==0,"EARLY_QUERY_NO_DEFER");
}

'''

class NativeAf09Drain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deadline=time.monotonic()+300
        cls.addClassCleanup(cls.check_deadline)
        cls.file_limit=compiler_file_limit(cls)

    @classmethod
    def check_deadline(cls):
        if time.monotonic()>cls.deadline:
            raise AssertionError("AF09 focused aggregate expired after finalization")

    def capture(self, command, out):
        remaining=self.deadline-time.monotonic()
        self.assertGreater(remaining,0,'AF09 focused host300-second bound')
        result=run_capture(command,cwd=ROOT,timeout=min(180,remaining),limit=4*1024*1024)
        for path in out.rglob('*'):
            if path.is_file():
                self.assertLessEqual(path.stat().st_size,16*1024*1024,'AF09 compiler file16MiB bound: '+str(path))
        return result

    def source(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        hooks=native[native.index('// Diagnostic hooks execute'):native.index('const elf =')]
        functions='\n'.join(block(native,'fn '+name+'(') for name in ('byte','channelBuffer','ownedChannel','channelOperation','rotate','publishSustained','refreshSustained','sustainedOperation','handle','lookup'))
        functions=block(native,'const ChannelBuffer = struct')+';\n'+functions
        tick=block(native,'fn nativeTick(')
        functions+='\n'+tick[:tick.index('    const monotonic')]+'}\n'
        ready=block(block(native,'fn control('),'    if (frame.rax == 0x20004 or frame.rax == 0x20005)')
        functions+='\nfn readyEntry(frame:*const Frame)*const Frame{const caller=&states[active];\n'+ready+'\nreturn select();}\n'
        copy=block(native,'fn copyOperation(')
        tail=copy[copy.index('    require(reader.transfer(active, f.r8, slot)'):]
        functions+='\nfn copyPublication()*const Frame{const from:usize=1;const slot:usize=2;const source=&states[from];const child=&states[slot];const caller=&states[6];const reader=&channels[1];const writer=&channels[0];const frame=Frame{.r8=reader.cap(0),.r9=writer.cap(1)};const f=&frame;'+tail+'\n'
        control=block(native,'fn control(')
        owner_check=block(control,'    if (active != supervisorSlot())')
        lookup_body=control[control.index('    const slot = lookup(frame.rdi)'):control.index('    switch (frame.rax)')]
        stop=block(control,'        0x20007 => {')
        functions+='\nfn stopEntry(frame:*const Frame)*const Frame{const slot:usize=2;const s=&states[slot];const caller=&states[6];switch(frame.rax){'+stop+',else=>unreachable,}return select();}\n'
        reclaim=block(control,'        0x20002 => {')
        functions+='\nfn reclaimEntry(slot:usize)*const Frame{const s=&states[slot];const caller=&states[6];switch(@as(u64,0x20002)){'+reclaim+',else=>unreachable,}return select();}\n'
        functions+='\n'+block(native,'fn closeChannels(')+'\n'
        query=block(control,'        0x20001 => {')
        functions+='\nfn queryEntry(frame:*const Frame)*const Frame{const caller=&states[active];'+owner_check+lookup_body+'switch(frame.rax){'+query+',else=>unreachable,}return select();}\n'
        irq=block(native,'    if (idle and frame.cs == 8 and frame.vector == 32)')
        functions+='\nfn idleIrq(frame:*const Frame)*const Frame{'+irq+'@panic("IDLE_ONLY");}\n'
        output=block(native,'        0x10000 + 1 => {')
        functions+='\nfn outputEntry(frame:*const Frame)*const Frame{const s=&states[active];switch(frame.rax){'+output+',else=>unreachable,}return select();}\n'
        select=block(native,'fn select(')
        functions+='\n'+select[:select.index('    const s = &states[active];')]+'return &states[active].context().frame;\n}\n'
        text=SCAFFOLD+hooks+functions+CASES
        for old,new in (('@import("../../native_af09_drain.zig")','K.Af09'),('@import("../../native_channel.zig")','C'),('@import("native_execution.zig")','E')):
            text=text.replace(old,new)
        return text

    def test_closed_selector_and_default_state_absence(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        declarations='\n'.join(line for line in native.splitlines() if line.startswith(('const af09_mode =','const af09_enabled =','var af09:')))
        with tempfile.TemporaryDirectory(prefix='aether-af09-selector-') as directory:
            out=Path(directory)
            for selection in (None,'none','UNKNOWN','stream,partial_ack'):
                options='' if selection is None else 'pub const native_af09_drain="'+selection+'";'
                (out/'options.zig').write_text(options)
                (out/'actual.zig').write_text('const Af09=@import("af09");\n'+declarations+'\ntest "default diagnostic state absent" { if (@sizeOf(@TypeOf(af09)) != 0) @compileError("AF09_DEFAULT_STATE"); }')
                # Strip symbols only; default Debug safety and file caps remain.
                command=['zig','test','-fstrip','--cache-dir',str(out/'cache'),'--global-cache-dir',str(out/'global'),'--dep','af09','--dep','build_options','-Mroot='+str(out/'actual.zig'),'-Maf09='+str(ROOT/'kernel/native_af09_drain.zig'),'-Mbuild_options='+str(out/'options.zig')]
                result=self.capture(command,out)
                if selection in (None,'none'):
                    self.assertEqual(result.returncode,0,result.stderr)
                else:
                    self.assertNotEqual(result.returncode,0)
                    self.assertIn('unknown native-af09-drain case',result.stderr)

    def test_actual_bodies_all_cases_and_semantic_omissions(self):
        source=self.source()
        cases=('file_prefix','exec_prefix','fork_prefix','stream','no_ack','partial_ack','exit_deadline','pending_fragment')
        variants=[(case,source,None) for case in cases]
        mutations=(
          ('early-query','states[1].terminal and states[1].terminal_kind == 1 and states[1].status == 0 and af09.child_ready and af09.late_written == 32 and af09.late_read == 0 and channels[af09.objects[0].index].stream.count == 32','states[1].terminal','NO_EARLY_QUERY','only exact'),
          ('missing-generation','states[slot].generation != af09.generations[slot]','false','STALE_CHILD','only exact'),
          ('no-primary-exclusion',' or (af09_enabled and af09Blocked(candidate))','','HELD_PRIMARY_IDLE','scheduler'),
          ('renewed-deadline','if (f.rdx != af09.deadline)','if (f.rdx == 0)','NO_RENEWAL','renewed deadline'),
          ('counter-wake-omitted','if (af09Hold(0, .counter) and af09_mode == .pending_fragment) publishSustained();','_ = af09Hold(0, .counter);','COUNTER_EVENT_WAKE','pending counter arrival orders'),
          ('counter-hold-ignored','if (af09Hold(0, .counter) and af09_mode == .pending_fragment) publishSustained();','const held = af09Hold(0, .counter); _ = held; if (af09_mode == .pending_fragment) publishSustained();','NO_INVALID_COUNTER_WAKE','pending notification'),
          ('early-events','af09.deferred_park = true;','af09.deferred_park = true; sustained_events.park(f.rsi,total_ticks,af09.deadline,false) catch unreachable;','DEFER_BEFORE_EVENTS','fixed timing'),
          ('early-child-release','if (slot == 2) af09.child_hold = hold','if (slot == 2) af09.child_hold = .none','READY_HOLD','both checkpoint'),
          ('engine-wide-block','if (session_lifecycle and next.channel_wait.endpoint != 0)','if ((session_lifecycle and next.channel_wait.endpoint != 0) or af09Blocked(candidate))','HELPER_RUNNABLE','scheduler'),
          ('late-read-unobserved','af09.late_read += amount;','af09.late_read += 0;','LATE_CONSUMPTION','real source closes'),
          ('source-close-omitted','const closed = selected.close(active, f.rdi);','const closed: i64 = 0;','DISPOSAL','real source closes'),
          ('source-close-wrong-side','af09Row(19, 6, status, 0, @intFromBool(af09Matches(c, 5)));','af09Row(19, 6, status, 0, @intFromBool(af09Matches(c, 4)));','SOURCE_CLOSE_ORDER','real source closes'),
          ('false-clean','for (states[0..workerCount()]) |*worker| busy = busy or worker.admitted;','','HALT','real source closes'),
        )
        for name,old,new,oracle,test_filter in mutations:
            if not oracle:continue
            self.assertIn(old,source,name)
            variants.append((name,source.replace(old,new),'pending_fragment' if name in ('early-events','counter-wake-omitted','counter-hold-ignored') else 'no_ack',oracle,test_filter))
        self.run_variants(variants)

    def test_pending_counter_arrival_orders(self):
        self.run_variants([('pending_fragment',self.source(),None,None,'pending counter arrival orders')])

    def run_variants(self, variants):
        cases=('file_prefix','exec_prefix','fork_prefix','stream','no_ack','partial_ack','exit_deadline','pending_fragment')
        with tempfile.TemporaryDirectory(prefix='aether-af09-kernel-') as directory, tempfile.NamedTemporaryFile(mode='w',prefix='.af09-host-imports-',suffix='.zig',dir=ROOT/'kernel') as facade:
            out=Path(directory)
            facade.write('pub const C=@import("native_channel.zig");pub const Sustained=@import("native_sustained.zig");pub const E=@import("arch/x86_64/native_execution.zig");pub const Frame=@import("arch/x86_64/context.zig").Frame;pub const FsRoles=@import("arch/x86_64/native_fs_roles.zig");pub const Af09=@import("native_af09_drain.zig");');facade.flush()
            for item in variants:
                name,body=item[:2];selected=name if name in cases else item[2];oracle=None if name in cases else item[3]
                (out/'options.zig').write_text('pub const native_af09_drain="'+selected+'";pub const native_signal_suspend=false;pub const native_service_channel_wait=false;pub const native_no_output=false;pub const native_service_block=false;pub const native_skip_zero=false;pub const native_signal_actions=false;')
                (out/'actual.zig').write_text(body)
                command=['zig','test','-fstrip','--cache-dir',str(out/'cache'),'--global-cache-dir',str(out/'global')]
                command+=['--dep','kernel','--dep','build_options','-Mroot='+str(out/'actual.zig'),'-Mkernel='+facade.name,'-Mbuild_options='+str(out/'options.zig')]
                if len(item)>4:
                    command+=['--test-filter',item[4]]
                result=self.capture(command,out)
                if oracle:
                    self.assertNotEqual(result.returncode,0,name);self.assertNotRegex(result.stderr,r':\d+:\d+: error:',name+result.stderr);self.assertIn(oracle,result.stderr,name+result.stderr)
                else:self.assertEqual(result.returncode,0,name+'\n'+result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
