# SPDX-License-Identifier: BSD-2-Clause
"""Borrowed userland Rust/C metadata and explicit read-only composition."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_metadata as selected


class Binding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-fs-metadata-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.out = Path(cls.temporary.name)
        cls.inputs = json.loads((ROOT / 'userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json').read_text())
        cls.tools = cls.inputs['tools']
        for tool in cls.tools.values():
            if hashlib.sha256(Path(tool['path']).read_bytes()).hexdigest() != tool['sha256']:
                raise RuntimeError('metadata tool pin: '+tool['path'])
        for path, digest in (cls.inputs['rust_native_libraries'] | cls.inputs['clang_resource_headers']).items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
                raise RuntimeError('metadata dependency pin: '+path)
        cls.binding = selected.BINDING.read_text()
        cls.sdk = subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        cls.run_command([cls.tools['clang']['path'],'-std=c11','-O2','-Wall','-Wextra','-Werror',
            '-isysroot',cls.sdk,'-I'+str(selected.VOLUME),'-c',ROOT/'tests/fixtures/fs_metadata.c','-o',cls.out/'fixture.o'])

    @classmethod
    def run_command(cls, args, expected=0):
        env = dict(os.environ)
        if Path(args[0]).name in ('rustc','rustfmt','clippy-driver'):
            env['DYLD_LIBRARY_PATH'] = str(Path(cls.tools['rustc']['path']).parent.parent/'lib')
        result = subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=60,env=env)
        if result.returncode != expected:
            raise AssertionError(str(args)+'\n'+result.stdout+result.stderr)
        return result.stdout+result.stderr

    @classmethod
    def compile(cls, body, label, tool='rustc'):
        source = cls.out/(label+'.rs')
        source.write_text(body)
        wrapper = cls.out/(label+'-tests.rs')
        wrapper.write_text('#[path = '+json.dumps(str(source))+']\nmod metadata;\n'
            +'#[path = '+json.dumps(str(selected.VOLUME/'metadata-check.rs'))+']\nmod metadata_check;\n'
            +(ROOT/'tests/fixtures/fs_metadata.rs').read_text())
        output = cls.out/(label+'-test')
        cls.run_command([cls.tools[tool]['path'],'--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn',
            '--test',wrapper,'-Clink-arg='+str(cls.out/'fixture.o'),'-o',output])
        return output

    def test_real_c_layout_all_fields_errors_and_disk_probe_reference_controls(self):
        binary = self.compile(self.binding,'positive')
        self.assertIn('1 passed',self.run_command([binary,'--nocapture']))

    def test_compiling_binding_omissions_fail_named_semantic_oracle(self):
        cases = (
            ('identity','value.node.object != object','false'),
            ('generation','value.node.generation != generation','false'),
            ('type','!matches!(value.node.mode & 0o170000, 0o040000 | 0o100000)','false'),
            ('parent','value.parent == 0','false'),
            ('links','value.links == 0','false'),
            ('flags','value.flags & 1 != 0','false'),
            ('nanos','time.nanoseconds >= 1_000_000_000','time.nanoseconds > u64::MAX'),
            ('status','if code != 0 {','if code < 0 {'),
            ('owner-truncation','    Ok(value)','    value.uid = u64::from(value.uid as u32);\n    Ok(value)'),
        )
        for name, old, new in cases:
            with self.subTest(omission=name):
                self.assertEqual(self.binding.count(old),1)
                # Keep omission controls compiling with warnings denied.
                if name == 'nanos': new = 'time.nanoseconds.wrapping_sub(time.nanoseconds) != 0'
                binary = self.compile(self.binding.replace(old,new,1),name)
                self.assertIn('metadata oracle:',self.run_command([binary,'--nocapture'],101))

    def test_pinned_rustfmt_and_default_clippy(self):
        self.run_command([self.tools['rustfmt']['path'],'--edition=2024','--check',selected.BINDING,
            selected.VOLUME/'metadata-check.rs',ROOT/'tests/fixtures/fs_metadata.rs'])
        self.compile(self.binding,'clippy','clippy-driver')

    def test_selected_owner_builds_native_and_preserves_original_inputs(self):
        original = (selected.VOLUME/'namespace-zpl.rs').read_text()
        before = selected.sha(selected.VOLUME/'namespace-zpl.rs')
        text = selected.selected_owner(original)
        self.assertEqual(text.count('metadata_check::check(backend.view'),1)
        with self.assertRaisesRegex(ValueError,'owner context'):
            selected.selected_owner(original.replace('    require(file.identity() == (2, 47))?;',''))
        path = self.out/'native-owner.rs'; path.write_text(text)
        self.run_command([self.tools['rustc']['path'],'--crate-type=lib','--emit=obj','--target=x86_64-unknown-none',
            '--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn','-Copt-level=2','-Cpanic=abort',
            '-Crelocation-model=static',path,'-o',self.out/'native-owner.o'])
        symbols = self.run_command([self.tools['nm']['path'],'--undefined-only',self.out/'native-owner.o'])
        self.assertIn('aether_zpl_getattr',symbols)
        self.assertEqual(selected.sha(selected.VOLUME/'namespace-zpl.rs'),before)

    def test_owner_admission_stays_unsafe_and_layout_drift_cannot_compile(self):
        path = self.out/'admission.rs'
        path.write_text('#![no_std]\n#[path = '+json.dumps(str(selected.BINDING))+'] mod metadata;\n'
            +'pub fn bad(view: core::ptr::NonNull<core::ffi::c_void>) { let _ = metadata::read(view, 2, 47); }\n')
        out = self.run_command([self.tools['rustc']['path'],'--crate-type=lib','--emit=metadata',
            '--edition=2024',path,'-o',self.out/'invalid.rmeta'],1)
        self.assertIn('E0133',out)
        path.write_text(self.binding.replace('    pub gid: u64,','    pub gid: u128,',1))
        out = self.run_command([self.tools['rustc']['path'],'--crate-type=lib','--emit=metadata',
            '--edition=2024',path,'-o',self.out/'invalid.rmeta'],1)
        self.assertIn('E0080',out)

    def test_campaign_failed_preparation_cleans_generated_output_without_guest(self):
        from unittest.mock import patch
        before = set((ROOT/'zig-out').glob('thread-suite-service-runtime-metadata-*'))
        try:
            def reject(stage, command, tools):
                stage.mkdir(); (stage/'owned.o').write_bytes(b'owned temporary double')
                raise ValueError('declared preparation rejection')
            with patch.object(selected,'build',reject), patch.object(selected,'run') as guest:
                with self.assertRaisesRegex(ValueError,'declared preparation'):
                    selected.qualify(True)
                guest.assert_not_called()
            roots = set((ROOT/'zig-out').glob('thread-suite-service-runtime-metadata-*'))-before
            self.assertEqual(len(roots),1)
            root = roots.pop()
            record = json.loads((root/'results.json').read_text())
            self.assertEqual(record['status'],'failed')
            self.assertFalse(record['native_attempted'])
            self.assertFalse(record['triage_required'])
            self.assertTrue(record['cleanup']['stopped'])
            self.assertEqual([p.name for p in root.iterdir()],['results.json'])
        finally:
            for root in set((ROOT/'zig-out').glob('thread-suite-service-runtime-metadata-*'))-before:
                import shutil
                shutil.rmtree(root)

    def test_explicit_build_callback_selects_each_provider_exactly_once(self):
        from unittest.mock import patch
        calls = []
        stage = self.out/'selection'; stage.parent.mkdir(exist_ok=True)
        def fake_reader(stage, command, tools):
            command(['cc','-c',selected.VOLUME/'zpl-read.c','-o','node.o'],'cc.log')
            command(['rustc',selected.VOLUME/'namespace-zpl.rs','-o','owner.o'],'rs.log')
            return dict(controller_bytes=1246,read_grant_only=True,kernel_tick_limit=3000)
        def command(args, log, rejection=None): calls.append(args)
        with patch.object(selected,'build_reader',fake_reader):
            result = selected.build(stage,command,{})
        self.assertEqual(result['selections'],dict(provider=1,owner=1))
        self.assertIn(str(selected.VOLUME/'zpl-metadata.c'),calls[0])
        self.assertIn(str(stage.parent/'metadata-owner.rs'),calls[1])
        with patch.object(selected,'build_reader',lambda *args: {}):
            with self.assertRaisesRegex(ValueError,'missing metadata'):
                selected.build(stage,command,{})

    def test_cli_usage_help_version_do_not_prepare_or_boot(self):
        before = set((ROOT/'zig-out').glob('thread-suite-service-runtime-metadata-*'))
        result = subprocess.run([sys.executable,'-B',ROOT/'scripts/fs_metadata.py','--disk','/dev/disk0'],
                                capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,64)
        self.assertFalse(result.stdout)
        self.assertIn('[FAIL] unrecognized arguments:',result.stderr)
        for flag, marker in (('--help','--run'),('--version','aether-fs-metadata 1')):
            result = subprocess.run([sys.executable,'-B',ROOT/'scripts/fs_metadata.py',flag],
                                    capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0)
            self.assertIn(marker,result.stdout)
            self.assertFalse(result.stderr)
        self.assertEqual(set((ROOT/'zig-out').glob('thread-suite-service-runtime-metadata-*')),before)
