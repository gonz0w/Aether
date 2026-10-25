# SPDX-License-Identifier: BSD-2-Clause
"""Execute pinned checked time bodies with controlled host clock outputs.

This isolates arithmetic/error coverage; it supplies no native UTC evidence.
"""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / '.deps/native-current/build-attempt-5/guarded-include/sys/time.h'
DIGEST = 'a8b600d9a69e96ebdc49357d104b3ebd1339e9967dc245ba71b7b17ca43d4331'
PREFIX = r'''
#include <time.h>
#include <stdint.h>
#include <limits.h>
#include <stdlib.h>
#define NANOSEC 1000000000LL
#define NSEC_PER_USEC 1000LL
typedef long long hrtime_t;
typedef struct timespec inode_timespec_t;
static struct timespec source;
static int error;
static clockid_t selected;
static int controlled_clock(clockid_t clock, struct timespec *out) {
    selected = clock;
    if (!error) *out = source;
    return error;
}
#define clock_gettime controlled_clock
'''
MAIN = r'''
int main(int argc, char **argv) {
    if (argc != 5) return 90;
    source = (struct timespec){strtoll(argv[2], NULL, 10),
                              strtoll(argv[3], NULL, 10)};
    error = atoi(argv[4]);
    struct timespec out;
    switch (atoi(argv[1])) {
    case 0:
        gethrestime(&out);
        if (out.tv_sec != source.tv_sec ||
            out.tv_nsec != source.tv_nsec / 1000 * 1000) return 91;
        break;
    case 1:
        if (gethrestime_sec() != (uint64_t)source.tv_sec) return 92;
        break;
    case 2:
        if ((uint64_t)getlrtime() != (uint64_t)source.tv_sec * NANOSEC +
                                    source.tv_nsec / 1000 * 1000) return 93;
        break;
    case 3:
        if ((uint64_t)gethrtime() != (uint64_t)source.tv_sec * NANOSEC +
                                    source.tv_nsec) return 94;
        break;
    default: return 95;
    }
    return selected != (atoi(argv[1]) == 3 ? CLOCK_MONOTONIC : CLOCK_REALTIME);
}
'''


class OpenZfsWallTime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = HEADER.read_bytes()
        if hashlib.sha256(source).hexdigest() != DIGEST:
            raise AssertionError('checked time header changed')
        text = source.decode()
        bodies = text[text.index('static inline void\ngethrestime('):
                      text.index('\n#endif /* _LIBSPL_SYS_TIME_H */')]
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-wall-time-')
        cls.addClassCleanup(cls.temp.cleanup)
        directory = Path(cls.temp.name)
        src = directory / 'consumer.c'
        src.write_text(PREFIX + bodies + MAIN)
        cls.binary = directory / 'consumer'
        subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                        '-Wall', '-Wextra', '-Werror', '-O2', str(src),
                        '-o', str(cls.binary)], check=True, capture_output=True)

    def check(self, body, seconds, nanoseconds, error=0, expected=0):
        result = subprocess.run([str(self.binary), str(body), str(seconds),
                                 str(nanoseconds), str(error)], timeout=3)
        self.assertEqual(result.returncode, expected)

    def test_real_and_monotonic_selection_and_microsecond_truncation(self):
        for body in range(4):
            for seconds in (0, 951827640, 1791280440):
                with self.subTest(body=body, seconds=seconds):
                    self.check(body, seconds, 999999999)

    def test_provider_errors_and_invalid_outputs_terminate(self):
        for body in range(4):
            for seconds, nanos, error in ((17, 29, -1), (-1, 0, 0),
                                          (0, -1, 0), (0, 1000000000, 0)):
                with self.subTest(body=body, seconds=seconds, nanos=nanos):
                    self.check(body, seconds, nanos, error, 125)

    def test_signed_boundary_with_actual_guard_and_truncation(self):
        seconds, remainder = divmod(2**63 - 1, 1000000000)
        self.check(2, seconds, 854775999)  # Truncates safely below signed max.
        self.check(2, seconds, 854776000, expected=125)
        self.check(3, seconds, remainder)
        self.check(3, seconds, remainder + 1, expected=125)
        for body in (2, 3):
            self.check(body, seconds + 1, 0, expected=125)
            self.check(body, 9246182400, 0, expected=125)  # 2263-01-01.
        # Calendar seconds/timespec do not require signed nanosecond encoding.
        self.check(0, 9246182400, 0)
        self.check(1, 9246182400, 0)
