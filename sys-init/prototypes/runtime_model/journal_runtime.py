# SPDX-License-Identifier: BSD-2-Clause
"""Trusted lifecycle owner with logical cut accounting; no native invocation."""
from .model import Model, Rejected
from .control import MAX_ID
from .effect_ledger import InvalidEffect
from .event_journal import EventJournal


class _OwnedModel(Model):
    def __init__(self, owner, services, **identity):
        super().__init__(services, **identity)
        self.owner = owner

    def _begin(self, count=1):
        if self.events + count > self.MAX_EVENTS:
            raise Rejected('event bound')
        self.owner._admit()
        super()._begin(count)

    def _operation(self, kind, scope, budget, restart=None, shutdown=False):
        if self.next_id > MAX_ID:
            raise InvalidEffect('operation exhausted')
        op = super()._operation(kind, scope, budget, restart, shutdown)
        for name in scope:
            state = self.state[name]
            if kind == 'stop':
                self.owner.causes[name] = ('stop', op.id)
            elif not state.owned and state.phase != 'retry' and not state.completed:
                self.owner.causes[name] = ('activation', op.id)
        return op

    def _launch(self, name, replacement=False):
        if self.state[name].generation >= MAX_ID:
            raise InvalidEffect('generation exhausted')
        cause = self.owner.causes[name]
        if cause is None:
            raise InvalidEffect('missing cause')
        self.owner.causes[name] = ('activation', cause[1])
        super()._launch(name, replacement)

    def _effect(self, action, name):
        super()._effect(action, name)
        cause = self.owner.causes[name]
        if cause is None or len(self.owner.attributed) >= 20:
            raise InvalidEffect('effect accounting')
        self.owner.attributed.append((action, name, self.state[name].generation, *cause))


class JournalRuntime:
    def __init__(self, services, **identity):
        self.model = _OwnedModel(self, services, **identity)
        self.journal = EventJournal(epoch=self.model.epoch, revision=self.model.revision,
                                    services=list(self.model.spec))
        self.causes = dict.fromkeys(self.model.spec)
        self.attributed = []
        self.pending = ()
        self.ticket = None
        self.failed = False
        self.running = False
        self.prepared = None
        self.consuming = None

    def _admit(self):
        self.ticket = self.prepared if self.prepared is not None else self.journal.reserve()
        self.journal.begin(self.ticket)
        self.attributed = []

    def _run(self, method, *args, **kwargs):
        if self.failed or self.running or (self.prepared is not None and self.consuming is None):
            raise InvalidEffect('owner closed or busy')
        self.running = True
        try:
            result = method(*args, **kwargs)
            self.pending = self.journal.capture(self.ticket, tuple(self.attributed))
            self.ticket = None
            return result
        except BaseException:
            if self.ticket is not None:
                self.driver_lost()
            raise
        finally:
            self.running = False

    def start(self, names, budget=100):
        operation, _ = self._run(self.model.start, names, budget)
        return operation

    def stop(self, names, budget=100, *, shutdown=False, restart=None):
        operation, _ = self._run(self.model.stop, names, budget,
                                 shutdown=shutdown, restart=restart)
        return operation

    def batch(self, events=(), *, now=None):
        self._run(self.model.batch, events, now=now)

    def issue_obligations(self):
        if self.failed or self.journal.closed:
            raise InvalidEffect('owner closed')
        if any(self.journal.observe(t) != 'reserved' for t in self.pending):
            raise InvalidEffect('not reserved')
        tokens = self.pending
        try:
            for token in tokens:
                self.journal.issue(token)
        except BaseException:
            self.driver_lost()
            raise
        self.pending = ()
        return tokens

    def acknowledge(self, token, outcome):
        return self.journal.acknowledge(token, outcome)

    def driver_lost(self):
        self.failed = True
        self.journal.driver_lost()

    def reserve_batch(self):
        if type(self) is not JournalRuntime:
            raise InvalidEffect('reserved batch runtime profile')
        if self.failed or self.running or self.prepared is not None or self.ticket is not None:
            raise InvalidEffect('owner closed or busy')
        self.prepared = self.journal.reserve()
        return self.prepared

    def cancel_batch(self, ticket):
        if self.failed or self.running or ticket is not self.prepared or ticket is None:
            raise InvalidEffect('prepared ticket')
        self.journal.cancel(ticket)
        self.prepared = None

    def batch_reserved(self, ticket, events):
        if self.failed or self.running or ticket is not self.prepared or ticket is None:
            raise InvalidEffect('prepared ticket')
        self.consuming = ticket
        try:
            self.batch(events, now=self.model.now)
        except BaseException:
            self.driver_lost()
            raise
        else:
            self.prepared = None
        finally:
            self.consuming = None
