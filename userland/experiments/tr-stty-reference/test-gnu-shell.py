#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run pinned GNU shell/PTY tests in one owned offline container; Python 3.12+."""

import argparse
import hashlib
import json
import os
import re
import shlex
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PODMAN = "/opt/homebrew/bin/podman"
IMAGE = "8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--getlimits", type=Path, required=True)
    parser.add_argument("--extended", action="store_true")
    args = parser.parse_args()
    build = args.build.resolve()
    evidence = json.loads((build / "evidence.json").read_text())
    if set(evidence["binaries"]) != {"tr", "stty"}:
        raise RuntimeError("wrong binary inventory")
    for row in evidence["binaries"].values():
        if sha(Path(row["path"])) != row["sha256"]:
            raise RuntimeError("binary changed")
    helper_receipt = args.getlimits.resolve() / "evidence.json"
    helper = json.loads(helper_receipt.read_text())
    if set(helper["binaries"]) != {"getlimits"}:
        raise RuntimeError("wrong helper inventory")
    row = helper["binaries"]["getlimits"]
    if sha(Path(row["path"])) != row["sha256"]:
        raise RuntimeError("helper changed")
    lock = json.loads((HERE / "source.lock.json").read_text())["coreutils"]
    if sha(ROOT / lock["archive"]) != lock["sha256"]:
        raise RuntimeError("source archive changed")
    out = Path(tempfile.mkdtemp(prefix="gnu-shell-", dir=ROOT / "build"))
    print(out, flush=True)
    inputs = {}
    with tarfile.open(ROOT / lock["archive"]) as archive:
        for name in ("tests/init.sh", "init.cfg", "COPYING",
                     "tests/tr/tr-case-class.sh", "tests/stty/stty-row-col.sh",
                     "tests/stty/stty-invalid.sh", "tests/stty/stty.sh",
                     "tests/stty/stty-pairs.sh", "src/stty.c"):
            with archive.extractfile("coreutils-9.11/" + name) as stream:
                data = stream.read()
            inputs[name] = hashlib.sha256(data).hexdigest()
            target = out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    (out / "src").mkdir(exist_ok=True)
    candidates = dict(evidence["binaries"], **helper["binaries"])
    for name, row in candidates.items():
        wrapper = out / "src" / name
        wrapper.write_text("#!/bin/sh\nexec /usr/bin/qemu-x86_64 "
                           + shlex.quote(row["path"]) + ' "$@"\n')
        wrapper.chmod(0o755)
    shutil.copyfile(HERE / "shell-cases.py", out / "shell-cases.py")
    shutil.copyfile(Path(__file__), out / "runner.py")
    shutil.copyfile(HERE / "PLAN.md", out / "PLAN.md")
    container = "userland-tr-stty-" + uuid.uuid4().hex
    env = dict(os.environ, LC_ALL="C")
    command = [PODMAN, "run", "--name", container, "--rm", "--pull=never",
               "--network=none", "--read-only", "--cap-drop=all",
               "--security-opt=no-new-privileges", "--user=65534:65534",
               "--memory=512m", "--pids-limit=32", "--mount",
               f"type=bind,src={ROOT},dst={ROOT},ro=true", "--mount",
               "type=tmpfs,dst=/scratch,tmpfs-size=67108864", "--workdir=/scratch",
               "--env", "LC_ALL=C", "--entrypoint=/usr/local/bin/python3",
               IMAGE, str(out / "shell-cases.py"), str(out)]
    if args.extended:
        command.append("--extended")
    with (out / "stdout").open("wb") as stdout:
        with (out / "stderr").open("wb") as stderr:
            try:
                result = subprocess.run(
                    command, stdout=stdout, stderr=stderr,
                    timeout=420 if args.extended else 180, cwd=ROOT, env=env)
                status = result.returncode
            except subprocess.TimeoutExpired:
                status = "timeout"
            finally:
                cleanup = subprocess.run(
                    [PODMAN, "rm", "--force", "--ignore", container],
                    capture_output=True, timeout=15, cwd=ROOT, env=env)
    (out / "cleanup.stdout").write_bytes(cleanup.stdout)
    (out / "cleanup.stderr").write_bytes(cleanup.stderr)
    try:
        report = json.loads((out / "stdout").read_text())
        passed = report["pass"] and len(report["results"]) == (6 if args.extended else 4)
    except (json.JSONDecodeError, KeyError):
        passed = False
    summary = {"argv": command, "image": IMAGE, "status": status,
               "cleanup_status": cleanup.returncode,
               "build_receipt_sha256": sha(build / "evidence.json"),
               "runner_sha256": sha(Path(__file__)),
               "cases_sha256": sha(out / "shell-cases.py"),
               "upstream_inputs": inputs, "extended": args.extended,
               "helper_receipt_sha256": sha(helper_receipt),
               "pass": passed and status == 0 and cleanup.returncode == 0}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "INCOMPLETE")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
