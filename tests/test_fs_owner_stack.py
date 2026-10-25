# SPDX-License-Identifier: BSD-2-Clause
"""Selected ABI31 stack mapping uses actual producer bodies; no hardware claim."""
from pathlib import Path
import tempfile
import unittest
from test_fs_owner_data import ROOT, SCAFFOLD, run
from test_native_cleanup import block
from test_fs_session import envelope, small_elf


class OwnerStack(unittest.TestCase):
    def test_actual_guarded_stack_zeroing_nx_entry_and_old_profile(self):
        native = (ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        source = '\n'.join(block(native, name) for name in (
            'fn addPage(', 'fn byte(', 'fn mapOwnerStack(', 'fn mapOwnerData(', 'fn ownerDataStartup(', 'fn auditOwnerStack('))
        source += '''
fn setup(s:*State)void{
 for(0..4)|i|addPage(s,0x400000+i*4096,5);
 mapOwnerStack(s);mapOwnerData(s);ownerDataStartup(&s.context().frame);
}
test "guarded stack and data use exactly existing owner backing" {
 states=@splat(.{});const s=&states[6];setup(s);
 const stack_pages:usize=if(combined_owner_stack)2 else 1;
 try std.testing.expectEqual(@as(usize,4+stack_pages+2),s.count);
 for(0..stack_pages)|i|{
  const address=0x800000+i*4096;
  for(s.backing[4+i])|v|try std.testing.expectEqual(@as(u8,if(combined_owner_stack)0 else 0xa5),v);
  try std.testing.expectEqual(backingFrame(s,4+i)|7|nx,pte(s,address));
  try std.testing.expect(byte(s,address,true)!=null and byte(s,address+4095,true)!=null);
 }
 try std.testing.expectEqual(@as(u64,0),pte(s,0x7ff000));
 try std.testing.expectEqual(@as(u64,0),pte(s,0x800000+stack_pages*4096));
 try std.testing.expectEqual(@as(u64,if(combined_owner_stack)31 else 30),s.execution.frame.rdi);
 try std.testing.expectEqual(@as(u64,if(combined_owner_stack)0x802000-8 else 0x801000-8),s.execution.frame.rsp);
 for(0..2)|i|{
  try std.testing.expectEqual(backingFrame(s,4+stack_pages+i)|7|nx,pte(s,0x900000+i*4096));
  for(s.backing[4+stack_pages+i])|v|try std.testing.expectEqual(@as(u8,0),v);
 }
 for(s.backing[0..4])|page|for(page)|v|try std.testing.expectEqual(@as(u8,0xa5),v);
 for(states[0..6])|*peer|{
  try std.testing.expectEqual(@as(usize,0),peer.count);
  try std.testing.expectEqual(@as(u64,0),pte(peer,0x800000));
 }
 try std.testing.expectEqual(@as(u64,0),s.memory_cap);
 auditOwnerStack(s,4);
}
'''
        variants = [('selected',True,source),('old',False,source)]
        for name,before,after in [
            ('zeroing','@memset(&s.backing[s.count], 0);','{}'),
            ('nx','addPage(s, 0x800000 + i * 4096, 7 | nx);','addPage(s, 0x800000 + i * 4096, 7);'),
            ('second-page','if (combined_owner_stack) 2 else 1','if (combined_owner_stack) 1 else 1'),
            ('entry-top','if (combined_owner_stack) frame.rsp = 0x802000 - 8;','{}'),
        ]:
            self.assertIn(before,source)
            variants.append((name,True,source.replace(before,after,1)))
        with tempfile.TemporaryDirectory(prefix='aether-owner-stack-') as folder:
            out=Path(folder)
            for name,selected,body in variants:
                with self.subTest(name=name):
                    (out/'options.zig').write_text('pub const selected=true;')
                    scaffold=SCAFFOLD.replace('const combined_owner_stack=false;',
                        'const combined_owner_stack='+str(selected).lower()+';')
                    (out/'test.zig').write_text(scaffold+body)
                    log=run(['zig','test','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                        '--dep','roles','--dep','options','-Mroot='+str(out/'test.zig'),
                        '-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),
                        '-Moptions='+str(out/'options.zig')],out,0 if name in ('selected','old')else 1)
                    self.assertNotRegex(log,r':\d+:\d+: error:')
                    if name not in ('selected','old'):self.assertIn('FAIL',log)

    def test_actual_boot_frame_is_consumed_by_rust_validator(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        assignment=next(line.strip() for line in block(native,'fn startSupervised(').splitlines()
            if line.strip().startswith('s.context().frame = .{'))
        constants={'combined_profile','combined_init','combined_owner_data','combined_owner_stack',
            'block_profile','launch_profile','channel_profile','program_profile'}
        names='combined_profile combined_init combined_owner_data combined_owner_stack block_profile launch_profile channel_profile program_profile console_profile console_relay connections_console pipeline_console pipeline_capacity sustained session_lifecycle init_large block_regions connections_profile connections_large init_composed coexist_profile init_profile file_profile io_profile pipeline_session console_handoff'.split()
        declarations='\n'.join('const '+name+'='+str(name in constants).lower()+';' for name in names)
        source='const std=@import("std");const Frame=@import("context").Frame;const FsRoles=@import("roles");'+declarations
        source+='fn require(ok:bool)void{std.debug.assert(ok);}'
        source+=block(native,'fn storageLifetime(')+block(native,'fn ownerDataStartup(')
        source+='test "exact kernel bootstrap scalars"{var frame:Frame='+assignment.split(' = ',1)[1]
        source+='ownerDataStartup(&frame);try std.testing.expectEqual(@as(u64,0x802000-8),frame.rsp);'
        source+='const words=[_]u64{frame.rdi,frame.rsi,frame.rdx,frame.rcx,frame.r8,frame.r9,frame.r10,frame.r11};'
        source+='for(words)|value|std.debug.print("ENTRY {x}\\n",.{value});}'
        with tempfile.TemporaryDirectory(prefix='aether-owner-entry-') as folder:
            out=Path(folder)
            (out/'test.zig').write_text(source)
            (out/'options.zig').write_text('pub const native_service_lifetime=false;pub const native_service_channel_wait=true;pub const native_service_channel=true;')
            log=run(['zig','test','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                '--dep','context','--dep','roles','--dep','build_options','-Mroot='+str(out/'test.zig'),
                '-Mcontext='+str(ROOT/'kernel/arch/x86_64/context.zig'),
                '-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),
                '-Mbuild_options='+str(out/'options.zig')],out)
            import re
            words=[int(value,16) for value in re.findall(r'ENTRY ([0-9a-f]+)',log)]
            self.assertEqual(len(words),8)
            (out/'consumer.rs').write_text('''#[path="'''+str(ROOT/'sys-init/prototypes/native-filesystem-session/owner_region.rs')+'''"]mod region;
#[test]fn actual_producer_matches_consumer(){let words='''+repr(words)+''';assert!(region::validate_stack(words).is_ok());
for i in 0..8{let mut wrong=words;wrong[i]^=1;assert!(region::validate_stack(wrong).is_err());}
let mut wrong=words;wrong[5]=0xe002;assert!(region::validate_stack(wrong).is_err());assert!(region::validate(words).is_err());}
''')
            run(['rustc','+1.98.0','--edition=2024','--test',out/'consumer.rs','-o',out/'consumer'],out)
            run([out/'consumer'],out)

    def test_exact_selected_parser_and_old_budget_rejections(self):
        with tempfile.TemporaryDirectory(prefix='aether-owner-stack-parser-') as folder:
            out=Path(folder)
            checks=[]
            parsers=['c.parse(raw)','c.parseProfile(raw,true)','c.parseOwnerData(raw)','c.parseOwnerStack(raw)']
            for profile,magic in enumerate((b'AENFS002',b'AENFS003',b'AENFS004',b'AENFS005')):
                for length in (1,8192,8193,16384,16385,39376,49152,49153):
                    for wrong in (False,True):
                        raw=bytearray(envelope(small_elf(),controller=length))
                        raw[:8]=magic
                        nested=48+4096
                        raw[nested:nested+8]=b'AENMX010' if (profile==3)^wrong else b'AENMX009'
                        name=f'{profile}-{length}-{wrong}.bin'
                        (out/name).write_bytes(raw)
                        checks.append('{const raw=@embedFile("'+name+'");')
                        for selected,expression in enumerate(parsers):
                            valid=selected==profile and not wrong and length<=(8192,16384,16384,49152)[selected]
                            checks.append('_=try '+expression+';' if valid else 'try std.testing.expectError(error.InvalidComposition,'+expression+');')
                        checks.append('}')
            (out/'test.zig').write_text('const std=@import("std");const c=@import("composition");test "no implicit ABI or budget upgrade"{'+''.join(checks)+'}')
            run(['zig','test','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                '--dep','composition','-Mroot='+str(out/'test.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')],out)

    def test_explicit_build_selection_requires_owner_data(self):
        with tempfile.TemporaryDirectory(prefix='aether-owner-stack-selector-') as folder:
            out=Path(folder)
            log=run(['zig','build','--help','--cache-dir',out/'cache','--global-cache-dir',out/'global',
                '-Dnative-fs-owner-stack=true'],out,expected=1)
            self.assertIn('filesystem owner stack requires the separate data profile',log)


if __name__=='__main__':unittest.main()
