# SPDX-License-Identifier: BSD-2-Clause
"""Private namespace C fault/ownership controls, independent of native media."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OWNED = ROOT / 'user/storage/openzfs-volume'


class NamespaceMutation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-c-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join(line for line in (OWNED / 'zpl-mutate.c').read_text().splitlines() if not line.startswith('#include')) + '\n'
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'namespace')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'mutate.inc').write_text(body)
        binary = cls.out / name
        p = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out), '-I' + str(OWNED),
            str(ROOT / 'tests/fixtures/openzfs_zpl_mutate.c'), '-o', str(binary)],
            capture_output=True, text=True, timeout=30)
        if p.returncode:
            raise RuntimeError(p.stdout + p.stderr)
        return binary

    def run_mode(self, op, mode, fault=0, binary=None, expected=0):
        p = subprocess.run([str(binary or self.binary), str(op), str(mode), str(fault)],
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
        return p.stdout

    def test_success_private_acl_same_directory_rename_remove_and_checked_noop(self):
        for op in range(3):
            self.run_mode(op, 0)
            self.run_mode(op, 42)
        self.run_mode(1, 40)
        self.run_mode(1, 41)

    def test_preflight_names_times_parent_flags_limits_and_expected_identity(self):
        common = [1, 2, 4, 7, 9, 10, 11, 12, 13, *range(15, 24)]
        for op in range(3):
            modes = common + ([14, 24, 31, 38, 39] if op == 0 else [3, 5, 6, 8, *range(32, 36)])
            modes += [31] if op == 1 else [36, 37] if op == 2 else []
            for mode in modes:
                with self.subTest(op=op, mode=mode):
                    self.run_mode(op, mode)

    def test_every_reachable_api_failure_commits_only_assigned_progress_and_cleans(self):
        for op in range(3):
            normal = self.run_mode(op, 0)
            calls = int(re.search(r'calls=(\d+)', normal)[1])
            for fault in range(1, calls + 1):
                with self.subTest(op=op, fault=fault):
                    self.run_mode(op, 0, fault)

    def test_compiling_missing_effects_holds_progress_sync_or_cleanup_fail94(self):
        for name, old, new, op, mode in (
                ('generation', 'out->node.generation != generation', '((void)generation, 0)', 1, 3),
                ('acl', 'error = sa_replace_all_by_template(handle, attrs, n, tx);', 'if (0) error = sa_replace_all_by_template(handle, attrs, n, tx);', 0, 0),
                ('create-name', 'error = zap_add(view->os, directory, component, 8, 1, &entry, tx);', 'if (0) error = zap_add(view->os, directory, component, 8, 1, &entry, tx);', 0, 0),
                ('rename-remove', 'error = zap_remove(view->os, directory, source, tx);', 'if (0) error = zap_remove(view->os, directory, source, tx);', 1, 0),
                ('free', 'error = dmu_object_free(view->os, object, tx);', 'if (0) error = dmu_object_free(view->os, object, tx);', 2, 0),
                ('netfree', 'dmu_tx_mark_netfree(tx);', 'if (0) dmu_tx_mark_netfree(tx);', 2, 0),
                ('commit', 'dmu_tx_commit(tx);', 'if (0) dmu_tx_commit(tx);', 0, 0),
                ('sync', 'if (!error && spa_last_synced_txg', 'if (0 && !error && spa_last_synced_txg', 0, 0),
                ('close', 'sa_handle_destroy(node->handle);', 'if (0) sa_handle_destroy(node->handle);', 1, 0)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                if name == 'sync':
                    # Last-sync getter failure is a distinct post-commit outcome.
                    normal = self.run_mode(op, 0)
                    fault = int(re.search(r'calls=(\d+)', normal)[1])
                    self.run_mode(op, mode, fault, binary, expected=94)
                else:
                    self.run_mode(op, mode, binary=binary, expected=94)


class NamespaceProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-probe-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.body = '\n'.join(line for line in (OWNED / 'zpl-mutation-probe.c').read_text().splitlines() if not line.startswith('#include')) + '\n'
        cls.binaries = {(kind, reader): cls.compile(cls.body, kind, reader, str(kind) + str(reader))
                        for kind in (1, 2, 3) for reader in (0, 1)}

    @classmethod
    def compile(cls, body, kind, reader, name):
        (cls.out / 'namespace-probe.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-DMNS_KIND=' + str(kind), '-DMNS_READER=' + str(reader),
            '-I' + str(cls.out), '-I' + str(OWNED), str(ROOT / 'tests/fixtures/openzfs_namespace_probe.c'), '-o', str(binary)],
            capture_output=True, text=True, timeout=30)
        if result.returncode: raise RuntimeError(result.stdout + result.stderr)
        return binary

    def run_mode(self, binary, mode, fault=0, expected=0):
        result = subprocess.run([str(binary), str(mode), str(fault)], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_all_six_verifiers_exact_names_objects_hash_metadata_acl_and_cleanup(self):
        for (kind, reader), binary in self.binaries.items():
            self.run_mode(binary, 0)
            modes = list(range(1, 20))
            if kind == 3 and reader:
                modes = [m for m in modes if m not in (7, 8, 9, 10, 14)]
            if not reader: modes += [21, 22, 23]
            if not reader and kind != 3: modes += [20]
            for mode in modes:
                with self.subTest(kind=kind, reader=reader, mode=mode): self.run_mode(binary, mode)

    def test_every_reachable_api_failure_stops_without_replay_or_owned_handles(self):
        for (kind, reader), binary in self.binaries.items():
            calls = int(re.search(r'calls=(\d+)', self.run_mode(binary, 0))[1])
            for fault in range(1, calls + 1):
                with self.subTest(kind=kind, reader=reader, fault=fault): self.run_mode(binary, 0, fault)

    def test_compiling_omissions_fail_independent_oracle95(self):
        for name, old, new, kind, reader, mode in (
                ('hash', 'memcmp(digest, expected, sizeof(expected))', '((void)expected, 0)', 1, 1, 4),
                ('inventory', 'return mask == 511 && added == !!extra ? 0 : EIO;', 'return ((void)mask, (void)added, 0);', 3, 1, 18),
                ('acl', 'acl[1].z_access_mask != UINT32_C(0x120088)', '0', 1, 1, 14),
                ('ctime', 'ctime[0] > 1791290100', '0', 3, 1, 13),
                ('progress', '*assigned = result.txg;', '*assigned = 0;', 1, 0, 0),
                ('state', 'result.state != AETHER_ZPL_SYNCED', '0', 1, 0, 21),
                ('close', 'if (view)\n        aether_zpl_close(&view);', 'if (0 && view)\n        aether_zpl_close(&view);', 1, 0, 0)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), kind, reader, name)
                self.run_mode(binary, mode, expected=95)
