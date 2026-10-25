# SPDX-License-Identifier: BSD-2-Clause
"""Inert receipt checks for the optional provider-return worker."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('init_consumer',ROOT/'tests/native-init.py')
consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)

class ServiceWorkerInputs(unittest.TestCase):
    def fixture(self,root):
        (root/'inputs').mkdir()
        (root/'inputs/source.c').write_bytes(b'inert source')
        (root/'service-worker.elf').write_bytes(b'inert ELF identity only')
        report=dict(schema='sys-init-native-service-worker-v1',result='pass',
                    inputs_unchanged=True,
                    inputs={'inputs/source.c':consumer.sha(root/'inputs/source.c')},
                    worker_sha256=consumer.sha(root/'service-worker.elf'))
        (root/'evidence.json').write_text(json.dumps(report))
        return consumer.sha(root/'evidence.json')

    def test_complete_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pin=self.fixture(root)
            self.assertEqual(consumer.validate_service_worker(root,pin)['result'],'pass')

    def test_pin_worker_input_and_escape_reject(self):
        for change in ('pin','worker','input','escape'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);pin=self.fixture(root)
                if change=='pin':pin='0'*64
                if change=='worker':(root/'service-worker.elf').write_bytes(b'changed')
                if change=='input':(root/'inputs/source.c').write_bytes(b'changed')
                if change=='escape':
                    report=json.loads((root/'evidence.json').read_text())
                    report['inputs']={'../outside':'0'*64}
                    (root/'evidence.json').write_text(json.dumps(report));pin=consumer.sha(root/'evidence.json')
                with self.assertRaises(ValueError):consumer.validate_service_worker(root,pin)
