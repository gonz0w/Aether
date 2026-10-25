# SPDX-License-Identifier: BSD-2-Clause
"""Actual startup provider validation/copy and pinned engine binding; no engine run."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_elapsed import CURRENT, OWNED, patch_startup, function


class OpenZFSStartup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zfs-startup-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        driver = out / 'driver.c'
        driver.write_text('''#include "startup-fixture.h"
#include <errno.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    if (argc != 2) return 90;
    int mode = atoi(argv[1]);
    struct aether_zfs_startup input = startup_fixture;
    if (mode == 1) input.version = 2;
    if (mode == 2) --input.bytes;
    if (mode == 3) input.hostid = 0;
    if (mode == 4) input.cache_policy = 2;
    if (mode == 5) input.reserved[7] = 1;
    if (mode == 6) input.padding[2] = 1;
    if (mode == 7) input.nodename[0] = '\\x1b';
    if (mode == 8) memset(input.release, 'x', 65);
    if (mode == 9) input.version_label[64] = 'x';
    if (mode == 10) input.sysname[0] = 'L';
    if (mode == 11) input.machine[0] = 'a';
    if (mode == 12) memset(input.nodename, 0, 65);
    if (mode == 14) aether_zfs_hostid();
    if (mode == 15) {struct utsname out; aether_zfs_uname(&out);}
    if (mode == 16) aether_zfs_empty_cache();
    if (mode >= 1 && mode <= 13) {
        int expected = mode == 4 ? ENOTSUP : EINVAL;
        if (aether_zfs_startup_bind(mode == 13 ? NULL : &input) != expected) return 91;
        /* Invalid input publishes no snapshot; a later valid bind still works. */
    } else if (mode != 0 && mode != 17 && mode != 18) return 92;
    if (aether_zfs_startup_bind(mode == 18 ? &input : &startup_fixture)) return 93;
    if (mode == 17) aether_zfs_uname(NULL);
    if (aether_zfs_startup_bind(&input) != EALREADY) return 94;
    input.hostid = 0;
    memset(input.nodename, 0, 65);
    struct utsname observed;
    memset(&observed, 0xa5, sizeof(observed));
    aether_zfs_uname(&observed);
    aether_zfs_empty_cache();
    if (aether_zfs_hostid() != startup_fixture.hostid ||
        strcmp(observed.sysname, startup_fixture.sysname) ||
        strcmp(observed.nodename, startup_fixture.nodename) ||
        strcmp(observed.release, startup_fixture.release) ||
        strcmp(observed.version, startup_fixture.version_label) ||
        strcmp(observed.machine, startup_fixture.machine)) return 95;
    return 0;
}
''')
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = out / 'probe'
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c17',
                                 '-O2', '-Wall', '-Wextra', '-Werror', '-isysroot', sdk,
                                 '-I', str(OWNED), str(driver), str(OWNED / 'startup.c'),
                                 '-o', str(cls.binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def test_actual_validation_rejects_without_poisoning_binding(self):
        for mode in range(14):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)], timeout=5).returncode, 0)

    def test_missing_required_binding_or_output_fails_closed(self):
        for mode in range(14, 18):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)], timeout=5).returncode, 125)

    def test_bound_snapshot_outlives_and_ignores_caller_mutation(self):
        self.assertEqual(subprocess.run([self.binary, '18'], timeout=5).returncode, 0)

    def test_pinned_engine_consumers_remove_linux_discovery_and_io_fallback(self):
        source = (CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        changed, edits = patch_startup(source)
        init = function(changed, 'kernel_init')
        self.assertIn('aether_zfs_hostid()', init)
        self.assertIn('aether_zfs_uname(&hw_utsname)', init)
        self.assertNotIn('get_system_hostid()', init)
        self.assertNotIn('uname(&hw_utsname)', init.replace('aether_zfs_uname(&hw_utsname)', ''))
        cache = function(changed, 'spa_config_load')
        self.assertIn('aether_zfs_empty_cache()', cache)
        self.assertNotIn('zfs_file_open', cache)
        self.assertEqual(len(edits), 4)
        for bad in (source.replace('get_system_hostid()', 'other_hostid()'),
                    source.replace('VERIFY0(uname(&hw_utsname));', 'uname(&hw_utsname);')):
            with self.assertRaises(RuntimeError):
                patch_startup(bad)
