# SPDX-License-Identifier: BSD-2-Clause
"""Actual original-API capacity probe over synthetic calls; native ENOSPC separate."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from openzfs_elapsed import function


class CapacityDenial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-capacity-host-')
        cls.addClassCleanup(cls.temp.cleanup);cls.out=Path(cls.temp.name)
        source=(ROOT/'user/storage/openzfs-volume/pool-data.c').read_text()
        cls.record=function(source,'aether_data_record');cls.body=function(source,'aether_pool_data_capacity')
        cls.binary=cls.compile(cls.body,'normal')

    @classmethod
    def compile(cls,body,name):
        scaffold=r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#define AETHER_DATASET "aether_pool_probe/data_probe"
#define AETHER_DATA_OBJECT 1
#define AETHER_DATA_BYTES 64
#define DMU_READ_NO_PREFETCH 1
#define DMU_OST_OTHER 4
#define B_FALSE 0
#define FTAG ((void*)7)
#define ZPROP_SRC_LOCAL 2
struct spa { int writable;const char *name; };typedef struct spa spa_t;
struct ds { uint64_t reservation; };typedef struct ds dsl_dataset_t;
struct os { spa_t *spa; };typedef struct os objset_t;
static spa_t spa={1,"aether_pool_probe"},foreign={1,"foreign"};
static dsl_dataset_t ds;static objset_t os={&spa};
static int scenario,owned,sets,reads,property_reads;static unsigned char media[64];
static void require(int ok) { if (!ok) { fputs("HOST CAPACITY oracle92\n",stderr);exit(92); } }
static int spa_writeable(spa_t *p) { return p->writable; }
static const char *spa_name(spa_t *p) { return p->name; }
static uint64_t spa_last_synced_txg(spa_t *p) { require(p==&spa);return 19; }
static int dmu_objset_own(const char *name,int type,int ro,int decrypt,void *tag,objset_t **out) {
    require(!owned && !strcmp(name,AETHER_DATASET) && type==4 && !ro && !decrypt && tag==FTAG);
    if (scenario==10) return ENOENT;owned=1;*out=&os;return 0;
}
static spa_t *dmu_objset_spa(objset_t *o) { require(owned && o==&os);return o->spa; }
static dsl_dataset_t *dmu_objset_ds(objset_t *o) { require(owned && o==&os);return &ds; }
static uint64_t dsl_get_refreservation(dsl_dataset_t *d) { require(owned && d==&ds);++property_reads;return d->reservation; }
static int dsl_dataset_set_refreservation(const char *name,int source,uint64_t bytes) {
    require(owned && os.spa==&spa && !strcmp(name,AETHER_DATASET) && source==ZPROP_SRC_LOCAL && bytes==UINT64_C(134217728));
    require(!ds.reservation && property_reads==1);++sets;
    if (scenario==1) { ds.reservation=bytes;return 0; }
    if (scenario==2) return EIO;
    if (scenario==8) ds.reservation=1;
    return ENOSPC;
}
static int dmu_read(objset_t *o,uint64_t object,uint64_t off,uint64_t len,void *out,int flags) {
    require(owned && o==&os && object==1 && !off && len==64 && flags==1 && sets==1 && property_reads==2 && !ds.reservation);
    ++reads;if (scenario==6) return EIO;
    memcpy(out,media,64);if (scenario==3) ((unsigned char*)out)[63]^=1;return 0;
}
static void dmu_objset_disown(objset_t *o,int decrypt,void *tag) { require(owned && o==&os && !decrypt && tag==FTAG);owned=0; }
'''
        main=r'''
int main(int argc,char **argv) {
    (void)dmu_objset_spa; /* Foreign-owner mutation removes the call. */
    require(argc==2);scenario=atoi(argv[1]);uint64_t baseline=17;
    if (scenario==4) os.spa=&foreign;
    if (scenario==5) spa.writable=0;
    if (scenario==7) ds.reservation=1;
    if (scenario==11) baseline=20;
    if (scenario==12) baseline=0;
    if (scenario==13) spa.name="foreign";
    aether_data_record(media,17);unsigned char before[64];memcpy(before,media,64);
    int error=aether_pool_data_capacity(scenario==9?NULL:&spa,baseline);
    int expected=!scenario?0:scenario==1 || scenario==2 || scenario==3 || scenario==6 || scenario==8?EIO:
                 scenario==4?EXDEV:scenario==10?ENOENT:EINVAL;
    require(error==expected && !owned && !memcmp(before,media,64));
    require(sets==(!scenario || scenario==1 || scenario==2 || scenario==3 || scenario==6 || scenario==8));
    require(reads==(!scenario || scenario==3 || scenario==6));
    require(ds.reservation==(scenario==1?UINT64_C(134217728):scenario==7 || scenario==8?1:0));
    puts("HOST CAPACITY PASS");return 0;
}
'''
        path=cls.out/(name+'.c');binary=cls.out/name;path.write_text(scaffold+cls.record+'\n'+body+main)
        r=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=c11','-O2','-Wall','-Wextra','-Werror',str(path),'-o',str(binary)],capture_output=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stderr.decode())
        return binary

    def check(self,modes):
        for mode in modes:
            with self.subTest(mode=mode):
                r=subprocess.run([str(self.binary),str(mode)],capture_output=True,timeout=5)
                self.assertEqual((r.returncode,r.stdout,r.stderr),(0,b'HOST CAPACITY PASS\n',b''))

    def test_enospc_preserves_property_data_and_releases_borrow(self):self.check((0,))
    def test_unexpected_success_or_other_error_cannot_pass(self):self.check((1,2))
    def test_identity_rights_baseline_and_prior_property_denials(self):self.check((4,5,7,9,10,11,12,13))
    def test_read_error_corruption_or_changed_property_cannot_pass(self):self.check((3,6,8))

    def test_compiling_omissions_fail_named_capacity_oracle(self):
        mutations=(
            ('errno','if (error == ENOSPC)','if (1)',2),
            ('success','} else if (!error) {','} else if (0) {',1),
            ('prior','if (dsl_get_refreservation(ds)) {\n        dmu_objset_disown','if (0) {\n        dmu_objset_disown',7),
            ('after','if (dsl_get_refreservation(ds)) {\n            error = EIO;','if (0) {\n            error = EIO;',8),
            ('record','memcmp(record, expected, sizeof(record))','0',3),
            ('size','reservation);','reservation - 1);',0),
            ('foreign','if (dmu_objset_spa(os) != spa)','if (0)',4),
        )
        for name,old,new,mode in mutations:
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old),1)
                binary=self.compile(self.body.replace(old,new),name)
                r=subprocess.run([str(binary),str(mode)],capture_output=True,timeout=5)
                self.assertEqual((r.returncode,r.stderr),(92,b'HOST CAPACITY oracle92\n'))
