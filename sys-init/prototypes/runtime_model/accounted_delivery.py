# SPDX-License-Identifier: BSD-2-Clause
"""Submission-only accounting experiment; event effects remain a separate gate."""
from .control import MAX_ID, InvalidRequest
from .control_delivery import Delivery, Backpressure
from .effect_ledger import EffectLedger, InvalidEffect


class AccountedDelivery(Delivery):
    def __init__(self, model):
        self.ledger = EffectLedger(epoch=model.epoch, revision=model.revision,
                                   services=list(model.spec))
        self.credits = 0
        self.pending_tokens = ()
        super().__init__(model)

    def _submit(self, request):
        payload = self.control._payload(request)
        sequence = payload[3]
        fresh = sequence == self.control.high_water + 1
        if fresh and not self.control.failed and self.control._current():
            if self.ledger.closed or self.ledger.live or self.credits or self.ledger.next_id > MAX_ID - 7:
                raise Backpressure('accounting capacity')
            self.credits = 8
        try:
            return super()._submit(request)
        except InvalidRequest:
            if not self.control.failed:
                self.credits = 0
            raise

    def _capture(self, submission):
        super()._capture(submission)
        try:
            if self.effects:
                operation = submission['receipt']['operation']['id']
                self.pending_tokens = self.ledger.reserve(operation, self.effects)
            else:
                self.pending_tokens = ()
            if not self.control.failed:
                self.credits = 0
        except BaseException:
            self.control.failed = True
            raise

    def take_effects(self):
        raise InvalidEffect('use issue_obligations')

    def issue_obligations(self):
        if self.control.failed or self.ledger.closed:
            raise InvalidEffect('driver closed')
        if any(self.ledger.observe(token) != 'reserved' for token in self.pending_tokens):
            raise InvalidEffect('not reserved')
        tokens = self.pending_tokens
        try:
            for token in tokens:
                self.ledger.issue(token)
        except BaseException:
            self.driver_lost()
            raise
        self.pending_tokens = ()
        self.effects = ()
        return tokens

    def acknowledge(self, token, outcome):
        return self.ledger.acknowledge(token, outcome)

    def driver_lost(self):
        self.ledger.driver_lost()
        self.control.failed = True
        self.disconnect()
