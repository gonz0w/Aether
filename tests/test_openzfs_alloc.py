# SPDX-License-Identifier: BSD-2-Clause
"""Actual inline allocation port with controlled failures, not native memory."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import CURRENT, patch_alloc_header, patch_alloc_kernel, function

PREFIX = r'''
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static unsigned calls, frees, constructors, destructors, failures;
static unsigned expected_calls=1, expected_frees;
static int aligned_error, constructor_error=ENOMEM;
static unsigned cookie;
static void *fake_malloc(size_t n) {
    ++calls;
    if (failures) {--failures; errno=ENOMEM; return NULL;}
    return malloc(n);
}
static void fake_free(void *p) {++frees; free(p);}
static int fake_posix(void **out, size_t align, size_t n) {
    ++calls;
    if (aligned_error) return aligned_error;
    if (failures) {--failures; return ENOMEM;}
    return posix_memalign(out,align,n);
}
_Noreturn void fatal(int status) {
    if (status!=125 || calls!=expected_calls || frees!=expected_frees || destructors)
        exit(94);
    exit(125);
}
#define malloc(n) fake_malloc(n)
#define free fake_free
#define posix_memalign fake_posix
#define _Exit fatal
#include "umem.h"
static int construct(void *p, void *private, int flags) {
    if (!p || private!=&cookie || flags!=UMEM_DEFAULT) exit(95);
    ++constructors;
    /* A failing constructor cleans its own external partial resources. */
    void *partial=fake_malloc(16);
    if (!partial) exit(96);
    fake_free(partial);
    memset(p,0x5a,64);
    return constructor_error;
}
static void destruct(void *p, void *private) {
    if (!p || private!=&cookie) exit(97);
    ++destructors;
}
#define CHECK(x) do {if (!(x)) return 98;} while(0)
'''
MAIN = r'''
int main(int argc, char **argv) {
    if (argc!=2) return 90;
    int mode=atoi(argv[1]);
    umem_cache_t cache={.cache_bufsize=64,.cache_constructor=construct,
        .cache_destructor=destruct,.cache_private=&cookie};
    if (mode==0 || mode==8) {
        cache.cache_align=mode==8?64:0;
        CHECK(!umem_cache_alloc(&cache,UMEM_DEFAULT) && errno==ENOMEM);
        CHECK(calls==2 && frees==2 && constructors==1 && !destructors);
    } else if (mode==1) {failures=1; umem_alloc(64,UMEM_NOFAIL); return 99;
    } else if (mode==2) {failures=1; umem_zalloc(64,UMEM_NOFAIL); return 99;
    } else if (mode==3) {failures=1; umem_alloc_aligned(64,64,UMEM_NOFAIL); return 99;
    } else if (mode==4) {aligned_error=EINVAL; umem_alloc_aligned(64,64,UMEM_NOFAIL); return 99;
    } else if (mode==5) {aligned_error=EIO; umem_alloc_aligned(64,64,UMEM_NOFAIL); return 99;
    } else if (mode==6 || mode==12) {
        cache.cache_align=mode==12?64:0;
        expected_calls=2; expected_frees=2;
        umem_cache_alloc(&cache,UMEM_NOFAIL); return 99;
    } else if (mode==7) {
        failures=1;
        umem_cache_create("failed",64,0,NULL,NULL,NULL,NULL,NULL,0); return 99;
    } else if (mode==9) {
        failures=1; CHECK(!umem_alloc(64,UMEM_DEFAULT) && errno==ENOMEM && calls==1);
    } else if (mode==10) {
        void *p=umem_alloc(64,UMEM_NOFAIL); CHECK(p); umem_free(p,64);
        p=umem_zalloc(64,UMEM_NOFAIL); CHECK(p);
        for (unsigned i=0;i<64;++i) CHECK(!((unsigned char *)p)[i]);
        umem_free(p,64);
        p=umem_alloc_aligned(64,64,UMEM_NOFAIL); CHECK(p && !((uintptr_t)p%64));
        umem_free_aligned(p,64); CHECK(calls==3 && frees==3);
    } else if (mode==11) {
        constructor_error=0;
        umem_cache_t *cp=umem_cache_create("good",64,64,construct,destruct,NULL,&cookie,NULL,0);
        CHECK(cp); void *p=umem_cache_alloc(cp,UMEM_NOFAIL); CHECK(p && !((uintptr_t)p%64));
        umem_cache_free(cp,p); umem_cache_destroy(cp);
        CHECK(calls==3 && frees==3 && constructors==1 && destructors==1);
    } else if (mode==13 || mode==14) {
        aligned_error=mode==13?EINVAL:EIO;
        CHECK(!umem_alloc_aligned(64,64,UMEM_DEFAULT) && errno==aligned_error && calls==1 && !frees);
    } else if (mode==15 || mode==16 || mode==17) {
        cache.cache_align=mode==17?64:0; failures=1;
        void *p=umem_cache_alloc(&cache,mode==16?UMEM_NOFAIL:UMEM_DEFAULT);
        if (mode==16) return 99;
        CHECK(!p && errno==ENOMEM && calls==1 && !constructors && !destructors && !frees);
    } else return 91;
    return 0;
}
'''


class OpenZFSAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zfs-alloc-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        original = (CURRENT / 'build-attempt-5/guarded-include/umem.h').read_text()
        changed = patch_alloc_header(original)[0]
        cls.binaries = {}
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        for name, header in (('port', changed), ('old-retry', original),
                             ('old-constructor', changed.replace(function(changed, 'umem_cache_alloc'),
                                                                 function(original, 'umem_cache_alloc'), 1))):
            folder = out / name
            (folder / 'sys').mkdir(parents=True)
            (folder / 'umem.h').write_text(header)
            (folder / 'sys/debug.h').write_bytes((CURRENT / 'build-attempt-5/guarded-include/sys/debug.h').read_bytes())
            (folder / 'probe.c').write_text(PREFIX + MAIN)
            binary = folder / 'probe'
            result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11', '-D_DARWIN_C_SOURCE',
                                     '-O2', '-Wall', '-Wextra', '-Werror', '-isysroot', sdk, '-I' + str(folder),
                                     str(folder / 'probe.c'), '-o', str(binary)], capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stderr)
            cls.binaries[name] = binary

    def test_default_cleanup_zero_alignment_and_success(self):
        for mode in (0,8,9,10,11,13,14,15,17):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binaries['port'], str(mode)], timeout=5).returncode, 0)

    def test_nofail_has_one_attempt_and_no_partial_object(self):
        for mode in (1,2,3,4,5,6,7,12,16):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binaries['port'], str(mode)], timeout=5).returncode, 125)

    def test_old_retry_and_ignored_constructor_fail_named_contract(self):
        # One controlled failure followed by success makes the old loop bounded
        # and observable: it returns99 rather than the required one-attempt125.
        self.assertEqual(subprocess.run([self.binaries['old-retry'], '1'], timeout=5).returncode, 99)
        self.assertEqual(subprocess.run([self.binaries['old-constructor'], '0'], timeout=5).returncode, 98)

    def test_callback_registration_removal_and_exact_input_guard(self):
        text = (CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        changed, edits = patch_alloc_kernel(text)
        self.assertNotIn('umem_out_of_memory', changed)
        self.assertNotIn('umem_nofail_callback', changed)
        self.assertEqual(len(edits), 2)
        with self.assertRaises(RuntimeError):
            patch_alloc_kernel(text.replace('umem_nofail_callback(umem_out_of_memory);', ''))
