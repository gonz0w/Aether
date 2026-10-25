#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Deterministic rejection controls for the command handoff reader."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("preflight", Path(__file__).with_name("native-command-preflight.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Controls(unittest.TestCase):
    def setUp(self):
        self.receipt = {"schema": "aether-userland.native-command-userland.v1",
                        "status": "pass", "artifacts": {name: "0" * 64 for name in MODULE.ARTIFACT_NAMES},
                        "cases": [{"case": name, "result": "pass", "negative": name in MODULE.NEGATIVE_CASES}
                                  for name in sorted(MODULE.CASES)]}
        self.receipt.update({flag: True for flag in MODULE.FLAGS})

    def test_schema_and_case_controls(self):
        self.assertEqual(len(MODULE.validate(self.receipt)), 53)
        mutations = [lambda d: d.update(schema="aether-userland.native-fileio-libc.v1"),
                     lambda d: d.update(status="fail"),
                     lambda d: d["cases"].pop(),
                     lambda d: d["cases"].append(copy.deepcopy(d["cases"][0])),
                     lambda d: d["cases"][0].update(case=d["cases"][1]["case"]),
                     lambda d: d["cases"][0].update(result="not-run"),
                     lambda d: d["cases"][0].update(negative=1),
                     lambda d: d.update(artifacts={})]
        for flag in MODULE.FLAGS:
            mutations.append(lambda d, flag=flag: d.update({flag: False}))
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                value = copy.deepcopy(self.receipt)
                mutate(value)
                with self.assertRaises(ValueError):
                    MODULE.validate(value)

    def test_paths_and_digest(self):
        with tempfile.TemporaryDirectory(prefix="pkg-command-preflight-") as tmp:
            root = Path(tmp).resolve()
            payload = root / "payload"
            payload.write_bytes(b"original")
            pin = hashlib.sha256(b"original").hexdigest()
            self.assertEqual(MODULE.checked(root, "payload", pin), payload)
            for name in ("../payload", str(payload), "./payload", ""):
                with self.subTest(path=name), self.assertRaises(ValueError):
                    MODULE.checked(root, name, pin)
            (root / "alias").symlink_to(payload)
            with self.assertRaises(ValueError):
                MODULE.checked(root, "alias", pin)
            payload.write_bytes(b"modified")
            with self.assertRaises(ValueError):
                MODULE.checked(root, "payload", pin)
            with self.assertRaises(ValueError):
                MODULE.checked(root, "payload", "bad-pin")

    def test_duplicate_json(self):
        with self.assertRaises(ValueError):
            MODULE.unique_object([("status", "fail"), ("status", "pass")])


if __name__ == "__main__":
    unittest.main()
