# SPDX-License-Identifier: BSD-2-Clause
"""SDK receipt validation rejects wrong pins/profiles/bytes before target work."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('io_stop_harness', Path(__file__).resolve().parent/'native-io-stop.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class NativeIOInputs(unittest.TestCase):
    def test_receipt_and_payload_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            sdk = Path(directory)
            raw = b'AENATC01' + bytes(32) + b'inert-format-fixture-not-a-bootable-ELF'
            receipt = dict(probe_variant='io', envelope_sha256=hashlib.sha256(raw).hexdigest(),
                           artifacts=[dict(name='startup', sha256=hashlib.sha256(raw[40:]).hexdigest())])
            (sdk/'native-c.bin').write_bytes(raw)
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            pin = harness.sha(sdk/'evidence.json')
            self.assertEqual(harness.validate_sdk(sdk, pin), raw)
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                harness.validate_sdk(sdk, '0'*64)
            (sdk/'native-c.bin').write_bytes(raw+b'changed')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                harness.validate_sdk(sdk, pin)
            (sdk/'native-c.bin').write_bytes(raw)
            receipt['probe_variant'] = 'supervised'
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                harness.validate_sdk(sdk, harness.sha(sdk/'evidence.json'))

    def test_retained_profile_requires_explicit_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            sdk = Path(directory)
            raw = b'AENATC01' + bytes(32) + b'inert-retained-format-fixture'
            receipt = dict(probe_variant='io-retained', envelope_sha256=hashlib.sha256(raw).hexdigest(),
                           artifacts=[dict(name='startup', sha256=hashlib.sha256(raw[40:]).hexdigest())])
            (sdk/'native-c.bin').write_bytes(raw)
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            pin = harness.sha(sdk/'evidence.json')
            with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                harness.validate_sdk(sdk, pin)
            self.assertEqual(harness.validate_sdk(sdk, pin, retained=True), raw)
            receipt['probe_variant'] = 'io'
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                harness.validate_sdk(sdk, harness.sha(sdk/'evidence.json'), retained=True)

    def test_readiness_profile_is_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            sdk = Path(directory)
            raw = b'AENATC01' + bytes(32) + b'inert-readiness-format-fixture'
            receipt = dict(probe_variant='io-readiness', envelope_sha256=hashlib.sha256(raw).hexdigest(),
                           artifacts=[dict(name='startup', sha256=hashlib.sha256(raw[40:]).hexdigest())])
            (sdk/'native-c.bin').write_bytes(raw)
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            pin = harness.sha(sdk/'evidence.json')
            for options in ({}, dict(retained=True)):
                with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                    harness.validate_sdk(sdk, pin, **options)
            self.assertEqual(harness.validate_sdk(sdk, pin, readiness=True), raw)
            receipt['probe_variant'] = 'io-retained'
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                harness.validate_sdk(sdk, harness.sha(sdk/'evidence.json'), readiness=True)

    def test_authority_profile_is_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            sdk = Path(directory)
            raw = b'AENATC01' + bytes(32) + b'inert-authority-format-fixture'
            receipt = dict(probe_variant='io-authority', envelope_sha256=hashlib.sha256(raw).hexdigest(),
                           artifacts=[dict(name='startup', sha256=hashlib.sha256(raw[40:]).hexdigest())])
            (sdk/'native-c.bin').write_bytes(raw)
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            pin = harness.sha(sdk/'evidence.json')
            for options in ({}, dict(retained=True), dict(readiness=True)):
                with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                    harness.validate_sdk(sdk, pin, **options)
            self.assertEqual(harness.validate_sdk(sdk, pin, authority=True), raw)
            receipt['probe_variant'] = 'io-readiness'
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                harness.validate_sdk(sdk, harness.sha(sdk/'evidence.json'), authority=True)

    def test_peer_profile_is_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            sdk = Path(directory)
            raw = b'AENATC01' + bytes(32) + b'inert-peer-format-fixture'
            receipt = dict(probe_variant='io-peer', envelope_sha256=hashlib.sha256(raw).hexdigest(),
                           artifacts=[dict(name='startup', sha256=hashlib.sha256(raw[40:]).hexdigest())])
            (sdk/'native-c.bin').write_bytes(raw)
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            pin = harness.sha(sdk/'evidence.json')
            for options in ({}, dict(retained=True), dict(readiness=True), dict(authority=True)):
                with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                    harness.validate_sdk(sdk, pin, **options)
            self.assertEqual(harness.validate_sdk(sdk, pin, peer=True), raw)
            receipt['probe_variant'] = 'io-authority'
            (sdk/'evidence.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'I/O envelope required'):
                harness.validate_sdk(sdk, harness.sha(sdk/'evidence.json'), peer=True)


if __name__ == '__main__': unittest.main()


class NativeIOCapture(unittest.TestCase):
    def test_isolated_builder_imports_only_captured_helper(self):
        import os
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            client = Path(directory) / 'sys-init'
            harness.capture_client(client)
            helper = client / 'scripts/bounded_tools.py'
            self.assertEqual(helper.read_bytes(),
                             (harness.ROOT / 'scripts/bounded_tools.py').read_bytes())
            command = [sys.executable, str(client / 'scripts/build-native-supervisor.py'), '--help']
            env = dict(os.environ, PYTHONPATH='', PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run(command, cwd=directory, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--variant', result.stdout)
            helper.unlink()
            result = subprocess.run(command, cwd=directory, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('bounded_tools', result.stderr)
            self.assertFalse(result.stdout)
