#!/usr/bin/env python3
"""Run pinned reference ELFs under QEMU user emulation in a local tool image."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = "8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4"
PODMAN = "/opt/homebrew/bin/podman"
build = json.loads((HERE / "evidence.json").read_text())
inputs = Path(build["output"])
for a in build["artifacts"]:
    assert hashlib.sha256((inputs / (a["name"] + ".elf")).read_bytes()).hexdigest() == a["sha256"]
out = Path(tempfile.mkdtemp(prefix="linux-reference-", dir=ROOT / "build"))
base = [PODMAN, "run", "--rm", "--pull=never", "--network=none", "--read-only",
        "--cap-drop=all", "--security-opt=no-new-privileges", "--user=65534:65534",
        "--mount", "type=bind,src=" + str(inputs) + ",dst=/inputs,ro=true",
        "--entrypoint=/bin/sh", IMAGE]
metadata = subprocess.run(base + ["-c", "uname -a; qemu-x86_64 --version; dpkg-query -W qemu-user strace; sha256sum /usr/bin/qemu-x86_64"],
                          capture_output=True, text=True, check=True)
(out / "environment.txt").write_text(metadata.stdout)
results = []
for program in ("startup", "allocator"):
    for case in ("pass", "bad-argument", "missing-environment", "closed-output"):
        qemu = ["qemu-x86_64", "-strace"]
        qemu += ["-U", "AETHER_PROBE"] if case == "missing-environment" else ["-E", "AETHER_PROBE=reference"]
        qemu += ["/inputs/" + program + ".elf", "bad" if case == "bad-argument" else "check"]
        # $@ preserves argv; only the closed-output case needs shell redirection.
        shell = 'exec "$@"' if case != "closed-output" else 'exec 1>&-; exec "$@"'
        command = base + ["-c", shell, "reference"] + qemu
        r = subprocess.run(command, capture_output=True, timeout=30)
        expected = 0 if case == "pass" else 14 if case == "closed-output" else 10
        expected_output = b"AETHER MUSL REFERENCE PASS\n" if case == "pass" else b""
        label = program + "-" + case
        (out / (label + ".stdout")).write_bytes(r.stdout)
        (out / (label + ".trace")).write_bytes(r.stderr)
        if r.returncode != expected or r.stdout != expected_output:
            raise RuntimeError("Unexpected result: " + label + "; inspect " + str(out))
        calls = sorted(set(re.findall(r"^\d+ (\w+)\(", r.stderr.decode(), re.M)))
        results.append({"case": label, "exit_code": r.returncode, "expected_exit": expected,
                        "command": command, "observed_syscall_names": calls,
                        "trace_sha256": hashlib.sha256(r.stderr).hexdigest()})
evidence = {"scope": "Linux x86-64 user ABI under QEMU on arm64 Linux; not native x86-64 or Aether",
            "image_id": IMAGE, "output": str(out), "build_evidence_sha256": hashlib.sha256((HERE / "evidence.json").read_bytes()).hexdigest(),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "environment": metadata.stdout, "results": results}
(out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
print("PASS: 8 Linux-emulated reference cases; evidence " + str(out))
