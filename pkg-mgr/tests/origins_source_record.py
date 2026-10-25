#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Read-only OC-H2 host inspector; not a runtime admission or trust verifier."""
import hashlib
import json
import os
import re
import stat
import sys

MAX_BYTES = 1048576
MAX_INT = 9007199254740991
MAX_OBJECT = 1073741824
TRANSFER_LIMIT = 16777216
TOKEN = re.compile(r'[a-z0-9][a-z0-9._-]{0,63}')
DIGEST = re.compile(r'[0-9a-f]{64}')
HELP = '''Inspect one pinned origins source record as inert data.
Usage: python3 tests/origins_source_record.py RECORD SHA256
Arguments: RECORD is a regular local file; SHA256 pins its complete original bytes.
Options: --help, --version
Example: substitute a local record path and its independently retained digest.
Limits: 1 MiB, ASCII canonical JSON, eight container levels; no fetch or execution.
Result: versioned JSON on stdout; errors on stderr. Success is inspection only.
Recovery: correct the input or pin; never regenerate a pin to hide changed bytes.
Reference: docs/ORIGINS-SOURCE-INSPECTION.md
'''


class Invalid(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def need(condition, code='format-invalid'):
    if not condition:
        raise Invalid(code)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
            + chr(10)).encode('ascii')


def preflight(raw):
    need(len(raw) <= MAX_BYTES, 'limit-exceeded')
    need(raw and all(b < 128 and b != 0 for b in raw))
    # This only bounds JSON nesting; the standard parser owns JSON syntax.
    depth = 0
    quoted = False
    escaped = False
    for b in raw:
        if quoted:
            if escaped:
                escaped = False
            elif b == 92:
                escaped = True
            elif b == 34:
                quoted = False
        elif b == 34:
            quoted = True
        elif b in (91, 123):
            depth += 1
            need(depth <= 8, 'limit-exceeded')
        elif b in (93, 125):
            depth -= 1
            need(depth >= 0)
    need(not quoted and depth == 0)


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'duplicate-key')
        result[key] = value
    return result


def integer(text):
    need(len(text) <= 16 and text.isascii() and text.isdecimal())
    value = int(text)
    need(value <= MAX_INT)
    return value


def invalid_number(_):
    raise Invalid('format-invalid')


def leaves(value):
    if type(value) is str:
        need(len(value) <= 4096 and all(32 <= ord(c) <= 126 for c in value))
    elif type(value) is int:
        need(0 <= value <= MAX_INT)
    elif type(value) is list:
        for item in value:
            leaves(item)
    elif type(value) is dict:
        for key, item in value.items():
            leaves(key)
            leaves(item)
    else:
        raise Invalid('format-invalid')


def fields(value, names):
    need(type(value) is dict and set(value) == set(names.split()))


def text(value, low, high):
    need(type(value) is str and low <= len(value) <= high)


def token(value):
    need(type(value) is str and TOKEN.fullmatch(value) is not None)


def package(value):
    need(type(value) is str and len(value.split('/')) == 2)
    for part in value.split('/'):
        token(part)


def path(value):
    text(value, 1, 240)
    for part in value.split('/'):
        token(part)


def array(value, low, high):
    need(type(value) is list and low <= len(value) <= high)


def ordered(values):
    need(values == sorted(set(values)), 'order-or-duplicate')


def inspect_bytes(raw, expected):
    need(type(expected) is str and DIGEST.fullmatch(expected) is not None, 'pin-invalid')
    preflight(raw)
    need(hashlib.sha256(raw).hexdigest() == expected, 'identity-mismatch')
    try:
        record = json.loads(raw, object_pairs_hook=pairs, parse_int=integer,
                            parse_float=invalid_number, parse_constant=invalid_number)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError):
        raise Invalid('format-invalid') from None
    leaves(record)
    need(canonical(record) == raw, 'noncanonical')
    fields(record, 'schema package version revision required_features inputs recipe patches '
           'helpers options dependencies sdk build host target licenses evidence')
    need(record['schema'] == 'origins-source-v1', 'unsupported-schema')
    package(record['package'])
    text(record['version'], 1, 128)
    need(type(record['revision']) is int and 1 <= record['revision'] <= MAX_INT)
    features = record['required_features']
    array(features, 0, 32)
    for feature in features:
        token(feature)
    ordered(features)
    need(not features, 'unsupported-feature')
    references = {}

    def reference(value):
        fields(value, 'sha256 size')
        need(type(value['sha256']) is str and DIGEST.fullmatch(value['sha256']) is not None)
        need(type(value['size']) is int and 0 <= value['size'] <= MAX_OBJECT)
        old = references.setdefault(value['sha256'], value['size'])
        need(old == value['size'], 'reference-conflict')

    inputs = record['inputs']
    array(inputs, 1, 4096)
    kinds = {}
    for item in inputs:
        fields(item, 'path kind object origin upstream_revision')
        path(item['path'])
        need(type(item['kind']) is str and item['kind'] in ('source', 'recipe', 'patch', 'helper', 'data'))
        reference(item['object'])
        text(item['origin'], 1, 4096)
        text(item['upstream_revision'], 0, 256)
        kinds[item['path']] = item['kind']
    ordered([item['path'] for item in inputs])
    for name in kinds:
        parts = name.split('/')
        need(all('/'.join(parts[:n]) not in kinds for n in range(1, len(parts))), 'path-conflict')
    need(list(kinds.values()).count('recipe') == 1 and 'source' in kinds.values())
    path(record['recipe'])
    need(kinds.get(record['recipe']) == 'recipe')
    for field, kind in (('patches', 'patch'), ('helpers', 'helper')):
        values = record[field]
        array(values, 0, 256)
        for value in values:
            path(value)
        need(len(set(values)) == len(values), 'order-or-duplicate')
        if field == 'helpers':
            ordered(values)
        need(set(values) == {name for name in kinds if kinds[name] == kind})
    options = record['options']
    array(options, 0, 256)
    for option in options:
        fields(option, 'name value')
        token(option['name'])
        text(option['value'], 0, 1024)
    ordered([option['name'] for option in options])
    dependencies = record['dependencies']
    array(dependencies, 0, 1024)
    for dependency in dependencies:
        fields(dependency, 'package record role')
        package(dependency['package'])
        reference(dependency['record'])
        need(type(dependency['role']) is str and dependency['role'] in ('build', 'target'))
    ordered([dependency['package'] for dependency in dependencies])
    reference(record['sdk'])
    for name in ('build', 'host', 'target'):
        token(record[name])
    licenses = record['licenses']
    array(licenses, 1, 256)
    for license_item in licenses:
        fields(license_item, 'expression text')
        text(license_item['expression'], 1, 256)
        reference(license_item['text'])
    ordered([item['expression'] for item in licenses])
    evidence = record['evidence']
    array(evidence, 1, 256)
    for item in evidence:
        reference(item)
    ordered([item['sha256'] for item in evidence])
    return {'schema': 'pkg-origins-inspection-v1', 'status': 'inspection-only',
            'record_sha256': expected, 'package': record['package'],
            'version': record['version'], 'revision': record['revision'],
            'input_count': len(inputs), 'dependency_count': len(dependencies),
            'referenced_object_count': len(references),
            'byte_handoff': 'over-16-mib' if any(n > TRANSFER_LIMIT for n in references.values())
                            else 'within-16-mib',
            'closure': 'unresolved', 'profiles': 'unresolved', 'eligibility': 'not-evaluated'}


def read_record(name):
    # Caller owns stable ancestors; final-component links/FIFOs/devices are rejected.
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'file-type-invalid')
        need(info.st_size <= MAX_BYTES, 'limit-exceeded')
        raw = bytearray()
        while len(raw) <= MAX_BYTES:
            chunk = os.read(fd, min(65536, MAX_BYTES + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        need(len(raw) <= MAX_BYTES, 'limit-exceeded')
        return bytes(raw)
    finally:
        os.close(fd)


def main(args):
    if args == ['--help']:
        sys.stdout.write(HELP)
        return 0
    if args == ['--version']:
        print('pkg-origins-inspector 0.1.0 (host development)')
        return 0
    if len(args) != 2:
        print('[BLOCKED] PKG-ORIGINS-USAGE: Expected RECORD SHA256; see --help.', file=sys.stderr)
        return 64
    try:
        result = inspect_bytes(read_record(args[0]), args[1])
        output = canonical(result)
        while output:
            count = os.write(sys.stdout.fileno(), output)
            if count <= 0:
                raise OSError('output made no progress')
            output = output[count:]
        return 0
    except Invalid as error:
        print('[BLOCKED] PKG-ORIGINS-' + error.code.upper() + ': Record inspection rejected.', file=sys.stderr)
        return 2
    except OSError:
        print('[FAILED] PKG-ORIGINS-IO-ERROR: Could not read input or deliver output.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
