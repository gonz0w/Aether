# SPDX-License-Identifier: BSD-2-Clause
"""Host framing/handshake counterexamples, not native shell acceptance."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from serial_session import BOUNDARY, check_serial, consumer_inputs, decode


def witness():
    inputs = consumer_inputs()
    exchange = json.loads(inputs['exchange.json'])
    raw, events = bytearray(BOUNDARY), []
    uart_offset = 0
    for generation in range(1, 4):
        raw.extend(f'NATIVE MEMORY admitted slot=0 generation={generation} used=73 remaining=55\n'.encode())
        for phase in range(1, 4):
            raw.extend(b'$ ')
            uart_offset += 2
            command = inputs[f'command-{phase}.sh']
            events.append(dict(generation=generation, phase=phase, prompt_uart_offset=uart_offset,
                               prompt_raw_offset=len(raw), observed_raw_bytes=len(raw),
                               writes=[dict(offset=i, requested_hex=command[i:i+7].hex(),
                                            accepted=len(command[i:i+7])) for i in range(0, len(command), 7)]))
            a = 5 * (generation - 1)
            peers = ([(2, a+1, True), (2, a+2, False), (3, 2*generation-1, True), (4, 2*generation-1, True)] if phase == 1 else
                     [(2, a+3, True), (2, a+4, False), (3, 2*generation, True), (4, 2*generation, True)] if phase == 2 else
                     [(2, a+5, True)])
            for slot, epoch, admitted in peers:
                if admitted:
                    raw.extend(f'NATIVE MEMORY admitted slot={slot} generation={epoch} used=24 remaining=104\n'.encode())
                raw.extend(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail=0\n'.encode())
            output = bytes.fromhex(exchange['steps'][phase-1]['expected_uart_after_input_hex'])
            raw.extend(output)
            uart_offset += len(output)
        raw.extend(f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0\n'.encode())
        stderr = b'$ ' * 3 + inputs['expected.stderr']
        raw.extend(f'NATIVE SESSION generation={generation} copies=9 execs=7 stdout={inputs["expected.stdout"].hex()} stderr={stderr.hex()}\n'.encode())
    raw.extend(b'NATIVE supervisor result=100 reclaimed=30\nAETHER NATIVE CONSOLE PASS\n')
    return bytes(raw), events, inputs


class SerialSession(unittest.TestCase):
    def test_complete_transcript(self):
        check_serial(*witness())

    def test_future_input_wrong_generation_and_byte_progress_reject(self):
        raw, events, inputs = witness()
        for kind in ('future', 'generation', 'drop', 'duplicate'):
            bad = copy.deepcopy(events)
            if kind == 'future':
                bad[1]['observed_raw_bytes'] = bad[0]['observed_raw_bytes']
            elif kind == 'generation':
                bad[0]['generation'] = 2
            elif kind == 'drop':
                bad[0]['writes'].pop()
            else:
                bad[0]['writes'].insert(1, bad[0]['writes'][0].copy())
            with self.assertRaises(RuntimeError):
                check_serial(raw, bad, inputs)

    def test_duplicate_missing_prompt_and_unknown_bytes_reject(self):
        raw, events, inputs = witness()
        for bad in (raw.replace(b'$ ', b'$ $ ', 1), raw.replace(b'$ ', b'', 1),
                    raw.replace(BOUNDARY, BOUNDARY + b'unrecognized output\n', 1)):
            with self.assertRaises(RuntimeError):
                check_serial(bad, events, inputs)

    def test_fabricated_prompt_before_terminal_rejects(self):
        raw, events, inputs = witness()
        marker = b'NATIVE terminal slot=4 generation=1 kind=1 detail=0\n'
        # Keep final counts intact but move phase1 terminal beyond the second prompt.
        before, after = raw.split(marker, 1)
        second = after.index(b'$ ') + 2
        bad = before + after[:second] + marker + after[second:]
        altered = copy.deepcopy(events)
        _, positions, _ = decode(bad)
        for event in altered:
            event['prompt_raw_offset'] = positions[event['prompt_uart_offset'] - 1] + 1
            event['observed_raw_bytes'] = event['prompt_raw_offset']
        with self.assertRaises(RuntimeError):
            check_serial(bad, altered, inputs)

    def test_missing_admission_and_early_observation_reject(self):
        import re
        raw, events, inputs = witness()
        admission = re.search(rb'NATIVE MEMORY admitted slot=2 generation=1 [^\n]+\n', raw)[0]
        observation = re.search(rb'NATIVE SESSION generation=1 [^\n]+\n', raw)[0]
        terminal = b'NATIVE terminal slot=2 generation=1 kind=1 detail=0\n'
        mutations = (raw.replace(admission, b'', 1),
                     raw.replace(admission, admission.replace(b'generation=1 ', b'generation=15 '), 1),
                     raw.replace(observation, b'', 1).replace(terminal, observation + terminal, 1))
        for index, bad in enumerate(mutations):
            with self.subTest(index=index):
                altered = copy.deepcopy(events)
                _, positions, _ = decode(bad)
                for event in altered:
                    event['prompt_raw_offset'] = positions[event['prompt_uart_offset'] - 1] + 1
                    event['observed_raw_bytes'] = event['prompt_raw_offset']
                with self.assertRaises(RuntimeError):
                    check_serial(bad, altered, inputs)
