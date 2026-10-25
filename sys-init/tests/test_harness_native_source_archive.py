# SPDX-License-Identifier: BSD-2-Clause
import gzip
import hashlib
import io
import json
import tarfile
import unittest
import test_harness_native_audit as fixtures


audit = fixtures.audit


def packed(entries):
    output=io.BytesIO()
    with tarfile.open(fileobj=output,mode='w') as archive:
        for name,data,kind in entries:
            info=tarfile.TarInfo(name);info.type=kind
            info.size=len(data) if kind==tarfile.REGTYPE else 0
            archive.addfile(info,io.BytesIO(data) if info.size else None)
    return gzip.compress(output.getvalue())


class SourceArchiveTests(unittest.TestCase):
    def test_all_retained_archives(self):
        count=0
        for entry in json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']:
            if entry['schema']!='sys-init-native-init-v1':continue
            directory=fixtures.ROOT/entry['directory']/'producer'
            summary=json.loads((directory/'summary.json').read_text())
            audit.check_source_archive((directory/'producer-sources.tar.gz').read_bytes(),summary['inputs']);count+=1
        self.assertEqual(count,45)

    def test_membership_types_and_hashes(self):
        expected={'a':hashlib.sha256(b'abc').hexdigest()}
        audit.check_source_archive(packed([('a',b'abc',tarfile.REGTYPE)]),expected)
        for entries in ([], [('a',b'wrong',tarfile.REGTYPE)],
                        [('a',b'abc',tarfile.REGTYPE)]*2,
                        [('a',b'abc',tarfile.REGTYPE),('extra',b'x',tarfile.REGTYPE)],
                        [('../a',b'abc',tarfile.REGTYPE)],
                        [('a',b'',tarfile.SYMTYPE)], [('a',b'',tarfile.LNKTYPE)],
                        [('a',b'',tarfile.DIRTYPE)], [('a',b'',tarfile.FIFOTYPE)]):
            with self.subTest(entries=repr(entries)[:60]),self.assertRaises(ValueError):
                audit.check_source_archive(packed(entries),expected)

    def test_encoding_and_resource_bounds(self):
        for raw in (b'not gzip',gzip.compress(b'not tar'),gzip.compress(bytes(32*1024*1024+1)),
                    packed([('a',bytes(audit.MAX_CATALOG+1),tarfile.REGTYPE)])):
            with self.assertRaises(ValueError):audit.check_source_archive(raw,{'a':'0'*64})
        raw=packed([('a',b'abc',tarfile.REGTYPE)])
        with self.assertRaises(ValueError):audit.check_source_archive(raw[:-5],{'a':'0'*64})
