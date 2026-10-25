# SPDX-License-Identifier: BSD-2-Clause
"""Real journal cleanup admission; resource inspection remains synthetic/trusted."""
from .cut_coordinator import CutError, Source
from .cut_retirement import Retirement
from .terminal_adapter import TerminalAdapter


class CleanedAdapter(TerminalAdapter):
    def __init__(self, runtime, owner, launched, terminal, cleaned, inspect):
        super().__init__(runtime, owner, launched, terminal)
        if type(cleaned) is not tuple or not 1 <= len(cleaned) <= 2 or not callable(inspect):
            raise CutError('cleaned bindings')
        attempts = set()
        for source, token in cleaned:
            previous = next((s for s, t in terminal if t == token), None)
            if (type(source) is not Source or previous is None or source.owner is not owner
                    or type(source.phase) is not int or source.phase != 3
                    or type(source.attempt) is not int or source.attempt != previous.attempt
                    or type(source.worker) is not int or source.worker != previous.worker
                    or type(source.token) is not tuple or any(type(v) is not int for v in source.token)
                    or source.token != previous.token or source.attempt in attempts
                    or type(source.content) is not tuple or source.content != (0,)
                    or type(source.content[0]) is not int):
                raise CutError('cleaned binding')
            attempts.add(source.attempt)
        self.bindings += cleaned
        self.inspect_resources = inspect
        self.reclaims = [None, None]
        self.observations = [None, None]

    @property
    def phases(self):
        phases = list(super().phases)
        for index, name in enumerate(self.names):
            state = self.runtime.model.state[name]
            token = self.reclaims[index]
            if (token is not None and state.generation == token[6]
                    and state.cleanup == 'complete' and not state.owned):
                phases[index] = 3
        return tuple(phases)

    def _event(self, source, token):
        if source.phase != 3:
            return super()._event(source, token)
        observation = self.inspect_resources(source)
        self.observations[source.attempt] = observation
        Retirement._empty(observation, source)
        # Revalidate after the callback, immediately before constructing the event.
        state = self.runtime.model.state[token[5]]
        reclaim = self.reclaims[source.attempt]
        if reclaim is None or self.runtime.journal.observe(reclaim) != 'executed':
            raise CutError('reclaim not executed')
        if (source.owner is not self.owner or source.token != self.encoded(token)
                or self.runtime.model.epoch != self.epoch or self.runtime.model.revision != self.revision
                or state.generation != token[6] or state.phase != 'terminal'
                or not state.owned or state.cleanup != 'pending' or not state.reclaim_sent
                or state.launch_pending):
            raise CutError('cleaned state')
        return ('cleaned', token[5], token[6], token[1], 0)

    def _verify(self, event):
        kind, name, generation, _, _ = event
        if kind != 'cleaned':
            super()._verify(event)
            if kind != 'launched':
                self.reclaims[self.names.index(name)] = next(
                    t for t in self.runtime.pending if t[5] == name and t[6] == generation and t[7] == 'reclaim')
            return
        state = self.runtime.model.state[name]
        if not (state.generation == generation and not state.owned
                and state.cleanup == 'complete' and state.deadline is None
                and not state.launch_pending):
            raise CutError('cleaned transition missing')
