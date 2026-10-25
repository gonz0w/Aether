#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""OC-H1 offline host byte handoff; no recipe or fresh-eligibility operation."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / 'fixtures/origins-exporter'
RUN = Path(tempfile.mkdtemp(prefix='.pkg-mgr-live-origins-', dir=REPO)).resolve()
os.chmod(RUN, 0o700)
print('origins-handoff: retained_root=' + str(RUN), flush=True)
RESULTS = []
COMMANDS = []
ENV = dict(os.environ, LC_ALL='C', PYTHONDONTWRITEBYTECODE='1')
SH = shutil.which('sh')
VERIFIER = REPO / 'mk/verify-metadata.sh'
RECORD = FIXTURE / 'source.kv'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def invoke(name, argv, environment=None):
    """Direct children only: frozen exporter execs Python; fixture stubs spawn none."""
    out = RUN / (name + '.stdout')
    err = RUN / (name + '.stderr')
    command = dict(name=name, argv=[str(a) for a in argv], timeout_seconds=10)
    COMMANDS.append(command)
    with out.open('xb') as stdout, err.open('xb') as stderr:
        try:
            result = subprocess.run(command['argv'], cwd=REPO,
                                    env=environment or ENV, stdout=stdout,
                                    stderr=stderr, timeout=10)
            command['exit'] = result.returncode
        except FileNotFoundError:
            command['exit'] = None
            command['outcome'] = 'tool-unavailable'
        except subprocess.TimeoutExpired:
            command['exit'] = None
            command['outcome'] = 'timeout'
            raise
    return command['exit'], out, err


def tree(root):
    """Snapshot names, types, modes and file bytes; never follow links."""
    result = {}
    for p in [root, *sorted(root.rglob('*'))]:
        info = p.lstat()
        row = {'mode': stat.S_IMODE(info.st_mode), 'type': stat.S_IFMT(info.st_mode)}
        if stat.S_ISREG(info.st_mode):
            row['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
        elif stat.S_ISLNK(info.st_mode):
            row['link'] = os.readlink(p)
        result[str(p.relative_to(root))] = row
    return result


def main():
    require(SH is not None, 'required sh unavailable')
    pin = json.loads((FIXTURE / 'pin.json').read_text())
    expected_files = {'source-store.sh', 'source_store.py', 'LICENSE',
                      'LOCAL-STORE.md', 'payload.bin', 'source.kv'}
    require(set(pin['files']) == expected_files, 'unexpected producer pin inventory')
    for name, digest in pin['files'].items():
        p = FIXTURE / name
        require(not p.is_symlink() and p.is_file(), 'unsafe pinned input: ' + name)
        require(hashlib.sha256(p.read_bytes()).hexdigest() == digest,
                'producer/input pin mismatch: ' + name)
    # Record development interpreter/tool identity, not complete host-library closure.
    tools = {}
    for name in ('sh', 'python3', 'shellcheck', 'dirname', 'wc', 'tr',
                 'sha256sum', 'shasum', 'sha256', 'openssl'):
        path = shutil.which(name)
        if path:
            tools[name] = {'path': path, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}
    (RUN / 'inputs.json').write_text(json.dumps({
        'producer': pin, 'platform': platform.platform(), 'python': sys.version,
        'tools': tools, 'consumer_inputs': {
            str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), VERIFIER, REPO / 'mk/check-root.sh')},
        'limits': 'Host stdlib/shared libraries not a complete bootstrap closure'}, indent=2))
    rc, _, _ = invoke('producer-lint', ['shellcheck', '--norc', '--shell=sh', FIXTURE / 'source-store.sh'])
    require(rc == 0, 'frozen producer lint failed or tool unavailable')
    fields = dict(line.split('=', 1) for line in RECORD.read_text().splitlines())
    digest, size = fields['source_hash'], fields['source_size']
    payload = (FIXTURE / 'payload.bin').read_bytes()
    require(hashlib.sha256(payload).hexdigest() == digest and len(payload) == int(size),
            'external payload identity mismatch')
    store = RUN / 'store'
    producer = [SH, FIXTURE / 'source-store.sh']
    rc, _, _ = invoke('store-init', producer + ['init', store])
    require(rc == 0, 'store init failed')
    rc, _, _ = invoke('store-put', producer + ['put', store, digest, size, FIXTURE / 'payload.bin'])
    require(rc == 0, 'store put failed')
    package = RUN / 'package'
    package.mkdir(mode=0o700)
    layout = dict(ROOT=str(package), PKGNAME='oc-h1', DISTNAME='payload.bin',
                  DISTDIR=str(package / 'distfiles'), DISTFILE=str(package / 'distfiles/payload.bin'), WRKDIR=str(package / 'work/oc-h1'),
                  STAGEDIR=str(package / 'stage/oc-h1'), DESTDIR=str(package / 'stage/oc-h1'),
                  MANIFEST=str(package / 'manifests/oc-h1.manifest'),
                  LOGDIR=str(package / 'logs/oc-h1'), PREFIX='/usr/local')
    rc, _, _ = invoke('package-init', [SH, REPO / 'mk/check-root.sh', 'init'], dict(ENV, **layout))
    require(rc == 0, 'private package root initialization failed')
    # Sentinel data is test-owned, not an invented valid installed package record.
    (package / 'state').mkdir()
    (package / 'state/world').write_bytes(b'preserve-this-test-sentinel')
    before = tree(package)
    (RUN / 'state-before.json').write_text(json.dumps(before, indent=2))
    original_object = tree(store / 'objects')

    def case(name, passed, detail):
        unchanged = tree(package) == before and not (RUN / 'trust-state').exists()
        unchanged = unchanged and tree(store / 'objects') == original_object
        RESULTS.append(dict(case=name, result='pass' if passed and unchanged else 'fail',
                            oracle=detail, state_unchanged=unchanged))
        require(passed and unchanged, 'case failed: ' + name)

    def transfer(name, argv, mutation=None, environment=None):
        rc, target, _ = invoke(name + '-export', argv)
        if rc != 0:
            return {'producer': rc, 'consumer': 'not-run', 'target': target}
        if mutation:
            target.write_bytes(mutation(target.read_bytes()))
        status, out, err = invoke(name + '-verify', [SH, VERIFIER, 'verify-source', RECORD, target], environment)
        return {'producer': rc, 'consumer': status, 'target': target,
                'stdout': out.read_text(), 'stderr': err.read_text()}

    get = producer + ['get', store, digest, size]
    for name in ('exact', 'retry'):
        r = transfer(name, get)
        expected = 'result=pass label=source-bytes-match target=' + str(r['target']) + chr(10)
        case(name, r['consumer'] == 0 and r['target'].read_bytes() == payload and r['stdout'] == expected,
             'exact fixture bytes; verifier source-bytes-match; state unchanged')
    for name, mutation, label in (
        ('same-size-corruption', lambda b: bytes([b[0] ^ 1]) + b[1:], 'source-hash-mismatch'),
        ('truncation', lambda b: b[:-1], 'source-size-mismatch'),
        ('extra-byte', lambda b: b + b'x', 'source-size-mismatch')):
        r = transfer(name, get, mutation)
        expected = 'result=fail label=' + label + ' target=' + str(r['target']) + chr(10)
        case(name, r['consumer'] == 1 and r['stdout'] == expected, label + '; no downstream execution')
    # Deterministic injected producers: errors must gate the actual consumer call.
    for name, count in (('partial-output-failure', 7), ('complete-output-failure', len(payload))):
        code = 'import os,sys; os.write(1,bytes.fromhex(sys.argv[1])); sys.exit(23)'
        r = transfer(name, [sys.executable, '-c', code, payload[:count].hex()])
        case(name, r['producer'] == 23 and r['consumer'] == 'not-run'
             and r['target'].read_bytes() == payload[:count]
             and not (RUN / (name + '-verify.stdout')).exists(),
             'injected producer exit 23; consumer never invoked even for complete bytes')
    r = transfer('missing-exporter', [RUN / 'absent-exporter'])
    case('missing-exporter', r['producer'] is None and r['consumer'] == 'not-run',
         'tool-unavailable; not an identity rejection')
    # Deliberately omit every hash implementation but keep byte-count dependencies.
    limited = RUN / 'no-hash-bin'
    limited.mkdir(mode=0o700)
    for name in ('dirname', 'wc', 'tr'):
        path = shutil.which(name)
        require(path is not None, 'missing required host utility: ' + name)
        (limited / name).symlink_to(path)
    r = transfer('hash-tool-unavailable', get, environment=dict(ENV, PATH=str(limited)))
    expected = 'result=fail label=source-hash-tool-unavailable target=' + str(r['target']) + chr(10)
    case('hash-tool-unavailable', r['consumer'] == 1 and r['stdout'] == expected,
         'consumer source-hash-tool-unavailable, distinct from mismatched identity')
    linked = RUN / 'store-link'
    linked.symlink_to(store, target_is_directory=True)
    rc, out, err = invoke('symlink-root', producer + ['get', linked, digest, size])
    case('symlink-root', rc == 1 and out.read_bytes() == b'' and 'ORIGINS-IO-ERROR:' in err.read_text(),
         'producer no-follow open rejects symlink with I/O status; no exported bytes')
    fifo = RUN / 'fifo'
    os.mkfifo(fifo, 0o600)
    rc, _, err = invoke('fifo-input', producer + ['put', store, digest, size, fifo])
    case('fifo-input', rc == 2 and 'ORIGINS-TYPE-INVALID:' in err.read_text(),
         'nonblocking producer open rejects FIFO type before copying')
    rc, out, err = invoke('dot-root', producer + ['get', str(store) + '/.', digest, size])
    case('dot-root', rc == 2 and out.read_bytes() == b'' and 'ORIGINS-PATH-INVALID:' in err.read_text(),
         'dot component rejected; no exported bytes')
    rc, _, _ = invoke('identical-put', producer + ['put', store, digest, size, FIXTURE / 'payload.bin'])
    case('identical-put', rc == 0, 'identical put preserves stored object and consumer state')
    (RUN / 'state-after.json').write_text(json.dumps(tree(package), indent=2))
    print('PASS: ' + str(len(RESULTS)) + ' OC-H1 cases; integrity only, no recipe/authentication/native claim')


if __name__ == '__main__':
    status = 1
    try:
        main()
        status = 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
    finally:
        (RUN / 'result.json').write_text(json.dumps({'exit': status, 'cases': RESULTS,
            'commands': COMMANDS, 'scope': 'host byte transfer; not fresh eligibility'}, indent=2))
    sys.exit(status)
