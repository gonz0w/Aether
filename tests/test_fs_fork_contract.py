# SPDX-License-Identifier: BSD-2-Clause
"""Execute native publication/freeze bodies; no native scheduler or FD clone."""
import hashlib
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest

from test_native_cleanup import block, af09_prelude, af09_command

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = []

SCAFFOLD = r'''
const std = @import("std");
const session_lifecycle = false;
const Frame = struct { rax:u64=0, rdi:u64=0, rsi:u64=0, rdx:u64=0, r10:u64=0, r8:u64=0, r9:u64=0 };
const Execution = struct { frame:Frame=.{}, fp:[16]u8=@splat(0), fs:u64=0, tls_base:u64=0, tls_bytes:u64=0, signal_mask:u64=0 };
const State = struct {
    execution:Execution=.{}, frozen:bool=false, terminal:bool=false, admitted:bool=false,
    freeze_sequence:u64=0, generation:u64=0, parent_pid:u64=0, memory_cap:u64=0,
    channel_cap:u64=0, channel_reply_cap:u64=0, image_commit:struct{pending:bool=false}=.{},
};
var states:[7]State=@splat(.{});
var active:usize=6;
var protected:usize=0;
var transferred:usize=0;
var publishing:bool=false;
const Channel = struct {
    expected:u64,
    fn transfer(self:*Channel, owner:usize, grant:u64, child:usize)bool {
        std.debug.assert(owner==6 and grant==self.expected and child==2);
        std.debug.assert(protected==7 and states[1].frozen and !states[2].admitted);
        transferred+=1;
        return true;
    }
};
var channels=[_]Channel{.{.expected=0x21},.{.expected=0x22}};
fn supervisorSlot()usize{return 6;}
fn processSlot(slot:usize)bool{return slot>=1 and slot<=5;}
fn threadedSlot(_:usize)bool{return false;}
fn lookup(h:u64)?usize{return if(h>=101 and h<=105 and states[@intCast(h-100)].admitted) @intCast(h-100) else null;}
fn handle(slot:usize)u64{return 100+slot;}
fn result(s:*State,v:i64)void{s.execution.frame.rax=@bitCast(v);}
fn aliases(_: *State, writable:bool)void{std.debug.assert(!writable and transferred==0);protected+=1;}
fn require(ok:bool)void{std.debug.assert(ok);}
fn rotate()void{}
fn publishSustained()void{unreachable;}
fn select()*const Frame{
    if(publishing){
        // A scheduler can choose either admitted process at this boundary.
        std.debug.assert(states[2].admitted and !states[1].frozen and transferred==2);
        std.debug.assert(states[1].execution.frame.rax==10 and states[6].execution.frame.rax==102);
    }
    return &states[active].execution.frame;
}
fn code(f:*const Frame)i64{return @bitCast(f.rax);}
fn reset()void{states=@splat(.{});active=6;protected=0;transferred=0;publishing=false;states[1].admitted=true;states[1].generation=1;}
'''

CASES = r'''
test "publication grants identity and resume are visible before scheduler" {
    reset();
    states[1].frozen=true;
    states[1].channel_cap=0x11;states[1].channel_reply_cap=0x12;
    states[1].execution=.{.frame=.{.rax=999,.rdi=0x40000102,.rsi=0x11,.rdx=0x12},
        .fs=1234,.tls_base=4096,.tls_bytes=80,.signal_mask=77,.fp=@splat(91)};
    const original=states[1].execution;
    publishing=true;
    try std.testing.expectEqual(@as(i64,102),code(publication(&.{.r8=0x21,.r9=0x22})));
    const child=&states[2];
    try std.testing.expectEqual(@as(u64,1),child.generation);
    try std.testing.expectEqual(@as(u64,9),child.parent_pid);
    try std.testing.expectEqual(@as(u64,0),child.execution.frame.rax);
    try std.testing.expectEqual(@as(u64,0x40000103),child.execution.frame.rdi);
    try std.testing.expectEqual(@as(u64,0x21),child.execution.frame.rsi);
    try std.testing.expectEqual(@as(u64,0x22),child.execution.frame.rdx);
    try std.testing.expectEqual(child.memory_cap,child.execution.frame.rdi);
    try std.testing.expectEqual(child.channel_cap,child.execution.frame.rsi);
    try std.testing.expectEqual(child.channel_reply_cap,child.execution.frame.rdx);
    try std.testing.expectEqual(original.fs,child.execution.fs);
    try std.testing.expectEqual(original.tls_base,child.execution.tls_base);
    try std.testing.expectEqual(original.tls_bytes,child.execution.tls_bytes);
    try std.testing.expectEqual(original.signal_mask,child.execution.signal_mask);
    try std.testing.expectEqualSlices(u8,&original.fp,&child.execution.fp);
    try std.testing.expectEqual(@as(u64,0x11),states[1].channel_cap);
    try std.testing.expectEqual(@as(u64,0x12),states[1].channel_reply_cap);
}
test "freeze observation exact thaw token and native cancellation EAGAIN" {
    reset();active=1;
    try std.testing.expectEqual(@as(i64,-11),code(freezeOperation(&.{.rax=0x23003})));
    try std.testing.expect(states[1].frozen);
    active=6;
    try std.testing.expectEqual(@as(i64,1),code(freezeOperation(&.{.rax=0x23004,.rdi=101})));
    try std.testing.expectEqual(@as(i64,-9),code(freezeOperation(&.{.rax=0x23005,.rdi=101,.rsi=2})));
    try std.testing.expect(states[1].frozen);
    try std.testing.expectEqual(@as(i64,0),code(freezeOperation(&.{.rax=0x23005,.rdi=101,.rsi=1})));
    try std.testing.expect(!states[1].frozen);
    try std.testing.expectEqual(@as(i64,-11),code(&states[1].execution.frame));
    try std.testing.expectEqual(@as(i64,0),code(freezeOperation(&.{.rax=0x23004,.rdi=101})));
    try std.testing.expectEqual(@as(i64,-16),code(freezeOperation(&.{.rax=0x23005,.rdi=101,.rsi=1})));
}
test "foreign owner and pending exec do not thaw source" {
    reset();states[1].frozen=true;states[1].freeze_sequence=3;states[1].execution.frame.rax=555;
    active=2;
    try std.testing.expectEqual(@as(i64,-13),code(freezeOperation(&.{.rax=0x23005,.rdi=101,.rsi=3})));
    active=6;states[1].image_commit.pending=true;
    try std.testing.expectEqual(@as(i64,-16),code(freezeOperation(&.{.rax=0x23005,.rdi=101,.rsi=3})));
    try std.testing.expect(states[1].frozen and states[1].execution.frame.rax==555);
}
'''


class TaggedForkNativeContract(unittest.TestCase):
    def test_publication_and_freeze_contract_with_semantic_controls(self):
        native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        copy = block(native, 'fn copyOperation(')
        tail = copy[copy.index('    child.generation = prior_generation + 1;'):]
        publication = '''fn publication(f:*const Frame)*const Frame{
const caller=&states[active];const from:usize=1;const slot:usize=2;
const source=&states[from];const child=&states[slot];const prior_generation=child.generation;
const reader=&channels[0];const writer=&channels[1];
''' + tail
        freeze = block(native, 'fn freezeOperation(')
        actual = publication + '\n' + freeze
        mutations = (
            ('parent-left-frozen', 'source.frozen = false;', 'source.frozen = true;'),
            ('wrong-child-grant', 'child.execution.frame.rdi = child.memory_cap;', 'child.execution.frame.rdi = source.memory_cap;'),
            ('wrong-parent-identity', 'child.parent_pid = source.generation * states.len + from + 1;', 'child.parent_pid = 0;'),
            ('ignore-thaw-token', '(f.rsi == 0 or f.rsi != source.freeze_sequence)', '(false)'),
        )
        variants = [('actual', actual)]
        for name, old, new in mutations:
            self.assertIn(old, actual)
            variants.append((name, actual.replace(old, new, 1)))
        compiler = shutil.which('zig')
        self.assertIsNotNone(compiler, 'Zig runner required')
        with tempfile.TemporaryDirectory(prefix='aether-fork-contract-') as folder:
            out = Path(folder)
            options = out/'options.zig'
            options.write_text('pub const native_signal_actions=false;pub const native_copy_signals=true;pub const native_freeze_skip_park=false;pub const native_process_exec=true;pub const native_freeze_ignore_token=false;')
            for name, selected in variants:
                with self.subTest(variant=name):
                    source = out/'contract.zig'
                    source.write_text(SCAFFOLD + af09_prelude(native) + selected + CASES)
                    argv = [compiler, 'test', '--cache-dir', str(out/'cache'), '--global-cache-dir', str(out/'global'),
                            '--dep', 'build_options', '-Mroot='+str(source), '-Mbuild_options='+str(options)]
                    argv = af09_command(argv)
                    process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                    try:
                        stdout, stderr = process.communicate(timeout=60)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        stdout, stderr = process.communicate(timeout=5)
                        self.fail('Zig compile/test watchdog: '+name)
                    finally:
                        COMMANDS.append(dict(variant=name, argv=argv, timeout_seconds=60,
                            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                            options_sha256=hashlib.sha256(options.read_bytes()).hexdigest(), exit=process.returncode,
                            stdout_sha256=hashlib.sha256(stdout).hexdigest(), stderr_sha256=hashlib.sha256(stderr).hexdigest(),
                            stderr_tail=stderr[-4000:].decode(errors='replace'), process_stopped=process.poll() is not None))
                    log = stderr.decode(errors='replace')
                    self.assertNotRegex(log, r':\d+:\d+: error:', log)
                    if name == 'actual':
                        self.assertEqual(process.returncode, 0, log)
                        self.assertIn('All 3 tests passed.', log)
                    else:
                        self.assertNotEqual(process.returncode, 0, log)
                        self.assertTrue('FAIL' in log or 'assert' in log.lower(), log)
                        self.assertIn('contract.zig:', log)
                        expected = {
                            'parent-left-frozen': 'states[2].admitted and !states[1].frozen',
                            'wrong-child-grant': 'expected 1073742083, found 0',
                            'wrong-parent-identity': 'expected 9, found 0',
                            'ignore-thaw-token': 'expected -9, found 0',
                        }
                        self.assertIn(expected[name], log)


if __name__ == '__main__':
    unittest.main()
