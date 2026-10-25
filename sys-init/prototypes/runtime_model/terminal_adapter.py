# SPDX-License-Identifier: BSD-2-Clause
"""Real model terminal/effect mapping; qualified facts remain synthetic inputs."""
from .cut_coordinator import CutError, Source, MAX_SERIAL
from .launched_adapter import LaunchedAdapter


class TerminalAdapter(LaunchedAdapter):
    def __init__(self, runtime, owner, launched, terminal):
        super().__init__(runtime, owner, launched)
        if type(terminal) is not tuple or not 1 <= len(terminal) <= 2:
            raise CutError('terminal bindings')
        attempts = set()
        for source, token in terminal:
            launch = next((s for s, t in launched if t == token), None)
            if (type(source) is not Source or source.owner is not owner or launch is None
                    or type(source.phase) is not int or source.phase != 2
                    or type(source.attempt) is not int or type(source.worker) is not int
                    or type(source.token) is not tuple or any(type(v) is not int for v in source.token)
                    or source.attempt != launch.attempt or source.worker != launch.worker
                    or source.token != launch.token or source.attempt in attempts):
                raise CutError('terminal binding')
            self._fact(source.content)
            attempts.add(source.attempt)
        self.bindings = launched + terminal

    @staticmethod
    def _fact(content):
        if (type(content) is not tuple or len(content) != 4
                or any(type(v) is not int for v in content)):
            raise CutError('terminal fact')
        revision, result, kind, ready = content
        if not (1 <= revision <= MAX_SERIAL and ready in (0, 1)
                and ((kind == 1 and 1 <= result <= 256) or
                     (kind == 2 and result == 135) or (kind == 3 and result == 144))):
            raise CutError('terminal fact')
        return result, kind

    @property
    def phases(self):
        return tuple(2 if self.runtime.model.state[n].phase == 'terminal' else
                     int(self.runtime.model.state[n].started) for n in self.names) + (0,) * (2 - len(self.names))

    def _event(self, source, token):
        if source.phase == 1:
            return super()._event(source, token)
        result, kind = self._fact(source.content)
        state = self.runtime.model.state[token[5]]
        if (source.owner is not self.owner or source.token != self.encoded(token)
                or self.runtime.model.epoch != self.epoch or self.runtime.model.revision != self.revision
                or self.runtime.journal.observe(token) != 'executed'
                or state.generation != token[6] or state.phase != 'running'
                or not state.owned or not state.started or state.launch_pending or state.reclaim_sent):
            raise CutError('terminal state')
        event_kind = {1: 'exit', 2: 'fault', 3: 'stopped'}[kind]
        return (event_kind, token[5], token[6], token[1], result - 1)

    def _verify(self, event):
        kind, name, generation, _, detail = event
        if kind == 'launched':
            return super()._verify(event)
        state = self.runtime.model.state[name]
        if not (state.generation == generation and state.phase == 'terminal'
                and state.owned and state.cleanup == 'pending' and state.reclaim_sent
                and not state.launch_pending and not state.ready):
            raise CutError('terminal transition missing')
        expected = 'exit-0' if kind == 'exit' and detail == 0 else kind
        if not (state.terminal == expected and state.terminal_detail == (None if kind == 'fault' else detail)):
            raise CutError('terminal kind missing')
        obligations = [t for t in self.runtime.pending if t[5] == name and t[6] == generation and t[7] == 'reclaim']
        if len(obligations) != 1:
            raise CutError('reclaim obligation missing')
