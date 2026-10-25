# SPDX-License-Identifier: BSD-2-Clause
"""Isolated imported runtime constructor checks; no CLI or guest execution."""
from pathlib import Path
import sys
import time

from home_runtime import runtime_archive, sha, verify_dependency

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check(record, work, proc, tools, deadline):
    sources = [Path(__file__).resolve(), ROOT / "scripts/home_runtime.py",
               ROOT / "tests/test_home_runtime.py", ROOT / "scripts/openzfs_failure.py"]
    frozen = {str(path): sha(path) for path in sources}
    frozen[str(Path(sys.executable).resolve())] = sha(sys.executable)
    dependency = ROOT / ".deps/native-utc-v3"
    verified = verify_dependency(dependency, tools)
    frozen.update(verified["inputs"])
    record.setdefault("sources", {}).update(frozen)
    record["home_runtime_inputs"] = dict(frozen)
    record["home_runtime_dependency"] = {"seals": verified["seals"], "tools": verified["tools"]}
    env = proc.clean_env(work)

    def command(args, log, rejection=None):
        args = list(map(str, args))
        label = Path(log).stem
        require(rejection is None, "runtime check has no subprocess rejection selection")
        for name, digest in frozen.items():
            require(sha(name) == digest, "runtime input changed before child: " + name)
        remaining = deadline - time.monotonic()
        require(remaining > 0, "runtime cumulative deadline before " + label)
        result = proc.run(args, cwd=ROOT, env=env, work=work, label=label,
                          timeout=min(180, remaining))
        record["rows"].append({"label": label, "process": result.record,
            "stdout": result.stdout.decode(errors="replace")[-5000:],
            "stderr": result.stderr.decode(errors="replace")[-5000:]})
        record["home_runtime_artifacts"] = {str(path): sha(path) for path in work.rglob("*")
            if path.is_file() and path.suffix in (".o", ".a", ".c", ".h")}
        for name, digest in frozen.items():
            require(sha(name) == digest, "runtime input changed after child: " + name)
        require(result.returncode == 0 and result.record["complete"] and
                result.record["cleanup"] == "complete", label)
        require(time.monotonic() <= deadline, "runtime cumulative deadline after " + label)
        return result.stdout.decode()

    command([sys.executable, "-O", "-B", "-m", "unittest", "discover", "-s", "tests",
             "-p", "test_home_runtime.py"], work / "runtime-unit-tests.log")
    record["home_runtime_unit_methods"] = 7
    port = work / "runtime-port"
    port.mkdir()
    try:
        result = runtime_archive(port, dependency, tools, command)
        record["home_runtime"] = result
        for name, digest in result["inputs"].items():
            require(sha(name) == digest, "runtime final dependent input changed: " + name)
        require(result["extracted_member_cleanup"] == "complete", "runtime proof member cleanup")
        record["sources"].update(result["inputs"])
    finally:
        record["home_runtime_artifacts"] = {str(path): sha(path) for path in work.rglob("*")
            if path.is_file() and path.suffix in (".o", ".a", ".c", ".h")}
        for name, digest in frozen.items():
            require(sha(name) == digest, "runtime final input changed: " + name)
