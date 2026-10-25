#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host-only proposed local output controls; Python 3.10+."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
import tempfile
from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[FAILED] ' + ascii(message)[1:-1] + '\n')


def main():
    parser = Parser(description=__doc__, epilog=(
        'Example: python3 -B experiments/command-runner/check-local-output.py. '
        'Uses pinned local tools; host-only tests, no native execution. '
        'Exit: 0 pass, 1 failure, 64 usage, 130 interruption.'))
    parser.add_argument('--version', action='version', version='local-output-check 0.1.0')
    parser.add_argument('--plain', action='store_true', help='plain ASCII output (the default)')
    parser.add_argument('--suite', choices=('delivery', 'frontend'), default='delivery',
                        help='host test suite (default: delivery)')
    args = parser.parse_args()
    frontend = args.suite == 'frontend'
    work = Path(tempfile.mkdtemp(prefix='runner-local-output-', dir=ROOT / 'build'))
    print(work, flush=True)
    pin = ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
    compiler = json.loads(pin.read_text())['tools']['clang']
    if sha(Path(compiler['path'])) != compiler['sha256']:
        raise RuntimeError('compiler pin mismatch')
    fixtures = ROOT / 'docs/proposals/runner-local'
    retained = ROOT / 'docs/evidence/runner-local-proposal-2026-09-06/fixtures'
    if sha(fixtures / 'manifest.json') != sha(retained / 'manifest.json'):
        raise RuntimeError('proposal fixture manifest changed')
    manifest = json.loads((retained / 'manifest.json').read_text())
    for entry in manifest['files']:
        if sha(fixtures / entry['file']) != entry['sha256']:
            raise RuntimeError('fixture pin mismatch')
    names = ['help', 'version', 'usage', 'unavailable', 'denied', 'capacity']
    paths = [fixtures / (name + '.txt') for name in names]
    expected = 280 if frontend else sum(p.stat().st_size for p in paths) * 9 + 6 * 18 + 10
    suite_label = 'frontend' if frontend else 'delivery'
    mutation_label = 'three' if frontend else 'four'
    inputs = [HERE / n for n in ('local-output.c', 'local-output.h',
              'local-output-controls.c', 'check-local-output.py', 'process.py')]
    if frontend:
        inputs += [HERE / n for n in ('local-frontend.c', 'local-frontend.h',
                   'local-frontend-controls.c', 'runner-parse.c', 'runner-parse.h',
                   'runner-result.c', 'runner-result.h')]
    plan_name = 'runner-local-frontend' if frontend else 'runner-local-delivery'
    inputs += paths + [fixtures / 'manifest.json',
        ROOT / ('docs/evidence/' + plan_name + '-2026-09-06/change-review.md')]
    report = {'status': 'incomplete', 'scope': 'host callback delivery candidate; no native roles or runner integration',
              'compiler': compiler, 'compiler_pin_sha256': sha(pin),
              'python': sys.version, 'platform': platform.platform(),
              'suite': args.suite, 'expected_scenarios': expected, 'commands': [], 'cases': [],
              'sources': {str(p): sha(p) for p in inputs}}
    snapshot = work / 'sources'
    snapshot.mkdir()
    for p in inputs:
        (snapshot / p.name).write_bytes(p.read_bytes())
    env = clean_env(work)
    env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    def command(label, argv, expected_exit=0):
        result = run(argv, cwd=work, env=env, work=work, label=label, timeout=30)
        report['commands'].append({'label': label, 'process': result.record})
        save()
        if not result.record['complete'] or result.returncode != expected_exit:
            raise RuntimeError(label + ': unexpected execution; retained logs')
        return result

    save()
    try:
        cc = [compiler['path'], '--no-default-config']
        sdk = command('host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
        resource = Path(command('resource-dir', cc + ['-print-resource-dir']).stdout.decode().strip())
        runtime = resource / 'lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib'
        report['sanitizer_runtime'] = {'path': str(runtime), 'sha256': sha(runtime)}
        flags = ['-std=c17', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                 '-Wpedantic', '-Wconversion', '-Wsign-conversion', '-Wshadow',
                 '-Wstrict-prototypes', '-Wmissing-prototypes',
                 '-fno-omit-frame-pointer', '-fsanitize=undefined',
                 '-fno-sanitize-recover=all', '-isysroot', sdk, '-I', str(HERE)]
        original = (HERE / ('local-frontend.c' if frontend else 'local-output.c')).read_text()
        mutations = [
            ('replay-prefix', 'plan->text + state->delivered', 'plan->text', 'unwritten-suffix'),
            ('ignore-close', 'state->closes[0] == AL_CLOSED &&\n        state->closes[1] == AL_CLOSED',
             '1', 'outcome-precedence'),
            ('after-unknown', 'state->failure = AL_UNKNOWN;\n            return 1;',
             'state->failure = AL_UNKNOWN;\n            break;', 'no-after-unknown'),
            ('wrong-sink', 'unsigned sink = plan->kind <= AL_VERSION ? 0u : 1u;',
             'unsigned sink = plan->kind <= AL_VERSION ? 1u : 0u;', 'stream-separation'),
        ]
        if frontend:
            arrays = []
            for i, path in enumerate(paths):
                data = path.read_bytes()
                arrays.append('static const unsigned char text_' + str(i) + '[] = {' +
                              ','.join(str(value) for value in data) + '};')
            arrays.append('static const struct { const unsigned char *bytes; size_t size; } local_text[] = {')
            arrays += ['{text_' + str(i) + ',sizeof text_' + str(i) + '},' for i in range(6)]
            arrays.append('};')
            generated = work / 'local-text.h'
            generated.write_text('/* Generated from pinned proposal fixtures. */\n' + '\n'.join(arrays) + '\n')
            report['generated_text_sha256'] = sha(generated)
            mutations = [
                ('launch-help', 'kind = AL_HELP;',
                 '{ unsigned char r[32]; size_t n = 0; (void)ops->admit(context, &state->invocation, r, &n); kind = AL_HELP; }',
                 'admission-count'),
                ('collapse-denied', 'kind = AL_DENIED;', 'kind = AL_UNAVAILABLE;', 'delivery-status'),
                ('repair-padding', 'state->admission_action =\n            ar_admission(',
                 'reply[31] = 0; state->admission_action =\n            ar_admission(', 'unexpected-local-output'),
            ]
        variants = [('controls', original, None)]
        for name, anchor, replacement, oracle in mutations:
            if original.count(anchor) != 1:
                raise RuntimeError(name + ': mutation anchor changed')
            variants.append((name, original.replace(anchor, replacement), oracle))
        for name, source, oracle in variants:
            path = work / (name + '.c')
            path.write_text(source)
            binary = work / name
            extra = ['local-frontend-controls.c', 'local-output.c', 'runner-parse.c',
                     'runner-result.c'] if frontend else ['local-output-controls.c']
            command(name + '-compile', cc + flags + [str(path)] +
                    [str(HERE / n) for n in extra] + ['-o', str(binary)])
            command(name + '-libraries', ['/usr/bin/otool', '-L', str(binary)])
            result = command(name, [str(binary)] + [str(p) for p in paths], 90 if oracle else 0)
            ok = (result.stderr == ('ORACLE: ' + oracle + '\n').encode() and not result.stdout
                  if oracle else result.stdout == f'PASS: {expected} local {suite_label} scenarios\n'.encode()
                  and not result.stderr)
            report['cases'].append({'variant': name, 'pass': ok, 'oracle': oracle,
                                    'binary_sha256': sha(binary), 'source_sha256': sha(path)})
            save()
            if not ok:
                raise RuntimeError(name + ': oracle mismatch')
        for p, digest in report['sources'].items():
            if sha(Path(p)) != digest:
                raise RuntimeError('source changed: ' + p)
        if sha(runtime) != report['sanitizer_runtime']['sha256']:
            raise RuntimeError('runtime changed')
        report['status'] = 'pass'
    finally:
        save()
    print(f'[PASS] {expected} local {suite_label} scenarios and {mutation_label} semantic mutations')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print('[FAILED] ' + ascii(str(error))[1:-1], file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        print('[FAILED] Interrupted', file=sys.stderr)
        raise SystemExit(130)
