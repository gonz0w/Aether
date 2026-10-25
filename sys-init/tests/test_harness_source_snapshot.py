# SPDX-License-Identifier: BSD-2-Clause
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_harness_runner import all_check as runner


class SnapshotTests(unittest.TestCase):
    def test_current_map_matches_legacy_selection(self):
        root=runner.ROOT
        paths=[p for base in ('scripts','prototypes','tests','docs') for p in (root/base).rglob('*.py')]
        paths += list((root/'docs').glob('*.lock'))+list((root/'docs/vendor').rglob('SHA256SUMS'))
        paths += [root/p for p in ('prototypes/native-supervisor/sample_receipts.rs','tests/native_sample_receipts.rs',
                  'prototypes/native-supervisor/pending_history.rs','tests/native_pending_history.rs',
                  'prototypes/native-supervisor/cut_reservation.rs','tests/native_cut_reservation.rs',
                  'docs/native-coverage.json','docs/static-tools.json','docs/native-boundaries.json',
                  'docs/quality-inventory.json','docs/QUALITY-PROCESS.md','docs/STANDARDS-UPDATE-REVIEW.md','AGENTS.md','CONTRIBUTING.md')]
        expected={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if 'archive' not in p.parts}
        self.assertEqual(runner.source_hashes(),expected)

    def test_stream_limits_and_special_files(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'ROOT',Path(tmp)):
            p=Path(tmp)/'source.py';p.write_bytes(b'x'*130000)
            original=runner.os.read;sizes=[]
            def read(fd,n):sizes.append(n);return original(fd,n)
            with patch.object(runner.os,'read',side_effect=read):
                self.assertEqual(runner.snapshot_digest(p,200000),(hashlib.sha256(p.read_bytes()).hexdigest(),130000))
            self.assertLessEqual(max(sizes),65536)
            with patch.object(runner.os,'open') as opened,self.assertRaises(ValueError):runner.snapshot_digest(p,10)
            opened.assert_not_called()
            with patch.object(runner,'SOURCE_FILE_LIMIT',10),self.assertRaises(ValueError):runner.snapshot_digest(p,200000)
            p.unlink();os.mkfifo(p)
            with patch.object(runner.os,'open') as opened,self.assertRaises(ValueError):runner.snapshot_digest(p,200000)
            opened.assert_not_called()
            p.unlink();p.symlink_to('/dev/null')
            with self.assertRaises(ValueError):runner.snapshot_digest(p,200000)

    def test_changed_file_and_error_close_descriptor(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'ROOT',Path(tmp)):
            p=Path(tmp)/'source.py';original=runner.os.read
            for mode in ('grow','error'):
                p.write_bytes(b'abc');seen=[]
                def read(fd,n):
                    seen.append(fd)
                    if mode=='error':raise OSError('injected')
                    data=original(fd,n)
                    if len(seen)==1:
                        with p.open('ab') as output:output.write(b'x')
                    return data
                with patch.object(runner.os,'read',side_effect=read),self.assertRaises((ValueError,OSError)):
                    runner.snapshot_digest(p,100)
                with self.assertRaises(OSError):os.fstat(seen[0])

    def test_traversal_and_snapshot_limits(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'ROOT',Path(tmp)):
            root=Path(tmp)
            for base in ('scripts','prototypes','tests','docs'):(root/base).mkdir()
            (root/'scripts/a.py').write_text('a')
            with patch.object(runner,'SOURCE_ENTRY_LIMIT',0),self.assertRaisesRegex(ValueError,'traversal limit'):runner.snapshot_paths()
            with patch.object(runner,'SOURCE_COUNT_LIMIT',0),self.assertRaisesRegex(ValueError,'count limit'):runner.snapshot_paths()
            (root/'scripts/link').symlink_to(root/'docs',target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'special file'):runner.snapshot_paths()
            (root/'scripts/link').unlink()
            p=root/'scripts/a.py'
            with patch.object(runner,'snapshot_paths',return_value=[p]),patch.object(runner,'SOURCE_TOTAL_LIMIT',0),self.assertRaises(ValueError):runner.source_hashes()
            with patch.object(runner,'snapshot_paths',side_effect=[[p],[]]),self.assertRaisesRegex(ValueError,'membership changed'):runner.source_hashes()

    def test_replacement_before_open_rejects(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'ROOT',Path(tmp)):
            p=Path(tmp)/'source.py';p.write_bytes(b'old')
            replacement=Path(tmp)/'replacement';replacement.write_bytes(b'new')
            original=runner.os.open;seen=[]
            def opened(path,flags):
                replacement.replace(p)
                fd=original(path,flags);seen.append(fd);return fd
            with patch.object(runner.os,'open',side_effect=opened),self.assertRaisesRegex(ValueError,'changed before read'):
                runner.snapshot_digest(p,100)
            with self.assertRaises(OSError):os.fstat(seen[0])
