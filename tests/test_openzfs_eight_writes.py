# SPDX-License-Identifier: BSD-2-Clause
"""Fixed eight-record admission, original graph bodies and full guest verifier."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import test_openzfs_pool_repeat as repeat
import test_openzfs_file_sizes as sizes
from openzfs_pool import eight_write_hooks, repeated_write_hooks

ROOT, OWNED = repeat.ROOT, repeat.OWNED


class EightTransactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = repeat.RepeatedTransactions
        cls.base.setUpClass(); cls.addClassCleanup(cls.base.doClassCleanups)
        cls.hooks = eight_write_hooks((OWNED / 'pool-vdev-hooks.inc').read_text())
        cls.binary = cls.compile(cls.hooks, 'eight')

    @classmethod
    def compile(cls, hooks, name):
        out = cls.base.base.output
        (out / 'repeat-flow-base.inc').write_text(cls.base.driver)
        prefix = (ROOT / 'tests/fixtures/openzfs_pool_repeat.c').read_text().split('int main(int argc, char **argv)')[0]
        (out / 'eight-flow-base.inc').write_text(prefix)
        (out / 'pool-bodies.inc').write_text(cls.base.file)
        (out / 'pool-graph-bodies.inc').write_text(cls.base.base.graph)
        (out / 'pool-vdev-hooks.inc').write_text(hooks)
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        binary = out / name
        p = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11', '-O2',
            '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk, '-I'+str(out), '-I'+str(OWNED),
            '-I'+str(ROOT/'tests/fixtures'), str(OWNED/'pool-witness.c'),
            str(ROOT/'tests/fixtures/openzfs_pool_eight.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if p.returncode: raise RuntimeError(p.stdout+p.stderr)
        return binary

    def run_mode(self, binary, mode, expected=0):
        p = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, expected, p.stdout+p.stderr)
        if expected: self.assertIn('pool hook rejection:', p.stderr)

    def test_eight_records_all_positions_ninth_sticky_capacity_retention_and_denials(self):
        for mode in range(39):
            with self.subTest(mode=mode): self.run_mode(self.binary, mode)

    def test_compiling_omissions_fail_for_record_count_wait_identity_and_sticky_capacity(self):
        for name, old, new, mode in (
            ('reuse', 'pool_repeat_records[n].txg', 'pool_repeat_records[0].txg', 0),
            ('count', 'count != POOL_REPEAT_LIMIT', '0', 0),
            ('wait', 'atomic_load_explicit(&previous->synced, memory_order_acquire) <\n                old', '0', 1),
            ('sticky', 'atomic_fetch_or(&pool_problems, AETHER_POOL_CAPACITY);', '(void)0;', 0),
            ('last-target', 'if (requested < target)', 'if (0 && requested < target)', 34),
            ('capacity', 'return ENOSPC;', 'return EINVAL;', 0)):
            with self.subTest(name=name):
                self.assertEqual(self.hooks.count(old), 1)
                self.run_mode(self.compile(self.hooks.replace(old,new,1),name),mode,1)

    def test_default_observer_exact_and_changed_budget_count_or_duplicate_context_rejected(self):
        original = (OWNED/'pool-vdev-hooks.inc').read_text()
        prior = json.loads((ROOT/'docs/evidence/zpl-file-sizes-2026-10-19.json').read_text())
        digest = prior['native']['report']['builds']['repeat/writer']['namespace_objects']['vdev-write-hooks-source']
        self.assertEqual(hashlib.sha256(repeated_write_hooks(original).encode()).hexdigest(),digest)
        for changed in (original+original, original.replace('8192,','8193,')):
            with self.assertRaises(ValueError): eight_write_hooks(changed)
        real = Path.read_text
        def changed(path, *args, **kwargs):
            value = real(path,*args,**kwargs)
            return value.replace('#define POOL_REPEAT_LIMIT 2','#define POOL_REPEAT_LIMIT 3') if path.name=='pool-repeat.inc' else value
        with patch.object(Path,'read_text',changed):
            with self.assertRaises(ValueError): eight_write_hooks(original)


class EightProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=sizes.FileSizeProbe;cls.base.setUpClass();cls.addClassCleanup(cls.base.doClassCleanups)
        cls.body=cls.base.body
        cls.binaries={reader:cls.compile(cls.body,reader,'eight-probe'+str(reader)) for reader in (0,1)}

    @classmethod
    def compile(cls,body,reader,name):
        return cls.base.compile(body,3,reader,name,('-DSZ_EIGHT=1',))

    def test_full_eight_write_or_recovery_denials_and_every_reachable_api_fault(self):
        for reader,binary in self.binaries.items():
            out=self.base.run_mode(self,binary,0);calls=int(re.search(r'calls=(\d+)',out)[1])
            modes=[*range(1,15)]
            if not reader:modes += [16,17,18,19,20,21,22,23,26,27,28,29,30]
            for mode in modes:
                with self.subTest(reader=reader,mode=mode):self.base.run_mode(self,binary,mode)
            for fault in range(1,calls+1):
                with self.subTest(reader=reader,fault=fault):self.base.run_mode(self,binary,0,fault)

    def test_omitted_eighth_write_last_hash_eof_or_retained_progress_fails96(self):
        for name,old,new,mode in (
            ('seven','part < loops','part + 1 < loops',0),
            ('old-hash','memcmp(digest, size_hashes[phase], sizeof(digest))','0',27),
            ('old-eof','i < 2','i < 1',6),
            ('last-progress','if (result.txg)\n                *assigned = result.txg;','*assigned = result.txg;',26),
            ('last-target','result.txg <= previous','((void)previous, !result.txg)',28)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old),1)
                self.base.run_mode(self,self.compile(self.body.replace(old,new,1),0,name),mode,expected=96)

    def test_eleven_hashes_match_independent_original_zdb_recipe(self):
        r=json.loads((ROOT/'docs/evidence/zpl-eight-writes-2026-10-19.json').read_text())['independent_oracle']
        self.assertEqual(r['status'],'pass-independent-oracle-only')
        values=re.findall(r'0x([0-9a-f]{2})',(OWNED/'zpl-eight-oracle.h').read_text())
        self.assertEqual(len(values),352)
        self.assertEqual([''.join(values[i:i+32]) for i in range(0,352,32)], [v['sha256'] for v in r['eight_oracle']])
        self.assertEqual([v['bytes'] for v in r['eight_oracle']],[780248,65539,69635]+[69635+4096*n for n in range(1,9)])


if __name__=='__main__':unittest.main()
