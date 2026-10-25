#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host mapped-runner uncertainty controls; Python 3.10+."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile
from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = ['normal0', 'normal64', 'normal255', 'fault', 'stop', 'wide',
         'pending-one', 'pending-last', 'pending-budget', 'pending-lost',
         'admission-lost', 'admission-receipt', 'admission-padding',
         'admission-positive', 'admission-error', 'collection-lost',
         'collection-receipt', 'collection-padding', 'collection-kind',
         'collection-error', 'pending-malformed', 'input-close-error',
         'output-close-error', 'read-error', 'not-eof']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='runner-uncertainty-', dir=ROOT / 'build'))
    print(work, flush=True)
    pin = ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
    cc_pin = json.loads(pin.read_text())['tools']['clang']
    if sha(Path(cc_pin['path'])) != cc_pin['sha256']:
        raise RuntimeError('compiler pin mismatch')
    inputs = [HERE / n for n in ('runner.c', 'mapped-runner.h', 'native-io.h',
              'runner-parse.c', 'runner-parse.h', 'runner-result.c', 'runner-result.h',
              'mapped-controls.c', 'mapped-controls.h', 'check-mapped.py', 'process.py')]
    inputs += [HERE.parent / 'native-channel/channel.h',
               ROOT / 'docs/evidence/runner-uncertainty-2026-09-06/change-review.md']
    report = {'status': 'incomplete', 'scope': 'host exchange seams; no native recovery',
              'compiler': cc_pin, 'pin_sha256': sha(pin), 'python': sys.version,
              'platform': platform.platform(), 'inventory': CASES, 'commands': [],
              'cases': [], 'sources': {str(p): sha(p) for p in inputs}}
    snapshot = work / 'sources'
    snapshot.mkdir()
    for p in inputs:
        (snapshot / p.name).write_bytes(p.read_bytes())
    env = clean_env(work)
    env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    def command(label, argv, expected=0):
        result = run(argv, cwd=work, env=env, work=work, label=label, timeout=30)
        report['commands'].append({'label': label, 'process': result.record})
        save()
        if not result.record['complete'] or result.returncode != expected:
            raise RuntimeError(label + ': unexpected execution; see retained logs')
        return result

    save()
    try:
        cc = [cc_pin['path'], '--no-default-config']
        sdk = command('host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
        resource = Path(command('resource-dir', cc + ['-print-resource-dir']).stdout.decode().strip())
        runtime = resource / 'lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib'
        report['sanitizer_runtime'] = {'path': str(runtime), 'sha256': sha(runtime)}
        flags = ['-std=c17', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-Wpedantic',
                 '-Wconversion', '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
                 '-Wmissing-prototypes', '-fno-omit-frame-pointer', '-fsanitize=undefined',
                 '-fno-sanitize-recover=all', '-isysroot', sdk, '-I', str(HERE)]
        objects = []
        for name, defines in [('runner-parse', []),
                              ('runner-result', ['-Dar_terminal_exit=result_policy']),
                              ('mapped-controls', ['-DNATIVE_RUNNER_STARTUP'])]:
            obj = work / (name + '.o')
            command(name + '-compile', cc + flags + defines + ['-c', str(HERE / (name + '.c')),
                    '-o', str(obj)])
            objects.append(str(obj))
        original = (HERE / 'mapped-runner.h').read_text()
        lost = '        if (!native_exchange(q, 32, r))\n            return 1;'
        mutations = [
            ('retry-lost', lost, lost.replace('return 1;', 'continue;'),
             'collection-lost', 'no-after-unknown-or-malformed'),
            ('extra-poll', 'turn < 100000', 'turn < 100001',
             'pending-budget', 'collection-budget'),
            ('skip-close', 'int input_closed = close(3) == 0;', 'int input_closed = 1;',
             'normal0', 'collection-after-input-close'),
            ('erase-detail', 'memset(r, 0xcc, sizeof r);',
             'memset(r, 0xcc, sizeof r);\n    terminal.detail = 0;',
             'normal64', 'raw-terminal-facts'),
        ]
        variants = [('controls', original, CASES, None)]
        for name, anchor, replacement, case, oracle in mutations:
            if original.count(anchor) != 1:
                raise RuntimeError(name + ': mutation anchor changed')
            variants.append((name, original.replace(anchor, replacement), [case], oracle))
        for name, header, cases, oracle in variants:
            private = work / name
            private.mkdir()
            (private / 'mapped-runner.h').write_text(header)
            (private / 'runner.c').write_bytes((HERE / 'runner.c').read_bytes())
            obj = private / 'runner.o'
            command(name + '-compile', cc + flags + ['-DNATIVE_RUNNER_STARTUP',
                    '-DNATIVE_MAPPED_RESULTS', '-Dmain=runner_main', '-Dclose=control_close',
                    '-Dread=control_read', '-include', str(HERE / 'mapped-controls.h'),
                    '-c', str(private / 'runner.c'), '-o', str(obj)])
            binary = private / 'controls'
            command(name + '-link', cc + flags + [str(obj)] + objects + ['-o', str(binary)])
            command(name + '-libraries', ['/usr/bin/otool', '-L', str(binary)])
            for case in cases:
                result = command(name + '-' + case, [str(binary), case], 90 if oracle else 0)
                ok = (not result.stdout and result.stderr == ('ORACLE: ' + oracle + '\n').encode()
                      if oracle else not result.stderr and result.stdout == b'PASS: mapped boundary\n')
                report['cases'].append({'variant': name, 'case': case, 'pass': ok,
                    'oracle': oracle, 'header_sha256': sha(private / 'mapped-runner.h'),
                    'binary_sha256': sha(binary)})
                save()
                if not ok:
                    raise RuntimeError(name + '-' + case + ': oracle mismatch')
        for p, digest in report['sources'].items():
            if sha(Path(p)) != digest:
                raise RuntimeError('source changed: ' + p)
        if sha(runtime) != report['sanitizer_runtime']['sha256']:
            raise RuntimeError('runtime changed')
        report['status'] = 'pass'
    finally:
        save()
    print('PASS: 25 mapped scenarios and four semantic mutations')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
