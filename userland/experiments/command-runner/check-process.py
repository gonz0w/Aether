#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Meaningful process ownership/environment controls; Python 3.10+."""
import json
import os
from pathlib import Path
import sys
import tempfile
from process import alive, clean_env, run

root = Path(__file__).resolve().parents[2]
work = Path(tempfile.mkdtemp(prefix="command-process-controls-", dir=root / "build"))
print(work, flush=True)
rows = []


def check(label, code, expected, failure=None, timeout=3):
    result = run([sys.executable, "-c", code], cwd=work, env=clean_env(work),
                 work=work, label=label, timeout=timeout)
    ok = (result.returncode == expected if expected is not None else True)
    ok = ok and result.record["failure"] == failure
    ok = ok and result.record["cleanup"] == "complete"
    ok = ok and not alive(result.record["process_group"])
    rows.append({"case": label, "pass": ok, "record": result.record})
    return result


check("normal", "print('ok')", 0)
check("nonzero", "raise SystemExit(7)", 7)
code = "import os,time; pid=os.fork(); print(pid,flush=True); time.sleep(30)"
check("timeout-descendant", code, -9, "timeout", timeout=0.2)
code = "import os,time; pid=os.fork(); time.sleep(30) if pid==0 else None"
check("leader-exits", code, 0, "descendant-after-exit")
missing = run([str(work / "missing")], cwd=work, env=clean_env(work),
              work=work, label="missing", timeout=1)
rows.append({"case": "missing", "pass": missing.returncode is None
             and not missing.record["complete"]
             and missing.record["failure"].startswith("FileNotFoundError"),
             "record": missing.record})
os.environ["PATH"] = str(work / "hostile-path")
os.environ["CC"] = "/nonexistent/hostile-compiler"
os.environ["CPATH"] = str(work / "hostile-headers")
result = check("clean-environment", "import os; print(dict(os.environ))", 0)
rows.append({"case": "poison-excluded", "pass": b"hostile" not in result.stdout})
(work / "summary.json").write_text(json.dumps(rows, indent=2) + "\n")
if not all(row["pass"] for row in rows):
    raise SystemExit("FAIL: process controls")
print("PASS: seven process/environment checks")
