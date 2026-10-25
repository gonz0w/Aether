# SPDX-License-Identifier: BSD-2-Clause
"""Offline consumer review; no sibling reads, VM or raw-UART reconstruction."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/evidence/filesystem-native-consumer-2026-10-20'
OWNER = ROOT / 'docs/evidence/filesystem-init-owner-2026-10-20'
SEAL = 'eb792686dadc0f5e17c4fc2538b5b6cb9c53e2da618213cbadf1ee0d528dcd5b'
RAW = 'c0a01ec913eb44de96d27d93ac71416df015951cdb12095c09c7b17e9e8d706e'
ELF = '1bae5d805308c0f664945e52e5bb4564febd38315d2c62e515217fe1e54e53a9'
ENGINE = '89bbc3291a3d13d3639503048f6378a2ffac351d1cfe689d698135cbeab24997'
FAILURES = ('startup-exit', 'malformed-greeting', 'reply-generation', 'failed-exit', 'reply-close')


def need(value, message):
    if not value:
        raise ValueError(message)


def expected_failure(selection):
    """Exact selected kernel span; stop phases1/2 are not reclaim phases3..7."""
    index = FAILURES.index(selection)
    late = index >= 2
    pages = 20 if index == 0 else 21
    lines = ['AETHER M1 PASS',
             'NATIVE SUPERVISION: sys-init owns launch/retry policy; bounded local grants',
             f'NATIVE MEMORY admitted slot=0 generation=1 used={pages} remaining={8192-pages}']
    if late:
        lines += ['NATIVE MEMORY admitted slot=1 generation=1 used=21 remaining=107',
                  'NATIVE terminal slot=1 generation=1 kind=1 detail=0']
        lines += [f'NATIVE CLEANUP v=1 slot=1 generation=1 phase={phase} selected={1 if phase == 1 else 6} pages=128 reclaimed={int(phase == 7)}'
                  for phase in range(1, 8)]
    lines.append(f'NATIVE observation slot=0 generation=1 offset=0 byte={b"SGDFL"[index]}')
    if index in (0, 3):
        lines.append(f'NATIVE terminal slot=0 generation=1 kind=1 detail={71 if index == 0 else 72}')
        lines += [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} selected={0 if phase == 1 else 6} pages=8192 reclaimed={int(late)}'
                  for phase in (1, 2)]
    lines += ['NATIVE fault vector=6 rip=400028 error=0',
              'AETHER PANIC: native supervisor terminated']
    return lines


def check_failure(text, selection):
    need(selection in FAILURES, 'unknown selection')
    need(text.splitlines() == expected_failure(selection), 'incomplete or mismatched kernel span')


def check_report(record):
    need(record['status'] == 'pass' and record['executed'] is True
         and record['sys_init'] is True and record['sys_init_checks'] is True, 'coverage')
    need(record['engine_intake']['elf_sha256'] == ENGINE, 'engine selection')
    need(record['owner_intake']['raw_sha256'] == RAW and record['owner_intake']['elf_sha256'] == ELF,
         'owner identity')
    need(record['artifacts']['writer']['owner.raw'] == RAW
         and record['artifacts']['writer']['owner.elf'] == ELF, 'boot artifact owner')
    need(len(record['failed_peers']) == 5
         and all(p['owner_sha256'] == RAW for p in record['failed_peers'].values()), 'failed-peer owner')
    roles = ['baseline', 'writer', 'reader', *('failure-' + s for s in FAILURES)]
    need([c['role'] for c in record['cases']] == roles, 'case closure')
    for case in record['cases']:
        need(case['status'] == 'pass' and case['vm_run_returned'] is True, 'incomplete case')
        need(case['namespace_media']['outside_region_canaries_match'] is True, 'media guard')
        need(case['serial_sha256'] == record['serial'][case['role']]['sha256'], 'serial binding')
    baseline, writer, reader, *failures = record['cases']
    need(writer['admitted_instances'] == 2 and writer['reclaimed'] == 2 and writer['final_live_workers'] == 0
         and writer['engine_terminal_zero'] is True and writer['selected_process_terminal_zero'] is True
         and writer['cleanup_boundaries_per_instance'] == 7, 'activation disposition')
    need(writer['primary_channel_waits'] == writer['primary_channel_wakes'] == 8, 'wait settlement')
    need(baseline['namespace_bytes_verified'] == reader['namespace_bytes_verified'] == 780248,
         'original file readback')
    need(reader['generations'] == reader['reclaimed'] == 3 and reader['final_live_workers'] == 0
         and reader['cleanup_boundaries_per_generation'] == 7, 'reader cleanup')
    # Import/export changes pool metadata. Only the fresh reader must preserve
    # the exported medium; do not equate it with the original pristine disk.
    need(writer['namespace_media']['sha256'] == reader['namespace_media']['sha256'], 'exported readback')
    need(record['after_activation_file_readback'] is True and record['readback_media_unchanged'] is True,
         'readback coverage')
    for selection, case in zip(FAILURES, failures):
        need(case['expected_failure'] == selection and case['actual_owner_fail_stop'] is True, 'negative selection')
        need(case['engine_reclaimed'] is False and case['successful_halt'] is False
             and case['automatic_replay'] is False, 'false failure cleanup/halt/replay')
        need(case['dependent_admitted'] is (selection not in FAILURES[:2]), 'negative admission')
        need(case['namespace_media'] == record['pristine_media'], 'negative changed media')


class FilesystemConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (PACKET / 'native-receipt.json').read_bytes()
        need(len(raw) <= 4 * 1024 * 1024 and hashlib.sha256(raw).hexdigest() == SEAL, 'receipt seal')
        cls.record = json.loads(raw)

    def test_exact_owner_and_frozen_local_inputs(self):
        raw = (OWNER / 'owner.raw').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), RAW)
        self.assertEqual(raw[0x28:0x2a], b'\x0f\x0b')
        prefix = '/Users/cam/DEV/sys-init/'
        checked = 0
        for name, digest in self.record['sys_init_delivery']['inputs'].items():
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix):]
            if relative.startswith('prototypes/native-filesystem/'):
                leaf = Path(relative).name
                path = OWNER / ('candidate-inputs.json' if leaf == 'inputs.json' else 'source/' + leaf)
            else:
                path = ROOT / relative
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, name)
            checked += 1
        self.assertEqual(checked, 13)

    def test_reported_positive_and_negative_dispositions(self):
        check_report(self.record)

    def test_all_five_retained_kernel_spans(self):
        for selection in FAILURES:
            text = (PACKET / ('failure-' + selection + '.kernel.log')).read_text()
            tail = self.record['serial']['failure-' + selection]['tail']
            self.assertEqual(text, tail[tail.index('AETHER M1 PASS\n'):])
            check_failure(text, selection)

    def test_sixty_five_semantic_corruptions_reject(self):
        for selection in FAILURES:
            text = (PACKET / ('failure-' + selection + '.kernel.log')).read_text()
            mutations = ['', text[:-5], text.replace('AETHER M1 PASS\n', ''),
                         text.replace('generation=1', 'generation=2', 1),
                         text.replace('offset=0 byte=', 'offset=8 byte=', 1),
                         text.replace('rip=400028', 'rip=400029'),
                         text.replace('vector=6', 'vector=14'),
                         text.replace('error=0', 'error=1'),
                         text.replace('AETHER PANIC:', 'AETHER PANIC'),
                         text + 'NATIVE init halted ticks=9 idle=0 reclaimed=2\n',
                         text + 'AETHER NATIVE BLOCK PASS\n',
                         text.replace('NATIVE observation ', 'NATIVE MEMORY admitted slot=1 generation=1 used=21 remaining=107\nNATIVE observation ', 1),
                         text.replace('NATIVE fault ', 'NATIVE CLEANUP v=1 slot=0 generation=1 phase=3 selected=6 pages=8192 reclaimed=1\nNATIVE fault ', 1)]
            self.assertEqual(len(mutations), 13)
            for mutated in mutations:
                with self.assertRaises(ValueError, msg=selection):
                    check_failure(mutated, selection)

    def test_receipt_semantic_corruptions_reject(self):
        mutations = [lambda r: r.update(executed=False),
                     lambda r: r['cases'][1].update(vm_run_returned=False),
                     lambda r: r['cases'][1].update(primary_channel_wakes=7),
                     lambda r: r['cases'][2]['namespace_media'].update(sha256='0'*64),
                     lambda r: r['cases'][3].update(successful_halt=True),
                     lambda r: r['cases'][4].update(engine_reclaimed=True),
                     lambda r: r['cases'][5].update(automatic_replay=True),
                     lambda r: r['owner_intake'].update(raw_sha256='0'*64)]
        for mutate in mutations:
            record = copy.deepcopy(self.record)
            mutate(record)
            with self.assertRaises(ValueError):
                check_report(record)
