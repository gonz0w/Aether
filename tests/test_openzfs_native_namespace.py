# SPDX-License-Identifier: BSD-2-Clause
"""Native fixture/helper preparation; API doubles do not qualify native decoding."""
import ast
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import openzfs_namespace as namespace
import service_runtime_smoke as runtime
import native_smoke


class NamespaceNativeMedia(unittest.TestCase):
    def test_written_snapshot_is_separate_and_requires_unchanged_guards(self):
        with tempfile.TemporaryDirectory(prefix='thread-suite-service-runtime-written-', dir=ROOT / 'zig-out') as tmp:
            out = Path(tmp)
            disk = Path(namespace.prepare_native_fixture(out)['output'])
            with self.assertRaisesRegex(ValueError, 'still pristine'):
                namespace.written_native_media_snapshot(disk)
            with disk.open('r+b') as stream:
                stream.seek(4096 + 1048576)
                original = stream.read(1)
                stream.seek(-1, 1)
                stream.write(bytes([original[0] ^ 1]))
            result = namespace.written_native_media_snapshot(disk)
            self.assertFalse(result['sealed_identity_match'])
            self.assertTrue(result['outside_region_canaries_match'])
            self.assertTrue(namespace.written_native_media_snapshot(
                disk, result['sha256'])['sealed_identity_match'])
            with self.assertRaisesRegex(ValueError, 'sealed hash mismatch'):
                namespace.written_native_media_snapshot(disk, '0' * 64)
            with self.assertRaisesRegex(ValueError, 'pinned region hash'):
                namespace.native_media_snapshot(disk)
            image = out / 'pool-import/aether.iso'
            image.parent.mkdir()
            with patch.object(native_smoke, 'verify', side_effect=AssertionError('no launch')):
                with self.assertRaisesRegex(ValueError, 'pinned region hash'):
                    native_smoke.run(image, block_disk=disk, block_large=True, block_namespace=True)
            for offset in (0, 1073745920):
                with disk.open('r+b') as stream:
                    stream.seek(offset)
                    stream.write(b'!')
                with self.assertRaisesRegex(ValueError, 'guard'):
                    namespace.written_native_media_snapshot(disk, result['sha256'])
                with disk.open('r+b') as stream:
                    stream.seek(offset)
                    stream.write(b'\xa5')
            alias = out / 'alias.raw'
            alias.symlink_to(disk)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                namespace.written_native_media_snapshot(alias)

    def test_written_snapshot_digest_syntax_rejects_before_open(self):
        for value in ('', 'A' * 64, 'g' * 64, '0' * 63, '0' * 65, 1, b'0' * 64):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'canonical SHA256'):
                namespace.written_native_media_snapshot('/absent', value)

    def test_fixed_wrapped_geometry_identity_guards_and_no_raw_copy(self):
        with tempfile.TemporaryDirectory(prefix='thread-suite-service-runtime-ns-host-', dir=ROOT / 'zig-out') as tmp:
            out = Path(tmp)
            result = namespace.prepare_native_fixture(out)
            disk = Path(result['output'])
            self.assertFalse((out / 'namespace-pool.img').exists())
            self.assertEqual(result['bytes'], 1073750016)
            self.assertEqual(namespace.native_media_snapshot(disk)['sha256'], result['sha256'])
            image = out / 'pool-import/aether.iso'
            image.parent.mkdir()
            image.write_bytes(b'not a boot image; dependency guard stops execution')
            with patch.object(native_smoke, 'verify', side_effect=RuntimeError('dependency boundary')):
                with self.assertRaisesRegex(RuntimeError, 'dependency boundary'):
                    native_smoke.run(image, block_disk=disk, block_large=True, block_namespace=True)
                with self.assertRaises(ValueError):
                    native_smoke.run(image, block_disk=disk, block_large=True)
                with self.assertRaises(ValueError):
                    native_smoke.run(image, block_disk=disk, block_namespace=True)
            with self.assertRaises(FileExistsError):
                namespace.prepare_native_fixture(out)
            self.assertTrue(disk.exists())
            self.assertFalse((out / 'namespace-pool.img').exists())
            for offset, message in ((0, 'leading guard'), (1073745920, 'trailing guard'), (4096, 'region hash')):
                with disk.open('r+b') as stream:
                    stream.seek(offset); original = stream.read(1)
                    stream.seek(offset); stream.write(bytes([original[0] ^ 1]))
                with self.assertRaisesRegex(ValueError, message):
                    namespace.native_media_snapshot(disk)
                with disk.open('r+b') as stream:
                    stream.seek(offset); stream.write(original)

    def test_trace_requires_success_row_and_exact_replacements(self):
        lines = [f'NATIVE observation slot=0 generation=1 offset={i*8} byte={b}'
                 for i, b in enumerate(b'BIUVWLPabcdefghOAMZDJFR')]
        lines += [f'NATIVE observation slot=0 generation={g} offset={i*8} byte={b}'
                  for g in (2, 3) for i, b in enumerate(b'BNR')]
        text = '\n'.join(lines)
        self.assertEqual(runtime.check_namespace_trace(text)['namespace_bytes_verified'], 780248)
        for changed in (text.replace('byte=90', 'byte=89'), text + '\nNATIVE observation malformed',
                        text.replace('generation=3', 'generation=4'), '\n'.join(lines[:18] + lines[19:])):
            with self.subTest(changed=changed[-70:]):
                with self.assertRaises(ValueError):
                    runtime.check_namespace_trace(changed)

    def test_selectors_reject_before_dependency_access(self):
        with patch.object(runtime, 'intake', side_effect=AssertionError('dependency access')):
            for kwargs in ({}, {'pool_create': True, 'case': 'pool-create', 'pool_diagnose': 'build'},
                           {'pool_create': True, 'case': 'pool-import', 'pool_diagnose': 'build', 'pool_data': True}):
                with self.subTest(kwargs=kwargs):
                    with self.assertRaisesRegex(ValueError, 'namespace requires exclusive'):
                        runtime.suite(Path('/absent'), pool_namespace=True, **kwargs)


class NamespaceHelper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-helper-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join(line for line in (ROOT / 'user/storage/openzfs-volume/pool-namespace.c').read_text().splitlines()
                             if not line.startswith('#include')) + '\n'
        cls.binary = cls.compile(cls.body, 'helper')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'namespace-helper.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/usr/bin/cc', '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                                 '-I' + str(cls.out), '-I' + str(ROOT / 'user/storage/openzfs-volume'),
                                 str(ROOT / 'tests/fixtures/openzfs_namespace_read.c'), '-o', str(binary)],
                                capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        return binary

    def modes(self, values):
        for value in values:
            result = subprocess.run([str(self.binary), str(value)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, (value, result.stderr))

    def test_full_stream_digest_contract_metadata_denials_and_close(self):
        self.modes(range(9))

    def test_every_provider_failure_preserves_cleanup(self):
        self.modes(range(101, 302))

    def test_compiling_omissions_fail_named_oracle(self):
        for name, old, new, mode in (
            ('digest', 'memcmp(digest, expected, sizeof(expected))', '((void)expected, 0)', 3),
            ('close', 'aether_zpl_close(&view);', '(void)view;', 0),
            ('stream', 'SHA2Update(&hash, buffer, count);', '(void)&hash;', 0),
        ):
            self.assertIn(old, self.body)
            binary = self.compile(self.body.replace(old, new, 1), 'omit-' + name)
            result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 94, result.stderr)
            self.assertIn(b'HOST NAMESPACE HELPER oracle94', result.stderr)


class NamespaceLabels(unittest.TestCase):
    recovery = False
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-label-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = (ROOT / 'user/storage/openzfs-volume/namespace-label.inc').read_text()
        if cls.recovery:
            cls.body = namespace.recovery_label_source(cls.body)
        scaffold = (ROOT / 'tests/fixtures/openzfs_pool_config.c').read_text().split('#include "pool-config-bodies.inc"')[0]
        scaffold = scaffold.replace('    assert(!old);\n    return list->count ? &list->pairs[0] : NULL;',
                                    '    if (!old) return list->count ? &list->pairs[0] : NULL;\n'
                                    '    unsigned next = (unsigned)(old - list->pairs) + 1;\n'
                                    '    return next < list->count ? &list->pairs[next] : NULL;')
        scaffold += '\n#define AETHER_POOL_LABEL_STATE 1\n#define DATA_TYPE_BOOLEAN 6\nstatic int nvpair_type(nvpair_t *p) { return p->type; }\n'
        scaffold += 'static const char *nvpair_name(nvpair_t *p) { return p->string; }\n'
        scaffold += '#include "namespace-config.inc"\n'
        cases = (ROOT / 'tests/fixtures/openzfs_namespace_config.inc').read_text()
        if cls.recovery:
            cases = cases.replace('                         782,', '                         788,', 1)
            cases = cases.replace('    if (mode >= 2 && mode <= 8)',
                                  '    if (mode == 23) values[5] = 782;\n'
                                  '    if (mode == 24) values[5] = 0;\n'
                                  '    if (mode == 25) values[5] = UINT64_MAX;\n'
                                  '    if (mode >= 2 && mode <= 8)', 1)
            cases = cases.replace('mode >= 2              ? EINVAL',
                                  '(mode >= 2 && mode != 7 && mode != 25) ? EINVAL', 1)
        scaffold += cases
        (cls.out / 'driver.c').write_text(scaffold)
        cls.binary = cls.compile(cls.body, 'labels')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'namespace-config.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/usr/bin/cc', '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                                 '-I' + str(cls.out), str(cls.out / 'driver.c'), '-o', str(binary)],
                                capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        return binary

    def test_exact_identity_geometry_features_and_path_reconstruction(self):
        for mode in range(23):
            result = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, (mode, result.stderr))

    def test_every_config_allocation_failure_cleans_partial_nvlists(self):
        result = subprocess.run([str(self.binary), 'failures'], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_compiling_omissions_fail_semantic_oracle(self):
        for name, old, new, mode in (
            ('features', 'bits == 3 && count == 2', '((void)bits, (void)count, 1)', 10),
            ('geometry', 'asize != UINT64_C(1069023232)', '0', 22),
            ('rewind', 'ZPOOL_NEVER_REWIND', '0', 0),
        ):
            self.assertIn(old, self.body)
            binary = self.compile(self.body.replace(old, new, 1), 'omit-' + name)
            result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 95, (name, result.stderr))
            self.assertIn(b'HOST NAMESPACE LABEL oracle95', result.stderr)


class NamespaceRecoveryLabels(NamespaceLabels):
    recovery = True

    def test_old_zero_and_maximum_txgs_and_selection_drift(self):
        for mode in (23, 24, 25):
            result = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
        for text in ('', self.body):
            with self.assertRaisesRegex(ValueError, 'context changed'):
                namespace.recovery_label_source(text)

    def test_compiling_txg_guard_omission_rejects_at_semantic_oracle(self):
        self.assertEqual(self.body.count('txg <= 782 ||'), 1)
        binary = self.compile(self.body.replace('txg <= 782 ||', '0 ||', 1), 'omit-txg')
        result = subprocess.run([str(binary), '23'], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 95, result.stderr)
        self.assertIn(b'HOST NAMESPACE LABEL oracle95', result.stderr)


if __name__ == '__main__':
    unittest.main()
