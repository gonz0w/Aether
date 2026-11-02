# SPDX-License-Identifier: BSD-2-Clause
"""Actual console body and build graph; host-only, no UART timing claim."""
import ast
import hashlib
import os
from pathlib import Path
import sys
import time
import unittest

from test_native_cleanup import block, compiler_file_limit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_capture import OwnedTemporaryDirectory, run_capture_bytes

SCAFFOLD = r'''
const std = @import("std");
const TtyMode = @import("tty_mode");
const Frame = struct { rax:u64=0x26004,rdi:u64=0xf001,rsi:u64=0,rdx:u64=0,r10:u64=0,r8:u64=0,r9:u64=0 };
const State = struct { admitted:bool=true,terminal:bool=false,generation:u64=3,answer:i64=123 };
var states:[4]State=@splat(.{});
var active:usize=2;
var console_closed=false;
var console_recipient:?struct{slot:usize,generation:u64}=null;
var lifecycle=true;
var frame:Frame=.{};
fn lifecycleEnabled()bool{return lifecycle;}
fn supervisorSlot()usize{return 2;}
fn result(s:*State,value:i64)void{s.answer=value;}
fn select()*const Frame{return &frame;}
fn lookup(value:u64)?usize{return if(value==9)1 else null;}
var cell:u8=0;
fn byte(_: *State,_:usize,_:bool)?*u8{return &cell;}
const serial=struct {
 var queries:usize=0;var reads:usize=0;var writes:usize=0;
 pub fn transmitterEmpty()i64{queries+=1;return -11;}
 fn readByte()error{LineError}!?u8{reads+=1;return null;}
 fn writeByte(_:u8)bool{writes+=1;return true;}
};
fn reset()void{states=@splat(.{});active=2;console_closed=false;console_recipient=null;lifecycle=true;frame=.{};serial.queries=0;serial.reads=0;serial.writes=0;}
fn invoke()i64{_=consoleOperation(&frame);return states[active].answer;}
'''
CASES = r'''
test "actual selected query checks authority and scalars before any UART observation" {
 reset();try std.testing.expectEqual(@as(i64,-11),invoke());
 try std.testing.expectEqual(@as(usize,1),serial.queries);
 try std.testing.expectEqual(@as(usize,0),serial.reads+serial.writes);
 reset();active=0;try std.testing.expectEqual(@as(i64,-13),invoke());
 try std.testing.expectEqual(@as(usize,0),serial.queries);
 reset();frame.rdi=0xf002;try std.testing.expectEqual(@as(i64,-13),invoke());
 try std.testing.expectEqual(@as(usize,0),serial.queries);
 reset();console_closed=true;try std.testing.expectEqual(@as(i64,-9),invoke());
 try std.testing.expectEqual(@as(usize,0),serial.queries);
 inline for(.{"rsi","rdx","r10","r8","r9"})|field|{
  reset();@field(frame,field)=1;try std.testing.expectEqual(@as(i64,-22),invoke());
  try std.testing.expectEqual(@as(usize,0),serial.queries);
 }
 for(0..4)|bad|{
  reset();active=1;console_recipient=.{.slot=1,.generation=3};
  switch(bad){0=>console_recipient.?.slot=0,1=>states[1].generation=4,2=>states[1].admitted=false,3=>states[1].terminal=true,else=>unreachable}
  try std.testing.expectEqual(@as(i64,-13),invoke());
  try std.testing.expectEqual(@as(usize,0),serial.queries);
 }
 reset();active=1;console_recipient=.{.slot=1,.generation=3};
 try std.testing.expectEqual(@as(i64,-11),invoke());
 try std.testing.expectEqual(@as(usize,1),serial.queries);
}
test "actual legacy close handoff and byte operations keep their contract" {
 reset();frame.rax=0x26002;try std.testing.expectEqual(@as(i64,0),invoke());
 try std.testing.expect(console_closed);try std.testing.expectEqual(@as(usize,0),serial.queries);
 reset();frame.rax=0x26003;lifecycle=false;frame.rsi=9;
 try std.testing.expectEqual(@as(i64,0),invoke());
 try std.testing.expectEqual(@as(usize,1),console_recipient.?.slot);
 try std.testing.expectEqual(@as(u64,3),console_recipient.?.generation);
 try std.testing.expectEqual(@as(i64,-13),invoke());
 reset();frame.rax=0x26003;try std.testing.expectEqual(@as(i64,-13),invoke());
 reset();frame.rax=0x26000;frame.rdx=1;try std.testing.expectEqual(@as(i64,-11),invoke());
 try std.testing.expectEqual(@as(usize,1),serial.reads);
 reset();frame.rax=0x26001;frame.rdx=1;try std.testing.expectEqual(@as(i64,1),invoke());
 try std.testing.expectEqual(@as(usize,1),serial.writes);
 try std.testing.expectEqual(@as(usize,0),serial.queries);
}
'''


class NativeTtyMode(unittest.TestCase):
    records = []

    @classmethod
    def setUpClass(cls):
        cls.deadline = time.monotonic() + 300
        cls.addClassCleanup(cls.finish)
        compiler_file_limit(cls)
        cls.work = OwnedTemporaryDirectory(prefix='aether-tty-mode-')
        cls.addClassCleanup(cls.work.cleanup)
        cls.out = Path(cls.work.name)
        cls.inputs = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
            'build.zig','kernel/arch/x86_64/native_c.zig','kernel/arch/x86_64/serial.zig',
            'kernel/native_sustained.zig','kernel/native_tty_mode.zig',
            'scripts/fs_session.py','tests/test_native_tty_mode.py')}

    @classmethod
    def finish(cls):
        if hasattr(cls, 'inputs'):
            for name, digest in cls.inputs.items():
                if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
                    raise AssertionError('TTY mode source changed: '+name)
        if time.monotonic() > cls.deadline:
            raise AssertionError('TTY mode host aggregate expired after cleanup')

    def run_command(self, argv, expected=0, marker=None):
        argv = list(map(str, argv))
        remaining = self.deadline - time.monotonic()
        self.assertGreater(remaining, 10)
        result = run_capture_bytes(argv, cwd=ROOT, timeout=min(180, remaining-10),
            deadline=self.deadline, owner=self.work,
            env={**os.environ, 'TMPDIR':str(self.out), 'LC_ALL':'C'})
        log = (result.stdout+result.stderr).decode(errors='replace')
        self.records.append(dict(argv=argv, exit=result.returncode, process=result.record,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
            stderr_sha256=hashlib.sha256(result.stderr).hexdigest(), tail=log[-2200:]))
        self.assertEqual(result.record['cleanup'], 'complete')
        self.assertTrue(result.record['group_absent'])
        if expected:
            self.assertNotEqual(result.returncode, 0, log)
        else:
            self.assertEqual(result.returncode, 0, log)
        if marker:
            self.assertIn(marker, log)
        return log

    def compile_body(self, selected=True, helper=None, expected=0, body=None):
        native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        source = SCAFFOLD + (body or block(native, 'fn consoleOperation('))
        source += CASES if selected else r'''
test "unselected query has no UART effects" {
 reset();try std.testing.expectEqual(@as(i64,-38),invoke());
 try std.testing.expectEqual(@as(usize,0),serial.queries+serial.reads+serial.writes);
}
'''
        (self.out/'test.zig').write_text(source)
        (self.out/'options.zig').write_text('pub const native_tty_mode_probe='+str(selected).lower()+';')
        command = ['zig', 'test', '--cache-dir', self.out/'cache', '--global-cache-dir',
                   self.out/'global', '--dep', 'build_options']
        helper = helper or ROOT/'kernel/native_tty_mode.zig'
        if helper.exists():
            command += ['--dep', 'tty_mode']
        command += ['-Mroot='+str(self.out/'test.zig'), '-Mbuild_options='+str(self.out/'options.zig')]
        if helper.exists():
            command += ['-Mtty_mode='+str(helper)]
        log = self.run_command(command, expected, 'FAIL' if expected else 'All ')
        self.assertNotRegex(log, r':\d+:\d+: error:')

    def test_actual_console_selected_and_legacy_behavior(self):
        self.compile_body()

    def test_actual_console_unselected(self):
        self.compile_body(False)

    def test_compiling_missing_holder_guard_fails_same_oracle(self):
        path = ROOT/'kernel/native_tty_mode.zig'
        source = path.read_text()
        before = '!guard.owns or guard.grant != 0xf001'
        self.assertEqual(source.count(before), 1)
        mutation = self.out/'missing-holder.zig'
        mutation.write_text(source.replace(before, 'guard.grant != 0xf001', 1))
        self.compile_body(helper=mutation, expected=1)

    def test_compiling_thre_instead_of_temt_fails_actual_status_oracle(self):
        path = ROOT/'kernel/native_sustained.zig'
        source = path.read_text()
        before = 'if (status & 0x40 != 0) 0 else -11'
        self.assertEqual(source.count(before), 1)
        mutation = self.out/'thre.zig'
        mutation.write_text(source.replace(before, 'if (status & 0x20 != 0) 0 else -11', 1))
        log = self.run_command(['zig','test',mutation,'--cache-dir',self.out/'cache',
            '--global-cache-dir',self.out/'global'], 1, 'FAIL')
        self.assertNotRegex(log, r':\d+:\d+: error:')
        self.assertIn('expected -11, found 0', log)

    def test_actual_dispatch_keeps_each_profile_selector_set(self):
        native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        lines = [line for line in native.splitlines() if 'return consoleOperation(frame);' in line]
        self.assertEqual(len(lines), 1)
        line = lines[0].replace('return consoleOperation(frame);', 'return true;')
        source = r'''
const std=@import("std");const TtyMode=@import("tty_mode");
const Frame=struct{rax:u64};
var console_profile=false;var console_handoff=false;
fn dispatch(frame:*const Frame)bool{
''' + line + r'''
 return false;
}
test "actual dispatch enforces selected and legacy selector sets" {
 for([_]bool{false,true})|console|for([_]bool{false,true})|handoff|{
  console_profile=console;console_handoff=handoff;
  for([_]u64{0x25fff,0x26000,0x26001,0x26002,0x26003,0x26004,0x26005})|op|{
   const expected=console and switch(op){0x26000...0x26002=>true,0x26003=>handoff,0x26004=>@import("build_options").native_tty_mode_probe,else=>false};
   try std.testing.expectEqual(expected,dispatch(&.{.rax=op}));
  }
 };
}
'''
        (self.out/'dispatch.zig').write_text(source)
        for selected in (False, True):
            (self.out/'options.zig').write_text('pub const native_tty_mode_probe='+str(selected).lower()+';')
            self.run_command(['zig','test','--cache-dir',self.out/'cache',
                '--global-cache-dir',self.out/'global','--dep','tty_mode','--dep','build_options',
                '-Mroot='+str(self.out/'dispatch.zig'),
                '-Mtty_mode='+str(ROOT/'kernel/native_tty_mode.zig'),
                '-Mbuild_options='+str(self.out/'options.zig')], marker='All ')

    def test_actual_serial_wrapper_reads_only_lsr_once_with_first_error_retention(self):
        serial = (ROOT/'kernel/arch/x86_64/serial.zig').read_text()
        source = r'''
const std=@import("std");
var input_status:@import("status").SerialStatus=.{};
var samples=[_]u8{0x23,0x60,0xff};var count:usize=0;
var receive=[_]u8{0,13,255};
fn in(port:u16)u8{
 std.debug.assert(port==0x3fd); // Any receive-data access fails the same run.
 const status=samples[count];count+=1;return status;
}
''' + block(serial, 'pub fn transmitterEmpty(') + r'''
test "actual serial wrapper keeps receive bytes and the first read-cleared error" {
 try std.testing.expectEqual(@as(i64,-11),transmitterEmpty());
 try std.testing.expectEqual(@as(usize,1),count);
 try std.testing.expectEqual(@as(u8,2),input_status.errors);
 try std.testing.expectEqual(@as(i64,0),transmitterEmpty());
 try std.testing.expectEqual(@as(usize,2),count);
 try std.testing.expectEqual(@as(u8,2),input_status.errors);
 try std.testing.expect(input_status.takeError(0));
 try std.testing.expect(!input_status.takeError(0));
 try std.testing.expectEqual(@as(i64,-5),transmitterEmpty());
 try std.testing.expectEqual(@as(usize,3),count);
 try std.testing.expectEqualSlices(u8,&.{0,13,255},&receive);
}
'''
        (self.out/'serial.zig').write_text(source)
        self.run_command(['zig','test','--cache-dir',self.out/'cache',
            '--global-cache-dir',self.out/'global','--dep','status',
            '-Mroot='+str(self.out/'serial.zig'),
            '-Mstatus='+str(ROOT/'kernel/native_sustained.zig')], marker='All ')

    def test_selected_earlier_writes_retain_errors_and_old_nonmonitoring_stays_legacy(self):
        serial = (ROOT/'kernel/arch/x86_64/serial.zig').read_text()
        source = r'''
const std=@import("std");const selected=@import("build_options").native_tty_mode_probe;
var input_status:@import("status").SerialStatus=.{};
var lsr_count:usize=0;var rx_count:usize=0;var tx_count:usize=0;
fn in(port:u16)u8{
 if(port==0x3f8){rx_count+=1;return 0x7d;}
 std.debug.assert(port==0x3fd);lsr_count+=1;
 return if(lsr_count==1)0x22 else if(lsr_count==(if(selected)@as(usize,4) else 3))0x61 else 0x60;
}
fn out(port:u16,value:u8)void{
 std.debug.assert(port==0x3f8 and value==0x41+tx_count);tx_count+=1;
}
''' + '\n'.join(block(serial, name) for name in ('fn lineStatus(', 'pub fn write(',
            'pub fn writeByte(', 'pub fn transmitterEmpty(')) + serial[serial.index('pub fn readByte('):serial.index('pub fn writeByte(')] + r'''
test "actual initial writes retain errors only in selected profile before query" {
 write(&.{0x41});try std.testing.expect(writeByte(0x42));
 try std.testing.expectEqual(@as(usize,2),lsr_count);
 try std.testing.expectEqual(@as(usize,2),tx_count);
 try std.testing.expectEqual(@as(usize,0),rx_count);
 try std.testing.expectEqual(@as(u8,if(selected)2 else 0),input_status.errors);
 try std.testing.expectEqual(selected,input_status.enabled);
 if(selected){
  try std.testing.expectEqual(@as(i64,0),transmitterEmpty());
  try std.testing.expectEqual(@as(usize,3),lsr_count);
  try std.testing.expectEqual(@as(usize,0),rx_count);
  try std.testing.expectEqual(@as(u8,2),input_status.errors);
  try std.testing.expectError(error.LineError,readByte());
 }else try std.testing.expectEqual(@as(?u8,0x7d),try readByte());
 try std.testing.expectEqual(@as(usize,1),rx_count);
 try std.testing.expectEqual(@as(u8,0),input_status.errors);
}
'''
        (self.out/'writer.zig').write_text(source)
        for selected in (True, False):
            (self.out/'options.zig').write_text('pub const native_tty_mode_probe='+str(selected).lower()+';')
            self.run_command(['zig','test','--cache-dir',self.out/'cache',
                '--global-cache-dir',self.out/'global','--dep','status','--dep','build_options',
                '-Mroot='+str(self.out/'writer.zig'),
                '-Mstatus='+str(ROOT/'kernel/native_sustained.zig'),
                '-Mbuild_options='+str(self.out/'options.zig')], marker='All ')

    def test_build_option_default_and_exact_private_closure(self):
        self.assertRegex((ROOT/'build.zig').read_text(),
            r'const native_tty_mode_probe = b.option\(bool, "native-tty-mode-probe", [^\n]+\) orelse false;')
        tree = ast.parse((ROOT/'scripts/fs_session.py').read_text())
        value = next(node.value for node in tree.body if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'FLAGS' for t in node.targets))
        flags = ast.literal_eval(value.func.value).split()
        flags += ['native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']
        image = self.out/'never-executed.bin'
        image.write_bytes(b'\0')
        base = {'smp':'false','native-c-image':str(image), **dict.fromkeys(flags,'true')}
        def invoke(options, bad=False):
            return self.run_command(['zig','build','--help','--cache-dir',self.out/'cache',
                '--global-cache-dir',self.out/'global',
                *['-D'+key+'='+value for key,value in options.items()]],
                int(bad), None if bad else 'native-tty-mode-probe')
        invoke({})
        invoke(base)
        invoke({**base,'native-tty-mode-probe':'false'})
        selected = {**base,'native-tty-mode-probe':'true'}
        invoke(selected)
        invoke({'native-tty-mode-probe':'true'}, True)
        for name in ('native-fs-session','native-fs-session-init','native-fs-owner-data',
                     'native-fs-owner-stack','native-service-channel-wait','native-process-copy',
                     'native-process-exec','native-parent-identity'):
            with self.subTest(missing=name):
                invoke({**selected,name:'false'}, True)
        for name in ('smp','release-artifact','native-mktemp-reader',
                     'native-fs-application-profile','native-service-lifetime'):
            with self.subTest(forbidden=name):
                invoke({**selected,name:'true'}, True)
        invoke({**selected,'native-af09-drain':'file_prefix'}, True)
        invoke({**base,'native-tty-mode-probe':'invalid'}, True)
