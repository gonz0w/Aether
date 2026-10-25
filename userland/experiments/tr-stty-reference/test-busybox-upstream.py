#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run pinned BusyBox focused upstream tests in one owned offline container; Python 3.12+."""

import hashlib
import json
import os
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
    build = Path(sys.argv[1]).resolve()
    evidence = json.loads((build / "evidence.json").read_text())
    if set(evidence["binaries"]) != {"tr", "stty"}:
        raise RuntimeError("wrong binary inventory")
    for row in evidence["binaries"].values():
        if sha(Path(row["path"])) != row["sha256"]:
            raise RuntimeError("binary changed")
    lock = evidence["sources"]["busybox"]
    if sha(ROOT / lock["archive"]) != lock["sha256"]:
        raise RuntimeError("source archive changed")
    src = Path(evidence["binaries"]["tr"]["path"]).parent
    inputs = {}
    with tarfile.open(ROOT / lock["archive"]) as archive:
        for name in ("testing.sh", "tr.tests"):
            member = archive.getmember("busybox-1.38.0/testsuite/" + name)
            with archive.extractfile(member) as stream:
                inputs[name] = hashlib.sha256(stream.read()).hexdigest()
            if sha(src / "testsuite" / name) != inputs[name]:
                raise RuntimeError("upstream test changed")
    out = Path(tempfile.mkdtemp(prefix="busybox-upstream-", dir=ROOT / "build"))
    print(out, flush=True)
    scratch = out / "scratch"
    scratch.mkdir()
    scratch.chmod(0o777)
    for name in inputs:
        shutil.copyfile(src / "testsuite" / name, out / name)
    wrapper = out / "tr"
    wrapper.write_text('#!/bin/sh\nexec /usr/bin/qemu-x86_64 "'
                       + str(src / "busybox_unstripped") + '" tr "$@"\n')
    wrapper.chmod(0o755)
    script = out / "run.sh"
    script.write_text(
        '#!/bin/bash\nset -e\n'
        'export PATH="' + str(out) + ':$PATH"\n'
        'export OPTIONFLAGS=:FEATURE_TR_CLASSES:FEATURE_TR_EQUIV:\n'
        'export ECHO=/bin/echo\n'
        'cp "' + str(out / "testing.sh") + '" /scratch/testing.sh\n'
        'exec /bin/bash "' + str(out / "tr.tests") + '"\n')
    config = (src / ".config").read_text()
    if "CONFIG_FEATURE_TR_CLASSES=y" not in config:
        raise RuntimeError("required class feature missing")
    shutil.copyfile(Path(__file__), out / "runner.py")
    container = "userland-tr-stty-" + uuid.uuid4().hex
    env = dict(os.environ, LC_ALL="C")
    command = [PODMAN, "run", "--name", container, "--rm", "--pull=never",
               "--network=none", "--read-only", "--cap-drop=all",
               "--security-opt=no-new-privileges", "--user=65534:65534",
               "--memory=512m", "--pids-limit=32", "--mount",
               f"type=bind,src={ROOT},dst={ROOT},ro=true", "--mount",
               f"type=bind,src={scratch},dst=/scratch", "--workdir=/scratch",
               "--env", "LC_ALL=C", "--entrypoint=/bin/bash",
               IMAGE, str(script)]
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
    log = (out / "stdout").read_text()
    count = sum(line.startswith("PASS: ") for line in log.splitlines())
    passed = count == 5 and "FAIL:" not in log and "SKIPPED:" not in log
    summary = {"argv": command, "image": IMAGE, "status": status,
               "cleanup_status": cleanup.returncode,
               "build_receipt_sha256": sha(build / "evidence.json"),
               "runner_sha256": sha(Path(__file__)),
               "upstream_inputs": inputs, "passed_tests": count,
               "wrapper_sha256": sha(wrapper), "script_sha256": sha(script),
               "pass": passed and status == 0 and cleanup.returncode == 0}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "INCOMPLETE")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
