# SPDX-License-Identifier: BSD-2-Clause
"""Execute the actual panic hook; no kernel failure attribution from host output."""
from pathlib import Path
import tempfile
import unittest
from test_fs_owner_data import ROOT,run
from test_native_cleanup import block


class PanicSite(unittest.TestCase):
    def test_selected_caller_old_null_and_compiling_omission(self):
        body=block((ROOT/'kernel/main.zig').read_text(),'fn panicImpl(')
        with tempfile.TemporaryDirectory(prefix='aether-panic-site-') as folder:
            out=Path(folder)
            for name,selected,address,source in [
                ('selected',True,'0xffffffff80001234',body),('old',False,'0xffffffff80001234',body),
                ('null',True,'null',body),('omission',True,'0xffffffff80001234',body.replace('if (return_address) |address| {','if (false) { const address=return_address orelse 0;'))]:
                with self.subTest(name=name):
                    prefix='const std=@import("std");const serial=struct{fn write(text:[]const u8)void{std.debug.print("{s}",.{text});}fn halt()noreturn{std.process.exit(93);}};'
                    (out/'main.zig').write_text(prefix+source+'pub fn main()void{panicImpl("reached unreachable code",'+address+');}')
                    (out/'options.zig').write_text('pub const native_fs_owner_stack='+str(selected).lower()+';')
                    binary=out/name
                    run(['zig','build-exe','-OReleaseSafe','--dep','build_options','-Mroot='+str(out/'main.zig'),
                        '-Mbuild_options='+str(out/'options.zig'),'-femit-bin='+str(binary),'--cache-dir',out/'cache','--global-cache-dir',out/'global'],out)
                    text=run([binary],out,93)
                    expected='AETHER PANIC: reached unreachable code\n'
                    if selected and address!='null':expected='NATIVE PANIC pc=ffffffff80001234\n'+expected
                    if name=='omission':self.assertNotEqual(text,expected)
                    else:self.assertEqual(text,expected)
