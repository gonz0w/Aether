# SPDX-License-Identifier: BSD-2-Clause
"""Actual sys-init delivery intake and independent activation-trace controls."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_init_consumer as consumer
import fs_session


def trace():
    lines = ['NATIVE MEMORY admitted slot=0 generation=1 used=1328 remaining=6864',
             'NATIVE MEMORY admitted slot=1 generation=1 used=21 remaining=107']
    for slot, pages, prior in ((1, 128, 0), (0, 8192, 1)):
        lines += [f'NATIVE terminal slot={slot} generation=1 kind=1 detail=0']
        lines += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+(phase==7)}' for phase in range(1, 8)]
    lines += ['NATIVE init halted ticks=2400 idle=0 reclaimed=2', 'AETHER NATIVE BLOCK PASS']
    return '\n'.join(lines)+'\n'


class Consumer(unittest.TestCase):
    def test_exact_delivery_sources_compiler_engine_process_and_scoped_stack(self):
        selected = consumer.intake()
        self.assertEqual(selected['owner_intake']['raw_bytes'], 2072)
        self.assertEqual(selected['owner_intake']['stack']['entry_stack_bytes'], 1096)
        self.assertEqual(selected['selected_program_sha256'], consumer.PROGRAM)
        self.assertEqual(consumer.intake(), selected)
        original = consumer.digest
        for path in (consumer.DELIVERY/'owner.raw', consumer.DELIVERY/'owner.elf',
                     consumer.DELIVERY/'preparation.json', consumer.DELIVERY/'candidate-inputs.json',
                     ROOT / 'sys-init/prototypes/native-filesystem/policy.rs'):
            with patch.object(consumer, 'digest', side_effect=lambda p: '0'*64 if Path(p)==path else original(p)):
                with self.assertRaisesRegex(ValueError, 'input drift'):
                    consumer.intake()

    def test_changed_selected_roles_engine_or_program_cannot_be_admitted(self):
        original = consumer.json.loads
        for key, value in (('bootstrap', [24, 0xa001, 0xc001, 0xc002, 0xd001, 0xc003]),
                ('engine_manifest_sha256', '0'*64), ('engine_elf_sha256', '0'*64),
                ('profile', 'AENFS002/ABI28'), ('roles', {}),
                ('selected_program_c002', {'sha256':'0'*64})):
            def changed(data, key=key, value=value):
                row = original(data)
                if 'bootstrap' in row:
                    row = copy.deepcopy(row)
                    row[key] = value
                return row
            with patch.object(consumer.json, 'loads', side_effect=changed):
                with self.assertRaisesRegex(ValueError, 'selection/coverage'):
                    consumer.intake()

    def test_activation_exact_settlement_and_absence_of_conformance_claims(self):
        result = consumer.trace(trace())
        self.assertEqual(result['reclaimed'], 2)
        self.assertTrue(result['read_only_activation'])
        self.assertFalse(result['native_failure_matrix'])
        self.assertFalse(result['after_activation_file_readback'])
        self.assertNotIn('assigned_target_txg', result)
        with self.assertRaises(ValueError):
            fs_session.check_writer(dict(result, status='pass', vm_run_returned=True, disk_sha256='a'*64))

    def test_every_admission_terminal_cleanup_halt_line_is_required_and_unique(self):
        good = trace()
        for line in good.splitlines():
            with self.subTest(line=line):
                with self.assertRaises(ValueError):
                    consumer.trace(good.replace(line+'\n', '', 1))
                with self.assertRaises(ValueError):
                    consumer.trace(good+line+'\n')
        for old, new in (('slot=1 generation=1 kind=1 detail=0', 'slot=1 generation=1 kind=1 detail=62'),
                ('slot=0 generation=1 kind=1 detail=0', 'slot=0 generation=1 kind=2 detail=6'),
                ('ticks=2400', 'ticks=6001'), ('ticks=2400', 'ticks=0'),
                ('used=21 remaining=107', 'used=20 remaining=108'),
                ('selected=6', 'selected=5'), ('reclaimed=2\nAETHER', 'reclaimed=1\nAETHER')):
            with self.assertRaises(ValueError):
                consumer.trace(good.replace(old, new))
        for line in ('NATIVE fault vector=6 rip=400000 error=0', 'AETHER PANIC: failure',
                     'NATIVE observation slot=6 generation=0 offset=0 byte=87'):
            with self.assertRaises(ValueError):
                consumer.trace(good+line+'\n')
        # Moving a clean engine terminal ahead of process settlement still fails.
        line='NATIVE terminal slot=0 generation=1 kind=1 detail=0\n'
        with self.assertRaises(ValueError):
            consumer.trace(line+good.replace(line, ''))

    def test_waits_require_exact_engine_identity_and_balanced_edges(self):
        park='NATIVE STORAGE WAIT slot=0 generation=1 phase=park status=0\n'
        wake=park.replace('park', 'wake')
        self.assertEqual(consumer.trace(park+wake+trace())['primary_channel_waits'], 1)
        for rows in (park, wake, park+park+wake, park+wake.replace('slot=0','slot=6'),
                     park+wake.replace('status=0','status=-9'), park.replace('generation=1','generation=2')+wake):
            with self.assertRaises(ValueError):
                consumer.trace(rows+trace())

    def test_cli_selection_is_explicit_and_keeps_legacy_conformance_separate(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/fs_session.py'), '--sys-init', '--controller-16k'], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 64)
        self.assertNotIn('[RUNNING]', result.stderr)
        source = (ROOT/'scripts/fs_session.py').read_text()
        self.assertIn('if not sys_init: adapt_clients(writer,metadata_service=metadata_candidate is not None)', source)
        self.assertIn("if sys_init: record['inputs'].update(record['sys_init_delivery']['inputs'])", source)
        self.assertIn('consumer_intake() !=', source)
        self.assertIn("sha(writer/'replacement.elf') != delivery['selected_program_sha256']", source)
        self.assertIn("('baseline','writer') if sys_init else ('baseline','writer','reader')", source)


if __name__ == '__main__':
    unittest.main()
