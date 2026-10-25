#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Verify SDK-08 consumer pins and that native execution stays NOT RUN."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path.cwd()
HERE = ROOT / "experiments/sdk-consumer"
CLOSURE = HERE / "sdk-08-closure.json"
PIN = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
RECEIPT = ROOT / "build/native-c-xhkdw6jv/evidence.json"
NATIVE = ROOT / "experiments/native-c"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_closure(data, root):
    if data.get("schema") != "aether-userland-sdk08-closure-v1":
        raise RuntimeError("unknown schema")
    if data.get("waiver") is not False:
        raise RuntimeError("cannot waive SDK-08")
    if data.get("status") != "not-run":
        raise RuntimeError("native execution must stay not-run without snapshot")
    pin = json.loads((root / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json").read_text())
    receipt_path = root / "build/native-c-xhkdw6jv/evidence.json"
    if sha(receipt_path) != pin["libc_receipt_sha256"]:
        raise RuntimeError("libc receipt identity mismatch")
    if sha(receipt_path) != data["consumer"]["libc_receipt_sha256"]:
        raise RuntimeError("closure receipt mismatch")
    receipt = json.loads(receipt_path.read_text())
    consumer = data["consumer"]
    if consumer["probe_sha256"] != receipt["probe_sha256"]:
        raise RuntimeError("probe pin mismatch")
    if sha(root / consumer["probe"]) != consumer["probe_sha256"]:
        raise RuntimeError("live io_probe drift")
    if sha(NATIVE / "native_io.c") != consumer["io_adapter_sha256"]:
        raise RuntimeError("live native_io drift")
    for name, digest in consumer["memory_sources"].items():
        if sha(NATIVE / name) != digest:
            raise RuntimeError("live " + name + " drift")
    elf = root / consumer["startup_elf_path"]
    if not elf.is_file():
        raise RuntimeError("startup ELF missing")
    if sha(elf) != consumer["startup_elf_sha256"]:
        raise RuntimeError("startup ELF hash mismatch")
    producer = data["producer"]
    if producer.get("selected") or producer.get("live_tree_selected"):
        raise RuntimeError("producer snapshot was not selected")
    if producer.get("historical_snapshot_present"):
        raise RuntimeError("historical snapshot is not present")
    live = Path(producer["live_native_c_md"])
    if sha(live) != producer["live_native_c_md_sha256"]:
        raise RuntimeError("live contract hash stale")
    if producer["live_native_c_md_sha256"] == producer["historical_kernel_contract_sha256"]:
        raise RuntimeError("live contract must not equal historical pin")
    for case in data["intended_cases"]:
        if case.get("status") != "not-run":
            raise RuntimeError(case.get("id", "?") + " must stay not-run")


def mutate_and_reject(data, root, label, mutator):
    clone = copy.deepcopy(data)
    mutator(clone)
    try:
        check_closure(clone, root)
    except RuntimeError:
        return
    raise RuntimeError(label + " was accepted")


def main():
    if sys.argv[1:] == ["--help"]:
        print(__doc__)
        print("Usage: python3 -B experiments/sdk-consumer/"
              "check-sdk08-closure.py [--help|--version]")
        return 0
    if sys.argv[1:] == ["--version"]:
        print("aether-sdk08-closure 0.1.0")
        return 0
    if sys.argv[1:]:
        print("[ERROR] Unexpected arguments; use --help.", file=sys.stderr)
        return 64
    work = Path(tempfile.mkdtemp(prefix="sdk08-closure-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    report = {"status": "incomplete", "scope": "SDK-08 selection; native NOT RUN",
              "python": sys.version,
              "sources": {str(p): sha(p) for p in (
                  CLOSURE, HERE / "check-sdk08-closure.py", PIN, RECEIPT)}}
    summary = work / "summary.json"

    def save():
        summary.write_text(json.dumps(report, indent=2) + "\n")

    save()
    try:
        data = json.loads(CLOSURE.read_text())
        check_closure(data, ROOT)

        def mark_run(clone):
            clone["status"] = "pass"
            clone["intended_cases"][0]["status"] = "pass"

        def wrong_elf(clone):
            clone["consumer"]["startup_elf_sha256"] = "0" * 64

        def equate_live(clone):
            clone["producer"]["live_native_c_md_sha256"] = clone["producer"][
                "historical_kernel_contract_sha256"]

        mutate_and_reject(data, ROOT, "native-pass", mark_run)
        mutate_and_reject(data, ROOT, "wrong-elf", wrong_elf)
        mutate_and_reject(data, ROOT, "equate-live", equate_live)
        report["native"] = "NOT RUN"
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        save()
        return 1
    save()
    print("[PASS] SDK-08 consumer pins verified; producer snapshot absent; "
          "native NOT RUN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
