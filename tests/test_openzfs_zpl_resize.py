# SPDX-License-Identifier: BSD-2-Clause
"""Private bounded shrink: actual C with faults, then pinned native headers."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

import test_openzfs_zpl_write as writer_tests

ROOT = writer_tests.ROOT
OWNED = writer_tests.OWNED


class ZplShrink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        writer = writer_tests.ZplWriter
        writer.setUpClass()
        cls.addClassCleanup(writer.doClassCleanups)
        cls.out, cls.clang, cls.sdk = writer.out, writer.clang, writer.sdk
        common = (ROOT / 'tests/fixtures/openzfs_zpl_write.c').read_text().split(
            '#include "zpl-adapter.inc"', 1)[0]
        for old, new in (
            ('disk[8192]', 'disk[1048582]'),
            ('tx->assigned && writes == 1 && n == 4 && !updates',
             'tx->assigned && (writes == 1 || shrink_frees == 1) && n == 4 && !updates'),
            ('tx->sa_hold && flags == DMU_TX_WAIT',
             'tx->sa_hold && (tx->data_hold != 2 || netfree == 1) && flags == DMU_TX_WAIT'),
        ):
            if common.count(old) != 1:
                raise RuntimeError('shrink fixture context changed: ' + old)
            common = common.replace(old, new, 1)
        extra = r'''
static void dmu_tx_hold_free(dmu_tx_t *tx, uint64_t object, uint64_t offset,
                             uint64_t length)
{
    CHECK(tx == &transaction && tx_live && !tx->assigned && object == 4 &&
          offset < nodes[4].size && length == nodes[4].size - offset &&
          length <= 1048576);
    tx->data_hold = 2;
    note('F');
}
static void dmu_tx_mark_netfree(dmu_tx_t *tx)
{
    CHECK(tx == &transaction && tx_live && !tx->assigned && tx->data_hold == 2 &&
          tx->sa_hold && !netfree);
    ++netfree;
    note('N');
}
static int dmu_free_range(objset_t *os, uint64_t object, uint64_t offset,
                           uint64_t length, dmu_tx_t *tx)
{
#ifdef AETHER_ZPL_ORDERED_WRITE
    CHECK(joins == 1 && (stage < 7 || stage == 10));
#endif
    CHECK(os == &dataset && object == 4 && tx == &transaction && tx_live &&
          tx->assigned && handles && tx->data_hold == 2 && netfree == 1 &&
          !free_calls && offset <= sizeof(disk) && length <= sizeof(disk) - offset);
    ++free_calls;
    if (stage == 10)
        return ENXIO;
    memset(disk + offset, 0, length);
    ++shrink_frees;
    note('R');
    return 0;
}
'''
        (cls.out / 'zpl-resize-common.inc').write_text(
            'static int shrink_frees, free_calls, netfree;\n' + common + extra)
        setup = (ROOT / 'tests/fixtures/openzfs_zpl_write.c').read_text().split(
            'static void setup(void)', 1)[1].split('\nint main(', 1)[0]
        (cls.out / 'zpl-resize-setup.inc').write_text('static void setup(void)' + setup)
        cls.prefix = '#define AETHER_ZPL_WRITE_PROVIDER 1\n' + writer.read_body + writer.write_body
        cls.body = '\n'.join(line for line in (OWNED / 'zpl-resize.c').read_text().splitlines()
                             if not line.startswith('#include')) + '\n'
        cls.binary = cls.compile(cls.body, 'shrink')

    @classmethod
    def compile(cls, body, name, ordered=False):
        (cls.out / 'zpl-resize-adapter.inc').write_text(cls.prefix + body)
        binary = cls.out / name
        argv = [str(cls.clang), '-isysroot', cls.sdk, '-std=gnu11', '-O2',
                '-Wall', '-Wextra', '-Werror',
                *(['-DAETHER_ZPL_ORDERED_WRITE=1'] if ordered else []),
                '-I' + str(cls.out), '-I' + str(OWNED),
                str(ROOT / 'tests/fixtures/openzfs_zpl_resize.c'), '-o', str(binary)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def modes(self, modes, binary=None):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(binary or self.binary), str(mode)],
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shrink_zero_noop_and_exact_tail_limit(self):
        self.modes(range(4))

    def test_stale_flags_types_bounds_time_readonly_and_metadata_rejections(self):
        self.modes(range(10, 33))

    def test_each_preflight_failure_balances_handles_and_excludes_transaction(self):
        self.modes(range(50, 55))

    def test_abort_and_irreversible_free_sa_and_sync_failures_retain_progress(self):
        self.modes(range(60, 67))

    def test_ordered_binding_precedes_free_and_failure_still_commits(self):
        binary = self.compile(self.body, 'ordered-shrink', ordered=True)
        self.modes([*range(4), *range(10, 33), *range(50, 55), *range(60, 67), 68, 69, 70], binary)

    def test_compiling_omissions_fail_data_progress_and_cleanup_oracles(self):
        for name, old, new, mode in (
            ('stale', 'node.generation != generation', '((void)generation, 0)', 14),
            ('flags', 'flags & (ZFS_IMMUTABLE | ZFS_APPENDONLY | ZFS_READONLY | ZFS_XATTR)', '0', 18),
            ('tail-limit', 'tail > UINT64_C(1048576)', '0', 30),
            ('free-hold', 'dmu_tx_hold_free(tx, object, size, tail);',
             'if (0) dmu_tx_hold_free(tx, object, size, tail);', 0),
            ('netfree', 'dmu_tx_mark_netfree(tx);', 'if (0) dmu_tx_mark_netfree(tx);', 0),
            ('missing-free', 'error = dmu_free_range(view->os, object, size, tail, tx);',
             'if (0) error = dmu_free_range(view->os, object, size, tail, tx);', 0),
            ('wrong-free-range', 'dmu_free_range(view->os, object, size, tail, tx)',
             'dmu_free_range(view->os, object, 0, tail, tx)', 0),
            ('size', 'original_size = size;', 'original_size = node.size;', 0),
            ('assigned-abort', 'dmu_tx_commit(tx);',
             'if (0) dmu_tx_commit(tx); dmu_tx_abort(tx);', 63),
            ('hidden-progress', 'out->state = AETHER_ZPL_COMMITTED;',
             'out->state = AETHER_ZPL_COMMITTED; if (error) memset(out, 0, sizeof(*out));', 63),
            ('early-sync', 'if (!error && spa_last_synced_txg(spa) < out->txg)',
             'if (0 && !error && spa_last_synced_txg(spa) < out->txg)', 65),
        ):
            with self.subTest(omission=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 93, result.stdout + result.stderr)
                self.assertIn('HOST ZPL WRITE oracle93', result.stderr)
                print('ZPL SHRINK semantic rejection:', name, mode, result.stderr.strip())

    def test_pinned_native_headers_imports_and_local_frame(self):
        receipt = json.loads((writer_tests.CURRENT / 'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-176-checked')
        prefix = [writer_tests.route(a) for a in recipe[:recipe.index('-c')]]
        llvm = Path(prefix[0]).parent
        results = {}
        for name in ('zpl-write', 'zpl-resize'):
            obj = self.out / (name + '.o')
            argv = prefix + ['-isystem', str(llvm.parent / 'lib/clang/21/include'),
                             '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-fstack-usage',
                             '-c', str(OWNED / (name + '.c')), '-o', str(obj)]
            result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            symbols = subprocess.check_output([str(llvm / 'llvm-nm'), '-u', str(obj)], text=True)
            imports = {line.split()[-1] for line in symbols.splitlines() if line.strip()}
            results[name] = {'argv': argv, 'bytes': obj.stat().st_size,
                             'sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
                             'imports': sorted(imports), 'stack': obj.with_suffix('.su').read_text()}
        self.assertEqual(results['zpl-write']['sha256'],
                         'e9265dffa274f45267674c33175be42f1afbdc28e0367fd80b6665499d40f116')
        self.assertEqual(set(results['zpl-resize']['imports']) - set(results['zpl-write']['imports']),
                         {'dmu_tx_hold_free', 'dmu_tx_mark_netfree', 'dmu_free_range'})
        self.assertNotIn('dynamic', results['zpl-resize']['stack'])
        frame = next(int(line.split('\t')[1]) for line in results['zpl-resize']['stack'].splitlines()
                     if line.split('\t')[0].endswith(':aether_zpl_shrink'))
        self.assertLessEqual(frame, 1024)
        print('ZPL SHRINK NATIVE ' + json.dumps(results))
