#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline private QEMU baseline/candidate build using an owned container."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import tempfile

ROOT = Path.cwd()
HERE = ROOT / 'experiments/qemu-termios'
CONTAINER = runpy.run_path(str(ROOT / 'experiments/dash-reference/container-process.py'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_create_args(args):
    args = list(args)
    if not args or args[0] != 'create':
        raise ValueError('create profile required')
    replacements = {'--read-only': None, '--user=65534:65534': '--user=0:0',
                    '--memory=512m': '--memory=1536m', '--pids-limit=32': '--pids-limit=128'}
    for old in replacements:
        if args.count(old) != 1:
            raise ValueError('unexpected lifecycle create profile: ' + old)
    for required in ('--network=none', '--pull=never', '--cap-drop=all',
                     '--security-opt=no-new-privileges'):
        if args.count(required) != 1:
            raise ValueError('missing build restriction: ' + required)
    result = []
    for item in args:
        value = replacements.get(item, item)
        if value is not None:
            result.append(value)
    index = result.index('--entrypoint')
    result[index:index] = ['--cpus=2', '--cap-add=CHOWN,DAC_OVERRIDE,FOWNER,SETUID,SETGID',
                           '--env=LC_ALL=C', '--env=PATH=/usr/sbin:/usr/bin:/sbin:/bin']
    return result


class BuildClient(CONTAINER['Client']):
    def call(self, args, timeout=20):
        if args and args[0] == 'create':
            args = build_create_args(args)
        return super().call(args, timeout)


def main():
    work = Path(tempfile.mkdtemp(prefix='qemu-build-', dir=ROOT / 'build')).resolve()
    work.chmod(0o755)
    inputs, output = work / 'inputs', work / 'output'
    inputs.mkdir()
    output.mkdir(mode=0o777)
    output.chmod(0o777)
    report = {'status': 'incomplete', 'work': str(work), 'scope': 'offline emulator build only',
              'sources': {str(p): sha(p) for p in [Path(__file__), HERE / 'build-guest.sh', HERE / 'extract-source.py', HERE / 'apply-cmspar.py',
                          HERE / 'BUILD-PLAN.md', HERE / 'cmspar.patch',
                          HERE / 'build-inputs.lock.json', HERE / 'source.lock.json',
                          ROOT / 'experiments/dash-reference/container-process.py',
                          ROOT / 'experiments/command-runner/process.py']}}

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    print('Build evidence: ' + str(work), flush=True)
    try:
        source = json.loads((HERE / 'source.lock.json').read_text())
        build = json.loads((HERE / 'build-inputs.lock.json').read_text())
        original = Path(build['root'])
        if sha(original / 'receipt.json') != build['receipt_sha256']:
            raise RuntimeError('build acquisition receipt drift')
        for name, digest in build['files'].items():
            if sha(original / name) != digest:
                raise RuntimeError('build input drift: ' + name)
        if sha(ROOT / source['archive']) != source['sha256']:
            raise RuntimeError('source archive drift')
        approved = json.loads((ROOT / 'docs/evidence/qemu-cmspar-translation-2026-09-07/maintainer-review.json').read_text())
        if sha(HERE / 'cmspar.patch') != approved['patch_sha256']:
            raise RuntimeError('approved patch drift')
        inputs.joinpath('debs').mkdir()
        stage = {inputs / 'qemu.tar.xz': ROOT / source['archive'],
                 inputs / 'cmspar.patch': HERE / 'cmspar.patch',
                 inputs / 'build.sh': HERE / 'build-guest.sh',
                 inputs / 'extract-source.py': HERE / 'extract-source.py',
                 inputs / 'apply-cmspar.py': HERE / 'apply-cmspar.py'}
        stage.update({inputs / name: original / name for name in build['files']
                      if name.startswith('debs/') and name.endswith('.deb')})
        report['staged'] = {}
        for dest, src in stage.items():
            digest = sha(src)
            shutil.copyfile(src, dest)
            dest.chmod(0o644)
            if sha(dest) != digest:
                raise RuntimeError('staged input drift')
            report['staged'][str(dest.relative_to(work))] = digest
        descriptor = CONTAINER['selected_descriptor'](work)
        client = BuildClient(descriptor, work)
        image = build['base_image']
        inspected = CONTAINER['checked'](client.call(['image', 'inspect', image]))
        if json.loads(inspected.stdout)[0]['Id'].removeprefix('sha256:') != image:
            raise RuntimeError('base image identity mismatch')
        report['image'] = image
        report['container_client'] = descriptor
        save()
        state = CONTAINER['run_container'](client, image,
                    ['/bin/sh', str(inputs / 'build.sh'), str(inputs), str(output)],
                    work, timeout=1200, generator_root=work, generator_cwd=output)
        report['container'] = state
        save()
        if not state['complete'] or state.get('guest_exit') != 0:
            raise RuntimeError('build incomplete or guest failure')
        artifacts = [output / kind / 'qemu-x86_64' for kind in ('baseline', 'patched')]
        report['artifacts'] = {str(p.relative_to(work)): sha(p) for p in artifacts}
        for path, digest in report['sources'].items():
            if sha(Path(path)) != digest:
                raise RuntimeError('build driver input drift')
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
        save()
        print('Build incomplete: ' + str(error), flush=True)
        return 1
    save()
    print('Offline baseline/candidate build complete; PTY tests pending.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
