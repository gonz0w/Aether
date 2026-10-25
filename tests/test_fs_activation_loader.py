# SPDX-License-Identifier: BSD-2-Clause
"""Execute the actual selected envelope and mapping checks, with host trap substitutes."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_native_cleanup import block

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = '''
const std=@import("std");
const service_bytes:[128]u8=undefined;
const nx:u64=1<<63;
const init_large=false;
const connections_large=false;
const Page=struct{address:usize=0,flags:u64=0};
const State=struct{pages:[3]Page=@splat(.{}),backing:[3][4096]u8=@splat(@splat(0)),aliases:[2]u64=@splat(0)};
var states:[2]State=@splat(.{});
var failed=false;
fn require(ok:bool) void {failed=failed or !ok;}
fn backingFrame(_: *State,i:usize) u64{return 0x100000+i*4096;}
fn backingAliasEntry(mapping:*State,_:*State,i:usize) u64{return mapping.aliases[i];}
fn fillEnvelope(data:[]u8,engine:u32,driver:u32) void {
 @memset(data,0);std.mem.writeInt(u32,data[8..12],engine,.little);std.mem.writeInt(u32,data[12..16],driver,.little);
}
'''
CASES = '''
test "selected exact code bounds preserve old envelope closure" {
 const limit:usize=if(@import("build_options").native_service_activation)8192 else 4096;
 var data:[48+128+8193]u8=undefined;
 for([_]usize{0,1,4095,4096,4097,8191,8192,8193}) |length| {
  fillEnvelope(&data,128,@intCast(length));
  try std.testing.expectEqual(length>0 and length<=limit,supervisedEnvelopeValid(data[0..48+128+length]));
 }
 for(0..48) |length| try std.testing.expect(!supervisedEnvelopeValid(data[0..length]));
 for([_]u32{0,129,0xffffffff}) |engine| {fillEnvelope(&data,engine,1);try std.testing.expect(!supervisedEnvelopeValid(&data));}
 fillEnvelope(&data,128,1);try std.testing.expect(!supervisedEnvelopeValid(data[0..176]));try std.testing.expect(!supervisedEnvelopeValid(data[0..178]));
}
fn setup() *State {
 states=@splat(.{});failed=false;const s=&states[0];
 s.pages=.{.{.address=0x400000,.flags=5},.{.address=0x401000,.flags=5},.{.address=0x800000,.flags=7|nx}};
 for(&states) |*mapping| for(0..2) |i| {mapping.aliases[i]=backingFrame(s,i)|1|nx;};
 return s;
}
test "actual second code page stack aliases and zero tail" {
 const expected=@import("build_options").native_service_activation;
 for(0..8) |mode| {
  const s=setup();
  switch(mode){
   0=>{},1=>s.pages[1].flags=7,2=>s.pages[1].flags=5|nx,
   3=>s.pages[1].address=0x402000,4=>s.pages[2].flags=7,
   5=>states[1].aliases[1]|=2,6=>s.backing[1][85]=0xa5,
   7=>s.pages[2].address=0x801000,else=>unreachable,
  }
  mappings(s,4181);
  try std.testing.expectEqual(expected and mode!=0,failed);
 }
}
'''


class Loader(unittest.TestCase):
    def test_actual_envelope_mapping_checks_and_compiling_omissions(self):
        text = (ROOT / 'kernel/arch/x86_64/native_c.zig').read_text()
        gate = block(text, 'fn supervisedEnvelopeValid(')
        mapping = block(text, '    if (init_large or connections_large or @import("build_options").native_service_activation) {')
        # Substitute only the native failure trap so denied metadata can be
        # asserted in-process; original predicates/loops/memory accesses execute.
        mapping = mapping.replace('@panic("native init code tail not zeroed");', 'failed=true;')
        variants = [('old', False, gate, mapping), ('activation', True, gate, mapping),
                    ('limit-omitted', True, gate.replace('supervisor_len <= limit', 'supervisor_len <= limit * 2'), mapping),
                    ('flags-omitted', True, gate, mapping.replace('page.flags == 5', '(page.flags & 1 != 0)')),
                    ('tail-omitted', True, gate, mapping.replace('failed=true;', 'failed=failed;'))]
        with tempfile.TemporaryDirectory(prefix='aether-activation-loader-') as directory:
            out = Path(directory)
            for name, selected, admission, checks in variants:
                with self.subTest(name=name):
                    options = out / 'options.zig'
                    options.write_text('pub const native_service_activation=' + str(selected).lower() + ';')
                    source = out / (name + '.zig')
                    source.write_text(SCAFFOLD + admission + '\nfn mappings(s:*State,supervisor_len:usize) void {\nconst supervisor_code=struct{len:usize}{.len=supervisor_len};\n' + checks + '\n}\n' + CASES)
                    result = subprocess.run(['zig', 'test', '--cache-dir', str(ROOT / '.zig-cache'),
                        '--global-cache-dir', str(ROOT / '.zig-cache/global'), '--dep', 'build_options',
                        '-Mroot=' + str(source), '-Mbuild_options=' + str(options)],
                        capture_output=True, text=True, timeout=120)
                    if name in ('old', 'activation'):
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertNotRegex(result.stderr, r':\d+:\d+: error:', result.stderr)
                        self.assertIn('TestExpectedEqual', result.stderr)


if __name__ == '__main__':
    unittest.main()
