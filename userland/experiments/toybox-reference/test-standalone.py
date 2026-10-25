#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Test one pinned standalone Toybox applet in QEMU Linux; Python 3.12+."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
from build import Parser, sha, require
from test import matches, PODMAN, IMAGE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import run as owned_run


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('build', type=Path, help='standalone reference build directory')
    parser.add_argument('--version', action='version', version='toybox-standalone-test 0.1.0')
    a = parser.parse_args()
    build = a.build.resolve()
    evidence = json.loads((build / 'evidence.json').read_text())
    applet = evidence.get('applet')
    require(applet in ('cat', 'wc'), 'not a standalone candidate')
    src = build / 'toybox-0.8.14'
    require(sha(src / 'toybox') == evidence['elf_sha256'], 'ELF changed')
    for name, h in evidence['files'].items():
        require(sha(Path(name)) == h, 'build input changed: ' + name)
    for name, h in evidence['test_inputs'].items():
        require(sha(src / name) == h, 'upstream input changed: ' + name)
    out = Path(tempfile.mkdtemp(prefix='toybox-single-tests-', dir=ROOT / 'build'))
    print(out, flush=True)
    shutil.copy2(src / 'toybox', out / 'candidate')
    shutil.copytree(src / 'tests', out / 'tests')
    shutil.copy2(src / 'scripts/runtest.sh', out / 'runtest.sh')
    (out / 'bin').mkdir()
    wrapper = out / 'bin' / applet
    wrapper.write_text('#!/bin/sh\nexec /usr/bin/qemu-x86_64 /inputs/candidate "$@"\n')
    wrapper.chmod(0o555)
    (out / 'upstream.sh').write_text(
        '#!/bin/bash\nset -o pipefail\nexport PATH=/inputs/bin:/usr/bin:/bin LC_ALL=C\n'
        'export TESTDIR=/scratch FILES=/inputs/tests/files\n'
        'export CMDNAME="$1" C="/inputs/bin/$1"\ncd /scratch || exit 90\n'
        'source /inputs/runtest.sh\nsource "/inputs/tests/$1.test"\n'
        'echo "UPSTREAM_FAILCOUNT=$FAILCOUNT"\n[ "$FAILCOUNT" -eq 0 ]\n')
    sources = {str(p): sha(p) for p in (Path(__file__), HERE / 'build.py', HERE / 'test.py',
               ROOT / 'experiments/command-runner/process.py')}
    for name in sources:
        shutil.copy2(name, out / Path(name).name)
    report = {'status': 'incomplete', 'applet': applet, 'image': IMAGE, 'sources': sources,
              'elf_sha256': evidence['elf_sha256'], 'build_receipt_sha256': sha(build / 'evidence.json'),
              'scope': 'QEMU Linux reference, not Aether', 'cases': []}
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'HOME': os.environ['HOME'],
           'TMPDIR': str(out)}

    def save():
        (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    def run(label, args, expected_status=0, expected=b'', stdin=b'', diagnostic=None,
            entry='/usr/bin/qemu-x86_64', timeout=45):
        container = 'userland-toybox-single-' + uuid.uuid4().hex
        argv = [PODMAN, 'run', '--name', container, '--rm', '-i', '--pull=never',
                '--network=none', '--read-only', '--cap-drop=all',
                '--security-opt=no-new-privileges', '--user=65534:65534',
                '--memory=512m', '--pids-limit=32', '--tmpfs', '/scratch:rw,nosuid,size=16m,mode=1777',
                '--mount', 'type=bind,src=' + str(out) + ',dst=/inputs,ro=true',
                '--env', 'LC_ALL=C', '--entrypoint=' + entry, IMAGE] + args
        try:
            result = owned_run(argv, cwd=ROOT, env=env, work=out, label=label,
                               timeout=timeout, input=stdin)
        finally:
            cleanup = owned_run([PODMAN, 'rm', '--force', '--ignore', container],
                                cwd=ROOT, env=env, work=out, label=label+'-cleanup', timeout=15)
        ok = (result.record['complete'] and cleanup.record['complete'] and
              matches(result.returncode, expected_status, cleanup.returncode,
                      result.stdout, expected, result.stderr, diagnostic))
        report['cases'].append({'case': label, 'pass': ok, 'expected_exit': expected_status,
                                'expected_stdout_hex': expected.hex() if expected is not None else None,
                                'diagnostic_hex': diagnostic.hex() if diagnostic else None,
                                'process': result.record, 'cleanup': cleanup.record})
        save()
        require(ok, label + ' failed; see ' + str(out))
        return result.stdout

    save()
    try:
        binary = bytes(range(256)) * 33
        run('binary', ['/inputs/candidate'] + ([] if applet == 'cat' else ['-c']),
            expected=binary if applet == 'cat' else b'8448\n', stdin=binary)
        run('empty', ['/inputs/candidate'] + ([] if applet == 'cat' else ['-c']),
            expected=b'' if applet == 'cat' else b'0\n')
        run('dash', ['/inputs/candidate'] + (['-'] if applet == 'cat' else ['-l', '-']),
            expected=b'a\nb\n' if applet == 'cat' else b'2 -\n', stdin=b'a\nb\n')
        run('missing', ['/inputs/candidate', '/inputs/missing'], 1, diagnostic=b'No such file')
        run('full', ['-c', 'exec /usr/bin/qemu-x86_64 /inputs/candidate > /dev/full'],
            1, stdin=b'data\n', diagnostic=b'No space left', entry='/bin/sh')
        report['wrong_output_rejected'] = not matches(0, 0, 0, (out/'binary.stdout').read_bytes(),
                                                      b'wrong-output', b'', None)
        log = run('upstream', ['/inputs/upstream.sh', applet], expected=None,
                  entry='/bin/bash', timeout=180)
        counts = {kind: sum(line.startswith(kind.encode()+b':') for line in log.splitlines())
                  for kind in ('PASS','FAIL','SKIP')}
        report['upstream_counts'] = counts
        require(counts == {'PASS': 9 if applet == 'cat' else 25, 'FAIL': 0, 'SKIP': 0},
                'upstream discovery/count mismatch')
        require(report['wrong_output_rejected'], 'matcher accepted wrong output')
        for name,h in sources.items():
            require(sha(Path(name)) == h, 'test input changed')
        require(sha(src/'toybox') == evidence['elf_sha256'], 'ELF changed during tests')
        report['status'] = 'pass'
    finally:
        save()
    print('[PASS] standalone '+applet+' reference checks')


if __name__ == '__main__':
    main()
