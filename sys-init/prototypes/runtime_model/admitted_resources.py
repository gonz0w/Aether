# SPDX-License-Identifier: BSD-2-Clause
"""Trusted ABI-6 reader/target/wait inventory; no native invocation."""
from .confirmed_result import PROFILE
from .effect_ledger import InvalidEffect


class AdmittedResources:
    def __init__(self, registry, target, reader, *, owner):
        registry._available(owner)
        _, record = registry._target(target)
        registry._current(record)
        if record['phase'] != 'admitted' or 'resources' in record:
            raise InvalidEffect('admitted resource inventory unavailable')
        if type(reader) is not int or not 0 < reader < (1 << 64):
            raise InvalidEffect('reader identity')
        if any(getattr(r.get('resources'), 'reader', None) == reader
               for r in registry.slots.values()):
            raise InvalidEffect('reader already bound')
        self.registry, self.record, self.target = registry, record, target
        self.reader, self.reader_open = reader, True
        self.wait = None
        self.registering = False
        if not hasattr(registry, '_wait_generation'):
            registry._wait_generation = 0
            registry._wait_holder = None
        record['resources'] = self

    def _current(self, owner):
        self.registry._available(owner)
        _, record = self.registry._target(self.target)
        if record is not self.record:
            raise InvalidEffect('resource binding changed')
        state = self.registry._current(record)
        if self.registry.applier.runtime.model.epoch != record['token'][1]:
            raise InvalidEffect('stale epoch')
        return state

    def _reply(self, reply, resource, syscall):
        fields = {'schema', 'profile', 'producer', 'target', 'resource', 'syscall', 'result'}
        if type(reply) is not dict or set(reply) != fields:
            raise InvalidEffect('resource reply fields')
        for field, value in (('schema', 'abi6-resource-return-v1'), ('profile', PROFILE),
                             ('producer', self.registry.applier.producer)):
            if type(reply[field]) is not str or reply[field] != value:
                raise InvalidEffect('resource reply identity')
        for field, value in (('target', self.target), ('resource', resource), ('syscall', syscall)):
            if type(reply[field]) is not int or reply[field] != value:
                raise InvalidEffect('resource call mismatch')
        if type(reply['result']) is not int:
            raise InvalidEffect('resource result type')
        return reply['result']

    def reserve_wait(self, *, owner):
        self._current(owner)
        registry = self.registry
        if (self.record['phase'] != 'admitted' or registry._wait_holder is not None
                or registry._wait_generation >= 64):
            raise InvalidEffect('wait unavailable')
        self.wait = 0xe1000000 | (registry._wait_generation + 1)
        self.registering = True
        registry._wait_holder = self
        return self.wait

    def register_reply(self, reply, *, owner):
        self._current(owner)
        if not self.registering or self.registry._wait_holder is not self:
            raise InvalidEffect('wait not reserved')
        result = self._reply(reply, self.wait, 0x25002)
        if result == self.wait:
            self.registering = False
            self.registry._wait_generation += 1
            return True
        if result not in (-13, -9, -22, -16, -28):
            raise InvalidEffect('unsupported registration result')
        self.wait = None
        self.registering = False
        self.registry._wait_holder = None
        return False

    def release_reply(self, reply, *, owner):
        self._current(owner)
        if self.wait is None or self.registering or self.registry._wait_holder is not self:
            raise InvalidEffect('wait not admitted')
        result = self._reply(reply, self.wait, 0x25005)
        if result in (-13, -9, -22):
            return False
        if result != 0:
            raise InvalidEffect('unsupported release result')
        self.wait = None
        self.registry._wait_holder = None
        return True

    def close_reply(self, reply, *, owner):
        self._current(owner)
        if not self.reader_open:
            raise InvalidEffect('reader already closed')
        result = self._reply(reply, self.reader, 0x24003)
        if result in (-13, -22):
            return False
        if result != 0:
            raise InvalidEffect('unsupported close result')
        self.reader_open = False
        return True

    def cleaned_event(self, *, owner):
        self._current(owner)
        token = self.record['token']
        expected = ('native-cleanup-v1', token[5], token[6], token[1], self.target)
        if (self.record['phase'] != 'reclaimed' or self.record['cleanup'] != expected
                or self.reader_open or self.wait is not None):
            raise InvalidEffect('generation resources remain owned')
        return ('cleaned', token[5], token[6], token[1], 0)
