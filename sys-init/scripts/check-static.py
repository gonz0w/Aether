#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check Python syntax, scoped Rust format/lints and boundary inventory offline."""
import argparse
import hashlib
import json
import os
import selectors
import signal
import stat
import tempfile
import time
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE = 1024 * 1024
MAX_TOTAL = 16 * MAX_FILE


class Blocked(ValueError):
    """A required tool or supported platform is unavailable."""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, json.dumps(message, ensure_ascii=True) + '\n')


def digest(data):
    return hashlib.sha256(data).hexdigest()


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


def read_input(path, root):
    before = checked_path(path, root)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('input must be an ordinary file')
    if before.st_size > MAX_FILE:
        raise ValueError('input exceeds 1 MiB')
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError('input changed before read')
        chunks, size = [], 0
        while size <= MAX_FILE:
            chunk = os.read(fd, min(65536, MAX_FILE + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        after = os.fstat(fd)
        if any(getattr(opened, field) != getattr(after, field) for field in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns')):
            raise ValueError('input changed during read')
        if size > MAX_FILE:
            raise ValueError('input exceeds 1 MiB')
        return b''.join(chunks)
    finally:
        os.close(fd)


def load_record(path, raw=None):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result

    def constant(value):
        raise ValueError('non-finite JSON constant: ' + value)

    if raw is None:
        raw = read_input(path, path.parent)
    if len(raw) > MAX_FILE:
        raise ValueError('record exceeds 1 MiB')
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
                raise ValueError('record nesting exceeds 32 levels')
        elif byte in (93, 125):
            depth -= 1
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except RecursionError as error:
        raise ValueError('record nesting exceeds parser capacity') from error


def fields(value, names):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ValueError('invalid record fields')


def string(value):
    if not isinstance(value, str) or not value or len(value) > 4096 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('invalid record string')
    value.encode('utf-8')


def relative_path(value):
    string(value)
    if value.startswith('/') or '\\' in value or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('invalid relative record path')


def sha256(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('invalid record digest')


def sequence(value, validate, minimum=0):
    if not isinstance(value, list) or not minimum <= len(value) <= 1000:
        raise ValueError('invalid record list')
    for item in value:
        validate(item)


def settings_record(path, raw=None):
    value = load_record(path, raw)
    fields(value, 'schema rust_toolchain rustfmt_version rustfmt_sha256 rustfmt_args rust_sources python_roots python_top_level clippy_version clippy_sha256 clippy_args clippy_modules')
    if value['schema'] != 'sys-init-static-tools-v1':
        raise ValueError('invalid static tools schema')
    for key in ('rust_toolchain', 'rustfmt_version', 'clippy_version'):
        string(value[key])
    for key in ('rustfmt_sha256', 'clippy_sha256'):
        hosts = value[key]
        if not isinstance(hosts, dict) or not 1 <= len(hosts) <= 1000:
            raise ValueError('invalid tool host map')
        for host, digest_value in hosts.items():
            string(host)
            sha256(digest_value)
    for key in ('rustfmt_args', 'clippy_args'):
        sequence(value[key], string, 1)
    for key in ('rust_sources', 'python_roots', 'python_top_level', 'clippy_modules'):
        sequence(value[key], relative_path, 1 if key == 'rust_sources' else 0)
        if len(set(value[key])) != len(value[key]):
            raise ValueError('duplicate source scope entry')
    return value


def boundary_record(path, raw=None):
    value = load_record(path, raw)
    fields(value, 'schema scope records')
    if value['schema'] != 'sys-init-native-boundaries-v1':
        raise ValueError('invalid native boundaries schema')
    string(value['scope'])
    def site(item):
        fields(item, 'line text')
        if type(item['line']) is not int or item['line'] <= 0:
            raise ValueError('invalid boundary line')
        string(item['text'])
    def record(item):
        fields(item, 'file sha256 sites review reference owner follow_up')
        relative_path(item['file'])
        relative_path(item['reference'])
        sha256(item['sha256'])
        for key in ('review', 'owner', 'follow_up'):
            string(item[key])
        sequence(item['sites'], site, 1)
    sequence(value['records'], record, 1)
    return value


def command(argv, data=None, timeout=10, limit=4 * MAX_FILE):
    # Trusted tools must not detach. Bound merged output and own the process group.
    output = bytearray()
    end = time.monotonic() + timeout
    with tempfile.TemporaryFile() as source:
        source.write(data or b'')
        source.seek(0)
        try:
            child = subprocess.Popen(argv, stdin=source, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, start_new_session=True)
        except OSError as error:
            raise Blocked(str(error)) from error
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(child.stdout, selectors.EVENT_READ)
                while selector.get_map():
                    remaining = end - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(argv, timeout)
                    for key, _ in selector.select(remaining):
                        block = os.read(key.fd, min(65536, limit - len(output) + 1))
                        if not block:
                            selector.unregister(key.fileobj)
                            continue
                        if len(output) + len(block) > limit:
                            raise ValueError('tool output exceeds limit')
                        output.extend(block)
            code = child.wait(timeout=max(0, end - time.monotonic()))
            if code:
                raise ValueError('tool failed: ' + output[:4096].decode('utf-8', 'replace'))
        except BaseException as error:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
            if isinstance(error, subprocess.TimeoutExpired):
                raise Blocked('tool timed out') from error
            raise
        finally:
            child.stdout.close()
    return bytes(output)


def identify_tool(path, expected_hash, expected_version, label="rustfmt"):
    try:
        actual = digest(path.read_bytes())
    except OSError as error:
        raise Blocked('required ' + label + ' unavailable') from error
    if actual != expected_hash:
        raise Blocked(label + ' digest differs from reviewed tool')
    if command([str(path), '--version']).decode().strip() != expected_version:
        raise Blocked(label + ' version differs from reviewed tool')
    return actual


def sources(root, settings):
    paths = set()
    for name in settings['python_roots']:
        if (root / name).exists() or (root / name).is_symlink():
            checked_path(root / name, root)
        paths.update((root / name).rglob('*.py'))
    for name in settings['python_top_level']:
        if (root / name).exists() or (root / name).is_symlink():
            checked_path(root / name, root)
        paths.update((root / name).glob('*.py'))
    paths.update(root / name for name in settings['rust_sources'])
    paths.update(root / name for name in settings.get('clippy_modules', []))
    if not paths or not settings['rust_sources'] or not any(p.suffix == '.py' for p in paths):
        raise ValueError('empty required static-check scope')
    if len(paths) > 1000:
        raise ValueError('static source count exceeds limit')
    data = {}
    total = 0
    for path in sorted(paths):
        raw = read_input(path, root)
        total += len(raw)
        if total > MAX_TOTAL:
            raise ValueError('static source total exceeds 16 MiB')
        data[path] = raw
    return data


def check_python(raw, name):
    # compile catches syntax and context errors; never execute the resulting code.
    compile(raw, name, 'exec', dont_inherit=True)


def check_rust(raw, path, tool, args):
    formatted = command([str(tool), *args], raw)
    if formatted != raw:
        raise ValueError('rustfmt changes required: ' + str(path))


def check_clippy(root, data, tool, settings):
    diagnostics = {}
    with tempfile.TemporaryDirectory(prefix='sys-init-clippy-') as directory:
        private = Path(directory)
        for source in settings['rust_sources'] + settings['clippy_modules']:
            target = private / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data[root / source])
        for index, source in enumerate(settings['rust_sources']):
            output = command([str(tool), *settings['clippy_args'],
                              str(private / source), '-o', str(private / (str(index) + '.rmeta'))])
            diagnostics[source] = output.decode('utf-8', 'replace')
    return diagnostics


def check_boundaries(root, raw=None):
    path = root / 'docs/native-boundaries.json'
    inventory = boundary_record(path, read_input(path, root) if raw is None else raw)
    expected = {}
    for record in inventory['records']:
        name = record['file']
        if name in expected:
            raise ValueError('duplicate native boundary record')
        expected[name] = record
    actual = {}
    if (root / 'prototypes').exists():
        checked_path(root / 'prototypes', root)
    for path in sorted((root / 'prototypes').rglob('*')):
        if path.suffix not in ('.rs', '.c'):
            continue
        raw_source = read_input(path, root)
        sites = [dict(line=index, text=line.strip())
                 for index, line in enumerate(raw_source.decode().splitlines(), 1)
                 if re.search(r'\bunsafe\b|extern "C"|__asm__', line)]
        if sites:
            actual[str(path.relative_to(root))] = dict(
                sites=sites, sha256=digest(raw_source))
    if not actual or set(actual) != set(expected):
        raise ValueError('native boundary inventory coverage changed; review required')
    for name, value in actual.items():
        if any(expected[name][key] != value[key] for key in ('sites', 'sha256')):
            raise ValueError('native boundary source changed; review required: ' + name)
    return len(actual)


def run(root):
    record_paths = [root / 'docs/native-boundaries.json', root / 'docs/static-tools.json']
    records = {path: read_input(path, root) for path in record_paths}
    boundary_files = check_boundaries(root, records[record_paths[0]])
    settings = settings_record(record_paths[1], records[record_paths[1]])
    host = platform.system() + '-' + platform.machine()
    expected = settings['rustfmt_sha256'].get(host)
    if expected is None:
        raise Blocked('no reviewed rustfmt identity for host ' + host)
    path = Path(command(['rustup', 'which', '--toolchain', settings['rust_toolchain'],
                         'rustfmt']).decode().strip())
    identity = identify_tool(path, expected, settings['rustfmt_version'])
    clippy_hash = settings['clippy_sha256'].get(host)
    if clippy_hash is None:
        raise Blocked('no reviewed Clippy identity for host ' + host)
    clippy = Path(command(['rustup', 'which', '--toolchain', settings['rust_toolchain'],
                           'clippy-driver']).decode().strip())
    clippy_identity = identify_tool(clippy, clippy_hash, settings['clippy_version'], 'Clippy')
    data = sources(root, settings)
    for source, raw in data.items():
        if source.suffix == '.py':
            check_python(raw, str(source.relative_to(root)))
        elif str(source.relative_to(root)) in settings['rust_sources']:
            check_rust(raw, source.relative_to(root), path, settings['rustfmt_args'])
    diagnostics = check_clippy(root, data, clippy, settings)
    if any(read_input(p, root) != raw for p, raw in data.items()):
        raise ValueError('source changed during static checks')
    if digest(path.read_bytes()) != identity:
        raise Blocked('rustfmt changed during static checks')
    if digest(clippy.read_bytes()) != clippy_identity:
        raise Blocked('Clippy changed during static checks')
    check_boundaries(root)
    if any(read_input(path, root) != raw for path, raw in records.items()):
        raise ValueError('static record changed during checks')
    return dict(schema='sys-init-static-v1', result='pass', host=host,
                python=sys.version, rustfmt=settings['rustfmt_version'],
                boundary_files=boundary_files, tool_sha256=identity, python_files=sum(p.suffix == '.py' for p in data),
                rust_files=len(settings['rust_sources']),
                clippy=settings['clippy_version'], clippy_sha256=clippy_identity,
                clippy_diagnostics=diagnostics,
                sources={str(p.relative_to(root)): digest(raw) for p, raw in data.items()},
                scope='Python syntax, two host Rust formats and Clippy with pure imported modules; no native execution')


def main():
    parser = Parser(description=__doc__, epilog='Run from any directory: python3 '
                    'scripts/check-static.py. Requires the pinned Rust 1.98.0 rustfmt '
                    'on a reviewed host. See docs/STATIC-CHECKS.md for scope and recovery.')
    parser.add_argument('--version', action='version', version='sys-init static checks 1')
    parser.parse_args()
    try:
        report = run(ROOT)
    except (OSError, ValueError, SyntaxError) as error:
        blocked = isinstance(error, Blocked)
        report = dict(schema='sys-init-static-v1', result='blocked' if blocked else 'fail',
                      diagnostic=str(error))
        print(json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        print(json.dumps(report, ensure_ascii=True))
        return 2 if blocked else 1
    print(json.dumps(report, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
