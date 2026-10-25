# SPDX-License-Identifier: BSD-2-Clause
"""Independent offline AF07 selected-oracle review; never execute producer code."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_harness_filesystem_consumer import check_failure, need, FAILURES

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/evidence/filesystem-af07-consumer-2026-10-21'
OWNER = ROOT / 'docs/evidence/filesystem-af07-owner-2026-10-21'
SEAL = 'a63ba3ef2f25789e8ae887b59d22c31fb91a8c9a8a34cc1cf64672f21c48b7d2'
RAW = '620939e5218df104586ff38ce843776696c70814efdd2180c0244e7defae08a7'
ELF = '87598149c7a33307fffd3dc393f4cb87a04f635b40276f079943f93a904ebc03'
ENGINE = '9039e7b1d9a488076e3f8329b3666f39d85385f294d89954dd03df7c2df1753a'
PREFIX = ['AETHER M1: entered x86_64 kernel', 'AETHER M1 PASS',
          'NATIVE SUPERVISION: sys-init owns launch/retry policy; bounded local grants']


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(witness):
    """Four exact wait substitutions; omitted clocks cannot be reconstructed."""
    need(witness['format'] == 'aether-af07-session-oracle-v2'
         and witness['selection_complete'] is True and witness['ceiling_utf8_bytes'] == 65536,
         'incomplete selection')
    lines = witness['lines']
    need(type(lines) is list and len(lines) <= 65536
         and all(type(s) is str and '\n' not in s and '\r' not in s for s in lines), 'line shape')
    raw = ''.join(s + '\n' for s in lines).encode()
    need(len(raw) <= 65536 and len(raw) == witness['retained_utf8_bytes']
         and len(lines) == witness['total_lines'] and digest(raw) == witness['full_selection_sha256'],
         'encoded identity/bound')
    restored = []
    for line in lines:
        if line.startswith('NATIVE RAW '):
            line = line[len('NATIVE RAW '):]
        elif line in ('NATIVE SW 0P', 'NATIVE SW 0W', 'NATIVE SW 6P', 'NATIVE SW 6W'):
            slot, phase = line[-2], ('park' if line[-1] == 'P' else 'wake')
            generation = 1 if slot == '0' else 0
            line = f'NATIVE STORAGE WAIT slot={slot} generation={generation} phase={phase} status=0'
        need(line.startswith(('NATIVE ', 'AETHER PANIC:')) or line in PREFIX
             or line == 'AETHER NATIVE BLOCK PASS', 'unknown selected record')
        restored.append(line)
    decoded = ''.join(s + '\n' for s in restored).encode()
    need(len(decoded) <= 5 * 65536 and len(restored) == witness['decoded_selection']['total_lines']
         and digest(decoded) == witness['decoded_selection']['sha256'], 'decoded identity/bound')
    omitted = witness['omitted_clock_events']
    need(type(omitted['lines']) is int and omitted['lines'] >= 0
         and witness['source_selection']['total_lines'] == len(lines) + omitted['lines'], 'clock count')
    for h in (omitted['sha256'], witness['source_selection']['sha256']):
        need(type(h) is str and re.fullmatch('[0-9a-f]{64}', h) is not None, 'clock/source digest')
    if omitted['lines'] == 0:
        need(omitted['sha256'] == digest(b'')
             and witness['source_selection']['sha256'] == digest(decoded), 'empty clock identity')
    return restored


def cleanup(slot, generation, pages, prior, owner):
    return [f'NATIVE CLEANUP v=1 slot={slot} generation={generation} phase={phase} '
            f'selected={slot if phase == 1 else owner} pages={pages} reclaimed={prior + (phase == 7)}'
            for phase in range(1, 8)]


def writer(lines):
    stripped = []
    pending = False
    parks = wakes = 0
    for line in lines:
        if line.startswith('NATIVE STORAGE WAIT '):
            match = re.fullmatch(r'NATIVE STORAGE WAIT slot=0 generation=1 phase=(park|wake) status=0', line)
            need(match is not None, 'wait identity')
            park = match[1] == 'park'
            need(park != pending, 'wait pairing')
            pending = park
            parks += park
            wakes += not park
        else:
            stripped.append(line)
    need(not pending and parks == wakes == 8, 'wait settlement')
    halt = stripped[-2]
    match = re.fullmatch(r'NATIVE init halted ticks=(\d+) idle=0 reclaimed=2', halt)
    need(match is not None and 0 < int(match[1]) <= 6000, 'halt bound')
    expected = [*PREFIX, 'NATIVE MEMORY admitted slot=0 generation=1 used=1329 remaining=6863',
                'NATIVE MEMORY admitted slot=1 generation=1 used=21 remaining=107',
                'NATIVE terminal slot=1 generation=1 kind=1 detail=0', *cleanup(1, 1, 128, 0, 6),
                'NATIVE terminal slot=0 generation=1 kind=1 detail=0', *cleanup(0, 1, 8192, 1, 6),
                halt, 'AETHER NATIVE BLOCK PASS']
    need(stripped == expected, 'activation ordering/identity/closure')


def reader(lines, fnv):
    expected = list(PREFIX)
    for generation in (1, 2, 3):
        expected.append(f'NATIVE MEMORY admitted slot=0 generation={generation} used=1319 remaining=6873')
        tags = b'BIUVWLP' + bytes.fromhex(fnv) + b'OAMZDJFR' if generation == 1 else b'BNR'
        for index, tag in enumerate(tags):
            expected.append(f'NATIVE observation slot=0 generation={generation} offset={index*8} byte={tag}')
        expected += [f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0',
                     *cleanup(0, generation, 8192, generation - 1, 2)]
    metric = lines[-3]
    need(re.fullmatch(r'NATIVE CLOCK workers scans=\d+ max_contexts=\d+ max_ns=\d+ valid=1', metric)
         is not None, 'reader worker validity')
    expected += [metric, 'NATIVE supervisor result=100 reclaimed=3', 'AETHER NATIVE BLOCK PASS']
    need(lines == expected, 'reader generations/hash/stages/cleanup')


def review(record):
    need(record['status'] == 'pass' and all(record[k] is True for k in
         ('executed', 'native_attempted', 'sys_init', 'sys_init_checks', 'metadata_sys_init_checks')),
         'execution coverage')
    need(record['metadata_protocol'] == 'AFSRPC07' and record['engine_intake']['elf_sha256'] == ENGINE,
         'engine/protocol selection')
    need(record['owner_intake']['raw_sha256'] == RAW and record['owner_intake']['elf_sha256'] == ELF,
         'owner identity')
    need(record['artifacts']['writer']['owner.raw'] == RAW
         and record['artifacts']['writer']['owner.elf'] == ELF, 'boot owner')
    delivery = record['sys_init_delivery']
    need(delivery['same_selected_engine_elf'] == ENGINE and delivery['original_engine_manifest'] ==
         'e28d249b97d2e0a94c376190ec3f3839d50b6c1426cf788bab8f303fdb4084ac'
         and delivery['selected_engine_manifest'] == record['engine_intake']['manifest_sha256'] ==
         'f80f45851c0f3616e66033641969ceff4249eebcf30f717c0df6086c9ddb7dca', 'separate engine seals')
    roles = ['baseline', 'writer', 'reader', *('failure-' + s for s in FAILURES)]
    need([c['role'] for c in record['cases']] == roles and set(record['serial']) == set(roles), 'case closure')
    need(set(record['failed_peers']) == {'failure-' + s for s in FAILURES} and all(p['owner_sha256'] == RAW for p in
         record['failed_peers'].values()), 'failed-peer owner')
    for case in record['cases']:
        role = case['role']
        need(case['status'] == 'pass' and case['vm_run_returned'] is True
             and case['serial_sha256'] == record['serial'][role]['sha256'], 'case/serial binding')
        need(case['namespace_media']['outside_region_canaries_match'] is True, 'media canary')
        lines = decode(record['serial'][role]['machine_witness'])
        if role == 'writer':
            writer(lines)
            need(case['admitted_instances'] == case['reclaimed'] == 2 and case['final_live_workers'] == 0
                 and case['primary_channel_waits'] == case['primary_channel_wakes'] == 8, 'writer disposition')
        elif role in ('baseline', 'reader'):
            reader(lines, case['input_xdr_fnv1a64'])
            need(case['namespace_bytes_verified'] == 780248 and case['generations'] == case['reclaimed'] == 3
                 and case['final_live_workers'] == 0, 'reader disposition')
        else:
            need(lines[:3] == PREFIX, 'negative boot prefix')
            check_failure('\n'.join(lines[1:]) + '\n', case['expected_failure'])
            need(case['expected_failure'] == role[len('failure-'):] and case['engine_reclaimed'] is False
                 and case['successful_halt'] is False and case['automatic_replay'] is False
                 and case['actual_owner_fail_stop'] is True, 'false failure settlement')
            need(case['namespace_media'] == record['pristine_media'], 'negative media')
    baseline, activation, recovered = record['cases'][:3]
    need(record['after_activation_file_readback'] is True and record['readback_media_unchanged'] is True
         and activation['namespace_media'] == recovered['namespace_media'] == record['stopped_media']
         and baseline['namespace_media'] == record['pristine_media'], 'media/readback binding')


class AF07ConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (PACKET / 'native-receipt.json').read_bytes()
        need(len(raw) <= 5 * 1024 * 1024 and digest(raw) == SEAL, 'receipt seal')
        cls.record = json.loads(raw)

    def test_exact_delivery_inputs_and_owner(self):
        for name, h in self.record['sys_init_delivery']['inputs'].items():
            prefix = str(ROOT) + '/'
            if name.startswith(prefix):
                relative = name[len(prefix):]
                if relative.startswith('prototypes/'):
                    path = PACKET / 'frozen-inputs' / relative
                else:
                    path = ROOT / relative
                self.assertEqual(digest(path.read_bytes()), h, name)
        raw = (OWNER / 'owner.raw').read_bytes()
        self.assertEqual(digest(raw), RAW)
        self.assertEqual(raw[0x28:0x2a], b'\x0f\x0b')
        self.assertEqual(digest((OWNER / 'owner.elf').read_bytes()), ELF)

    def test_all_eight_complete_selected_oracles(self):
        review(self.record)

    def test_semantic_record_corruptions(self):
        for case in self.record['cases']:
            role = case['role']
            lines = decode(self.record['serial'][role]['machine_witness'])
            check = (writer if role == 'writer' else
                     (lambda value: reader(value, case['input_xdr_fnv1a64'])) if role in ('baseline', 'reader') else
                     (lambda value: check_failure('\n'.join(value[1:]) + '\n', case['expected_failure'])))
            mutations = [[], lines[:-1], lines + ['AETHER NATIVE BLOCK PASS'],
                         [s.replace('generation=1', 'generation=2', 1) for s in lines],
                         [s.replace('detail=0', 'detail=9') for s in lines],
                         [s.replace('phase=7 ', 'phase=6 ') for s in lines],
                         [s for s in lines if not s.startswith('NATIVE MEMORY admitted ')]]
            # Some negative cases have no terminal/cleanup; retain only actual changes.
            for mutated in mutations:
                if mutated == lines:
                    continue
                with self.assertRaises((ValueError, IndexError), msg=role):
                    check(mutated)

    def test_witness_corruptions(self):
        for serial in self.record['serial'].values():
            w = serial['machine_witness']
            for key, value in [('selection_complete', False), ('total_lines', 0),
                               ('retained_utf8_bytes', 0), ('full_selection_sha256', '0'*64),
                               ('ceiling_utf8_bytes', 65537), ('lines', ['NATIVE SW 0P\nbad'])]:
                bad = copy.deepcopy(w)
                bad[key] = value
                with self.assertRaises(ValueError):
                    decode(bad)

    def test_receipt_corruptions(self):
        for path, value in [(('executed',), False), (('metadata_protocol',), 'AFSRPC06'),
                            (('owner_intake', 'raw_sha256'), '0'*64),
                            (('engine_intake', 'elf_sha256'), '0'*64),
                            (('cases', 1, 'reclaimed'), 1), (('cases', 2, 'namespace_bytes_verified'), 0),
                            (('cases', 3, 'engine_reclaimed'), True),
                            (('cases', 4, 'successful_halt'), True),
                            (('after_activation_file_readback',), False)]:
            bad = copy.deepcopy(self.record)
            dest = bad
            for key in path[:-1]:
                dest = dest[key]
            dest[path[-1]] = value
            with self.assertRaises(ValueError):
                review(bad)
