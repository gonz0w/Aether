# SPDX-License-Identifier: BSD-2-Clause
"""Actual ARC adapter math and initializer patch; no engine/reclaim execution."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import CURRENT, OWNED, function, patch_arc_adapter, patch_arc_initializer

BASE = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1'


class OpenZFSARCPressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zfs-arc-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        owned = (OWNED / 'arc-functions.c').read_text()
        original = (BASE / 'lib/libzpool/arc_os.c').read_text()
        source = '''#include <stdint.h>
#include <stdlib.h>
static uint64_t total=8192, remaining=4096, arc_sys_free=819*4096;
static uint64_t aether_zfs_granted_pages(void) {return total;}
static uint64_t aether_zfs_free_pages(void) {return remaining;}
#define MAX(a,b) ((a)>(b)?(a):(b))
'''
        for name in ('arc_all_memory','arc_free_memory','arc_available_memory'):
            source += function(owned,name) + '\n'
        source += function(original,'arc_default_max') + '\n'
        source += '''int main(int argc,char **argv) {
    if (argc!=2) return 90;
    int mode=atoi(argv[1]);
    if (mode==1) remaining=819;
    else if (mode==2) remaining=818;
    else if (mode==3) {total=128;remaining=16;arc_sys_free=12*4096;}
    else if (mode==4) arc_sys_free=8193*4096;
    else if (mode==5) {remaining=0;arc_sys_free=0;}
    else if (mode==6) {remaining=0;arc_sys_free=8192*4096;}
    else if (mode!=0) return 91;
    if (arc_all_memory()!=total*4096 || arc_free_memory()!=remaining*4096 ||
        arc_available_memory()!=(int64_t)(remaining*4096)-(int64_t)arc_sys_free) return 92;
    if (arc_default_max(32*1024*1024,total*4096)!=32*1024*1024) return 93;
    return 0;
}
'''
        (out / 'probe.c').write_text(source)
        cls.binary = out / 'probe'
        sdk = subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=c11',
                                 '-O2','-Wall','-Wextra','-Werror','-isysroot',sdk,
                                 str(out / 'probe.c'),'-o',str(cls.binary)],capture_output=True,text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def test_positive_zero_negative_and_target_is_not_usage(self):
        for mode in (0,1,2,3,5,6):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary,str(mode)],timeout=5).returncode,0)

    def test_invalid_headroom_fails_closed(self):
        self.assertEqual(subprocess.run([self.binary,'4'],timeout=5).returncode,125)

    def test_actual_adapter_and_initializer_preserve_floor(self):
        original = (BASE / 'lib/libzpool/arc_os.c').read_text()
        changed, edits = patch_arc_adapter(original)
        for name in ('arc_all_memory','arc_free_memory','arc_available_memory'):
            self.assertNotIn('random_in_range',function(changed,name))
        self.assertEqual(function(original,'arc_default_max'),function(changed,'arc_default_max'))
        self.assertEqual(len(edits),3)
        original = (BASE / 'module/zfs/arc.c').read_text()
        changed, edits = patch_arc_initializer(original)
        self.assertIn('arc_sys_free = (allmem / 4096 / 10) * 4096;',changed)
        self.assertIn('arc_c_min = MAX(arc_c_max / 2, 2ULL << SPA_MAXBLOCKSHIFT);',changed)
        self.assertEqual(len(edits),1)
        with self.assertRaises(RuntimeError):
            patch_arc_initializer(original.replace('arc_c_min = MAX(arc_c_max / 2,','arc_c_min = MAX(arc_c_max / 3,'))
