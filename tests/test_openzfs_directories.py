# SPDX-License-Identifier: BSD-2-Clause
"""Directory extension: actual C, semantic faults and pinned native headers."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from test_openzfs_zpl_write import CURRENT, OWNED, ROOT, route


class Directories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-directories-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.clang = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.body = ''.join(line + '\n' for name in ('zpl-mutate.c', 'zpl-directories.c')
                           for line in (OWNED / name).read_text().splitlines()
                           if not line.startswith('#include'))
        cls.binary = cls.compile(cls.body, 'directories')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'directories.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run([str(cls.clang), '-isysroot', cls.sdk, '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out), '-I' + str(OWNED),
            str(ROOT / 'tests/fixtures/openzfs_zpl_directories.c'), '-o', str(binary)],
            capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def mode(self, op, mode=0, fault=0, binary=None, expected=0):
        result = subprocess.run([str(binary or self.binary), str(op), str(mode), str(fault)],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected == 94:
            self.assertIn('HOST MUTATION oracle94', result.stderr)
        return result.stdout

    def test_mkdir_rmdir_and_directory_refresh_exact_metadata_and_cleanup(self):
        for op in (0, 2, 3):
            self.mode(op)

    def test_scope_identity_format_names_flags_empty_and_overflow(self):
        common = [1, 2, 4, 7, 10, 11, 12, 13, *range(15, 24)]
        for op in (0, 2):
            modes = common + ([24, 56] if op == 0 else [3, *range(50, 56), *range(57, 62)])
            for mode in modes:
                with self.subTest(op=op, mode=mode):
                    self.mode(op, mode)
        for mode in (3, 4, 54):
            self.mode(3, mode)

    def test_all_reachable_api_faults_keep_assigned_outcomes_and_release_handles(self):
        for op in (0, 2, 3):
            calls = int(re.search(r'calls=(\d+)', self.mode(op))[1])
            for fault in range(1, calls + 1):
                with self.subTest(op=op, fault=fault):
                    self.mode(op, fault=fault)

    def test_compiling_omissions_fail_exact_semantic_oracle(self):
        for name, old, new, op, mode in (
            ('parent-links', 'uint64_t links = parent.links + 1;', 'uint64_t links = parent.links;', 0, 0),
            ('directory-kind', 'IFTODT(S_IFDIR) << 60', 'IFTODT(S_IFREG) << 60', 0, 0),
            ('directory-acl', 'ACE_DELETE_CHILD |', '0 |', 0, 0),
            ('new-zap-hold', 'dmu_tx_hold_zap(tx, DMU_NEW_OBJECT, B_TRUE, NULL);', 'if (0) dmu_tx_hold_zap(tx, DMU_NEW_OBJECT, B_TRUE, NULL);', 0, 0),
            ('empty-only', 'child.node.size != 2 || child.links != 2', '0', 2, 50),
            ('parent-identity', 'child.parent != directory', '0', 2, 52),
            ('root-removal', 'object == view->root.object', '0', 2, 59),
            ('free-directory', 'error = zap_destroy(view->os, object, tx);', 'if (0) error = zap_destroy(view->os, object, tx);', 2, 0),
            ('refresh-generation', '!error && node.generation != generation', '!error && ((void)generation, 0)', 3, 3),
        ):
            with self.subTest(omission=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                self.mode(op, mode, binary=binary, expected=94)

    def test_pinned_native_headers_object_dependencies_and_local_frames(self):
        receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-176-checked')
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        llvm = Path(prefix[0]).parent
        obj, deps = self.out / 'directories.o', self.out / 'directories.d'
        argv = prefix + ['-isystem', str(llvm.parent / 'lib/clang/21/include'),
            '-I' + str(OWNED), '-std=gnu11', '-Wall', '-Wextra', '-Werror',
            '-fstack-usage', '-MD', '-MF', str(deps), '-c', str(OWNED / 'zpl-directories.c'), '-o', str(obj)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        definitions = subprocess.check_output([str(llvm / 'llvm-nm'), '--defined-only', str(obj)], text=True)
        imports = subprocess.check_output([str(llvm / 'llvm-nm'), '-u', str(obj)], text=True)
        for name in ('aether_zpl_directory', 'aether_zpl_mkdir', 'aether_zpl_rmdir',
                     'aether_zpl_create', 'aether_zpl_rename', 'aether_zpl_remove'):
            self.assertEqual(sum(line.split()[-1:] == [name] for line in definitions.splitlines()), 1)
        for name in ('zap_create', 'zap_destroy', 'sa_replace_all_by_template', 'dmu_tx_hold_zap'):
            self.assertIn(name, imports)
        pins = json.loads((CURRENT / 'current-inputs.json').read_text())['files']
        inputs = {}
        for name in deps.read_text().split(':', 1)[1].replace('\\\n', ' ').split():
            path = Path(name)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            inputs[str(path)] = digest
            if path.is_relative_to(CURRENT):
                self.assertEqual(pins[str(path.relative_to(CURRENT))], digest)
        stack = obj.with_suffix('.su').read_text()
        self.assertNotIn('dynamic', stack)
        self.assertTrue(stack)
        self.assertLessEqual(max(int(line.split('\t')[1]) for line in stack.splitlines()), 8192)
        print('DIRECTORY NATIVE ' + json.dumps(dict(argv=argv,
            object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),
            dependency_sha256=inputs, local_frames=stack,
            scope='Unlinked native headers; not disk execution or full call-chain fit')))


if __name__ == '__main__':
    unittest.main()
