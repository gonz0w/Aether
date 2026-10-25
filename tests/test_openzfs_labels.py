# SPDX-License-Identifier: BSD-2-Clause
"""Original label reader over fake decode/provider; no import or native run."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from deps import ROOT
from openzfs_elapsed import CURRENT, function, route, patch_alloc_header
from openzfs_pool import pool_label_bodies
from openzfs_volume import OWNED


def label_profile(text):
    """Execute the adapter's actual compile-time profile in config excerpts."""
    match = re.search(r'#ifndef AETHER_POOL_ACTIVE_LABELS\n.*?\n#endif', text, re.S)
    if match is None or text.count('#ifndef AETHER_POOL_ACTIVE_LABELS') != 1:
        raise AssertionError('label profile selection context drift')
    return match.group()


class OpenZfsLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-label-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)
        cls.source = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libzutil/zutil_import.c'
        cls.original = cls.source.read_text()
        cls.bodies = pool_label_bodies(cls.original)
        cls.binary = cls.compile(cls.output)
        cls.host_receipt = {
            'argv': cls.host_command,
            'binary_sha256': hashlib.sha256(cls.binary.read_bytes()).hexdigest(),
            'upstream_excerpt_sha256': hashlib.sha256(cls.bodies.encode()).hexdigest(),
            'scope': 'actual reader/adapter with synthetic decoder/provider; no native execution',
        }

    @classmethod
    def compile(cls, output, adapter=None, active=False):
        for name in ('zfs_context.h', 'vdev_impl.h', 'zfs_file.h'):
            header = output / 'sys' / name
            header.parent.mkdir(exist_ok=True)
            header.write_text('/* Host scaffolding supplies types, not native headers. */\n')
        (output / 'pool-label-original.inc').write_text(pool_label_bodies(
            (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libzutil/zutil_import.c').read_text()))
        selected = adapter or (OWNED / 'pool-label.c').read_text()
        # This harness exercises intake only; the independent config harness
        # executes the new builder against owned/deep-copy nvlist scaffolding.
        selected = selected.replace(function(selected, 'aether_pool_label_config'), '', 1)
        (output / 'pool-label.c').write_text(selected)
        binary = output / 'probe'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        argv = [
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11', '-O2',
            '-Wall', '-Wextra', '-Werror', '-isysroot', sdk,
            '-I' + str(output), '-I' + str(OWNED),
            *(['-DAETHER_POOL_ACTIVE_LABELS=1'] if active else []),
            str(ROOT / 'tests/fixtures/openzfs_pool_label.c'), '-o', str(binary),
        ]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)
        if adapter is None and not active:
            cls.host_command = argv
        return binary

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_offsets_readonly_authority_and_exact_cleanup(self):
        self.check_modes((0, 1, 2, 3, 4, 5, 6, 7, 8))

    def test_guid_matching_and_original_invalid_label_rejection(self):
        self.check_modes((9, 10, 26, 27, 28))

    def test_private_topology_name_path_format_and_feature_scope(self):
        self.check_modes((*range(11, 26), 29, 30, 31, 32))

    def test_omitted_matching_count_and_feature_guards_fail_named_oracles(self):
        text = (OWNED / 'pool-label.c').read_text()
        for anchor, replacement, mode in (
            ('!label || count != VDEV_LABELS', '!label', 9),
            ('nvlist_next_nvpair(features, NULL)', '(nvlist_next_nvpair(features, NULL), 0)', 18),
        ):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='aether-pool-label-broken-') as directory:
                self.assertEqual(text.count(anchor), 1)
                binary = self.compile(Path(directory), text.replace(anchor, replacement, 1))
                result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 90, result.stdout + result.stderr)
                self.assertIn(b'label oracle:', result.stderr)

    def test_original_body_drift_and_duplicate_selection_reject(self):
        for name in ('label_offset', 'zpool_read_label_slow'):
            body = function(self.original, name)
            for changed in (self.original + '\n' + body,
                            self.original.replace(body, body.replace('{', '{ /* changed */', 1), 1)):
                with self.subTest(name=name), self.assertRaises(RuntimeError):
                    pool_label_bodies(changed)
        self.assertIn('CDDL', self.bodies)
        self.assertIn('struct aether_label_reader *fd', self.bodies)
        # Prefix is consumed for notices too; intact bodies cannot authorize
        # injected preprocessor code outside them.
        with self.assertRaisesRegex(RuntimeError, 'original label source changed'):
            pool_label_bodies('#define nvlist_unpack forged_decoder\n' + self.original)

    def test_native_object_with_selected_headers_and_no_host_io_imports(self, active=False):
        receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-104-checked')
        selected = next(row for row in receipt['objects'] if row['index'] == 104)
        recorded = {route(path): digest for path, digest in selected['dependencies'].items()}
        for path, digest in recorded.items():
            self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), digest, path)
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        with tempfile.TemporaryDirectory(prefix='aether-pool-label-native-') as directory:
            output = Path(directory)
            (output / 'pool-label-original.inc').write_text(pool_label_bodies(
                (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libzutil/zutil_import.c').read_text()))
            header = CURRENT / 'build-attempt-5/guarded-include/umem.h'
            selected_header, _ = patch_alloc_header(header.read_text())
            (output / 'umem.h').write_text(selected_header)
            target = output / 'label.o'
            dependencies = output / 'label.d'
            argv = [prefix[0], '-I' + str(output), *prefix[1:],
                '-I' + str(OWNED), '-isystem',
                str(Path(prefix[0]).parents[1] / 'lib/clang/21/include'),
                '-Wall', '-Wextra', '-Werror', '-MD', '-MF', str(dependencies),
                *(['-DAETHER_POOL_ACTIVE_LABELS=1'] if active else []),
                '-c', str(OWNED / 'pool-label.c'),
                '-o', str(target),
            ]
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(output / 'umem.h'), dependencies.read_text())
            self.assertNotIn(str(header), dependencies.read_text())
            imports = subprocess.check_output([
                '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-nm', '--undefined-only', str(target),
            ], text=True)
            names = {row.split()[-1] for row in imports.splitlines() if row.strip()}
            self.assertEqual(names, {
                '__stack_chk_fail', '__errno_location', 'free', 'posix_memalign', 'spl_pagesize',
                'nvlist_exists', 'nvlist_free', 'nvlist_lookup_nvlist',
                'nvlist_lookup_string', 'nvlist_lookup_uint64', 'nvlist_next_nvpair',
                'nvlist_unpack', 'strcmp', 'zfs_file_close', 'zfs_file_getattr',
                'zfs_file_open', 'zfs_file_pread',
                'nvlist_alloc', 'nvlist_add_nvlist', 'nvlist_add_nvlist_array',
                'nvlist_add_string', 'nvlist_add_uint32', 'nvlist_add_uint64',
            }, imports)
            self.assertGreater(target.stat().st_size, 0)
            # Optional caller can retain this compact result before temp cleanup;
            # the unittest itself creates no persistent evidence or binary bundle.
            paths = dependencies.read_text().replace('\\\n', '').split(': ', 1)[1].split()
            self.__class__.native_receipt = {
                'argv': argv,
                'object_bytes': target.stat().st_size,
                'object_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                'undefined_symbols': sorted(names),
                'headers_and_sources': {
                    path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                    for path in paths
                },
                'allocation_header_sha256': hashlib.sha256(selected_header.encode()).hexdigest(),
                'baseline_dependencies_verified': len(recorded),
                'profile': 'active' if active else 'exported',
                'scope': 'x86_64-linux-musl object only; not linked or executed in native pool profile',
            }
            for path, digest in recorded.items():
                self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), digest, path)


class OpenZfsImportConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-config-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)
        cls.binary = cls.compile(cls.output)

    @classmethod
    def compile(cls, output, changed=None, active=False):
        text = changed or (OWNED / 'pool-label.c').read_text()
        bodies = '\n'.join(function(text, name) for name in
                           ('aether_label_validate', 'aether_pool_label_config'))
        (output / 'pool-config-bodies.inc').write_text(label_profile(text) + '\n' + bodies)
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        binary = output / 'config'
        result = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11', '-O2',
            '-Wall', '-Wextra', '-Werror', '-isysroot', sdk, '-I' + str(output),
            *(['-DAETHER_POOL_ACTIVE_LABELS=1'] if active else []),
            str(ROOT / 'tests/fixtures/openzfs_pool_config.c'), '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)
        return binary

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_root_identity_policy_type_and_no_raw_field_passthrough(self):
        self.check_modes((0, 1, 2))

    def test_metadatasize_topology_and_required_type_rejections(self):
        self.check_modes(range(3, 12))

    def test_every_allocation_and_add_failure_preserves_errno_and_cleanup(self):
        self.check_modes(('failures',))

    def test_weaker_rewind_policy_fails_named_semantic_oracle(self):
        text = (OWNED / 'pool-label.c').read_text()
        self.assertEqual(text.count('ZPOOL_NEVER_REWIND'), 1)
        with tempfile.TemporaryDirectory(prefix='aether-pool-config-broken-') as directory:
            binary = self.compile(Path(directory), text.replace('ZPOOL_NEVER_REWIND', '0', 1))
            result = subprocess.run([str(binary), '0'], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 91, result.stdout + result.stderr)
            self.assertIn(b'policy must be uint32 NEVER_REWIND', result.stderr)


class OpenZfsActiveLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-active-label-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        cls.reader = OpenZfsLabels.compile(out, active=True)
        cls.config = OpenZfsImportConfig.compile(out, active=True)
        default = out / 'default'
        default.mkdir()
        cls.default_reader = OpenZfsLabels.compile(default)
        cls.default_config = OpenZfsImportConfig.compile(default)

    def check(self, binary, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_active_reader_keeps_all_existing_bounds_and_error_cleanup(self):
        self.check(self.reader, range(35))

    def test_default_reader_rejects_active_destroyed_missing_states(self):
        self.check(self.default_reader, (11, 33, 34))

    def test_active_config_preserves_state_policy_and_allocation_failure_cleanup(self):
        self.check(self.config, (*range(18), 'failures'))
        self.check(self.default_config, range(12, 18))

    def test_omitted_state_guard_fails_named_reader_oracle(self):
        text = (OWNED / 'pool-label.c').read_text()
        anchor = 'state != AETHER_POOL_LABEL_STATE'
        self.assertEqual(text.count(anchor), 1)
        with tempfile.TemporaryDirectory(prefix='aether-active-label-broken-') as directory:
            binary = OpenZfsLabels.compile(Path(directory), text.replace(anchor, '0', 1), active=True)
            result = subprocess.run([str(binary), '11'], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 90, result.stdout + result.stderr)
            self.assertIn(b'label oracle:', result.stderr)

    def test_forged_exported_config_fails_named_state_preservation_oracle(self):
        text = (OWNED / 'pool-label.c').read_text()
        anchor = '                                 AETHER_POOL_LABEL_STATE));'
        self.assertEqual(text.count(anchor), 1)
        with tempfile.TemporaryDirectory(prefix='aether-active-config-broken-') as directory:
            binary = OpenZfsImportConfig.compile(Path(directory),
                text.replace(anchor, '                                 POOL_STATE_EXPORTED));', 1), active=True)
            result = subprocess.run([str(binary), '0'], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 92, result.stdout + result.stderr)
            self.assertIn(b'selected pool state must be preserved92', result.stderr)

    def test_active_native_object_preserves_selected_headers_and_imports(self):
        check = OpenZfsLabels('test_native_object_with_selected_headers_and_no_host_io_imports')
        check.test_native_object_with_selected_headers_and_no_host_io_imports(active=True)
        self.__class__.active_native_receipt = OpenZfsLabels.native_receipt

    def test_unsupported_profile_value_rejects_compilation(self):
        text = (OWNED / 'pool-label.c').read_text()
        for value in (0, 2):
            with self.subTest(value=value), tempfile.TemporaryDirectory(prefix='aether-active-selector-') as directory:
                with self.assertRaisesRegex(RuntimeError, 'must be 1 when selected'):
                    OpenZfsLabels.compile(Path(directory),
                        '#define AETHER_POOL_ACTIVE_LABELS ' + str(value) + '\n' + text)


if __name__ == '__main__':
    unittest.main()
