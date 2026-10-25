# SPDX-License-Identifier: BSD-2-Clause
import hashlib
import struct
import unittest
import test_harness_native_audit as fixtures


audit = fixtures.audit


class IOEnvelopeTests(unittest.TestCase):
    def test_layout_and_correspondence(self):
        image = b'inert-image'; supervisor = b'inert-supervisor'; entropy = bytes(range(32))
        raw = struct.pack('<8sII',b'AENFD001',len(image),len(supervisor))+entropy+image+supervisor
        digest = hashlib.sha256(b'AENATC01'+entropy+image).hexdigest()
        audit.check_io_envelope(raw,digest,supervisor)
        for changed, expected in [(raw[:48]+b'X'+raw[49:],'native envelope'),
                                  (raw[:-1]+b'X','embedded supervisor')]:
            with self.subTest(expected=expected), self.assertRaisesRegex(ValueError,expected):
                audit.check_io_envelope(changed,digest,supervisor)
        for changed in (raw[:47],raw[:-1],raw+b'x',b'BADMAGIC'+raw[8:]):
            with self.assertRaises(ValueError): audit.check_io_envelope(changed,digest,supervisor)
        for a,b in ((0,16),(11,0),(1048577,16),(11,4097)):
            with self.subTest(a=a,b=b), self.assertRaises(ValueError):
                audit.check_io_envelope(struct.pack('<8sII',b'AENFD001',a,b)+raw[16:],digest,supervisor)

    def test_maximum_sizes(self):
        image=bytes(1048576);supervisor=bytes(4096);entropy=bytes(32)
        raw=struct.pack('<8sII',b'AENFD001',len(image),len(supervisor))+entropy+image+supervisor
        audit.check_io_envelope(raw,hashlib.sha256(b'AENATC01'+entropy+image).hexdigest(),supervisor)
