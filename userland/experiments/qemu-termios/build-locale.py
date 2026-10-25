#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build private candidate locale probe."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='locale-build-', dir=ROOT / 'build'))
    report = dict(status='incomplete', work=str(work), python=sys.version, commands=[])
    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    print(str(work), flush=True)
    try:
        receipt_path = ROOT / 'build/coreutils-musl-bdcrzzq6/evidence.json'
        receipt = json.loads(receipt_path.read_text())
        sdk = ROOT / 'build/musl-reference-q39nl2io'
        for rel, digest in receipt['sdk_inputs'].items():
            if sha(sdk / rel) != digest:
                raise RuntimeError('SDK drift')
        for tool in receipt['tools'].values():
            if sha(Path(tool['path'])) != tool['sha256']:
                raise RuntimeError('tool drift')
        original = Path(receipt['binaries']['stty']['path'])
        if sha(original) != receipt['binaries']['stty']['sha256']:
            raise RuntimeError('candidate drift')
        src = original.parent.parent
        helper = ROOT / 'experiments/command-runner/process.py'
        process = runpy.run_path(str(helper))
        env = process['clean_env'](work)
        stage = sdk / 'stage'
        lib = stage / 'usr/lib'
        objects = [src / 'src/stty.o', src / 'src/libver.a', src / 'lib/libcoreutils.a']
        paths = [Path(__file__), HERE / 'locale-probe.c', HERE / 'LOCALE-PLAN.md', receipt_path, helper] + objects
        report['sources'] = {str(p):sha(p) for p in paths}
        report['sdk_inputs'] = receipt['sdk_inputs']
        report['tools'] = receipt['tools']
        cc = [receipt['tools']['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
              '--sysroot=' + str(stage), '-nostdinc', '-isystem', str(stage / 'usr/include')]
        def run(label, argv):
            result = process['run'](argv, cwd=work, env=env, work=work, label=label, timeout=60)
            report['commands'].append(result.record)
            save()
            if not result.record['complete'] or result.returncode != 0:
                raise RuntimeError(label + ' failed')
            return result
        binary = work / 'locale-probe'
        run('probe-build', cc + ['--ld-path=' + receipt['tools']['lld']['path'],
            '-std=c17', '-O2', '-Wall', '-Wextra', '-Werror', '-nostdlib', '-static',
            str(lib / 'crt1.o'), str(lib / 'crti.o'), str(HERE / 'locale-probe.c'),
            '-Wl,-z,noexecstack', '-Wl,--no-undefined', str(lib / 'libc.a'),
            str(lib / 'crtn.o'), '-o', str(binary)])
        headers = run('probe-headers', [receipt['tools']['readelf']['path'], '-h', '-l', str(binary)])
        undefined = run('probe-undefined', [receipt['tools']['nm']['path'], '--extern-only', '--undefined-only', str(binary)])
        if undefined.stdout.strip() or b'INTERP' in headers.stdout:
            raise RuntimeError('unexpected dynamic/undefined closure')
        report['binaries'] = {'probe': dict(path=str(binary), sha256=sha(binary))}
        for p, digest in report['sources'].items():
            if sha(Path(p)) != digest:
                raise RuntimeError('source drift')
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        report['error'] = str(error)
    save()
    print(report['status'], flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
