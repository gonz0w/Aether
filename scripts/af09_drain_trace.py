# SPDX-License-Identifier: BSD-2-Clause
"""Decode prospective AF09 trace rows; parsing is not native qualification."""
from dataclasses import dataclass
import re

CASES = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
         'partial_ack', 'exit_deadline', 'pending_fragment')
FIELDS = ('case', 'row', 'phase', 'slot', 'gen', 'seq', 'tick', 'deadline',
          'status', 'count', 'aux')
PHASES = frozenset(range(1, 30)) | {255}
SINGLETONS = frozenset((1, 2, 3, 4, 5, 7, 8, 9, 13, 16, 20, 21, 22, 23, 27, 28))
U64_MAX = (1 << 64) - 1
CAPTURE_LIMIT = 65536
TRACE_LIMIT = 32768
LINE_LIMIT = 256
_UNSIGNED = rb'(?:0|[1-9][0-9]*)'
_SIGNED = rb'(?:0|-?[1-9][0-9]*)'
_PATTERN = re.compile(b'AF09-DRAIN v=1 ' + b' '.join(
    name.encode('ascii') + b'=(' + (_SIGNED if name == 'status' else _UNSIGNED) + b')'
    for name in FIELDS) + b'\n')


@dataclass(frozen=True)
class Row:
    case: int
    row: int
    phase: int
    slot: int
    gen: int
    seq: int
    tick: int
    deadline: int
    status: int
    count: int
    aux: int


@dataclass(frozen=True)
class Trace:
    rows: tuple[Row, ...]
    unparsed: tuple[bytes, ...]


def parse_trace(capture: bytes, selection: str) -> Trace:
    """Retain other UART bytes verbatim; never promote row suffixes to records.

    A caller still needs artifact association and phase-specific native oracles.
    This function deliberately returns no qualification or execution verdict.
    """
    if selection not in CASES:
        raise ValueError('unknown AF09 selection')
    if not isinstance(capture, bytes) or len(capture) > CAPTURE_LIMIT:
        raise ValueError('AF09 capture type or limit')
    expected_case = CASES.index(selection) + 1
    rows, unparsed = [], []
    seen, generations = set(), {}
    trace_bytes = 0
    # splitlines would silently accept CR/other line separators in machine rows.
    parts = capture.split(b'\n')
    for index, part in enumerate(parts):
        if index == len(parts) - 1 and not part:
            continue
        line = part + (b'\n' if index < len(parts) - 1 else b'')
        if not line.startswith(b'AF09-DRAIN'):
            unparsed.append(line)
            continue
        trace_bytes += len(line)
        if len(line) > LINE_LIMIT or trace_bytes > TRACE_LIMIT - LINE_LIMIT:
            raise ValueError('AF09 diagnostic budget')
        match = _PATTERN.fullmatch(line)
        if match is None:
            raise ValueError('AF09 row grammar')
        values = tuple(int(value) for value in match.groups())
        for name, value in zip(FIELDS, values):
            low, high = (-(1 << 63), (1 << 63) - 1) if name == 'status' else (0, U64_MAX)
            if not low <= value <= high:
                raise ValueError('AF09 numeric range: ' + name)
        row = Row(*values)
        if row.case != expected_case or row.row != len(rows):
            raise ValueError('AF09 case or row sequence')
        if row.phase not in PHASES or row.slot > 6:
            raise ValueError('AF09 phase or slot')
        if row.phase in (29, 255):
            raise ValueError('AF09 failure or overflow')
        if not rows and row.phase != 1:
            raise ValueError('AF09 missing begin')
        if row.phase in SINGLETONS:
            if row.phase in seen:
                raise ValueError('AF09 duplicate singleton')
            seen.add(row.phase)
        if rows and row.tick < rows[-1].tick:
            raise ValueError('AF09 tick regression')
        previous = generations.setdefault(row.slot, row.gen)
        if previous != row.gen:
            raise ValueError('AF09 generation changed')
        rows.append(row)
    if not rows:
        raise ValueError('AF09 missing trace')
    return Trace(tuple(rows), tuple(unparsed))
