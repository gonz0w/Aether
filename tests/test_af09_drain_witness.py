# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic prospective oracle controls; none of these rows ran in a guest."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from af09_drain_trace import CASES, FIELDS, validate_witness

ADMISSION = dict(engine_pages=300, shell_pages=40, helper_pages=30, owner_bytes=48000)


def specimen(case):
    """Construct typed facts plus ordinary markers for mutation-based denials."""
    result = []
    ordinal = 0
    negative = CASES.index(case) >= 4
    def raw(text):
        result.append(text)
    def emit(phase, slot, tick, count=0, aux=0, status=0, seq=100):
        nonlocal ordinal
        # Ordinary production markers precede the corresponding typed facts.
        if phase in (7, 14, 21):
            kind, detail = (3, 143) if phase == 14 else (1, 0)
            raw(f'NATIVE terminal slot={slot} generation=1 kind={kind} detail={detail}\n')
        if phase == 15:
            pages, prior = (8192, 2) if slot == 0 else (128, 0 if slot == 2 else 1)
            for p in range(3, 8):
                raw(f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={p} selected=6 pages={pages} reclaimed={prior + int(p == 7)}\n')
        if phase == 16:
            raw('NATIVE observation slot=0 generation=1 offset=0 byte=1\n')
        if phase == 23:
            raw(f'NATIVE init halted ticks={tick} idle=1 reclaimed=3\n')
        values = dict(case=CASES.index(case)+1, row=ordinal, phase=phase, slot=slot,
                      gen=0 if slot == 6 else 1, seq=seq, tick=tick,
                      deadline=510 if phase == 9 or tick >= 10 else 0,
                      status=status, count=count, aux=aux)
        result.append(values); ordinal += 1
        if phase in (7, 21):
            prior = 0 if phase == 7 else 2
            pages = 128 if phase == 7 else 8192
            for p in (1, 2):
                selected = slot if p == 1 else (2 if phase == 7 else 6)
                raw(f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={p} selected={selected} pages={pages} reclaimed={prior}\n')
    for slot, key, cap in ((0, 'engine_pages', 8192), (1, 'shell_pages', 128)):
        raw(f'NATIVE MEMORY admitted slot={slot} generation=1 used={ADMISSION[key]} remaining={cap-ADMISSION[key]}\n')
    emit(1,6,0);emit(2,2,1,1);emit(3,2,2,304);emit(25,2,3,1);emit(4,2,3)
    emit(27,2,3,32);emit(28,1,3,32);emit(5,1,3);emit(25,2,3,1,1)
    emit(7,1,4);emit(6,2,4,16);emit(6,2,4,32);emit(8,1,4,aux=1,status=1)
    emit(9,6,10);emit(13,2,10,32);emit(14,2,10);emit(15,2,10);emit(15,1,10)
    emit(16,0,11,2,3,8)
    if case == 'pending_fragment':
        emit(25,0,11,2);emit(24,6,12,aux=6,status=-11)
        emit(10,6,12,seq=50);emit(26,6,12,seq=50);emit(25,0,12,2,1)
        emit(17,0,12,16);emit(25,0,12,3)
        emit(26,6,510,aux=1,seq=50);emit(11,6,510,status=-110)
    elif case == 'no_ack':
        emit(25,0,11,2);emit(24,6,12,aux=6,status=-11)
        emit(10,6,12,seq=50);emit(11,6,510,status=-110)
    elif case == 'partial_ack':
        emit(17,0,12,16);emit(25,0,12,3);emit(18,6,13,16)
        emit(25,0,110,3,1);emit(17,0,110,32);emit(25,0,110,3);emit(18,6,111,32)
        emit(25,0,210,3,1);emit(17,0,210,48);emit(25,0,210,3);emit(18,6,211,48)
        emit(24,6,211,aux=6,status=-11);emit(10,6,211,seq=50);emit(11,6,510,status=-110)
    else:
        if case == 'exit_deadline':
            emit(24,6,11,aux=6,status=-11)
        for i in range(1,5):
            emit(17,0,10+i*2,i*16);emit(18,6,11+i*2,i*16)
        emit(20,0,20)
        if negative:
            emit(25,0,20,4);emit(10,6,21,seq=50);emit(11,6,510,status=-110)
        else:
            emit(21,0,20)
    closed_tick = 510 if negative else 21
    emit(19,6,closed_tick,aux=0);emit(19,6,closed_tick,aux=1);emit(22,0,closed_tick,1,1)
    if negative:
        raw('NATIVE fault vector=6 rip=123 error=0\nNATIVE PANIC pc=123\nAETHER PANIC: native supervisor terminated\n')
    else:
        emit(15,0,22);emit(23,6,23);raw('AETHER NATIVE BLOCK PASS\n')
    return result


def encode(items):
    result = []
    ordinal = 0
    for item in items:
        if isinstance(item, str):
            result.append(item)
        else:
            item = {**item, 'row': ordinal};ordinal += 1
            result.append('AF09-DRAIN v=1 ' + ' '.join(f'{f}={item[f]}' for f in FIELDS) + '\n')
    return ''.join(result).encode()


class DrainWitness(unittest.TestCase):
    def test_eight_complete_prospective_cases(self):
        for case in CASES:
            with self.subTest(case=case):
                result = validate_witness(encode(specimen(case)), case, ADMISSION)
                self.assertEqual(result['clean_halt'], CASES.index(case) < 4)
                self.assertIs(result['native_executed'], False)

    def test_every_required_phase_omission_is_denied(self):
        for case in CASES:
            original = specimen(case)
            phases = {item['phase'] for item in original if isinstance(item, dict)}
            for phase in phases - {24}:
                changed = [item for item in original if not isinstance(item, dict) or item['phase'] != phase]
                with self.subTest(case=case, phase=phase), self.assertRaises(ValueError):
                    validate_witness(encode(changed), case, ADMISSION)

    def test_identity_counter_deadline_prefix_and_ack_mutations(self):
        changes = ((2, 'count', 2), (3, 'count', 303), (8, 'status', 0),
                   (6, 'count', 31), (13, 'aux', 1), (16, 'count', 3),
                   (16, 'aux', 4), (16, 'status', 7), (9, 'deadline', 511),
                   (17, 'count', 15), (19, 'status', -9), (22, 'aux', 0),
                   (4, 'gen', 2), (4, 'slot', 1), (27, 'count', 31))
        for case in CASES:
            for phase, field, value in changes:
                original = specimen(case)
                selected = next((i for i in original if isinstance(i, dict) and i['phase'] == phase), None)
                if selected is None:
                    continue
                selected[field] = value
                with self.subTest(case=case, phase=phase, field=field), self.assertRaises(ValueError):
                    validate_witness(encode(original), case, ADMISSION)

    def test_overlapping_parks_and_inconsistent_ordinary_halt_reject(self):
        items = specimen('no_ack')
        park_index = next(i for i,item in enumerate(items) if isinstance(item,dict) and item['phase']==10)
        second = dict(items[park_index])
        completion = dict(second,phase=11,status=0)
        items[park_index+1:park_index+1] = [second,completion]
        with self.assertRaises(ValueError):
            validate_witness(encode(items),'no_ack',ADMISSION)
        good=encode(specimen('stream'))
        for bad in (good.replace(b'halted ticks=23',b'halted ticks=5999'),
                    good.replace(b'ticks=23 idle=1',b'ticks=23 idle=24')):
            with self.assertRaises(ValueError):
                validate_witness(bad,'stream',ADMISSION)

    def test_copy_is_not_a_helper_load_or_exec(self):
        for case in CASES:
            good = encode(specimen(case))
            extra = b'NATIVE MEMORY admitted slot=2 generation=1 used=30 remaining=98\n'
            with self.subTest(case=case), self.assertRaises(ValueError):
                validate_witness(extra + good, case, ADMISSION)

    def test_existing_counter_observation_required_exact_unique_and_before_counter(self):
        marker = b'NATIVE observation slot=0 generation=1 offset=0 byte=1\n'
        for case in CASES:
            good = encode(specimen(case))
            for bad in (good.replace(marker,b''),good.replace(marker,marker+marker),
                        good.replace(marker,marker.replace(b'offset=0',b'offset=8')),
                        good.replace(marker,b'')+marker):
                with self.subTest(case=case),self.assertRaises(ValueError):
                    validate_witness(bad,case,ADMISSION)

    def test_pending_fragment_and_partial_release_denials(self):
        for phase, field, value in ((26,'seq',101),(17,'seq',49),(17,'tick',510),(11,'status',0)):
            items = specimen('pending_fragment')
            next(i for i in items if isinstance(i,dict) and i['phase']==phase)[field]=value
            with self.subTest(phase=phase,field=field), self.assertRaises(ValueError):
                validate_witness(encode(items),'pending_fragment',ADMISSION)
        items=specimen('partial_ack')
        next(i for i in items if isinstance(i,dict) and i['phase']==25 and i['slot']==0 and i['aux']==1)['tick']=109
        with self.assertRaises(ValueError):
            validate_witness(encode(items),'partial_ack',ADMISSION)

    def test_old_workload_fault_alone_truncation_and_geometry_denials(self):
        for case in CASES:
            good=encode(specimen(case))
            for bad in (good[:-1], good+b'AF09-BEGIN\n', good.replace(b'NATIVE CLEANUP v=1 slot=2',b'NATIVE CLEANUP v=1 slot=3'),
                        good.replace(b'NATIVE terminal slot=2 generation=1 kind=3 detail=143',b'NATIVE terminal slot=2 generation=1 kind=1 detail=7')):
                with self.subTest(case=case), self.assertRaises(ValueError):
                    validate_witness(bad,case,ADMISSION)
            for geometry in ({}, {**ADMISSION,'shell_pages':129}, {**ADMISSION,'owner_bytes':49153}):
                with self.assertRaises(ValueError):
                    validate_witness(good,case,geometry)
        with self.assertRaises(ValueError):
            validate_witness(b'NATIVE fault vector=6 rip=123 error=0\n','no_ack',ADMISSION)


if __name__ == '__main__':
    unittest.main()
