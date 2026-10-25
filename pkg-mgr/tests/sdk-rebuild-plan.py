#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Retained synthetic private-root SDK planner controls; no native execution."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
SDK = 'aether-musl-sdk'
(REPO / 'work').mkdir(exist_ok=True)
WORK = Path(tempfile.mkdtemp(prefix='sdk-plan-', dir=REPO / 'work'))
COMMANDS = []
CASES = []
SCRATCH = WORK/'scratch'; SCRATCH.mkdir(mode=0o700)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args, status=0, env=None):
    start = time.monotonic()
    result = subprocess.run([str(a) for a in args], cwd=REPO, capture_output=True,
                            env=dict(os.environ, **(env or {})), timeout=60)
    COMMANDS.append(dict(argv=[str(a) for a in args], status=result.returncode,
                         stdout=result.stdout.decode(errors='backslashreplace'),
                         stderr=result.stderr.decode(errors='backslashreplace'),
                         seconds=time.monotonic()-start))
    assert result.returncode == status, COMMANDS[-1]
    return result

def snapshot(root):
    result = {}
    for p in [root, *root.rglob('*')]:
        info = p.lstat()
        data = os.readlink(p) if p.is_symlink() else digest(p) if stat.S_ISREG(info.st_mode) else None
        result[str(p.relative_to(root))] = [stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode), data]
    return result

def register(root, name):
    stage = root / 'stage' / name
    evidence = WORK / ('input-' + str(len(COMMANDS)))
    evidence.mkdir()
    manifest = evidence / 'manifest'
    run(['sh', 'mk/verify-metadata.sh', 'manifest', stage, manifest])
    replacements = {'package_name': name, 'manifest_ref': str(manifest.relative_to(REPO))}
    rows = (REPO / 'fixtures/metadata-boundary/build-input.kv').read_text().splitlines()
    (evidence / 'input').write_text(''.join(k+'='+replacements.get(k, v)+'\n'
        for k, v in (line.split('=', 1) for line in rows)))
    run(['sh', 'mk/verify-metadata.sh', 'build-record', evidence/'input', evidence/'build'])
    (evidence / 'deps').write_bytes(b'')
    # Fixture-only re-registration after deliberate payload mutations.
    record = root/'state/packages'/f'{name}.tsv'
    if record.exists():
        record.unlink()
    run(['sh', 'mk/state.sh', 'register', root, manifest, evidence/'build', evidence/'deps'])

def edges(root, mapping):
    for name, deps in mapping.items():
        p = root/'state/packages'/f'{name}.tsv'
        lines = [line for line in p.read_text().splitlines() if not line.startswith('dependency\t')]
        offset = next(i for i, line in enumerate(lines) if line.startswith('file\t'))
        lines[offset:offset] = ['dependency\t'+dep for dep in sorted(deps)]
        p.write_text('\n'.join(lines)+'\n')

def init(label, changed=False):
    root = WORK/label
    root.mkdir(mode=0o700)
    run(['make', '-s', '-f', 'mk/pkg.mk', f'ROOT={root}', 'init-root'])
    run(['sh', 'mk/state.sh', 'init', root])
    (root/'sentinel').write_bytes(b'keep\n')
    stage = root/'stage'/SDK
    meta = stage/'usr/local/share/pkg-mgr'/SDK
    meta.mkdir(parents=True)
    (stage/'payload').write_bytes(b'changed SDK\n' if changed else b'original SDK\n')
    (meta/'sdk-build-receipt').write_bytes(b'synthetic build\n')
    (meta/'sdk-native-profile').write_bytes(b'synthetic profile\n')
    (meta/'sdk-target.kv').write_text('format=cross-sdk-target-v1\nrole=build-inputs-only\n'
        'build_os=FixtureOS\nbuild_arch=fixture64\ncompiler_target=fixture-none\n'
        f'build_receipt_sha256={digest(meta/"sdk-build-receipt")}\n'
        f'native_profile_sha256={digest(meta/"sdk-native-profile")}\n'
        'modes=recorded-0000-0777\n')
    register(root, SDK)
    return root

def binding(root, name):
    return root/'stage'/name/'usr/local/share/pkg-mgr'/name/'sdk-binding.kv'

def record_pin(root, name=SDK):
    return digest(root/'state/packages'/f'{name}.tsv')

try:
    installed = init('installed')
    candidate = init('candidate', True)
    pin = record_pin(installed)
    target_pin = digest(candidate/'stage'/SDK/'usr/local/share/pkg-mgr'/SDK/'sdk-target.kv')
    # Hand-written graph oracle: diamond, cycle and a package literally named record.
    graph = {'base': [SDK], 'record': [SDK, 'base'], 'left': ['base'],
             'right': ['base'], 'top': ['left', 'right'], 'cycle': ['top', 'cycle2'],
             'cycle2': ['cycle'], 'unrelated': []}
    for name in graph:
        stage = installed/'stage'/name
        stage.mkdir(parents=True)
        (stage/(name+'-artifact')).write_bytes(b'identical ELF-shaped data; never executed\n')
        if SDK in graph[name]:
            (stage/(name+'-inputs')).write_bytes(b'opaque synthetic inputs\n')
            b = binding(installed, name); b.parent.mkdir(parents=True)
            b.write_text('format=sdk-static-binding-v1\nsdk_package=aether-musl-sdk\n'
                f'sdk_record_sha256={pin}\ninput_receipt_path={name}-inputs\n'
                f'input_receipt_sha256={digest(stage/(name+"-inputs"))}\nartifact_path={name}-artifact\n'
                f'artifact_sha256={digest(stage/(name+"-artifact"))}\n')
        register(installed, name)
    edges(installed, graph)
    # World does not limit the selection (it contains only the SDK).
    (installed/'state/world').write_text(SDK+'\n')
    expected = {'base': 'direct', 'record': 'direct', 'left': 'transitive',
                'right': 'transitive', 'top': 'transitive', 'cycle': 'transitive', 'cycle2': 'transitive'}

    def invoke(label, root=installed, selected=candidate, status=0, selection=None,
               pins=None, env=None, diagnostic=None):
        before = [snapshot(root), snapshot(selected)]
        args = ['sh', 'mk/sdk-rebuild-plan.sh', root, selected,
                *(pins or [record_pin(root), record_pin(selected), target_pin])]
        result = run(args, status, {'TMPDIR': str(SCRATCH), **(env or {})})
        assert not list(SCRATCH.iterdir()), label
        assert before == [snapshot(root), snapshot(selected)], label
        if status:
            assert result.stdout == b'', (label, result.stdout)
            if diagnostic:
                assert result.stderr == f'sdk-plan-error: {diagnostic}\n'.encode(), COMMANDS[-1]
        else:
            assert result.stderr == b'', COMMANDS[-1]
            lines = ['format\tsdk-rebuild-plan-v1', 'sdk-installed\t'+record_pin(root),
                     'sdk-candidate\t'+record_pin(selected), 'candidate-profile\t'+target_pin,
                     'world\t'+digest(root/'state/world')]
            lines += ['record\t'+p.stem+'\t'+digest(p) for p in sorted((root/'state/packages').glob('*.tsv'))]
            lines += ['requalify\t'+n+'\t'+scope+'\t'+record_pin(root, n)
                      for n, scope in sorted((selection or {}).items())]
            assert result.stdout == ('\n'.join(lines)+'\n').encode(), COMMANDS[-1]
        CASES.append(label)
        return result

    invoke('changed-sdk-closure', selection=expected)
    same = WORK/'same-sdk'; shutil.copytree(candidate, same)
    shutil.copytree(installed/'stage'/SDK, same/'stage'/SDK, dirs_exist_ok=True)
    shutil.copy2(installed/'state/packages'/f'{SDK}.tsv', same/'state/packages'/f'{SDK}.tsv')
    invoke('unchanged-sdk-empty-selection', selected=same)
    invoke('wrong-installed-pin', status=1, pins=['0'*64, record_pin(candidate), target_pin], diagnostic='SDK record pin mismatch')
    invoke('wrong-candidate-pin', status=1, pins=[pin, '0'*64, target_pin], diagnostic='SDK record pin mismatch')
    invoke('wrong-profile-pin', status=1, pins=[pin, record_pin(candidate), '0'*64], diagnostic='candidate profile invalid')
    invoke('malformed-pin', status=64, pins=['x', record_pin(candidate), target_pin])

    def variant(label, edit, diagnostic, unchanged=False):
        root = WORK/label; shutil.copytree(installed, root)
        edit(binding(root, 'base'))
        # Remove graph edges while the test re-registers the edited consumer.
        edges(root, {n: [] for n in graph})
        register(root, 'base')
        edges(root, graph)
        invoke(label, root=root, selected=same if unchanged else candidate,
               status=1, diagnostic=diagnostic)

    original = binding(installed, 'base').read_bytes()
    mutations = {
        'stale-binding': (original.replace(pin.encode(), b'0'*64), 'stale SDK binding'),
        'bad-version': (original.replace(b'binding-v1', b'binding-v2'), 'invalid binding grammar'),
        'wrong-sdk': (original.replace(b'sdk_package=aether-musl-sdk', b'sdk_package=other'), 'invalid binding grammar'),
        'missing-row': (b'\n'.join(original.split(b'\n')[1:]), 'invalid binding grammar'),
        'duplicate-row': (original+original.splitlines()[0]+b'\n', 'invalid binding grammar'),
        'unknown-key': (original.replace(b'artifact_path=', b'unknown_path='), 'invalid binding grammar'),
        'missing-lf': (original[:-1], 'noncanonical binding bytes'),
        'crlf': (original.replace(b'\n', b'\r\n'), 'invalid binding grammar'),
        'nul': (original.replace(b'inputs\n', b'inputs\x00\n'), 'invalid binding grammar'),
        'parent-path': (original.replace(b'artifact_path=base-artifact', b'artifact_path=../artifact'), 'invalid binding grammar'),
        'absolute-path': (original.replace(b'artifact_path=base-artifact', b'artifact_path=/artifact'), 'invalid binding grammar'),
        'same-path': (original.replace(b'artifact_path=base-artifact', b'artifact_path=base-inputs'), 'binding paths must be distinct'),
        'artifact-pin': (original.replace(digest(installed/'stage/base/base-artifact').encode(), b'0'*64), 'bound file hash mismatch'),
        'oversize-binding': (b'x'*4097, 'metadata limit exceeded'),
    }
    for label, (data, diagnostic) in mutations.items():
        variant(label, lambda p, data=data: p.write_bytes(data), diagnostic)
    variant('stale-even-unchanged', lambda p: p.write_bytes(mutations['stale-binding'][0]), 'stale SDK binding', True)
    variant('missing-binding', lambda p: p.unlink(), 'expected regular input')
    variant('missing-even-unchanged', lambda p: p.unlink(), 'expected regular input', True)

    def raw(label, edit, diagnostic):
        root = WORK/label; shutil.copytree(installed, root); edit(root)
        invoke(label, root=root, status=1, diagnostic=diagnostic)
    raw('pending', lambda r: (r/'.replacement').mkdir(), None)
    raw('v1', lambda r: (r/'state/packages/base.tsv').write_bytes(
        (r/'state/packages/base.tsv').read_bytes().replace(b'pkg-state-v2', b'pkg-state-v1')), 'v2 records required')
    raw('world-oversize', lambda r: (r/'state/world').write_bytes(b'x'*1048577), 'metadata limit exceeded')
    raw('record-oversize', lambda r: (r/'state/packages/base.tsv').write_bytes(b'x'*1048577), 'metadata limit exceeded')
    raw('receipt-substitution', lambda r: (r/'stage/base/base-inputs').write_bytes(b'changed\n'), 'state verification failed')
    raw('symlink-binding', lambda r: (binding(r,'base').unlink(), binding(r,'base').symlink_to(WORK/'outside')), 'state verification failed')
    raw('fifo-binding', lambda r: (binding(r,'base').unlink(), os.mkfifo(binding(r,'base'))), 'state verification failed')
    raw('dangling-dependency', lambda r: edges(r, {'base': ['missing']}), 'state verification failed')
    invoke('same-roots', selected=installed, status=1, diagnostic='roots must be separate')
    invoke('scratch-inside-root', status=1, env={'TMPDIR': str(installed)}, diagnostic='scratch must be outside roots')
    invoke('missing-scratch', status=1, env={'TMPDIR': str(WORK/'absent')})

    # Bound failures happen before interpreting these deliberately invalid records.
    raw('edge-limit', lambda r: (r/'state/packages/base.tsv').write_bytes(
        b'format\tpkg-state-v2\n'+b'dependency\tx\n'*16385), 'edge limit exceeded')
    def too_many(r):
        for i in range(1025):
            (r/'state/packages'/f'p{i}.tsv').write_bytes(b'format\tpkg-state-v2\n')
    raw('package-limit', too_many, 'package limit exceeded')
    def aggregate(r):
        for i in range(17):
            (r/'state/packages'/f'a{i}.tsv').write_bytes(b'format\tpkg-state-v2\n'+b'x'*(1048576-20))
    raw('aggregate-limit', aggregate, 'aggregate record limit exceeded')
    def receipt_size(size):
        root = WORK/f'receipt-size-{size}'; shutil.copytree(installed, root)
        payload = root/'stage/base/base-inputs'; payload.write_bytes(b'x'*size)
        b = binding(root, 'base')
        b.write_bytes(b.read_bytes().replace(digest(installed/'stage/base/base-inputs').encode(), digest(payload).encode()))
        edges(root, {n: [] for n in graph}); register(root, 'base'); edges(root, graph)
        invoke(f'receipt-size-{size}', root=root, status=0 if size==1048576 else 1,
               selection=expected, diagnostic=None if size==1048576 else 'metadata limit exceeded')
    receipt_size(1048576)
    receipt_size(1048577)

    # Failed providers must not turn plausible hash bytes into accepted evidence.
    tools = WORK/'tools'; tools.mkdir()
    wrapper = tools/'sh'
    wrapper.write_text('''#!/bin/sh
if test "$#" -eq 3 && test "${1##*/}" = verify-metadata.sh && test "$2" = hash-file && test "$3" = "$HASH_TARGET"; then
    "$REAL_SH" "$@" || exit
    exit 73
fi
exec "$REAL_SH" "$@"
'''); wrapper.chmod(0o700)
    invoke('plausible-failed-hash', status=1, diagnostic='cannot hash record', env={
        'PATH': str(tools)+os.pathsep+os.environ['PATH'], 'REAL_SH': shutil.which('sh'),
        'HASH_TARGET': str(installed/'state/packages'/f'{SDK}.tsv')})
    # Revalidation must notice an injected world change without repairing it.
    wrapper.write_text('''#!/bin/sh
if test "$#" -eq 3 && test "${1##*/}" = state.sh && test "$2" = verify && test "$3" = "$DRIFT_ROOT"; then
    count=0
    if test -f "$DRIFT_COUNT"; then read -r count < "$DRIFT_COUNT"; fi
    count=$((count+1)); printf '%s\\n' "$count" > "$DRIFT_COUNT"
    if test "$count" -eq 2; then : > "$DRIFT_ROOT/state/world"; fi
fi
exec "$REAL_SH" "$@"
''')
    root = WORK/'drift'; shutil.copytree(installed, root)
    before = snapshot(root); world = (root/'state/world').read_bytes()
    result = run(['sh', 'mk/sdk-rebuild-plan.sh', root, candidate, pin, record_pin(candidate), target_pin], 1, {
        'PATH': str(tools)+os.pathsep+os.environ['PATH'], 'REAL_SH': shutil.which('sh'),
        'DRIFT_ROOT': str(root), 'DRIFT_COUNT': str(WORK/'drift-count'), 'TMPDIR': str(SCRATCH)})
    assert result.stdout == b'' and result.stderr == b'sdk-plan-error: input drift detected\n'
    assert (root/'state/world').read_bytes() == b''
    (root/'state/world').write_bytes(world)  # Undo only this test's injected edit.
    assert snapshot(root) == before and not list(SCRATCH.iterdir())
    CASES.append('world-drift')
    wrapper.unlink()

    # Inject a failed final delivery and a catchable interruption at that boundary.
    cat_wrapper = tools/'cat'
    cat_wrapper.write_text('''#!/bin/sh
case ${1-} in */report)
    if test "$INJECT" = signal; then kill -TERM "$PPID"; fi
    exit 73 ;;
esac
exec "$REAL_CAT" "$@"
'''); cat_wrapper.chmod(0o700)
    for injection in ['write', 'signal']:
        invoke('final-'+injection, status=1, env={
            'PATH': str(tools)+os.pathsep+os.environ['PATH'], 'REAL_CAT': shutil.which('cat'),
            'INJECT': injection})
    cat_wrapper.unlink()
    # A provider's successful-looking header with failed status must also reject.
    head_wrapper = tools/'head'
    head_wrapper.write_text('''#!/bin/sh
"$REAL_HEAD" "$@" || exit
exit 73
'''); head_wrapper.chmod(0o700)
    invoke('plausible-failed-header', status=1, diagnostic='cannot read record header', env={
        'PATH': str(tools)+os.pathsep+os.environ['PATH'], 'REAL_HEAD': shutil.which('head')})
    head_wrapper.unlink()
    root = WORK/'root with spaces'; shutil.copytree(installed, root)
    invoke('root-with-spaces', root=root, selection=expected)
    invoke('candidate-has-consumers', root=same, selected=installed, status=1,
           diagnostic='candidate must contain only SDK')
    print(f'PASS: {len(CASES)} SDK rebuild-plan controls; evidence: {WORK}')
finally:
    (WORK/'result.json').write_text(json.dumps({'cases': CASES, 'commands': COMMANDS,
        'inputs': {p: digest(REPO/p) for p in ['mk/sdk-rebuild-plan.sh', 'mk/sdk-rebuild-plan.awk',
                    'tests/sdk-rebuild-plan.py', 'mk/state.sh', 'mk/sdk-profile.sh']}}, indent=2)+'\n')
    print(f'SDK planner retained run: {WORK}', flush=True)
