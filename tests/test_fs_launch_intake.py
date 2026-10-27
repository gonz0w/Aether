# SPDX-License-Identifier: BSD-2-Clause
"""Exact candidate intake, real loader failure controls and provenance guards."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_launch
import fs_launch_intake as delivery
CURRENT = ROOT/'.deps/fs-launch-2026-10-20-v4'


def runtime_fixture(path, data, body, *, io='std.testing.io', allocator='std.testing.allocator'):
    """Read one full owned fixture, verify its exact bytes, then free it."""
    # Zig0.16 rejects a stream that reaches its exclusive limit. One EOF
    # probe byte permits exactly N payload bytes; length/hash still require N.
    expected = ','.join(str(byte) for byte in hashlib.sha256(data).digest())
    return ('{ const fixture = try std.Io.Dir.cwd().readFileAlloc(' + io + ', ' +
            json.dumps(str(path.resolve())) + ', ' + allocator + ', .limited(' + str(len(data) + 1) + '));\n' +
            'defer ' + allocator + '.free(fixture);\n' +
            'try std.testing.expectEqual(@as(usize,' + str(len(data)) + '), fixture.len);\n' +
            'var digest: [32]u8 = undefined; std.crypto.hash.sha2.Sha256.hash(fixture, &digest, .{});\n' +
            'try std.testing.expectEqualSlices(u8, &[_]u8{' + expected + '}, &digest);\n' + body + '\n}\n')


class LaunchIntake(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aether-launch-intake-', dir='/private/tmp')
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)

    def copy(self):
        path = self.out/'candidate'
        shutil.copytree(CURRENT, path)
        return path

    def test_exact_candidate_and_tampered_missing_extra_symlink_members(self):
        selected = delivery.intake(CURRENT)
        self.assertEqual(selected['members'], 30)
        self.assertFalse(selected['native_acceptance'])
        root = self.copy()
        elf = root/'filesystem.elf'
        original = elf.read_bytes()
        elf.write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError, 'member identity'): delivery.intake(root)
        elf.write_bytes(original)
        (root/'extra').write_text('extra')
        with self.assertRaisesRegex(ValueError, 'closure'): delivery.intake(root)
        (root/'extra').unlink()
        elf.unlink()
        elf.symlink_to(CURRENT/'filesystem.elf')
        with self.assertRaisesRegex(ValueError, 'member identity'): delivery.intake(root)
        with self.assertRaisesRegex(ValueError, 'manifest identity'): delivery.intake(CURRENT, '0'*64)

    def test_duplicate_paths_and_report_native_or_false_success_claims_reject(self):
        root = self.copy()
        manifest = root/'SHA256SUMS'
        original = manifest.read_text()
        manifest.write_text(original+original.splitlines()[0]+'\n')
        with self.assertRaisesRegex(ValueError, 'member path'):
            delivery.intake(root, delivery.digest(manifest))
        record = json.loads((root/'build.json').read_text())
        for key, value in (('executed', True), ('status','incomplete'), ('elf_bytes',1), ('origins',{})):
            with self.subTest(key=key):
                altered = {**record,key:value}
                (root/'build.json').write_text(json.dumps(altered))
                lines = [delivery.digest(root/n)+'  '+n for n in
                         [line.split(maxsplit=1)[1] for line in original.splitlines()]]
                manifest.write_text('\n'.join(lines)+'\n')
                with self.assertRaisesRegex(ValueError,'build identity/coverage'):
                    delivery.intake(root,delivery.digest(manifest))

    def test_exact_recipe_origins_and_destination_guards(self):
        record = {'commands':[{'argv':['ld','a','-o','/owned/engine.o'],'exit_code':0}]}
        self.assertEqual(fs_launch.recipe(record,'engine.o')[-1],'/owned/engine.o')
        record['commands'] *= 2
        with self.assertRaisesRegex(ValueError,'ambiguous'): fs_launch.recipe(record,'engine.o')
        good = '1 1 4 1 /owned/main.o:(.text.main)\n1 1 4 1 main\n'
        self.assertEqual(fs_launch.origins(good,{'main':'main.o'})['main'],'/owned/main.o')
        for text in (good+good,good.replace('main.o','fixture.o'),''):
            with self.assertRaises(ValueError): fs_launch.origins(text,{'main':'main.o'})
        for path in (CURRENT,self.out/'arbitrary',ROOT/'.deps/other'):
            with self.assertRaises(ValueError): fs_launch.validate_destination(path)
        source = (fs_launch.VOLUME/'namespace-label.inc').read_text()
        changed = fs_launch.labels(source)
        self.assertEqual(changed.replace('txg < 782','txg != 782'),source)
        with self.assertRaises(ValueError): fs_launch.labels(changed)

    def test_build_only_hook_and_cli_reject_before_intake(self):
        import service_runtime_smoke as runtime
        with patch.object(runtime, 'intake', side_effect=AssertionError('intake reached')):
            for flags in ({}, {'_zpl_fs_directories':True, 'pool_diagnose':'run'},
                          {'_zpl_fs_directories':True,'pool_diagnose':'build','_zpl_storage_lifetime':True}):
                with self.subTest(flags=flags), self.assertRaisesRegex(ValueError, 'launch owner requires'):
                    runtime.suite(ROOT/'.deps/native-utc-v3/base',
                                  _fs_launch_output=ROOT/'.deps/fs-launch-unexecuted-test', **flags)
        for args, status in (([],64), (['--bad\x1bfield'],64),
                             (['--output',str(self.out/'unowned')],1)):
            run = subprocess.run([sys.executable,'-B',str(ROOT/'scripts/fs_launch.py'),*args],
                                 capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,status,run.stdout+run.stderr)
            self.assertEqual(run.stdout,'')
            self.assertNotIn('\x1b',run.stderr)
        self.assertFalse((self.out/'unowned').exists())

    def test_actual_kernel_parser_requires_tls_wx_and_existing_geometry_limits(self):
        original = bytearray((CURRENT/'filesystem.elf').read_bytes())
        phoff = struct.unpack_from('<Q',original,32)[0]
        count = struct.unpack_from('<H',original,56)[0]
        offsets = [phoff+i*56 for i in range(count)]
        tls = next(p for p in offsets if struct.unpack_from('<I',original,p)[0]==7)
        rx = next(p for p in offsets if struct.unpack_from('<II',original,p)==(1,5))
        images = {'valid':original}
        missing = original.copy()
        # Another permitted metadata view; only the required TLS presence is lost.
        struct.pack_into('<I',missing,tls,0x6474e550)
        images['missing_tls']=missing
        wx = original.copy(); struct.pack_into('<I',wx,rx+4,7); images['writable_code']=wx
        large = original.copy(); struct.pack_into('<Q',large,tls+40,4097); images['oversized_tls']=large
        for name, data in images.items(): (self.out/(name+'.elf')).write_bytes(data)
        checks = 'const std=@import("std");const elf=@import("native_elf");\npub fn main(init: std.process.Init) !void {\n'
        checks += runtime_fixture(self.out/'valid.elf', images['valid'],
            '_=try elf.parseWithLimits(fixture,elf.large_limits);\n'
            'try std.testing.expectError(error.InvalidImage,elf.parse(fixture));', io='init.io', allocator='init.gpa')
        for name, data in images.items():
            if name != 'valid':
                checks += runtime_fixture(self.out/(name+'.elf'), data,
                    'try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(fixture,elf.large_limits));',
                    io='init.io', allocator='init.gpa')
        checks += '}\n'
        (self.out/'check.zig').write_text(checks)
        run=subprocess.run(['zig','build-exe','--cache-dir',str(ROOT/'.zig-cache'),
            '--global-cache-dir',str(ROOT/'.zig-cache/global'),'-O','ReleaseSafe','--dep','native_elf',
            '-Mroot='+str(self.out/'check.zig'),'-Mnative_elf='+str(ROOT/'kernel/native_elf.zig'),
            '-femit-bin='+str(self.out/'check')],capture_output=True,text=True,timeout=60)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        executed=subprocess.run([str(self.out/'check')],capture_output=True,text=True,timeout=60)
        self.assertEqual(executed.returncode,0,executed.stdout+executed.stderr)


if __name__ == '__main__':
    unittest.main()
