# SPDX-License-Identifier: BSD-2-Clause
"""Independent exact byte/identity/cleanup oracle for the selected ABI24 session."""
import json
from pathlib import Path
import re
def need(value, message):
    if not value:
        raise ValueError(message)

BOUNDARY = b'NATIVE SUPERVISION: sys-init owns launch/retry policy; bounded local grants\n'
ADMISSION = rb'NATIVE MEMORY admitted slot=([0-4]) generation=([0-9]+) used=([0-9]+) remaining=([0-9]+)\n'
TERMINAL = rb'NATIVE terminal slot=([0-4]) generation=([0-9]+) kind=([0-9]+) detail=([0-9]+)\n'
HALT = rb'NATIVE init halted ticks=([0-9]+) idle=([0-9]+) reclaimed=([0-9]+)\n'


def check(raw, record, workload):
    need(raw.count(BOUNDARY) == 1, 'unique supervision boundary')
    need(b'AETHER PANIC:' not in raw and b'NATIVE supervisor result=' not in raw
         and b'NATIVE SESSION ' not in raw, 'no alternate failure/completion')
    cursor = raw.index(BOUNDARY) + len(BOUNDARY)
    uart = bytearray()
    positions = []
    admitted = []
    terminal = []
    halt = []
    while cursor < len(raw):
        rest = raw[cursor:]
        match = re.match(ADMISSION, rest)
        if match:
            admitted.append((tuple(map(int, match.groups())), cursor))
        else:
            match = re.match(TERMINAL, rest)
            if match:
                terminal.append((tuple(map(int, match.groups())), cursor))
            else:
                match = re.match(HALT, rest)
                if match:
                    halt.append((tuple(map(int, match.groups())), cursor))
        if match:
            cursor += len(match[0])
        else:
            # Unknown/malformed diagnostics remain bytes and fail exact UART.
            uart.append(raw[cursor])
            positions.append(cursor)
            cursor += 1
    need(len(halt) == 1 and halt[0][1] + len(re.match(HALT, raw[halt[0][1]:])[0]) == len(raw), 'unique final halt')
    polling = record['label'] == 'polling-limit'
    expected_uart = b'$ ' if polling else bytes.fromhex(workload['expected.uart'])
    need(bytes(uart) == expected_uart, 'exact UART bytes')
    expected_terminal = {(0, 1, 1, 0)}
    if not polling:
        expected_terminal |= {(2, g, 1, 0) for g in range(1, 6)}
        expected_terminal |= {(s, g, 1, 0) for s in (3, 4) for g in (1, 2)}
    need(len(terminal) == len(expected_terminal)
         and {x for x, _ in terminal} == expected_terminal, 'exact terminal identities')
    expected_admitted = {(0, 1)} if polling else {(0, 1), (2, 1), (2, 3), (2, 5), (3, 1), (3, 2), (4, 1), (4, 2)}
    need(len(admitted) == len(expected_admitted)
         and {x[:2] for x, _ in admitted} == expected_admitted, 'exact admission identities')
    need(all(x[2:] == ((73, 55) if x[0] == 0 else (24, 104))
             for x, _ in admitted), 'bounded memory observations')
    need(all(offset < halt[0][1] for _, offset in terminal), 'all terminals before halt')
    events = record['events']
    need(len(events) == (0 if polling else 3), 'input count')
    offset = 0
    exchange = json.loads(bytes.fromhex(workload['exchange.json']))
    for i, event in enumerate(events):
        phase = i + 1
        offset += 2
        raw_boundary = positions[offset - 1] + 1
        need((event['generation'], event['phase'], event['prompt_uart_offset']) == (1, phase, offset)
             and event['prompt_raw_offset'] == raw_boundary
             and event['observed_raw_bytes'] >= raw_boundary, 'prompt-driven input')
        required = {(2, 1), (2, 2), (3, 1), (4, 1)} if phase >= 2 else set()
        if phase >= 3:
            required |= {(2, 3), (2, 4), (3, 2), (4, 2)}
        prior = {x[:2] for x, at in terminal if at < raw_boundary}
        need(required <= prior, 'phase cleanup before next prompt')
        command = bytes.fromhex(workload['command-' + str(phase) + '.sh'])
        sent = 0
        for write in event['writes']:
            requested = bytes.fromhex(write['requested_hex'])
            accepted = write['accepted']
            need(write['offset'] == sent and 0 < accepted <= len(requested)
                 and requested == command[sent:sent + len(requested)], 'exact input fragments')
            sent += accepted
        need(sent == len(command) and len(event['writes']) >= 2, 'complete fragmented input')
        need(event['delay_seconds'] >= (35 if record['label'] == 'delayed' and phase == 1
                                       else 2 if record['label'] == 'delayed' else 0), 'input delay')
        offset += len(bytes.fromhex(exchange['steps'][i]['expected_uart_after_input_hex']))
    ticks, idle, reclaims = halt[0][0]
    need((ticks, idle, reclaims) == (record['ticks'], record['idle'], record['reclaims'])
         and reclaims == len(expected_terminal), 'halt receipt agreement')
    if record['label'] == 'delayed':
        need(ticks > 3000 and idle > 3000, 'idle witness')
    if polling:
        need(ticks < 3000, 'old polling exhausted before delayed input')
    need(record['cleanup'] == 'emulator-reaped', 'emulator cleanup')
    return {'uart_bytes': len(uart), 'terminals': len(terminal), 'admissions': len(admitted)}


