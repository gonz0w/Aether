#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check extended family/stage inventory and ASan compensation; Python 3.10+."""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATRIX = HERE / "extended-matrix.json"
EXTENDED = HERE / "EXTENDED.md"
PLAN = ROOT / "docs/evidence/extended-matrix-2026-09-07/PLAN.md"
PX_RE = re.compile(r"^\| (PX[A-Z]*-[0-9]+[a-z]?) \|", re.M)
FAMILIES = {
    "unit/property", "contract/integration", "system/workflow", "static/build",
    "memory/undefined behavior", "fuzz", "security", "fault/recovery",
    "concurrency", "stress/soak", "compatibility", "performance", "hardware",
    "usability/accessibility", "documentation/package",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_matrix(path):
    data = json.loads(Path(path).read_text())
    if data.get("schema") != "aether-userland-extended-matrix-v1":
        raise RuntimeError("unknown matrix schema")
    if data.get("waiver") is not False:
        raise RuntimeError("matrix must not set a waiver")
    return data


def check_matrix(data, root):
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RuntimeError("missing cases")
    ids = [c.get("id") for c in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate case id")
    table = {i for i in PX_RE.findall(EXTENDED.read_text())
             if not i.startswith("PXM")}
    px = {i for i in ids if i.startswith("PX")}
    if px != table:
        raise RuntimeError("PX ids differ from EXTENDED.md: " +
                           str(sorted(px.symmetric_difference(table))))
    families = set()
    for case in cases:
        for key in ("id", "family", "layer", "stage", "status", "oracle"):
            if not case.get(key):
                raise RuntimeError(case.get("id", "?") + " missing " + key)
        if case["family"] not in FAMILIES:
            raise RuntimeError(case["id"] + " unknown family")
        if case["status"] not in ("pass", "blocked", "excluded"):
            raise RuntimeError(case["id"] + " bad status")
        if case["id"] in ("PXE-04", "PXA-04") and case["status"] != "blocked":
            raise RuntimeError(case["id"] + " ASan heap case cannot pass")
        families.add(case["family"])
        evidence = case.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise RuntimeError(case["id"] + " missing evidence")
        for item in evidence:
            path = root / item["path"]
            if not path.is_file():
                raise RuntimeError(case["id"] + " missing " + item["path"])
            if sha(path) != item["sha256"]:
                raise RuntimeError(case["id"] + " hash mismatch " + item["path"])
        if case["status"] == "blocked":
            comp = case.get("compensation")
            if not isinstance(comp, dict):
                raise RuntimeError(case["id"] + " missing compensation")
            if comp.get("waiver") is not False:
                raise RuntimeError(case["id"] + " cannot waive")
            if "host heap OOB" not in comp.get("does_not_cover", ""):
                raise RuntimeError(case["id"] + " compensation overclaim")
            for nid in comp.get("ids", []):
                if nid not in ids:
                    raise RuntimeError(case["id"] + " unknown compensation " + nid)
    excluded = {e["family"] for e in data.get("exclusions", [])}
    missing = FAMILIES - families - excluded
    if missing:
        raise RuntimeError("unmapped families: " + str(sorted(missing)))


def mutate_and_reject(data, root, label, mutator):
    clone = copy.deepcopy(data)
    mutator(clone)
    try:
        check_matrix(clone, root)
    except RuntimeError:
        return
    raise RuntimeError(label + " was accepted")


def main():
    if sys.argv[1:] == ["--help"]:
        print(__doc__)
        print("Usage: python3 -B experiments/command-runner/"
              "check-extended-matrix.py [--help|--version]")
        print("No arguments: check inventory hashes and compensation limits.")
        return 0
    if sys.argv[1:] == ["--version"]:
        print("aether-extended-matrix 0.1.0")
        return 0
    if sys.argv[1:]:
        print("[ERROR] Unexpected arguments; use --help.", file=sys.stderr)
        return 64
    work = Path(tempfile.mkdtemp(prefix="extended-matrix-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    report = {"status": "incomplete", "scope": "inventory hashes; no native rerun",
              "python": sys.version, "sources": {
                  str(MATRIX): sha(MATRIX), str(EXTENDED): sha(EXTENDED),
                  str(PLAN): sha(PLAN), str(HERE / "check-extended-matrix.py"):
                  sha(HERE / "check-extended-matrix.py"),
              }}

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    save()
    try:
        data = load_matrix(MATRIX)
        check_matrix(data, ROOT)
        blocked = [c["id"] for c in data["cases"] if c["status"] == "blocked"]

        def mark_pass(clone):
            for case in clone["cases"]:
                if case["id"] == "PXE-04":
                    case["status"] = "pass"
                    case.pop("compensation", None)

        def drop_limit(clone):
            for case in clone["cases"]:
                if case["id"] == "PXE-04":
                    case["compensation"]["does_not_cover"] = "unspecified"

        def missing_file(clone):
            clone["cases"][0]["evidence"][0]["path"] = "docs/missing.md"

        def wrong_hash(clone):
            clone["cases"][0]["evidence"][0]["sha256"] = "0" * 64

        mutate_and_reject(data, ROOT, "pxe04-pass", mark_pass)
        mutate_and_reject(data, ROOT, "overclaim", drop_limit)
        mutate_and_reject(data, ROOT, "missing-file", missing_file)
        mutate_and_reject(data, ROOT, "wrong-hash", wrong_hash)
        report["blocked"] = blocked
        report["cases"] = len(data["cases"])
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        save()
        return 1
    save()
    print("[PASS] Extended family/stage inventory and native ASan compensation "
          "limits; PXE-04 remains blocked without waiver.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
