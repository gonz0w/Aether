# SPDX-License-Identifier: BSD-2-Clause
"""Actual private C backend under controlled providers, separate from VM proof."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LongWaitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-long-wait-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        source = (ROOT / 'user/native-memory/real_time.c').read_text()
        source = source.split('#define CHECK', 1)[0]
        source = source.replace('#include "adapter.h"', '''
static long fake_trap(unsigned long, unsigned long, unsigned long,
                      unsigned long, unsigned long);
#define memtrap fake_trap
#define getauxval(tag) 17UL
#define clock_gettime isolated_clock_gettime
''', 1).replace('#include <sys/auxv.h>', '', 1)
        source += '''
#include <stdlib.h>
static int mode, calls, reads;
static unsigned long current, deadlines[8];
static long fake_trap(unsigned long op, unsigned long cap, unsigned long word,
                      unsigned long value, unsigned long until)
{
    if (cap != 17) abort();
    if (op == 0x2800f) {
        ++reads;
        if (mode == 5 || (mode == 6 && calls)) return -ENOSYS;
        return current;
    }
    if (op != 0x28010 || !word || value != 0 || calls == 8 ||
        until <= current || until - current > SECOND) abort();
    deadlines[calls++] = until;
    if (mode == 3) {current = until - 1; return -ETIMEDOUT;}
    if (mode == 4 || (mode == 13 && calls == 2)) return -EACCES;
    if (mode == 7) return 1;
    if (calls == 1 && (mode == 1 || mode == 2 || mode == 8 || mode == 14)) {
        current += 250000000;
        return mode == 2 || mode == 14 ? -EAGAIN : 0;
    }
    current = until;
    return -ETIMEDOUT;
}
int main(int argc, char **argv)
{
    if (argc != 2) return 90;
    mode = atoi(argv[1]);
    volatile int word = 0;
    struct timespec at = {2, 500000000};
    int result;
    if (mode == 9) {
        current = 1;
        at = (struct timespec){LONG_MAX / SECOND, LONG_MAX % SECOND};
        result = -aether_sleep_syscall(SYS_clock_nanosleep,
                                      CLOCK_MONOTONIC, 0, (long)&at, 0);
        return result != EOVERFLOW || calls;
    }
    if (mode == 10) {
        current = LONG_MAX - 2500000000UL;
        at = (struct timespec){LONG_MAX / SECOND, LONG_MAX % SECOND};
    }
    if (mode == 11) {
        return aether_monotonic_wait(&word, 0, CLOCK_REALTIME, &at, 1) !=
                   ENOTSUP || calls || reads;
    }
    if (mode == 12) {
        at.tv_nsec = SECOND;
        if (aether_monotonic_wait(&word, 0, CLOCK_MONOTONIC, &at, 1) !=
            EINVAL) return 91;
        at = (struct timespec){-1, 0};
        if (aether_monotonic_wait(&word, 0, CLOCK_MONOTONIC, &at, 1) !=
            ETIMEDOUT) return 92;
        at = (struct timespec){LONG_MAX, 0};
        if (aether_monotonic_wait(&word, 0, CLOCK_MONOTONIC, &at, 1) !=
            EOVERFLOW) return 93;
        if (aether_monotonic_wait(&word, 0, CLOCK_MONOTONIC, &at, 0) !=
            ENOTSUP) return 94;
        return calls || reads;
    }
    if (mode == 8 || mode == 14) {
        result = -aether_sleep_syscall(SYS_clock_nanosleep,
                                      CLOCK_MONOTONIC, 0, (long)&at, 0);
        return result || calls != 4 || current != 2500000000UL ||
            deadlines[0] != 1000000000UL || deadlines[1] != 1250000000UL ||
            deadlines[2] != 2250000000UL || deadlines[3] != 2500000000UL;
    }
    result = aether_monotonic_wait(&word, 0, CLOCK_MONOTONIC, &at, 1);
#ifndef AETHER_LONG_WAITS
    return result != EINVAL || calls;
#else
    if (mode == 1 || mode == 2) return result || calls != 1;
    if (mode == 3 || mode == 7) return result != EIO || calls != 1;
    if (mode == 4) return result != EACCES || calls != 1;
    if (mode == 5) return result != ENOSYS || calls;
    if (mode == 6) return result != ENOSYS || calls != 1;
    if (mode == 13) return result != EACCES || calls != 2;
    if (mode == 10) return result != ETIMEDOUT || calls != 3 ||
        current != LONG_MAX || deadlines[2] != LONG_MAX;
    return result != ETIMEDOUT || calls != 3 || current != 2500000000UL ||
        deadlines[0] != 1000000000UL || deadlines[1] != 2000000000UL ||
        deadlines[2] != 2500000000UL;
#endif
}
'''
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binaries = {}
        for name, flags in (('long', ['-DAETHER_LONG_WAITS']), ('short', [])):
            path = out / (name + '.c')
            path.write_text(source)
            binary = out / name
            command = ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                       '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                       '-DSYS_clock_nanosleep=230', '-DSYS_nanosleep=35',
                       '-DTIMER_ABSTIME=1', '-isysroot', sdk,
                       '-I' + str(ROOT / 'user/native-memory'), *flags,
                       str(path), '-o', str(binary)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)
            cls.binaries[name] = binary

    def test_original_deadline_wakes_errors_and_ranges(self):
        for mode in range(15):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binaries['long'], str(mode)],
                                                timeout=5).returncode, 0)

    def test_default_profile_still_rejects_long_deadlines(self):
        for mode in (0, 11, 12):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binaries['short'], str(mode)],
                                                timeout=5).returncode, 0)
