# SPDX-License-Identifier: BSD-2-Clause
"""Public source-wiring checks and host Zig fixture; no process is launched.

Run python3 -B -m unittest discover -s tests -p test_native_envelope_gate.py -v.
These public checks cover extraction/wiring only. Actual compiling scalar gate,
semantic omission and typed-parser checks use the existing private qualified
capture entry recorded in issue137. Committed public bounded_capture.py lacks
that private execution API; this file neither imports it nor adds a runner.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


def gate_guard(source):
    guards=[line.strip() for line in source.splitlines() if '@panic("native envelope oversized")' in line]
    if len(guards)!=1:raise ValueError('one actual boot-module guard required')
    if source.index(guards[0])>=source.index('@import("arch/x86_64/native_c.zig").start('):
        raise ValueError('module gate must precede native.start')
    return guards[0]


def checker_source(source,omission=None):
    guard=gate_guard(source).replace('@import("build_options")','options').replace('@import("native_fs_session.zig")','Fs')
    if omission=='old-gate':
        selected='if (options.native_fs_application_profile) Fs.application_envelope_limit else '
        if guard.count(selected)!=1:raise ValueError('exact selected profile branch required')
        guard=guard.replace(selected,'')
    elif omission=='no-gate':
        if guard.count('if (native.size >')!=1:raise ValueError('exact scalar comparison required')
        guard=guard.replace('if (native.size >','if (false and native.size >')
    elif omission is not None:raise ValueError('closed omission selection')
    guard=guard.replace('@panic("native envelope oversized")','return false')
    return r'''

const std=@import("std");const K=@import("kernel");const Fs=K.Fs;const Elf=K.Elf;const Roles=K.Roles;
const options=struct{var native_fs_application_profile=false;var native_image_large=false;};
var starts:usize=0;
fn admitted(size:u64)bool{
 const native=struct{size:u64}{.size=size};
 GUARD
 starts+=1;return true;
}
fn check(application:bool,large:bool,size:u64,expected:bool,comptime marker:[]const u8)void{
 options.native_fs_application_profile=application;options.native_image_large=large;starts=0;
 const result=admitted(size);
 if(result!=expected or starts!=@intFromBool(expected)){std.debug.print("{s}\n",.{marker});std.process.exit(91);}
}
pub fn main()void{
 const actual:u64=9081744;
 const application_cap:u64=48+Elf.large_limits.file_bytes+112+3*Elf.application_limits.file_bytes+Roles.owner_stack_code_limit;
 const large_cap:u64=8*1024*1024+4096+48;
 const ordinary_cap:u64=3*1024*1024+8192+80;
 if(application_cap!=13156512)std.process.exit(92);
 check(true,true,actual,true,"SELECTED_REAL_ENVELOPE_ADMITTED");
 check(false,false,actual,false,"ORDINARY_REAL_ENVELOPE_DENIED");
 check(false,true,actual,false,"LARGE_REAL_ENVELOPE_DENIED");
 check(true,false,actual,true,"APPLICATION_SELECTION_FIRST");
 for([_]bool{false,true})|large|{
  check(true,large,application_cap,true,"APPLICATION_EXACT_CAP");
  check(true,large,application_cap+1,false,"APPLICATION_ONE_OVER_NO_START");
  check(true,large,std.math.maxInt(u64),false,"APPLICATION_OVERFLOW_NO_START");
 }
 check(false,true,large_cap,true,"OLD_LARGE_EXACT_CAP");
 check(false,true,large_cap+1,false,"OLD_LARGE_ONE_OVER_NO_START");
 check(false,false,ordinary_cap,true,"OLD_ORDINARY_EXACT_CAP");
 check(false,false,ordinary_cap+1,false,"OLD_ORDINARY_ONE_OVER_NO_START");
 std.debug.print("NATIVE ENVELOPE GATE PASS\n",.{});
}
'''.replace('GUARD',guard)


class NativeEnvelopeGateSource(unittest.TestCase):
    def test_actual_application_branch_precedes_unchanged_older_limits(self):
        source=(ROOT/'kernel/main.zig').read_text();guard=gate_guard(source)
        self.assertLess(guard.index('native_fs_application_profile'),guard.index('native_image_large'))
        self.assertIn('@import("native_fs_session.zig").application_envelope_limit',guard)
        self.assertIn('8 * 1024 * 1024 + 4096 + 48',guard)
        self.assertIn('3 * 1024 * 1024 + 8192 + 80',guard)
        self.assertIn('NATIVE ENVELOPE GATE PASS',checker_source(source))

    def test_fixture_refuses_missing_duplicate_reordered_guard_or_unknown_omission(self):
        source=(ROOT/'kernel/main.zig').read_text();guard=gate_guard(source)
        for changed in (source.replace(guard,''),source+'\n'+guard,source.replace(guard,'')+'\n'+guard):
            with self.assertRaises(ValueError):gate_guard(changed)
        with self.assertRaises(ValueError):checker_source(source,'unknown')


if __name__=='__main__':unittest.main()
