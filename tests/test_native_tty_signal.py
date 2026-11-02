# SPDX-License-Identifier: BSD-2-Clause
"""Selected terminal SIGINT actual bodies and checked frames; no guest claim."""
import ast
import hashlib
from pathlib import Path
import unittest

from test_native_cleanup import block
from test_native_tty_mode import NativeTtyMode, ROOT

def function(source, anchor):
    """Extract single-line signatures even when the return type has an error set."""
    start = source.index(anchor)
    opening = source.rfind('{', start, source.index('\n', start))
    if opening < start:
        raise AssertionError('function opening missing: '+anchor)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


SCAFFOLD = r'''
const std=@import("std");const K=@import("kernel");
const Frame=K.Frame;const Execution=K.E.Execution;const App=K.App;const Sustained=K.Sustained;
const nx:u64=1<<63;
const State=struct{
 admitted:bool=true,terminal:bool=false,generation:u64=1,
 tty_signal_owner_generation:?u64=null,app_binding:App.Binding=.{},
 signal_actions:K.Pending.State=.{},execution:Execution=.{},
 pages:[17]struct{address:u64=0,flags:u64=0}=@splat(.{}),
 backing:[17][4096]u8 align(4096)=@splat(@splat(0)),count:usize=17,
 fn context(s:*@This())*Execution{return &s.execution;}
};
var states:[7]State=@splat(.{});var active:usize=1;
const connections_profile=true;const sustained=false;
var threaded=false;
fn threadedSlot(_:usize)bool{return threaded;}
fn supervisorSlot()usize{return 6;}
fn workerCount()usize{return 6;}
fn result(s:*State,value:i64)void{s.context().frame.rax=@bitCast(value);}
fn select()*const Frame{return &states[active].context().frame;}
fn ordinaryAppEnabled()bool{return true;}
fn byte(s:*State,address:u64,writing:bool)?*u8{
 for(s.pages[0..s.count],0..)|page,i|{
  if(address>=page.address and address-page.address<4096 and (!writing or page.flags&2!=0))return &s.backing[i][@intCast(address-page.address)];
 }return null;
}
fn readUserBytes(s:*State,address:u64,out:[]u8)bool{
 for(out,0..)|*value,i|value.*=(byte(s,address+i,false) orelse return false).*;return true;
}
fn word(s:*State,address:u64,value:u64)void{
 var raw:[8]u8=undefined;std.mem.writeInt(u64,&raw,value,.little);
 for(raw,0..)|v,i|(byte(s,address+i,true) orelse unreachable).* = v;
}
fn reset()void{
 states=@splat(.{});active=1;threaded=false;
 for(&states)|*s|{
  s.pages[0]=.{.address=0x200000,.flags=5};
  for(0..16)|i|s.pages[i+1]=.{.address=0x08000000+i*4096,.flags=7|nx};
  s.context().frame=.{.rip=0x200030,.rsp=0x0800c000,.cs=0x23,.ss=0x1b,.flags=0x202,.rax=77};
  std.mem.writeInt(u32,s.context().fp[24..28],0x1f80,.little);
 }
}
fn installHandler(s:*State)void{
 _=s.signal_actions.install(2,.{.handler=.{.entry=0x200010,.restorer=0x200020,.mask=0}}) catch unreachable;
}
'''
MASK_CASES = r'''
test "actual safe mask return reports delivery failure and rolls back mask without dequeue" {
 for(0..4)|bad|{
  reset();const s=&states[1];installHandler(s);try s.signal_actions.post(2);s.context().signal_mask=2;
  switch(bad){0=>s.pages[0].flags|=nx,1=>s.pages[12].flags=5|nx,2=>s.context().frame.rsp=0x08000080,3=>std.mem.writeInt(u32,s.context().fp[24..28],0xffff0000,.little),else=>unreachable}
  const actions=s.signal_actions;const cpu=s.context().frame;const fp=s.context().fp;
  const f:Frame=.{.rax=0x1000e,.rdi=2,.rsi=0x08000000,.r10=8};_=maskSyscall(&f);
  const selected=@import("build_options").native_tty_signal_probe;
  try std.testing.expectEqual(@as(i64,if(selected)-5 else 0),@as(i64,@bitCast(s.context().frame.rax)));
  try std.testing.expectEqual(@as(u64,if(selected)2 else 0),s.context().signal_mask);
  try std.testing.expectEqualDeep(actions,s.signal_actions);
  var expected=cpu;expected.rax=@bitCast(@as(i64,if(selected)-5 else 0));
  try std.testing.expectEqualDeep(expected,s.context().frame);
  try std.testing.expectEqualSlices(u8,&fp,&s.context().fp);
 }
}
test "actual safe mask return enters real checked handler and preserves successful return payload" {
 reset();const s=&states[1];installHandler(s);try s.signal_actions.post(2);s.context().signal_mask=2;
 const f:Frame=.{.rax=0x1000e,.rdi=2,.rsi=0x08000000,.r10=8};_=maskSyscall(&f);
 try std.testing.expectEqual(@as(u64,0x200010),s.context().frame.rip);
 try std.testing.expectEqual(@as(u64,2),s.context().frame.rdi);
 try std.testing.expectEqual(@as(u32,0),s.signal_actions.pending);
 try std.testing.expectEqual(@as(u64,2),s.context().signal_mask);
 var restored:K.Signals.Candidate=undefined;
 try K.Signals.readReturnInto(&s.pages,&s.backing,s.context().frame.rsp+8,0xffbf,&restored);
 try std.testing.expectEqual(@as(u64,0x200030),restored.cpu.rip);
 try std.testing.expectEqual(@as(u64,0),restored.cpu.rax);
 try std.testing.expectEqual(@as(u64,0),restored.mask);
}
test "actual unmask rejects a newly unsupported pending SIGINT without false success" {
 reset();const s=&states[1];installHandler(s);try s.signal_actions.post(2);s.context().signal_mask=2;
 _=try s.signal_actions.install(2,.default);
 const prior=s.signal_actions;const f:Frame=.{.rax=0x1000e,.rdi=2,.rsi=0x08000000,.r10=8};_=maskSyscall(&f);
 const selected=@import("build_options").native_tty_signal_probe;
 try std.testing.expectEqual(@as(i64,if(selected)-5 else 0),@as(i64,@bitCast(s.context().frame.rax)));
 try std.testing.expectEqual(@as(u64,if(selected)2 else 0),s.context().signal_mask);
 try std.testing.expectEqualDeep(prior,s.signal_actions);
 try std.testing.expectEqual(@as(u64,0x200030),s.context().frame.rip);
}
test "masked pending never injects a handler during the actual mask query" {
 reset();const s=&states[1];installHandler(s);try s.signal_actions.post(2);s.context().signal_mask=2;
 const f:Frame=.{.rax=0x1000e,.r10=8};_=maskSyscall(&f);
 try std.testing.expectEqual(@as(u64,0x200030),s.context().frame.rip);
 try std.testing.expectEqual(@as(u64,2),s.context().signal_mask);
 try std.testing.expectEqual(@as(u32,2),s.signal_actions.pending);
 try std.testing.expectEqual(@as(u64,0),s.context().frame.rax);
}
'''


OP_CASES = r'''
fn binding()void{
 reset();active=6;states[6].generation=7;states[1].generation=3;
 states[1].app_binding=App.Binding.init(1,3,7,8,9).?;
 states[1].tty_signal_owner_generation=7;installHandler(&states[1]);
}
fn invoke(f:Frame)i64{_=ttySignalOperation(&f);return @bitCast(states[active].context().frame.rax);}
fn unchanged(f:Frame,wanted:i64)!void{
 const before=states;try std.testing.expectEqual(wanted,invoke(f));
 var after=states;after[active].context().frame.rax=before[active].execution.frame.rax;
 try std.testing.expect(std.meta.eql(before,after));
}
test "actual owner app SIGINT preflight post and disposition changes use current state" {
 binding();var f:Frame=.{.rax=0x29003,.rdi=handle(1),.rsi=2};
 try unchanged(f,1);try std.testing.expectEqual(@as(u32,0),states[1].signal_actions.pending);
 states[6].generation=0;states[1].tty_signal_owner_generation=0;try unchanged(f,1);
 states[1].tty_signal_owner_generation=null;try unchanged(f,-13);
 states[1].tty_signal_owner_generation=0;try unchanged(f,1);
 states[6].generation=7;states[1].tty_signal_owner_generation=7;
 f.rdx=1;try std.testing.expectEqual(@as(i64,1),invoke(f));
 try std.testing.expectEqual(@as(u32,2),states[1].signal_actions.pending);
 try unchanged(f,2);f.rdx=0;try unchanged(f,1);
 _=try states[1].signal_actions.install(2,.ignore);try unchanged(f,0);f.rdx=1;try unchanged(f,0);
 try std.testing.expectEqual(@as(u32,0),states[1].signal_actions.pending);
 installHandler(&states[1]);f.rdx=0;try unchanged(f,1);
 _=try states[1].signal_actions.install(2,.default);f.rdx=1;try unchanged(f,-95);f.rdx=0;try unchanged(f,-95);
 installHandler(&states[1]);try unchanged(f,1);
 _=try states[1].signal_actions.install(2,.{.handler=.{.entry=0x200040,.restorer=0x200050,.mask=4}});
 f.rdx=1;states[1].context().signal_mask=2;
 try std.testing.expectEqual(@as(i64,1),invoke(f));
 try std.testing.expect(states[1].signal_actions.peek(2)==null);
 try std.testing.expectEqual(@as(u64,0x200040),states[1].signal_actions.peek(0).?.action.handler.entry);
 try std.testing.expectEqual(@as(u64,0x200030),states[1].context().frame.rip);
}
test "actual scalar relationship target and generation denials have no effects" {
 for([_]u64{0,1})|post|{
  for(0..20)|bad|{
   binding();var f:Frame=.{.rax=0x29003,.rdi=handle(1),.rsi=2,.rdx=post};
   const expected:i64=switch(bad){
    0=>blk:{active=1;f.rdi=0;break :blk -13;},
    1=>blk:{states[6].admitted=false;break :blk -13;},
    2=>blk:{states[6].terminal=true;break :blk -13;},
    3=>blk:{states[6].generation+=1;break :blk -13;},
    4=>blk:{f.rdi=handle(0);break :blk -13;},
    5=>blk:{f.rdi=handle(6);break :blk -13;},
    6=>blk:{f.rdi=handle(2);break :blk -13;},
    7=>blk:{states[1].terminal=true;break :blk -3;},
    8=>blk:{states[1].admitted=false;break :blk -3;},
    9=>blk:{states[1].generation+=1;break :blk -3;},
    10=>blk:{states[1].generation+=1;f.rdi=handle(1);break :blk -13;},
    11=>blk:{states[1].app_binding=.{};break :blk -13;},
    12=>blk:{states[1].tty_signal_owner_generation=0;break :blk -13;},
    13=>blk:{threaded=true;break :blk -13;},
    14=>blk:{f.rsi=3;break :blk -22;},
    15=>blk:{f.rdx=2;break :blk -22;},
    16=>blk:{f.r10=1;break :blk -22;},
    17=>blk:{f.r8=1;break :blk -22;},
    18=>blk:{f.r9=1;break :blk -22;},
    19=>blk:{f.rdi=0;break :blk -3;},
    else=>unreachable,
   };
   try unchanged(f,expected);
  }
 }
}
'''


class NativeTtySignal(unittest.TestCase):
    records = []
    run_command = NativeTtyMode.run_command
    finish = classmethod(NativeTtyMode.finish.__func__)

    @classmethod
    def setUpClass(cls):
        NativeTtyMode.setUpClass.__func__(cls)
        cls.inputs.update({name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
            'kernel/arch/x86_64/native_pending.zig','kernel/arch/x86_64/native_signal.zig',
            'kernel/native_app.zig','tests/test_native_tty_signal.py',
            'tests/test_native_app.py','tests/test_native_cleanup.py')})

    def native(self):
        return (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()

    def compile(self, source, selected=True, expected=0, pending=None):
        for old,new in (('@import("native_pending.zig")','K.Pending'),
                        ('@import("native_signal.zig")','K.Signals'),
                        ('@import("native_execution.zig")','K.E')):
            source=source.replace(old,new)
        path=self.out/'actual.zig';path.write_text(source)
        (self.out/'options.zig').write_text('pub const native_tty_signal_probe='+str(selected).lower()+';'+
            'pub const native_signal_termination=false;pub const native_signal_actions=true;'+
            'pub const native_signal_mask_delivery=true;pub const native_runner_local=true;'+
            'pub const native_memory=true;pub const native_clock=true;pub const native_clock_ticks=false;'+
            'pub const native_service_lifetime=false;pub const native_signal_suspend=false;'+
            'pub const native_service_channel_wait=false;pub const native_skip_zero=false;'+
            'pub const native_process_exec=true;pub const native_exec_copy=false;pub const native_copy_signals=false;'+
            'pub const native_freeze_skip_park=false;pub const native_freeze_ignore_token=false;pub const native_exec_token=false;')
        with self.work.named_file(mode='w',prefix='.tty-signal-import-',suffix='.zig',dir=ROOT/'kernel') as facade:
            facade.write('pub const Pending=@import("arch/x86_64/'+(pending or 'native_pending.zig')+'");'+
                'pub const Signals=@import("arch/x86_64/native_signal.zig");'+
                'pub const E=@import("arch/x86_64/native_execution.zig");'+
                'pub const Frame=@import("arch/x86_64/context.zig").Frame;'+
                'pub const App=@import("native_app.zig");pub const Sustained=@import("native_sustained.zig");'+
                'pub const C=@import("native_channel.zig");pub const launch=@import("native_launch.zig");'+
                'pub const elf=@import("native_elf.zig");pub const memory=@import("native_memory.zig");'+
                'pub const FsRoles=@import("arch/x86_64/native_fs_roles.zig");'+
                'pub const Clock=@import("native_clock.zig");pub const Af09=@import("native_af09_drain.zig");')
            facade.flush()
            log=self.run_command(['zig','test','--test-filter','actual','--cache-dir',self.out/'cache',
                '--global-cache-dir',self.out/'global','--dep','kernel','--dep','build_options',
                '-Mroot='+str(path),'-Mkernel='+facade.name,
                '-Mbuild_options='+str(self.out/'options.zig')],expected,
                'FAIL' if expected else 'All ')
            self.assertNotRegex(log,r':\d+:\d+: error:')
        return log

    def mask_source(self, native=None):
        native=native or self.native()
        branch=block(native,'        0x10000 + 14 => {')
        return SCAFFOLD+block(native,'fn changeMask(')+function(native,'fn deliverPending(')+r'''
fn maskSyscall(frame:*const Frame)*const Frame{
 const s=&states[active];switch(frame.rax){
'''+branch+',else=>unreachable,}return select();}\n'+MASK_CASES

    def test_actual_selected_safe_unmask_delivery_and_failure(self):
        self.compile(self.mask_source())

    def test_actual_legacy_safe_mask_return_stays_unchanged(self):
        self.compile(self.mask_source(),False)

    def operation_source(self, native=None):
        native = native or self.native()
        return SCAFFOLD + 'fn processSlot(slot:usize)bool{return slot>0 and slot<6;}\n' + ''.join(
            block(native, name) for name in ('fn handle(', 'fn lookup(', 'fn ttySignalOperation(')) + OP_CASES

    def test_actual_owner_target_disposition_and_negative_effects(self):
        self.compile(self.operation_source())

    def test_unselected_operation_is_enosys_without_signal_storage(self):
        native=self.native()
        source=SCAFFOLD.replace('tty_signal_owner_generation:?u64=null','tty_signal_owner_generation:void={}').replace(
            'signal_actions:K.Pending.State=.{}','signal_actions:void={}')
        # No setup/handler helper may claim an available old-profile action record.
        source=source[:source.index('fn reset()')]
        source+='fn processSlot(slot:usize)bool{return slot>0 and slot<6;}\n'
        source+=''.join(block(native, name) for name in ('fn handle(', 'fn lookup(', 'fn ttySignalOperation('))
        source+=r'''
test "actual unselected SIGINT entry never touches absent action or relationship storage" {
 active=6;const f:Frame=.{.rax=0x29003,.rdi=0,.rsi=2};_=ttySignalOperation(&f);
 try std.testing.expectEqual(@as(i64,-38),@as(i64,@bitCast(states[6].context().frame.rax)));
}
'''
        self.compile(source,False)

    def test_compiling_owner_generation_omission_fails_actual_oracle(self):
        native=self.native();before='target.tty_signal_owner_generation != caller.generation or'
        self.assertEqual(native.count(before),1)
        self.compile(self.operation_source(native.replace(before,'false or',1)),expected=1)

    def test_compiling_failed_delivery_omission_fails_actual_oracle(self):
        native=self.native()
        before='if (!explicit and @hasDecl(@import("build_options"), "native_tty_signal_probe") and @import("build_options").native_tty_signal_probe) return error.DeliveryFailed;'
        self.assertEqual(native.count(before),1)
        self.compile(self.mask_source(native.replace(before,'',1)),expected=1)

    def test_compiling_mask_rollback_omission_fails_actual_oracle(self):
        native=self.native();before='s.context().signal_mask = prior_mask;'
        self.assertEqual(native.count(before),1)
        self.compile(self.mask_source(native.replace(before,'_ = prior_mask;',1)),expected=1)

    def test_actual_selected_self_post_denial_and_legacy_dispatch(self):
        native=self.native();branch=block(native,'    if (frame.rax == 0x29002) {')
        source=SCAFFOLD+r'''
var self_calls:usize=0;
fn finish(_:u64,_:u64)*const Frame{@panic("unexpected terminal");}
fn selfSignalOperation(_: *State,_:*const Frame)?K.Pending.SignalTerminal{self_calls+=1;return null;}
fn dispatch(frame:*const Frame)*const Frame{const s=&states[active];
'''+branch+r'''
 result(s,-38);return select();
}
test "actual selected self-post denied while old dispatch stays available" {
 reset();const f:Frame=.{.rax=0x29002,.rdi=2};_=dispatch(&f);
 if(@import("build_options").native_tty_signal_probe){
  try std.testing.expectEqual(@as(i64,-13),@as(i64,@bitCast(states[active].context().frame.rax)));
  try std.testing.expectEqual(@as(usize,0),self_calls);
 }else try std.testing.expectEqual(@as(usize,1),self_calls);
}
'''
        for selected in (True,False):
            self.compile(source,selected)

    def test_exact_selected_build_closure_and_defaults(self):
        self.assertRegex((ROOT/'build.zig').read_text(),
            r'const native_tty_signal_probe = b.option\(bool, "native-tty-signal-probe", [^\n]+\) orelse false;')
        tree=ast.parse((ROOT/'scripts/fs_session.py').read_text())
        value=next(node.value for node in tree.body if isinstance(node,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='FLAGS' for t in node.targets))
        flags=ast.literal_eval(value.func.value).split()+['native-fs-session-init',
            'native-fs-owner-data','native-fs-owner-stack','native-tty-mode-probe','native-signal-mask-delivery']
        image=self.out/'never-executed.bin';image.write_bytes(b'\0')
        base={'smp':'false','native-c-image':str(image),**dict.fromkeys(flags,'true')}
        def invoke(options,bad=False):
            return self.run_command(['zig','build','--help','--cache-dir',self.out/'cache',
                '--global-cache-dir',self.out/'global',
                *['-D'+key+'='+value for key,value in options.items()]],int(bad),
                None if bad else 'native-tty-signal-probe')
        invoke({});invoke(base);invoke({**base,'native-tty-signal-probe':'false'})
        selected={**base,'native-tty-signal-probe':'true'};invoke(selected)
        for flag in ('native-tty-mode-probe','native-signal-actions','native-signal-public',
                     'native-signal-mask-delivery','native-fs-owner-stack','native-process-copy'):
            with self.subTest(missing=flag):invoke({**selected,flag:'false'},True)
        for flag in ('smp','release-artifact','native-mktemp-reader','native-fs-application-profile'):
            with self.subTest(forbidden=flag):invoke({**selected,flag:'true'},True)
        invoke({**selected,'native-af09-drain':'file_prefix'},True)


    def test_actual_app_admission_and_all_terminal_paths_bind_then_revoke(self):
        from test_native_app import NativeApp
        source = NativeApp.actual_source(self)
        before = 'app_binding:App.Binding=.{},channel_cap:u64=0'
        self.assertEqual(source.count(before), 1)
        source = source.replace(before,
            'app_binding:App.Binding=.{},tty_signal_owner_generation:?u64=null,signal_actions:K.Pending.State=.{},channel_cap:u64=0')
        source += r'''
test "actual admission binds boot Owner generation zero and revokes every lifetime path" {
 reset();try std.testing.expect(states[1].tty_signal_owner_generation==null);
 var invalid=launchFrame();invalid.rdi=0;_=appLaunchOperation(&invalid);
 try std.testing.expect(response==-13 and states[1].tty_signal_owner_generation==null);
 launchApp();try std.testing.expectEqual(@as(?u64,0),states[1].tty_signal_owner_generation);
 try std.testing.expect(states[1].app_binding.bound());
 stopContexts(&states[1]);try std.testing.expect(states[1].tty_signal_owner_generation==null);
 for([_]u64{1,2})|kind|{
  reset();launchApp();active=1;_=finishEntry(17,kind);
  try std.testing.expect(states[1].terminal and states[1].tty_signal_owner_generation==null);
 }
 reset();states[6].generation=7;launchApp();
 try std.testing.expectEqual(@as(?u64,7),states[1].tty_signal_owner_generation);
 active=6;_=stopEntry(&.{.rax=0x20007});
 try std.testing.expect(states[1].terminal and states[1].tty_signal_owner_generation==null);
 reset();launchApp();states[1].terminal=true;_=reclaimEntry();
 try std.testing.expect(states[1].tty_signal_owner_generation==null);
 reset();launchApp();resetState(&states[1]);try std.testing.expect(states[1].tty_signal_owner_generation==null);
 reset();launchApp();closeEntry();try std.testing.expect(states[1].tty_signal_owner_generation==null);
}
'''
        self.compile(source)

    def test_actual_dispatch_reaches_selected_operation_only(self):
        native=self.native()
        lines=[line for line in native.splitlines() if 'return ttySignalOperation(frame);' in line]
        self.assertEqual(len(lines),1)
        source=self.operation_source()+r'''
fn dispatch(frame:*const Frame)*const Frame{
'''+lines[0]+r'''
 result(&states[active],-38);return select();
}
test "actual SIGINT selector reaches authority gate and adjacent selector stays unsupported" {
 binding();var f:Frame=.{.rax=0x29003,.rdi=handle(1),.rsi=2};_=dispatch(&f);
 try std.testing.expectEqual(@as(u64,1),states[6].context().frame.rax);
 active=1;f.rdi=0;_=dispatch(&f);try std.testing.expectEqual(@as(i64,-13),@as(i64,@bitCast(states[1].context().frame.rax)));
 f.rax=0x29004;_=dispatch(&f);try std.testing.expectEqual(@as(i64,-38),@as(i64,@bitCast(states[1].context().frame.rax)));
}
'''
        self.compile(source)

    def test_compiling_target_generation_binding_omission_fails_actual_oracle(self):
        native=self.native()
        before='!target.app_binding.valid(slot, target.generation, target.admitted, target.terminal, target.app_binding.clock)'
        self.assertEqual(native.count(before),1)
        self.compile(self.operation_source(native.replace(before,'false',1)),expected=1)

    def test_compiling_coalesced_outcome_omission_fails_actual_oracle(self):
        source=(ROOT/'kernel/arch/x86_64/native_pending.zig').read_text()
        before='if (self.pending & 2 != 0) return 2;'
        self.assertEqual(source.count(before),1)
        with self.work.named_file(mode='w',prefix='.tty-signal-pending-',suffix='.zig',
                                  dir=ROOT/'kernel/arch/x86_64') as mutated:
            mutated.write(source.replace(before,'if (self.pending & 2 != 0) return 1;',1))
            mutated.flush()
            self.compile(self.operation_source(),pending=Path(mutated.name).name,expected=1)
