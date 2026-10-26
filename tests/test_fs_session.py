# SPDX-License-Identifier: BSD-2-Clause
"""Actual combined parser and fixed geometry; no native acceptance from host."""
from pathlib import Path
import struct
import re
import subprocess
import tempfile
import unittest
from test_native_cleanup import block
from test_fs_launch_intake import runtime_fixture

ROOT = Path(__file__).resolve().parents[1]


def small_elf(memsz=4096):
    raw = bytearray(4096)
    raw[:8] = b'\x7fELF\x02\x01\x01\0'
    struct.pack_into('<HHIQQQIHHHHHH', raw, 16, 2, 62, 1, 0x200200, 64, 0, 0, 64, 56, 4, 0, 0, 0)
    for i, row in enumerate(((6,4,64,0x200040,0x200040,224,224,8),
                             (1,5,0,0x200000,0x200000,4096,memsz,4096),
                             (7,4,768,0x200300,0x200300,4,4,4),
                             (0x6474e551,6,0,0,0,0,0,16))):
        struct.pack_into('<IIQQQQQQ',raw,64+56*i,*row)
    return bytes(raw)


def envelope(engine, images=None, controller=1):
    images = images or [small_elf()]*3
    nested = struct.pack('<8sIIIIQ',b'AENMX009',*[len(p) for p in images],controller,0)+bytes(range(80))
    nested += b''.join(images)+bytes(controller)
    return struct.pack('<8sII',b'AENFS002',len(engine),len(nested))+bytes(range(32))+engine+nested


class FilesystemSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-fs-session-',dir='/private/tmp')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.source = ROOT/'kernel/native_fs_session.zig'
        cls.engine = (ROOT/'.deps/fs-launch-2026-10-20-v4/filesystem.elf').read_bytes()
        cls.cases = {'valid':envelope(cls.engine)}
        for name, offset, data in (
                ('old_magic',0,b'AENBD004'),('zero_engine',8,bytes(4)),
                ('zero_session',12,bytes(4)),('wrong_nested',48+len(cls.engine),b'AENMX008'),
                ('reserved_nested',48+len(cls.engine)+24,b'\x01')):
            raw=bytearray(cls.cases['valid']);raw[offset:offset+len(data)]=data;cls.cases[name]=bytes(raw)
        cls.cases['truncated']=cls.cases['valid'][:-1]
        cls.cases['tail']=cls.cases['valid']+b'\0'
        cls.cases['oversized_process']=envelope(cls.engine,[small_elf(113*4096),small_elf(),small_elf()])
        cls.cases['oversized_owner']=envelope(cls.engine,controller=8193)
        cls.cases['malformed_process']=envelope(cls.engine,[b'bad',small_elf(),small_elf()])
        for name,data in cls.cases.items(): (cls.out/(name+'.bin')).write_bytes(data)

    def compile_run(self, source=None, expected=0):
        tests = 'const std=@import("std");const c=@import("composition");\ntest "actual combined exact envelope and rejected boundaries" {\n'
        tests += runtime_fixture(self.out/'valid.bin', self.cases['valid'],
            'const good=try c.parse(fixture);\n'
            'try std.testing.expectEqualStrings("AENMX009",fixture[48+good.engine.len..][0..8]);\n'
            'try std.testing.expectEqual(@as(usize,80),good.session.entropy.len);\n'
            'try std.testing.expectEqual(@as(usize,32),good.engine_entropy.len);')
        for name, data in self.cases.items():
            if name != 'valid':
                tests += runtime_fixture(self.out/(name+'.bin'), data,
                    'if (c.parse(fixture)) |_| return error.COMPOSITION_ACCEPTED_' + name +
                    ' else |err| try std.testing.expectEqual(error.InvalidComposition, err);')
        tests += '}\n'
        (self.out/'test.zig').write_text(tests)
        run=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),
            '--global-cache-dir',str(ROOT/'.zig-cache/global'),'--dep','composition',
            '-Mroot='+str(self.out/'test.zig'),'-Mcomposition='+str(source or self.source),'-femit-bin='+str(self.out/'parser-tests')],
            capture_output=True,text=True,timeout=60)
        self.assertEqual(run.returncode,expected,run.stdout+run.stderr)
        return run.stdout+run.stderr

    def test_actual_parser_real_engine_and_all_rejected_closures(self):
        self.compile_run()

    def test_compiling_omissions_fail_process_size_owner_size_and_exact_session_oracles(self):
        original=self.source.read_text()
        for old,new,marker in (
            ('if (bundle.supervisor.len > limit)', 'if (false)', 'oversized_owner'),
            ('elf.parse(process_bytes)', 'elf.parseWithLimits(process_bytes, elf.large_limits)', 'oversized_process'),
            ('if (!std.mem.eql(u8, nested[0..8], if (profile == .application) "AENMX011" else if (profile == .owner_stack) "AENMX010" else "AENMX009"))', 'if (false)', 'wrong_nested'),
        ):
            with self.subTest(omission=old):
                self.assertEqual(original.count(old),1)
                # Same package root preserves original relative imports. Owned
                # transient source is removed immediately, never evidence/archive.
                with tempfile.NamedTemporaryFile(mode='w',suffix='.zig',prefix='fs-session-omission-',
                                                  dir=ROOT/'kernel',delete=False) as stream:
                    path=Path(stream.name);stream.write(original.replace(old,new,1))
                try:
                    log=self.compile_run(path,expected=1)
                    self.assertIn('FAIL',log)
                    self.assertIn('FAIL (COMPOSITION_ACCEPTED_' + marker + ')', log)
                    self.assertNotRegex(log, r':\d+:\d+: error:')
                finally: path.unlink()


class FilesystemRoleOperations(unittest.TestCase):
    def test_actual_admission_exec_copy_and_both_block_delegation_bodies(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        prefixes={}
        for name,anchor in [('exec','    if (f.rax == 0x23008)'),('copy','    const reader = ownedChannel'),('launch','    var raw: [launch.record_size]u8')]:
            text=block(native,'fn '+name+'Operation(')
            prefixes[name]=text[:text.index(anchor)]+(block(text,'if (failure != 0)') if name=='launch' else '')+('    _=s;\n' if name=='exec' else '')+'    effects+=1; result(caller,77); return select();\n}'
        # Both actual delegations: the older whole-device path must not bypass
        # the new region path's role restriction. Execute their complete bodies.
        for op in ('27003','27005'):
            branch=block(native,'if (f.rax == 0x'+op+')')
            prefixes[op]='fn block'+op+'(f:*const Frame)*const Frame{const s=&states[active];'+branch+'return select();}'
        source='\n'.join(prefixes.values())
        scaffold=r"""
const std=@import("std");const FsRoles=@import("roles");const combined_profile=true;
const Frame=struct{rax:u64=0,rdi:u64=0,rsi:u64=0,rdx:u64=0,r10:u64=0,r8:u64=0,r9:u64=0};
const State=struct{terminal:bool=false,frozen:bool=true,admitted:bool=false,generation:u64=1,freeze_sequence:u64=1,image_commit:struct{pending:bool=false}=.{},frame:Frame=.{}};
var states:[7]State=@splat(.{});var active:usize=6;var effects:usize=0;
var block_base:u64=0;var block_count:u64=2097160;var block_rights:u64=7;
var block_recipient:?struct{slot:usize,generation:u64}=null;
var scratch:[24]u8=@splat(0);
const program_profile=true;
fn supervisorSlot()usize{return 6;}fn workerCount()usize{return 6;}
fn processSlot(s:usize)bool{return FsRoles.process(s);}fn threadedSlot(s:usize)bool{return FsRoles.threaded(s);}
fn lifetimeLimit()u64{return 15;}
fn lookup(h:u64)?usize{if(h>=100 and h<106 and states[@intCast(h-100)].admitted)return @intCast(h-100);return null;}
fn result(s:*State,v:i64)void{s.frame.rax=@bitCast(v);}fn select()*const Frame{return &states[active].frame;}
fn ownedChannel(_:usize,_:u64)?u8{return null;}
fn byte(_: *State,at:usize,_:bool)?*u8{return if(at<24)&scratch[at] else null;}
fn code(f:*const Frame)i64{return @bitCast(f.rax);}
fn reset()void{states=@splat(.{});states[0].admitted=true;states[1].admitted=true;active=6;effects=0;block_base=0;block_count=2097160;block_rights=7;block_recipient=null;std.mem.writeInt(u64,scratch[0..8],8,.little);std.mem.writeInt(u64,scratch[8..16],2097152,.little);std.mem.writeInt(u64,scratch[16..24],7,.little);}
"""
        cases=r"""
test "process preflights deny engine without effects; actual authority and stale lookup retained" {
 reset();
 try std.testing.expectEqual(@as(i64,-13),code(execOperation(&.{.rdi=0xa001,.rsi=100})));
 try std.testing.expectEqual(@as(i64,-9),code(execOperation(&.{.rdi=0xa001,.rsi=99})));
 active=1;try std.testing.expectEqual(@as(i64,-13),code(execOperation(&.{.rdi=0xa001,.rsi=101})));
 active=6;try std.testing.expectEqual(@as(i64,-13),code(execOperation(&.{.rdi=0xa002,.rsi=101})));
 try std.testing.expectEqual(@as(usize,0),effects);
 try std.testing.expectEqual(@as(i64,77),code(execOperation(&.{.rdi=0xa001,.rsi=101})));
 effects=0;
 try std.testing.expectEqual(@as(i64,-13),code(launchOperation(&.{.rdi=0xa001,.rsi=0xc001,.rdx=0})));
 try std.testing.expectEqual(@as(i64,-13),code(launchOperation(&.{.rdi=0xa001,.rsi=0xc001,.rdx=6})));
 try std.testing.expectEqual(@as(usize,0),effects);
 states[1].admitted=false;try std.testing.expectEqual(@as(i64,77),code(launchOperation(&.{.rdi=0xa001,.rsi=0xc001,.rdx=1})));
 reset();states[0].admitted=false;
 try std.testing.expectEqual(@as(i64,-95),code(copyOperation(&.{.rdi=0xa001,.rsi=101,.rdx=0,.r10=1})));
 states[0].admitted=true;states[2].admitted=false;
 try std.testing.expectEqual(@as(i64,-95),code(copyOperation(&.{.rdi=0xa001,.rsi=100,.rdx=2,.r10=1})));
 try std.testing.expectEqual(@as(usize,0),effects);
 try std.testing.expectEqual(@as(i64,77),code(copyOperation(&.{.rdi=0xa001,.rsi=101,.rdx=2,.r10=1})));
}
test "both block delegation operations deny process roles before changing authority" {
 for([_]u64{0x27003,0x27005})|op|{
  reset();const f=Frame{.rax=op,.rdi=0xf101,.rsi=101,.rdx=if(op==0x27003)7 else 0,.r10=if(op==0x27003)0 else 24};
  const out=if(op==0x27003)block27003(&f) else block27005(&f);
  try std.testing.expectEqual(@as(i64,-13),code(out));
  try std.testing.expect(block_recipient==null and block_base==0 and block_count==2097160 and block_rights==7);
  var engine=f;engine.rsi=100;
  const good=if(op==0x27003)block27003(&engine) else block27005(&engine);
  try std.testing.expectEqual(@as(i64,0),code(good));try std.testing.expectEqual(@as(usize,0),block_recipient.?.slot);
 }
}
"""
        variants=[('positive',source),('exec-role',source.replace('!processSlot(slot)','false',1)),('launch-role',source.replace('!processSlot(@intCast(f.rdx))','false',1)),('copy-role',source.replace('!processSlot(slot)','false',1)),('block-role',source.replace('combined_profile and slot != FsRoles.engine_slot','false'))]
        # Select each exact operation when making omissions (the combined source
        # also contains the copy slot guard before launch's separate guard).
        variants[3]=('copy-role',source.replace('threadedSlot(from) or !processSlot(from) or !processSlot(slot)','threadedSlot(from) or !processSlot(from) or false',1))
        with tempfile.TemporaryDirectory(prefix='aether-fs-role-') as d:
            out=Path(d);(out/'options.zig').write_text('pub const native_signal_actions=false;pub const native_copy_signals=true;pub const native_process_exec=true;pub const native_exec_copy=false;')
            for name,selected in variants:
                with self.subTest(name=name):
                    (out/'test.zig').write_text(scaffold+selected+cases)
                    run=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'--dep','roles','--dep','build_options','-Mroot='+str(out/'test.zig'),'-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),'-Mbuild_options='+str(out/'options.zig')],capture_output=True,text=True,timeout=60)
                    self.assertEqual(run.returncode,0 if name=='positive' else 1,run.stderr)
                    self.assertNotRegex(run.stderr,r':\d+:\d+: error:',run.stderr)

class FilesystemComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        import fs_session
        cls.profile=fs_session

    def trace(self):
        lines=['NATIVE MEMORY admitted slot=0 generation=1 used=1328 remaining=6864',
               'NATIVE observation slot=6 generation=0 offset=0 byte=82',
               'NATIVE MEMORY admitted slot=1 generation=1 used=25 remaining=103',
               'NATIVE MEMORY admitted slot=1 generation=1 used=26 remaining=102']
        for slot,pages,prior in ((1,128,0),(0,8192,1)):
            if slot==0:
                raw=b'PT'+(799).to_bytes(8,'little')
                lines += [f'NATIVE observation slot=6 generation=0 offset={(i+1)*8} byte={b}' for i,b in enumerate(raw)]
            lines.append(f'NATIVE terminal slot={slot} generation=1 kind=1 detail=0')
            lines += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+(phase==7)}' for phase in range(1,8)]
        lines.append('NATIVE observation slot=6 generation=0 offset=88 byte=67')
        for slot,generation in ((0,1),(6,0)):
            lines += [f'NATIVE STORAGE WAIT slot={slot} generation={generation} phase={phase} status=0' for phase in ('park','wake')]
        return '\n'.join(lines)+'\nNATIVE init halted ticks=5123 idle=3 reclaimed=2\nAETHER NATIVE BLOCK PASS\n'

    def test_exact_two_role_trace_and_missing_wrong_stale_fault_cleanup_or_wait_reject(self):
        text=self.trace()
        self.assertEqual(self.profile.writer_trace(text)['assigned_target_txg'],799)
        for changed in (text.replace('phase=4','phase=5',1),text.replace('pages=128','pages=8192',1),text.replace('selected=6','selected=2',1),text.replace('detail=0','detail=1',1),text.replace('reclaimed=2','reclaimed=3'),text.replace('ticks=5123','ticks=6001'),text.replace('byte=82','byte=0'),text.replace('slot=6 generation=0 offset=0','slot=2 generation=0 offset=0'),text.replace('phase=wake','phase=park'),text+'NATIVE fault vector=6\n',text.replace('AETHER NATIVE BLOCK PASS','')):
            with self.subTest(changed=changed[-60:]):
                with self.assertRaises(ValueError): self.profile.writer_trace(changed)

    def test_actual_channel_create_body_keeps_factories_quotas_and_holders_separate(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        branch=block(block(native,'fn channelOperation('),'if (f.rax == 0x24000)').replace('@import("../../native_channel.zig")','C')
        source='''const std=@import("std");const C=@import("channel");const FsRoles=@import("roles");
const Frame=struct{rax:u64=0x24000,rdi:u64=0,rsi:u64=0,rdx:u64=0,r10:u64=0,r8:u64=0,r9:u64=0};
const State=struct{frame:Frame=.{},fn context(s:*@This())*@This(){return s;}};
var states:[7]State=@splat(.{});var channels:[12]C.Channel=@splat(.{});var active:usize=6;
const combined_profile=true;const sustained=false;const pipeline_session=true;
fn supervisorSlot()usize{return 6;}fn channelCount()usize{return 12;}fn lifetimeLimit()u64{return 15;}
fn result(s:*State,v:i64)void{s.frame.rax=@bitCast(v);}fn select()*const Frame{return &states[active].frame;}fn publishSustained()void{}
fn create(f:*const Frame)*const Frame{const s=&states[active];'''+branch+'''return select();}
fn code(f:*const Frame)i64{return @bitCast(f.rax);}
test "actual factory disjoint exhaustion and nonholder denial" {
 for(&channels,0..)|*c,i|c.identity=i+1;
 active=1;try std.testing.expectEqual(@as(i64,-13),code(create(&.{.rdi=0xd002})));
 active=6;try std.testing.expectEqual(@as(i64,-13),code(create(&.{.rdi=0xd003})));
 for(channels)|c|try std.testing.expectEqual(@as(u64,0),c.generation);
 for(0..2)|i|{const h=code(create(&.{.rdi=0xd002}));try std.testing.expect(h>0);try std.testing.expect(channels[10+i].lookup(6,@intCast(h))==0);}
 try std.testing.expectEqual(@as(i64,-16),code(create(&.{.rdi=0xd002})));
 for(channels[0..10])|c|try std.testing.expectEqual(@as(u64,0),c.generation);
 for(0..10)|i|{const h=code(create(&.{.rdi=0xd001}));try std.testing.expect(h>0);try std.testing.expect(channels[i].lookup(6,@intCast(h))==0);}
 try std.testing.expectEqual(@as(i64,-16),code(create(&.{.rdi=0xd001})));
 const r=channels[10].cap(0);const w=channels[11].cap(1);
 try std.testing.expect(C.connectionPair(channels[0..10],6,r,w)==null);
 try std.testing.expect(C.connectionPair(channels[10..12],6,r,w)!=null);
 try std.testing.expect(C.connectionPair(channels[10..12],1,r,w)==null);
 for(&channels)|*c|{c.closeOwner(6);c.generation=3;}
 try std.testing.expectEqual(@as(i64,-28),code(create(&.{.rdi=0xd002})));
 try std.testing.expect(code(create(&.{.rdi=0xd001}))>0);
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-fs-channel-') as d:
            path=Path(d)/'test.zig';path.write_text(source)
            r=subprocess.run(['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'--dep','channel','--dep','roles','-Mroot='+str(path),'-Mchannel='+str(ROOT/'kernel/native_channel.zig'),'-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig')],capture_output=True,text=True,timeout=60)
            self.assertEqual(r.returncode,0,r.stderr)

    def test_combined_build_closure_and_old_incompatibility_guards(self):
        selected=['zig','build','--help','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),'-Dsmp=false','-Dnative-c-image='+str(ROOT/'.deps/fs-launch-2026-10-20-v4/filesystem.elf')]
        cases=[([f for f in self.profile.FLAGS if f!=missing],[]) for missing in ('native-fs-session','native-service-activation','native-service-zpl-budget','native-session-lifecycle')]
        cases += [(self.profile.FLAGS,['-Drelease-artifact=true'])]
        for flags,extra in cases:
            with self.subTest(missing=set(self.profile.FLAGS)-set(flags),extra=extra):
                r=subprocess.run(selected+['-D'+f+'=true' for f in flags]+extra,capture_output=True,text=True,timeout=60)
                self.assertNotEqual(r.returncode,0)
                self.assertIn('panic',r.stderr)

    def test_recovery_refuses_legacy_writer_guessed_counts_and_unconfirmed_stop(self):
        from unittest.mock import patch
        writer=dict(self.profile.writer_trace(self.trace()),status='pass',vm_run_returned=True,disk_sha256='1'*64)
        with patch.object(self.profile,'written_native_media_snapshot',return_value={'sha256':'1'*64}) as snapshot:
            self.profile.recovery_media(writer,Path('/unused'))
            self.assertEqual(snapshot.call_args.args,(Path('/unused'),'1'*64))
            for change in ({'profile':'AENBD004/ABI26'},{'vm_run_returned':False},{'reclaimed':3},{'admitted_instances':3},{'engine_terminal_zero':False},{'status':'failed'},{'disk_sha256':''}):
                with self.assertRaises(ValueError): self.profile.recovery_media({**writer,**change},Path('/unused'))
            self.assertEqual(snapshot.call_count,1)
        reader=dict(status='pass',vm_run_returned=True,reclaimed=3,generations=3,final_live_workers=0,cleanup_trace_version=1,cleanup_boundaries_per_generation=7,readonly_pool_retired=True,namespace_bytes_verified=780248,recovered_pool_txg=801,disk_sha256='1'*64)
        self.assertTrue(self.profile.qualify_pair(writer,reader)['fresh_vm_readback_qualified'])
        for change in ({'reclaimed':2},{'recovered_pool_txg':798},{'disk_sha256':'2'*64},{'namespace_bytes_verified':4096},{'readonly_pool_retired':False}):
            with self.assertRaises(ValueError): self.profile.qualify_pair(writer,{**reader,**change})

    def test_native_reader_selector_cannot_raise_watchdog_or_bypass_fresh_media_check(self):
        from unittest.mock import patch
        import native_smoke
        with tempfile.TemporaryDirectory(prefix=self.profile.PREFIX,dir=ROOT/'zig-out') as d:
            parent=Path(d);(parent/'reader').mkdir();image=parent/'reader/aether.iso'
            disk=parent/'native-namespace.raw'
            with disk.open('wb') as stream:stream.truncate(1024**3+8192)
            args=dict(_fs_session_writer={},_pair_stop=True,block_disk=disk,block_large=True,block_namespace=True,marker=b'AETHER NATIVE BLOCK PASS')
            for change in ({'_zpl_writer_60s':True},{'_storage_lifetime':True},{'zpl_writer':{}},{'expected_panic':b'x'},{'_pair_stop':False}):
                with self.assertRaises(ValueError): native_smoke.run(image,**{**args,**change})
            with patch.object(self.profile,'recovery_media',side_effect=ValueError('COMBINED_MEDIA_REQUIRED')) as media:
                with self.assertRaisesRegex(ValueError,'COMBINED_MEDIA_REQUIRED'):native_smoke.run(image,**args)
                self.assertEqual(media.call_count,1)

    def test_controller_adaptation_changes_only_fixed_witness_factory_and_slot_denial(self):
        with tempfile.TemporaryDirectory(prefix='aether-fs-adapt-') as d:
            out=Path(d);self.profile.adapt_clients(out)
            source=(out/'service-client.rs').read_text()
            original=(ROOT/'user/storage/service-runtime/fs-service-client.rs').read_text()
            source=source.replace('0xd002','0xd001').replace('factory, 1, self.request, self.reply).0 == -13','factory, 1, self.request, self.reply).0 == -12')
            parent=ROOT/'user/storage/service-runtime'
            original=re.sub(r'#\[path = "([^"]+)"\]',lambda m:'#[path = '+__import__('json').dumps(str((parent/m[1]).resolve()))+']',original)
            source=source.replace(str(out/'directories.rs'),str(parent/'fs-directories-client.rs'))
            self.assertEqual(source,original)
            self.assertEqual((out/'directories.rs').read_text().replace('\n                super::super::witness(txg);',''),(parent/'fs-directories-client.rs').read_text())


    def test_native_process_trap_zeros_reserved_registers_in_actual_compiled_ir(self):
        import json
        sdk=ROOT/'.deps/native-current/sdk'
        tools=json.loads((sdk/'tools.lock.json').read_text())['tools']
        original=(ROOT/'user/storage/session/process.c').read_text()
        with tempfile.TemporaryDirectory(prefix='aether-fs-trap-') as d:
            out=Path(d)
            for name,source in [('positive',original),('wrong-reserved',original.replace('r8 __asm__("r8") = 0','r8 __asm__("r8") = 1',1))]:
                self.assertNotEqual(source,original) if name!='positive' else None
                path=out/(name+'.c');path.write_text(source)
                r=subprocess.run([tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root'),'-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include'),'-S','-emit-llvm',str(path),'-o',str(out/'probe.ll')],capture_output=True,text=True,timeout=30)
                self.assertEqual(r.returncode,0,r.stderr)
                lines=[line for line in (out/'probe.ll').read_text().splitlines() if 'asm sideeffect "int $$0x81"' in line]
                self.assertEqual(len(lines),4)
                correct=all(line.split(') #')[0].endswith('i64 0, i64 0') for line in lines)
                self.assertEqual(correct,name=='positive','actual scalar trap reserved-register oracle')


if __name__ == '__main__':
    unittest.main()
