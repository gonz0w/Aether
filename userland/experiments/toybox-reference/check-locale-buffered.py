#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Bounded cat locale and buffered-output checks; Python 3.12+."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

from build import Parser, require, sha
from test import IMAGE, PODMAN

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import clean_env, run


def accepts(result, status, output, trace, diagnostic):
    if diagnostic is None:
        stderr_ok = result.stderr == trace
    else:
        stderr_ok = result.stderr.startswith(trace) and diagnostic in result.stderr
    return (result.returncode == status and result.stdout == output and stderr_ok)


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='toybox-locale-buffered 0.1.0')
    parser.parse_args()
    prior = ROOT / 'docs/evidence/toybox-standalone-2026-09-06'
    for line in (prior / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(sha(prior / name) == digest, 'prior evidence drift')
    source = ROOT / 'build/toybox-reference-1nutoq_n'
    receipt = json.loads((source / 'evidence.json').read_text())
    require(sha(source / 'evidence.json') ==
            sha(prior / 'builds/cat/evidence.json'), 'receipt drift')
    for name, digest in receipt['files'].items():
        require(sha(Path(name)) == digest, 'input drift: ' + name)
    for tool in receipt['tools'].values():
        require(sha(Path(tool['path'])) == tool['sha256'], 'tool drift')
    sdk = Path(json.loads((ROOT / 'experiments/musl-reference/evidence.json').read_text())['output'])
    for name, digest in receipt['sdk_inputs'].items():
        require(sha(sdk / name) == digest, 'SDK drift')
    out = Path(tempfile.mkdtemp(prefix='toybox-locale-buffered-', dir=ROOT / 'build'))
    print(out, flush=True)
    inputs = [Path(__file__), Path(__file__).with_name('locale-faults.c'),
              ROOT / 'experiments/command-runner/process.py',
              ROOT / 'docs/evidence/toybox-locale-buffered-2026-09-06/change-review.md']
    objects = sorted((source / 'toybox-0.8.14/generated/unstripped/obj').glob('*.o'))
    require(bool(objects), 'no objects')
    # The earlier import receipt binds the object inventory paths, not their bytes.
    # Pin the actual local objects before consuming them in this new experiment.
    hashes = {str(p): sha(p) for p in inputs + objects}
    (out / 'inputs.json').write_text(json.dumps(hashes, indent=2) + '\n')
    for p in inputs:
        shutil.copy2(p, out / p.name)
    shutil.copytree(source / 'toybox-0.8.14/generated/unstripped/obj', out / 'objects')
    shutil.copy2(source / 'cc.py', out / 'cc.py')
    env = clean_env(out)

    def checked(label, argv):
        result = run(argv, cwd=ROOT, env=env, work=out, label=label, timeout=60)
        require(result.record['complete'] and result.returncode == 0, label)
        return result

    checked('format', ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang-format',
                       '--dry-run', '--Werror', '--style=file:docs/quality/clang-format.yaml',
                       str(out / 'locale-faults.c')])
    checked('compile', [str(out / 'cc.py'), '-std=c17', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fstack-protector-strong', '-c', str(out / 'locale-faults.c'),
                        '-o', str(out / 'faults.o')])
    link = [str(out / 'cc.py'), '-Wl,--gc-sections', '-Wl,-z,noexecstack',
            '-Wl,--no-undefined']
    ordered = [p for p in objects if p.name.startswith('lib_')]
    ordered += [next(p for p in objects if p.name == n)
                for n in ('main.o', 'cat.o')]
    require(len(ordered) == len(objects), 'unexpected object inventory')
    copied_objects = [str(out / 'objects' / p.name) for p in ordered]
    checked('control-link', link + copied_objects + ['-o', str(out / 'control')])
    require(sha(out / 'control') == receipt['elf_sha256'],
            'object relink did not reproduce baseline')
    checked('fault-link', link + copied_objects + [str(out / 'faults.o'),
            '-Wl,--wrap=setlocale', '-Wl,--wrap=newlocale',
            '-Wl,--wrap=uselocale', '-Wl,--wrap=read',
            '-o', str(out / 'candidate')])
    checked('headers', [receipt['tools']['readelf']['path'], '-h', '-l',
                        str(out / 'candidate')])
    undefined = checked('undefined', [receipt['tools']['nm']['path'],
                                     '--undefined-only', '--extern-only', str(out / 'candidate')])
    require(not undefined.stdout.strip(), 'undefined symbols')
    payload = b'alpha\x00beta\n'
    startup = b'SET_OK\nPRIMARY_OK\nUSE_SET\nREAD_UTF8\n'
    cases = [
        ('baseline', 0, payload, startup, None, [], payload, False),
        ('set-denied', 0, payload,
         b'SET_DENIED\nPRIMARY_OK\nUSE_SET\nREAD_UTF8\n',
         None, [], payload, False),
        ('primary-denied', 0, payload,
         b'SET_OK\nPRIMARY_DENIED\nFALLBACK_OK\nUSE_SET\nREAD_UTF8\n',
         None, [], payload, False),
        ('all-denied', 0, payload,
         b'SET_OK\nPRIMARY_DENIED\nFALLBACK_DENIED\nUSE_QUERY\nREAD_OTHER\n',
         None, [], payload, False),
    ]
    for size, data in [('small', b'a\nb\n'), ('large', b'a\nb\n' * 3000)]:
        cases.append(('buffered-' + size, 0, data.replace(b'\n', b'$\n'),
                      b'', None, ['-e'], data, False))
        cases.append(('full-' + size, 1, b'', b'', b'No space left',
                      ['-e'], data, True))
    report = {'status': 'incomplete', 'scope': 'Link-time injected Linux reference',
              'inputs': hashes, 'image': IMAGE, 'python': sys.version,
              'candidate_sha256': sha(out / 'candidate'),
              'control_matches_original': True, 'cases': []}
    host_env = dict(env, HOME=os.environ['HOME'])

    def save():
        (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for name, status, output, trace, diagnostic, args, data, full in cases:
        container = 'userland-toybox-locale-' + uuid.uuid4().hex
        argv = [PODMAN, 'run', '--name', container, '--rm', '-i', '--pull=never',
                '--network=none', '--read-only', '--cap-drop=all',
                '--security-opt=no-new-privileges', '--user=65534:65534',
                '--memory=512m', '--pids-limit=32',
                '--mount', 'type=bind,src=' + str(out) + ',dst=/inputs,ro=true',
                '--env', 'LC_ALL=C', '--env', 'TOYBOX_LOCALE_FAULT=' + name,
                '--entrypoint=' + ('/bin/sh' if full else '/usr/bin/qemu-x86_64'), IMAGE]
        program = '/inputs/control' if args else '/inputs/candidate'
        if full:
            argv += ['-c', 'exec /usr/bin/qemu-x86_64 /inputs/control -e > /dev/full']
        else:
            argv += [program] + args
        try:
            result = run(argv, cwd=ROOT, env=host_env, work=out, label=name,
                         timeout=45, input=data)
        finally:
            cleanup = run([PODMAN, 'rm', '--force', '--ignore', container],
                          cwd=ROOT, env=host_env, work=out,
                          label=name + '-cleanup', timeout=15)
        ok = (result.record['complete'] and cleanup.record['complete']
              and cleanup.returncode == 0
              and accepts(result, status, output, trace, diagnostic))
        report['cases'].append({'name': name, 'pass': ok,
                                'expected_status': status,
                                'expected_output_hex': output.hex(),
                                'expected_trace': trace.decode(),
                                'diagnostic': diagnostic.decode() if diagnostic else None})
        save()
        require(ok, name + ' failed; see ' + str(out))
    require(not accepts(result, 0, b'', b'', diagnostic), 'wrong status accepted')
    require(not accepts(result, 1, b'', b'IMPOSSIBLE_TRACE', diagnostic),
            'wrong trace accepted')
    for name, digest in hashes.items():
        require(sha(Path(name)) == digest, 'input changed during run')
    ast.parse(Path(__file__).read_text(), feature_version=(3, 12))
    report.update(status='pass', rejected_oracle_controls=2)
    save()
    print('[PASS] eight locale/buffered cases and two oracle controls')


if __name__ == '__main__':
    main()
