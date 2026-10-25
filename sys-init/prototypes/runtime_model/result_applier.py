# SPDX-License-Identifier: BSD-2-Clause
"""Trusted serialized journal application; never lifecycle observation or I/O."""
import re

from .confirmed_result import BoundCall
from .effect_ledger import InvalidEffect


class ResultApplier:
    def __init__(self, runtime, *, owner, producer):
        if owner is None or type(producer) is not str or re.fullmatch(r'[0-9a-f]{64}', producer) is None:
            raise InvalidEffect('applier identity')
        if (runtime.failed or runtime.running or runtime.journal.closed
                or getattr(runtime, '_result_applier_claimed', False)):
            raise InvalidEffect('applier unavailable')
        self.runtime, self.owner, self.producer = runtime, owner, producer
        self.bindings = {}
        self.busy = False
        self.last_attempt = None
        self.last_applied = None
        runtime._result_applier_claimed = True

    def _available(self, owner):
        if owner is not self.owner:
            raise InvalidEffect('owner mismatch')
        if self.busy or self.runtime.running or self.runtime.failed or self.runtime.journal.closed:
            raise InvalidEffect('applier unavailable')

    def bind(self, token, syscall, target, *, owner):
        self._available(owner)
        call = BoundCall(self.runtime.journal, self.owner, self.producer, token, syscall, target)
        if token in self.bindings or len(self.bindings) >= 20:
            raise InvalidEffect('binding capacity or duplicate')
        self.bindings[token] = call
        return call

    def apply(self, call, reply, *, owner):
        self._available(owner)
        if type(call) is not BoundCall:
            raise InvalidEffect('call context')
        if self.bindings.get(call.token) is not call:
            raise InvalidEffect('unretained call')
        self.busy = self.runtime.running = True
        acknowledging = False
        try:
            verdict = call.qualify(reply, owner=owner)
            attempt = (call.token, verdict)
            self.last_attempt = attempt
            acknowledging = True
            result = self.runtime.acknowledge(call.token, verdict[1])
            if result != 'recorded':
                raise InvalidEffect('unexpected acknowledgment')
            self.bindings.pop(call.token)
            self.last_applied = attempt
            return verdict
        except BaseException:
            if acknowledging:
                self.runtime.driver_lost()
            raise
        finally:
            self.busy = self.runtime.running = False
