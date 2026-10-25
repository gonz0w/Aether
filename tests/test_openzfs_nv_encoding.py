# SPDX-License-Identifier: BSD-2-Clause
"""Pinned actual nvlist encoding dispatch/unpack; payload codecs are scaffolding."""
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from openzfs_elapsed import CURRENT, function


class NvEncoding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-nv-encoding-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        original = (CURRENT/'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/nvpair/nvpair.c').read_text()
        common = function(original, 'nvlist_common')
        unpack = function(original, 'nvlist_xunpack')
        if hashlib.sha256((common+unpack).encode()).hexdigest() != '114f6fed801f9a88c71897a7683efb77194b1606420abeef062550d85510a8c5':
            raise AssertionError('original encoding/unpack body drift')
        header = re.search(r'typedef struct \{\n\tchar\tnvh_encoding;.*?\} nvs_header_t;', original, re.S).group()
        scaffold = r'''
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#define _ZFS_LITTLE_ENDIAN 1
#define NVS_OP_ENCODE 0
#define NVS_OP_DECODE 1
#define NVS_OP_GETSIZE 2
#define NV_ENCODE_NATIVE 0
#define NV_ENCODE_XDR 1
typedef struct { int unused; } nvpriv_t;
typedef struct { uintptr_t nvl_priv; } nvlist_t;
typedef struct { nvpriv_t *nvs_priv; int nvs_op, nvs_recursion; } nvstream_t;
typedef struct { int unused; } nv_alloc_t;
static int calls, allocations, frees;
static nvpriv_t private;
static nvlist_t allocated;
static void require(int ok) {
    if (!ok) { fputs("HOST NV ENCODING oracle91\n", stderr); exit(91); }
}
static int nvs_native(nvstream_t *s, nvlist_t *n, char *b, size_t *z) {
    (void)s; (void)n; (void)b; (void)z; ++calls; return 0;
}
static int nvs_xdr(nvstream_t *s, nvlist_t *n, char *b, size_t *z) {
    return nvs_native(s,n,b,z);
}
static int nvlist_xalloc(nvlist_t **n, int flags, nv_alloc_t *a) {
    require(!flags && a); ++allocations;
    allocated.nvl_priv=(uintptr_t)&private; *n=&allocated; return 0;
}
static void nvlist_free(nvlist_t *n) { require(n==&allocated); ++frees; }
'''
        main = r'''
int main(int argc, char **argv) {
    require(argc == 2);
    unsigned encoding=(unsigned)strtoul(argv[1],NULL,10);
    char bytes[4]={(char)encoding,1,0,0};
    nvlist_t *output=NULL; nv_alloc_t allocator={0};
    int error=nvlist_xunpack(bytes,sizeof(bytes),&output,&allocator);
    int valid=encoding==NV_ENCODE_NATIVE || encoding==NV_ENCODE_XDR;
    require(allocations==1 && calls==valid && frees==!valid);
    require(valid ? error==0 && output==&allocated : error==ENOTSUP && output==NULL);
    puts("HOST NV ENCODING PASS"); return 0;
}
'''
        cls.binaries={}
        for label, body, char_flag in (
                ('signed',common,'-fsigned-char'),('unsigned',common,'-funsigned-char'),
                ('broken-method',common.replace('encoding = nvh->nvh_encoding;',
                                              'encoding = NV_ENCODE_XDR;',1),'-fsigned-char')):
            if label=='broken-method' and body==common:raise AssertionError('encoding mutation drift')
            path=out/(label+'.c')
            path.write_text(original[:original.index('#include')]+scaffold+header+'\n'+body+'\n'+unpack+'\n'+main)
            binary=out/label
            result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=c11','-O2',
                                   '-Wall','-Wextra','-Werror',char_flag,str(path),'-o',str(binary)],
                                  capture_output=True,timeout=30)
            if result.returncode:raise RuntimeError(result.stderr.decode())
            cls.binaries[label]=binary

    def run_encoding(self, encoding, label='signed'):
        return subprocess.run([str(self.binaries[label]),str(encoding)],capture_output=True,timeout=5)

    def test_all_unsupported_encodings_reject_before_payload_dispatch(self):
        for label in ('signed','unsigned'):
            for encoding in range(2,256):
                result=self.run_encoding(encoding,label)
                self.assertEqual((result.returncode,result.stdout,result.stderr),(0,b'HOST NV ENCODING PASS\n',b''))

    def test_supported_encodings_reach_selected_codec_scaffolding(self):
        for encoding in (0,1):
            self.assertEqual(self.run_encoding(encoding).returncode,0)

    def test_omitted_method_read_fails_exact_unsupported_oracle(self):
        result=self.run_encoding(255,'broken-method')
        self.assertEqual((result.returncode,result.stderr),(91,b'HOST NV ENCODING oracle91\n'))
