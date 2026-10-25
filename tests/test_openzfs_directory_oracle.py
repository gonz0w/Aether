# SPDX-License-Identifier: BSD-2-Clause
"""Independent hierarchy verifier fails on corrupted data/metadata/inventory."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from test_openzfs_directories import ROOT,OWNED


class Oracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-directory-oracle-');cls.addClassCleanup(cls.temp.cleanup)
        cls.out=Path(cls.temp.name)
        cls.sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        cls.body=(OWNED/'directory-oracle.inc').read_text();cls.binary=cls.compile(cls.body,'oracle')

    @classmethod
    def compile(cls,body,name,extra=()):
        (cls.out/'directory-oracle.inc').write_text(body);binary=cls.out/name
        r=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-isysroot',cls.sdk,
            *extra,'-std=gnu11','-O2','-Wall','-Wextra','-Werror','-I'+str(cls.out),'-I'+str(OWNED),
            str(ROOT/'tests/fixtures/openzfs_directory_oracle.c'),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        return binary

    def mode(self,phase,mode=0,fault=0,binary=None,expected=0):
        r=subprocess.run([str(binary or self.binary),str(phase),str(mode),str(fault)],capture_output=True,text=True,timeout=5)
        self.assertEqual(r.returncode,expected,r.stdout+r.stderr)
        if expected==96:self.assertIn('DIRECTORY ORACLE96',r.stderr)
        return r.stdout

    def test_pristine_interrupted_and_full_hierarchy_and_every_api_failure(self):
        for phase in range(3):
            calls=int(re.search(r'calls=(\d+)',self.mode(phase))[1])
            for fault in range(1,calls+1):
                with self.subTest(phase=phase,fault=fault):self.mode(phase,fault=fault)

    def test_each_metadata_acl_content_eof_inventory_and_leftover_corruption_fails(self):
        for phase in range(3):
            modes=[1,2,12,13,14,15,22] if phase==0 else [1,2,3,4,5,6,7,8,9,12,13,14,15,17,18,19,20,22] if phase==1 else range(1,23)
            for mode in modes:
                with self.subTest(phase=phase,mode=mode):self.mode(phase,mode)

    def test_compiling_omissions_fail_the_exact_corrupted_field_oracle(self):
        for name,old,new,phase,mode in [
            ('root-generation','root.generation != 45','0',2,1),
            ('parent','parent != expected_parent','((void)expected_parent, 0)',2,4),
            ('acl','acl[0].z_access_mask !=\n             (S_ISDIR(node.mode) ? UINT32_C(0x1e01ff) : UINT32_C(0x1e019f))','0',2,9),
            ('data','data[i] != (unsigned char)(71 + offset + i)','0',2,10),
            ('eof','if (!error && got)','if (0 && !error && got)',2,11),
            ('inventory','if (i == length)','if (0 && i == length)',2,12),
            ('counts','count != expected || node.size != count + 2','((void)expected, 0)',0,15),
            ('original-file','error = namespace_original(view);','if (0) error = namespace_original(view);',0,22),
        ]:
            with self.subTest(omission=name):
                self.assertEqual(self.body.count(old),1)
                binary=self.compile(self.body.replace(old,new,1),name);self.mode(phase,mode,binary=binary,expected=96)

    def test_only_explicit_lifetime_oracle_accepts120s_window_and_rejects_later_metadata(self):
        old=self.compile(self.body,'old-late',['-DTEST_TIME=1791290157'])
        self.mode(2,binary=old,expected=96)
        selected='#define AETHER_DIRECTORY_LAST 1791290160\n'+self.body
        allowed=self.compile(selected,'lifetime-limit',['-DTEST_TIME=1791290157'])
        self.mode(2,binary=allowed)
        late=self.compile(selected,'lifetime-late',['-DTEST_TIME=1791290158'])
        self.mode(2,binary=late,expected=96)


if __name__=='__main__':unittest.main()
