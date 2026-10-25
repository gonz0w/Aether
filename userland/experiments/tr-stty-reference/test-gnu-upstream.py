#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run pinned GNU tr upstream tests in one owned offline container; Python 3.12+."""

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
    parser.add_argument("--failure-control", action="store_true")
    args = parser.parse_args()
    build = args.build.resolve()
    control = args.failure_control
    evidence = json.loads((build / "evidence.json").read_text())
    if set(evidence["binaries"]) != {"tr", "stty"}:
        raise RuntimeError("wrong binary inventory")
    for row in evidence["binaries"].values():
        if sha(Path(row["path"])) != row["sha256"]:
            raise RuntimeError("binary changed")
    lock = json.loads((HERE / "source.lock.json").read_text())["coreutils"]
    if sha(ROOT / lock["archive"]) != lock["sha256"]:
        raise RuntimeError("source archive changed")
    out = Path(tempfile.mkdtemp(prefix="gnu-tr-upstream-", dir=ROOT / "build"))
    print(out, flush=True)
    inputs = {}
    with tarfile.open(ROOT / lock["archive"]) as archive:
        for name in ("tests/Coreutils.pm", "tests/CuSkip.pm",
                     "tests/tr/tr.pl", "COPYING"):
            with archive.extractfile("coreutils-9.11/" + name) as stream:
                data = stream.read()
            inputs[name] = hashlib.sha256(data).hexdigest()
            (out / Path(name).name).write_bytes(data)
    helpers = json.loads((HERE / "perl-helpers.lock.json").read_text())
    for name, row in helpers["files"].items():
        source = ROOT / helpers["root"] / name
        if sha(source) != row["sha256"]:
            raise RuntimeError("Perl helper changed")
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    spec = (out / "tr.pl").read_text()
    names = re.findall(r"^  \['([^']+)'", spec, re.MULTILINE)
    expected = {name + suffix for name in names for suffix in (".p", ".r")}
    if not expected or len(expected) != 2 * len(names):
        raise RuntimeError("empty or duplicate upstream inventory")
    wrapper = out / "tr"
    binary = evidence["binaries"]["tr"]["path"]
    body = ("exit 99\n" if control else
            "exec /usr/bin/qemu-x86_64 " + shlex.quote(binary) + ' "$@"\n')
    wrapper.write_text("#!/bin/sh\n" + body)
    wrapper.chmod(0o755)
    script = out / "run.sh"
    script.write_text(
        "#!/bin/sh\nset -e\n"
        + "/usr/bin/perl -v\n/usr/bin/uname -a\n"
        + "/usr/bin/sha256sum /usr/bin/perl /usr/bin/qemu-x86_64\n"
        + "/bin/sh -n " + shlex.quote(str(wrapper)) + "\n"
        + "export PATH=" + shlex.quote(str(out) + ":/usr/bin:/bin") + "\n"
        + "export built_programs=tr VERBOSE=1 DEBUG=0 srcdir="
        + shlex.quote(str(out)) + "\n"
        + "exec /usr/bin/perl -I " + shlex.quote(str(out))
        + " -MCuSkip -MCoreutils " + shlex.quote(str(out / "tr.pl")) + "\n")
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
    log = (out / "stderr").read_text()
    observed = re.findall(r"^([a-zA-Z0-9-]+\.[pr])\.\.\.$", log, re.MULTILINE)
    inventory_ok = set(observed) == expected and len(observed) == len(expected)
    passed = inventory_ok and status == 0
    if control:
        passed = inventory_ok and status == 1 and "exit status mismatch" in log
    summary = {"argv": command, "image": IMAGE, "status": status,
               "cleanup_status": cleanup.returncode,
               "build_receipt_sha256": sha(build / "evidence.json"),
               "runner_sha256": sha(Path(__file__)),
               "upstream_inputs": inputs, "perl_helpers": helpers,
               "expected_tests": sorted(expected),
               "observed_tests": observed, "failure_control": control,
               "wrapper_sha256": sha(wrapper), "script_sha256": sha(script),
               "pass": passed and cleanup.returncode == 0}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "INCOMPLETE")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
