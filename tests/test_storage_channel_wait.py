# SPDX-License-Identifier: BSD-2-Clause
"""Actual scheduler/registration/frame bodies; host scaffolding is not a VM."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import storage_channel_wait as wait
import service_runtime_smoke as runtime
from test_native_cleanup import block

RUST = r'''
use std::{cell::RefCell,collections::VecDeque};
std::thread_local! { static EVENTS: RefCell<VecDeque<(u64,i64,usize)>> = RefCell::new(VecDeque::new()); static BASE: RefCell<usize> = const { RefCell::new(0) }; }
std::thread_local! {static LIMIT: RefCell<(bool,usize)> = const {RefCell::new((false,0))};}
unsafe fn trap(op:u64, endpoint:u64, pointer:u64, length:u64, reserved:u64)->(i64,u64) {
 if LIMIT.with(|s|s.borrow().0) {LIMIT.with(|s|s.borrow_mut().1+=1);return (if op==0x24004 {0}else{-11},0);}
 assert_eq!(endpoint,23); assert_eq!(reserved,0);
 let (expected,result,offset)=EVENTS.with(|s|s.borrow_mut().pop_front().expect("FRAME_WAIT unexpected transfer"));
 assert_eq!(op,expected,"FRAME_WAIT");
 if op==0x24004 { assert_eq!((pointer,length),(0,0)); }
 else {
  BASE.with(|b|assert_eq!(pointer as usize,*b.borrow()+offset,"FRAME_OFFSET"));
  assert_eq!(length,(64-offset).min(16) as u64);
  if op==0x24001 && result>0 && result<=length as i64 {
   for i in 0..result as usize { unsafe { *((pointer as *mut u8).add(i))=(offset+i) as u8; } }
  }
 }
 (result,0)
}
fn run(writing:bool,events:&[(u64,i64,usize)],ok:bool) {
 let mut bytes=[0xa5;64]; BASE.with(|s|*s.borrow_mut()=bytes.as_ptr() as usize);
 EVENTS.with(|s|*s.borrow_mut()=events.iter().copied().collect());
 let result=frame(23,&mut bytes,writing);
 assert_eq!(result.is_ok(),ok,"FRAME_TERMINAL");
 EVENTS.with(|s|assert!(s.borrow().is_empty(),"FRAME_WAIT unconsumed events"));
 if !ok { assert_eq!(bytes,[0;64],"FRAME_CLEAR"); }
 else if !writing { for (i,b) in bytes.into_iter().enumerate(){assert_eq!(b,i as u8);} }
}
#[test] fn partial_progress_spurious_hints_and_no_polling() {
 for writing in [false,true] {
  let op=if writing {0x24002} else {0x24001};
  run(writing,&[(op,5,0),(op,-11,5),(0x24004,0,0),(op,-11,5),(0x24004,0,0),(op,11,5),(op,16,16),(op,16,32),(op,16,48)],true);
 }
}
#[test] fn spurious_hint_exhaustion_retains_original_attempt_ceiling() {
 LIMIT.with(|s|*s.borrow_mut()=(true,0));let mut bytes=[0xa5;64];
 assert_eq!(frame(23,&mut bytes,false),Err(-110));assert_eq!(bytes,[0;64],"FRAME_CLEAR");
 LIMIT.with(|s|{assert_eq!(s.borrow().1,200_000);*s.borrow_mut()=(false,0);});
}
#[test] fn every_wait_failure_and_partial_terminal_clears_frame() {
 for status in [-4,-13,-38,-5,1] {
  run(false,&[(0x24001,5,0),(0x24001,-11,5),(0x24004,status,0)],false);
 }
 for result in [0,-32,17] {
  run(false,&[(0x24001,5,0),(0x24001,-11,5),(0x24004,0,0),(0x24001,result,5)],false);
 }
}
'''

ZIG = r'''
const std=@import("std");
const E=@import("exec"); const C=@import("channel");
const Execution=E.Execution; const Child=E.Child; const Frame=@TypeOf((Execution{}).frame);
const ContextList=[3]*Execution;
fn contextView(list:*const ContextList) []const *Execution { return list; }
const State=struct {
 admitted:bool=true,terminal:bool=false,frozen:bool=false,
 channel_wait:C.Wait=.{},execution:Execution=.{},children:[2]Child=@splat(.{.used=true,.running=true}),
 selected_child:usize=0,on_child:bool=false,suspend_mask:?u64=null,
 fn context(s:*State) *Execution {return if(s.on_child) &s.children[s.selected_child].execution else &s.execution;}
 fn childRecords(s:*State) []Child {return &s.children;}
 fn contexts(s:*State) ContextList {return .{&s.execution,&s.children[0].execution,&s.children[1].execution};}
};
var states:[2]State=@splat(.{}); var channels:[2]C.Channel=@splat(.{});
var active:usize=1;var idle=false;const supervised=true;var session_lifecycle=false;
const sustained_events=struct {fn parked() bool {return false;}};
fn supervisorSlot() usize{return 1;}
fn ownerEventsEnabled() bool{return false;}
fn refreshSustained() void{}
fn resumeSuspended(_: *State) void{}
fn channelInterrupted(_: *const State) bool{return false;}
fn select() *const Frame {return &states[active].context().frame;}
fn traceStorageChannelWait(_:usize,_:[]const u8,_:i64) void{}
'''
ZIG_TEST = r'''
fn reset() void {states=@splat(.{});channels=@splat(.{});active=1;idle=false;states[1].admitted=false;}
test "parked primary does not stop runnable helpers; all blocked becomes idle" {
 reset(); const reader:u64=@intCast(channels[0].create(0));
 try std.testing.expect(states[0].channel_wait.begin(&channels[0],0,reader,false)==null);
 for(0..6) |_| {rotate();try std.testing.expect(!idle and active==0 and states[0].on_child);}
 states[0].children[0].execution.wait.address=4096;states[0].children[1].running=false;
 rotate();try std.testing.expect(idle);
 try std.testing.expectEqual(@as(i64,0),channels[0].stream.push(42));
 rotate();try std.testing.expect(!idle and active==0 and !states[0].on_child);
 try std.testing.expectEqual(@as(u64,0),states[0].channel_wait.endpoint);
}
test "readiness completes only registered primary once while helper is selected" {
 reset();const reader:u64=@intCast(channels[0].create(0));
 _=states[0].channel_wait.begin(&channels[0],0,reader,false);
 states[0].execution.frame.rax=77;states[0].children[0].execution.frame.rax=93;states[0].on_child=true;
 _=channels[0].stream.push(42);refreshChannelWaits();
 try std.testing.expectEqual(@as(u64,0),states[0].execution.frame.rax);
 try std.testing.expectEqual(@as(u64,93),states[0].children[0].execution.frame.rax);
 states[0].execution.frame.rax=55;refreshChannelWaits();try std.testing.expectEqual(@as(u64,55),states[0].execution.frame.rax);
}
test "stale endpoint close wake and reset keep primary completion scoped" {
 reset();const reader:u64=@intCast(channels[0].create(0));
 _=states[0].channel_wait.begin(&channels[0],0,reader,false);_=channels[0].close(0,reader);
 refreshChannelWaits();try std.testing.expectEqual(@as(u64,@bitCast(@as(i64,-13))),states[0].execution.frame.rax);
 states[0].execution.frame.rax=55;states[0].channel_wait=.{};refreshChannelWaits();
 try std.testing.expectEqual(@as(u64,55),states[0].execution.frame.rax);
 reset();const r:u64=@intCast(channels[0].create(0));const writer=channels[0].cap(1);
 _=states[0].channel_wait.begin(&channels[0],0,r,false);_=channels[0].close(0,writer);refreshChannelWaits();
 try std.testing.expectEqual(@as(u64,0),states[0].channel_wait.endpoint);
}

test "actual syscall branch denies worker and foreign waits before registration" {
 reset();active=0;const reader:u64=@intCast(channels[0].create(0));
 var frame=Frame{.rax=0x24004,.rdi=reader};states[0].on_child=true;
 _=waitEntry(&frame);try std.testing.expectEqual(@as(i64,-22),@as(i64,@bitCast(states[0].children[0].execution.frame.rax)));
 try std.testing.expectEqual(@as(u64,0),states[0].channel_wait.endpoint);
 frame.rdi=reader+3;_=waitEntry(&frame);try std.testing.expectEqual(@as(i64,-13),@as(i64,@bitCast(states[0].children[0].execution.frame.rax)));
 states[0].on_child=false;frame.rdi=reader;frame.rsi=1;_=waitEntry(&frame);
 try std.testing.expectEqual(@as(i64,-22),@as(i64,@bitCast(states[0].execution.frame.rax)));
 try std.testing.expectEqual(@as(u64,0),states[0].channel_wait.endpoint);
}
'''

class StorageWait(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='aether-storage-wait-');self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)

    def test_actual_frame_and_compiling_wait_offset_clear_terminal_omissions(self):
        body='pub fn frame('+(ROOT/'user/storage/namespace-wait-channel.rs').read_text().split('pub fn frame(',1)[1]
        cases=[('base',body,None),('clear',body.replace('bytes.fill(0);',''),'FRAME_CLEAR'),
            ('offset',body.replace('if count == -11 {','if count == -11 { offset=0;'),'FRAME_OFFSET'),
            ('wait',body.replace('if status != 0 {','if false {'),'FRAME_WAIT'),
            ('eof',body.replace('if count == -11 {','if count==0 { return Ok(()); } else if count == -11 {'),'FRAME_TERMINAL')]
        for name,text,oracle in cases:
            p=self.out/(name+'.rs');p.write_text(RUST+text)
            binary=self.out/name
            c=subprocess.run(['rustc','+1.98.0','--edition=2024','--test','-Dwarnings',str(p),'-o',str(binary)],capture_output=True,text=True,timeout=60)
            self.assertEqual(c.returncode,0,c.stdout+c.stderr)
            run=subprocess.run([str(binary),'--test-threads=1'],capture_output=True,text=True,timeout=10)
            if oracle:self.assertNotEqual(run.returncode,0);self.assertIn(oracle,run.stdout+run.stderr)
            else:self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    def test_actual_scheduler_and_primary_completion_with_compiling_domain_skip_omission(self):
        source=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        funcs='\n'.join(block(source,'fn '+n+'(') for n in ('rotate','storagePrimaryWaiting','channelWaitEnabled','refreshChannelWaits','ownedChannel'))
        funcs=funcs.replace('@import("native_execution.zig")','@import("exec")').replace('@import("../../native_channel.zig")','@import("channel")')
        funcs=funcs.replace('channels[0..channelCount()]','&channels')
        early=block(source,'if (f.rax == 0x24004 and !channelWaitEnabled())')
        operation=block(source,'fn channelOperation(')
        tail=operation[operation.index('    const selected = ownedChannel'):operation.index('    if (f.r10 != 0 or f.r8 != 0')]
        tail=tail.replace('const end = selected.lookup(active, f.rdi).?;','const end = selected.lookup(active, f.rdi).?; _=end;')
        funcs+='\n'+block(source,'fn result(')+'\nfn waitEntry(f:*const Frame) *const Frame { const s=&states[active];\n'+early+tail+'\n@panic("wait-only test");}\n'

        options=self.out/'options.zig';options.write_text('pub const native_service_channel_wait=true;pub const native_signal_suspend=false;')
        for name,body in [('base',funcs),('domain-skip',funcs.replace('if (session_lifecycle and next.channel_wait.endpoint != 0)','if ((session_lifecycle or storagePrimaryWaiting(next)) and next.channel_wait.endpoint != 0)')),
                ('wrong-frame',funcs.replace('s.execution.frame.rax = @bitCast(done);','s.children[0].execution.frame.rax = @bitCast(done);')),('worker-wait',funcs.replace('and s.on_child)', 'and false)'))]:
            p=self.out/(name+'.zig');p.write_text(ZIG+body+ZIG_TEST)
            c=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),
                '--dep','exec','--dep','channel','--dep','build_options','-Mroot='+str(p),
                '-Mexec='+str(ROOT/'kernel/arch/x86_64/native_execution.zig'),'-Mchannel='+str(ROOT/'kernel/native_channel.zig'),'-Mbuild_options='+str(options)],capture_output=True,text=True,timeout=180)
            if name=='base':self.assertEqual(c.returncode,0,c.stdout+c.stderr)
            else:self.assertNotEqual(c.returncode,0);self.assertIn('TestUnexpectedResult' if name=='domain-skip' else 'expected -22, found' if name=='worker-wait' else 'expected 0, found 77',c.stdout+c.stderr)

    def test_default_namespace_object_preserves_the_pre_wait_bytes(self):
        # Preserve legacy panic/source locations when adding opt-in modules.
        # A moved cfg declaration must not silently alter old engine artifacts.
        compiler=subprocess.check_output(['rustup','which','--toolchain','1.98.0','rustc'],text=True).strip()
        output=self.out/'legacy-namespace.o'
        command=[compiler,'--crate-name','namespace_zpl','--edition=2024','--crate-type=lib',
            '--target=x86_64-unknown-none','--emit=obj','-Dwarnings','-Copt-level=2',
            '-Cpanic=abort','-Crelocation-model=static',
            str(ROOT/'user/storage/openzfs-volume/namespace-zpl.rs'),'-o',str(output)]
        result=subprocess.run(command,capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        previous=json.loads((ROOT/'docs/evidence/fs-service-mixed-native-2026-10-19.json').read_text())
        self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),
            previous['builds']['normal/baseline']['namespace_objects']['namespace-zpl'])

    def test_profile_and_trace_reject_unsafe_or_incomplete_inputs(self):
        wait.validate(True,True,True)
        for kw in ({'writer':True},{'reader':True},{'service':{}},{'mutation':'create'}):
            with self.assertRaises(ValueError):wait.validate(True,True,True,**kw)
        for selected,ipc,namespace in [(1,True,True),(True,False,True),(True,True,False)]:
            with self.assertRaises(ValueError):wait.validate(selected,ipc,namespace)
        with self.assertRaises(ValueError):runtime.suite(Path('/absent'),namespace_wait=True)
        text='NATIVE STORAGE WAIT slot=0 generation=1 phase=park status=0\nNATIVE STORAGE WAIT slot=0 generation=1 phase=wake status=0\n'
        text+='NATIVE STORAGE WAIT slot=2 generation=0 phase=park status=0\nNATIVE STORAGE WAIT slot=2 generation=0 phase=wake status=0\n'
        self.assertEqual(wait.trace(text)['primary_channel_waits'],2)
        for bad in ('',text.splitlines()[0],text+text.splitlines()[1],text.replace('slot=0','slot=3'),text.replace('slot=2 generation=0','slot=3 generation=0'),text.replace('status=0','status=-13'),text.replace('phase=park','phase=unknown')):
            with self.assertRaises(ValueError):wait.trace(bad)

    def test_private_build_gate_and_cli_reject_before_external_inputs(self):
        p=subprocess.run(['zig','build','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'-Dnative-service-channel-wait=true'],capture_output=True,text=True,timeout=60)
        self.assertNotEqual(p.returncode,0);self.assertIn('storage channel wait requires storage channel profile',p.stdout+p.stderr)
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/service_runtime_smoke.py'),'--delivery','/absent','--namespace-wait'],capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,64);self.assertNotIn('[RUNNING]',p.stderr)

    def test_strict_native_codegen_and_version_selection_preserve_legacy(self):
        out=self.out/'wait.o'
        c=subprocess.run(['rustc','+1.98.0','--edition=2024','--crate-type=lib','--target=x86_64-unknown-none','--emit=obj','-Dwarnings','-Copt-level=2','-Cpanic=abort','--cfg','namespace_ipc','--cfg','namespace_wait',str(ROOT/'user/storage/openzfs-volume/namespace-zpl.rs'),'-o',str(out)],capture_output=True,text=True,timeout=60)
        self.assertEqual(c.returncode,0,c.stdout+c.stderr)
        base=(runtime.SOURCE/'engine-supervisor.rs').read_text().replace('abi == 1','abi == 14')
        self.assertIn('abi == 25',runtime.namespace_ipc_driver(base))
        self.assertIn('abi == 26',runtime.namespace_ipc_driver(base,True))
