# SPDX-License-Identifier: BSD-2-Clause
"""Explicit current input selection never admits a guest or edits an old seal."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fs_af07_inputs as inputs


class Inputs(unittest.TestCase):
    def test_selection_rejects_unknown_duplicate_path_and_digest(self):
        original=inputs.selection()
        with tempfile.TemporaryDirectory(prefix='aether-af07-selection-') as folder:
            path=Path(folder)/'selection.json'
            with patch.object(inputs,'SELECTION',path):
                path.write_text(json.dumps(original))
                self.assertEqual(inputs.selection(),original)
                bad=[]
                for key,value in [('format','unknown'),('extra',True),('engine',[]),
                    ('engine',dict(directory='../escape',seal='0'*64)),
                    ('engine',dict(directory='.deps/test',seal='bad'))]:
                    data=dict(original);data[key]=value;bad.append(json.dumps(data))
                bad += ['{"format":"wrong",'+json.dumps(original)[1:]]
                for raw in bad:
                    path.write_text(raw)
                    with self.subTest(raw=raw),self.assertRaises(ValueError):inputs.selection()
                path.unlink();path.symlink_to(ROOT/'docs/native-af07-inputs-v1.json')
                with self.assertRaises(ValueError):inputs.selection()

    def test_exact_historical_artifact_bytes_are_not_live_admission(self):
        members=inputs.checked_members(inputs.ORIGINAL,inputs.ORIGINAL_SEAL)
        self.assertIn('owner.raw',members)
        with tempfile.TemporaryDirectory(prefix='aether-af07-members-') as folder:
            root=Path(folder).resolve();(root/'x').write_bytes(b'body')
            row={'x':{'sha256':inputs.digest(root/'x'),'bytes':4}}
            (root/'sha256.json').write_text(json.dumps(row));seal=inputs.digest(root/'sha256.json')
            self.assertEqual(inputs.checked_members(root,seal),row)
            for action in ('drift','extra','link'):
                (root/'x').unlink(missing_ok=True);(root/'x').write_bytes(b'body')
                if action=='drift':(root/'x').write_bytes(b'bad')
                if action=='extra':(root/'extra').write_text('extra')
                if action=='link':(root/'x').unlink();(root/'x').symlink_to(root/'sha256.json')
                with self.subTest(action=action),self.assertRaises(ValueError):inputs.checked_members(root,seal)
                (root/'extra').unlink(missing_ok=True)

    def test_output_selection_preconditions_before_build_and_cli(self):
        script=ROOT/'scripts/fs_af07_inputs.py'
        for args,code,stream in [(['--help'],0,'out'),(['--version'],0,'out'),([],64,'err'),
            (['--engine-output','/tmp/wrong','--activation-output','/tmp/wrong'],1,'err'),
            (['--engine-output','/tmp/wrong','--activation-output','/tmp/wrong','--paths'],64,'err'),
            (['--engine-output','/tmp/wrong','--activation-output','/tmp/wrong','--dup2'],64,'err')]:
            result=subprocess.run([sys.executable,'-B',script,*args],capture_output=True,timeout=15)
            self.assertEqual(result.returncode,code,result.stderr)
            self.assertTrue(result.stdout if stream=='out' else result.stderr)
        with tempfile.TemporaryDirectory(prefix='aether-af07-out-') as folder:
            root=Path(folder).resolve()
            with patch.object(inputs,'ROOT',root):
                (root/'.deps').mkdir()
                good=root/'.deps/fs-owner-af07-new'
                self.assertEqual(inputs.output_path(good,'fs-owner-af07-'),good)
                good.mkdir()
                with self.assertRaises(ValueError):inputs.output_path(good,'fs-owner-af07-')
                good.rmdir();good.symlink_to(root/'.deps',target_is_directory=True)
                with self.assertRaises(ValueError):inputs.output_path(good,'fs-owner-af07-')

    def test_guarded_profile_and_explicit_checked_outputs_reject_before_engine(self):
        for kwargs in [dict(cwd=True),dict(cwd=1),dict(dup2=True),dict(paths=1),dict(dup2=1),dict(checked={}),dict(checked={'producer':'/tmp/wrong'})]:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                inputs.guarded('/tmp/wrong','/tmp/wrong','0'*64,**kwargs)
