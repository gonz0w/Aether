# SPDX-License-Identifier: BSD-2-Clause
"""Isolated logical event accounting; no lifecycle mutation or native execution."""
from collections import OrderedDict

from .control import MAX_ID
from .effect_ledger import EffectLedger, InvalidEffect


class EventJournal:
    def __init__(self, *, epoch, revision, services):
        checked = EffectLedger(epoch=epoch, revision=revision, services=services)
        self.epoch, self.revision = epoch, revision
        self.generations = dict.fromkeys(checked.seen, 0)
        self.next_cut = 1
        self.ticket = None
        self.phase = None
        self.credits = 0
        self.raw = ()
        self.live = {}
        self.history = OrderedDict()
        self.closed = False

    def _open(self):
        if self.closed:
            raise InvalidEffect('journal closed')

    def reserve(self):
        self._open()
        if self.ticket is not None or self.live or self.next_cut > MAX_ID:
            raise InvalidEffect('cut capacity')
        self.ticket = object()
        self.phase, self.credits, self.raw = 'reserved', 20, ()
        self.next_cut += 1
        return self.ticket

    def _ticket(self, ticket, phase):
        self._open()
        if ticket is not self.ticket or self.ticket is None or self.phase != phase:
            raise InvalidEffect('reservation')

    def cancel(self, ticket):
        self._ticket(ticket, 'reserved')
        self.ticket, self.phase, self.credits = None, None, 0

    def begin(self, ticket):
        self._ticket(ticket, 'reserved')
        self.phase = 'recording'

    def _record(self, record):
        if type(record) is not tuple or len(record) != 5:
            raise InvalidEffect('record')
        kind, name, generation, cause, operation = record
        if type(kind) is not str or kind not in ('launch', 'stop', 'force', 'reclaim'):
            raise InvalidEffect('kind')
        if type(name) is not str or name not in self.generations:
            raise InvalidEffect('service')
        EffectLedger._id(generation)
        EffectLedger._id(operation)
        if type(cause) is not str or cause not in ('activation', 'stop'):
            raise InvalidEffect('cause')

    def capture(self, ticket, records):
        self._ticket(ticket, 'recording')
        try:
            if type(records) is not tuple or len(records) > 20:
                raise InvalidEffect('cut bound')
            generations = self.generations.copy()
            for record in records:
                self._record(record)
                _, name, generation, _, _ = record
                if generation < generations[name]:
                    raise InvalidEffect('retired generation')
                generations[name] = generation
            self.raw = records
            tokens = tuple(('event-effect-v1', self.epoch, self.revision,
                            self.next_cut - 1, index, name, generation, kind, cause, operation)
                           for index, (kind, name, generation, cause, operation) in enumerate(records))
            self.live = {t[3:5]: (t, 'reserved') for t in tokens}
            self.generations = generations
            self.ticket, self.phase, self.credits = None, None, 0
            return tokens
        except BaseException:
            self.closed = True
            raise

    def _lookup(self, token):
        if type(token) is not tuple or len(token) != 10:
            raise InvalidEffect('token')
        if any(type(v) is not str for v in token[:3]) or token[:3] != ('event-effect-v1', self.epoch, self.revision):
            raise InvalidEffect('token')
        EffectLedger._id(token[3])
        if type(token[4]) is not int or not 0 <= token[4] < 20:
            raise InvalidEffect('index')
        self._record((token[7], token[5], token[6], token[8], token[9]))
        key = token[3:5]
        record = self.live.get(key, self.history.get(key))
        if record is not None and record[0] != token:
            raise InvalidEffect('token mismatch')
        if record is None and token[3] >= self.next_cut:
            raise InvalidEffect('future cut')
        return record

    def issue(self, token):
        self._open()
        record = self._lookup(token)
        if record is None or record[1] != 'reserved':
            raise InvalidEffect('not reserved')
        self.live[token[3:5]] = (token, 'issued')
        return token

    def _finish(self, token, outcome):
        key = token[3:5]
        self.history[key] = (token, outcome)
        self.live.pop(key)
        if len(self.history) > 64:
            self.history.popitem(last=False)

    def acknowledge(self, token, outcome):
        self._open()
        if type(outcome) is not str or outcome not in ('executed', 'rejected-before-effects', 'unknown'):
            raise InvalidEffect('outcome')
        record = self._lookup(token)
        if record is None:
            return 'retired'
        state = record[1]
        if state in ('executed', 'rejected-before-effects', 'unknown'):
            if state != outcome:
                raise InvalidEffect('acknowledgment conflict')
            return 'replayed'
        if state == 'reserved' and outcome != 'rejected-before-effects':
            raise InvalidEffect('not issued')
        if outcome == 'unknown':
            self.live[token[3:5]] = (token, outcome)
        else:
            self._finish(token, outcome)
        return 'recorded'

    def observe(self, token):
        record = self._lookup(token)
        return record[1] if record else 'unknown'

    def driver_lost(self):
        self.closed = True
        if self.phase == 'reserved':
            self.ticket, self.phase, self.credits = None, None, 0
        for token, state in tuple(self.live.values()):
            if state == 'reserved':
                self._finish(token, 'rejected-before-effects')
            else:
                self.live[token[3:5]] = (token, 'unknown')
