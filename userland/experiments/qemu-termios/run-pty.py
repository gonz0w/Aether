#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run CMSPAR Linux PTY checks against a completed private QEMU build."""
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import tarfile

ROOT = Path.cwd()
HERE = ROOT / 'experiments/qemu-termios'
CONTAINER = runpy.run_path(str(ROOT / 'experiments/dash-reference/container-process.py'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    build = Path(sys.argv[1]).resolve()
    work = Path(tempfile.mkdtemp(prefix='qemu-pty-', dir=ROOT / 'build')).resolve()
    work.chmod(0o755)
    inputs = work / 'inputs'
    inputs.mkdir()
    report = {'status': 'incomplete', 'work': str(work), 'scope': 'Linux PTY CMSPAR/recovery only'}

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    print('PTY evidence: ' + str(work), flush=True)
    try:
        receipt = json.loads((build / 'summary.json').read_text())
        if receipt['status'] != 'pass' or receipt['container']['cleanup'] != 'absent':
            raise RuntimeError('full build or cleanup not accepted')
        binaries = {}
        for name in ('baseline', 'patched'):
            rel = 'output/' + name + '/qemu-x86_64'
            path = build / rel
            if sha(path) != receipt['artifacts'][rel]:
                raise RuntimeError('emulator drift')
            binaries[name] = path
        candidate = ROOT / 'docs/evidence/gnu-stty-extended-2026-09-06/candidate-receipt.json'
        stty = json.loads(candidate.read_text())['binaries']['stty']
        if sha(Path(stty['path'])) != stty['sha256']:
            raise RuntimeError('GNU stty drift')
        binaries['stty'] = Path(stty['path'])
        selected = dict(binaries, **{'check-pty.py': HERE / 'check-pty.py',
                                    'process.py': ROOT / 'experiments/command-runner/process.py'})
        report['inputs'] = {}
        for name, path in selected.items():
            digest = sha(path)
            shutil.copyfile(path, inputs / name)
            (inputs / name).chmod(0o755 if name in binaries else 0o644)
            if sha(inputs / name) != digest:
                raise RuntimeError('PTY stage drift')
            report['inputs'][name] = digest
        report['sources'] = {str(p): sha(p) for p in [Path(__file__), HERE / 'check-pty.py',
                             HERE / 'PTY-PLAN.md', candidate, build / 'summary.json',
                             HERE / 'build-inputs.lock.json',
                             ROOT / 'experiments/dash-reference/container-process.py',
                             ROOT / 'experiments/command-runner/process.py']}
        packages = json.loads((HERE / 'build-inputs.lock.json').read_text())
        runtime = {
            'debs/libglib2.0-0t64_2.84.4-3~deb13u3_arm64.deb': {
                './usr/lib/aarch64-linux-gnu/libglib-2.0.so.0.8400.4': 'lib/libglib-2.0.so.0',
                './usr/share/doc/libglib2.0-0t64/copyright': 'notices/GLib-copyright.txt'},
            'debs/libatomic1_14.2.0-19_arm64.deb': {
                './usr/lib/aarch64-linux-gnu/libatomic.so.1.2.0': 'lib/libatomic.so.1'},
        }
        report['runtime_packages'] = {}
        for number, (name, members) in enumerate(runtime.items()):
            package = Path(packages['root']) / name
            if sha(package) != packages['files'][name]:
                raise RuntimeError('runtime package drift')
            extracted = CONTAINER['PROCESS']['run'](
                ['/usr/bin/ar', 'p', str(package), 'data.tar.xz'], cwd=work,
                env=CONTAINER['PROCESS']['clean_env'](work), work=work,
                label='runtime-extract-' + str(number), timeout=20)
            report['runtime_packages'][name] = {
                'path': str(package), 'sha256': packages['files'][name],
                'members': members, 'process': extracted.record}
            save()
            CONTAINER['checked'](extracted)
            with tarfile.open(fileobj=io.BytesIO(extracted.stdout), mode='r:xz') as archive:
                for member, target in members.items():
                    entry = archive.getmember(member)
                    if not entry.isfile():
                        raise RuntimeError('unexpected runtime member type')
                    dest = inputs / target
                    dest.parent.mkdir(exist_ok=True)
                    dest.write_bytes(archive.extractfile(entry).read())
                    report['inputs'][target] = sha(dest)
        descriptor = CONTAINER['selected_descriptor'](work)
        client = CONTAINER['Client'](descriptor, work)
        save()
        state = CONTAINER['run_container'](client, receipt['image'],
                  ['/usr/local/bin/python3', '/inputs/check-pty.py'], work,
                  timeout=120, inputs=inputs)
        report['container'] = state
        save()
        if not state['complete'] or state.get('guest_exit') != 0:
            raise RuntimeError('PTY guest incomplete')
        result = json.loads((work / 'guest.stdout').read_text())
        report['results'] = result
        if (result['status'] != 'pass' or len(result['results']) != 12 or
                not all(row['status'] == 'pass' and row['restored'] and
                        row['process']['complete'] for row in result['results'])):
            raise RuntimeError('PTY oracle or restoration failed')
        for path, digest in report['sources'].items():
            if sha(Path(path)) != digest:
                raise RuntimeError('PTY source drift')
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
        save()
        print('PTY incomplete: ' + str(error), flush=True)
        return 1
    save()
    print('Twelve Linux PTY cases and restoration pass; full consumer suites pending.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
