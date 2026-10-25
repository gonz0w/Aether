# SPDX-License-Identifier: BSD-2-Clause
"""Owned offline host checks for the private filesystem policy layer."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
P = R / 'docs/evidence/filesystem-policy-2026-10-18'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = json.loads((P / 'inputs.json').read_text())
pair = json.loads((P / 'producer-pair.json').read_text())
for name, digest in inputs['producer_files'].items():
    path = P / 'producer-pair.json' if name.startswith('docs/evidence/') else P / 'producer' / name
    assert sha(path) == digest, name
    if not name.startswith('docs/evidence/'):
        assert pair['source_freeze_base'][name] == digest, name
for tool in inputs['tools'].values():
    assert sha(Path(tool['path'])) == tool['sha256']
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-policy-', dir=R / 'build'))
env = proc.clean_env(W)
tools = inputs['tools']
rust = Path(tools['rustc']['path']).parent
rows = []
record = {'root': str(W), 'status': 'running', 'rows': rows,
          'driver_sha256': sha(Path(__file__)), 'python': sys.version,
          'producer_input_manifest_sha256': sha(P / 'inputs.json')}


def run(name, args, timeout=60, rust_env=False):
    selected_env = dict(env)
    if rust_env:
        selected_env['DYLD_LIBRARY_PATH'] = str(rust.parent / 'lib')
    result = proc.run([str(a) for a in args], cwd=R, env=selected_env,
                      work=W, label=name, timeout=timeout)
    rows.append({'name': name, 'record': result.record})
    assert result.returncode == 0 and result.record['complete'] and result.record['cleanup'] == 'complete', name


try:
    run('rust-version', [tools['rustc']['path'], '-vV'], rust_env=True)
    run('rustfmt-version', [tools['rustfmt']['path'], '--version'], rust_env=True)
    run('clippy-version', [tools['clippy-driver']['path'], '--version'], rust_env=True)
    if '--format' in sys.argv[1:]:
        run('format', [tools['rustfmt']['path'], '--edition', '2021', '--config-path',
                      R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
                      S / 'owner.rs', S / 'tests.rs'], rust_env=True)
    source_pins = {str(p.relative_to(R)): sha(p) for p in (S / 'owner.rs', S / 'tests.rs', Path(__file__))}
    record['sources'] = source_pins
    run('format-check', [tools['rustfmt']['path'], '--edition', '2021', '--check',
                         '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
                         S / 'owner.rs', S / 'tests.rs'], rust_env=True)
    common = ['--edition=2021', '-Dwarnings', '-Funsafe-code', S / 'owner.rs']
    run('library', [tools['rustc']['path'], *common, '--crate-type=lib', '-Cpanic=abort', '-o', W / 'policy.rlib'], rust_env=True)
    run('clippy', [tools['clippy-driver']['path'], *common, '--crate-type=lib', '-Cpanic=abort', '-o', W / 'clippy.rlib'], rust_env=True)
    run('compile-tests', [tools['rustc']['path'], *common, '--test', '-o', W / 'tests'], rust_env=True)
    run('clippy-tests', [tools['clippy-driver']['path'], *common, '--test', '-o', W / 'clippy-tests'], rust_env=True)
    run('host-tests', [W / 'tests', '--test-threads=1'], 30)
    code = 'import pathlib,sys; [compile(pathlib.Path(f).read_bytes(),f,"exec") for f in sys.argv[1:]]'
    for name, py in [('10', R / 'build/python-qualification/Python-3.10.21/python.exe'),
                     ('14', Path('/opt/homebrew/opt/python@3.14/bin/python3.14'))]:
        run('syntax-' + name, [py, '-B', '-c', code, S / 'check.py', S / 'check-mutations.py'])
    run('quality', [sys.executable, '-B', R / 'docs/quality/check.py'], 180)
    run('whitespace', ['/usr/bin/git', 'diff', '--check'])
    for name, digest in source_pins.items():
        assert sha(R / name) == digest, name
    record.update(status='pass', no_std_library_sha256=sha(W / 'policy.rlib'),
                  host_tests_sha256=sha(W / 'tests'), native_execution=False,
                  scope='host policy and no_std library; no native FFI/wire/service acceptance',
                  reader_review='pending/deferred')
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Filesystem policy check:', record['status'], str(W))
