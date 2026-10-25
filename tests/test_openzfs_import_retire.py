# SPDX-License-Identifier: BSD-2-Clause
"""Actual original eviction/control flow over synthetic namespace/helper state."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from openzfs_elapsed import CURRENT, function


class ReadonlyImportRetirement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-import-retire-')
        cls.addClassCleanup(cls.temporary.cleanup)
        out = Path(cls.temporary.name)
        original = (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/spa.c').read_text()
        eviction = function(original, 'spa_evict_all')
        if hashlib.sha256(eviction.encode()).hexdigest() != '507e3c7fdd6dfc6fe17827fcfa2869fcddfc7a58585e40354a8946a8f9802f00':
            raise AssertionError('original eviction body drift')
        owned = (ROOT / 'user/storage/openzfs-volume/spa-import.inc').read_text()
        retire = function(owned, 'aether_spa_import_retire')
        cls.owned = owned
        original_dbuf = (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/dbuf.c').read_text()
        wait = function(original_dbuf, 'dmu_buf_user_evict_wait')
        if hashlib.sha256(wait.encode()).hexdigest() != '44b095c2da3ed50e0bd12ccb0bd6d0a18034f59d0634be60b65a5161000f08e6':
            raise AssertionError('original user eviction wait body drift')
        # Preserve the original CDDL/copyright preface in temporary extracted code.
        preface = original[:original.index('#include')]
        scaffold = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define FTAG ((void *)7)
#define POOL_STATE_UNINITIALIZED 0
typedef struct spa {
    int spa_state, refs, writable, suspended;
    const char *name;
} spa_t;
static spa_t expected_pool = {1, 0, 0, 0, "aether_pool_probe"};
static spa_t foreign_pool = {1, 0, 0, 0, "foreign"};
static spa_t *first, *second;
static int mode, locked, evictions, holds, suspends, unloads, deactivations, removals;
static int user_waits;
static void *dbu_evict_taskq = (void *)9;
static void require(int ok) {
    if (!ok) { fputs("HOST RETIRE oracle91\n", stderr); exit(91); }
}
static void taskq_wait(void *queue) {
    require(queue == dbu_evict_taskq && !locked);
    ++user_waits;
    if (mode == 8) expected_pool.refs = 0; /* Queued async hold release. */
}
static void spa_namespace_enter(void *tag) {
    require(tag == FTAG && !locked); locked = 1;
}
static void spa_namespace_exit(void *tag) {
    require(tag == FTAG && locked); locked = 0;
}
static spa_t *spa_lookup(const char *name) {
    require(locked);
    if (first && !strcmp(first->name, name)) return first;
    if (second && !strcmp(second->name, name)) return second;
    return NULL;
}
static spa_t *spa_next(spa_t *previous) {
    require(locked);
    return previous == NULL ? first : previous == first ? second : NULL;
}
static int spa_writeable(spa_t *spa) { require(locked && spa); return spa->writable; }
static int spa_refcount_zero(spa_t *spa) { require(locked && spa); return !spa->refs; }
static void spa_open_ref(spa_t *spa, void *tag) {
    require(locked && spa && tag == FTAG); ++spa->refs; ++holds;
}
static void spa_async_suspend(spa_t *spa) {
    require(!locked && spa && spa->refs > 0 && !spa->suspended);
    spa->suspended = 1; ++suspends;
}
static void spa_close(spa_t *spa, void *tag) {
    require(locked && tag == FTAG && spa->suspended && spa->refs > 0); --spa->refs;
}
static void spa_unload(spa_t *spa) {
    require(locked && spa->suspended && !spa->refs && spa->spa_state == 1);
    ++unloads;
}
static void spa_deactivate(spa_t *spa) {
    require(locked && spa->suspended && !spa->refs && unloads == deactivations + 1);
    spa->spa_state = POOL_STATE_UNINITIALIZED; ++deactivations;
}
static void spa_remove(spa_t *spa) {
    require(locked && spa == first && !spa->refs && !spa->spa_state && spa->suspended);
    first = second; second = NULL; ++removals;
}
'''
        wrapper = '''
static void spa_evict_all(void) {
    ++evictions;
    original_spa_evict_all();
    if (mode == 5) first = &foreign_pool; /* Synthetic retained namespace entry. */
}
'''
        main = r'''
int main(int argc, char **argv) {
    (void)spa_writeable; (void)spa_refcount_zero; /* Mutation-only unused stubs. */
    require(argc == 2); mode = atoi(argv[1]); first = &expected_pool;
    if (mode == 1) first = NULL;
    if (mode == 2) second = &foreign_pool;
    if (mode == 3) expected_pool.writable = 1;
    if (mode == 4) expected_pool.refs = 1;
    if (mode == 6) first = &foreign_pool;
    if (mode == 7) expected_pool.spa_state = POOL_STATE_UNINITIALIZED;
    if (mode == 8 || mode == 9) {
        expected_pool.refs = 1;
        dmu_buf_user_evict_wait();
    }
    int result = aether_spa_import_retire();
    require(!locked);
    require(user_waits == (mode == 8 || mode == 9));
    if (mode == 0 || mode == 7 || mode == 8) {
        require(result == 0 && !first && !second && evictions == 1);
        require(holds == 1 && suspends == 1 && removals == 1);
        require(unloads == (mode == 0 || mode == 8) && deactivations == unloads);
    } else if (mode == 5) {
        require(result == 873 && first == &foreign_pool && evictions == 1 && removals == 1);
    } else {
        require(result == 873 && !evictions && !holds && !suspends && !unloads && !removals);
    }
    puts("HOST RETIRE PASS"); return 0;
}
'''
        cls.binaries = {}
        variants = {'healthy': retire,
                    'omit-exclusive': retire.replace(' && spa_next(pool) == NULL', '', 1),
                    'omit-readonly': retire.replace('!spa_writeable(pool) && ', '', 1),
                    'omit-unreferenced': retire.replace(' && spa_refcount_zero(pool)', '', 1),
                    'omit-empty': retire.replace('int remaining = spa_next(NULL) != NULL;', 'int remaining = 0;', 1),
                    'omit-user-wait': retire}
        for name, body in variants.items():
            if name not in ('healthy', 'omit-user-wait') and body == retire:
                raise AssertionError('mutation anchor drift: ' + name)
            path = out / (name + '.c')
            actual_wait = wait if name != 'omit-user-wait' else wait.replace('taskq_wait(dbu_evict_taskq);', '(void)taskq_wait; (void)dbu_evict_taskq; ++user_waits;', 1)
            path.write_text(preface + scaffold + actual_wait + eviction.replace('spa_evict_all(', 'original_spa_evict_all(', 1) + wrapper + body + main)
            binary = out / name
            result = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                                     str(path), '-o', str(binary)],
                                    capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise AssertionError(result.stderr)
            cls.binaries[name] = binary

    def run_mode(self, mode, name='healthy'):
        return subprocess.run([str(self.binaries[name]), str(mode)], capture_output=True,
                              text=True, timeout=5)

    def test_actual_original_retirement_and_uninitialized_removal(self):
        for mode in (0, 7):
            result = self.run_mode(mode)
            self.assertEqual((result.returncode, result.stdout, result.stderr),
                             (0, 'HOST RETIRE PASS\n', ''))

    def test_absent_additional_writable_referenced_or_foreign_reject_before_effects(self):
        for mode in (1, 2, 3, 4, 6):
            result = self.run_mode(mode)
            self.assertEqual((result.returncode, result.stdout, result.stderr),
                             (0, 'HOST RETIRE PASS\n', ''))

    def test_namespace_must_be_empty_after_original_eviction(self):
        result = self.run_mode(5)
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, 'HOST RETIRE PASS\n', ''))

    def test_compiling_guard_omissions_fail_named_oracle(self):
        for name, mode in [('omit-exclusive', 2), ('omit-readonly', 3),
                           ('omit-unreferenced', 4), ('omit-empty', 5)]:
            result = self.run_mode(mode, name)
            self.assertEqual((result.returncode, result.stderr), (91, 'HOST RETIRE oracle91\n'))

    def test_importer_closes_borrow_before_retirement_and_uses_no_export(self):
        probe = function(self.owned, 'aether_spa_import_probe')
        self.assertLess(probe.index('spa_close(spa, FTAG)'), probe.index('aether_spa_import_retire()'))
        self.assertLess(probe.index('aether_spa_import_retire()'), probe.index("aether_engine_utc_phase('D')"))
        self.assertNotIn('spa_export(', probe)

    def test_original_user_queue_drain_releases_async_but_not_client_holds(self):
        for mode in (8, 9):
            result = self.run_mode(mode)
            self.assertEqual((result.returncode, result.stdout, result.stderr),
                             (0, 'HOST RETIRE PASS\n', ''))
        result = self.run_mode(8, 'omit-user-wait')
        self.assertEqual((result.returncode, result.stderr), (91, 'HOST RETIRE oracle91\n'))

    def test_data_only_wait_after_closed_borrows_before_guard(self):
        probe = function(self.owned, 'aether_spa_import_probe')
        data = probe.split('#ifdef AETHER_POOL_DATA', 1)[1].split('#else', 1)[0]
        self.assertLess(data.rindex('spa_close(spa, FTAG)'), data.index('dmu_buf_user_evict_wait();'))
        self.assertEqual(probe.count('dmu_buf_user_evict_wait();'), 1)
        self.assertLess(probe.index('dmu_buf_user_evict_wait();'), probe.index('aether_spa_import_retire()'))
