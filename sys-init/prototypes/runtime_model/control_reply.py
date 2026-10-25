# SPDX-License-Identifier: BSD-2-Clause
"""Pure bounded reply encoding; never serialize internal submission effects."""
import json
import re

from .control import MAX_ID
from .control_codec import InvalidFrame, MAX_BODY, _decode_frame

REJECTED = frozenset(('shutdown admission closed', 'operation conflict',
                      'unresolved ownership', 'required consumer outside stop scope'))


def _require(condition):
    if not condition:
        raise InvalidFrame('receipt')


def _fields(value, fields):
    _require(type(value) is dict and value.keys() == set(fields.split()))


def _text(value, maximum, minimum=0):
    _require(type(value) is str and minimum <= len(value) <= maximum)
    _require(not any(0xD800 <= ord(char) <= 0xDFFF for char in value))
    return value


def _integer(value, minimum=1):
    _require(type(value) is int and minimum <= value <= MAX_ID)
    return value


def _operation(value):
    if value is None:
        return None
    _fields(value, 'epoch id kind scope revision deadline shutdown')
    epoch = _text(value['epoch'], 64, 1)
    revision = _text(value['revision'], 64, 1)
    identity = _integer(value['id'])
    deadline = _integer(value['deadline'], 0)
    kind = _text(value['kind'], 5)
    _require(kind in ('start', 'stop'))
    shutdown = value['shutdown']
    _require(type(shutdown) is bool and (not shutdown or kind == 'stop'))
    scope = value['scope']
    _require(type(scope) in (list, tuple) and 1 <= len(scope) <= 8)
    for name in scope:
        _text(name, 32, 1)
        _require(re.fullmatch(r'[a-z][a-z0-9_-]{0,31}', name) is not None)
    _require(len(set(scope)) == len(scope))
    return dict(epoch=epoch, id=identity, kind=kind, scope=sorted(scope),
                revision=revision, deadline=deadline, shutdown=shutdown)


def _receipt(value):
    _fields(value, 'schema sequence disposition reason operation')
    schema = _text(value['schema'], 32)
    _require(schema == 'sys-init-control-receipt-v1')
    sequence = _integer(value['sequence'])
    disposition = _text(value['disposition'], 8)
    reason = _text(value['reason'], 64)
    operation = _operation(value['operation'])
    if disposition in ('accepted', 'joined'):
        _require(operation is not None and reason == '')
    elif disposition == 'rejected':
        _require(reason in REJECTED)
    else:
        _require(disposition == 'unknown' and operation is None and
                 reason in ('receipt-retired', 'session-failed'))
    return dict(schema=schema, sequence=sequence, disposition=disposition,
                reason=reason, operation=operation)


def encode_receipt(receipt):
    """Validate bounded leaves before serializing a detached client-only receipt."""
    return _encode(_receipt(receipt))


def _encode(value):
    body = json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')
    _require(1 <= len(body) <= MAX_BODY)
    return len(body).to_bytes(4, 'big') + body


def decode_receipt(frame):
    """Reject extra fields and invalid receipt combinations after bounded parsing."""
    return _receipt(_decode_frame(frame, 3))


TERMINAL = frozenset(('success', 'failed', 'cancelled', 'incomplete'))


def _observation(value):
    _fields(value, 'schema epoch id outcome operation')
    schema = _text(value['schema'], 40)
    _require(schema == 'sys-init-control-observation-v1')
    epoch = _text(value['epoch'], 64, 1)
    identity = _integer(value['id'])
    outcome = _text(value['outcome'], 10)
    _require(outcome in TERMINAL or outcome in ('pending', 'unknown'))
    operation = _operation(value['operation'])
    if outcome == 'unknown':
        _require(operation is None)
    else:
        _require(operation is not None)
        _require(operation['epoch'] == epoch and operation['id'] == identity)
    return dict(schema=schema, epoch=epoch, id=identity, outcome=outcome, operation=operation)


def _wait(value):
    _fields(value, 'schema state observation')
    schema = _text(value['schema'], 40)
    _require(schema == 'sys-init-control-wait-v1')
    state = _text(value['state'], 8)
    observation = _observation(value['observation'])
    outcome = observation['outcome']
    _require((state in ('pending', 'timeout') and outcome == 'pending') or
             (state == 'complete' and outcome in TERMINAL) or
             (state == 'unknown' and outcome == 'unknown'))
    return dict(schema=schema, state=state, observation=observation)


def _validate(value, validator, category):
    try:
        return validator(value)
    except InvalidFrame:
        raise InvalidFrame(category) from None


def encode_observation(observation):
    return _encode(_validate(observation, _observation, 'observation'))


def decode_observation(frame):
    return _validate(_decode_frame(frame, 3), _observation, 'observation')


def encode_wait(wait):
    return _encode(_validate(wait, _wait, 'wait'))


def decode_wait(frame):
    return _validate(_decode_frame(frame, 4), _wait, 'wait')


def _error(value):
    _fields(value, 'schema code disposition')
    schema = _text(value['schema'], 40)
    _require(schema == 'sys-init-control-error-v1')
    code = _text(value['code'], 16)
    disposition = _text(value['disposition'], 16)
    _require((code in ('invalid-frame', 'invalid-request', 'busy') and
              disposition == 'not-dispatched') or
             (code == 'internal-error' and disposition == 'unknown'))
    return dict(schema=schema, code=code, disposition=disposition)


def encode_error(error):
    return _encode(_validate(error, _error, 'error-reply'))


def decode_error(frame):
    return _validate(_decode_frame(frame, 1), _error, 'error-reply')
