#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Audit pinned historical native evidence offline; never execute its contents."""
import argparse
import gzip
import tarfile
import zlib
import hashlib
import json
import io
import math
from pathlib import Path, PurePosixPath
import sys
import struct
import re
import os
import stat

ROOT = Path(__file__).resolve().parents[1]

MAX_CATALOG = 4 * 1024 * 1024
MAX_PAYLOAD = 64 * 1024 * 1024
IO_SCHEMAS = {'sys-init-native-' + name + '-v1' for name in
              ('io-stop', 'io-retained', 'readiness', 'authority', 'peer')}


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


def read_metadata(path, root=None):
    root = path.parent if root is None else root
    before = checked_path(path, root)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('input must be an ordinary file')
    if before.st_size > MAX_CATALOG:
        raise ValueError('input exceeds 4 MiB')
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError('input changed before read')
        chunks, size = [], 0
        while size <= MAX_CATALOG:
            chunk = os.read(fd, min(65536, MAX_CATALOG + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        after = os.fstat(fd)
        if any(getattr(opened, field) != getattr(after, field) for field in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns')):
            raise ValueError('input changed during read')
        if size > MAX_CATALOG:
            raise ValueError('input exceeds 4 MiB')
        return b''.join(chunks)
    finally:
        os.close(fd)


def decode_text(raw):
    # Preserve Path.read_text's host-default decoding and universal newlines.
    with io.TextIOWrapper(io.BytesIO(raw)) as source:
        return source.read()


def read_text(path, root=None):
    return decode_text(read_metadata(path, root))


def parse_catalog(raw, kind="catalog"):
    if len(raw) > MAX_CATALOG:
        raise ValueError(kind + ' record exceeds 4 MiB')
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
                raise ValueError(kind + ' record exceeds 32 nesting levels')
        elif byte in (93, 125):
            depth -= 1
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate ' + kind + ' JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-finite ' + kind + ' JSON constant')
    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError('non-finite ' + kind + ' JSON number')
        return result
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                          parse_constant=constant, parse_float=finite_float)
    except RecursionError as error:
        raise ValueError(kind + ' JSON parser nesting failure') from error



def parse_receipt(raw):
    record = parse_catalog(raw, 'receipt')
    if not isinstance(record, dict):
        raise ValueError('receipt root must be an object')
    return record


def catalog_fields(value, required, optional=''):
    if not isinstance(value, dict) or not set(required.split()) <= set(value) or set(value) - set((required + ' ' + optional).split()):
        raise ValueError('invalid catalog fields')


def catalog_text(value, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not 1 <= len(value) <= 4096 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('invalid catalog text')
    value.encode('utf-8')


def catalog_path(value):
    catalog_text(value)
    if value.startswith('/') or '\\' in value or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('invalid catalog path')


def validate_catalog(catalog):
    catalog_fields(catalog, 'schema scope bundles')
    if catalog['schema'] != 'sys-init-native-coverage-v1':
        raise ValueError('unsupported catalog schema')
    catalog_text(catalog['scope'])
    bundles = catalog['bundles']
    if not isinstance(bundles, list) or not 1 <= len(bundles) <= 1000:
        raise ValueError('invalid catalog bundles')
    directories, total = set(), 0
    for bundle in bundles:
        catalog_fields(bundle, 'directory manifest_sha256 schema cases', 'native_profile')
        catalog_path(bundle['directory'])
        if bundle['directory'] in directories:
            raise ValueError('duplicate bundles')
        directories.add(bundle['directory'])
        if not isinstance(bundle['manifest_sha256'], str) or re.fullmatch('[0-9a-f]{64}', bundle['manifest_sha256']) is None:
            raise ValueError('invalid catalog manifest digest')
        schema = bundle['schema']
        if not isinstance(schema, str) or schema not in IO_SCHEMAS | {'sys-init-native-init-v1'}:
            raise ValueError('unsupported catalog bundle schema')
        init = schema == 'sys-init-native-init-v1'
        if 'native_profile' in bundle and (not init or bundle['native_profile'] not in ('AENIN001', 'AENIN002')):
            raise ValueError('unsupported catalog native profile')
        cases = bundle['cases']
        if not isinstance(cases, list) or not 1 <= len(cases) <= 1000:
            raise ValueError('invalid catalog cases')
        total += len(cases)
        if total > 10000:
            raise ValueError('catalog exceeds 10000 cases')
        names = set()
        for case in cases:
            catalog_fields(case, 'name marker assertion expected_panic context' if init else 'name marker assertion smoke_exit', 'first_image' if init else '')
            catalog_path(case['name'])
            if '/' in case['name'] or case['name'] in names:
                raise ValueError('invalid or duplicate catalog case name')
            names.add(case['name'])
            catalog_text(case['assertion'], nullable=not init)
            catalog_text(case['marker'], nullable=init)
            if init:
                catalog_text(case['expected_panic'], nullable=True)
                catalog_text(case['context'], nullable=True)
                if case['expected_panic'] is None and case['marker'] is None:
                    raise ValueError('missing catalog init outcome')
                if 'first_image' in case and case['first_image'] != 'service-worker':
                    raise ValueError('unsupported catalog first image')
            elif type(case['smoke_exit']) is not int or not 0 <= case['smoke_exit'] <= 255:
                raise ValueError('invalid catalog smoke exit')


def sha(path, root=None):
    root = path.parent if root is None else root
    before = checked_path(path, root)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('hashed input must be an ordinary file')
    if before.st_size > MAX_PAYLOAD:
        raise ValueError('hashed input exceeds 64 MiB')
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ValueError('hashed input changed before read')
        digest, size = hashlib.sha256(), 0
        while size <= MAX_PAYLOAD:
            chunk = os.read(fd, min(65536, MAX_PAYLOAD + 1 - size))
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        after = os.fstat(fd)
        if any(getattr(opened, field) != getattr(after, field) for field in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns')):
            raise ValueError('hashed input changed during read')
        if size > MAX_PAYLOAD:
            raise ValueError('hashed input exceeds 64 MiB')
        return digest.hexdigest()
    finally:
        os.close(fd)

def inside(root, name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or str(path) != name:
        raise ValueError('non-relative evidence path')
    target = root / name
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('evidence path escapes root')
    return target

def bundle_files(directory, root):
    checked_path(directory, root)
    files, pending, count = set(), [directory], 0
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                count += 1
                if count > 20000:
                    raise ValueError('bundle tree exceeds 20000 entries')
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    pending.append(Path(entry.path))
                elif stat.S_ISREG(mode):
                    files.add(Path(entry.path).relative_to(directory).as_posix())
                else:
                    raise ValueError('bundle contains symlink or special file')
    return files


def verify_manifest(directory, pin, root=None):
    root = directory if root is None else root
    manifest = directory / 'SHA256SUMS.json'
    raw = read_metadata(manifest, root)
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError('manifest pin mismatch')
    files = parse_catalog(raw, 'manifest')
    if not isinstance(files, dict) or not files:
        raise ValueError('empty manifest')
    if len(files) > 10000:
        raise ValueError('manifest exceeds 10000 entries')
    for name, digest in files.items():
        catalog_path(name)
        if name == 'SHA256SUMS.json':
            raise ValueError('manifest must not list itself')
        if not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None:
            raise ValueError('invalid manifest digest')
    expected_files = set(files) | {'SHA256SUMS.json'}
    if bundle_files(directory, root) != expected_files:
        raise ValueError('bundle file inventory differs from manifest')
    for name, digest in files.items():
        if sha(inside(directory, name), root) != digest:
            raise ValueError('evidence digest mismatch: ' + name)
    if bundle_files(directory, root) != expected_files:
        raise ValueError('bundle file inventory differs from manifest')
    if read_metadata(manifest, root) != raw:
        raise ValueError('manifest changed during verification')
    return files


def report_digest(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('invalid report digest')


def validate_report(report, entry):
    init = entry['schema'] == 'sys-init-native-init-v1'
    catalog_fields(report, 'schema result sources_unchanged smp cases commands ' +
                   ('native_profile summary_sha256' if init else 'native_memory native_sha256 sdk_receipt_sha256'),
                   'service_worker_sha256 service_worker_receipt_sha256 build_profile' if init else '')
    for key in ('schema', 'result'):
        catalog_text(report[key])
    for key in ('sources_unchanged', 'smp') + (() if init else ('native_memory',)):
        if type(report[key]) is not bool:
            raise ValueError('invalid report boolean')
    for key in (('summary_sha256',) if init else ('native_sha256', 'sdk_receipt_sha256')):
        report_digest(report[key])
    if init:
        if report['native_profile'] not in ('AENIN001', 'AENIN002'):
            raise ValueError('invalid report native profile')
        worker_fields = {'service_worker_sha256', 'service_worker_receipt_sha256'}
        present = worker_fields & set(report)
        if present and present != worker_fields:
            raise ValueError('incomplete report worker pins')
        if any(c.get('first_image') == 'service-worker' for c in entry['cases']) and present != worker_fields:
            raise ValueError('missing report worker pins')
        for key in present:
            report_digest(report[key])
        if 'build_profile' in report:
            expected = 'retained-sampling-v1' + ('-abi15' if report['native_profile'] == 'AENIN002' else '')
            if report['build_profile'] != expected:
                raise ValueError('invalid report build profile')
    cases = report['cases']
    if not isinstance(cases, list) or not 1 <= len(cases) <= 1000:
        raise ValueError('invalid report case list')
    for case in cases:
        catalog_fields(case, 'name result context expected_panic marker envelope_sha256 iso_sha256 serial_sha256 supervisor_sha256' if init else
                       'case result smoke_exit marker envelope_sha256 image_sha256 serial_sha256')
        name = case['name' if init else 'case']
        catalog_path(name)
        if '/' in name:
            raise ValueError('invalid report case name')
        catalog_text(case['result'])
        catalog_text(case['marker'], nullable=init)
        for key in ('envelope_sha256', 'serial_sha256') + (('iso_sha256', 'supervisor_sha256') if init else ('image_sha256',)):
            report_digest(case[key])
        if init:
            for key in ('context', 'expected_panic'):
                catalog_text(case[key], nullable=True)
        elif type(case['smoke_exit']) is not int or not 0 <= case['smoke_exit'] <= 255:
            raise ValueError('invalid report smoke exit')
    commands = report['commands']
    if not isinstance(commands, list) or not 1 <= len(commands) <= 3004:
        raise ValueError('invalid report commands')
    for command in commands:
        catalog_fields(command, 'argv exit')
        if type(command['exit']) is not int or not -255 <= command['exit'] <= 255:
            raise ValueError('invalid report command exit')
        argv = command['argv']
        if not isinstance(argv, list) or not 1 <= len(argv) <= 1000:
            raise ValueError('invalid report command argv')
        for arg in argv:
            if arg == '':
                continue
            catalog_text(arg)


def check_cases(report, entry):
    if (report['schema'] != entry['schema'] or report['result'] != 'pass'
            or report.get('sources_unchanged') is not True
            or report.get('native_memory') is not False or report.get('smp') is not False):
        raise ValueError('unsupported or incomplete native report')
    expected = {c['name']:c for c in entry['cases']}
    cases = report['cases']
    names = [c['case'] for c in cases]
    if (not expected or len(expected) != len(entry['cases']) or len(names) != len(set(names))
            or set(names) != set(expected)):
        raise ValueError('missing, duplicate or unexpected cases')
    commands = report['commands']
    if len(commands) != len(cases)*3 or any('outcome' in c for c in commands):
        raise ValueError('missing or interrupted commands')
    for index, case in enumerate(cases):
        wanted = expected[case['case']]
        if (case['result'] != 'pass' or type(case['smoke_exit']) is not int
                or case['smoke_exit'] != wanted['smoke_exit'] or case['marker'] != wanted['marker']):
            raise ValueError('wrong semantic case result')
        for command, code in zip(commands[index*3:index*3+3], (0,0,wanted['smoke_exit'])):
            if type(command.get('exit')) is not int or command['exit'] != code:
                raise ValueError('wrong command outcome')
    return expected

def check_init_cases(report, entry):
    profile = entry.get('native_profile', 'AENIN001')
    if (profile not in ('AENIN001', 'AENIN002')
            or report['schema'] != entry['schema'] or report['result'] != 'pass'
            or report.get('sources_unchanged') is not True
            or report.get('native_profile') != profile or report.get('smp') is not False):
        raise ValueError('unsupported or incomplete init report')
    expected = {c['name']: c for c in entry['cases']}
    names = [c['name'] for c in report['cases']]
    if (not expected or len(expected) != len(entry['cases'])
            or len(names) != len(set(names)) or set(names) != set(expected)):
        raise ValueError('missing, duplicate or unexpected init cases')
    commands = report['commands']
    # Four dependency/tool receipts precede three commands for each target case.
    if (len(commands) != 4 + 3 * len(names)
            or any('outcome' in c or type(c.get('exit')) is not int or c['exit'] != 0
                   for c in commands)):
        raise ValueError('missing, failed or interrupted init commands')
    for case in report['cases']:
        wanted = expected[case['name']]
        if (case['result'] != 'pass' or any(case[k] != wanted[k]
                for k in ('expected_panic', 'context', 'marker'))):
            raise ValueError('wrong init semantic result')
    return expected

def init_envelope(raw, profile="AENIN001"):
    if profile not in ("AENIN001", "AENIN002"): raise ValueError("unsupported init profile")
    if len(raw) < 56: raise ValueError('short init envelope')
    magic, a, b, c, reserved = struct.unpack_from('<8sIIII', raw)
    if (magic != profile.encode('ascii') or reserved or not 0 < a <= 1048576
            or not 0 < b <= 1048576 or not 0 < c <= (8192 if profile == "AENIN002" else 4096) or len(raw) != 56+a+b+c):
        raise ValueError('invalid bounded init envelope')
    return raw[24:56], raw[56:56+a], raw[56+a:56+a+b], raw[56+a+b:]

def check_io_envelope(raw, native_digest, supervisor):
    if len(raw) < 48:
        raise ValueError('short I/O envelope')
    magic, image_size, supervisor_size = struct.unpack_from('<8sII', raw)
    if (magic != b'AENFD001' or not 0 < image_size <= 1048576
            or not 0 < supervisor_size <= 4096
            or len(raw) != 48 + image_size + supervisor_size):
        raise ValueError('invalid bounded I/O envelope')
    native = b'AENATC01' + raw[16:48 + image_size]
    if hashlib.sha256(native).hexdigest() != native_digest:
        raise ValueError('I/O native envelope correspondence mismatch')
    if raw[48 + image_size:] != supervisor:
        raise ValueError('I/O embedded supervisor mismatch')


def check_init_serial(lines, wanted):
    markers = {'AETHER NATIVE INIT PASS', 'AETHER NATIVE INIT CLOSED',
               'AETHER NATIVE INIT LARGE PASS', 'AETHER NATIVE INIT LARGE CLOSED'}
    panic = wanted['expected_panic']
    expected_marker = 'AETHER PANIC: '+panic if panic else wanted['marker']
    outcomes = [line for line in lines if line in markers or line.startswith('AETHER PANIC:')]
    if outcomes != [expected_marker]: raise ValueError('wrong init serial outcome')
    assertion = wanted['assertion']
    if assertion not in lines or lines.index(assertion) >= lines.index(expected_marker):
        raise ValueError('init assertion missing or out of order')

def receipt_collection(value, kind, maximum):
    if not isinstance(value, kind) or not 1 <= len(value) <= maximum:
        raise ValueError('invalid receipt collection')


def receipt_integer(value, maximum):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError('invalid receipt integer')


def receipt_digests(value):
    receipt_collection(value, dict, 10000)
    for name, digest in value.items():
        catalog_path(name)
        report_digest(digest)


def receipt_argv(value):
    receipt_collection(value, list, 1000)
    for arg in value:
        if arg != '':
            catalog_text(arg)


def receipt_commands(value):
    receipt_collection(value, list, 1000)
    for argv in value:
        receipt_argv(argv)


def receipt_tools(value):
    receipt_collection(value, dict, 64)
    for name, tool in value.items():
        catalog_text(name)
        catalog_fields(tool, 'path resolved_path sha256 version')
        for key in ('path', 'resolved_path', 'version'):
            catalog_text(tool[key])
        report_digest(tool['sha256'])


def validate_summary(value):
    base = 'inputs scope source_archive_sha256 suites'
    if 'schema' in value:
        catalog_fields(value, base + ' schema native_profile upstream_manifest_sha256 upstream_producer_sha256')
        if value['schema'] != 'sys-init-normalized-producer-v1' or value['native_profile'] != 'AENIN002':
            raise ValueError('invalid normalized producer summary')
        for key in ('upstream_manifest_sha256', 'upstream_producer_sha256'):
            report_digest(value[key])
    elif 'host' in value or 'tools' in value:
        catalog_fields(value, base + ' host tools')
        catalog_text(value['host'])
        receipt_tools(value['tools'])
    else:
        catalog_fields(value, base)
    catalog_text(value['scope'])
    report_digest(value['source_archive_sha256'])
    receipt_digests(value['inputs'])
    receipt_collection(value['suites'], dict, 64)
    if 'init' not in value['suites']:
        raise ValueError('missing init suite')
    for name, suite in value['suites'].items():
        catalog_text(name)
        catalog_fields(suite, 'report_sha256' if 'schema' in value else 'output report_sha256 cases')
        report_digest(suite['report_sha256'])
        if 'schema' not in value:
            catalog_text(suite['output'])
            receipt_integer(suite['cases'], 1000)
            if suite['cases'] == 0:
                raise ValueError('empty producer suite')


def validate_producer(value):
    catalog_fields(value, 'cases commands libc_receipt_sha256 libc_sha256 profile sources status tools tools_lock_sha256')
    if value['status'] != 'pass' or value['profile'] not in ('init', 'init-large'):
        raise ValueError('invalid producer status/profile')
    for key in ('libc_receipt_sha256', 'libc_sha256', 'tools_lock_sha256'):
        report_digest(value[key])
    receipt_digests(value['sources'])
    receipt_tools(value['tools'])
    receipt_commands(value['commands'])
    receipt_collection(value['cases'], list, 1000)
    names = set()
    for case in value['cases']:
        catalog_fields(case, 'name status envelope_sha256 iso_sha256 serial_sha256')
        catalog_path(case['name'])
        if '/' in case['name'] or case['name'] in names or case['status'] != 'pass':
            raise ValueError('invalid producer case')
        names.add(case['name'])
        for key in ('envelope_sha256', 'iso_sha256', 'serial_sha256'):
            report_digest(case[key])


def validate_worker(value):
    catalog_fields(value, 'commands inputs inputs_unchanged libc_sha256 program_headers result schema sdk_receipt_sha256 tools_lock_sha256 tools_used worker_sha256')
    if (value['schema'] != 'sys-init-native-service-worker-v1' or value['result'] != 'pass'
            or value['inputs_unchanged'] is not True):
        raise ValueError('invalid service worker receipt')
    for key in ('libc_sha256', 'sdk_receipt_sha256', 'tools_lock_sha256', 'worker_sha256'):
        report_digest(value[key])
    receipt_digests(value['inputs'])
    for key, name in (('sdk_receipt_sha256', 'inputs/sdk-evidence.json'),
                      ('tools_lock_sha256', 'inputs/tools.lock.json'),
                      ('libc_sha256', 'inputs/libc.a')):
        if value['inputs'].get(name) != value[key]:
            raise ValueError('service worker input identity mismatch')
    receipt_commands(value['commands'])
    receipt_collection(value['tools_used'], list, 64)
    for name in value['tools_used']:
        catalog_text(name)
    if len(set(value['tools_used'])) != len(value['tools_used']):
        raise ValueError('duplicate receipt tool')
    receipt_collection(value['program_headers'], list, 64)
    for row in value['program_headers']:
        if not isinstance(row, list) or len(row) != 8:
            raise ValueError('invalid receipt program header')
        for index, number in enumerate(row):
            receipt_integer(number, (1 << (32 if index < 2 else 64)) - 1)


def receipt_headers(value):
    receipt_collection(value, list, 64)
    for row in value:
        if not isinstance(row, list) or len(row) != 8:
            raise ValueError('invalid receipt program header')
        for index, number in enumerate(row):
            receipt_integer(number, (1 << (32 if index < 2 else 64)) - 1)


def validate_sdk(value, direct=False):
    derived = 'inputs' in value
    common = 'artifacts envelope_sha256 probe_variant scope'
    catalog_fields(value, common + (' commands inputs inputs_unchanged program_headers sdk_receipt_sha256 tools_used' if derived else
                   ' checks compiler_runtime entropy io_adapter_sha256 libc_archive_sha256 libc_patches native_entry output probe_sha256 script_sha256 source_sha256 tools_lock_sha256'))
    if direct and derived:
        raise ValueError('direct SDK receipt required')
    catalog_text(value['scope'])
    report_digest(value['envelope_sha256'])
    if value['probe_variant'] not in (('io-retained', 'io-readiness', 'io-authority', 'io-peer') if derived else ('io',)):
        raise ValueError('invalid SDK probe variant')
    if derived:
        if value['inputs_unchanged'] is not True:
            raise ValueError('changed SDK inputs')
        receipt_digests(value['inputs'])
        report_digest(value['sdk_receipt_sha256'])
        if value['inputs'].get('inputs/sdk-evidence.json') != value['sdk_receipt_sha256']:
            raise ValueError('derived SDK input identity mismatch')
        receipt_commands(value['commands'])
        receipt_collection(value['tools_used'], list, 64)
        for name in value['tools_used']:
            catalog_text(name)
        if len(set(value['tools_used'])) != len(value['tools_used']):
            raise ValueError('duplicate SDK tool')
        receipt_headers(value['program_headers'])
    else:
        for key in ('compiler_runtime', 'entropy', 'native_entry', 'output'):
            catalog_text(value[key])
        for key in ('io_adapter_sha256', 'libc_archive_sha256', 'probe_sha256', 'script_sha256', 'source_sha256', 'tools_lock_sha256'):
            report_digest(value[key])
        receipt_collection(value['checks'], list, 64)
        for check in value['checks']:
            catalog_text(check)
        receipt_collection(value['libc_patches'], list, 64)
        names = set()
        for patch in value['libc_patches']:
            catalog_fields(patch, 'name path before_sha256 after_sha256 old new reference_evidence_sha256 reference_patch_sha256')
            catalog_text(patch['name'])
            catalog_path(patch['path'])
            if patch['name'] in names:
                raise ValueError('duplicate SDK patch')
            names.add(patch['name'])
            for key in ('before_sha256', 'after_sha256', 'reference_evidence_sha256', 'reference_patch_sha256'):
                report_digest(patch[key])
            for key in ('old', 'new'):
                text = patch[key]
                if (not isinstance(text, str) or not 1 <= len(text) <= 65536
                        or any((ord(c) < 32 and c not in '\t\r\n') or ord(c) == 127 for c in text)):
                    raise ValueError('invalid SDK patch text')
    receipt_collection(value['artifacts'], list, 64)
    names = set()
    for artifact in value['artifacts']:
        catalog_fields(artifact, 'name sha256' + ('' if derived else ' bytes program_headers static_syscall_instruction_sites'))
        catalog_text(artifact['name'])
        if artifact['name'] in names:
            raise ValueError('duplicate SDK artifact')
        names.add(artifact['name'])
        report_digest(artifact['sha256'])
        if not derived:
            receipt_integer(artifact['bytes'], 2**64 - 1)
            receipt_integer(artifact['static_syscall_instruction_sites'], 2**32 - 1)
            receipt_headers(artifact['program_headers'])


def validate_io_build(value):
    catalog_fields(value, 'command envelope_sha256 native_sha256 supervisor_sha256 variant')
    receipt_argv(value['command'])
    catalog_text(value['variant'])
    for key in ('envelope_sha256', 'native_sha256', 'supervisor_sha256'):
        report_digest(value[key])


def check_source_archive(raw, expected):
    # Decompression is bounded before tar metadata or member allocation.
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as compressed:
            expanded = compressed.read(32 * 1024 * 1024 + 1)
        if len(expanded) > 32 * 1024 * 1024:
            raise ValueError('source archive expansion limit')
        found = set()
        with tarfile.open(fileobj=io.BytesIO(expanded), mode='r:') as archive:
            for member in archive:
                if len(found) >= 10000:
                    raise ValueError('source archive member limit')
                catalog_path(member.name)
                if (not member.isfile() or member.sparse is not None
                        or member.name in found or not 0 <= member.size <= MAX_CATALOG):
                    raise ValueError('invalid source archive member')
                if member.name not in expected:
                    raise ValueError('unlisted source archive member')
                found.add(member.name)
                digest = hashlib.sha256()
                with archive.extractfile(member) as payload:
                    remaining = member.size
                    while remaining:
                        chunk = payload.read(min(65536, remaining))
                        if not chunk:
                            raise ValueError('short source archive member')
                        remaining -= len(chunk)
                        digest.update(chunk)
                if digest.hexdigest() != expected[member.name]:
                    raise ValueError('source archive digest mismatch')
        if found != set(expected):
            raise ValueError('source archive membership mismatch')
    except (OSError, EOFError, tarfile.TarError, zlib.error) as error:
        raise ValueError('invalid source archive encoding') from error


# Decision 0141: immutable historical omissions, never a general filename waiver.
SOURCE_OMISSION_PINS = {
    '75731e7d6da6a03a8f2801ec87add064295d6d9eac71e147d3ac98effe7dd30e',
    'be0e9edcf0aec0453e02430e68a6ed6c0199b687ce48311555003f57f9e0da15',
    'dc0f35fabe47f8179db83563cc91d84beadee8474e488f38f7b719c7c02a8cad',
    '39e8a3d69b9bc889d4d0f0f65f4ab0647809a08ed9be87d5ea1abb0df832be68',
    '4217e7dff9f8def91dd149494c05682bd256ab0c6e4fbd8f4c71df100c973888',
}
SOURCE_OMISSION_HASHES = {
    'kernel/.DS_Store': 'd78076c5f0254a03f8a01f1b5d0aa3dfdde2be96a69ab132c202385567764681',
    'kernel/arch/.DS_Store': '0e80b85751e0fe54d71851917b79a60773458025e7d41e96ed5560f46626663d',
}


def check_producer_sources(summary, producer, entry):
    historical = (entry['manifest_sha256'] in SOURCE_OMISSION_PINS
                  and summary.get('schema') == 'sys-init-normalized-producer-v1')
    for name, digest in producer['sources'].items():
        if name in summary['inputs']:
            if summary['inputs'][name] != digest:
                raise ValueError('producer source digest mismatch')
        elif not (historical and SOURCE_OMISSION_HASHES.get(name) == digest):
            raise ValueError('producer source missing from archive')


def check_producer_links(summary, producer, worker=None):
    suite = summary['suites']['init']
    if 'cases' in suite and suite['cases'] != len(producer['cases']):
        raise ValueError('producer suite count mismatch')
    if worker is not None:
        for source, target in (('libc_receipt_sha256', 'sdk_receipt_sha256'),
                               ('libc_sha256', 'libc_sha256'),
                               ('tools_lock_sha256', 'tools_lock_sha256')):
            if producer[source] != worker[target]:
                raise ValueError('producer/worker dependency mismatch')


def audit_init(retained, report, entry, content, digest_file):
    expected = check_init_cases(report, entry)
    profile = entry.get("native_profile", "AENIN001")
    summary_path = retained('producer/summary.json')
    if digest_file(summary_path) != report['summary_sha256']:
        raise ValueError('init producer summary mismatch')
    summary = parse_receipt(content(summary_path))
    validate_summary(summary)
    if (digest_file(retained('producer/producer-sources.tar.gz')) != summary['source_archive_sha256']
            or digest_file(retained('producer/init/results.json')) != summary['suites']['init']['report_sha256']):
        raise ValueError('init producer receipt mismatch')
    check_source_archive(content(retained('producer/producer-sources.tar.gz')), summary['inputs'])
    producer_report = parse_receipt(content(retained('producer/init/results.json')))
    validate_producer(producer_report)
    check_producer_sources(summary, producer_report, entry)
    check_producer_links(summary, producer_report)
    if (producer_report.get('status') != 'pass'
            or producer_report.get('profile') != ('init-large' if profile == 'AENIN002' else 'init')):
        raise ValueError('init producer profile mismatch')
    positives = [c for c in producer_report['cases'] if c['name'] == 'positive']
    producer = retained('producer/init/positive/native-c.bin')
    if len(positives) != 1 or digest_file(producer) != positives[0]['envelope_sha256']:
        raise ValueError('init producer envelope mismatch')
    entropy, first, second, _ = init_envelope(content(producer), profile)
    if (first != content(retained('producer/init/helper1.elf'))
            or second != content(retained('producer/init/helper2.elf'))):
        raise ValueError('init producer ELF correspondence mismatch')
    service_worker = None
    if any(case.get('first_image') == 'service-worker' for case in entry['cases']):
        service_worker = content(retained('worker/service-worker.elf'))
        worker_evidence = retained('worker/evidence.json')
        if (digest_file(worker_evidence) != report.get('service_worker_receipt_sha256')
                or digest_file(retained('worker/service-worker.elf')) != report.get('service_worker_sha256')):
            raise ValueError('service worker receipt mismatch')
        worker_report = parse_receipt(content(worker_evidence))
        validate_worker(worker_report)
        check_producer_links(summary, producer_report, worker_report)
        if (worker_report.get('result') != 'pass'
                or worker_report.get('worker_sha256') != report['service_worker_sha256']):
            raise ValueError('incomplete service worker receipt')
        validate_sdk(parse_receipt(content(retained('worker/inputs/sdk-evidence.json'))), direct=True)
        for name, digest in worker_report.get('inputs', {}).items():
            if digest_file(retained('worker/'+name)) != digest:
                raise ValueError('service worker build input mismatch: '+name)
    for case in report['cases']:
        prefix = 'cases/'+case['name']+'/'
        serial = retained(prefix+'native-serial.log')
        envelope = retained(prefix+'native-c.bin')
        supervisor = retained(prefix+'supervisor.raw')
        for path, key in ((serial,'serial_sha256'), (envelope,'envelope_sha256'),
                          (supervisor,'supervisor_sha256')):
            if digest_file(path) != case[key]: raise ValueError('init artifact identity mismatch')
        wanted_first = service_worker if expected[case['name']].get('first_image') == 'service-worker' else first
        if init_envelope(content(envelope), profile) != (entropy, wanted_first, second, content(supervisor)):
            raise ValueError('init consumer envelope correspondence mismatch')
        check_init_serial(decode_text(content(serial)).splitlines(), expected[case['name']])
    return expected

def audit_derived_sdk(sdk, report, retained, content, digest_file):
    for name, digest in sdk['inputs'].items():
        if digest_file(retained('worker/'+name)) != digest:
            raise ValueError('derived SDK build input mismatch')
    if len(sdk['artifacts']) != 1 or sdk['artifacts'][0]['name'] != 'startup':
        raise ValueError('unsupported derived SDK artifact set')
    worker = retained('worker/worker.elf')
    if digest_file(worker) != sdk['artifacts'][0]['sha256']:
        raise ValueError('derived SDK worker identity mismatch')
    envelope = retained('worker/native-c.bin')
    if digest_file(envelope) != sdk['envelope_sha256'] or sdk['envelope_sha256'] != report['native_sha256']:
        raise ValueError('derived SDK envelope identity mismatch')
    raw = content(envelope)
    if not 40 < len(raw) <= 1048576 + 40 or raw[:8] != b'AENATC01':
        raise ValueError('invalid derived SDK envelope')
    if raw[40:] != content(worker):
        raise ValueError('derived SDK ELF correspondence mismatch')


def audit_bundle(root, entry):
    directory = inside(root, entry['directory'])
    files = verify_manifest(directory, entry['manifest_sha256'], root)
    def expected_digest(path):
        name = path.relative_to(directory).as_posix()
        if name not in files:
            raise ValueError('unlisted semantic input: ' + name)
        return files[name]
    def digest_file(path):
        digest = sha(path, root)
        if digest != expected_digest(path):
            raise ValueError('retained digest changed during audit')
        return digest
    def content(path):
        expected = expected_digest(path)
        raw = read_metadata(path, root)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('semantic input differs from manifest')
        return raw
    def retained(name):
        if name not in files: raise ValueError('unlisted required evidence: '+name)
        return inside(directory, name)
    report = parse_receipt(content(retained('results.json')))
    validate_report(report, entry)
    if entry['schema'] == 'sys-init-native-init-v1':
        expected = audit_init(retained, report, entry, content, digest_file)
        verify_manifest(directory, entry['manifest_sha256'], root)
        return dict(directory=entry['directory'],cases=len(expected),files=len(files),result='pass')
    expected = check_cases(report, entry)
    if digest_file(retained('sdk-evidence.json')) != report['sdk_receipt_sha256']:
        raise ValueError('SDK receipt identity mismatch')
    sdk = parse_receipt(content(retained('sdk-evidence.json')))
    validate_sdk(sdk)
    if 'inputs' in sdk:
        nested_sdk = retained('worker/inputs/sdk-evidence.json')
        if digest_file(nested_sdk) != sdk['sdk_receipt_sha256']:
            raise ValueError('derived SDK receipt mismatch')
        validate_sdk(parse_receipt(content(nested_sdk)), direct=True)
        audit_derived_sdk(sdk, report, retained, content, digest_file)
    for case in report['cases']:
        name = case['case']
        serial = retained(name+'-serial.log')
        envelope = retained('clients/'+name+'/supervised.bin')
        if digest_file(serial) != case['serial_sha256'] or digest_file(envelope) != case['envelope_sha256']:
            raise ValueError('case artifact identity mismatch')
        build = parse_receipt(content(retained('clients/'+name+'/build.json')))
        validate_io_build(build)
        if digest_file(retained('clients/'+name+'/supervisor.raw')) != build['supervisor_sha256']:
            raise ValueError('I/O supervisor identity mismatch')
        if build['native_sha256'] != report['native_sha256'] or build['envelope_sha256'] != digest_file(envelope):
            raise ValueError('producer/consumer identity mismatch')
        check_io_envelope(content(envelope), report['native_sha256'],
                          content(retained('clients/'+name+'/supervisor.raw')))
        lines = decode_text(content(serial)).splitlines()
        wanted = expected[name]
        if wanted['marker'] not in lines or (case['smoke_exit'] != 0 and 'AETHER NATIVE IO PASS' in lines):
            raise ValueError('wrong serial outcome')
        if case['smoke_exit'] == 0 and 'NATIVE supervisor result=100 reclaimed=2' not in lines:
            raise ValueError('positive completion missing')
        if wanted['assertion'] and wanted['assertion'] not in lines:
            raise ValueError('semantic rejection assertion missing')
    verify_manifest(directory, entry['manifest_sha256'], root)
    return dict(directory=entry['directory'],cases=len(expected),files=len(files),result='pass')

def main():
    class Parser(argparse.ArgumentParser):
        def error(self, message): self.exit(64, self.prog+': '+message+'\n')
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='sys-init native evidence audit 1')
    parser.parse_args()
    catalog_path = ROOT/'docs/native-coverage.json'
    catalog_raw = read_metadata(catalog_path, ROOT)
    catalog = parse_catalog(catalog_raw)
    validate_catalog(catalog)
    results = [audit_bundle(ROOT,b) for b in catalog['bundles']]
    for entry in catalog['bundles']:
        verify_manifest(inside(ROOT, entry['directory']), entry['manifest_sha256'], ROOT)
    if read_metadata(catalog_path, ROOT) != catalog_raw:
        raise ValueError('catalog changed during audit')
    print(json.dumps(dict(schema='sys-init-native-evidence-audit-v1',result='pass',
                         catalog_sha256=hashlib.sha256(catalog_raw).hexdigest(),bundles=results,
                         recorded_cases=sum(b['cases'] for b in results),native='not-run')))

if __name__ == '__main__':
    try: main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('native evidence audit: '+str(error), file=sys.stderr)
        raise SystemExit(1)
