# SPDX-License-Identifier: BSD-2-Clause
"""Actual selected caller arithmetic/errors with controlled host providers.

These execute extracted C functions, not a model or a full tpool lifecycle.
Native actual-musl/thread qualification remains a separate required check.
"""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import CURRENT, OWNED, PINS, function, patch_kernel, patch_tpool, declarations, adapt_fixture, check_intermediate_imports

HARNESS = r'''
#include <pthread.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include <errno.h>
#define NANOSEC 1000000000LL
#define CALLOUT_FLAG_ABSOLUTE 2
#define VERIFY0(x) do { if ((x) != 0) _Exit(125); } while (0)
typedef long long hrtime_t;
typedef long test_clock_t;
#define clock_t test_clock_t
typedef pthread_cond_t kcondvar_t;
typedef struct { pthread_mutex_t m_lock; pthread_t m_owner; } kmutex_t;
static kmutex_t mutex;
static hrtime_t source = 1000000000LL, jump;
static unsigned reads, calls, sleeps, attrs, destroyed;
static int error, clock_error, init_error;
static clockid_t selected_clock;
static struct timespec captured;
static hrtime_t gethrtime(void) { hrtime_t result=source; source+=jump; ++reads; return result; }
#define ddi_get_lbolt() (gethrtime() >>23)
static int mock_wait(pthread_cond_t *cv, pthread_mutex_t *lock, const struct timespec *at) {
    (void)cv;
    if (lock == &mutex.m_lock && mutex.m_owner != 0) _Exit(90);
    captured=*at; ++calls; return error;
}
static int mock_sleep(const struct timespec *at, struct timespec *rem) {
    if (rem) _Exit(91); captured=*at; ++sleeps; return error;
}
static int mock_attr_init(pthread_condattr_t *attr) { (void)attr; ++attrs; return init_error; }
static int mock_attr_clock(pthread_condattr_t *attr, clockid_t clock) { (void)attr; selected_clock=clock; return init_error; }
static int mock_attr_destroy(pthread_condattr_t *attr) { (void)attr; ++destroyed; return init_error; }
static int mock_init(pthread_cond_t *cv, const pthread_condattr_t *attr) { (void)cv; if (!attr) _Exit(92); return init_error; }
static int mock_clock(clockid_t clock, struct timespec *ts) {
    selected_clock=clock; *ts=captured; return clock_error;
}
#define pthread_cond_timedwait mock_wait
#define nanosleep mock_sleep
#define pthread_condattr_init mock_attr_init
#define pthread_condattr_setclock mock_attr_clock
#define pthread_condattr_destroy mock_attr_destroy
#define pthread_cond_init mock_init
#define clock_gettime mock_clock
'''

MAIN = r'''
static unsigned long long ns(struct timespec at) { return at.tv_sec*1000000000ULL+at.tv_nsec; }
#define CHECK(x) do { if (!(x)) return __LINE__ % 120 + 1; } while (0)
int main(int argc, char **argv) {
    if (argc != 2) return 94;
    int mode=atoi(argv[1]); kcondvar_t cv;
    mutex.m_owner=pthread_self(); error=ETIMEDOUT;
    if (mode == 0) {
        cv_init(&cv,0,0,0);
        CHECK(selected_clock==CLOCK_MONOTONIC && attrs==1 && destroyed==1);
        jump=333000000;
        CHECK(cv_timedwait_hires(&cv,&mutex,1400000000,1,2)==-1);
        CHECK(ns(captured)==1400000000 && reads==1 && calls==1 && mutex.m_owner==pthread_self());
    } else if (mode == 1) {
        CHECK(cv_timedwait_hires(&cv,&mutex,150000000,1,0)==-1);
        CHECK(ns(captured)==1150000000 && reads==1 && mutex.m_owner==pthread_self());
    } else if (mode == 2) {
        CHECK(cv_timedwait(&cv,&mutex,130)==-1);
        CHECK(ns(captured)==130ULL*8388608 && mutex.m_owner==pthread_self());
        CHECK(cv_timedwait(&cv,&mutex,LONG_MIN)==-1 && calls==1);
    } else if (mode == 3) {
        CHECK(cv_timedwait_hires(&cv,&mutex,source,1,2)==-1);
        CHECK(cv_timedwait_hires(&cv,&mutex,0,1,0)==-1);
        CHECK(calls==0 && mutex.m_owner==pthread_self());
    } else if (mode == 4) { error=0;
        delay(0); CHECK(!sleeps); delay(8);
        CHECK(ns(captured)==67108864 && sleeps==1);
    } else if (mode == 5) { error=0;
        CHECK(cv_timedwait_hires(&cv,&mutex,30000000,1,0)==1 && mutex.m_owner==pthread_self());
    } else if (mode == 6) { error=EIO; cv_timedwait_hires(&cv,&mutex,1000000,1,0);
    } else if (mode == 7) { source=LLONG_MAX-10; cv_timedwait_hires(&cv,&mutex,20,1,0);
    } else if (mode == 8) { cv_timedwait_hires(&cv,&mutex,1,1,1);
    } else if (mode == 9) { cv_timedwait(&cv,&mutex,(LLONG_MAX >>23)+1);
    } else if (mode == 10) { delay(-1);
    } else if (mode == 11) { delay((LLONG_MAX >>23)+1);
    } else if (mode == 12) { error=EINTR; delay(8);
    } else if (mode == 13) { init_error=ENOTSUP; cv_init(&cv,0,0,0);
    } else if (mode == 14) { struct timespec at; cv_deadline(LLONG_MAX/NANOSEC+1,0,&at);
    } else if (mode == 15) { struct timespec at; cv_deadline(0,NANOSEC,&at);
    } else if (mode == 16) { aether_tpool_cond_init(&cv);
        CHECK(selected_clock==CLOCK_MONOTONIC && destroyed==1);
        captured=(struct timespec){4,999999999};
        CHECK(ns(test_deadline(2))==6999999999ULL && selected_clock==CLOCK_MONOTONIC);
        CHECK(test_wait(ETIMEDOUT)==1 && test_wait(0)==0);
    } else if (mode == 17) { test_wait(EIO);
    } else if (mode == 18) { clock_error=ENOTSUP; test_deadline(1);
    } else if (mode == 19) { captured=(struct timespec){LLONG_MAX,0}; test_deadline(1);
    } else if (mode == 20) { init_error=EINVAL; aether_tpool_cond_init(&cv);
    } else if (mode == 21) { captured=(struct timespec){0,NANOSEC}; test_deadline(1);
    } else return 95;
    if (mode >= 6 && mode <= 15) return 96;
    if (mode >= 17) return 97;
    return 0;
}
'''


class OpenZFSElapsedTests(unittest.TestCase):
    def test_physical_intermediate_hook_is_exact_and_weak(self):
        base = '                 U _DYNAMIC\n'
        hook = '                 w aether_physical_io_phase\n'
        check_intermediate_imports(base)
        check_intermediate_imports(base + hook, physical=True)
        for imports, physical in ((base + hook, False),
                                  (base + hook.replace('w ', 'U '), True),
                                  (base + hook.replace('io_phase', 'other'), True),
                                  (base + ' U ambient_provider\n', True)):
            with self.subTest(imports=imports, physical=physical), self.assertRaises(RuntimeError):
                check_intermediate_imports(imports, physical=physical)

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zfs-caller-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        kernel = (CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        tpool = (CURRENT / 'previous-build/source/thread_pool.c').read_text()
        for p, h in PINS.items():
            if hashlib.sha256((CURRENT / p).read_bytes()).hexdigest() != h:
                raise RuntimeError('selected caller pin drift')
        cls.kernel, cls.tpool = kernel, tpool
        changed, _ = patch_tpool(tpool)
        helper = function(changed, 'aether_tpool_cond_init')
        start = changed.index('\t\t\t\tstruct timespec ts;')
        end = changed.index('\n\n\t\t\t\tint wait_error', start)
        deadline = 'static struct timespec test_deadline(unsigned linger) { struct { unsigned tp_linger; } pool={linger}; __typeof(pool) *tpool=&pool;\n' + changed[start:end] + '\nreturn ts; }\n'
        start = changed.index('\t\t\t\tint wait_error')
        end = changed.index('\n\t\t\t}', start)
        wait = 'static int test_wait(int code) { pthread_cond_t cv; struct { pthread_cond_t tp_workcv; pthread_mutex_t tp_mutex; } pool; __typeof(pool) *tpool=&pool; struct timespec ts={0}; int elapsed=0; (void)cv; error=code; do {\n' + changed[start:end] + '\n} while(0); return elapsed; }\n'
        source = out / 'caller.c'
        source.write_text(HARNESS + (OWNED / 'kernel-functions.c').read_text() + '\n' + helper + deadline + wait + MAIN)
        cls.binary = out / 'caller'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11', '-O2', '-isysroot', sdk, str(source), '-o', str(cls.binary)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def test_actual_caller_deadline_owner_delay_and_tpool_blocks(self):
        for mode in (*range(6), 16):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)]).returncode, 0)

    def test_errors_and_overflow_fail_closed_not_elapsed(self):
        for mode in (*range(6, 16), *range(17, 22)):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)]).returncode, 125)

    def test_exact_patch_context_and_copied_declarations(self):
        for patcher, text in ((patch_kernel, self.kernel), (patch_tpool, self.tpool)):
            with self.assertRaisesRegex(RuntimeError, 'context changed'):
                patcher(text.replace('cv_init(', 'lost(') if patcher is patch_kernel else text.replace('CLOCK_REALTIME', 'CLOCK_OTHER'))
        header = declarations()
        self.assertIn('m_owner', header)
        self.assertIn('CDDL HEADER START', header)
        self.assertNotIn('#if', header)
        source = (OWNED.parents[1] / 'native-memory/service_time.inc').read_text()
        changed, _ = adapt_fixture(source)
        self.assertIn('zfs_timedwait', changed)
        with self.assertRaisesRegex(RuntimeError, 'context changed'):
            adapt_fixture(source.replace('static pthread_mutex_t timed_mutex', 'static pthread_mutex_t lost'))
