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


def validate_witness(capture: bytes, selection: str, admission: dict) -> dict:
    """Check a prospective complete writer transcript after artifact association.

    The caller must first bind the supplied bytes to the selected prepared image
    and measured admission. This validates observations, not guest execution or
    filesystem durability. Clean cases still require an independent cold reader.
    """
    trace = parse_trace(capture, selection)
    rows = trace.rows
    by_phase = {phase: [r for r in rows if r.phase == phase] for phase in PHASES}

    def require(ok, message):
        if not ok:
            raise ValueError('AF09 witness ' + message)

    def one(phase):
        require(len(by_phase[phase]) == 1, 'missing/duplicate phase ' + str(phase))
        return by_phase[phase][0]

    def before(left, right):
        require(left.row < right.row, 'causal ordering')

    negative = CASES.index(selection) >= 4
    require(isinstance(admission, dict)
            and set(admission) == {'engine_pages', 'shell_pages', 'helper_pages', 'owner_bytes'}
            and all(type(value) is int for value in admission.values()), 'measured geometry shape')
    require(16 < admission['engine_pages'] <= 2048
            and 16 < admission['shell_pages'] <= 128
            and 16 < admission['helper_pages'] <= 128
            and 0 < admission['owner_bytes'] <= 49152, 'measured geometry limits')
    slots = {1: (6,), 2: (2,), 3: (2,), 4: (2,), 5: (1,), 6: (2,),
             7: (1,), 8: (1,), 9: (6,), 10: (6,), 11: (6,), 12: (2,),
             13: (2,), 14: (2,), 15: (0, 1, 2), 16: (0,), 17: (0,),
             18: (6,), 19: (6,), 20: (0,), 21: (0,), 22: (0,),
             23: (6,), 24: (0, 2, 6), 25: (0, 2), 26: (6,), 27: (2,), 28: (1,)}
    for r in rows:
        require(r.slot in slots[r.phase] and r.gen == (0 if r.slot == 6 else 1), 'domain identity')
        if r.phase not in (8, 11, 13, 16, 19, 24):
            require(r.status == 0, 'unexpected status')
        if r.phase not in (2, 3, 6, 12, 13, 16, 17, 18, 22, 25, 27, 28):
            require(r.count == 0, 'reserved count')
        if r.phase not in (8, 13, 16, 19, 22, 24, 25, 26):
            require(r.aux == 0, 'reserved aux')
    begin, copy, startup, ready, query = (one(p) for p in (1, 2, 3, 4, 5))
    parent, positive, observed = (one(p) for p in (7, 8, 9))
    disposed, counter, retained = (one(p) for p in (13, 16, 22))
    wire, disposition = one(27), one(28)
    require(copy.count == 1 and startup.count == 304 and wire.count == disposition.count == 32,
            'copy/startup/publication ledger')
    for left, right in ((begin, copy), (copy, startup), (startup, ready),
                        (startup, wire), (wire, disposition), (disposition, query),
                        (disposition, parent), (ready, positive), (query, positive),
                        (parent, positive), (positive, observed), (observed, disposed),
                        (disposed, counter)):
        before(left, right)
    # Native READY can precede the owner's wire READY consumption.
    require((positive.status, positive.aux) == (1, 1), 'actual parent query')
    late = by_phase[6]
    require([r.count for r in late] == [16, 32] and not by_phase[12], 'unread exact late prefix')
    for r in late:
        before(ready, r); before(query, r); before(r, positive)
    require((disposed.status, disposed.count, disposed.aux) == (0, 32, 0), 'queue disposal')
    stop = one(14)
    before(observed, stop); before(stop, counter)
    reclaims = by_phase[15]
    require([r.slot for r in reclaims] == ([2, 1] if negative else [2, 1, 0]), 'reclaim order/retained engine')
    for r in reclaims[:2]:
        before(stop, r); before(r, counter)
    require((counter.status, counter.count, counter.aux) == (8, 2, 3), 'actual pre-ACK counters')
    t0, deadline = observed.tick, observed.deadline
    require(t0 <= 5400 and deadline == t0 + 500 and deadline <= 5900, 'fixed drain window')
    require(all(r.deadline == (0 if r.row < observed.row else deadline) for r in rows), 'deadline renewal')
    require(all(r.tick < deadline for r in rows if r.phase in (16, 17, 20)), 'late engine activity')
    writes, reads = by_phase[17], by_phase[18]
    expected = 0 if selection == 'no_ack' else 48 if selection == 'partial_ack' else 16 if selection == 'pending_fragment' else 64
    require([r.count for r in writes] == list(range(16, expected + 1, 16)), 'ACK write ledger')
    read_expected = 0 if selection in ('no_ack', 'pending_fragment') else expected
    require([r.count for r in reads] == list(range(16, read_expected + 1, 16)), 'ACK read ledger')
    for r in writes:
        before(counter, r)
    for r in reads:
        matching = next(w for w in writes if w.count == r.count)
        before(matching, r)
    closes = by_phase[19]
    require(len(closes) == 2 and [r.aux for r in closes] == [0, 1]
            and all(r.status == 0 for r in closes), 'actual both source-close results')
    before(counter, closes[0]); before(closes[0], closes[1]); before(closes[1], retained)
    require((retained.count, retained.aux) == (1, 1), 'admitted backing at source close')
    # Completed holds are causal facts, not scheduler intent.
    holds = by_phase[25]
    require(all(r.count in (1, 2, 3, 4) and r.aux in (0, 1) for r in holds), 'hold identity')
    child_holds = [r for r in holds if r.slot == 2]
    require([(r.count, r.aux) for r in child_holds] == [(1, 0), (1, 1)], 'child hold/release')
    before(child_holds[0], ready); before(query, child_holds[1]); before(child_holds[1], late[0])
    engine_holds = [r for r in holds if r.slot == 0]
    wanted_holds = ([(2, 0)] if selection == 'no_ack' else
                    [(3, 0), (3, 1), (3, 0), (3, 1), (3, 0)] if selection == 'partial_ack' else
                    [(4, 0)] if selection == 'exit_deadline' else
                    [(2, 0), (2, 1), (3, 0)] if selection == 'pending_fragment' else [])
    require([(r.count, r.aux) for r in engine_holds] == wanted_holds, 'engine hold/release ledger')
    if selection == 'partial_ack':
        require([r.tick for r in engine_holds if r.aux == 1] == [t0 + 100, t0 + 200], 'fixed ACK releases')
        for w, hold in zip(writes, [r for r in engine_holds if r.aux == 0]):
            before(w, hold)
        require(writes[0].tick < t0 + 100 <= writes[1].tick < t0 + 200 <= writes[2].tick < deadline,
                'partial ACK timing')
    parks, completions = by_phase[10], by_phase[11]
    require(len(parks) == len(completions), 'park completion coverage')
    for park, completion in zip(parks, completions):
        before(observed, park); before(park, completion)
        require(completion.status in (0, -110) and completion.seq >= park.seq
                and completion.tick >= park.tick, 'actual park completion')
    for completion, next_park in zip(completions, parks[1:]):
        before(completion, next_park)
    if negative:
        require(parks and completions[-1].status == -110 and completions[-1].tick == deadline,
                'actual deadline completion')
        require(all(c.status == 0 and c.tick < deadline for c in completions[:-1]), 'early deadline completion')
        require(any(r.status == -11 and r.slot == 6 and r.aux == 6
                    and observed.row < r.row < parks[-1].row for r in by_phase[24])
                if selection in ('no_ack', 'pending_fragment') else
                any(r.status == -11 and observed.row < r.row < parks[-1].row for r in by_phase[24]),
                'actual EAGAIN before park')
        before(completions[-1], closes[0])
        require(not by_phase[21] and not by_phase[23] and rows[-1] == retained, 'false clean completion')
    else:
        terminal, halt, exit_trap = one(21), one(23), one(20)
        require(all(c.status == 0 for c in completions), 'clean deadline completion')
        before(writes[-1], exit_trap); before(exit_trap, terminal)
        before(reads[-1], closes[0]); before(terminal, closes[0])
        before(retained, reclaims[-1]); before(reclaims[-1], halt)
        require(rows[-1] == halt and halt.tick < deadline, 'complete clean boundary')
    if selection == 'exit_deadline':
        exit_trap = one(20)
        before(writes[-1], exit_trap); before(exit_trap, engine_holds[0]); before(engine_holds[0], completions[-1])
    elif negative:
        require(not by_phase[20], 'unexpected normal exit')
    if selection == 'pending_fragment':
        deferred = by_phase[26]
        require(len(deferred) == 2 and [r.aux for r in deferred] == [0, 1], 'deferred registration')
        captured, registered = deferred
        before(parks[-1], captured); before(captured, writes[0]); before(writes[0], registered)
        before(registered, completions[-1])
        require(captured.seq == registered.seq == parks[-1].seq
                and captured.tick <= writes[0].tick < deadline
                and registered.tick == deadline and writes[0].seq > captured.seq,
                'real pending fragment before deadline')
    else:
        require(not by_phase[26], 'unexpected deferred park')
    for r in by_phase[24]:
        require(r.status == -11 and r.aux in range(1, 7), 'EAGAIN direction/status')
    _writer_uart(trace, capture, negative, admission)
    return dict(format='aether-af09-drain-writer-transcript-v1', case=selection,
                status='pass', native_executed=False, provider_attempts=2,
                service_requests=3, late_consumed=0, late_discarded=32,
                clean_halt=not negative, engine_retained=negative,
                scope='Supplied transcript oracle only; artifact association, execution and cold recovery are separate')


def _writer_uart(trace, capture, negative, admission):
    """Preserve ordinary admission/terminal/cleanup/emergency machine contracts."""
    raw = b''.join(trace.unparsed)
    try:
        text = raw.decode('ascii')
    except UnicodeDecodeError as error:
        raise ValueError('AF09 witness non-ASCII UART') from error
    if '\x00' in text or '\x1b' in text or '\r' in text:
        raise ValueError('AF09 witness malformed UART')
    lines = text.splitlines()

    def exact(prefix, pattern):
        result = []
        for line in lines:
            if not line.startswith(prefix):
                continue
            match = re.fullmatch(pattern, line)
            if match is None:
                raise ValueError('AF09 witness malformed ' + prefix)
            result.append(tuple(map(int, match.groups())))
        return result

    admitted = exact('NATIVE MEMORY admitted', r'NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)')
    wanted = [(i, 1, admission[name], capacity - admission[name]) for i, name, capacity in
              ((0, 'engine_pages', 8192), (1, 'shell_pages', 128))]
    if admitted != wanted:
        raise ValueError('AF09 witness exact measured admission')
    terminals = exact('NATIVE terminal', r'NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)')
    if terminals != [(1, 1, 1, 0), (2, 1, 3, 143)] + ([] if negative else [(0, 1, 1, 0)]):
        raise ValueError('AF09 witness exact terminal identities/status')
    observations = exact('NATIVE observation', r'NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)')
    if observations != [(0, 1, 0, 1)]:
        raise ValueError('AF09 witness exact existing counter observation')
    cleanup = exact('NATIVE CLEANUP', r'NATIVE CLEANUP v=1 slot=(\d+) generation=(\d+) phase=(\d+) selected=(\d+) pages=(\d+) reclaimed=(\d+)')
    # Parent terminal cleanup1/2 precedes child stop. The stop API retires the
    # child contexts directly; its reclaim still executes actual phases3..7.
    wanted_cleanup = [(1, 1, p, 1 if p == 1 else 6, 128, 0) for p in (1, 2)]
    wanted_cleanup += [(2, 1, p, 6, 128, int(p == 7)) for p in range(3, 8)]
    wanted_cleanup += [(1, 1, p, 6, 128, 1 + int(p == 7)) for p in range(3, 8)]
    if not negative:
        wanted_cleanup += [(0, 1, p, 0 if p == 1 else 6, 8192, 2 + int(p == 7)) for p in range(1, 8)]
    if len(cleanup) != len(wanted_cleanup):
        raise ValueError('AF09 witness complete ordinary cleanup')
    for actual, wanted in zip(cleanup, wanted_cleanup):
        # A deferred owner query can leave engine/child selected after parent
        # retirement; phase2 names the real selected runnable domain.
        if wanted[:3] == (1, 1, 2):
            if actual[:3] != wanted[:3] or actual[3] not in (0, 2, 6) or actual[4:] != wanted[4:]:
                raise ValueError('AF09 witness parent rotate cleanup')
        elif actual != wanted:
            raise ValueError('AF09 witness complete ordinary cleanup')
    halts = exact('NATIVE init halted', r'NATIVE init halted ticks=(\d+) idle=(\d+) reclaimed=(\d+)')
    panic = 'AETHER PANIC: native supervisor terminated'
    if negative:
        if (halts or 'AETHER NATIVE BLOCK PASS' in lines or not text.endswith(panic + '\n')
                or lines.count(panic) != 1
                or len([line for line in lines if line.startswith('NATIVE fault ')]) != 1
                or not any(re.fullmatch(r'NATIVE fault vector=6 rip=[0-9a-f]+ error=0', line) for line in lines)):
            raise ValueError('AF09 witness complete retained failure boundary')
        if any('PANIC' in line and line != panic and re.fullmatch(r'NATIVE PANIC pc=[0-9a-f]+', line) is None for line in lines):
            raise ValueError('AF09 witness unrelated panic')
    elif (len(halts) != 1 or halts[0][2] != 3 or not 0 < halts[0][0] <= 6000
          or not text.endswith('AETHER NATIVE BLOCK PASS\n')
          or lines.count('AETHER NATIVE BLOCK PASS') != 1 or 'PANIC' in text or 'NATIVE fault ' in text):
        raise ValueError('AF09 witness complete clean UART')
    full_lines = capture.decode('ascii').splitlines()
    def position(line):
        if full_lines.count(line) != 1:
            raise ValueError('AF09 witness duplicate/missing ordinary boundary')
        return full_lines.index(line)
    def typed_position(row):
        return position('AF09-DRAIN v=1 ' + ' '.join(f'{name}={getattr(row, name)}' for name in FIELDS))
    counter = next(r for r in trace.rows if r.phase == 16)
    if position('NATIVE observation slot=0 generation=1 offset=0 byte=1') >= typed_position(counter):
        raise ValueError('AF09 witness counter observation/typed boundary order')
    for slot, kind, detail, phase in ((1, 1, 0, 7), (2, 3, 143, 14), (0, 1, 0, 21)):
        if negative and slot == 0:
            continue
        typed = next(r for r in trace.rows if r.phase == phase)
        marker = f'NATIVE terminal slot={slot} generation=1 kind={kind} detail={detail}'
        if position(marker) >= typed_position(typed):
            raise ValueError('AF09 witness terminal/typed boundary order')
    for row in (r for r in trace.rows if r.phase == 15):
        marker = next(line for line in lines if line.startswith(f'NATIVE CLEANUP v=1 slot={row.slot} generation=1 phase=7 '))
        if position(marker) >= typed_position(row):
            raise ValueError('AF09 witness reclaim/typed boundary order')
    if not negative:
        halt = next(r for r in trace.rows if r.phase == 23)
        if halts[0][0] != halt.tick or halts[0][1] > halt.tick:
            raise ValueError('AF09 witness halt tick/idle consistency')
        if not position(next(line for line in lines if line.startswith('NATIVE init halted '))) < typed_position(halt) < position('AETHER NATIVE BLOCK PASS'):
            raise ValueError('AF09 witness halt/typed boundary order')
    if any(line.startswith(('AF07-', 'AF09-BEGIN', 'AF09-HOME-', 'AF09-STATUS:',
                            'NATIVE supervisor')) for line in lines):
        raise ValueError('AF09 witness substituted old workload/observations')
