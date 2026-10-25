# SPDX-License-Identifier: BSD-2-Clause
"""Fixed approved writer-only diagnostic bound; process doubles never boot."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import test_zpl_pair as controls
import test_openzfs_zpl_sync_stages as sync
import native_smoke as native
import zpl_pair as pair
from openzfs_namespace import native_media_snapshot

ROOT = pair.ROOT


class WriterBudget(unittest.TestCase):
    def test_wrong_role_authority_marker_or_mode_rejects_before_intake(self):
        with patch.object(native, 'verify', side_effect=AssertionError('intake')):
            common = dict(_pair_stop=True, _zpl_writer_60s=True, block_namespace=True,
                          block_large=True, block_disk='/absent', marker=pair.MARKER.encode())
            image = ROOT / 'zig-out' / (pair.PREFIX + 'owned') / 'writer/aether.iso'
            for args in ({'_pair_stop': False}, {'block_namespace': False}, {'block_large': False},
                         {'block_disk': None}, {'zpl_writer': {}}, {'expected_panic': b'x'},
                         {'marker': b'AETHER NATIVE C PASS'}, {'_zpl_writer_60s': 60}):
                with self.subTest(args=args), self.assertRaises(ValueError):
                    native.run(image, **(common | args))
            for wrong in (image.parent.parent / 'reader/aether.iso', Path('/tmp/else/writer/aether.iso')):
                with self.assertRaises(ValueError): native.run(wrong, **common)

    def test_actual_runner_uses_fixed60_only_for_writer_and_preserves_default30(self):
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT / 'zig-out') as directory:
            root = Path(directory)
            disk = root / 'native-namespace.raw'
            with disk.open('wb') as f: f.truncate(1073750016)
            for role, extended, expected in (('writer', True, 60), ('writer', False, 30), ('baseline', False, 30), ('reader', False, 30)):
                dest = root / role; dest.mkdir(exist_ok=True)
                process = Mock(); process.poll.return_value = 0
                with patch.object(native, 'verify'), patch.object(native.subprocess, 'check_output', return_value='QEMU emulator version ' + native.LOCK['qemu']), \
                     patch.object(native.subprocess, 'Popen', return_value=process), patch.object(native.shutil, 'copyfile'), \
                     patch('openzfs_namespace.native_media_snapshot'), patch.object(native, 'wait_for_boot') as wait:
                    native.run(dest / 'aether.iso', _pair_stop=True, _zpl_writer_60s=extended,
                               block_namespace=True, block_large=True, block_disk=disk, marker=pair.MARKER.encode())
                self.assertEqual(wait.call_args.args[2], expected)
                command = json.loads((dest / 'native-qemu-command.json').read_text())
                self.assertEqual(command.get('writer_watchdog_seconds'), 60 if extended else None)
                process.terminate.assert_not_called()

    def test_timeout_still_terminates_and_joins_and_never_becomes_pass(self):
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT / 'zig-out') as directory:
            root = Path(directory); (root / 'writer').mkdir()
            disk = root / 'native-namespace.raw'
            with disk.open('wb') as f: f.truncate(1073750016)
            for stop_error in (False, True):
                process = Mock(); process.poll.return_value = None
                process.wait.side_effect = subprocess.TimeoutExpired('qemu', 3) if stop_error else [0]
                with patch.object(native, 'verify'), patch.object(native.subprocess, 'check_output', return_value='QEMU emulator version ' + native.LOCK['qemu']), \
                     patch.object(native.subprocess, 'Popen', return_value=process), patch.object(native.shutil, 'copyfile'), \
                     patch('openzfs_namespace.native_media_snapshot'), patch.object(native, 'wait_for_boot', side_effect=TimeoutError('bounded60')):
                    with self.assertRaises(native.NativeStopError if stop_error else TimeoutError):
                        native.run(root / 'writer/aether.iso', _pair_stop=True, _zpl_writer_60s=True,
                                   block_namespace=True, block_large=True, block_disk=disk, marker=pair.MARKER.encode())
                process.terminate.assert_called_once()
                self.assertEqual(process.wait.call_count, 2 if stop_error else 1)
                self.assertTrue(all(c.kwargs == {'timeout': 3} for c in process.wait.call_args_list))

    def test_pair_dispatch_has60_writer_only_and_keeps_full_admission(self):
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        flags = []
        real_execute = pair.execute_pair
        def execute(output, builds, record):
            # Capture the actual dispatcher run arguments while retaining all
            # trace/cleanup/media interpretation in PairControls.execute.
            actual_run = pair.run
            def capture(image, **kwargs):
                flags.append((image.parent.name, kwargs.get('_zpl_writer_60s', False)))
                return actual_run(image, **kwargs)
            with patch.object(pair, 'run', side_effect=capture):
                return real_execute(output, builds, record)
        with patch.object(pair, 'execute_pair', side_effect=execute):
            result = f.execute(writer_text=sync.success(), txg_worker_diagnostic=True, sync_stages=True, writer_60s=True)
        self.assertEqual(flags, [('baseline', False), ('writer', True), ('reader', False)])
        self.assertTrue(result['fresh_vm_readback_qualified'])
        self.assertEqual([c['watchdog_seconds'] for c in result['cases']], [30, 60, 30])
        for bad in (sync.outer.observations(b'BIUVWLPOAMTbeicpv'), sync.success().replace('phase=7', 'phase=6', 1)):
            with self.assertRaises(ValueError): f.execute(writer_text=bad, txg_worker_diagnostic=True, sync_stages=True, writer_60s=True)
            self.assertEqual(f.launched, ['baseline', 'writer'])

    def test_cli_and_direct_pair_require_the_exact_refinement_before_builds(self):
        with patch.object(pair.runtime, 'suite', side_effect=AssertionError('build')):
            with self.assertRaisesRegex(ValueError, 'writer60 requires'):
                pair.pair(Path('/absent'), Path('/absent'), writer_60s=True)
        for args in (['--writer-60s'], ['--writer-60s', '--repeated-writes', '--txg-worker-diagnostic']):
            r = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'), *args, '--delivery', '/absent', '--utc-delivery', '/absent'], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 64)
