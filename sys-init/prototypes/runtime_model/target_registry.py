# SPDX-License-Identifier: BSD-2-Clause
"""Trusted empty-domain ABI-6 target bookkeeping; no native calls or recovery."""
from .confirmed_result import PROFILE
from .effect_ledger import InvalidEffect


class TargetRegistry:
    def __init__(self, applier):
        applier._available(applier.owner)
        if getattr(applier, '_target_registry_claimed', False):
            raise InvalidEffect('registry already claimed')
        self.applier = applier
        self.slots = {}
        self.generations = [0, 0]
        applier._target_registry_claimed = True

    def _available(self, owner):
        self.applier._available(owner)

    def reserve(self, token, slot, *, owner):
        self._available(owner)
        runtime = self.applier.runtime
        if runtime.journal.observe(token) != 'issued' or token[7] != 'launch':
            raise InvalidEffect('issued launch required')
        if type(slot) is not int or slot not in (0, 1) or slot in self.slots:
            raise InvalidEffect('slot unavailable')
        if self.generations[slot] >= 3:
            raise InvalidEffect('native generation exhausted')
        state = runtime.model.state[token[5]]
        if not state.owned or not state.launch_pending or state.generation != token[6]:
            raise InvalidEffect('model launch mismatch')
        if any(record['token'][5] == token[5] for record in self.slots.values()):
            raise InvalidEffect('service already bound')
        target = 0xb0000000 | ((self.generations[slot] + 1) << 8) | (slot + 1)
        self.slots[slot] = dict(target=target, token=token, phase='reserved', cleanup=None)
        return target

    def _target(self, target):
        if type(target) is not int:
            raise InvalidEffect('target')
        for slot, record in self.slots.items():
            if record['target'] == target:
                return slot, record
        raise InvalidEffect('unbound target')

    def _current(self, record):
        token = record['token']
        state = self.applier.runtime.model.state[token[5]]
        if not state.owned or state.generation != token[6]:
            raise InvalidEffect('stale model generation')
        return state

    def _last(self, target, syscall):
        last = self.applier.last_applied
        if last is None:
            raise InvalidEffect('missing applied result')
        token, verdict = last
        if verdict[2] != syscall or verdict[4] != target:
            raise InvalidEffect('applied call mismatch')
        if self.applier.runtime.journal.observe(token) != verdict[1]:
            raise InvalidEffect('applied outcome retired')
        return token, verdict

    def accept_launch(self, target, *, owner):
        self._available(owner)
        slot, record = self._target(target)
        token, verdict = self._last(target, 0x23001)
        if record['phase'] != 'reserved' or token != record['token']:
            raise InvalidEffect('launch binding mismatch')
        self._current(record)
        if verdict[1] == 'executed':
            record['phase'] = 'admitted'
            self.generations[slot] += 1
        else:
            del self.slots[slot]
        return verdict[1]

    def status(self, reply, *, owner):
        self._available(owner)
        fields = {'schema', 'profile', 'producer', 'target', 'syscall', 'result', 'kind'}
        if type(reply) is not dict or set(reply) != fields:
            raise InvalidEffect('status fields')
        for field, value in (('schema', 'abi6-status-v1'), ('profile', PROFILE),
                             ('producer', self.applier.producer)):
            if type(reply[field]) is not str or reply[field] != value:
                raise InvalidEffect('status identity')
        if type(reply['syscall']) is not int or reply['syscall'] != 0x20001:
            raise InvalidEffect('status operation')
        _, record = self._target(reply['target'])
        if record['phase'] != 'admitted':
            raise InvalidEffect('target not admitted')
        self._current(record)
        result, kind = reply['result'], reply['kind']
        if type(result) is not int or type(kind) is not int:
            raise InvalidEffect('terminal types')
        if (result, kind) == (0, 0):
            return None
        if not ((kind == 1 and 1 <= result <= 256)
                or (kind == 2 and result == 135) or (kind == 3 and result == 144)):
            raise InvalidEffect('terminal kind/detail')
        token = record['token']
        return ('native-terminal-v1', token[5], token[6], token[1], reply['target'],
                {1: 'normal', 2: 'fault', 3: 'stopped'}[kind], result - 1)

    def terminal_event(self, reply, *, owner):
        """Project a freshly qualified status; delivery and cleanup remain explicit."""
        fact = self.status(reply, owner=owner)
        if fact is None:
            return None
        _, service, generation, epoch, _, kind, detail = fact
        return ({'normal': 'exit', 'fault': 'fault', 'stopped': 'stopped'}[kind],
                service, generation, epoch, detail)

    def accept_reclaim(self, target, *, owner):
        self._available(owner)
        _, record = self._target(target)
        token, verdict = self._last(target, 0x20002)
        state = self._current(record)
        if (record['phase'] != 'admitted' or verdict[1] != 'executed'
                or token[5:7] != record['token'][5:7] or not state.reclaim_sent):
            raise InvalidEffect('reclaim binding mismatch')
        fact = ('native-cleanup-v1', token[5], token[6], token[1], target)
        record['cleanup'], record['phase'] = fact, 'reclaimed'
        return fact

    def retire(self, target, *, owner):
        self._available(owner)
        slot, record = self._target(target)
        token = record['token']
        state = self.applier.runtime.model.state[token[5]]
        if (record['phase'] != 'reclaimed' or state.owned or state.cleanup != 'complete'
                or state.generation != token[6]):
            raise InvalidEffect('model cleanup incomplete')
        del self.slots[slot]
