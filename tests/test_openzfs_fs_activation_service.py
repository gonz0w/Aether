# SPDX-License-Identifier: BSD-2-Clause
"""Matched readiness candidate; preserve independent runtime recovery and old profiles."""
import ast
import copy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_openzfs_fs_runtime_service as prior
from openzfs_fs_service import intake, recheck
import openzfs_fs_activation_service as activation
import openzfs_fs_mixed_service as mixed
import service_runtime_smoke as runtime
import zpl_pair as pair

ROOT, SOURCE = prior.ROOT, prior.SOURCE
DELIVERY = prior.DELIVERY.with_name('filesystem-service-activation-2026-10-20-v1')


class Activation(unittest.TestCase):
    def fixture(self, case):
        helper = prior.RuntimeService(); f = helper.fixture(case); self.addCleanup(helper.doCleanups)
        selected = intake(DELIVERY, mixed=True, waiting=True, bulk=True, runtime=True, activation=True)
        b = f.builds['writer']; b['fs_service'] = selected; b['fs_service_activation'] = True
        b['port']['volume']['namespace_objects'].update({'fs-service-consumer': mixed.sha(selected['object']),
            'mixed-owner-source': prior.sha(activation.owner((SOURCE / 'fs-service-owner.inc').read_text()))})
        origins = b['port']['fs_service_origins']; origins.pop('aether_fs_runtime_run')
        origins['aether_fs_activation_run'] = '/delivery/filesystem-activation.o'
        for role, build in f.builds.items():
            if role == 'writer':
                build['commands'][0]['argv'].append('-Dnative-service-activation=true')
                build['commands'][1]['argv'][1:1] = ['--cfg', 'fs_activation']
                build['commands'][1]['argv'] += ['-C', 'link-arg=-Tuser/storage/service-runtime/activation-linker.ld']
            else:
                build['commands'] = [{'argv': ['zig', 'build']},
                    {'argv': ['rustc', '-Clink-arg=--oformat=binary', '-C', 'link-arg=-Tuser/protection/linker.ld']}]
            build['cases'][0]['supervisor_bytes'] = 4181 if role == 'writer' else 3000
        return f

    def verify(self, f, case, **changes):
        options = dict(writer_ticks_6000=True, writer_60s=True, recovery_diagnostic=True,
            filesystem_service=DELIVERY, filesystem_service_case=case, filesystem_service_mixed=True,
            filesystem_service_wait=True, filesystem_service_bulk=True, filesystem_service_runtime=True,
            filesystem_service_activation=True)
        options.update(changes)
        with patch.object(runtime, 'sealed'):
            pair.verify_prepared(f.output, f.builds, **options)

    def test_exact_candidate_legacy_substitution_and_consumed_record_rejection(self):
        selected = intake(DELIVERY, mixed=True, waiting=True, bulk=True, runtime=True, activation=True)
        recheck(selected); self.assertEqual(selected['manifest_sha256'], mixed.ACTIVATION_SEAL)
        for root, flag in [(DELIVERY, False), (prior.DELIVERY, True)]:
            with self.assertRaises(ValueError):
                intake(root, mixed=True, waiting=True, bulk=True, runtime=True, activation=flag)
        for key, value in [('activation', False), ('object', str(prior.DELIVERY / 'objects/filesystem-runtime.o'))]:
            changed = copy.deepcopy(selected); changed[key] = value
            with self.assertRaises(ValueError): recheck(changed)
        for args in [(True,False,True,None), (True,True,False,selected), (False,True,True,selected)]:
            with self.assertRaises(ValueError): activation.validate_profile(*args)

    def test_all_four_cases_match_sources_origins_size_and_actual_kernel_linker(self):
        for case in ('normal', 'lost-reply', 'partial-request', 'close-failure'):
            f = self.fixture(case); self.verify(f, case); original = copy.deepcopy(f.builds)
            for change in ('flag', 'reader-flag', 'cfg', 'linker', 'limit', 'origin', 'owner', 'record'):
                f.builds = copy.deepcopy(original); b = f.builds['writer']
                if change == 'cfg': b['commands'][1]['argv'].remove('fs_activation')
                if change == 'flag': b['commands'][0]['argv'].remove('-Dnative-service-activation=true')
                if change == 'reader-flag': f.builds['reader']['commands'][0]['argv'].append('-Dnative-service-activation=true')
                if change == 'linker': b['commands'][1]['argv'][-1] = 'link-arg=-Tuser/protection/linker.ld'
                if change == 'limit': b['cases'][0]['supervisor_bytes'] = 8193
                if change == 'origin': b['port']['fs_service_origins']['aether_fs_activation_run'] = '/fake/filesystem-runtime.o'
                if change == 'owner': b['port']['volume']['namespace_objects']['mixed-owner-source'] = 'drift'
                if change == 'record': b['fs_service_activation'] = False
                with self.subTest(case=case, change=change), self.assertRaises(ValueError): self.verify(f, case)
            f.builds = original
            with self.assertRaises(ValueError): self.verify(f, case, filesystem_service_activation=False)

    def test_actual_driver_emits_separate_linker_and_early_cli_guard(self):
        node = next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text())) if isinstance(n, ast.Expr)
            and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'command'
            and 'link-arg=--oformat=binary' in ast.unparse(n))
        f = self.fixture('normal'); emitted = []
        scope = {n.id: False for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        scope.update(command=lambda argv, log: emitted.append(list(map(str, argv))), str=str,
            volume_readonly=runtime.volume_readonly, SOURCE=runtime.SOURCE, name='pool-import',
            namespace_ipc=True, namespace_wait=True, service_case=0, volume=True, engine_native=True,
            service={'activation': True}, _zpl_fs_namespace=None, _zpl_fs_runtime=True, _zpl_fs_activation=True,
            _zpl_fs_bulk=True, _zpl_fs_mixed=True, pool_create=True, pool_zpl_write=True,
            WRITE_CASES=runtime.WRITE_CASES, driver_source=f.output/'writer/supervisor.rs', dest=f.output/'writer')
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual activation driver>', 'exec'), scope)
        f.builds['writer']['commands'][1] = {'argv': emitted[0]}; self.verify(f, 'normal')
        with self.assertRaisesRegex(ValueError, 'activation requires'):
            runtime.suite(None, _zpl_fs_activation=True)
        with self.assertRaisesRegex(ValueError, 'activation requires'):
            pair.pair(None, None, filesystem_service_activation=True)
        result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/zpl_pair.py'),
            '--delivery', '/missing', '--utc-delivery', '/missing', '--filesystem-service-activation'],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 64)
        self.assertIn('activation requires', result.stderr)
        self.assertNotIn('[RUNNING]', result.stderr)


if __name__ == '__main__':
    unittest.main()
