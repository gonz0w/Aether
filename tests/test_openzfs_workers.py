# SPDX-License-Identifier: BSD-2-Clause
"""Source-selected queue sizing/progress; no native resource/durability claim."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import CURRENT, function, route
from openzfs_volume import patch_pool_workers

UPSTREAM = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1'


class PoolWorkers(unittest.TestCase):
    def test_exact_free_floor_and_context_drift(self):
        original = (UPSTREAM / 'module/zfs/spa.c').read_text()
        selected, edits = patch_pool_workers(original)
        self.assertEqual(len(edits), 1)
        edit = edits[0]
        self.assertEqual(selected.replace(edit['new'], edit['old'], 1), original)
        self.assertEqual(original.count('VERIFY'), selected.count('VERIFY'))
        for changed in (original.replace(edit['old'], '', 1), original + edit['old']):
            with self.assertRaises(RuntimeError): patch_pool_workers(changed)

    def test_selected_sources_match_actual_checked_slots(self):
        receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
        for index, expected in ((1, 'profile/source'), (90, 'baseline/source')):
            recipe = next(row['argv'] for row in receipt['commands']
                          if row['name'] == f'input-{index}-checked')
            source = Path(route(recipe[recipe.index('-c')+1]))
            row = next(row for row in receipt['objects'] if row['index']==index)
            original_path = recipe[recipe.index('-c')+1]
            self.assertTrue(str(source).startswith(str(CURRENT / expected)))
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                             row['dependencies'][original_path])
        # Executed globals already differ from upstream defaults; never silently
        # base a budget on the unselected baseline copy.
        taskq = (CURRENT/'profile/source'/UPSTREAM.name/'lib/libzpool/taskq.c').read_text()
        self.assertIn('taskq_create("system_taskq", 1, maxclsyspri, 4,',taskq)
        self.assertIn('taskq_create("delay_taskq", 1, maxclsyspri, 4,',taskq)
        self.assertNotIn('taskq_create("system_taskq", 64,',taskq)

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-pool-workers-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name)
        (cls.output / 'sys').mkdir()
        (cls.output / 'sys/zfs_context.h').write_text('/* Types are extracted below. */\n')
        taskq = (CURRENT/'profile/source'/UPSTREAM.name/'lib/libzpool/taskq.c').read_text()
        # Same established resource-wrapper CPU substitution as the real builder.
        if taskq.count('sysconf(_SC_NPROCESSORS_ONLN)') != 1:
            raise RuntimeError('taskq assigned CPU context changed')
        taskq = taskq.replace('sysconf(_SC_NPROCESSORS_ONLN)', 'aether_zfs_assigned_cpus()', 1)
        context = (UPSTREAM / 'include/sys/zfs_context.h').read_text()
        types = context[context.index('#define\tTASKQ_NAMELEN'):context.index('extern taskqid_t taskq_dispatch_delay')]
        spa, _ = patch_pool_workers((UPSTREAM / 'module/zfs/spa.c').read_text())
        table = spa[spa.index('typedef enum zti_modes {'):spa.index('static void spa_sync_version')]
        mock = '''
#define ZIO_TYPES 7
#define ZIO_TASKQ_TYPES 4
#define ZIO_TYPE_WRITE 2
#define ZIO_TASKQ_ISSUE 0
#define boot_ncpus 1
static uint_t zio_taskq_batch_pct=80, zio_taskq_batch_tpq=0, zio_taskq_write_tpq=0;
static const char *zio_type_name[7]={"null","read","write","free","claim","flush","trim"};
typedef int zio_type_t;
typedef int zio_taskq_type_t;
typedef struct {unsigned stqs_count;taskq_t **stqs_taskq;} spa_taskqs_t;
typedef struct {unsigned spa_alloc_count;void *spa_proc;spa_taskqs_t spa_zio_taskq[7][4];} spa_t;
'''
        # Functions with non-void signatures are selected by explicit boundaries.
        bodies = types + '\n' + taskq + '\n' + mock + table
        bodies += '\n' + function(spa, 'spa_taskqs_init') + '\n' + function(spa, 'spa_taskqs_fini')
        cls.bodies_sha256 = hashlib.sha256(bodies.encode()).hexdigest()
        for name, source in (('selected', bodies), ('broken-wait', bodies.replace(
                function(taskq, 'taskq_wait'), 'void taskq_wait(taskq_t *tq) {(void)tq;}', 1))):
            (cls.output / 'selected-queue-bodies.inc').write_text(source)
            result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                                     '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-pthread',
                                     '-I' + str(cls.output), str(Path(__file__).parent/'fixtures/openzfs_pool_workers.c'),
                                     '-o', str(cls.output/name)], capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)

    def test_actual_distinct_queue_wait_and_drain(self):
        result = subprocess.run([str(self.output/'selected'), '0'], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_actual_all_pool_queue_sizes_dispatch_and_fini(self):
        result = subprocess.run([str(self.output/'selected'), '2'], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_merged_completion_queue_cannot_pass(self):
        result = subprocess.run([str(self.output/'selected'), '1'], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 99, result.stderr)

    def test_premature_wait_return_mutation_is_rejected(self):
        result = subprocess.run([str(self.output/'broken-wait'), '0'], capture_output=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(result.returncode, (90, 98))
