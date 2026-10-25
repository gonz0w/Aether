# SPDX-License-Identifier: BSD-2-Clause
"""Bounded trusted observation intake; retention is not reconciliation."""
from collections import deque

from .control import MAX_ID
from .effect_ledger import InvalidEffect
from .model import Rejected
from .journal_runtime import JournalRuntime


class QueuedRuntime(JournalRuntime):
    def __init__(self, services, **identity):
        super().__init__(services, **identity)
        self.inbox = deque()
        self.next_intake = 1
        self.accepted_time = self.model.now
        self.intake_lost = False

    def _available(self):
        if self.failed or self.running or self.journal.closed:
            raise InvalidEffect('owner closed or busy')

    def batch(self, events=(), *, now=None):
        self._available()
        floor = max(self.accepted_time, self.model.now)
        now = self.model._validate_batch(events, floor if now is None else now)
        if now < floor:
            raise Rejected('intake clock')
        for kind, name, generation, epoch, value in events:
            if (any(type(v) is not str for v in (kind, name, epoch))
                    or generation > MAX_ID
                    or (type(value) is int and not -(1 << 63) <= value < (1 << 63))
                    or type(value) not in (int, str)):
                raise Rejected('retained payload bound')
        queued = sum(max(1, len(cut[2])) for cut in self.inbox)
        if self.model.events + queued + max(1, len(events)) > self.model.MAX_EVENTS:
            raise Rejected('event bound')
        if self.next_intake > MAX_ID:
            raise InvalidEffect('intake exhausted')
        frozen = tuple(tuple(event) for event in events)
        if len(self.inbox) >= 4:
            self.intake_lost = True
            self.driver_lost()
            raise InvalidEffect('observation capacity lost')
        serial = self.next_intake
        next_serial = serial + 1
        self.inbox.append((serial, now, frozen))
        self.next_intake = next_serial
        self.accepted_time = now
        return serial

    def peek(self):
        return self.inbox[0] if self.inbox else None

    def apply_next(self):
        self._available()
        if not self.inbox or self.journal.live or self.journal.ticket is not None:
            return None
        serial, now, events = self.inbox[0]
        super().batch(events, now=now)
        self.inbox.popleft()
        return serial

    def _command(self):
        self._available()
        if self.inbox:
            raise InvalidEffect('observations pending')

    def start(self, names, budget=100):
        self._command()
        return super().start(names, budget)

    def stop(self, names, budget=100, *, shutdown=False, restart=None):
        self._command()
        return super().stop(names, budget, shutdown=shutdown, restart=restart)
