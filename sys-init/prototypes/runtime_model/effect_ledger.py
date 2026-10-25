# SPDX-License-Identifier: BSD-2-Clause
"""Trusted effect accounting only; no invocation or lifecycle observation."""
from collections import OrderedDict
import re

from .control import MAX_ID


class InvalidEffect(ValueError):
    pass


class EffectLedger:
    def __init__(self, *, epoch, revision, services):
        for value in (epoch, revision):
            if type(value) is not str or not 1 <= len(value) <= 64:
                raise InvalidEffect('identity')
        if type(services) not in (list, tuple) or not 1 <= len(services) <= 8:
            raise InvalidEffect('services')
        if any(type(n) is not str or len(n) > 32 or not re.fullmatch(r'[a-z][a-z0-9_-]{0,31}', n) for n in services):
            raise InvalidEffect('services')
        if len(set(services)) != len(services):
            raise InvalidEffect('services')
        self.epoch, self.revision = epoch, revision
        self.seen = {name: (0, frozenset()) for name in services}
        self.next_id = 1
        self.live = {}
        self.history = OrderedDict()
        self.closed = False

    def _open(self):
        if self.closed:
            raise InvalidEffect('driver closed')

    @staticmethod
    def _id(value):
        if type(value) is not int or not 1 <= value <= MAX_ID:
            raise InvalidEffect('identity')

    def reserve(self, operation, effects):
        self._open()
        self._id(operation)
        if type(effects) not in (list, tuple) or not 1 <= len(effects) <= 8:
            raise InvalidEffect('batch')
        if len(self.live) + len(effects) > 8 or self.next_id + len(effects) - 1 > MAX_ID:
            raise InvalidEffect('capacity')
        seen = self.seen.copy()
        tokens = []
        for effect in effects:
            if type(effect) not in (list, tuple) or len(effect) != 3:
                raise InvalidEffect('effect')
            kind, name, generation = effect
            if type(kind) is not str or kind not in ('launch', 'stop', 'reclaim'):
                raise InvalidEffect('kind')
            if type(name) is not str or len(name) > 32 or name not in seen:
                raise InvalidEffect('service')
            self._id(generation)
            previous, kinds = seen[name]
            if generation < previous or (generation == previous and kind in kinds):
                raise InvalidEffect('retired effect')
            if generation > previous:
                if any(t[4] == name for t, _ in self.live.values()) or any(t[4] == name for t in tokens):
                    raise InvalidEffect('unresolved generation')
                kinds = frozenset()
            seen[name] = (generation, kinds | {kind})
            tokens.append((self.epoch, self.revision, self.next_id + len(tokens),
                           operation, name, generation, kind))
        records = {token[2]: (token, 'reserved') for token in tokens}
        self.live.update(records)
        self.seen = seen
        self.next_id += len(tokens)
        return tuple(tokens)

    def _lookup(self, token):
        if type(token) is not tuple or len(token) != 7:
            raise InvalidEffect('token')
        for index in (2, 3, 5):
            self._id(token[index])
        for index, bound in ((0, 64), (1, 64), (4, 32), (6, 7)):
            if type(token[index]) is not str or not 1 <= len(token[index]) <= bound:
                raise InvalidEffect('token')
        if token[:2] != (self.epoch, self.revision):
            raise InvalidEffect('token')
        record = self.live.get(token[2], self.history.get(token[2]))
        if record is not None and record[0] != token:
            raise InvalidEffect('token mismatch')
        return record

    def issue(self, token):
        self._open()
        record = self._lookup(token)
        if record is None or record[1] != 'reserved':
            raise InvalidEffect('not reserved')
        self.live[token[2]] = (token, 'issued')
        return token

    def _finish(self, token, outcome):
        self.history[token[2]] = (token, outcome)
        self.live.pop(token[2])
        if len(self.history) > 64:
            self.history.popitem(last=False)

    def acknowledge(self, token, outcome):
        self._open()
        if type(outcome) is not str or outcome not in ('executed', 'rejected-before-effects', 'unknown'):
            raise InvalidEffect('outcome')
        record = self._lookup(token)
        if record is None:
            if token[2] < self.next_id:
                return 'retired'
            raise InvalidEffect('unknown token')
        state = record[1]
        if state in ('executed', 'rejected-before-effects', 'unknown'):
            if state != outcome:
                raise InvalidEffect('acknowledgment conflict')
            return 'replayed'
        if state == 'reserved' and outcome != 'rejected-before-effects':
            raise InvalidEffect('not issued')
        if outcome == 'unknown':
            self.live[token[2]] = (token, outcome)
        else:
            self._finish(token, outcome)
        return 'recorded'

    def observe(self, token):
        record = self._lookup(token)
        return record[1] if record else 'unknown'

    def driver_lost(self):
        self.closed = True
        for token, state in tuple(self.live.values()):
            if state == 'reserved':
                self._finish(token, 'rejected-before-effects')
            else:
                self.live[token[2]] = (token, 'unknown')
