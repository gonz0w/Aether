# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic resource disposition and tombstones; no native cleanup or reuse."""
from dataclasses import dataclass
from .cut_coordinator import CutError, Receipt


@dataclass(frozen=True)
class Resources:
    source: object
    live: tuple  # reader, writer, worker, wait ownership, in that order
    reclaim_applied: bool
    unresolved: bool


class Retirement:
    """Trusted adapter: inspect(source) is read-only; mark(source, receipt) returns
    that exact receipt after marking its own tombstone. A failed mark may have
    completed: retain started state plus adapter evidence and close, never retry.
    """
    def __init__(self, core, adapter):
        if getattr(core, 'retirement', None) is not None or core.closed or core.running:
            raise CutError('retirement owner unavailable')
        self.core, self.adapter = core, adapter
        self.dispositions = [None, None]
        self.observations = [None, None]
        self.returned = [None, None]
        self.releases = [None, None]
        self.release_observations = [None, None]
        self.release_returns = [None, None]
        core.retirement = self

    def _applied(self, owner, receipt):
        if type(receipt) is not Receipt:
            raise CutError('receipt')
        record = self.core._record(owner, receipt.cut)
        if self.core.closed or self.core.active is not None:
            raise CutError('closed or busy')
        if record.state != 'applied' or record.receipt is not receipt:
            raise CutError('unapplied receipt')
        return receipt.cut.members

    def _receipt(self, owner, receipt):
        members = tuple(s for s in self._applied(owner, receipt) if s.phase == 3)
        if not members:
            raise CutError('cleaned cut required')
        for source in members:
            for phase in (1, 2):
                if not any(r.state == 'applied' and any(
                        s.attempt == source.attempt and s.phase == phase for s in r.cut.members)
                           for r in self.core.records):
                    raise CutError('prior application missing')
            release = self.releases[source.attempt]
            if release is None or release[0] != 'released':
                raise CutError('pending release required')
            terminal = self.core._record(owner, release[1].cut)
            if (terminal.state != 'applied' or terminal.receipt is not release[1]
                    or not any(s.attempt == source.attempt and s.phase == 2
                               for s in terminal.cut.members)):
                raise CutError('pending receipt mismatch')
        return members

    @staticmethod
    def _empty(state, source):
        if (type(state) is not Resources or state.source is not source
                or type(state.live) is not tuple or len(state.live) != 4
                or any(type(v) is not bool for v in state.live)
                or type(state.reclaim_applied) is not bool or type(state.unresolved) is not bool):
            raise CutError('disposition identity')
        if any(state.live) or not state.reclaim_applied or state.unresolved:
            raise CutError('resources unresolved')

    def retire(self, owner, receipt):
        members = self._receipt(owner, receipt)
        if all(self.dispositions[s.attempt] == ('retired', receipt) for s in members):
            return 'already-retired'
        if any(self.dispositions[s.attempt] is not None for s in members):
            raise CutError('retirement conflict')
        # Whole-cut preflight is read-only. No tombstone is marked on any denial.
        states = []
        for source in members:
            state = self.core._invoke(self.adapter.inspect, source)
            self._empty(state, source)
            states.append(state)
        # Both snapshots remain retained if a later member's mark fails.
        for source, state in zip(members, states):
            self.observations[source.attempt] = state
        try:
            for source in members:
                index = source.attempt
                self.dispositions[index] = ('started', receipt)
                result = self.core._invoke(self.adapter.mark, source, receipt)
                self.returned[index] = (result,)
                if result is not receipt:
                    raise CutError('retirement not confirmed')
                self.dispositions[index] = ('retired', receipt)
        except BaseException:
            self.core.closed = True
            raise
        return 'retired'

    def release_pending(self, owner, receipt, source):
        members = self._applied(owner, receipt)
        if not any(source is s and s.phase == 2 for s in members):
            raise CutError('terminal member required')
        index = source.attempt
        if self.releases[index] == ('released', receipt):
            return 'already-released'
        if self.releases[index] is not None:
            raise CutError('release conflict')
        pending = self.core._invoke(self.adapter.pending_source)
        if pending is not source:
            raise CutError('pending identity')
        self.release_observations[index] = pending
        self.releases[index] = ('started', receipt)
        try:
            result = self.core._invoke(self.adapter.release, source, receipt)
            self.release_returns[index] = (result,)
            if result is not receipt or self.core._invoke(self.adapter.pending_source) is not None:
                raise CutError('pending release not confirmed')
            self.releases[index] = ('released', receipt)
        except BaseException:
            self.core.closed = True
            raise
        return 'released'
