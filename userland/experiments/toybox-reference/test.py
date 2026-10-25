#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run pinned Toybox under QEMU Linux in owned containers (Python 3.12+)."""

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


def matches(status, expected_status, cleanup, stdout, expected, stderr,
            diagnostic):
    return (status == expected_status and cleanup == 0
            and (expected is None or stdout == expected)
            and (diagnostic is None or diagnostic in stderr))


def main():
    build = Path(sys.argv[1]).resolve()
    evidence = json.loads((build / "evidence.json").read_text())
    src = build / "toybox-0.8.14"
    if sha(src / "toybox") != evidence["elf_sha256"]:
        raise RuntimeError("candidate changed")
    for path, digest in evidence["files"].items():
        if sha(Path(path)) != digest:
            raise RuntimeError("build input changed: " + path)
    for path, digest in evidence["test_inputs"].items():
        if sha(src / path) != digest:
            raise RuntimeError("upstream test input changed: " + path)
    out = Path(tempfile.mkdtemp(prefix="toybox-cases-", dir=ROOT / "build"))
    print(out, flush=True)
    shutil.copyfile(src / "toybox", out / "toybox")
    (out / "toybox").chmod(0o555)
    shutil.copytree(src / "tests", out / "tests")
    shutil.copyfile(src / "scripts/runtest.sh", out / "runtest.sh")
    wrappers = out / "bin"
    wrappers.mkdir()
    for command in ("cat", "wc", "printf", "test", "[", "true", "false"):
        wrapper = wrappers / command
        wrapper.write_text(
            '#!/bin/sh\nexec /usr/bin/qemu-x86_64 /inputs/toybox '
            + command + ' "$@"\n'
        )
        wrapper.chmod(0o555)
    # Upstream printf tests use only xxd -p; this host helper is not shipped.
    hex_helper = wrappers / "xxd"
    hex_helper.write_text(
        '#!/usr/local/bin/python3\n'
        '# SPDX-License-Identifier: BSD-2-Clause\n'
        'import sys\n'
        'if sys.argv[1:] != ["-p"]: sys.exit(64)\n'
        'while True:\n'
        '    data = sys.stdin.buffer.read(30)\n'
        '    if not data: break\n'
        '    print(data.hex())\n'
    )
    hex_helper.chmod(0o555)
    upstream = out / "upstream.sh"
    upstream.write_text(
        '#!/bin/bash\nset -o pipefail\n'
        'export PATH=/inputs/bin:/usr/bin:/bin LC_ALL=C\n'
        'export TESTDIR=/scratch FILES=/inputs/tests/files\n'
        'export CMDNAME="$1" C="/inputs/bin/$1"\n'
        'cd /scratch || exit 90\n'
        'source /inputs/runtest.sh\n'
        'enable -n test [ printf true false\n'
        'source "/inputs/tests/$1.test"\n'
        'echo "UPSTREAM_FAILCOUNT=$FAILCOUNT"\n'
        '[ "$FAILCOUNT" -eq 0 ]\n'
    )
    results = []
    env = dict(os.environ, LC_ALL="C")

    def run(name, args, status, output=None, diagnostic=None, stdin=b"",
            entry="/usr/bin/qemu-x86_64", timeout=45):
        container = "userland-toybox-" + uuid.uuid4().hex
        command = [
            PODMAN, "run", "--name", container, "--rm", "-i",
            "--pull=never", "--network=none", "--read-only",
            "--cap-drop=all", "--security-opt=no-new-privileges",
            "--user=65534:65534", "--memory=512m", "--pids-limit=32",
            "--tmpfs", "/scratch:rw,nosuid,size=16m,mode=1777",
            "--mount", "type=bind,src=" + str(out) + ",dst=/inputs,ro=true",
            "--env", "LC_ALL=C", "--entrypoint=" + entry, IMAGE,
        ] + args
        try:
            result = subprocess.run(
                command, input=stdin, capture_output=True, timeout=timeout,
                env=env, cwd=ROOT,
            )
            observed = result.returncode
            stdout, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired as error:
            observed = "timeout"
            stdout, stderr = error.stdout or b"", error.stderr or b""
        finally:
            cleanup = subprocess.run(
                [PODMAN, "rm", "--force", "--ignore", container],
                capture_output=True, timeout=15, env=env, cwd=ROOT,
            )
        (out / (name + ".stdout")).write_bytes(stdout)
        (out / (name + ".stderr")).write_bytes(stderr)
        passed = matches(observed, status, cleanup.returncode, stdout,
                         output, stderr, diagnostic)
        row = {
            "case": name, "argv": command, "expected_status": status,
            "observed_status": observed, "expected_stdout_hex":
            None if output is None else output.hex(),
            "required_diagnostic": diagnostic.decode() if diagnostic else None,
            "stdin_sha256": hashlib.sha256(stdin).hexdigest(),
            "cleanup_status": cleanup.returncode, "pass": passed,
        }
        results.append(row)
        (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        if not passed:
            print("FAILED: " + name, flush=True)
        return stdout

    def case(name, args, status=0, output=b"", **kwargs):
        return run(name, ["/inputs/toybox"] + args, status, output, **kwargs)

    listing = case("inventory", [], output=None)
    expected = {b"[", b"cat", b"false", b"printf", b"test", b"true", b"wc"}
    if set(listing.split()) != expected:
        raise RuntimeError("unexpected dispatch inventory: " + repr(listing))
    case("disabled-sh", ["sh"], 127, diagnostic=b"Unknown command")
    case("true", ["true"])
    case("false", ["false"], 1)
    case("test-equal", ["test", "7", "-eq", "7"])
    case("test-false", ["test", "7", "-eq", "8"], 1)
    case("test-invalid", ["test", "7", "-eq", "bad"], 2,
         diagnostic=b"bad")
    case("bracket", ["[", "x", "=", "x", "]"])
    case("bracket-missing", ["[", "x"], 2, diagnostic=b"]")
    case("printf", ["printf", "%s:%d\\n", "a b", "7"], output=b"a b:7\n")
    case("printf-nul", ["printf", "a\\0b"], output=b"a\x00b")
    case("printf-invalid", ["printf", "%"], 1, diagnostic=b"bad %")
    binary = bytes(range(256)) * 33
    case("cat-binary", ["cat"], output=binary, stdin=binary)
    case("cat-empty", ["cat"])
    case("cat-missing", ["cat", "/inputs/missing"], 1,
         diagnostic=b"No such file")
    case("wc-bytes", ["wc", "-c"], output=b"8448\n", stdin=binary)
    case("wc-lines", ["wc", "-l"], output=b"2\n", stdin=b"a\nb\nc")
    case("wc-empty", ["wc", "-c"], output=b"0\n")
    case("wc-missing", ["wc", "/inputs/missing"], 1,
         diagnostic=b"No such file")
    for applet in ("cat", "printf", "wc"):
        tail = " x" if applet == "printf" else ""
        script = ("exec /usr/bin/qemu-x86_64 /inputs/toybox "
                  + applet + tail + " > /dev/full")
        run(applet + "-full", ["-c", script], 1, b"",
            diagnostic=b"No space left", stdin=b"data\n", entry="/bin/sh")
    # Reuse the real output matcher with a deliberately wrong expectation.
    actual = (out / "cat-binary.stdout").read_bytes()
    control = not matches(0, 0, 0, actual, b"not-the-output", b"", None)
    run("hex-helper", ["/inputs/bin/xxd", "-p"], 0,
        (bytes(range(30)).hex() + "\n1e1f\n").encode(),
        stdin=bytes(range(32)), entry="/usr/local/bin/python3")
    run("hex-helper-reject", ["/inputs/bin/xxd", "--unknown"], 64,
        b"", entry="/usr/local/bin/python3")
    upstream_counts = {}
    for applet in ("cat", "wc", "printf", "test"):
        log = run("upstream-" + applet, ["/inputs/upstream.sh", applet], 0,
            entry="/bin/bash", timeout=180)
        counts = {kind: sum(line.startswith(kind.encode() + b":")
                            for line in log.splitlines())
                  for kind in ("PASS", "FAIL", "SKIP")}
        upstream_counts[applet] = counts
        if counts["PASS"] == 0 or counts["FAIL"] or counts["SKIP"]:
            results[-1]["pass"] = False
    summary = {
        "scope": "Linux QEMU, not native Aether or full POSIX",
        "image": IMAGE, "candidate_sha256": evidence["elf_sha256"],
        "runner_sha256": sha(Path(__file__)), "output": str(out),
        "results": results, "upstream_counts": upstream_counts,
        "test_inputs": {str(p.relative_to(out)): sha(p)
                        for p in out.rglob("*") if p.is_file()
                        and (p.is_relative_to(wrappers)
                             or p.is_relative_to(out / "tests")
                             or p in (upstream, out / "runtest.sh"))},
        "wrong-output-control-rejected": control,
        "pass": all(r["pass"] for r in results) and control,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "FAILED", flush=True)
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
