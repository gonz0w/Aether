#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host semantic controls and native link only for dash startup prerequisites."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import clean_env, run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='dash-startup-', dir=ROOT / 'build'))
    report = dict(status='incomplete', native_execution='NOT RUN', commands=[],
                  work=str(work), sources={})
    def save():
        (work / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    def command(label, argv, expected=0):
        result = run(argv, cwd=work, env=clean_env(work), work=work,
                     label=label, timeout=180)
        report['commands'].append(dict(expected=expected, **result.record))
        save()
        if not result.record['complete'] or result.returncode != expected:
            raise RuntimeError(label + ' failed')
    print(work, file=sys.stderr, flush=True)
    save()
    try:
        prior = ROOT / 'docs/evidence/dash-native-link-2026-09-07'
        for line in (prior / 'SHA256SUMS').read_text().splitlines():
            digest, name = line.split('  ', 1)
            if sha(prior / name) != digest:
                raise RuntimeError('prior evidence drift')
        receipt = json.loads((prior / 'results.json').read_text())
        snapshot = ROOT / 'build/toybox-close-consumer-q91nkwbt'
        if sha(snapshot / 'intake.json') != receipt['intake_sha256']:
            raise RuntimeError('intake drift')
        for name, digest in json.loads((snapshot / 'intake.json').read_text())['pins'].items():
            if sha(snapshot / name) != digest:
                raise RuntimeError('snapshot drift')
        base = snapshot / 'producer/docs/evidence/toybox-native-link-2026-09-07'
        sdk = base / 'inputs/sdk-stage'
        for name, digest in receipt['sdk_inputs'].items():
            if sha(sdk / name) != digest:
                raise RuntimeError('SDK drift')
        for tool in receipt['tools'].values():
            if sha(Path(tool['path'])) != tool['sha256']:
                raise RuntimeError('tool drift')
        source = ROOT / 'experiments/dash-native'
        for name in ('startup.c', 'startup-test.c', 'check-startup.py', 'PLAN.md'):
            report['sources'][name] = sha(source / name)
            (work / name).write_bytes((source / name).read_bytes())
        report['prior_receipt_sha256'] = sha(prior / 'results.json')
        clang = receipt['tools']['clang']['path']
        common = ['-std=c17', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror']
        command('format', [str(Path(clang).with_name('clang-format')), '--dry-run',
                '--Werror', '--style=file:' + str(ROOT / 'docs/quality/clang-format.yaml'),
                str(work / 'startup.c'), str(work / 'startup-test.c')])
        host_sdk = Path('/Applications/Xcode-beta.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk').resolve(strict=True)
        report['host_sdk'] = dict(path=str(host_sdk),
                settings_sha256=sha(host_sdk / 'SDKSettings.json'))
        command('host-build', [clang, '--no-default-config', '-isysroot', str(host_sdk)] + common +
                [str(work / 'startup-test.c'), '-o', str(work / 'host-test')])
        for case, expected in enumerate((0, 10, 20, 20, 21, 30)):
            command('host-' + str(case), [str(work / 'host-test'), str(case)], expected)
        (work / 'empty-root').mkdir()
        target = [clang, '--no-default-config', '--target=x86_64-linux-musl',
                  '--sysroot=' + str(work / 'empty-root')]
        compile_flags = common + ['-ffreestanding', '-fno-builtin',
                '-fstack-protector-strong', '-nostdinc', '-isystem', str(sdk / 'usr/include')]
        for label, src in [('probe', work / 'startup.c'), ('adapter', base / 'inputs/adapter.c')]:
            command(label, target + compile_flags + ['-c', str(src), '-o', str(work / (label + '.o'))])
        lib = sdk / 'usr/lib'
        elf = work / 'dash-startup.elf'
        command('link', target + ['--ld-path=' + receipt['tools']['lld']['path'],
                '-nostdlib', '-static', '-Wl,-z,noexecstack', '-Wl,--no-undefined',
                str(lib / 'crt1.o'), str(lib / 'crti.o'), str(work / 'probe.o'),
                str(work / 'adapter.o'), str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(elf)])
        report.update(status='pass', elf_sha256=sha(elf), elf_bytes=elf.stat().st_size,
                      host_cases=6)
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        report['error'] = str(error)
    save()
    print(report['status'], flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
