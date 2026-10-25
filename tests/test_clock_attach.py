# SPDX-License-Identifier: BSD-2-Clause
"""Execute actual clock reattachment; hardware bit updates are simulated on host."""
from pathlib import Path
import tempfile
import unittest
from test_fs_owner_data import ROOT, run
from test_native_cleanup import block


PREFIX = r'''
const std=@import("std");
const Table=[512]u64;
var source:?u8=1;
const pd_physical:u64=0x123000;
var observed_table:Table=@splat(0xcccc);
var original:u64=0;
pub const panic=std.debug.FullPanic(panicImpl);
fn unchanged() bool {
    for(observed_table,0..) |value,index| if(value!=(if(index==509) original else @as(u64,0xcccc))) return false;
    return true;
}
fn panicImpl(message:[]const u8,_:?usize) noreturn {
    if(!unchanged()) std.process.exit(92);
    std.debug.print("AETHER PANIC: {s}\n",.{message});
    std.process.exit(91);
}
'''
MAIN = r'''
pub fn main(init:std.process.Init.Minimal) void {
    const args=init.args.vector;
    if(args.len!=3) std.process.exit(64);
    const repeat=std.mem.eql(u8,std.mem.span(args[1]),"reattach");
    original=if(repeat) 0 else std.fmt.parseInt(u64,std.mem.span(args[1]),16) catch std.process.exit(64);
    source=if(std.mem.eql(u8,std.mem.span(args[2]),"1")) 1 else null;
    observed_table[509]=original;
    attach(&observed_table);
    if(repeat) {
        observed_table[509]|=32; // Model the hardware update; no device access.
        original=observed_table[509];
        attach(&observed_table);
    }
    if(observed_table[509]!=(0x123003|(original&32))) std.process.exit(92);
    for(observed_table,0..) |value,index| if(index!=509 and value!=0xcccc) std.process.exit(92);
    std.debug.print("ATTACHED\n",.{});
}
'''


class ClockAttach(unittest.TestCase):
    def test_actual_reattachment_flags_identity_source_and_compiling_controls(self):
        body=block((ROOT/'kernel/arch/x86_64/clock.zig').read_text(),'pub fn attach(')
        expected=0x123003
        cases=[(1,0),(1,expected),(1,expected|32),(0,0),(0,expected),(0,expected|32),(1,0xffffffffffffffff)]
        for accessed in (0,32):cases += [(1,(expected|accessed)^(1<<bit)) for bit in range(64)]
        variants=[('actual',body,None,None),
            ('missing-accessed',body.replace('previous & ~accessed == expected','previous == expected'),expected|32,0),
            ('user-mask',body.replace('~accessed','~(accessed | @as(u64, 1 << 2))'),expected|4,91),
            ('frame-mask',body.replace('~accessed','~(accessed | @as(u64, 1 << 14))'),expected^16384,91),
            ('lost-accessed',body.replace('expected | (previous & accessed)','expected'),expected|32,0)]
        self.assertTrue(all(source!=body for _,source,_,_ in variants[1:]))
        with tempfile.TemporaryDirectory(prefix='aether-clock-attach-') as folder:
            out=Path(folder)
            for mode in ('Debug','ReleaseSafe'):
                for name,implementation,control_input,correct_exit in variants:
                    with self.subTest(mode=mode,variant=name):
                        (out/'main.zig').write_text(PREFIX+implementation+MAIN)
                        binary=out/(name+'-'+mode)
                        run(['zig','build-exe','-O'+mode,'-Mroot='+str(out/'main.zig'),'-femit-bin='+str(binary),
                             '--cache-dir',out/'cache','--global-cache-dir',out/'global'],out)
                        if name!='actual':
                            with self.assertRaises(AssertionError) as failure:
                                run([binary,f'{control_input:x}','1'],out,correct_exit)
                            self.assertEqual(failure.exception.args[0]['exit'],{'missing-accessed':91,'user-mask':0,'frame-mask':0,'lost-accessed':92}[name])
                            continue
                        for ready,prior in cases:
                            valid=ready==1 and prior in (0,expected,expected|32)
                            with self.subTest(mode=mode,ready=ready,prior=hex(prior)):
                                text=run([binary,f'{prior:x}',str(ready)],out,0 if valid else 91)
                                self.assertEqual(text,'ATTACHED\n' if valid else 'AETHER PANIC: reached unreachable code\n')
                        self.assertEqual(run([binary,'reattach','1'],out),'ATTACHED\n')
