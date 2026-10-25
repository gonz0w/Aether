# SPDX-License-Identifier: BSD-2-Clause
"""Bounded ABI30 boot placement; actual mapping bodies, not hardware execution."""
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest

from test_native_cleanup import block
from test_fs_session import envelope, small_elf

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = []


def run(argv, folder, expected=0):
    """Own compiler groups and retain bounded command results for the caller."""
    argv = list(map(str, argv))
    record = {"argv": argv, "expected": expected, "timeout_seconds": 60}
    COMMANDS.append(record)
    process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True,
                               env={**os.environ, "LC_ALL": "C", "TMPDIR": str(folder)})
    try:
        output, errors = process.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        output, errors = process.communicate()
        record["timeout"] = True
        raise
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            record["group_complete"] = True
        else:
            record["group_complete"] = False
    record.update(exit=process.returncode,
                  stdout_sha256=hashlib.sha256(output).hexdigest(),
                  stderr_sha256=hashlib.sha256(errors).hexdigest(),
                  stdout_tail=output.decode(errors="replace")[-3000:],
                  stderr_tail=errors.decode(errors="replace")[-3000:])
    if process.returncode != expected or not record["group_complete"]:
        raise AssertionError(record)
    return (output + errors).decode(errors="replace")


SCAFFOLD = r'''
const std=@import("std");
const FsRoles=@import("roles");
const combined_profile=true;
const combined_init=true;
const combined_owner_data=@import("options").selected;
const combined_owner_stack=false;
const nx:u64=1<<63;
const Page=struct{address:usize=0,flags:u64=0};
const Frame=struct{rsp:u64=0x801000-8,rdi:u64=29,rsi:u64=0xa001,rdx:u64=0xf101,rcx:u64=0xc002,r8:u64=0xd001,r9:u64=0xe002,r10:u64=0,r11:u64=0};
const Context=struct{frame:Frame=.{}};
const State=struct{
 pages:[128]Page=@splat(.{}),backing:[128][4096]u8=@splat(@splat(0xa5)),count:usize=0,
 pt_index:[4]usize=@splat(0),pt_count:usize=0,pts:[4][512]u64=@splat(@splat(0)),pd:[512]u64=@splat(0),
 memory_cap:u64=0,execution:Context=.{},
 fn context(s:*State)*Context{return &s.execution;}
};
var states:[7]State=@splat(.{});
fn supervisorSlot()usize{return 6;}
fn require(ok:bool)void{std.debug.assert(ok);}
fn phys(p:anytype)u64{return @intFromPtr(p)&~@as(u64,4095);}
fn backingFrame(s:*State,i:usize)u64{
 const slot=(@intFromPtr(s)-@intFromPtr(&states[0]))/@sizeOf(State);
 // Same disjoint partition geometry, with no dereference of synthetic frames.
 return 0x10000000+(8192+(slot-1)*128+i)*4096;
}
fn pte(s:*State,address:usize)u64{
 for(s.pt_index[0..s.pt_count],0..)|index,i|if(index==address/(2*1024*1024))return s.pts[i][address/4096%512];
 return 0;
}
'''
CASES = r'''
test "selected owner alone has zeroed private data with exact RW NX PTEs and holes" {
 states=@splat(.{});const s=&states[6];
 setup(s);
 try std.testing.expectEqual(@as(usize,if(combined_owner_data) 7 else 5),s.count);
 for(s.backing[0..5])|page|for(page)|value|try std.testing.expectEqual(@as(u8,0xa5),value);
 for(0..2)|i|{
  const address=0x900000+i*4096;
  if(combined_owner_data){
   try std.testing.expectEqual(backingFrame(s,5+i)|7|nx,pte(s,address));
   for(s.backing[5+i])|value|try std.testing.expectEqual(@as(u8,0),value);
   try std.testing.expectEqual(@as(u8,0),byte(s,address+4095,false).?.*);
   byte(s,address+4095,true).?.*=0x6e;
   try std.testing.expectEqual(@as(u8,0x6e),s.backing[5+i][4095]);
  }else try std.testing.expectEqual(@as(u64,0),pte(s,address));
 }
 try std.testing.expectEqual(@as(u64,0),pte(s,0x8ff000));
 try std.testing.expectEqual(@as(u64,0),pte(s,0x902000));
 try std.testing.expect(byte(s,0x8fffff,true)==null and byte(s,0x902000,true)==null);
 try std.testing.expect(byte(s,0x400000,true)==null);
 try std.testing.expectEqual(@as(u64,0),s.memory_cap);
 for(states[0..6])|*peer|{
  try std.testing.expectEqual(@as(usize,0),peer.count);
  try std.testing.expectEqual(@as(u64,0),pte(peer,0x900000));
  for(peer.backing[0])|value|try std.testing.expectEqual(@as(u8,0xa5),value);
 }
}
test "trusted entry binds only selected ABI30 and preserves existing grants" {
 states=@splat(.{});const s=&states[6];setup(s);const f=s.context().frame;
 try std.testing.expectEqual(@as(u64,if(combined_owner_data) 30 else 29),f.rdi);
 try std.testing.expectEqual(@as(u64,if(combined_owner_data) 0x900000 else 0),f.r10);
 try std.testing.expectEqual(@as(u64,if(combined_owner_data) 8192 else 0),f.r11);
 try std.testing.expectEqual(@as(u64,0xa001),f.rsi);try std.testing.expectEqual(@as(u64,0xf101),f.rdx);
 try std.testing.expectEqual(@as(u64,0xc002),f.rcx);try std.testing.expectEqual(@as(u64,0xd001),f.r8);
 try std.testing.expectEqual(@as(u64,0xe002),f.r9);
}
'''


class OwnerData(unittest.TestCase):
    def test_actual_mapping_startup_old_profile_and_compiling_semantic_controls(self):
        native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        start = block(native, 'fn startSupervised(')
        maps = start[start.index('    for (0..(supervisor_code.len + 4095)'):start.index('    copy(s, 0x400000, supervisor_code);')]
        binding = '    ownerDataStartup(&s.context().frame);'
        self.assertEqual(start.count(binding), 1)
        actual = '\n'.join(block(native, name) for name in (
            'fn addPage(', 'fn byte(', 'fn mapOwnerStack(', 'fn mapOwnerData(', 'fn ownerDataStartup('))
        actual += '\nfn setup(s:*State)void{const supervisor_code=struct{len:usize}{.len=16384};\n'+maps+binding+'\n}\n'
        omissions = (
            ('zeroing', '@memset(&s.backing[s.count], 0);\n        addPage(s, FsRoles.owner_data_base', '{}\n        addPage(s, FsRoles.owner_data_base'),
            ('nx', 'addPage(s, FsRoles.owner_data_base + i * 4096, 7 | nx);', 'addPage(s, FsRoles.owner_data_base + i * 4096, 7);'),
            ('mapping', 'if (combined_owner_data) mapOwnerData(s);', '{}'),
            ('entry-binding', 'ownerDataStartup(&s.context().frame);', '{}'),
        )
        variants = [('selected', True, actual), ('old-profile', False, actual)]
        for label, before, after in omissions:
            self.assertEqual(actual.count(before), 1)
            variants.append((label, True, actual.replace(before, after, 1)))
        with tempfile.TemporaryDirectory(prefix='aether-owner-data-') as folder:
            out = Path(folder)
            for label, selected, source in variants:
                with self.subTest(variant=label):
                    (out/'options.zig').write_text('pub const selected='+str(selected).lower()+';')
                    (out/'probe.zig').write_text(SCAFFOLD+source+CASES)
                    log = run(['zig', 'test', '--cache-dir', out/'cache',
                               '--global-cache-dir', out/'global', '--dep', 'roles',
                               '--dep', 'options', '-Mroot='+str(out/'probe.zig'),
                               '-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),
                               '-Moptions='+str(out/'options.zig')], out,
                              0 if label in ('selected', 'old-profile') else 1)
                    self.assertNotRegex(log, r':\d+:\d+: error:')
                    if label not in ('selected', 'old-profile'):
                        self.assertIn('FAIL', log)
                        self.assertIn('TestExpectedEqual', log)

    def test_exact_new_parser_preserves_old_profiles_and_bounds(self):
        with tempfile.TemporaryDirectory(prefix='aether-owner-data-parse-') as folder:
            out = Path(folder)
            checks = []
            parsers = ['c.parse(raw)', 'c.parseProfile(raw,true)', 'c.parseOwnerData(raw)']
            for profile, magic in enumerate((b'AENFS002', b'AENFS003', b'AENFS004')):
                for length in (1, 8192, 8193, 16384, 16385):
                    data = envelope(small_elf(), controller=length)
                    data = magic+data[8:]
                    name = f'{profile}-{length}.bin'
                    (out/name).write_bytes(data)
                    checks.append('{const raw=@embedFile("'+name+'");')
                    for selected, expression in enumerate(parsers):
                        valid = selected == profile and length <= (8192 if selected == 0 else 16384)
                        checks.append('_=try '+expression+';' if valid else 'try std.testing.expectError(error.InvalidComposition,'+expression+');')
                    checks.append('}')
            source = 'const std=@import("std");const c=@import("composition");test "exact independent selection and unchanged code budgets"{'+''.join(checks)+'}'
            (out/'test.zig').write_text(source)
            run(['zig', 'test', '--cache-dir', out/'cache', '--global-cache-dir', out/'global',
                 '--dep', 'composition', '-Mroot='+str(out/'test.zig'),
                 '-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')], out)

    def test_new_selector_denies_incomplete_and_release_compositions(self):
        with tempfile.TemporaryDirectory(prefix='aether-owner-data-guard-') as folder:
            out = Path(folder)
            common = ['zig', 'build', '--help', '--cache-dir', out/'cache',
                      '--global-cache-dir', out/'global', '-Dnative-fs-owner-data=true']
            for flags, error in (
                    ([], 'filesystem owner data requires the separate init profile'),
                    (['-Dnative-fs-session-init=true'], 'filesystem init owner requires the combined profile'),
                    (['-Dnative-fs-session-init=true', '-Dnative-fs-session=true', '-Drelease-artifact=true'], 'filesystem SESSION requires its exact private BSP writer and process closure')):
                with self.subTest(flags=flags):
                    log = run(common+flags, out, expected=1)
                    self.assertIn(error, log)
