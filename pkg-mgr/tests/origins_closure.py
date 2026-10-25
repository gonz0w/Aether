#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""OC-H3 host-review declared closure; no trust, builds or installed-state writes."""
import hashlib
import json
import os
import stat
import sys

import origins_source_record as source

MAX_OBJECT = 16777216
MAX_TOTAL = 33554432
MAX_READ = 67108864
MAX_OBJECTS = 256
MAX_PACKAGES = 64
MAX_EDGES = 256
MAX_DEPTH = 16
HELP = '''Verify a pinned synthetic source closure without executing it.
Usage: python3 tests/origins_closure.py OBJECTS SELECTION SHA256
Arguments: private object directory, local selection file, retained selection digest.
Options: --help, --version
Example: run python3 tests/origins-closure-cases.py for retained fixture inputs.
Limits: host-review schemas only; 64 packages, 256 objects, 32 MiB total.
Success is declared-closure-only; no SDK completeness, trust or base approval.
Reference: docs/ORIGINS-CLOSURE.md
'''


def decode(raw, digest):
    source.preflight(raw)
    source.need(hashlib.sha256(raw).hexdigest() == digest, 'identity-mismatch')
    try:
        value = json.loads(raw, object_pairs_hook=source.pairs, parse_int=source.integer,
                           parse_float=source.invalid_number, parse_constant=source.invalid_number)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError):
        raise source.Invalid('format-invalid') from None
    source.leaves(value)
    source.need(source.canonical(value) == raw, 'noncanonical')
    return value


def ref(value):
    source.fields(value, 'sha256 size')
    source.need(type(value['sha256']) is str and source.DIGEST.fullmatch(value['sha256']) is not None)
    source.need(type(value['size']) is int and 0 <= value['size'] <= MAX_OBJECT, 'object-limit')


def schema(value, name, names):
    source.fields(value, 'schema ' + names)
    source.need(value['schema'] == name, 'unsupported-schema')


class Objects:
    def __init__(self, directory):
        self.fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        info = os.fstat(self.fd)
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            os.close(self.fd)
            raise source.Invalid('root-invalid')
        self.seen = {}
        self.total = 0
        self.read_bytes = 0

    def read(self, reference, metadata=False):
        ref(reference)
        digest, size = reference['sha256'], reference['size']
        source.need(not metadata or size <= source.MAX_BYTES, 'metadata-limit')
        if digest in self.seen:
            source.need(self.seen[digest] == size, 'reference-conflict')
        else:
            source.need(len(self.seen) < MAX_OBJECTS and self.total + size <= MAX_TOTAL, 'closure-limit')
            self.seen[digest] = size
            self.total += size
        # Charge the full bounded read before touching the file, including repeats.
        source.need(self.read_bytes + size + 1 <= MAX_READ, 'read-limit')
        self.read_bytes += size + 1
        try:
            fd = os.open(digest, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.fd)
        except FileNotFoundError:
            raise source.Invalid('object-missing') from None
        try:
            info = os.fstat(fd)
            source.need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'file-type-invalid')
            source.need(info.st_size == size, 'identity-mismatch')
            total = 0
            checksum = hashlib.sha256()
            chunks = []
            while total <= size:
                chunk = os.read(fd, min(65536, size + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                checksum.update(chunk)
                if metadata:
                    chunks.append(chunk)
            source.need(total == size and checksum.hexdigest() == digest, 'identity-mismatch')
            return b''.join(chunks) if metadata else None
        finally:
            os.close(fd)

    def metadata(self, reference):
        return decode(self.read(reference, True), reference['sha256'])


def inspect(directory, selection_path, digest):
    source.need(type(digest) is str and source.DIGEST.fullmatch(digest) is not None, 'pin-invalid')
    selection = decode(source.read_record(selection_path), digest)
    schema(selection, 'pkg-origins-review-selection-v1', 'release roots mapping')
    ref(selection['release'])
    source.array(selection['roots'], 1, MAX_PACKAGES)
    for name in selection['roots']:
        source.package(name)
    source.ordered(selection['roots'])
    source.array(selection['mapping'], 1, MAX_PACKAGES)
    mapping = {}
    for entry in selection['mapping']:
        source.fields(entry, 'package local_name')
        source.package(entry['package'])
        source.token(entry['local_name'])
        mapping[entry['package']] = entry['local_name']
    source.ordered([item['package'] for item in selection['mapping']])
    source.need(len(set(mapping.values())) == len(mapping), 'mapping-collision')
    objects = Objects(directory)
    try:
        release = objects.metadata(selection['release'])
        schema(release, 'pkg-origins-review-release-v1', 'repository profile packages')
        source.need(type(release['repository']) is str and source.DIGEST.fullmatch(release['repository']) is not None)
        profile = objects.metadata(release['profile'])
        schema(profile, 'pkg-origins-review-profile-v1', 'name purpose build host target')
        source.need(profile['purpose'] == 'synthetic-host-fixture', 'profile-unsupported')
        source.token(profile['name'])
        source.need(all(profile[key] == profile['name'] for key in ('build','host','target')), 'profile-unsupported')
        source.array(release['packages'], 1, MAX_PACKAGES)
        catalog = {}
        for entry in release['packages']:
            source.fields(entry, 'package record')
            source.package(entry['package'])
            ref(entry['record'])
            catalog[entry['package']] = entry['record']
        source.ordered([entry['package'] for entry in release['packages']])
        active, complete = set(), set()
        heights = {}
        edges = 0
        sdks = set()

        def visit(name, expected=None, depth=1):
            nonlocal edges
            source.need(depth <= MAX_DEPTH, 'depth-limit')
            source.need(name not in active, 'dependency-cycle')
            source.need(name in catalog, 'package-missing')
            reference = catalog[name]
            source.need(expected is None or expected == reference, 'release-map-conflict')
            if name in complete:
                return
            raw = objects.read(reference, True)
            source.inspect_bytes(raw, reference['sha256'])
            record = json.loads(raw)
            source.need(record['package'] == name, 'package-conflict')
            source.need(all(record[key] == profile[key] for key in ('build','host','target')), 'profile-mismatch')
            active.add(name)
            sdk = objects.metadata(record['sdk'])
            schema(sdk, 'pkg-origins-review-sdk-v1', 'purpose profile inputs')
            source.need(sdk['purpose'] == 'synthetic-host-fixture', 'sdk-unsupported')
            source.need(sdk['profile'] == release['profile'], 'sdk-profile-mismatch')
            source.array(sdk['inputs'], 1, 32)
            for item in sdk['inputs']:
                source.fields(item, 'name object')
                source.token(item['name'])
                objects.read(item['object'])
            source.ordered([item['name'] for item in sdk['inputs']])
            sdks.add(record['sdk']['sha256'])
            for item in record['inputs']:
                objects.read(item['object'])
            for item in record['licenses']:
                objects.read(item['text'])
            for evidence_ref in record['evidence']:
                evidence = objects.metadata(evidence_ref)
                schema(evidence, 'pkg-origins-review-evidence-v1', 'kind objects')
                source.need(evidence['kind'] == 'synthetic', 'evidence-unsupported')
                source.array(evidence['objects'], 1, 32)
                for item in evidence['objects']:
                    objects.read(item)
                source.ordered([item['sha256'] for item in evidence['objects']])
            height = 1
            for dependency in record['dependencies']:
                source.need(edges < MAX_EDGES, 'edge-limit')
                edges += 1
                visit(dependency['package'], dependency['record'], depth + 1)
                height = max(height, 1 + heights[dependency['package']])
            source.need(height <= MAX_DEPTH, 'depth-limit')
            heights[name] = height
            active.remove(name)
            complete.add(name)

        for name in selection['roots']:
            visit(name)
        source.need(set(mapping) == complete, 'mapping-incomplete')
        return {'schema':'pkg-origins-closure-report-v1', 'status':'declared-closure-only',
                'selection_sha256':digest, 'release_sha256':selection['release']['sha256'],
                'packages':[{'package':name,'local_name':mapping[name]} for name in sorted(complete)],
                'dependency_edges':edges, 'object_count':len(objects.seen), 'object_bytes':objects.total,
                'sdk_count':len(sdks), 'eligibility':'not-evaluated', 'sdk_completeness':'not-proven',
                'base_admission':'not-evaluated'}
    finally:
        os.close(objects.fd)


def main(args):
    if args == ['--help']:
        print(HELP, end='')
        return 0
    if args == ['--version']:
        print('pkg-origins-closure 0.1.0 (host review)')
        return 0
    if len(args) != 3:
        print('[BLOCKED] PKG-ORIGINS-CLOSURE-USAGE: Expected OBJECTS SELECTION SHA256.', file=sys.stderr)
        return 64
    try:
        result = source.canonical(inspect(*args))
        while result:
            count = os.write(sys.stdout.fileno(), result)
            if count <= 0:
                raise OSError('output made no progress')
            result = result[count:]
        return 0
    except source.Invalid as error:
        print('[BLOCKED] PKG-ORIGINS-CLOSURE-' + error.code.upper() + ': Closure inspection rejected.', file=sys.stderr)
        return 2
    except OSError:
        print('[FAILED] PKG-ORIGINS-CLOSURE-IO-ERROR: Input or output failed.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
