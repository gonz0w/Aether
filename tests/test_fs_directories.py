# SPDX-License-Identifier: BSD-2-Clause
"""Actual native directory controller transcripts, corruptions and fixed fit."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
import unittest
import test_fs_activation as prior
ROOT=prior.ROOT


class DirectoryClient(unittest.TestCase):
    def test_actual_controller_transcripts_and_failure_modes(self):
        with tempfile.TemporaryDirectory(prefix='aether-directory-client-') as directory:
            out=Path(directory);source=out/'test.rs'
            source.write_text((ROOT/'tests/fixtures/fs_directory_client.rs').read_text().replace('CONTROLLER',str(ROOT/'user/storage/service-runtime/fs-directories-client.rs')))
            for case,cfg,count in [('normal',None,2),('lost-reply','fs_lost_reply',1),('partial-request','fs_partial_request',1)]:
                binary=out/case;argv=['rustc','+1.98.0','--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn','--test',str(source),'-o',str(binary)]
                if cfg:argv+=['--cfg',cfg]
                r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=60);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                r=subprocess.run([str(binary),'--test-threads=1'],capture_output=True,text=True,timeout=60)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn(f'{count} passed; 0 failed',r.stdout)

    def test_all_four_actual_controllers_fit_unchanged_readonly_code_budget(self):
        with tempfile.TemporaryDirectory(prefix='aether-directory-controller-') as directory:
            out=Path(directory);source=out/'supervisor.rs';source.write_text(prior.Controller().driver())
            for case in ['normal','lost-reply','partial-request','close-failure']:
                binary=out/(case+'.raw');argv=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-Dwarnings','-Copt-level=z','-Clto=fat','-Ccodegen-units=1','-Cpanic=abort','-Crelocation-model=static','-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld','-Clink-arg=--oformat=binary']
                for cfg in ['pool_create','pool_import','fs_mixed','namespace_wait','fs_bulk','fs_runtime','fs_activation','fs_names','fs_directories']:argv+=['--cfg',cfg]
                if case in ('lost-reply','partial-request'):argv+=['--cfg','fs_lost_reply' if case=='lost-reply' else 'fs_partial_request']
                argv += [str(source),'-o',str(binary)]
                r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=60);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                self.assertLessEqual(binary.stat().st_size,8192)
                print('directory controller',case,binary.stat().st_size,hashlib.sha256(binary.read_bytes()).hexdigest())


if __name__=='__main__':unittest.main()
