# SPDX-License-Identifier: BSD-2-Clause
"""Fixed two-endpoint rejected-launch fixture; no I/O or recovery."""
from .confirmed_result import BoundCall, PROFILE
from .effect_ledger import InvalidEffect


class RejectedLaunchCleanup:
    def __init__(self, applier, call, reader, writer, *, owner):
        applier._available(owner)
        if (type(call) is not BoundCall or call.syscall != 0x23001
                or applier.bindings.get(call.token) is not call):
            raise InvalidEffect('retained launch call required')
        for handle in (reader, writer):
            if type(handle) is not int or not 0 < handle < (1 << 64):
                raise InvalidEffect('endpoint identity')
        claims = getattr(applier, '_cleanup_claims', set()) & applier.bindings.keys()
        if reader == writer or call.token in claims:
            raise InvalidEffect('duplicate cleanup inventory')
        self.applier, self.call = applier, call
        self.endpoints = {reader: True, writer: True}
        self.verdict = None
        self.reclaim = None
        applier._cleanup_claims = claims | {call.token}

    def _current(self, owner):
        self.applier._available(owner)
        token = self.call.token
        model = self.applier.runtime.model
        state = model.state[token[5]]
        if not state.owned or state.generation != token[6] or model.epoch != token[1]:
            raise InvalidEffect('stale cleanup generation')
        return state

    def accept_rejection(self, *, owner):
        self._current(owner)
        last = self.applier.last_applied
        if self.verdict is not None or last is None:
            raise InvalidEffect('missing or duplicate rejection')
        token, verdict = last
        if (token != self.call.token or verdict[1] != 'rejected-before-effects'
                or verdict[2] != self.call.syscall or verdict[4] != self.call.target
                or self.applier.runtime.journal.observe(token) != verdict[1]):
            raise InvalidEffect('confirmed launch rejection required')
        self.verdict = verdict

    def failure_event(self, *, owner):
        self._current(owner)
        if self.verdict is None:
            raise InvalidEffect('unconfirmed launch')
        token = self.call.token
        kind = 'denied' if self.verdict[3] == -13 else 'launch_failed'
        return (kind, token[5], token[6], token[1], self.verdict[3])

    def close_reply(self, reply, *, owner):
        self._current(owner)
        fields = {'schema', 'profile', 'producer', 'endpoint', 'syscall', 'result'}
        if self.verdict is None or type(reply) is not dict or set(reply) != fields:
            raise InvalidEffect('close reply fields or unconfirmed launch')
        for field, expected in (('schema', 'abi6-close-v1'), ('profile', PROFILE),
                                ('producer', self.applier.producer)):
            if type(reply[field]) is not str or reply[field] != expected:
                raise InvalidEffect('close identity')
        endpoint = reply['endpoint']
        if type(endpoint) is not int or not self.endpoints.get(endpoint, False):
            raise InvalidEffect('unowned endpoint')
        if type(reply['syscall']) is not int or reply['syscall'] != 0x24003:
            raise InvalidEffect('close operation')
        result = reply['result']
        if type(result) is not int or result not in (0, -13, -22):
            raise InvalidEffect('unsupported close result')
        if result != 0:
            return False
        self.endpoints[endpoint] = False
        return True

    def qualify_reclaim(self, token, *, owner):
        state = self._current(owner)
        journal = self.applier.runtime.journal
        if (self.verdict is None or any(self.endpoints.values())
                or not state.reclaim_sent or journal.observe(token) != 'issued'
                or token[7] != 'reclaim' or token[1:3] != self.call.token[1:3]
                or token[5:7] != self.call.token[5:7]):
            raise InvalidEffect('cleanup incomplete or reclaim mismatch')
        if self.reclaim is not None and token != self.reclaim:
            raise InvalidEffect('different cleanup occurrence')
        self.reclaim = token
        return ('local-cleanup-v1', token, 'rejected-launch-endpoints-closed')

    def cleaned_event(self, *, owner):
        self._current(owner)
        if (self.reclaim is None
                or self.applier.runtime.journal.observe(self.reclaim) != 'executed'):
            raise InvalidEffect('local reclaim not acknowledged')
        token = self.call.token
        return ('cleaned', token[5], token[6], token[1], 0)
