# SPDX-License-Identifier: BSD-2-Clause
"""Execute actual selected entropy callers with controlled host providers.

The provider is a model for deterministic faults/counts, never native entropy.
The native composition separately executes the real trap and hardware transport.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import OWNED, CURRENT, patch_entropy, declarations, adapt_fixture, adapt_entropy_fixture

PREFIX = r'''
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <errno.h>
static unsigned long aux=0x60000101;
static unsigned long mock_aux(unsigned long key) { return key == 0xa002 ? aux : 0; }
#define getauxval mock_aux
'''
PROVIDER = r'''
static unsigned calls, closes, remaining=4096, closed, fault_at;
static long fault;
static size_t counts[32];
static long aether_random_call(unsigned long op, uint8_t *ptr, size_t len) {
    if (aether_random_grant != 0x60000101) return -EACCES;
    if (closed) return -EBADF;
    if (op == 0x2b001) { if (fault_at==99) return fault; ++closes; closed=1; return 0; }
    if (op != 0x2b000 || !len || len>256) return -EINVAL;
    counts[calls++]=len;
    if (calls == fault_at) return fault;
    if (len>remaining) return -ENOSPC;
    memset(ptr,0x5a,len); remaining-=len; return len;
}
'''
MAIN = r'''
#define CHECK(x) do { if (!(x)) return __LINE__ % 100 + 1; } while(0)
int main(int argc, char **argv) {
    if (argc != 2) return 90;
    int mode=atoi(argv[1]); uint8_t data[4098]; memset(data,0xa5,sizeof(data));
    if (mode == 0) {
        random_init(); CHECK(calls==1 && counts[0]==8);
        CHECK(!random_get_bytes(NULL,0) && calls==1);
        CHECK(!random_get_bytes(data+1,513) && calls==4);
        CHECK(counts[1]==256 && counts[2]==256 && counts[3]==1);
        CHECK(remaining==4096-8-513 && data[0]==0xa5 && data[514]==0xa5 && data[513]==0x5a);
        CHECK(!random_get_pseudo_bytes(data+1,8) && counts[4]==8);
        random_fini(); random_fini(); CHECK(closes==1 && !aether_random_grant);
        return 0;
    } else if (mode == 1) {
        random_init(); CHECK(!random_get_bytes(data+1,4088) && !remaining && calls==17);
        random_fini(); return 0;
    } else if (mode == 2) { aux=0; random_init();
    } else if (mode == 3) { aux+=256; random_init();
    } else if (mode == 4) { random_init(); random_init();
    } else if (mode == 5) { random_get_bytes(NULL,0);
    } else if (mode == 6) { random_init(); random_fini(); random_get_bytes(data,1);
    } else if (mode == 7) { random_init(); random_fini(); random_init();
    } else if (mode == 8) { random_init(); random_get_bytes(NULL,1);
    } else if (mode == 9) { random_init(); random_get_bytes((uint8_t *)(UINTPTR_MAX-5),10);
    } else if (mode == 10) { random_init(); random_get_bytes(data,4097);
    } else if (mode == 11) { random_init(); random_get_bytes(data,4088); random_get_bytes(data,1);
    } else if (mode >= 12 && mode <= 17) {
        random_init(); fault_at=3;
        long outcomes[]={0,1,257,-EIO,-EINTR,-ENOSPC}; fault=outcomes[mode-12];
        random_get_bytes(data,513);
    } else if (mode == 18) { fault_at=1; fault=-EIO; random_init();
    } else if (mode == 19) { fault_at=1; fault=7; random_init();
    } else if (mode == 20) { random_init(); fault_at=99; fault=-EBADF; random_fini();
    } else return 91;
    return 92; /* Every control above must fail closed before returning. */
}
'''


class OpenZFSEntropyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zfs-entropy-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        source = (OWNED / 'entropy-functions.c').read_text()
        start = source.index('static long aether_random_call(')
        end = source.index('void random_init(', start)
        (out / 'caller.c').write_text(PREFIX + source[:start] + PROVIDER + source[end:] + MAIN)
        cls.binary = out / 'caller'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11', '-O2', '-isysroot', sdk,
                                 str(out / 'caller.c'), '-o', str(cls.binary)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def test_actual_fill_chunking_zero_length_and_quiescent_close(self):
        for mode in range(2):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)]).returncode, 0)

    def test_partial_zero_short_error_overflow_and_authority_fail_closed(self):
        for mode in range(2,21):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)]).returncode, 125)

    def test_exact_context_and_public_declarations(self):
        original=(CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        changed, edits=patch_entropy(original)
        self.assertEqual(len(edits),2)
        self.assertNotIn('random_get_bytes_common', changed)
        self.assertNotIn('open(random_path', changed)
        self.assertIn('sys/auxv.h',changed)
        self.assertIn('random_fini(void)',declarations(True))
        with self.assertRaises((RuntimeError,ValueError)):
            patch_entropy(original.replace('open(random_path','lost(random_path'))
        fixture,_=adapt_fixture((OWNED.parents[1] / 'native-memory/service_time.inc').read_text())
        self.assertIn('zfs_entropy_worker()',adapt_entropy_fixture(fixture)[0])
        with self.assertRaisesRegex(RuntimeError,'context changed'):
            adapt_entropy_fixture(fixture.replace('    CHECK(!zfs_result, zfs_result);',''))
