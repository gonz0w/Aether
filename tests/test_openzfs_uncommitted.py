# SPDX-License-Identifier: BSD-2-Clause
"""Actual dirty-tx helper over synthetic DMU ownership; no crash/durability claim."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from openzfs_elapsed import CURRENT
from openzfs_pool import pool_transaction_body


class UncommittedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-uncommitted-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join(line for line in
                             (ROOT / 'user/storage/openzfs-volume/pool-data.c').read_text().splitlines()
                             if not line.startswith('#include')) + '\n'
        original = (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/dmu_tx.c').read_text()
        (cls.out / 'original-getter.inc').write_text(pool_transaction_body(original, 'dmu_tx_get_txg'))
        # Reuse synthetic calls, not an alternative implementation of the helper.
        cls.scaffold = (ROOT / 'tests/fixtures/openzfs_pool_data.c').read_text().split('#include "data-helper.inc"')[0]
        cls.scaffold = cls.scaffold.replace('binds == 1 && flags == 1', 'binds == 0 && flags == 1')
        cls.binary = cls.compile(cls.body, 'normal')

    @classmethod
    def compile(cls, body, name):
        main = r'''
#include <setjmp.h>
static jmp_buf paused;
static int checkpoints, scenario;
int aether_engine_pool_uncommitted(uint64_t candidate) {
    unsigned char expected[64]; aether_data_record(expected,17);
    require(scenario<2 && owned && os.spa==&spa && tx.live && tx.tx_txg==17 && candidate==17);
    require(!commits && !aborts && writes==1 && !waits && !binds && !reads);
    require(!memcmp(media,expected,64) && !strcmp(events,"OTHAW"));
    ++checkpoints;
    if (scenario==1) return 872;
    longjmp(paused,1);
}
int main(int argc,char **argv) {
    require(argc==2); scenario=atoi(argv[1]); uint64_t baseline=16;
    mode=scenario==2?5:scenario==3?3:scenario==4?4:0;
    if (scenario==4) os.spa=&foreign;
    if (scenario==5) spa.writable=0;
    if (scenario==6) spa.name="foreign";
    if (scenario==7) baseline=17;
    if (scenario==8) baseline=20;
    if (scenario==9) baseline=0;
    if (!setjmp(paused)) {
        int error=aether_pool_data_hold(scenario==10?NULL:&spa,baseline);
        int expected=scenario==1?EIO:scenario==2?ENOSPC:scenario==3?ENOENT:scenario==4?EXDEV:EINVAL;
        require(scenario && error==expected && !owned && !tx.live && !waits && !reads && !binds);
        require(commits==(scenario==1 || scenario==7) && aborts==(scenario==2));
        require(writes==(scenario==1) && checkpoints==(scenario==1));
        if (scenario>=8 || scenario==5 || scenario==6) require(!count);
    } else {
        require(!scenario && checkpoints==1 && owned && tx.live && !commits && !aborts);
    }
    puts("HOST UNCOMMITTED PASS"); return 0;
}
'''
        source = cls.out / (name + '.c')
        source.write_text('#define AETHER_POOL_UNCOMMITTED 1\n' + cls.scaffold + '\n' + body + main)
        binary = cls.out / name
        r = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11', '-O2',
                            '-Wall', '-Wextra', '-Werror', '-I', str(cls.out), str(source), '-o', str(binary)],
                           capture_output=True, timeout=30)
        if r.returncode:
            raise RuntimeError(r.stderr.decode())
        return binary

    def check(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                r = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b'HOST UNCOMMITTED PASS\n', b''))

    def test_dirty_candidate_stays_assigned_owned_and_uncommitted(self):
        self.check((0,))

    def test_checkpoint_error_commits_only_for_release_and_returns_failure(self):
        self.check((1,))

    def test_unassigned_abort_and_assigned_ordering_error_release(self):
        self.check((2, 3, 7))

    def test_spa_identity_rights_baseline_and_null_denials(self):
        self.check((4, 5, 6, 8, 9, 10))

    def test_compiling_omissions_fail_held_transaction_oracle(self):
        changes = (
            ('early-commit', '(void)aether_engine_pool_uncommitted(candidate);',
             'dmu_tx_commit(tx); (void)aether_engine_pool_uncommitted(candidate);', 0),
            ('wrong-target', '(void)aether_engine_pool_uncommitted(candidate);',
             '(void)aether_engine_pool_uncommitted(candidate + 1);', 0),
            ('missing-write', 'dmu_write(os, AETHER_DATA_OBJECT, 0, sizeof(record), record, tx,\n                  DMU_READ_NO_PREFETCH);',
             '(void)record;', 0),
            ('old-target', 'if (candidate > baseline)', 'if (1)', 7),
            ('foreign', 'if (dmu_objset_spa(os) != spa)', 'if (0)', 4),
            ('release', '    dmu_tx_commit(tx);\n    dmu_objset_disown(os, B_FALSE, FTAG);\n    return error;',
             '    dmu_objset_disown(os, B_FALSE, FTAG);\n    return error;', 1),
        )
        for name, old, new, mode in changes:
            with self.subTest(name=name):
                start = self.body.index('int aether_pool_data_hold(')
                end = self.body.index('\n#endif', start)
                hold = self.body[start:end]
                self.assertEqual(hold.count(old), 1)
                binary = self.compile(self.body[:start] + hold.replace(old, new) + self.body[end:], name)
                r = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual((r.returncode, r.stderr), (92, b'HOST DATA oracle92\n'))
