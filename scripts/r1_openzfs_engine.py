#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build one R1 OpenZFS engine role from fresh source build outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
import types

from fs_home_launch import check_frames
from r1_openzfs_overlays import render

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'scripts'
FILESYSTEM = ROOT / 'userland/experiments/filesystem-service'
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_tools import run_tool

ZFS = 'zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1'
SDK_SHA = '2459a32ba53cfc1dd62160d4bb8ea8e1afbac3615f2784c7351ad04f91183719'
RUNTIME_SHA = '661a590b5779605008947559e76c9ff22229b62324aac9f4c937aca30e5fa440'
SUPPORT_SHA = '33213650e4491c2eb89187f97289d56225d3c3828b049886b1047e325395b098'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def build(args):
    work, support, sdk, runtime, lock = (getattr(args, name).resolve() for name in
                                         ('work', 'support', 'sdk', 'runtime', 'toolchain'))
    need(sha(sdk / 'lib/libc.a') == SDK_SHA, 'SDK libc differs')
    need(sha(runtime / 'libaether_runtime.a') == RUNTIME_SHA, 'source runtime differs')
    support_receipt = support / 'support.json'
    need(sha(support_receipt) == SUPPORT_SHA, 'source support receipt differs')
    support_pins = json.loads(support_receipt.read_text())
    for name, item in support_pins['objects'].items():
        need(sha(support / name) == item['sha256'], 'support object differs: ' + name)
    for name, expected in support_pins['config_sha256'].items():
        need(sha(support / 'include' / name) == expected, 'support header differs: ' + name)
    for name, expected in support_pins['sdk_link_inputs'].items():
        need(sha(sdk / 'lib' / name) == expected, 'SDK link input differs: ' + name)
    pins = json.loads(lock.read_text())
    tools = pins['tools']
    for name in ('clang', 'lld', 'rustc', 'clippy-driver', 'nm', 'readelf'):
        need(sha(Path(tools[name]['path'])) == tools[name]['sha256'], 'tool differs: ' + name)
    work.mkdir(mode=0o700)
    headers = work / 'runtime-headers'
    headers.mkdir()
    for relative in ('native-service-runtime/runtime.h', 'native-utc/utc.h'):
        source = ROOT / 'userland/experiments' / relative
        (headers / source.name).write_bytes(source.read_bytes())
    logs = work / 'logs'
    logs.mkdir()
    (work / 'tmp').mkdir()
    environment = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work / 'tmp')}
    started = time.monotonic()

    def run(label, argv):
        remaining = 300 - (time.monotonic() - started)
        need(remaining > 0, 'engine build deadline')
        return run_tool(argv, environment, logs / (label + '.log'),
                        timeout=min(120, remaining), cwd=work)

    resource = run('clang-resource', [tools['clang']['path'], '-print-resource-dir']).decode().strip()
    roots = dict(root=ROOT, work=work, support=support, zfs=support / ZFS, sdk=sdk,
                 runtime=runtime, clang_resource=Path(resource))

    def expand(argument):
        return re.sub(r'@([a-z_]+)', lambda match: str(roots[match[1]]), argument)

    generated = render(roots['zfs'], sdk, work)
    recipe = json.loads((HERE / 'r1-openzfs-compile.json').read_text())
    actions = recipe['actions']
    if args.role == 'note':
        for index, action in recipe['note_overrides'].items():
            actions[int(index)] = action
    missing = [expand(row[1]) for row in actions
               if isinstance(row[0], int) and not Path(expand(row[1])).is_file()]
    need(not missing, 'missing selected sources: ' + ', '.join(missing))

    helper = ROOT / 'userland/experiments/command-runner/process.py'
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
    frontend = runpy.run_path(str(FILESYSTEM / 'home_engine_build.py'))['build']
    frontend_record = {}
    frontend(work, proc, dict(tools), started + 300, frontend_record,
             terminfo_nine=args.role == 'seed', cold_note=args.role == 'note',
             source_toolchain=(lock, pins))

    normal = [f'-ffile-prefix-map={roots[key]}={value}' for key, value in
              (('work', '/build/aether/openzfs'), ('support', '/build/aether/support'),
               ('sdk', '/build/aether/sdk'), ('runtime', '/build/aether/runtime'),
               ('root', '/src/aether'))]
    for index, row in enumerate(actions):
        if isinstance(row[0], int):
            group, source, target = row
            destination = Path(expand(target))
            destination.parent.mkdir(parents=True, exist_ok=True)
            argv = [tools['clang']['path'], *normal, *map(expand, recipe['flags'][group]),
                    '-c', expand(source), '-o', str(destination)]
        else:
            name, flags = row
            tool = 'lld' if name == 'ld.lld' else name
            argv = [tools[tool]['path'], *map(expand, flags)]
            if tool == 'rustc':
                argv[1:1] = [f'--remap-path-prefix={work}=/build/aether/openzfs',
                             f'--remap-path-prefix={ROOT}=/src/aether']
        try:
            run(f'engine-{index:03d}', argv)
        except subprocess.SubprocessError as error:
            raise ValueError(f'engine action {index} failed. See {logs / f"engine-{index:03d}.log"}') from error
    frames = {path.name: path.read_text() for path in (work / 'launch').glob('*.su')}
    check_frames(frames)
    elf = work / 'filesystem.elf'
    need(0 < elf.stat().st_size <= 8 * 1024 * 1024, 'engine image exceeds role limit')
    result = dict(role=args.role, engine_sha256=sha(elf), bytes=elf.stat().st_size,
                  actions=len(actions), generated=generated,
                  frame_units=sorted(frames))
    (work / 'engine.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'generated'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=('seed', 'note'))
    for name in ('work', 'support', 'sdk', 'runtime', 'toolchain'):
        parser.add_argument('--' + name, type=Path, required=True)
    try:
        build(parser.parse_args())
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'OpenZFS source build failed: {error}\n')


if __name__ == '__main__':
    main()
