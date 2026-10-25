# SPDX-License-Identifier: BSD-2-Clause
"""Actual private checkpoint boundary over sleep/observer scaffolding; no VM."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PoolCheckpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-checkpoint-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        text = (ROOT / 'user/storage/openzfs-volume/spa-pool.inc').read_text()
        start = '  spa_close(spa, FTAG);\n#ifdef AETHER_POOL_INTERRUPT'
        end = '  nvlist_t *exported = NULL, *tree = NULL;'
        if text.count(start) != 1 or text.count(end) != 1:
            raise AssertionError('checkpoint boundary context drift')
        cls.boundary = text[text.index(start):text.index(end)]
        cls.checkpoint = (ROOT / 'user/storage/service-runtime/pool-checkpoint.inc').read_text()
        cls.binary = cls.compile(cls.boundary, 'normal')

    @classmethod
    def compile(cls, boundary, name):
        scaffold = r'''
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define AETHER_POOL_INTERRUPT 1
#define AETHER_POOL_DATA 1
#define FTAG 0
static jmp_buf stopped;
static int mode, closed, checked, observed, sleeps;
typedef struct { int unused; } spa_t;
static void require(int ok) {
    if (!ok) { fputs("HOST CHECKPOINT oracle93\n", stderr); exit(93); }
}
static void spa_close(spa_t *spa, int tag) {
    require(spa && !tag && !closed); ++closed;
}
static unsigned __attribute__((unused)) aether_pool_hooks_check_ordered(void) {
    require(closed && !checked); ++checked;
    return mode==2 ? 16 : 0;
}
static void engine_observe(unsigned char phase) {
    require(closed && checked && mode!=2 && phase=='K' && !observed);
    ++observed;
}
static int pause_call(const struct timespec *pause, struct timespec *remaining) {
    require(observed && !remaining && pause->tv_sec==0 && pause->tv_nsec==1000000);
    ++sleeps;
    if (mode==1) return -1;
    if (sleeps==3) longjmp(stopped,1);
    return 0;
}
#define nanosleep pause_call
'''
        main = r'''
int main(int argc, char **argv) {
    require(argc==2); mode=atoi(argv[1]);
    if (setjmp(stopped)) {
        require(mode==0 && closed==1 && checked==1 && observed==1 && sleeps==3);
    } else {
        int result=exercise();
        require(result==872 && closed==1 && checked==1);
        require(mode==1 ? observed==1 && sleeps==1 : mode==2 && !observed && !sleeps);
    }
    puts("HOST CHECKPOINT PASS"); return 0;
}
'''
        source = cls.out / (name + '.c')
        source.write_text(scaffold + cls.checkpoint +
                          '\nstatic int exercise(void) { spa_t pool={0}; spa_t *spa=&pool;\n' +
                          boundary + '\nreturn 799;\n}\n' + main)
        binary = cls.out / name
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11',
                                 '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(binary)],
                                capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        return binary

    def check(self, mode):
        result = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, b'HOST CHECKPOINT PASS\n', b''))

    def test_success_closes_borrow_checks_order_then_stays_parked(self):
        self.check(0)

    def test_sleep_failure_never_reaches_export(self):
        self.check(1)

    def test_ordered_failure_never_emits_checkpoint(self):
        self.check(2)

    def test_omitted_ordered_check_fails_named_checkpoint_oracle(self):
        anchor = 'if (aether_pool_hooks_check_ordered())'
        self.assertEqual(self.boundary.count(anchor), 1)
        binary = self.compile(self.boundary.replace(anchor, 'if (0)', 1), 'omitted-check')
        result = subprocess.run([str(binary), '2'], capture_output=True, timeout=5)
        self.assertEqual((result.returncode, result.stderr), (93, b'HOST CHECKPOINT oracle93\n'))

    def test_actual_uncommitted_checkpoint_emits_candidate_before_park(self):
        scaffold = r'''
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define ENGINE_POOL_UNCOMMITTED 1
static jmp_buf stopped;
static unsigned count, sleeps;
static int fail;
static void require(int ok) { if (!ok) { fputs("HOST CHECKPOINT oracle93\n",stderr); exit(93); } }
static void engine_observe(unsigned char byte) {
    const unsigned char expected[]={ 'H',1,2,3,4,5,6,7,8,'K' };
    require(count<sizeof(expected) && byte==expected[count]); ++count;
}
static int pause_call(const struct timespec *pause, struct timespec *remaining) {
    require(count==10 && !remaining && pause->tv_sec==0 && pause->tv_nsec==1000000);
    ++sleeps; if (fail) return -1; longjmp(stopped,1);
}
#define nanosleep pause_call
'''
        main = r'''
int main(int argc,char **argv) {
    require(argc==2); fail=atoi(argv[1]);
    if (!setjmp(stopped)) {
        int result=aether_engine_pool_uncommitted(UINT64_C(0x0807060504030201));
        require(fail && result==872);
    }
    require(count==10 && sleeps==1); puts("HOST CHECKPOINT PASS"); return 0;
}
'''
        source = self.out / 'uncommitted.c'; binary = self.out / 'uncommitted'
        source.write_text(scaffold + self.checkpoint + main)
        r = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=c11','-O2',
                            '-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],capture_output=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stderr)
        for mode in ('0','1'):
            r=subprocess.run([str(binary),mode],capture_output=True,timeout=5)
            self.assertEqual((r.returncode,r.stdout,r.stderr),(0,b'HOST CHECKPOINT PASS\n',b''))
