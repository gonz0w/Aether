# SPDX-License-Identifier: BSD-2-Clause
"""Separate16384 admission/stack/mapping controls; no sys-init acceptance."""
from pathlib import Path
import json
import re
import struct
import subprocess
import sys
import tempfile
import unittest

from test_native_cleanup import block
from test_fs_session import envelope, small_elf, ROOT
sys.path.insert(0, str(ROOT/'scripts'))
import fs_session
import owner_stack


class InitOwner(unittest.TestCase):
    def test_actual_old_new_parser_boundaries_magic_and_all_rejected_inputs(self):
        engine=(ROOT/'.deps/fs-launch-2026-10-20-v4/filesystem.elf').read_bytes()
        with tempfile.TemporaryDirectory(prefix='aether-fs-init-parse-') as folder:
            out=Path(folder)
            cases=[]
            for wide in (False, True):
                for length in (1,8192,8193,12289,15120,16384,16385,24576):
                    raw=envelope(engine,controller=length)
                    if wide: raw=b'AENFS003'+raw[8:]
                    name=f'{wide}-{length}.bin';(out/name).write_bytes(raw)
                    for selected in (False,True):
                        expression=f'c.parseProfile(@embedFile("{name}"),{str(selected).lower()})'
                        valid=wide==selected and length <= (16384 if selected else 8192)
                        cases.append(' _=try '+expression+';' if valid else ' try std.testing.expectError(error.InvalidComposition,'+expression+');')
            for name,raw in [('reserved',b'AENFS003'+envelope(engine)[8:]),('process',b'AENFS003'+envelope(engine,[small_elf(113*4096),small_elf(),small_elf()])[8:])]:
                if name=='reserved':
                    data=bytearray(raw);data[48+len(engine)+24]=1;raw=bytes(data)
                (out/(name+'.bin')).write_bytes(raw)
                cases.append(' try std.testing.expectError(error.InvalidComposition,c.parseProfile(@embedFile("'+name+'.bin"),true));')
            (out/'test.zig').write_text('const std=@import("std");const c=@import("composition");test "explicit fixed bounds and profile mismatch" {\n'+'\n'.join(cases)+'\n}')
            r=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'--dep','composition','-Mroot='+str(out/'test.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')],capture_output=True,text=True,timeout=90)
            self.assertEqual(r.returncode,0,r.stderr)

    def test_actual_four_page_mapping_all_seven_aliases_zero_tail_stack_nx(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        check=block(native,'    if (init_large or connections_large or @import("build_options").native_service_activation) {')
        check=check.replace('@panic("native init code tail not zeroed");','failed=true;')
        scaffold='''const std=@import("std");const nx:u64=1<<63;const init_large=false;const connections_large=false;
const Page=struct{address:usize=0,flags:u64=0};
const State=struct{pages:[5]Page=@splat(.{}),backing:[4][4096]u8=@splat(@splat(0)),aliases:[4]u64=@splat(0)};
var states:[7]State=@splat(.{});var failed=false;
fn require(ok:bool)void{failed=failed or !ok;}
fn backingFrame(_: *State,i:usize)u64{return 0x100000+i*4096;}
fn backingAliasEntry(mapping:*State,_:*State,i:usize)u64{return mapping.aliases[i];}
fn checkMappings(s:*State)void{const supervisor_code=struct{len:usize}{.len=15120};'''+check+'''}
test "four code pages with complete alias tail and stack guards" {
 for(0..5)|mode|{
  states=@splat(.{});failed=false;const s=&states[6];
  for(0..4)|i|{s.pages[i]=.{.address=0x400000+i*4096,.flags=5};for(&states)|*m|m.aliases[i]=backingFrame(s,i)|1|nx;}
  s.pages[4]=.{.address=0x800000,.flags=7|nx};
  switch(mode){0=>{},1=>s.pages[3].flags=7,2=>states[5].aliases[3]|=2,3=>s.backing[3][2832]=1,4=>s.pages[4].flags=7,else=>unreachable,}
  checkMappings(s);try std.testing.expectEqual(mode!=0,failed);
 }
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-fs-init-map-') as folder:
            out=Path(folder);(out/'options.zig').write_text('pub const native_service_activation=true;')
            for name,source in [('positive',scaffold),('omitted-last-page',scaffold.replace('for (s.pages[0..code_pages],','for (s.pages[0..code_pages-1],')),('omitted-tail',scaffold.replace('failed=true;','failed=failed;'))]:
                (out/'test.zig').write_text(source)
                r=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'--dep','build_options','-Mroot='+str(out/'test.zig'),'-Mbuild_options='+str(out/'options.zig')],capture_output=True,text=True,timeout=60)
                self.assertEqual(r.returncode,0 if name=='positive' else 1,r.stderr)
                self.assertNotRegex(r.stderr,r':\d+:\d+: error:')

    def test_stack_inspector_rejects_dynamic_unknown_recursive_and_excess_edges(self):
        good='''0000000000400000 <_start>:
 400000: push rbp
 400001: sub rsp, 0x100
 400005: call 0x400100 <worker>
 40000a: ret
0000000000400100 <worker>:
 400100: push r12
 400102: sub rsp, 0x80
 400106: ret
'''
        self.assertEqual(owner_stack.inspect(good)['entry_stack_bytes'],664)
        for bad in (good.replace('call 0x400100 <worker>','call rax'),good.replace('sub rsp, 0x100','sub rsp, rax'),good.replace('sub rsp, 0x100','mov rsp, rax'),good.replace('sub rsp, 0x100','pop rsp'),good.replace('sub rsp, 0x100','sub rsp, 0x1000'),good.replace('400106: ret','400106: call 0x400000 <_start>'),good.replace('call 0x400100 <worker>','call 0x401000 <unknown>')):
            with self.assertRaises(ValueError):owner_stack.inspect(bad)

    def test_wide_controller_actual_rust_readonly_witness_and_corruption_control(self):
        source=(ROOT/'user/storage/session/wide.rs').read_text()
        with tempfile.TemporaryDirectory(prefix='aether-fs-init-wide-') as folder:
            out=Path(folder)
            for name,selected in [('positive',source),('corrupt',source.replace('(i % 251) as u8','(i % 249) as u8',1))]:
                (out/'test.rs').write_text(selected+'\n#[test] fn all_bytes(){assert!(verify(),"FOUR_PAGE_BYTES");}\n')
                r=subprocess.run(['rustc','+1.98.0','--edition=2024','--test',str(out/'test.rs'),'-o',str(out/'test')],capture_output=True,text=True,timeout=60)
                self.assertEqual(r.returncode,0,r.stderr)
                r=subprocess.run([str(out/'test')],capture_output=True,text=True)
                self.assertEqual(r.returncode,0 if name=='positive' else 101,r.stdout+r.stderr)

    def test_trace_profile_cannot_invent_or_omit_four_page_witness(self):
        from test_fs_session import FilesystemComposition
        old=FilesystemComposition().trace()
        wide=re.sub(r'(NATIVE observation slot=6 generation=0 offset=)(\d+)',lambda m:m[1]+str(int(m[2])+8),old)
        wide='NATIVE observation slot=6 generation=0 offset=0 byte=87\n'+wide
        self.assertEqual(fs_session.writer_trace(wide,True)['profile'],'AENFS003/owner29/engine26')
        for text,selected in ((old,True),(wide,False),(wide.replace('byte=87','byte=0'),True)):
            with self.assertRaises(ValueError):fs_session.writer_trace(text,selected)

    def test_new_build_selector_rejects_missing_combined_or_release_before_runtime(self):
        common=['zig','build','--help','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'-Dnative-fs-session-init=true']
        for args in ([],['-Drelease-artifact=true']):
            r=subprocess.run(common+args,capture_output=True,text=True,timeout=60)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('filesystem init owner requires the combined profile',r.stderr)
