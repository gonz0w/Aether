#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build a private opt-in UTC variant from the sealed elapsed runtime; Python3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SEAL = '5adc4f6e9c255df3ead08404fca177d22db00a089429f1c0666fd90dd1812c6d'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024**2), b''):
            h.update(chunk)
    return h.hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def display(value):
    return ''.join('\\x%02x' % ord(c) if ord(c) < 32 or ord(c) == 127 else c
                   for c in str(value))


class Parser(argparse.ArgumentParser):
    def error(self, message):
        super().error(display(message))


def build(delivery, output):
    delivery, output = delivery.resolve(), output.resolve()
    need(output.is_relative_to(ROOT / 'build') and not output.exists(),
         'output must be fresh under build')
    need(sha(delivery / 'SHA256SUMS') == SEAL, 'elapsed runtime delivery seal')
    members = {}
    for line in (delivery / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        relative = Path(name)
        need(not relative.is_absolute() and '..' not in relative.parts and
             name not in members, 'sealed path')
        path = delivery / name
        need(path.is_file() and not path.is_symlink() and sha(path) == digest,
             'sealed member ' + name)
        members[name] = digest
    need(len(members) == 294, 'elapsed delivery member count')
    helper = ROOT / 'experiments/command-runner/process.py'
    need(sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e',
         'owned process helper')
    tools = json.loads((delivery / 'sdk/tools.lock.json').read_text())['tools']
    for name in ('clang', 'ar', 'nm'):
        need(sha(Path(tools[name]['path'])) == tools[name]['sha256'], name)
    output.mkdir()
    source = output / 'source'
    source.mkdir()
    for name in ('calendar.c', 'utc.c', 'utc.h', 'wrappers.c'):
        shutil.copyfile(HERE / name, source / name)
    base = delivery / 'runtime'
    for name in ('adapter.h', 'runtime.h', 'real_time.h'):
        shutil.copyfile(delivery / 'source/experiments/native-service-runtime' / name, source / name)
    original = (delivery / 'source/experiments/native-service-runtime/real_time.c').read_text()
    old = '    if (id != CLOCK_MONOTONIC) {\n'
    new = ('    if (id == CLOCK_REALTIME) {\n'
           '        int error = aether_utc_read(out);\n'
           '        if (error) { errno = error; return -1; }\n'
           '        return 0;\n'
           '    }\n' + old)
    need(original.count(old) == 1, 'elapsed clock anchor')
    patched = '#include "utc.h"\n' + original.replace(old, new)
    (source / 'real_time.c').write_text(patched)
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
    env = proc.clean_env(output)
    commands = []

    def run(label, argv):
        argv = [str(x) for x in argv]
        result = proc.run(argv, cwd=output, env=env, work=output,
                          label=label, timeout=120)
        commands.append({'label': label, 'argv': argv, 'record': result.record})
        (output / 'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        need(result.returncode == 0 and result.record['complete'] and
             result.record['cleanup'] == 'complete', label)
        return result

    cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
          '--sysroot=' + str(output / 'empty-root'), '-std=c17', '-D_GNU_SOURCE',
          '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin',
          '-fstack-protector-strong', '-nostdinc', '-DAETHER_LONG_WAITS',
          '-isystem', delivery / 'sdk/stage/usr/include', '-I', source]
    objects = []
    for name in ('real_time', 'calendar', 'utc', 'wrappers'):
        obj = output / (name + '.o')
        run(name, cc + ['-c', source / (name + '.c'), '-o', obj])
        objects.append(obj)
    archive = output / 'libaether_runtime.a'
    shutil.copyfile(base / 'libaether_runtime.a', archive)
    run('archive', [tools['ar']['path'], 'rcs', archive, *objects])
    run('symbols', [tools['nm']['path'], '--defined-only', archive])
    shutil.copyfile(HERE / 'utc.h', output / 'utc.h')
    shutil.copyfile(base / 'runtime.h', output / 'runtime.h')
    receipt = {'status': 'built, native execution required', 'profile': 'native-utc-v0',
               'base_seal': SEAL, 'base_members': members, 'tools': tools,
               'helper_sha256': sha(helper), 'recipe_sha256': sha(Path(__file__)),
               'sources': {x.name: sha(x) for x in source.iterdir()},
               'patch': {'old': old, 'new': new,
                         'before': sha(delivery / 'source/experiments/native-service-runtime/real_time.c'),
                         'after': sha(source / 'real_time.c')},
               'archive_sha256': sha(archive),
               'required_link': ['--whole-archive', 'libaether_runtime.a',
                                 '--no-whole-archive', 'libc.a'],
               'utc_policy': 'explicit unauthenticated q35 RTC-as-UTC',
               'quantization_ns': 1000000000, 'maximum_read_bracket_ns': 2000000}
    (output / 'build.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return output


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--delivery', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--version', action='version', version='aether-native-utc 0')
    args = parser.parse_args()
    try:
        print(display(build(args.delivery, args.output)))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, display(error) + '\n')
