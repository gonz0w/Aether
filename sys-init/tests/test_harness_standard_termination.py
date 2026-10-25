# SPDX-License-Identifier: BSD-2-Clause
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import test_harness_offline_locks as fixtures
import test_harness_standard_private as private_fixtures
import test_harness_standard_capture as capture_fixtures


class StandardTerminationTests(unittest.TestCase):
    def test_real_termination_reaps_child_and_removes_stage(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(root, suffix)
                marker = root / 'ready.json'
                code = ('import os,json,time\nfrom pathlib import Path\n'
                        'marker=Path(' + repr(str(marker)) + ')\n'
                        'marker.with_suffix(".tmp").write_text(json.dumps([os.getpid(),__file__]))\n'
                        'marker.with_suffix(".tmp").replace(marker)\ntime.sleep(20)\n')
                private_fixtures.PrivateStandardTests().reseal(lock, manifest, checker, code)
                Path(module.__file__).write_bytes((fixtures.ROOT / 'docs' / ('check-' + suffix + '.py')).read_bytes())
                wrapper = subprocess.Popen([sys.executable, module.__file__], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                child_pid = None
                try:
                    deadline = time.monotonic() + 5
                    while not marker.exists() and wrapper.poll() is None and time.monotonic() < deadline:
                        time.sleep(0.01)
                    self.assertTrue(marker.exists(), 'child did not become ready')
                    child_pid, staged = json.loads(marker.read_text())
                    wrapper.send_signal(signal.SIGTERM)
                    output, errors = wrapper.communicate(timeout=5)
                    self.assertEqual(wrapper.returncode, 130, errors)
                    self.assertEqual(output, b'')
                    self.assertEqual(errors, b'reference check interrupted\n')
                    with self.assertRaises(ProcessLookupError):
                        os.kill(child_pid, 0)
                    self.assertFalse(Path(staged).parents[2].exists())
                finally:
                    if wrapper.poll() is None:
                        wrapper.kill()
                    wrapper.communicate(timeout=5)
                    if child_pid is not None:
                        try:
                            os.killpg(child_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

    def test_custom_handler_restored_after_success_and_timeout(self):
        for suffix in fixtures.FAMILIES:
            for timeout in (False, True):
                with self.subTest(suffix=suffix, timeout=timeout), tempfile.TemporaryDirectory() as directory:
                    module, _, _, _ = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                    streams, _, _ = capture_fixtures.StandardCaptureTests().streams()
                    previous = signal.getsignal(signal.SIGTERM)
                    handler = lambda signum, frame: None
                    signal.signal(signal.SIGTERM, handler)
                    try:
                        with patch.object(module, 'sys', streams), patch.object(module, 'CHILD_TIMEOUT', 0.2):
                            command = [sys.executable, '-I', '-S', '-B', '-c', 'import time;time.sleep(10)' if timeout else 'pass']
                            if timeout:
                                with self.assertRaises(subprocess.TimeoutExpired):
                                    module.run_reference(command)
                            else:
                                module.run_reference(command)
                        self.assertIs(signal.getsignal(signal.SIGTERM), handler)
                    finally:
                        signal.signal(signal.SIGTERM, previous)

    def test_background_capture_does_not_manage_signals(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, _, _, _ = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                streams, _, _ = capture_fixtures.StandardCaptureTests().streams()
                errors = []
                def run():
                    try:
                        module.run_reference([sys.executable, '-I', '-S', '-B', '-c', 'pass'])
                    except BaseException as error:
                        errors.append(error)
                with patch.object(module, 'sys', streams), patch.object(module.signal, 'signal') as set_signal:
                    worker = threading.Thread(target=run)
                    worker.start()
                    worker.join(timeout=5)
                    self.assertFalse(worker.is_alive())
                    self.assertEqual(errors, [])
                    set_signal.assert_not_called()
