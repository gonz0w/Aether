# SPDX-License-Identifier: BSD-2-Clause
"""Actual read-only adapter under faulting API doubles; no disk-decoding claim."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from openzfs_elapsed import CURRENT, route


class ZplReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.source = ROOT / 'user/storage/openzfs-volume/zpl-read.c'
        cls.body = '\n'.join(line for line in cls.source.read_text().splitlines()
                             if not line.startswith('#include')) + '\n'
        cls.binary = cls.compile(cls.body, 'reader')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'zpl-adapter.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run([
            '/usr/bin/cc', '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
            '-I', str(cls.out), '-I', str(cls.source.parent),
            str(ROOT / 'tests/fixtures/openzfs_zpl_read.c'), '-o', str(binary)
        ], capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        return binary

    def modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)],
                                        capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_root_format_identity_ownership_and_cleanup(self):
        self.modes(range(21))

    def test_open_failure_at_every_api_boundary_including_set_out_then_error(self):
        self.modes(range(100, 113))

    def test_component_names_registered_sa_mapping_type_and_generation(self):
        self.modes(range(30, 49))

    def test_lookup_failure_at_every_api_boundary_publishes_no_node(self):
        self.modes(range(200, 207))

    def test_exact_short_zero_eof_bounded_reads_and_stale_rejection(self):
        self.modes(range(50, 61))

    def test_read_failures_clear_partial_output_and_release_sa(self):
        self.modes(range(300, 304))

    def test_root_revalidation_and_nullable_zero_read(self):
        self.modes((70, 71, 72))

    def test_named_compiling_omissions_fail_semantic_oracle(self):
        mutations = (
            ('foreign', 'dmu_objset_spa(view->os) != spa', '0', 3),
            ('format', 'version != ZPL_VERSION_SA', '0', 6),
            ('stale', 'node.generation != generation', '((void)generation, 0)', 57),
            ('type', 'ZFS_DIRENT_TYPE(entry) != IFTODT(node.mode)', '0', 42),
            ('traversal', "name[i] == '/'", '0', 37),
            ('partial', 'memset(buffer, 0, length);\n        return error;', 'return error;', 303),
            ('failed-own', 'if (error)\n        goto fail;\n    view->os = os;',
             'view->os = os;\n    if (error)\n        goto fail;', 100),
        )
        for name, old, new, mode in mutations:
            with self.subTest(name=name):
                self.assertIn(old, self.body)
                body = self.body.replace(old, new, 1)
                # Keep a function referenced when the owner check is omitted;
                # each mutant must compile and fail behavior, not warnings.
                if name == 'foreign':
                    body += '\nstatic void *const keep_spa __attribute__((used)) = (void *)&dmu_objset_spa;\n'
                binary = self.compile(body, 'omit-' + name)
                result = subprocess.run([str(binary), str(mode)],
                                        capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 92, result.stderr.decode())
                self.assertIn(b'HOST ZPL oracle92', result.stderr)

    def test_full_native_headers_and_read_only_import_allowlist(self):
        # Reuse the exact pinned common zfs_znode compile recipe; its selected
        # sys/vfs compatibility header is necessary, unlike the vdev recipe.
        receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands']
                      if c['name'] == 'input-176-checked')
        self.assertTrue(any(a.endswith('/module/zfs/zfs_znode.c') for a in recipe))
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        llvm = Path(prefix[0]).parent
        obj = self.out / 'native-zpl.o'
        deps = self.out / 'native-zpl.d'
        result = subprocess.run(prefix + [
            '-isystem', str(llvm.parent / 'lib/clang/21/include'),
            '-std=gnu11', '-Wall', '-Wextra', '-Werror',
            '-MD', '-MF', str(deps),
            '-c', str(self.source), '-o', str(obj)
        ], capture_output=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = subprocess.run([str(llvm / 'llvm-nm'), '-u', str(obj)],
                                capture_output=True, text=True, timeout=30, check=True)
        imports = {line.split()[-1] for line in result.stdout.splitlines() if line.strip()}
        self.assertEqual(imports, {
            '__stack_chk_fail', 'dmu_object_info', 'dmu_objset_disown',
            'dmu_objset_own', 'dmu_objset_spa', 'dmu_read', 'memcpy', 'memset',
            'sa_bulk_lookup', 'sa_handle_destroy', 'sa_handle_get', 'sa_setup',
            'spa_writeable', 'free', 'calloc', 'zap_lookup',
            'zfs_attr_table', 'zfs_get_zplprop',
        })
        pins = json.loads((CURRENT / 'current-inputs.json').read_text())['files']
        inputs = {}
        for name in deps.read_text().split(':', 1)[1].replace('\\\n', ' ').split():
            path = Path(name)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            inputs[str(path)] = digest
            if path.is_relative_to(CURRENT):
                self.assertEqual(pins[str(path.relative_to(CURRENT))], digest, str(path))
        print('ZPL NATIVE HEADER ' + json.dumps({
            'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
            'bytes': obj.stat().st_size,
            'imports': sorted(imports),
            'command': prefix + ['-isystem', str(llvm.parent / 'lib/clang/21/include'),
                                '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                                '-MD', '-MF', str(deps), '-c', str(self.source), '-o', str(obj)],
            'dependency_sha256': inputs,
            'tool_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (llvm / 'clang', llvm / 'llvm-nm')},
            'scope': 'Unlinked original common-znode header recipe; active resource allocator wrappers not selected',
        }))


if __name__ == '__main__':
    unittest.main()
