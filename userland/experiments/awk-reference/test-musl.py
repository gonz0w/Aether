#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run mawk's pinned upstream suites and consumer fixtures in offline Linux."""

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
    binary = Path(evidence["binaries"]["mawk"]["path"])
    src = binary.parent
    if sha(binary) != evidence["binaries"]["mawk"]["sha256"]:
        raise RuntimeError("candidate changed")
    for path, digest in evidence["test_inputs"].items():
        if sha(src / path) != digest:
            raise RuntimeError("upstream input changed: " + path)
    lock = evidence["sources"]["mawk"]
    archive = ROOT / lock["archive"]
    if sha(archive) != lock["sha256"]:
        raise RuntimeError("source archive changed")
    with tarfile.open(archive) as original:
        for member in original.getmembers():
            parts = Path(member.name).parts
            if (member.isfile() and len(parts) > 2
                    and parts[1] in ("test", "examples")):
                stream = original.extractfile(member)
                with stream:
                    digest = hashlib.sha256(stream.read()).hexdigest()
                if sha(src.joinpath(*parts[1:])) != digest:
                    raise RuntimeError("fixture changed: " + member.name)
    out = Path(tempfile.mkdtemp(prefix="mawk-musl-cases-", dir=ROOT / "build"))
    out.chmod(0o755)
    print(out, flush=True)
    wrapper = out / "mawk-wrapper"
    wrapper.write_text('#!/bin/sh\nexec /usr/bin/qemu-x86_64 "' + str(binary)
                       + '" "$@"\n')
    wrapper.chmod(0o555)
    scratch = out / "scratch"
    scratch.mkdir(mode=0o777)
    scratch.chmod(0o777)
    results = []
    env = dict(os.environ, LC_ALL="C")

    def run(name, args):
        container = "userland-mawk-" + uuid.uuid4().hex
        command = [PODMAN, "run", "--name", container, "--rm",
                   "--pull=never", "--network=none", "--read-only",
                   "--cap-drop=all", "--security-opt=no-new-privileges",
                   "--user=65534:65534", "--memory=512m", "--pids-limit=32",
                   "--mount", f"type=bind,src={ROOT},dst={ROOT},ro=true",
                   "--mount", f"type=bind,src={scratch},dst=/scratch",
                   "--env", "LC_ALL=C", "--env", "TMPDIR=/scratch",
                   "--env", "AWK=" + str(wrapper),
                   "--env", "MAWK=" + str(wrapper),
                   "--workdir=/scratch", "--entrypoint=/bin/sh",
                   IMAGE] + args
        try:
            result = subprocess.run(command, capture_output=True, timeout=180,
                                    cwd=ROOT, env=env)
            status = result.returncode
            stdout, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired as error:
            status = "timeout"
            stdout, stderr = error.stdout or b"", error.stderr or b""
        finally:
            cleanup = subprocess.run([PODMAN, "rm", "--force", "--ignore",
                                      container], capture_output=True, timeout=15,
                                     cwd=ROOT, env=env)
        (out / (name + ".stdout")).write_bytes(stdout)
        (out / (name + ".stderr")).write_bytes(stderr)
        (out / (name + ".cleanup.stdout")).write_bytes(cleanup.stdout)
        (out / (name + ".cleanup.stderr")).write_bytes(cleanup.stderr)
        row = {"case": name, "argv": command, "status": status,
               "cleanup_status": cleanup.returncode,
               "pass": status == 0 and cleanup.returncode == 0}
        results.append(row)
        (out / "results.json").write_text(
            json.dumps(results, indent=2) + "\n")
        return row, stdout, stderr

    run("environment", ["-c",
        "uname -a && /usr/bin/qemu-x86_64 --version && "
        "/usr/local/bin/python3 --version && "
        "sha256sum /usr/bin/qemu-x86_64 /bin/sh /usr/local/bin/python3"])
    if "math_probe_sha256" in evidence:
        if sha(build / "math-probe") != evidence["math_probe_sha256"]:
            raise RuntimeError("math probe changed")
        row, stdout, stderr = run("math-probe", ["-c",
            'exec /usr/bin/qemu-x86_64 "$1"', "probe", 
            str(build / "math-probe")])
        row["pass"] &= stdout == b"" and stderr == b""
    for suite in ("mawktest", "mawkerrs", "fpe_test"):
        # Whole source supplies examples/decl.awk as well as the test tree.
        row, stdout, stderr = run(suite, ["-c",
            'cp -R "$1" "/scratch/$2" && cd "/scratch/$2/test" && /bin/sh "./$2"',
            "upstream", str(src), suite])
        log = stdout + stderr
        row["skipped"] = b"skipping" in log.lower()
        row["reported_failure"] = b"?? fail" in log
        row["pass"] &= not row["skipped"] and not row["reported_failure"]
        marker = b"results consistent:" if suite == "fpe_test" else b"tested "
        row["completion_marker"] = marker in stdout
        row["pass"] &= row["completion_marker"]
        if suite != "fpe_test":
            row["groups"] = sum(line.endswith(b" OK")
                                and not line.startswith(b"tested ")
                                for line in stdout.splitlines())
            expected = sum(line.lstrip().startswith("Begin ") for line in
                           (src / "test" / suite).read_text().splitlines())
            row["expected_groups"] = expected
            row["pass"] &= expected > 0 and row["groups"] == expected
        print(suite, row["pass"], flush=True)
    row, stdout, stderr = run("consumers", ["-c",
        'exec /usr/local/bin/python3 "$1" "$2" --qemu --output-root /scratch',
        "consumers", str(HERE / "test.py"), str(build)])
    summaries = list(scratch.glob("awk-cases-*/summary.json"))
    if len(summaries) == 1:
        consumer = json.loads(summaries[0].read_text())
        row["observed_cases"] = len(consumer["results"])
        row["pass"] &= (consumer["expected_cases"] == 11
                        and len(consumer["results"]) == 11
                        and all(case["pass"] for case in consumer["results"]))
        shutil.copyfile(summaries[0], out / "consumer-summary.json")
    else:
        row["pass"] = False
    summary = {"scope": "Linux x86-64 QEMU; not Aether/POSIX certification",
               "image": IMAGE, 
               "build_receipt_sha256": sha(build / "evidence.json"),
               "runner_sha256": sha(Path(__file__)),
               "consumer_runner_sha256": sha(HERE / "test.py"),
               "wrapper_sha256": sha(wrapper), "python": sys.version,
               "results": results, "pass": all(row["pass"] for row in results)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "INCOMPLETE", flush=True)
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
