# SPDX-License-Identifier: BSD-2-Clause
"""Trusted policy fixture, not a protection boundary against Python callers."""
from .control import InvalidRequest
from .control_codec import decode_request, InvalidFrame
from .control_reply import decode_receipt, decode_error
from .control_stream import Stream


class Denied(RuntimeError):
    pass


def _selection(values, allowed, bound):
    if type(values) not in (list, tuple) or len(values) > bound:
        raise ValueError('policy scope')
    if any(type(value) is not str or len(value) > 32 or value not in allowed for value in values):
        raise ValueError('policy scope')
    if len(set(values)) != len(values):
        raise ValueError('policy scope')
    return frozenset(values)


class AuthorizedStream(Stream):
    def __init__(self, model, *, binding, policy_revision, verbs, mutate, observe, **options):
        if type(binding) is not object:
            raise ValueError('binding')
        if type(policy_revision) is not str or not 1 <= len(policy_revision) <= 64:
            raise ValueError('policy revision')
        if any(0xD800 <= ord(char) <= 0xDFFF for char in policy_revision):
            raise ValueError('policy revision')
        self.verbs = _selection(verbs, ('start', 'stop', 'shutdown'), 3)
        self.mutate_scope = _selection(mutate, model.spec, 8)
        self.observe_scope = _selection(observe, model.spec, 8)
        self.binding, self.policy_revision = binding, policy_revision
        self.epoch, self.revision = model.epoch, model.revision
        self.revoked = False
        self.reply_guard = False
        self.reply_scope = None
        super().__init__(model, **options)

    def _authorize(self, binding):
        if binding is not self.binding:
            raise Denied('authority')
        model = self.delivery.control.model
        if (model.epoch, model.revision) != (self.epoch, self.revision):
            self.revoke()
        if self.revoked:
            raise Denied('authority')

    def _disclose(self, scope):
        required = set(self.delivery.control.model.spec) if scope is None else set(scope)
        if not required <= self.observe_scope:
            raise Denied('authority')

    def _receive(self, frame):
        control = self.delivery.control
        try:
            request = decode_request(frame)
            payload = control._payload(request)
        except (InvalidFrame, InvalidRequest):
            super()._receive(frame)
            self.reply_guard = False
            return
        verb, names = payload[4:6]
        scope = control.model._closure(names) if verb == 'start' else names
        if verb not in self.verbs or not set(scope) <= self.mutate_scope:
            raise Denied('authority')
        super()._receive(frame)
        self.reply_guard = False
        try:
            receipt = decode_receipt(self.delivery.reply)
        except InvalidFrame:
            decode_error(self.delivery.reply)
            return
        operation = receipt['operation']
        self.reply_scope = None if operation is None else tuple(operation['scope'])
        self._disclose(self.reply_scope)
        self.reply_guard = True

    def feed(self, chunk, *, now, binding=None):
        self._authorize(binding)
        return super().feed(chunk, now=now)

    def read(self, maximum, *, now, binding=None):
        self._authorize(binding)
        if self.reply_guard:
            self._disclose(self.reply_scope)
        return super().read(maximum, now=now)

    def reconnect(self, *, now, binding=None):
        self._authorize(binding)
        return super().reconnect(now=now)

    def revoke(self):
        self.revoked = True
        self.disconnect()

    def observe(self, epoch, identity, *, binding=None):
        self._authorize(binding)
        result = self.delivery.control.observe(epoch, identity)
        self._disclose(None if result['operation'] is None else result['operation']['scope'])
        return result

    def wait(self, epoch, identity, *, now, deadline, binding=None):
        self._authorize(binding)
        result = self.delivery.control.wait(epoch, identity, now=now, deadline=deadline)
        operation = result['observation']['operation']
        self._disclose(None if operation is None else operation['scope'])
        return result
