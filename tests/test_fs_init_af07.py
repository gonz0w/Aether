# SPDX-License-Identifier: BSD-2-Clause
"""Separate AF07 owner intake and actual activation-oracle boundaries."""
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_init_af07 as owner
import fs_init_consumer as old
import fs_session
from test_fs_init_consumer import trace as old_trace
from test_native_cleanup import block


def trace():
    return old_trace().replace('used=1328 remaining=6864', 'used=1329 remaining=6863')


class AF07Init(unittest.TestCase):
    def test_corrected_linked_client_requires_real_boot_parent(self):
        from fs_metadata_launch import closure
        candidates=(('v1','66d8ec0f8353563a270d2f7ae2fbb9e288be2287ff08ff566e16dc4a3491a468',
                     '6265a3eb21f110f4888572987f4bc4420c9b2f6c932810567ecc369512a47c3b'),
                    ('v2','e559c2ef5a0675c6c243aa3cc517bf5c34fd78ae5ef90a8ca3f3e99b04999081',
                     '70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942'))
        compiler=Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')
        self.assertEqual(owner.digest(compiler),'625165a3accc542dafef0264b5bbd18721b8e765c7ec819742ec7d7afd2491f6')
        control=r'''/* SPDX-License-Identifier: BSD-2-Clause */
#include "fs-identity.h"
#include <stdio.h>
static void put(unsigned char *p,unsigned n){for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(n>>(8*i));}
static int probe(unsigned slot,unsigned epoch,unsigned shell,unsigned parent,long observed,int wrong_memory){
 unsigned char frame[32]="AEFSH001";put(frame+8,29);put(frame+12,7);put(frame+16,slot);put(frame+20,epoch);put(frame+24,parent);put(frame+28,shell);
 struct aether_fs_session_identity out={91,92,93};
 uint64_t memory=UINT64_C(0x40000000)|((uint64_t)epoch<<8)|(slot+1);
 int ok=aether_fs_session_decode(frame,32,memory^(unsigned)wrong_memory,epoch*7+slot+1,observed,&out);
 if(!ok&&(out.slot!=91||out.epoch!=92||out.shell_generation!=93))return -1;
 if(ok&&(out.slot!=slot||out.epoch!=epoch||out.shell_generation!=shell))return -1;
 return ok;
}
int main(void){
 for(unsigned shell=1;shell<=3;shell++)if(probe(1,shell,shell,7,7,0)!=CORRECTED)return 41;
 if(probe(1,1,1,14,7,0)!=0)return 42;
 for(unsigned parent=14;parent<=28;parent+=7)if(probe(1,1,1,parent,parent,0)!=(1-CORRECTED))return 43;
 if(probe(2,1,1,9,9,0)!=1||probe(2,1,1,7,7,0)!=0)return 44;
 if(probe(1,1,1,7,14,0)!=0||probe(1,1,1,7,7,1)!=0)return 45;
 puts("BOOT_PARENT_PROFILE_PASS");return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-af07-linked-parent-') as folder:
            out=Path(folder);(out/'identity.c').write_text(control)
            for version,outer_seal,bundle_seal in candidates:
                directory=ROOT / 'userland/build/session-deliveries'/('filesystem-abi29-linked-2026-10-21-'+version)
                closure(directory,outer_seal,580);closure(directory/'bundle',bundle_seal,574)
                args=[str(compiler),'-std=c17','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=undefined',
                      '-fno-sanitize-recover=all','-DCORRECTED='+str(int(version=='v2')),
                      '-I',str(directory/'bundle/src'),str(out/'identity.c'),'-o',str(out/'identity')]
                run=subprocess.run(args,capture_output=True,text=True,timeout=30)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
                run=subprocess.run([str(out/'identity')],capture_output=True,text=True,timeout=10)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
                self.assertEqual(run.stdout,'BOOT_PARENT_PROFILE_PASS\n')

    def test_actual_boot_owner_pid_and_copied_parent_identity(self):
        native=(ROOT/'kernel/arch/x86_64/native_c.zig').read_text()
        boot=block(native,'fn startSupervised(')
        self.assertIn('const s = &states[supervisorSlot()];',boot)
        self.assertNotIn('s.generation',boot)
        generation=next(line.strip() for line in native.splitlines() if line.strip().startswith('generation: u64 ='))
        states=next(line for line in native.splitlines() if line.startswith('var states:'))
        pid=block(native,'0x10000 + 39 => {')
        ppid=block(native,'0x10000 + 110 => {')
        copied=next(line.strip() for line in native.splitlines() if line.strip().startswith('child.parent_pid ='))
        owner=block(native,'fn supervisorSlot(')
        scaffold='''const std=@import("std");const FsRoles=@import("roles");
const combined_profile=true;const pipeline_capacity=true;const program_profile=true;const connections_profile=true;
const Frame=struct{rax:u64=0};const State=struct{'''+generation+'''parent_pid:u64=0,admitted:bool=false,frame:Frame=.{}};
'''+states+'\n'+owner+'''
var active:usize=6;
fn result(s:*State,value:i64)void{s.frame.rax=@bitCast(value);}
fn query(op:u64)i64{const s=&states[active];switch(op){'''+pid+','+ppid+''',else=>unreachable,}return @bitCast(s.frame.rax);}
fn copyParent(from:usize,slot:usize)void{const source=&states[from];const child=&states[slot];'''+copied+'''}
test "actual boot owner and first admitted/copied identities" {
 states=@splat(.{});const s=&states[supervisorSlot()];'''+next(line.strip() for line in boot.splitlines() if line.strip()=='s.admitted = true;')+'''
 active=supervisorSlot();try std.testing.expectEqual(@as(i64,7),query(0x10000+39));try std.testing.expectEqual(@as(i64,0),query(0x10000+110));
 states[1].generation=1;states[1].admitted=true;active=1;
 try std.testing.expectEqual(@as(i64,9),query(0x10000+39));try std.testing.expectEqual(@as(i64,7),query(0x10000+110));
 states[2].generation=1;copyParent(1,2);active=2;
 try std.testing.expectEqual(@as(i64,10),query(0x10000+39));try std.testing.expectEqual(@as(i64,9),query(0x10000+110));
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-af07-boot-identity-') as folder:
            out=Path(folder)
            (out/'options.zig').write_text('pub const native_parent_identity=true;pub const native_process_copy=true;pub const native_runner_local=true;')
            variants=(('actual',scaffold),('false-owner-generation',scaffold.replace(generation,'generation: u64 = 1,')),
                      ('old-domain-pid',scaffold.replace('s.generation * states.len + active + 1','s.generation * 6 + active + 1')),
                      ('lost-copied-parent',scaffold.replace(copied,'child.parent_pid = 0; _=source;')))
            for name,source in variants:
                (out/'probe.zig').write_text(source)
                args=['zig','test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),
                      '--dep','roles','--dep','build_options','-Mroot='+str(out/'probe.zig'),
                      '-Mroles='+str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig'),'-Mbuild_options='+str(out/'options.zig')]
                run=subprocess.run(args,capture_output=True,text=True,timeout=60)
                self.assertEqual(run.returncode,0 if name=='actual' else 1,run.stdout+run.stderr)
                self.assertNotRegex(run.stderr,r':\d+:\d+: error:')
                self.assertIn('passed' if name=='actual' else 'FAIL',run.stderr)

    def test_full_current_engine_and_actual_owner_intake(self):
        from fs_af07_inputs import selection
        engine=selection()['engine']
        selected=owner.intake(ROOT/engine['directory'],engine['seal'])
        self.assertEqual(selected['same_selected_engine_elf'],owner.ENGINE_ELF)
        self.assertNotEqual(selected['original_engine_manifest'],selected['selected_engine_manifest'])
        self.assertEqual(selected['owner_intake']['raw_bytes'],2072)

    def intake(self):
        # Isolate consumer verification from the separately tested engine intake.
        with patch.object(owner, 'engine_intake', return_value={'elf_sha256':owner.ENGINE_ELF}):
            return owner.intake(owner.ENGINE, owner.ENGINE_SEAL)

    def test_sealed_actual_owner_sources_tools_and_stack(self):
        result = self.intake()
        self.assertEqual(result['owner_intake']['raw_bytes'], 2072)
        self.assertEqual(result['owner_intake']['stack']['entry_stack_bytes'], 1096)
        self.assertEqual(result['protocol'], 'AFSRPC07')
        self.assertNotEqual(result['raw'], old.intake()['raw'])
        original = owner.digest
        for path in (owner.DELIVERY/'sha256.json', owner.DELIVERY/'owner.raw',
                     owner.DELIVERY/'owner.elf', owner.DELIVERY/'inputs.json',
                     ROOT / 'sys-init/prototypes/native-filesystem-af07/policy.rs',
                     owner.ENGINE/'filesystem.elf'):
            with self.subTest(path=path), patch.object(owner, 'digest',
                    side_effect=lambda p: '0'*64 if Path(p)==path else original(p)):
                with self.assertRaisesRegex(ValueError, 'input drift'):
                    self.intake()

    def test_wrong_wire_roles_bootstrap_engine_or_coverage_reject(self):
        original = owner.json.loads
        for key, value in (('wire_protocol','AFSRPC06'), ('engine_root_rights',1),
                ('bootstrap',[28]), ('roles',{}), ('profile','AENFS002/ABI28'),
                ('engine_manifest_sha256','0'*64), ('engine_elf_sha256','0'*64),
                ('native_acceptance',True)):
            def altered(data):
                result = original(data)
                if 'bootstrap' in result:
                    result = copy.deepcopy(result); result[key] = value
                return result
            with self.subTest(key=key), patch.object(owner.json,'loads',side_effect=altered):
                with self.assertRaisesRegex(ValueError,'selection/coverage'):
                    self.intake()
        with patch.object(owner,'engine_intake',return_value={'elf_sha256':'0'*64}):
            with self.assertRaisesRegex(ValueError,'rebuilt engine differs'):
                owner.intake(owner.ENGINE,owner.ENGINE_SEAL)

    def test_selected_loader_geometry_and_every_terminal_cleanup_halt_required(self):
        result = owner.trace(trace())
        self.assertEqual(result['engine_loader_pages'],1329)
        self.assertFalse(result['after_activation_file_readback'])
        self.assertNotIn('assigned_target_txg',result)
        with self.assertRaises(ValueError):owner.trace(old_trace())
        with self.assertRaises(ValueError):old.trace(trace())
        for line in trace().splitlines():
            with self.subTest(line=line):
                with self.assertRaises(ValueError):owner.trace(trace().replace(line+'\n','',1))
                with self.assertRaises(ValueError):owner.trace(trace()+line+'\n')
        witness=fs_session.metadata_oracle_witness(trace())
        self.assertEqual(owner.trace(fs_session.metadata_oracle_text(witness)),result)

    def test_private_peer_adaptation_preserves_all_non_wire_bytes(self):
        original=(ROOT/'user/storage/session/failed-peer.c').read_text()
        adapted=owner.failed_peer_source(original)
        self.assertEqual(adapted.count('AFSRPC07'),2)
        self.assertEqual(adapted.count('AFSRPC06'),1)
        self.assertEqual(adapted.replace('AFSRPC06','AFSRPC05').replace('AFSRPC07','AFSRPC06'),original)
        for value in (original+'AFSRPC06', original.replace('AFSRPC05','AFSRPC07')):
            with self.assertRaises(ValueError):owner.failed_peer_source(value)

    def test_explicit_selection_before_preparation_and_no_legacy_mixing(self):
        script=str(ROOT/'scripts/fs_session.py')
        for args in (['--metadata-sys-init-checks'],
                     ['--metadata-sys-init-checks','--sys-init'],
                     ['--metadata-sys-init-checks','--metadata-engine',str(owner.ENGINE),'--metadata-seal','bad']):
            run=subprocess.run([sys.executable,'-B',script,*args],capture_output=True,text=True,timeout=5)
            self.assertEqual(run.returncode,64)
            self.assertNotIn('[RUNNING]',run.stderr)
        with patch.object(fs_session.tempfile,'mkdtemp') as temporary:
            for kwargs in ({'metadata_sys_init_checks':True},
                    {'metadata_sys_init_checks':True,'metadata_candidate':(owner.ENGINE,owner.ENGINE_SEAL),'sys_init':True}):
                with self.assertRaises(ValueError):fs_session.campaign(**kwargs)
            temporary.assert_not_called()
