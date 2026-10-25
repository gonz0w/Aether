#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check local quality records and reviewed bytes; no runtime conformance claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_RECORD = 1024 * 1024


def checked_path(path, root):
    anchor = root.absolute()
    if anchor.is_symlink():
        raise ValueError('input root must not be a symlink')
    try:
        parts = path.absolute().relative_to(anchor).parts
    except ValueError as error:
        raise ValueError('source must be an owned ordinary file') from error
    if any(part in ('.', '..') for part in parts):
        raise ValueError('source must be an owned ordinary file')
    current = anchor
    for part in parts:
        current /= part
        if stat.S_ISLNK(current.lstat().st_mode):
            raise ValueError('source must be an owned ordinary file; symlink component')
    return current.lstat()


def read_record(path, root=None):
    root = path.parent if root is None else root
    before = checked_path(path, root)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('input must be an ordinary file')
    if before.st_size > MAX_RECORD:
        raise ValueError('input exceeds 1 MiB')
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError('input changed before read')
        chunks, size = [], 0
        while size <= MAX_RECORD:
            chunk = os.read(fd, min(65536, MAX_RECORD + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        after = os.fstat(fd)
        if any(getattr(opened, field) != getattr(after, field) for field in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns')):
            raise ValueError('input changed during read')
        if size > MAX_RECORD:
            raise ValueError('input exceeds 1 MiB')
        return b''.join(chunks)
    finally:
        os.close(fd)


def parse_record(raw):
    if len(raw) > MAX_RECORD:
        raise ValueError('quality record exceeds 1 MiB')
    depth, quoted, escaped = 0, False, False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            if depth > 32:
                raise ValueError('quality record exceeds 32 nesting levels')
        elif byte in (93, 125):
            depth -= 1
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate quality JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-finite quality JSON constant')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except RecursionError as error:
        raise ValueError('quality JSON parser nesting failure') from error


def fields(value, required, optional=''):
    if not isinstance(value, dict) or not set(required.split()) <= set(value) or set(value) - set((required + ' ' + optional).split()):
        raise ValueError('invalid quality record fields')


def text(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 4096 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('invalid quality record string')
    value.encode('utf-8')


def relative(value):
    text(value)
    if value.startswith('/') or '\\' in value or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('nonlocal or unnormalized reference')


def pin(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('invalid quality digest')


def entries(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 1000:
        raise ValueError('invalid quality record list')


def references(value):
    entries(value)
    for name in value:
        relative(name)
    if len(set(value)) != len(value):
        raise ValueError('duplicate quality reference')


def validate_inventory(record):
    fields(record, 'schema scope snapshot snapshot_manifest_sha256 process surfaces gaps')
    if record['schema'] != 'sys-init-quality-inventory-v1':
        raise ValueError('unsupported inventory schema')
    text(record['scope'])
    relative(record['snapshot'])
    pin(record['snapshot_manifest_sha256'])
    references(record['process'])
    entries(record['surfaces'])
    entries(record['gaps'])
    for item in record['surfaces']:
        fields(item, 'id owner status layer reference evidence tests oracle stage')
        for key in ('id', 'owner', 'status', 'layer', 'oracle', 'stage'):
            text(item[key])
        for key in ('reference', 'evidence'):
            relative(item[key])
        references(item['tests'])
        if item['status'] != 'experimental' or item['layer'] not in ('model', 'host', 'target'):
            raise ValueError('unsupported coverage claim')
    for item in record['gaps']:
        fields(item, 'id owner status topic milestone backlog', 'reference review_evidence')
        for key in ('id', 'owner', 'status', 'topic', 'milestone'):
            text(item[key])
        if item['status'] != 'open':
            raise ValueError('gap needs explicit disposition')
        for key in ('backlog', 'reference', 'review_evidence'):
            if key in item:
                relative(item[key])

    ids = [item['id'] for item in record['surfaces'] + record['gaps']]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate ID or missing owner')


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or not 1 <= len(manifest) <= 1000:
        raise ValueError('empty or oversized snapshot inventory')
    for name, value in manifest.items():
        relative(name)
        pin(value)


def local_file(root, name):
    if not isinstance(name, str) or not name:
        raise ValueError('missing local file reference')
    path = Path(name)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('nonlocal reference')
    result = root / path
    try:
        mode = checked_path(result, root).st_mode
    except (FileNotFoundError, NotADirectoryError) as error:
        raise ValueError('missing or escaping local file: ' + name) from error
    if not stat.S_ISREG(mode):
        raise ValueError('reference must be an ordinary file: ' + name)
    return result


def digest(path, root=None):
    return hashlib.sha256(read_record(path, root)).hexdigest()


def snapshot_files(root, manifest):
    expected = set(manifest) | {'SHA256SUMS.json'}
    actual, pending, count = set(), [root], 0
    if root.is_symlink():
        raise ValueError('snapshot root is a symlink')
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                count += 1
                if count > 2000:
                    raise ValueError('snapshot tree exceeds 2000 entries')
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    pending.append(Path(entry.path))
                elif stat.S_ISREG(mode):
                    actual.add(str(Path(entry.path).relative_to(root)))
                else:
                    raise ValueError('snapshot contains symlink or special file')
    if actual != expected:
        raise ValueError('snapshot file inventory differs from manifest')


def snapshot_path(root, path):
    current = root
    if current.is_symlink():
        raise ValueError('snapshot input root is a symlink')
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise ValueError('snapshot path contains symlink')


def check(root=ROOT):
    inventory_path = root / 'docs/quality-inventory.json'
    inventory_raw = read_record(inventory_path, root)
    record = parse_record(inventory_raw)
    validate_inventory(record)
    manifest_path = local_file(root, record['snapshot'] + '/SHA256SUMS.json')
    snapshot_path(root, manifest_path)
    manifest_raw = read_record(manifest_path, root)
    if hashlib.sha256(manifest_raw).hexdigest() != record['snapshot_manifest_sha256']:
        raise ValueError('review snapshot manifest changed')
    manifest = parse_record(manifest_raw)
    validate_manifest(manifest)
    snapshot_files(manifest_path.parent, manifest)
    for name, pin in manifest.items():
        if digest(local_file(manifest_path.parent, name), root) != pin:
            raise ValueError('reviewed source changed: ' + name)
    for name in record['process']:
        local_file(root, name)
    if not record['process'] or not record['surfaces'] or not record['gaps']:
        raise ValueError('incomplete process inventory')
    seen = set()
    for item in record['surfaces'] + record['gaps']:
        if not item['id'] or item['id'] in seen or not item['owner']:
            raise ValueError('duplicate ID or missing owner')
        seen.add(item['id'])
    for item in record['surfaces']:
        if item['status'] != 'experimental' or item['layer'] not in ('model', 'host', 'target'):
            raise ValueError('unsupported coverage claim')
        if not item['oracle'] or not item['stage'] or not item['tests']:
            raise ValueError('missing test selection or oracle')
        for name in [item['reference'], item['evidence']] + item['tests']:
            local_file(root, name)
    for item in record['gaps']:
        if item['status'] != 'open' or not item['topic'] or not item['milestone']:
            raise ValueError('gap needs explicit disposition')
        local_file(root, item['backlog'])
        for key in ('reference', 'review_evidence'):
            if key in item:
                local_file(root, item[key])
    snapshot_path(root, manifest_path)
    snapshot_files(manifest_path.parent, manifest)
    for name, pin in manifest.items():
        if digest(local_file(manifest_path.parent, name), root) != pin:
            raise ValueError('reviewed source changed: ' + name)
    if read_record(inventory_path, root) != inventory_raw or read_record(manifest_path, root) != manifest_raw:
        raise ValueError('quality record changed during check')
    return {'schema': 'sys-init-quality-check-v1', 'result': 'pass',
            'scope': 'record structure and reviewed bytes only',
            'surfaces': len(record['surfaces']), 'open_gaps': len(record['gaps'])}


if __name__ == '__main__':
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            self.exit(64, self.prog + ': ' + message + '\n')

    parser = Parser(description=__doc__, epilog=(
        'Example: python3 scripts/check-quality-process.py. '
        'Offline; see docs/QUALITY-PROCESS.md for scope and follow-up.'))
    parser.add_argument('--version', action='version',
                        version='sys-init quality process 1')
    parser.parse_args()
    try:
        print(json.dumps(check()))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('quality process: ' + ascii(str(error)), file=sys.stderr)
        raise SystemExit(1)
