#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Compare exact pinned package-script observations; Python 3.12+."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "build")
    parser.add_argument("--qemu", action="store_true")
    args = parser.parse_args()
    build = args.build.resolve()
    evidence = json.loads((build / "evidence.json").read_text())
    locks = json.loads((HERE / "consumer.lock.json").read_text())
    for name, digest in locks.items():
        if sha(HERE / "pkg-mgr" / name) != digest:
            raise RuntimeError("consumer source changed: " + name)
    for entry in evidence["binaries"].values():
        if sha(Path(entry["path"])) != entry["sha256"]:
            raise RuntimeError("provider changed")
    out = Path(tempfile.mkdtemp(prefix="awk-cases-", dir=args.output_root))
    print(out, flush=True)
    old = "package\tp\t1\nfile\tA\t1\tchanged\t0644\n"
    old += "file\tA\t1\tremoved\t0644\ndependency\tolddep\n"
    new = "package\tp\t2\nfile\tB\t2\tchanged\t0600\n"
    new += "file\tC\t1\tadded\t0644\ndependency\tnewdep\n"
    (out / "old").write_text(old)
    (out / "new").write_text(new)
    states = {
        "unchanged": ("A", "A", "A"),
        "package": ("A", "B", "A"),
        "local": ("A", "A", "C"),
        "match": ("A", "B", "B"),
        "conflict": ("A", "B", "C"),
        "unknown": ("A", "B", "unsupported"),
    }
    for index, name in enumerate(("before", "after", "observed")):
        lines = []
        for path, values in states.items():
            value = values[index]
            if index < 2:
                lines.append(f"file\t{value}\t1\t{path}\t0644\n")
            else:
                lines.append(f"observed\t{path}\t{value}\t0644\n")
        (out / name).write_text("".join(lines))
    cases = [
        ("names", "state-schema.awk", ["mode=names"], [],
         b"# comment\nalpha\npkg-2\n", 0, b"alpha\npkg-2\n", b"", False),
        ("duplicate", "state-schema.awk", ["mode=names"], [],
         b"alpha\nalpha\n", 1, b"alpha\n",
         b"state-record-invalid: invalid or duplicate package name\n", False),
        ("invalid-name", "state-schema.awk", ["mode=names"], [],
         b"../escape\n", 1, b"",
         b"state-record-invalid: invalid or duplicate package name\n", False),
        ("incomplete-build", "state-schema.awk", ["mode=build"], [],
         b"", 1, b"", b"state-record-invalid: incomplete build evidence\n",
         False),
        ("render-controls", "cli-render.awk", ["diagnostic=yes"], [],
         b"a\x1b[31m\tb\n", 0, b"  a\\x1b[31m\\x09b\n", b"", False),
        ("render-ascii", "cli-render.awk", ["plain=yes", "diagnostic=yes"],
         [], b"hello\n", 0, b"  hello\n", b"", False),
        ("render-utf8-bytes", "cli-render.awk",
         ["plain=yes", "diagnostic=yes"], [], b"\xc3\xa9\n", 0,
         b"  \\xc3\\xa9\n", b"", False),
        ("render-invalid-byte", "cli-render.awk",
         ["plain=yes", "diagnostic=yes"], [], b"\xff\n", 0,
         b"  \\xff\n", b"", False),
        ("render-list", "cli-render.awk", ["command=list"], [],
         b"p\t1\texplicit\n", 0,
         b"Package  Version  Selection\np  1  explicit\n", b"", False),
        ("update-diff", "update-diff.awk", [], ["old", "new"], b"", 0,
         b"version\t1\t2\ncontent-change\tchanged\nmode-change\tchanged\n"
         b"add\tadded\nremove\tremoved\ndependency-remove\tolddep\n"
         b"dependency-add\tnewdep\n", b"", True),
        ("three-way", "update-three-way.awk", [],
         ["before", "after", "observed"], b"", 0,
         b"three-way\tpackage-only\tpackage\nthree-way\tlocal-only\tlocal\n"
         b"three-way\tmatching-change\tmatch\nthree-way\tconflict\tconflict\n"
         b"three-way\tuninspectable\tunknown\n", b"", False),
    ]
    results = []
    for provider, entry in evidence["binaries"].items():
        for spec in cases:
            (name, script, variables, files, stdin, status,
             expected, err, sort) = spec
            command = (["/usr/bin/qemu-x86_64"] if args.qemu else [])
            command += [entry["path"]]
            for variable in variables:
                command += ["-v", variable]
            command += ["-f", str(HERE / "pkg-mgr" / script)]
            command += [str(out / file) for file in files]
            result = subprocess.run(
                command, input=stdin, capture_output=True, timeout=15,
                cwd=out, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
            )
            actual = result.stdout
            if sort:
                same = (sorted(actual.splitlines())
                        == sorted(expected.splitlines()))
            else:
                same = actual == expected
            passed = (same and result.stderr == err
                      and result.returncode == status)
            row = {"provider": provider, "case": name, "pass": passed,
                   "argv": command, "stdin_hex": stdin.hex(),
                   "expected_exit": status, "actual_exit": result.returncode,
                   "expected_stdout_hex": expected.hex(),
                   "actual_stdout_hex": result.stdout.hex(),
                   "expected_stderr_hex": err.hex(),
                   "actual_stderr_hex": result.stderr.hex(),
                   "unordered_output": sort}
            results.append(row)
            (out / "results.json").write_text(json.dumps(results, indent=2))
            label = " PASS" if passed else " DIFFERENT"
            print(provider + " " + name + label)
    summary = {"scope": ("Linux QEMU consumer compatibility" if args.qemu
                          else "host consumer compatibility") + "; no native claim",
               "python": sys.version, "build": str(build),
               "build_receipt_sha256": sha(build / "evidence.json"),
               "consumer_pins": locks, "runner_sha256": sha(Path(__file__)),
               "results": results, "expected_cases": len(cases) * len(evidence["binaries"])}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return 0 if results and all(row["pass"] for row in results) else 1


if __name__ == "__main__":
    sys.exit(main())
