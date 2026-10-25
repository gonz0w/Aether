#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host bytecount tests and native object preparation; no Aether command execution."""
import argparse
import hashlib
import json
import platform
import tempfile
from pathlib import Path

from process import clean_env, run as owned_run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', type=Path, required=True)
    a = p.parse_args()
    sdk = a.sdk.resolve()
    pin = (
        ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
    )
    reference = json.loads(pin.read_text())
    tools = reference['tools']
    for name, t in tools.items():
        need(sha(Path(t['path'])) == t['sha256'], 'tool changed: ' + name)

    def inventory():
        return {
            str(p.relative_to(sdk)): sha(p)
            for p in (sdk / 'stage').rglob('*')
            if p.is_file()
        }

    need(
        not any((p.is_symlink() for p in (sdk / 'stage').rglob('*'))),
        'SDK symlink'
    )
    need(inventory() == reference['sdk_inputs'], 'SDK mismatch')
    need(
        sha(sdk / 'evidence.json') == reference['libc_receipt_sha256'],
        'SDK receipt mismatch'
    )
    inputs = {str(p): sha(p) for p in HERE.iterdir() if p.is_file()}
    work = Path(tempfile.mkdtemp(
        prefix='bytecount-prepare-',
        dir=ROOT / 'build'
    ))
    print(work, flush=True)
    r = {
        'schema': 'aether-userland.bytecount-prepare.v1',
        'status': 'incomplete',
        'scope': (
            'host command algorithm/control execution and native C '
            'object only; no native executable or command-runner '
            'acceptance'
        ),
        'host': platform.platform(),
        'sources': inputs,
        'tools': tools,
        'sdk_pin': str(pin),
        'sdk_pin_sha256': sha(pin),
        'commands': [],
        'cases': []
    }

    def save():
        (work / 'summary.json').write_text(json.dumps(r, indent=2) + '\n')

    def command(label, args, expected=0, **kwargs):
        result = owned_run(
            args,
            cwd=work,
            env=kwargs.pop('env', clean_env(work)),
            work=work,
            label=label,
            timeout=30,
            **kwargs
        )
        (work / (label + '.stdout')).write_bytes(result.stdout)
        (work / (label + '.stderr')).write_bytes(result.stderr)
        r['commands'].append({
            'label': label,
            'argv': args,
            'exit': result.returncode,
            'process': result.record
        })
        save()
        need(
            result.record['complete'] and result.returncode == expected,
            label + ' unexpected exit'
        )
        return result.stdout
    save()
    try:
        cc = [tools['clang']['path'], '--no-default-config']
        flags = ['-std=c17', '-O2', '-Wall', '-Wextra', '-Werror']
        host_sdk = command(
            'host-sdk',
            ['/usr/bin/xcrun', '--show-sdk-path']
        ).decode().strip()
        r['host_sdk'] = host_sdk
        host = cc + flags + ['-isysroot', host_sdk]
        source = str(HERE / 'bytecount.c')
        binary = str(work / 'bytecount')
        command('host-build', host + [source, '-o', binary])
        environment = {'LC_ALL': 'C'}
        for label, data, args, env, expected, output in [
            ('six', b'abcdef', ['--decimal'], environment, 0, b'6\n'),
            ('empty', b'', ['--decimal'], environment, 0, b'0\n'),
            (
                'binary',
                bytes(range(256)) * 17,
                ['--decimal'],
                environment,
                0,
                b'4352\n'
            ),
            ('wrong-option', b'abc', ['--hex'], environment, 64, b''),
            ('no-option', b'abc', [], environment, 64, b''),
            (
                'extra-option',
                b'abc',
                ['--decimal', 'extra'],
                environment,
                64,
                b''
            ),
            ('missing-locale', b'abc', ['--decimal'], {}, 64, b''),
            (
                'wrong-locale',
                b'abc',
                ['--decimal'],
                {'LC_ALL': 'wrong'},
                64,
                b''
            )
        ]:
            actual = command(
                label,
                [binary] + args,
                expected,
                input=data,
                env=env
            )
            need(actual == output, label + ' output')
            r['cases'].append({
                'case': label,
                'layer': 'host-libc',
                'result': 'pass',
                'input_sha256': hashlib.sha256(data).hexdigest(),
                'expected_exit': expected,
                'output': output.decode()
            })
            save()
        for label, args, expected in [
            ('help', ['--help'], b'Count bytes from standard input.'),
            ('version', ['--version'], b'bytecount 0.1\n')
        ]:
            actual = command(label, [binary] + args, input=b'', env={})
            need(
                actual.startswith(expected) if label == 'help' else actual == expected,
                label + ' output'
            )
            r['cases'].append({
                'case': label,
                'layer': 'host-libc',
                'result': 'pass',
                'expected_exit': 0
            })
            save()
        command(
            'controlled-object',
            host + [
                '-Dmain=bytecount_main',
                '-Dread=controlled_read',
                '-Dwrite=controlled_write',
                '-Dclose=controlled_close',
                '-c',
                source,
                '-o',
                str(work / 'controlled.o')
            ]
        )
        control = str(work / 'controls')
        command(
            'control-link',
            host + [
                str(HERE / 'bytecount-controls.c'),
                str(work / 'controlled.o'),
                '-o',
                control
            ]
        )
        for mode in [
            'short-io',
            'read-eintr',
            'write-eintr',
            'read-error',
            'read-eagain',
            'read-overlong',
            'write-error',
            'write-zero',
            'write-overlong',
            'close-error',
            'close-eintr'
        ]:
            command(mode, [control, mode], env=environment)
            r['cases'].append({
                'case': mode,
                'layer': 'host injected libc-call boundary',
                'result': 'pass'
            })
            save()
        obj = work / 'bytecount-native.o'
        command(
            'native-compile',
            cc + flags + [
                '--target=x86_64-linux-musl',
                '--sysroot=' + str(sdk / 'empty-root'),
                '-nostdinc',
                '-isystem',
                str(sdk / 'stage/usr/include'),
                '-ffreestanding',
                '-fno-builtin',
                '-fstack-protector-strong',
                '-c',
                source,
                '-o',
                str(obj)
            ]
        )
        command('native-headers', [tools['readelf']['path'], '-h', str(obj)])
        symbols = command(
            'native-imports',
            [tools['nm']['path'], '--undefined-only', str(obj)]
        ).decode()
        for symbol in ('read', 'write', 'close'):
            need(
                any((line.split()[-1] == symbol for line in symbols.splitlines())),
                'missing public libc call: ' + symbol
            )
        r['native_object_sha256'] = sha(obj)
        r['native_object_bytes'] = obj.stat().st_size
        for n, h in inputs.items():
            need(sha(Path(n)) == h, 'source changed')
        need(inventory() == reference['sdk_inputs'], 'SDK changed')
        r['status'] = 'pass'
        print('PASS: 10 host cases, 11 injected controls; native object only')
    finally:
        save()

if __name__ == '__main__':
    main()
