#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Unit controls for reduction outcome classification; no child processes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "check_parser_extended", HERE / "check-parser-extended.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Result:
    def __init__(self, code, stdout=b"", stderr=b"", complete=True):
        self.returncode = code
        self.stdout = stdout
        self.stderr = stderr
        self.record = {"complete": complete}


def old_outcome(result, directory, candidate, must_accept, oracle):
    reproduced = False
    if result.returncode == 90:
        if (b"ORACLE: " + oracle.encode() + b" ") not in result.stderr:
            raise MODULE.ReduceError("unnamed failure")
        payload = (directory / "failure.bin").read_bytes()
        meta = json.loads((directory / "failure.json").read_text())
        reproduced = (payload == candidate and meta["oracle"] == oracle
                      and meta["must_accept"] == must_accept)
    elif ((directory / "failure.bin").exists() or
          (directory / "failure.json").exists()):
        raise MODULE.ReduceError("incomplete retention")
    elif result.returncode not in (0, 91):
        raise MODULE.ReduceError("unexpected oracle exit")
    return reproduced


def write_failure(directory, data, oracle, must_accept, size=None):
    (directory / "failure.bin").write_bytes(data)
    meta = {"oracle": oracle, "size": len(data) if size is None else size,
            "must_accept": must_accept}
    (directory / "failure.json").write_text(json.dumps(meta) + "\n")


class ReductionOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="reduce-outcome-"))
        self.candidate = b"\x01\x02"
        self.oracle = "nonzero"
        self.pass_stdout = b"PASS: replay\n"
        self.fail_stderr = b"ORACLE: nonzero seed=0 offset=0 value=0\n"

    def classify(self, result):
        return MODULE.reduction_outcome(
            result, self.work, self.candidate, 0, self.oracle)

    def test_positive(self):
        write_failure(self.work, self.candidate, self.oracle, 0)
        result = Result(90, stderr=self.fail_stderr)
        self.assertTrue(self.classify(result))
        self.assertTrue(old_outcome(result, self.work, self.candidate, 0,
                                    self.oracle))

    def test_negative(self):
        result = Result(0, stdout=self.pass_stdout)
        self.assertFalse(self.classify(result))
        self.assertFalse(old_outcome(result, self.work, self.candidate, 0,
                                     self.oracle))

    def test_fixture_error_not_negative(self):
        result = Result(91)
        self.assertFalse(old_outcome(result, self.work, self.candidate, 0,
                                     self.oracle))
        with self.assertRaises(MODULE.ReduceError) as raised:
            self.classify(result)
        self.assertIn("unexpected replay exit", str(raised.exception))

    def test_mismatched_bytes_not_negative(self):
        write_failure(self.work, b"\x00\x00", self.oracle, 0)
        result = Result(90, stderr=self.fail_stderr)
        self.assertFalse(old_outcome(result, self.work, self.candidate, 0,
                                     self.oracle))
        with self.assertRaises(MODULE.ReduceError) as raised:
            self.classify(result)
        self.assertIn("mismatched replay evidence", str(raised.exception))

    def test_crash(self):
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(-11, complete=True))

    def test_cleanup_failure(self):
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(0, stdout=self.pass_stdout, complete=False))

    def test_diagnostic_noise(self):
        write_failure(self.work, self.candidate, self.oracle, 0)
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(90, stdout=b"noise\n", stderr=self.fail_stderr))

    def test_missing_success_marker(self):
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(0, stdout=b""))

    def test_mismatched_metadata(self):
        write_failure(self.work, self.candidate, "other", 0)
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(90, stderr=self.fail_stderr))

    def test_invalid_json(self):
        (self.work / "failure.bin").write_bytes(self.candidate)
        (self.work / "failure.json").write_bytes(b"{")
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(90, stderr=self.fail_stderr))

    def test_boolean_numeric_fields(self):
        write_failure(self.work, self.candidate, self.oracle, True)
        with self.assertRaises(MODULE.ReduceError):
            self.classify(Result(90, stderr=self.fail_stderr))


if __name__ == "__main__":
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful()
                     else 1)
