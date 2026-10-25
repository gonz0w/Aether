# SPDX-License-Identifier: BSD-2-Clause
"""Launched-only real policy-model/journal adapter; Source origin remains synthetic."""
from .cut_coordinator import CutError, Receipt, Source
from .journal_runtime import JournalRuntime


class LaunchedAdapter:
    def __init__(self, runtime, owner, bindings):
        if (type(runtime) is not JournalRuntime or len(runtime.model.spec) > 2
                or type(bindings) is not tuple or not 1 <= len(bindings) <= 2):
            raise CutError('adapter profile')
        self.runtime, self.owner = runtime, owner
        self.names = tuple(sorted(runtime.model.spec))
        self.epoch, self.revision = runtime.model.epoch, runtime.model.revision
        # Each token position has its own fixed symbolic domain, never a hash.
        self.bindings = bindings
        if len({s.attempt for s, _ in bindings}) != len(bindings):
            raise CutError('duplicate attempt')
        for source, token in bindings:
            self._source(source, token)
        self.serial = None
        self.ticket = None
        self.captured = None

    def encoded(self, token):
        if (type(token) is not tuple or len(token) != 10
                or token[:3] != ('event-effect-v1', self.epoch, self.revision)
                or token[5] not in self.names or token[7] != 'launch'
                or token[8] != 'activation'):
            raise CutError('launch token')
        if any(type(token[i]) is not int for i in (3, 4, 6, 9)):
            raise CutError('launch scalar')
        return (1, 2, 3, token[3], token[4], self.names.index(token[5]) + 4,
                token[6], 6, 7, token[9])

    @property
    def phases(self):
        return tuple(int(self.runtime.model.state[n].started) for n in self.names) + (0,) * (2 - len(self.names))

    def _source(self, source, token):
        if (type(source) is not Source or source.owner is not self.owner
                or type(source.attempt) is not int or not 0 <= source.attempt < len(self.names)
                or type(source.phase) is not int or source.phase != 1
                or type(source.token) is not tuple or len(source.token) != 10
                or any(type(v) is not int for v in source.token)
                or type(source.content) is not tuple or source.content != (0,)
                or type(source.content[0]) is not int
                or source.token != self.encoded(token)
                or self.names[source.attempt] != token[5]
                or self.runtime.model.epoch != self.epoch or self.runtime.model.revision != self.revision
                or self.runtime.journal.observe(token) != 'executed'):
            raise CutError('source binding')
        state = self.runtime.model.state[token[5]]
        if (state.generation != token[6] or state.phase != 'starting'
                or not state.owned or not state.launch_pending or state.started):
            raise CutError('launch state')

    def _event(self, source, token):
        self._source(source, token)
        return ('launched', token[5], token[6], token[1], 0)

    def _verify(self, event):
        _, name, generation, _, _ = event
        state = self.runtime.model.state[name]
        if not (state.generation == generation and state.started and not state.launch_pending):
            raise CutError('launch transition missing')

    def reserve(self, credits):
        if credits != 20 or self.ticket is not None:
            raise CutError('reservation')
        ticket = self.runtime.reserve_batch()
        self.ticket = ticket
        self.serial = self.runtime.journal.next_cut - 1
        return ticket

    def cancel(self, ticket):
        if ticket is not self.ticket or ticket is None:
            raise CutError('ticket')
        self.runtime.cancel_batch(ticket)
        self.ticket = None

    def apply(self, ticket, cut):
        if ticket is not self.ticket or ticket is None:
            raise CutError('ticket')
        try:
            events = []
            for source in cut.members:
                token = next((t for s, t in self.bindings if s is source), None)
                if token is None:
                    raise CutError('unregistered source')
                events.append(self._event(source, token))
            before = self.phases
            self.runtime.batch_reserved(ticket, events)
            # Keep actual returned obligations even if later verification fails.
            self.captured = self.runtime.pending
            for event in events:
                self._verify(event)
            journal = self.runtime.journal
            expected = tuple(('event-effect-v1', self.epoch, self.revision, self.serial,
                              index, name, generation, kind, cause, operation)
                             for index, (kind, name, generation, cause, operation)
                             in enumerate(self.runtime.attributed))
            if not (journal.raw == tuple(self.runtime.attributed) and self.captured == expected
                    and len(journal.live) == len(expected)
                    and all(journal.live.get(t[3:5]) == (t, 'reserved') for t in expected)
                    and journal.ticket is None and journal.phase is None):
                raise CutError('journal capture missing')
            receipt = Receipt(cut, self.serial, before, self.phases)
            self.ticket = None
            return receipt
        except BaseException:
            self.runtime.driver_lost()
            raise
