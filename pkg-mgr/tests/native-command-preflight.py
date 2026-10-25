#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Read-only command-runner handoff preflight. Does not stage or boot images."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

CASES = frozenset(('positive', 'empty-input', 'rejected-launch', 'partial-reservation', 'short-write', 'full-output', 'wrong-startup', 'wrong-status', 'skip-write', 'bootstrap-reference', 'bootstrap-descriptor', 'bootstrap-rights', 'bootstrap-early-publication', 'reply-drop-read', 'reply-bad-read', 'reply-drop-close', 'reply-disabled-poison', 'launch-corpus', 'allow-launch-version', 'launch-eof-0', 'launch-eof-1', 'launch-eof-4', 'launch-eof-16', 'launch-eof-31', 'launch-eof-32', 'launch-eof-383', 'pad-launch-eof', 'terminal-normal', 'terminal-fault', 'fault-as-exit', 'startup-simple', 'startup-delimiter', 'startup-wide', 'startup-corrupt', 'mapped-0', 'mapped-1', 'mapped-2', 'mapped-64', 'mapped-125', 'mapped-126', 'mapped-127', 'mapped-134', 'mapped-255', 'mapped-fault', 'mapped-ignore-kind', 'mapped-force-zero', 'mapped-cleanup', 'uncertain-admission-lost', 'uncertain-admission-padding', 'uncertain-collection-lost', 'uncertain-collection-padding', 'uncertain-collection-receipt', 'uncertain-retry'))
FLAGS = ('bootstrap_controls', 'reply_controls', 'launch_controls', 'terminal_controls', 'startup_controls', 'mapped_results', 'mapped_uncertainty')

NEGATIVE_CASES = frozenset(('wrong-startup', 'wrong-status', 'skip-write', 'bootstrap-reference', 'bootstrap-descriptor', 'bootstrap-rights', 'bootstrap-early-publication', 'reply-drop-read', 'reply-bad-read', 'reply-drop-close', 'reply-disabled-poison', 'allow-launch-version', 'launch-eof-0', 'launch-eof-1', 'launch-eof-4', 'launch-eof-16', 'launch-eof-31', 'launch-eof-32', 'launch-eof-383', 'pad-launch-eof', 'fault-as-exit', 'startup-corrupt', 'mapped-ignore-kind', 'mapped-force-zero', 'mapped-cleanup', 'uncertain-admission-lost', 'uncertain-admission-padding', 'uncertain-collection-lost', 'uncertain-collection-padding', 'uncertain-collection-receipt', 'uncertain-retry'))
ARTIFACT_NAMES = frozenset(('worker.elf', 'empty-worker.elf', 'broker.raw', 'rejected-launch.raw', 'partial-reservation.raw', 'short-write.raw', 'full-output.raw', 'wrong-startup.raw', 'wrong-status.raw', 'skip-write.raw', 'allow-launch-version.raw', 'pad-launch-eof.raw', 'fault-as-exit.raw', 'startup-simple.raw', 'startup-delimiter.raw', 'startup-wide.raw', 'startup-corrupt.raw', 'mapped-0.raw', 'mapped-1.raw', 'mapped-2.raw', 'mapped-64.raw', 'mapped-125.raw', 'mapped-126.raw', 'mapped-127.raw', 'mapped-134.raw', 'mapped-255.raw', 'mapped-fault.raw', 'mapped-ignore-kind.raw', 'mapped-force-zero.raw', 'mapped-cleanup.raw', 'uncertain-admission-lost.raw', 'uncertain-admission-padding.raw', 'uncertain-collection-lost.raw', 'uncertain-collection-padding.raw', 'uncertain-collection-receipt.raw', 'uncertain-retry.raw'))

def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    require(stat.S_ISREG(path.lstat().st_mode), "not a regular file: " + str(path))
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def checked(root, relative, expected):
    require(isinstance(relative, str), "path must be text")
    part = Path(relative)
    require(not part.is_absolute() and part.parts and
            all(v not in (".", "..") for v in relative.split("/")), "unsafe artifact path")
    path = root / part
    for ancestor in (path, *path.parents):
        require(not ancestor.is_symlink(), "symlink in artifact path")
    require(isinstance(expected, str) and re.fullmatch("[0-9a-f]{64}", expected), "invalid digest")
    require(digest(path) == expected, "artifact digest mismatch: " + relative)
    return path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def validate(receipt):
    require(receipt.get("schema") == "aether-userland.native-command-userland.v1", "wrong schema")
    require(receipt.get("status") == "pass", "receipt did not pass")
    require(all(receipt.get(flag) is True for flag in FLAGS), "wrong feature flags")
    cases = receipt.get("cases")
    require(isinstance(cases, list) and len(cases) == len(CASES), "incomplete case set")
    require(all(isinstance(c, dict) for c in cases), "invalid case")
    names = [c.get("case") for c in cases]
    require(all(isinstance(n, str) for n in names) and set(names) == CASES, "wrong case set")
    require(all(c.get("result") == "pass" and type(c.get("negative")) is bool for c in cases), "unaccepted case")
    require(all(c["negative"] is (c["case"] in NEGATIVE_CASES) for c in cases), "wrong case polarity")
    require(isinstance(receipt.get("artifacts"), dict) and set(receipt["artifacts"]) == ARTIFACT_NAMES, "wrong artifact set")
    return cases


def preflight(evidence, pin, build, clients):
    # Caller selects all roots. Recorded commands and absolute artifact paths are
    # never executed or used to select a filesystem root.
    checked(evidence.parent, evidence.name, pin)
    receipt = read_json(evidence)
    cases = validate(receipt)
    inspected = {}
    def check(root, name, expected):
        path = checked(root, name, expected)
        inspected[str(path)] = expected
        return path
    check(evidence.parent, evidence.name, pin)
    for case in cases:
        name = case["case"]
        check(build, name + "/aether.iso", case["iso_sha256"])
        check(build, name + "/native-serial.log", case["serial_sha256"])
        check(build, name + "/native-c.bin", case["envelope_sha256"])
    for name, expected in receipt["artifacts"].items():
        check(build, name, expected)
    requester_pin = receipt["requester_build"]["receipt_sha256"]
    require(all(c["client_build_receipt_sha256"] == requester_pin for c in cases), "mixed client receipt")
    client_receipt = read_json(check(clients, "evidence.json", requester_pin))
    require(client_receipt.get("schema") == "aether-userland.command-clients-build.v1" and
            client_receipt.get("status") == "pass", "wrong client receipt")
    artifacts = client_receipt.get("artifacts")
    require(isinstance(artifacts, dict) and artifacts, "missing client artifacts")
    names = set()
    for artifact in artifacts.values():
        name = Path(artifact["path"]).name
        require(name not in names, "duplicate client basename")
        names.add(name)
        path = check(clients, name, artifact["sha256"])
        require(path.stat().st_size == artifact["bytes"], "client size mismatch")
    # Detect persistent input drift during inspection; not hostile race isolation.
    for name, expected in inspected.items():
        require(digest(Path(name)) == expected, "input changed during preflight")
    return {"result": "pass", "scope": "artifact preflight only; no staging, boot or runtime acceptance",
            "receipt_sha256": pin, "cases": len(cases), "client_artifacts": len(artifacts),
            "inputs": inspected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--evidence-sha256", required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--clients", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = preflight(args.evidence.absolute(), args.evidence_sha256,
                           args.build.absolute(), args.clients.absolute())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("command-preflight-error: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
