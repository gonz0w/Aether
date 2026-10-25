#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Real host process boundary controls for the quality adapter; Python 3.10+."""

import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import shutil
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
RUN = runpy.run_path(str(ROOT / "docs/quality/processes.py"))["run_checked"]
ALIVE = runpy.run_path(str(
    ROOT / "experiments/command-runner/process.py"
))["alive"]


class ProcessTests(unittest.TestCase):
    def execute(self, code, failure=None, timeout=3, executable=None):
        stdout, stderr = io.BytesIO(), io.BytesIO()
        with patch.object(sys, "stdout", types.SimpleNamespace(buffer=stdout)):
            with patch.object(sys, "stderr", types.SimpleNamespace(buffer=stderr)):
                argv = [executable or sys.executable, "-c", code]
                if failure:
                    with self.assertRaises(ValueError) as caught:
                        RUN(argv, timeout)
                    work = Path(str(caught.exception).split(
                        "retained evidence: ", 1)[1])
                else:
                    work = RUN(argv, timeout)
        print(f"retained: {work}", file=sys.stderr)
        record = json.loads((work / "check.process.json").read_text())
        if "process_group" in record:
            self.assertFalse(ALIVE(record["process_group"]))
            self.assertEqual(record["cleanup"], "complete")
        for name, captured in [("stdout", stdout), ("stderr", stderr)]:
            path = work / ("check." + name)
            self.assertEqual(captured.getvalue(),
                             path.read_bytes() if path.exists() else b"")
        if failure:
            self.assertTrue(record["failure"] or record["exit"] != 0)
        else:
            self.assertTrue(record["complete"])
            self.assertEqual(record["exit"], 0)
        return record, stdout.getvalue(), stderr.getvalue()

    def test_separate_streams(self):
        _, out, err = self.execute(
            "import os; os.write(1,b'raw\\x00out'); os.write(2,b'raw\\x00err')")
        self.assertEqual(out, b"raw\x00out")
        self.assertEqual(err, b"raw\x00err")

    def test_nonzero(self):
        rec, _, _ = self.execute("raise SystemExit(7)", failure=True)
        self.assertEqual(rec["exit"], 7)

    def test_missing(self):
        rec, _, _ = self.execute("", failure=True,
                                 executable="/nonexistent/quality-python")
        self.assertTrue(rec["failure"].startswith("FileNotFoundError"))

    def test_timeout_descendant(self):
        rec, _, _ = self.execute(
            "import os,time; os.fork(); time.sleep(30)",
            failure=True, timeout=0.2)
        self.assertEqual(rec["failure"], "timeout")

    def test_leader_exits(self):
        rec, _, _ = self.execute(
            "import os,time; pid=os.fork(); time.sleep(30) if pid==0 else None",
            failure=True)
        self.assertEqual(rec["exit"], 0)
        self.assertEqual(rec["failure"], "descendant-after-exit")

    def test_output_limit(self):
        rec, out, _ = self.execute(
            "import os\nwhile True: os.write(1,b'x'*65536)", failure=True)
        self.assertLessEqual(len(out), 16 * 1024**2)
        self.assertNotEqual(rec["exit"], 0)

    def test_environment(self):
        with patch.dict(os.environ, {"CPATH": "hostile", "SECRET_TEST": "omit"}):
            _, out, _ = self.execute(
                "import os; print(os.environ.get('CPATH')); "
                "print(os.environ.get('SECRET_TEST')); print(os.environ['PATH'])")
        self.assertEqual(out, b"None\nNone\n/usr/bin:/bin\n")

    def test_wrapper_pin_rejection(self):
        for name, folder in [("standards", "foundations"),
                             ("distribution", "distribution"),
                             ("experience", "experience")]:
            with self.subTest(wrapper=name):
                with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmp:
                    fixture = Path(tmp)
                    docs = fixture / "docs"
                    (docs / "quality").mkdir(parents=True)
                    release = docs / "vendor" / ("aether-" + folder) / "v0.1.0"
                    release.mkdir(parents=True)
                    (release / "SHA256SUMS").write_text("invalid manifest\n")
                    shutil.copyfile(ROOT / "docs" / (name + ".lock"),
                                    docs / (name + ".lock"))
                    wrapper = docs / ("check-" + name + ".py")
                    shutil.copyfile(ROOT / "docs" / wrapper.name, wrapper)
                    marker = fixture / "executed"
                    (docs / "quality/processes.py").write_text(
                        "from pathlib import Path\nPath(" + repr(str(marker))
                        + ").write_text('must not execute')\n")
                    rec, _, err = self.execute(
                        "import runpy; runpy.run_path(" + repr(str(wrapper))
                        + ", run_name='__main__')", failure=True)
                    self.assertEqual(rec["exit"], 1)
                    self.assertIn(b"manifest pin mismatch", err)
                    self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
