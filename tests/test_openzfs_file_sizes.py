# SPDX-License-Identifier: BSD-2-Clause
"""Original writer-based zero extension and actual fixed guest verifiers."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import test_openzfs_zpl_write as original

ROOT, OWNED = original.ROOT, original.OWNED


class InitializedExtension(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        w = original.ZplWriter; w.setUpClass(); cls.addClassCleanup(w.doClassCleanups)
        cls.out, cls.clang, cls.sdk = w.out, w.clang, w.sdk
        seed = (ROOT / 'tests/fixtures/openzfs_zpl_write.c').read_text()
        (cls.out / 'extend-common.inc').write_text(seed.split('#include "zpl-adapter.inc"')[0])
        setup = seed.split('static void setup(void)', 1)[1].split('\nint main(', 1)[0]
        (cls.out / 'extend-setup.inc').write_text('static void setup(void)' + setup)
        cls.prefix = '#define AETHER_ZPL_WRITE_PROVIDER 1\n' + w.read_body + w.write_body
        cls.body = '\n'.join(line for line in (OWNED / 'zpl-extend.c').read_text().splitlines() if not line.startswith('#include')) + '\n'
        cls.binary = cls.compile(cls.body, 'extend')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'extend-adapter.inc').write_text(cls.prefix + body)
        binary = cls.out / name
        p = subprocess.run([str(cls.clang), '-isysroot', cls.sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
            '-DAETHER_ZPL_ORDERED_WRITE=1', '-I' + str(cls.out), '-I' + str(OWNED),
            str(ROOT / 'tests/fixtures/openzfs_zpl_extend.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if p.returncode: raise RuntimeError(p.stdout + p.stderr)
        return binary

    def run_mode(self, mode, binary=None, expected=0):
        p = subprocess.run([str(binary or self.binary), str(mode)], capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
        return p.stdout

    def test_prefix_full4096_initialized_growth_noop_and_all_preflight_denials(self):
        for mode in range(15):
            with self.subTest(mode=mode): self.run_mode(mode)

    def test_assignment_staging_metadata_sync_and_binding_errors_retain_progress(self):
        for mode in range(20, 29):
            with self.subTest(mode=mode): self.run_mode(mode)
        calls = int(re.search(r'calls=(\d+)', self.run_mode(0))[1])
        # Remaining calls are side effects/getters without injected errno APIs.
        for fault in range(1, calls + 1):
            self.run_mode(100 + fault)

    def test_compiling_zero_length_offset_or_growth_guard_omissions_fail93(self):
        for name, old, new, mode in (
                ('zeros', 'zeros[4096] = {0}', 'zeros[4096] = {1}', 0),
                ('length', 'size - node.size, seconds', 'size - node.size - 1, seconds', 0),
                ('offset', 'generation, node.size, zeros', 'generation, 0, zeros', 0),
                ('limit', 'size - node.size > 4096', '0', 4)):
            self.assertEqual(self.body.count(old), 1)
            binary = self.compile(self.body.replace(old, new, 1), name)
            self.run_mode(mode, binary, 93)




class FileSizeProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-size-probe-'); cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name); cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        types = (ROOT / 'tests/fixtures/openzfs_namespace_probe.c').read_text().split('static int attrs[')[0]
        types = types.replace('HOST NAMESPACE oracle95', 'HOST SIZE oracle96').replace('exit(95)', 'exit(96)')
        (cls.out / 'size-types.inc').write_text(types)
        cls.body = '\n'.join(line for line in (OWNED / 'zpl-size-probe.c').read_text().splitlines() if not line.startswith('#include')) + '\n'
        cls.binaries = {(kind, reader): cls.compile(cls.body, kind, reader, str(kind) + str(reader)) for kind in (1, 2, 3) for reader in (0, 1)}

    @classmethod
    def compile(cls, body, kind, reader, name, extra=()):
        (cls.out / 'size-probe.inc').write_text(body); binary = cls.out / name
        p = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-DSZ_KIND=' + str(kind), '-DSZ_READER=' + str(reader), *extra,
            '-I' + str(cls.out), '-I' + str(OWNED), str(ROOT / 'tests/fixtures/openzfs_file_size_probe.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if p.returncode: raise RuntimeError(p.stdout + p.stderr)
        return binary

    def run_mode(self, binary, mode, fault=0, expected=0):
        p = subprocess.run([str(binary), str(mode), str(fault)], capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr); return p.stdout

    def test_six_verifiers_prefix_zeros_patterns_metadata_eof_and_progress_denials(self):
        for (kind, reader), binary in self.binaries.items():
            self.run_mode(binary, 0)
            modes = list(range(1, 15))
            if not reader: modes += [16, 17, 18, 19, 22, 23]
            if not reader and kind == 1: modes += [25]
            if not reader and kind == 2: modes += [24]
            if not reader and kind == 3: modes += [20, 21]
            for mode in modes:
                with self.subTest(kind=kind, reader=reader, mode=mode): self.run_mode(binary, mode)

    def test_every_reachable_api_fault_retains_prior_commits_and_closes(self):
        for key, binary in self.binaries.items():
            calls = int(re.search(r'calls=(\d+)', self.run_mode(binary, 0))[1])
            for fault in range(1, calls + 1):
                with self.subTest(key=key, fault=fault): self.run_mode(binary, 0, fault)

    def test_compiling_missing_hash_eof_timestamp_sync_progress_or_close_fails96(self):
        for name, old, new, kind, reader, mode in (
                ('hash', 'memcmp(digest, size_hashes[phase], sizeof(digest))', '0', 2, 0, 24),
                ('eof', 'i < 2', 'i < 1', 1, 1, 6),
                ('time', 'mtime[0] > 1791290100', '0', 1, 1, 11),
                ('sync', 'result.state != AETHER_ZPL_SYNCED', '0', 1, 0, 19),
                ('retain', 'if (result.txg)\n                *assigned = result.txg;', '*assigned = result.txg;', 3, 0, 21),
                ('advance', 'result.txg <= previous', '((void)previous, !result.txg)', 3, 0, 20),
                ('close', 'if (view)\n        aether_zpl_close(&view);', 'if (0 && view)\n        aether_zpl_close(&view);', 1, 0, 0)):
            self.assertEqual(self.body.count(old), 1, name)
            binary = self.compile(self.body.replace(old, new, 1), kind, reader, name)
            self.run_mode(binary, mode, expected=96)

    def test_oracle_constants_match_independent_zdb_record(self):
        oracle = json.loads((ROOT / 'docs/evidence/zpl-file-sizes-2026-10-19.json').read_text())['independent_oracle']
        self.assertEqual(oracle['status'], 'pass-independent-oracle-only')
        source = (OWNED / 'zpl-size-oracle.h').read_text()
        values = re.findall(r'0x([0-9a-f]{2})', source)
        keys = ['pristine', 'shrink', 'extend', 'first-write', 'repeat']
        self.assertEqual(len(values), 160)
        self.assertEqual([''.join(values[i:i+32]) for i in range(0,160,32)], [oracle['oracle'][key]['sha256'] for key in keys])
        self.assertTrue(oracle['oracle']['removed_interval_was_nonzero'])


if __name__ == '__main__':
    unittest.main()
