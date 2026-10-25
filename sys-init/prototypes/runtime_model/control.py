# SPDX-License-Identifier: BSD-2-Clause
"""Single-caller model facade; see docs/decisions/0027-control-receipts.md."""
from collections import OrderedDict
from copy import deepcopy

from .model import Rejected

MAX_ID = (1 << 64) - 1


class InvalidRequest(ValueError):
    pass


class Control:
    """Own mutation dispatch; observations may be injected between calls."""

    def __init__(self, model):
        if getattr(model, '_control_claimed', False):
            raise InvalidRequest('control already claimed')
        self.model = model
        self.epoch, self.revision = model.epoch, model.revision
        self.high_water = 0
        self.receipts = OrderedDict()
        self.failed = False
        # Permanent for this trusted model lifetime, including disconnect/failure.
        # The owner retains this facade; recreating it would erase replay history.
        model._control_claimed = True

    def _current(self):
        return (self.model.epoch, self.model.revision) == (self.epoch, self.revision)

    def _payload(self, request):
        fields = {'version', 'epoch', 'revision', 'sequence', 'verb', 'services', 'budget'}
        if type(request) is not dict or request.keys() != fields:
            raise InvalidRequest('request fields')
        if type(request['version']) is not int or request['version'] != 0:
            raise InvalidRequest('version')
        for key, expected in [('epoch', self.epoch), ('revision', self.revision)]:
            if type(request[key]) is not str or not 1 <= len(request[key]) <= 64 or request[key] != expected:
                raise InvalidRequest(key)
        for key, maximum in [('sequence', MAX_ID), ('budget', 1000000)]:
            if type(request[key]) is not int or not 1 <= request[key] <= maximum:
                raise InvalidRequest(key)
        verb, names = request['verb'], request['services']
        if type(verb) is not str or verb not in ('start', 'stop', 'shutdown'):
            raise InvalidRequest('verb')
        if type(names) is not list or not 1 <= len(names) <= 8:
            raise InvalidRequest('selection bound')
        if any(type(n) is not str or len(n) > 32 or n not in self.model.spec for n in names):
            raise InvalidRequest('service')
        if len(set(names)) != len(names):
            raise InvalidRequest('duplicate service')
        if verb == 'shutdown' and set(names) != set(self.model.spec):
            raise InvalidRequest('shutdown scope')
        return (request['version'], request['epoch'], request['revision'],
                request['sequence'], verb, tuple(sorted(names)), request['budget'])

    def _operation(self, operation):
        return dict(epoch=self.epoch, id=operation.id, kind=operation.kind,
                    scope=operation.scope, revision=self.revision,
                    deadline=operation.deadline, shutdown=operation.shutdown)

    def _result(self, sequence, disposition, reason='', operation=None):
        return dict(schema='sys-init-control-receipt-v1', sequence=sequence,
                    disposition=disposition, reason=reason, operation=operation)

    @staticmethod
    def _submission(receipt, effects=(), replayed=False):
        return deepcopy(dict(schema='sys-init-control-submit-v1', receipt=receipt,
                             effects=tuple(effects), replayed=replayed))

    def submit(self, request):
        payload = self._payload(request)
        sequence, verb, names, budget = payload[3:]
        if self.failed or not self._current():
            self.failed = True
            return self._submission(self._result(sequence, 'unknown', 'session-failed'))
        if sequence in self.receipts:
            old, receipt = self.receipts[sequence]
            if old != payload:
                raise InvalidRequest('request identity conflict')
            return self._submission(receipt, replayed=True)
        if sequence <= self.high_water:
            return self._submission(self._result(sequence, 'unknown', 'receipt-retired'))
        if sequence != self.high_water + 1:
            raise InvalidRequest('sequence gap')
        if self.model.next_id > MAX_ID:
            raise InvalidRequest('operation identity exhausted')

        # Reserve before effects; high-water prevents replay after eviction.
        if len(self.receipts) == 64:
            self.receipts.popitem(last=False)
        self.receipts[sequence] = (payload, None)
        self.high_water = sequence
        try:
            previous_id = self.model.next_id
            try:
                if verb == 'start':
                    identity, effects = self.model.start(list(names), budget=budget)
                else:
                    identity, effects = self.model.stop(list(names), budget=budget,
                                                        shutdown=verb == 'shutdown')
            except Rejected as error:
                operation = self._operation(self.model.active) if self.model.active else None
                receipt = self._result(sequence, 'rejected', str(error), operation)
                effects = ()
            else:
                operation = next(o for o in self.model.operations if o.id == identity)
                receipt = self._result(sequence, 'accepted' if identity == previous_id else 'joined',
                                       operation=self._operation(operation))
            self.receipts[sequence] = (payload, deepcopy(receipt))
            return self._submission(receipt, effects)
        except BaseException:
            # Dispatch may already have effects. Never silently retry this session.
            self.failed = True
            raise

    def observe(self, epoch, identity):
        if type(epoch) is not str or type(identity) is not int or not 1 <= identity <= MAX_ID:
            raise InvalidRequest('operation identity')
        operation = None
        if not self.failed and self._current() and epoch == self.epoch:
            if self.model.active and self.model.active.id == identity:
                operation = self.model.active
            else:
                operation = next((o for o in self.model.operations if o.id == identity), None)
        return deepcopy(dict(schema='sys-init-control-observation-v1', epoch=epoch,
                             id=identity, outcome=operation.status if operation else 'unknown',
                             operation=self._operation(operation) if operation else None))

    def wait(self, epoch, identity, *, now, deadline):
        for value in (now, deadline):
            if type(value) is not int or not 0 <= value <= MAX_ID:
                raise InvalidRequest('client wait bound')
        observation = self.observe(epoch, identity)
        outcome = observation['outcome']
        state = ('unknown' if outcome == 'unknown' else
                 ('timeout' if now >= deadline else 'pending') if outcome == 'pending'
                 else 'complete')
        return dict(schema='sys-init-control-wait-v1', state=state, observation=observation)

    def disconnect(self):
        """Detach a waiting view; this does not destroy the manager's session."""
