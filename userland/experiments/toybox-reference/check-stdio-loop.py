#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Actual musl stdio loop reference checks; Python 3.12+."""
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import uuid
from build import Parser, require, sha
from test import IMAGE, PODMAN
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import run, clean_env


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='toybox-stdio-loop 0.1.0')
    parser.parse_args()
    old = ROOT / 'build/toybox-reference-1nutoq_n'
    receipt = json.loads((old / 'evidence.json').read_text())
    prior = ROOT / 'docs/evidence/toybox-standalone-2026-09-06'
    require(sha(old / 'evidence.json') == sha(prior / 'builds/cat/evidence.json'), 'receipt drift')
    for name, digest in receipt['files'].items():
        require(sha(Path(name)) == digest, 'input drift')
    sdk = Path(json.loads((ROOT / 'experiments/musl-reference/evidence.json').read_text())['output'])
    for name, digest in receipt['sdk_inputs'].items():
        require(sha(sdk / name) == digest, 'SDK drift')
    for tool in receipt['tools'].values():
        require(sha(Path(tool['path'])) == tool['sha256'], 'tool drift')
    src = sdk / 'musl-1.2.6'
    original = src / 'src/stdio/__stdio_write.c'
    audit = json.loads((ROOT / 'docs/evidence/toybox-native-sdk-2026-09-06/summary.json').read_text())
    archive = ROOT / 'build/musl-audit/musl-1.2.6.tar.gz'
    require(sha(archive) == audit['archive_sha256'], 'archive drift')
    with tarfile.open(archive) as tar:
        require(tar.extractfile('musl-1.2.6/src/stdio/__stdio_write.c').read() == original.read_bytes(), 'source drift')
    out = Path(tempfile.mkdtemp(prefix='toybox-stdio-loop-', dir=ROOT / 'build'))
    print(out, flush=True)
    inputs = [Path(__file__), original, ROOT / 'experiments/command-runner/process.py',
              ROOT / 'docs/evidence/toybox-stdio-loop-2026-09-06/change-review.md']
    for n in ('stdio-loop-controls.c', 'stdio-loop.h', 'vector.c', 'vector.h'):
        inputs.append(Path(__file__).with_name(n))
    for directory in ('src/include', 'src/internal', 'arch/x86_64', 'arch/generic', 'include'):
        inputs += [p for p in (src / directory).rglob('*') if p.is_file()]
        shutil.copytree(src / directory, out / 'musl' / directory)
    hashes = {str(p): sha(p) for p in inputs}
    for p in inputs[:8]:
        shutil.copy2(p, out / p.name)
    shutil.copy2(old / 'cc.py', out / 'cc.py')
    shutil.copy2(src / 'COPYRIGHT', out / 'COPYRIGHT')
    (out / 'inputs.json').write_text(json.dumps(hashes, indent=2) + '\n')
    text = original.read_text()
    require(text.count('syscall(SYS_writev,') == 1, 'write hook anchor')
    control = text.replace('__stdio_write(', 'control_stdio_write(')
    candidate = text.replace('__stdio_write(', 'candidate_stdio_write(').replace('syscall(SYS_writev,', 'fixture_writev(')
    (out / 'control.c').write_text(control)
    (out / 'candidate.c').write_text(candidate)
    (out / 'patch.json').write_text(json.dumps({'original_sha256': sha(original),
        'control_sha256': sha(out / 'control.c'), 'candidate_sha256': sha(out / 'candidate.c'),
        'changes': ['rename function for fixture', 'replace only SYS_writev call with fixture_writev']}, indent=2) + '\n')
    env = clean_env(out)

    def checked(label, argv):
        r = run(argv, cwd=ROOT, env=env, work=out, label=label, timeout=60)
        require(r.record['complete'] and r.returncode == 0, label)
        return r

    checked('format', ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang-format', '--dry-run', '--Werror',
                      '--style=file:docs/quality/clang-format.yaml'] + [str(out / n) for n in ('vector.c', 'vector.h', 'stdio-loop-controls.c', 'stdio-loop.h')])
    base = [str(out / 'cc.py'), '-std=c17', '-O1', '-Wall', '-Wextra', '-Werror', '-I', str(out)]
    internal = ['-I' + str(out / 'musl' / d) for d in ('src/include', 'src/internal', 'arch/x86_64', 'arch/generic')]
    for name in ('control', 'candidate'):
        checked(name+'-compile', base + internal + ['-Wno-sign-compare', '-Wno-unused-parameter',
            '-include', str(out / 'stdio-loop.h'), '-c', str(out / (name+'.c')), '-o', str(out / (name+'.o'))])
    checked('fixture-compile', base + internal + ['-Wno-unused-parameter', '-c', str(out / 'stdio-loop-controls.c'), '-o', str(out / 'fixture.o')])
    variants = {'baseline': (out / 'vector.c').read_text(),
                'lose-poison': (out / 'vector.c').read_text().replace('s->poisoned = 1;', 's->poisoned = 0;'),
                'wrong-order': (out / 'vector.c').read_text().replace('memcpy(bytes + used, parts[i].data, n);', 'memcpy(bytes, parts[i].data, n);')}
    for name, body in variants.items():
        (out / (name+'.c')).write_text(body)
        checked(name+'-compile', base + ['-c', str(out / (name+'.c')), '-o', str(out / (name+'.o'))])
        checked(name+'-link', [str(out / 'cc.py'), '-Wl,-z,noexecstack', '-Wl,--no-undefined',
            str(out / (name+'.o')), str(out / 'fixture.o'), str(out / 'control.o'), str(out / 'candidate.o'), '-o', str(out / name)])
        checked(name+'-headers', [receipt['tools']['readelf']['path'], '-h', '-l', str(out / name)])
    report = {'status': 'incomplete', 'scope': 'Actual musl FILE callback Linux reference; no native wiring',
              'image': IMAGE, 'inputs': hashes, 'python': sys.version, 'variants': {}}
    def save():
        (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for name in variants:
        container = 'userland-stdio-loop-' + uuid.uuid4().hex
        argv = [PODMAN, 'run', '--name', container, '--rm', '--pull=never', '--network=none',
                '--read-only', '--cap-drop=all', '--security-opt=no-new-privileges', '--user=65534:65534',
                '--memory=512m', '--pids-limit=32', '--mount', 'type=bind,src='+str(out)+',dst=/inputs,ro=true',
                '--env', 'LC_ALL=C', '--entrypoint=/usr/bin/qemu-x86_64', IMAGE, '/inputs/'+name]
        try:
            r = run(argv, cwd=ROOT, env=dict(env, HOME=os.environ['HOME']), work=out, label=name, timeout=60)
        finally:
            cleanup = run([PODMAN, 'rm', '--force', '--ignore', container], cwd=ROOT,
                          env=dict(env, HOME=os.environ['HOME']), work=out, label=name+'-cleanup', timeout=15)
        ok = (r.record['complete'] and cleanup.record['complete'] and cleanup.returncode == 0)
        if name == 'baseline':
            ok = ok and r.returncode == 0 and r.stdout == b'PASS: 9720 musl-loop cases and pipe control\n' and not r.stderr
        else:
            ok = ok and r.returncode == 99 and b'Assertion failed' in r.stderr
        report['variants'][name] = {'pass': bool(ok), 'elf_sha256': sha(out / name), 'exit': r.returncode}
        save()
        require(ok, name + ' failed; see ' + str(out))
    for p, digest in hashes.items():
        require(sha(Path(p)) == digest, 'input changed')
    report['status'] = 'pass'
    save()
    print('[PASS] 9720 musl-loop cases, pipe control and two mutants')


if __name__ == '__main__':
    main()
