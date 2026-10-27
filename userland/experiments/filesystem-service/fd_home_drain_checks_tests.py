# SPDX-License-Identifier: BSD-2-Clause
"""Mock-only controller cleanup/deadline controls; no compiler or child process.

From userland: python3 -B experiments/filesystem-service/fd_home_drain_checks_tests.py
"""
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    "fd_home_drain_checks", Path(__file__).with_name("fd_home_drain_checks.py"))
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


class Clock:
    def __init__(self, now=0):
        self.now = now

    def monotonic(self):
        return self.now


class ControllerTests(unittest.TestCase):
    def setUp(self):
        # Platform metadata may run host probes; this controller test must not.
        probe = mock.patch.object(checks.platform, "platform", return_value="mock-host")
        probe.start()
        self.addCleanup(probe.stop)
        self.root = Path(tempfile.mkdtemp(prefix="af09-controller-test-"))
        self.work = self.root / "work"
        self.work.mkdir()
        self.nested = self.work / "child.process.json"
        self.nested.write_text('{"mock_only":true,"cleanup":"unknown"}\n')
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.destination = self.evidence / "result.json"
        self.clock = Clock()
        self.record = dict(result="pass", commands=[],
                           process=dict(state="idle", cleanup="complete"))

    def tearDown(self):
        # Every retained directory here belongs to a mock with no actual child.
        # Only the test, after retention assertions, removes these fixed fixtures.
        shutil.rmtree(self.root)

    def helper(self, metadata=None, error=None):
        def run(*args, **kwargs):
            self.assertEqual(self.record["process"]["state"], "inflight")
            self.assertEqual(self.record["process"]["cleanup"], "unknown")
            if error is not None:
                raise error
            return SimpleNamespace(record=metadata, returncode=metadata.get("exit", 0),
                                   stdout=b"", stderr=b"")
        return dict(run=run, clean_env=lambda work: {})

    def finish(self):
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic):
            checks.finish(self.record, {}, self.work, 0, 300, self.destination)
        return json.loads(self.destination.read_text())

    def test_recipe_keeps_native_yield_visible(self):
        self.assertFalse(any("sched_yield" in flag for flag in checks.DOUBLES))
        self.assertIn("-Dpipe=aefd_home_drain_test_pipe", checks.DOUBLES)
        self.assertIn("-Dfork=aefd_home_drain_test_fork", checks.DOUBLES)
        self.assertIn("-D__builtin_trap=aefd_home_drain_test_trap", checks.DOUBLES)

    def test_check_retains_helper_raise(self):
        def run(*args, **kwargs):
            raise RuntimeError("mock helper raised after possibly starting child")
        proc = dict(run=run, clean_env=lambda work: {})
        with mock.patch.object(checks.runpy, "run_path", return_value=proc), \
                mock.patch.object(checks, "closure", return_value={}), \
                mock.patch.object(checks, "sha", return_value="fixed"), \
                mock.patch.object(checks.tempfile, "mkdtemp", return_value=str(self.work)), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            status = checks.check(self.evidence)
        self.assertEqual(status, 1)
        self.assertTrue(self.nested.exists(), "helper raise must retain unknown-child evidence")
        result = json.loads((self.evidence / "c-host-01.json").read_text())
        self.assertEqual(result["process"]["cleanup"], "unknown")
        self.assertEqual(result["failures"][0]["kind"], "helper-exception")
        self.assertEqual(result["retained_work"], str(self.work))

    def test_initial_hash_expiry_prevents_helper(self):
        called = []

        def closure(paths):
            self.clock.now = 301
            return {}

        def run(*args, **kwargs):
            called.append(True)
            raise RuntimeError("helper must not be called after initial hash expiry")
        proc = dict(run=run, clean_env=lambda work: {})
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic), \
                mock.patch.object(checks.runpy, "run_path", return_value=proc), \
                mock.patch.object(checks, "closure", side_effect=closure), \
                mock.patch.object(checks, "sha", return_value="fixed"), \
                mock.patch.object(checks.tempfile, "mkdtemp", return_value=str(self.work)), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            status = checks.check(self.evidence)
        self.assertEqual(status, 1)
        self.assertFalse(called, "initial hash/setup must consume aggregate budget")
        result = json.loads((self.evidence / "c-host-01.json").read_text())
        self.assertTrue(any(item["kind"] == "aggregate-deadline"
                            for item in result["failures"]))

    def test_unknown_and_unresolved_cleanup_retain(self):
        for cleanup in (None, "unknown", "not-started", "unresolved"):
            with self.subTest(cleanup=cleanup):
                self.record = dict(result="pass", commands=[],
                                   process=dict(state="idle", cleanup="complete"))
                metadata = dict(complete=False, exit=1, failure="mock-incomplete")
                if cleanup is not None:
                    metadata["cleanup"] = cleanup
                with mock.patch.object(checks.time, "monotonic", self.clock.monotonic):
                    with self.assertRaises(RuntimeError):
                        checks.run_child(self.helper(metadata), self.work, self.record,
                                         300, "mock", ["/mock/tool"])
                result = self.finish()
                self.assertTrue(self.nested.exists())
                self.assertEqual(result["result"], "failed")
                self.assertEqual(result["failures"][0]["kind"], "cleanup-unresolved")
                self.assertEqual(result["commands"][0].get("cleanup"), cleanup)
                self.assertEqual(result["retained_work"], str(self.work))

    def test_reported_complete_cannot_override_unresolved_cleanup(self):
        metadata = dict(complete=True, cleanup="unresolved", exit=0, failure=None)
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic):
            with self.assertRaises(RuntimeError):
                checks.run_child(self.helper(metadata), self.work, self.record,
                                 300, "mock", ["/mock/tool"])
        self.finish()
        self.assertTrue(self.nested.exists())
        self.assertEqual(self.record["result"], "failed")

    def test_known_cleanup_failure_compacts_and_keeps_timeout(self):
        metadata = dict(complete=False, cleanup="complete", exit=-9, failure="timeout")
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic):
            with self.assertRaises(RuntimeError):
                checks.run_child(self.helper(metadata), self.work, self.record,
                                 300, "mock", ["/mock/tool"])
        result = self.finish()
        self.assertFalse(self.work.exists())
        self.assertEqual(result["failures"][0]["kind"], "timeout")
        self.assertEqual(result["commands"][0]["cleanup"], "complete")
        self.assertEqual(result["commands"][0]["failure"], "timeout")

    def test_known_cleanup_nonzero_compacts_as_check_failure(self):
        metadata = dict(complete=True, cleanup="complete", exit=1, failure=None)
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic):
            with self.assertRaises(RuntimeError):
                checks.run_child(self.helper(metadata), self.work, self.record,
                                 300, "mock", ["/mock/tool"])
        self.finish()
        self.assertFalse(self.work.exists())
        self.assertEqual(self.record["failures"][0]["kind"], "check-failure")

    def test_complete_success_removes_owned_work(self):
        metadata = dict(complete=True, cleanup="complete", exit=0, failure=None)
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic), \
                contextlib.redirect_stderr(io.StringIO()):
            checks.run_child(self.helper(metadata), self.work, self.record,
                             300, "mock", ["/mock/tool"])
        self.finish()
        self.assertFalse(self.work.exists())
        self.assertEqual(self.record["result"], "pass")

    def test_final_hash_expiry_cannot_pass(self):
        original = checks.sha
        expected = original(self.nested)

        def sha(path):
            self.clock.now = 301
            return original(path)
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic), \
                mock.patch.object(checks, "sha", side_effect=sha):
            checks.finish(self.record, {str(self.nested): expected}, self.work,
                          0, 300, self.destination)
        self.assertEqual(self.record["result"], "failed")
        self.assertEqual(self.record["failures"][0]["kind"], "aggregate-deadline")
        self.assertFalse(self.work.exists())

    def test_cleanup_expiry_cannot_pass(self):
        original = shutil.rmtree

        def remove(path):
            original(path)
            self.clock.now = 301
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic), \
                mock.patch.object(checks.shutil, "rmtree", side_effect=remove):
            checks.finish(self.record, {}, self.work, 0, 300, self.destination)
        self.assertEqual(self.record["result"], "failed")
        self.assertEqual(self.record["failures"][0]["kind"], "aggregate-deadline")

    def test_receipt_write_expiry_cannot_pass(self):
        clock = self.clock
        destination = self.destination

        class SlowReceipt:
            def write_text(self, text):
                destination.write_text(text)
                clock.now = 301
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic):
            checks.finish(self.record, {}, self.work, 0, 300, SlowReceipt())
        result = json.loads(self.destination.read_text())
        self.assertEqual(result["result"], "failed")
        self.assertEqual(result["failures"][0]["kind"], "aggregate-deadline")

    def test_failed_owned_removal_is_not_complete_cleanup(self):
        with mock.patch.object(checks.time, "monotonic", self.clock.monotonic), \
                mock.patch.object(checks.shutil, "rmtree", side_effect=OSError("mock removal failure")):
            checks.finish(self.record, {}, self.work, 0, 300, self.destination)
        self.assertTrue(self.nested.exists())
        self.assertEqual(self.record["result"], "failed")
        self.assertEqual(self.record["failures"][0]["kind"], "work-cleanup-failure")
        self.assertEqual(self.record["cleanup"], "owned work removal unresolved")


if __name__ == "__main__":
    unittest.main()
