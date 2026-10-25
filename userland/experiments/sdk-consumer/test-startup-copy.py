#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""SDK-05 staged-source rejection control; run from the repository root."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path.cwd()
spec = importlib.util.spec_from_file_location(
    'sdk_startup', ROOT / 'experiments/sdk-consumer/check-startup.py')
startup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(startup)


class StartupCopyTests(unittest.TestCase):
    def test_changed_copy_rejects_before_compile(self):
        work = Path(tempfile.mkdtemp(prefix='sdk-copy-control-', dir=ROOT / 'build'))
        original_copy = shutil.copy2
        source = ROOT / 'experiments/native-c/native_io.c'
        source_hash = startup.sha(source)
        changed = []

        def changed_copy(src, dst, *args, **kwargs):
            result = original_copy(src, dst, *args, **kwargs)
            if Path(src) == source:
                # Model bytes copied during a transient source change. The
                # live source remains/restores pinned bytes, so a final live
                # source check cannot detect this staged-content mismatch.
                Path(dst).write_bytes(Path(dst).read_bytes() + b'\n')
                changed.append(str(dst))
            return result

        with mock.patch.object(startup.tempfile, 'mkdtemp', return_value=str(work)), \
                mock.patch.object(startup.shutil, 'copy2', side_effect=changed_copy), \
                mock.patch.object(startup, 'run', side_effect=AssertionError(
                    'compiler reached with changed staged source')) as command, \
                contextlib.redirect_stderr(io.StringIO()):
            result = startup.main()
        self.assertEqual(result, 1)
        self.assertEqual(len(changed), 1)
        command.assert_not_called()
        report = json.loads((work / 'summary.json').read_text())
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['commands'], [])
        self.assertEqual(report['error'],
                         'adapter drift before build: native_io.c')
        self.assertEqual(startup.sha(source), source_hash)
        self.assertNotEqual(startup.sha(Path(changed[0])), source_hash)


if __name__ == '__main__':
    unittest.main()
