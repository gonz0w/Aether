# SPDX-License-Identifier: BSD-2-Clause
"""Run the isolated host decoder proposal; never modify runtime sources."""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'experiments/command-runner'
P = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from process import clean_env, run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


baseline = json.loads((P / 'baseline.json').read_text())
for name, digest in baseline.items():
    assert sha(HERE / name) == digest, name
work = Path(tempfile.mkdtemp(prefix='sustained-decoder-', dir=ROOT / 'build'))
print(work, flush=True)
src = work / 'source'
src.mkdir()
for name in baseline:
    shutil.copy2(HERE / name, src / name)
clang = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang-21')
assert sha(clang) == '625165a3accc542dafef0264b5bbd18721b8e765c7ec819742ec7d7afd2491f6'
inputs = {str(f.relative_to(ROOT)): sha(f) for f in P.iterdir() if f.is_file()}
inputs.update({str((HERE / n).relative_to(ROOT)): d for n, d in baseline.items()})
for name in inputs:
    dest = work / 'inputs' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, dest)
report = {'status': 'incomplete', 'inputs': inputs, 'platform': platform.platform(),
          'python': {'path': sys.executable, 'sha256': sha(Path(sys.executable).resolve()),
                     'version': sys.version},
          'clang': {'path': str(clang), 'sha256': sha(clang)},
          'native_execution': 'NOT RUN', 'commands': []}
env = clean_env(work)
env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'


def save():
    (work / 'results.json').write_text(json.dumps(report, indent=2) + '\n')


def command(label, argv, cwd=work, expected=0):
    tool = Path(argv[0]).resolve()
    report.setdefault('tools', {})[str(tool)] = sha(tool)
    save()
    result = run(argv, cwd=cwd, env=env, work=work, label=label,
                 timeout=30, file_limit=16 * 1024**2)
    report['commands'].append(result.record)
    save()
    assert result.record['complete'] and result.record['cleanup'] == 'complete', label
    if expected == 0:
        assert result.returncode == 0, label
    else:
        assert result.returncode != 0, label
    return result


command('patch', ['/usr/bin/patch', '--batch', '--fuzz=0', '-p1', '-i', str(P / 'decoder.patch')], src)
report['patched_sources'] = {f.name: sha(f) for f in src.iterdir() if f.is_file()}
host_sdk = command('host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
resource = command('resource', [str(clang), '--no-default-config', '-print-resource-dir']).stdout.decode().strip()
runtime = Path(resource) / 'lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib'
report['ubsan'] = {'path': str(runtime), 'sha256': sha(runtime)}
report['host_sdk'] = {'path': host_sdk, 'sha256': sha(Path(host_sdk) / 'SDKSettings.json')}
flags = [str(clang), '--no-default-config', '-std=c17', '-Wall', '-Wextra', '-Werror',
         '-O1', '-g', '-fno-omit-frame-pointer', '-fsanitize=undefined',
         '-fno-sanitize-recover=all', '-isysroot', host_sdk]
for label, source, control in [('roles', 'four-role.c', 'four-role-controls.c'),
                               ('results', 'runner-result.c', 'result-controls.c')]:
    for profile, location, controls in [('legacy', HERE, HERE), ('v2', src, P)]:
        name = profile + '-' + label
        command(name + '-build', flags + ['-I', str(location), str(location / source),
            str(controls / control), '-o', str(work / name)])
        command(name + '-run', [str(work / name)])
objects = []
for profile, location in [('legacy', HERE), ('v2', src)]:
    for source in ['four-role.c', 'runner-result.c']:
        obj = work / (profile + '-' + source + '.o')
        command(obj.stem, flags + ['-I', str(location), '-c', str(location / source), '-o', str(obj)])
        objects.append(str(obj))
command('peer-build', flags + ['-I', str(src), str(P / 'peer-controls.c')] + objects + ['-o', str(work / 'peer')])
command('peer-run', [str(work / 'peer')])
# The control uses v2 declarations but supplies legacy definitions. Require the
# undefined versioned symbol, not an arbitrary compiler or tool failure.
negative = command('mixed-link', flags + ['-I', str(src), str(P / 'four-role-controls.c'),
    str(work / 'legacy-four-role.c.o'), '-o', str(work / 'must-not-link')], expected=1)
assert b'Undefined symbols' in negative.stderr and b'ar_roles_decode_sustained_v2' in negative.stderr
assert not (work / 'must-not-link').exists()
formatter = clang.parent / 'clang-format'
command('format', [str(formatter), '--dry-run', '--Werror',
    '--style=file:' + str(ROOT / 'docs/quality/clang-format.yaml')] +
    [str(P / n) for n in ['peer-controls.c', 'four-role-controls.c', 'result-controls.c']])
command('syntax', [sys.executable, '-B', '-c',
    'import ast,pathlib; ast.parse(pathlib.Path(' + repr(str(P / 'check.py')) + ').read_text())'])
for name, digest in inputs.items():
    assert sha(ROOT / name) == digest, name
assert sha(clang) == report['clang']['sha256']
report['status'] = 'pass'
save()
print('PASS: isolated v2 decoder, legacy compatibility and mixed-link rejection')
