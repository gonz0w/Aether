# SPDX-License-Identifier: BSD-2-Clause
"""Bounded complete-frame decoding; candidates still need Control validation."""
import json

MAX_BODY = 4096
MAX_DEPTH = 2


class InvalidFrame(ValueError):
    """A fixed local error category, never a copy of untrusted input."""


def _depth(text, limit):
    depth = 0
    quoted = escaped = False
    for character in text:
        if quoted:
            if escaped:
                escaped = False
            elif character == '\\':
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
        elif character in '{[':
            depth += 1
            if depth > limit:
                raise InvalidFrame('depth')
        elif character in '}]':
            depth -= 1
            if depth < 0:
                raise InvalidFrame('json')
    # Full grammar, matching delimiter types and string validity belong to JSON.
    if depth or quoted:
        raise InvalidFrame('json')


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidFrame('duplicate-key')
        result[key] = value
    return result


def _integer(token):
    if len(token.lstrip('-')) > 20:
        raise InvalidFrame('number')
    return int(token)


def _not_integer(token):
    raise InvalidFrame('number')


def _unicode(value):
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise InvalidFrame('unicode')
    elif isinstance(value, dict):
        for key, item in value.items():
            _unicode(key)
            _unicode(item)
    elif isinstance(value, list):
        for item in value:
            _unicode(item)


def decode_request(frame):
    """Return a syntax-checked candidate; Control.submit validates logical fields."""
    return _decode_frame(frame, MAX_DEPTH)


def _decode_frame(frame, depth_limit):
    if type(frame) is not bytes:
        raise InvalidFrame('frame-type')
    if not 5 <= len(frame) <= MAX_BODY + 4:
        raise InvalidFrame('frame-length')
    length = int.from_bytes(frame[:4], 'big')
    if not 1 <= length <= MAX_BODY or length != len(frame) - 4:
        raise InvalidFrame('frame-length')
    try:
        text = frame[4:].decode('utf-8')
    except UnicodeDecodeError:
        raise InvalidFrame('utf8') from None
    _depth(text, depth_limit)
    try:
        value = json.loads(text, object_pairs_hook=_object, parse_int=_integer,
                           parse_float=_not_integer, parse_constant=_not_integer)
    except json.JSONDecodeError:
        raise InvalidFrame('json') from None
    if type(value) is not dict:
        raise InvalidFrame('root')
    _unicode(value)
    return value
