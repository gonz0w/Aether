# SPDX-License-Identifier: BSD-2-Clause
"""Independent AF07 executable intake and actual kernel ELF failure controls."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fs_metadata_launch as launch
import test_fs_launch_intake as previous

from fs_af07_inputs import selection
SELECTED=selection()['engine']
CANDIDATE=ROOT/SELECTED['directory']
SEAL=SELECTED['seal']
ELF='9039e7b1d9a488076e3f8329b3666f39d85385f294d89954dd03df7c2df1753a'


class MetadataLaunchIntake(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='aether-af07-link-intake-')
        self.addCleanup(temporary.cleanup);self.out=Path(temporary.name)

    def test_exact_candidate_and_old_profile_drift_extra_missing_and_symlink_reject(self):
        selected=launch.intake(CANDIDATE,SEAL)
        self.assertEqual(selected['elf_sha256'],ELF)
        self.assertEqual(selected['members'],30)
        self.assertFalse(selected['native_acceptance']);self.assertFalse(selected['executed'])
        with self.assertRaises(ValueError):launch.intake(launch.CURRENT,launch.metadata.digest(launch.CURRENT/'SHA256SUMS'))
        root=self.out/'candidate';shutil.copytree(CANDIDATE,root)
        binary=root/'filesystem.elf';original=binary.read_bytes()
        for name,change in (('drift',lambda:binary.write_bytes(b'bad')),
                            ('missing',lambda:binary.unlink()),
                            ('symlink',lambda:binary.symlink_to(CANDIDATE/'filesystem.elf'))):
            change()
            with self.subTest(name=name),self.assertRaises((ValueError,OSError)):launch.intake(root,SEAL)
            if binary.is_symlink() or binary.exists():binary.unlink()
            if name!='missing':binary.write_bytes(original)
        binary.unlink();binary.write_bytes(original)
        (root/'extra').write_text('extra')
        with self.assertRaises(ValueError):launch.intake(root,SEAL)
        with self.assertRaises(ValueError):launch.intake(CANDIDATE,'0'*64)

    def test_resealed_false_build_origins_consumed_inputs_and_frames_reject(self):
        root=self.out/'candidate';shutil.copytree(CANDIDATE,root)
        original=json.loads((root/'build.json').read_text())
        for key,value in (('executed',True),('status','incomplete'),('schema','aether-fs-launch-build-v1'),
                          ('elf_bytes',1),('origins',{}),('structural_loader',''),('commands',[]),
                          ('inputs',{}),('local_frames',{}),('owner_manifest_sha256','0'*64)):
            altered=copy.deepcopy(original);altered[key]=value
            (root/'build.json').write_text(json.dumps(altered))
            self.reseal(root)
            with self.subTest(key=key),self.assertRaises(ValueError):launch.intake(root,launch.metadata.digest(root/'SHA256SUMS'))
        altered=copy.deepcopy(original)
        altered['origins']['main']='/owned/foreign-owner.o'
        (root/'build.json').write_text(json.dumps(altered));self.reseal(root)
        with self.assertRaises(ValueError):launch.intake(root,launch.metadata.digest(root/'SHA256SUMS'))
        for bad in ({**original['local_frames'],'extra.su':'wrong'},
                    {**original['local_frames'],'filesystem-engine.su':'wrong\t9000\tstatic\n'},
                    {**original['local_frames'],'filesystem-engine.su':'wrong\t8\tdynamic\n'}):
            with self.assertRaises(ValueError):launch.check_frames(bad)

    def reseal(self,root):
        members=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
        (root/'SHA256SUMS').write_text(''.join(launch.metadata.digest(p)+'  '+str(p.relative_to(root))+'\n' for p in members))

    def test_actual_kernel_parser_rejects_missing_tls_writable_code_and_oversized_tls(self):
        # Reuse the unchanged real parser mutation workload with the new ELF.
        with patch.object(previous,'CURRENT',CANDIDATE):
            previous.LaunchIntake.test_actual_kernel_parser_requires_tls_wx_and_existing_geometry_limits(self)
