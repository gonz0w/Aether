# SPDX-License-Identifier: BSD-2-Clause
"""Actual resource validation with controlled observations; no native authority claim."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import CURRENT, OWNED, patch_resources


class OpenZFSResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zfs-resources-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        source = (OWNED / 'resources.c').read_text()
        start = source.index('static long aether_zfs_native_pages(')
        end = source.index('\nstatic uint64_t aether_zfs_observe(', start)
        provider = '''static uint64_t supplied_total=8192;
static long supplied_free=123;
static long aether_zfs_native_pages(uint64_t *total) {
    *total=supplied_total; return supplied_free;
}
'''
        source = (source[:start] + provider + source[end:]).replace('#include <sys/auxv.h>\n','')
        source += '''
int main(int argc, char **argv) {
    if (argc!=2) return 90;
    int mode=atoi(argv[1]);
    if (mode==1) supplied_free=-EPERM;
    else if (mode==2) supplied_total=0;
    else if (mode==3) supplied_free=8193;
    else if (mode==4) supplied_total=(uint64_t)INT64_MAX/4096+1;
    else if (mode==5) {supplied_total=INT64_MAX/4096;supplied_free=0;}
    else if (mode==6) supplied_free=0;
    else if (mode==7) supplied_free=-1;
    else if (mode!=0 && mode!=8) return 91;
    if (aether_zfs_granted_pages()!=supplied_total ||
        aether_zfs_free_pages()!=(uint64_t)supplied_free ||
        aether_zfs_assigned_cpus()!=1) return 92;
    if (mode==8) {
        --supplied_free;
        if (aether_zfs_granted_pages()!=8192 || aether_zfs_free_pages()!=122) return 93;
        supplied_free=-EPERM;
        aether_zfs_assigned_cpus();
        return 94;
    }
    return 0;
}
'''
        (out / 'probe.c').write_text(source)
        cls.binary = out / 'probe'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11',
                                 '-O2', '-Wall', '-Wextra', '-Werror', '-isysroot', sdk,
                                 str(out / 'probe.c'), '-o', str(cls.binary)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def test_quota_free_and_assigned_core_observations(self):
        for mode in (0,5,6):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary,str(mode)],timeout=5).returncode,0)

    def test_denial_malformed_overflow_and_revalidation(self):
        for mode in (1,2,3,4,7,8):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary,str(mode)],timeout=5).returncode,125)

    def test_exact_initialization_removes_unsigned_host_assumptions(self):
        source = (CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        changed, edits = patch_resources(source)
        self.assertIn('physmem = aether_zfs_granted_pages();',changed)
        self.assertNotIn('sysconf(_SC_PHYS_PAGES)',changed)
        self.assertNotIn('physmem = %llu pages',changed)
        self.assertEqual(len(edits),1)
        with self.assertRaises(RuntimeError):
            patch_resources(source.replace('physmem = sysconf(_SC_PHYS_PAGES);','physmem = 0;'))
