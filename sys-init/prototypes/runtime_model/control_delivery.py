# SPDX-License-Identifier: BSD-2-Clause
"""One trusted in-memory connection and an explicit effect ownership transfer."""
from .control import Control, InvalidRequest
from .control_codec import decode_request, InvalidFrame
from .control_reply import encode_receipt, encode_error


class Backpressure(RuntimeError):
    pass


class Delivery:
    def __init__(self, model):
        self.control = Control(model)
        self.connected = True
        self.reply = None
        self.effects = ()

    def _error(self, code):
        self.reply = encode_error(dict(schema='sys-init-control-error-v1', code=code,
            disposition='unknown' if code == 'internal-error' else 'not-dispatched'))

    def receive(self, frame):
        if not self.connected or self.reply is not None:
            raise Backpressure('connection unavailable')
        if self.effects:
            self._error('busy')
            return
        try:
            request = decode_request(frame)
        except InvalidFrame:
            self.connected = False
            self._error('invalid-frame')
            return
        try:
            submission = self._submit(request)
        except Backpressure:
            self._error('internal-error' if self.control.failed else 'busy')
            return
        except InvalidRequest:
            self._error('internal-error' if self.control.failed else 'invalid-request')
            return
        except Exception:
            self._error('internal-error')
            return
        self._capture(submission)
        try:
            self.reply = encode_receipt(submission['receipt'])
        except Exception:
            self._error('internal-error')

    def _submit(self, request):
        return self.control.submit(request)

    def _capture(self, submission):
        # Retain manager work independently of reply serialization/connection loss.
        self.effects = submission['effects']
        if len(self.effects) > 8:
            self.control.failed = True
            raise RuntimeError('effect bound violated')

    def read_reply(self):
        reply, self.reply = self.reply, None
        return reply

    def take_effects(self):
        """Transfer to the trusted driver; this is not execution acknowledgment."""
        effects, self.effects = self.effects, ()
        return effects

    def disconnect(self):
        self.connected = False
        self.reply = None

    def reconnect(self):
        if self.reply is not None:
            raise Backpressure('reply pending')
        self.connected = True
