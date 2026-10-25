#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run GNU fixtures in one owned offline container; Python 3.12+."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PODMAN = "/opt/homebrew/bin/podman"
IMAGE = "8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    build = Path(sys.argv[1]).resolve()
    evidence = json.loads((build / "evidence.json").read_text())
    if set(evidence["binaries"]) != {"tr", "stty"}:
        raise RuntimeError("wrong binary inventory")
    for row in evidence["binaries"].values():
        if sha(Path(row["path"])) != row["sha256"]:
            raise RuntimeError("binary changed")
    out = Path(tempfile.mkdtemp(prefix="tr-stty-cases-", dir=ROOT / "build"))
    print(out, flush=True)
    scratch = out / "scratch"
    scratch.mkdir()
    scratch.chmod(0o777)
    shutil.copyfile(HERE / "cases.py", out / "cases.py")
    shutil.copyfile(Path(__file__), out / "runner.py")
    container = "userland-tr-stty-" + uuid.uuid4().hex
    env = dict(os.environ, LC_ALL="C")
    command = [PODMAN, "run", "--name", container, "--rm", "--pull=never",
               "--network=none", "--read-only", "--cap-drop=all",
               "--security-opt=no-new-privileges", "--user=65534:65534",
               "--memory=512m", "--pids-limit=32", "--mount",
               f"type=bind,src={ROOT},dst={ROOT},ro=true", "--mount",
               f"type=bind,src={scratch},dst=/scratch", "--workdir=/scratch",
               "--env", "LC_ALL=C", "--entrypoint=/usr/local/bin/python3",
               IMAGE, str(out / "cases.py"), str(build)]
    with (out / "stdout").open("wb") as stdout:
        with (out / "stderr").open("wb") as stderr:
            try:
                result = subprocess.run(
                    command, stdout=stdout, stderr=stderr,
                    timeout=180, cwd=ROOT, env=env)
                status = result.returncode
            except subprocess.TimeoutExpired:
                status = "timeout"
            finally:
                cleanup = subprocess.run(
                    [PODMAN, "rm", "--force", "--ignore", container],
                    capture_output=True, timeout=15, cwd=ROOT, env=env)
    (out / "cleanup.stdout").write_bytes(cleanup.stdout)
    (out / "cleanup.stderr").write_bytes(cleanup.stderr)
    if (scratch / "partial-cases.json").is_file():
        shutil.copyfile(scratch / "partial-cases.json",
                        out / "partial-cases.json")
    passed = False
    if (scratch / "cases.json").is_file():
        cases = json.loads((scratch / "cases.json").read_text())
        shutil.copyfile(scratch / "cases.json", out / "cases.json")
        passed = (cases["pass"] and len(cases["results"]) == 17
                  and all(row["pass"] for row in cases["results"]))
    summary = {"argv": command, "image": IMAGE, "status": status,
               "cleanup_status": cleanup.returncode,
               "build_receipt_sha256": sha(build / "evidence.json"),
               "runner_sha256": sha(Path(__file__)),
               "cases_sha256": sha(out / "cases.py"),
               "pass": passed and status == 0 and cleanup.returncode == 0}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "INCOMPLETE")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
