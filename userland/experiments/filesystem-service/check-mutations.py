# SPDX-License-Identifier: BSD-2-Clause
"""Prove selected authority/progress tests detect removed enforcement."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
P = R / 'docs/evidence/filesystem-policy-2026-10-18'
I = json.loads((P / 'inputs.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
rustc = Path(I['tools']['rustc']['path'])
assert sha(rustc) == I['tools']['rustc']['sha256']
W = Path(tempfile.mkdtemp(prefix='filesystem-policy-mutations-', dir=R / 'build'))
env = proc.clean_env(W)
source = (S / 'owner.rs').read_text()
mutations = {
    'write-authority': ('if !file.rights.contains(Rights::WRITE)', 'if false'),
    'endpoint-binding': ('c.peer != peer', '{ let _ = peer; c.peer == 0 }'),
    'alias-size': ('open.node.size = file.node.size.max(end);', 'let _ = end;'),
    'retirement': ('self.poisoned = true;\n        self.shutdown();', 'self.poisoned = true;'),
    'single-write': ('self.write_used = true;', 'self.write_used = false;'),
    'clock-bounds': ('utc.seconds > i64::MAX as u64 || utc.nanoseconds >= 1_000_000_000',
                     'utc.seconds == u64::MAX && utc.nanoseconds == u64::MAX'),
    'assigned-txg': ('            || completion.txg == 0\n', ''),
    'reply-zero': ('        reply.fill(0);\n', ''),
}
rows = []
record = {'status': 'running', 'root': str(W), 'source_sha256': sha(S / 'owner.rs'),
          'tests_sha256': sha(S / 'tests.rs'), 'driver_sha256': sha(Path(__file__)),
          'python': sys.version, 'rows': rows}
try:
    for name, (old, new) in mutations.items():
        assert old in source, name
        path = W / name
        path.mkdir()
        selected = path / 'owner.rs'
        selected.write_text(source.replace(old, new, 1))
        shutil.copyfile(S / 'tests.rs', path / 'tests.rs')
        for stage, argv, expected in [
            ('compile', [rustc, '--edition=2021', '-Dwarnings', '-Funsafe-code', '--test', selected, '-o', path / 'tests'], 0),
            ('test', [path / 'tests', '--test-threads=1'], 101),
        ]:
            selected_env = dict(env)
            if stage == 'compile':
                selected_env['DYLD_LIBRARY_PATH'] = str(rustc.parent.parent / 'lib')
            label = name + '-' + stage
            result = proc.run([str(a) for a in argv], cwd=R, env=selected_env,
                              work=W, label=label, timeout=60 if stage == 'compile' else 30)
            rows.append({'name': label, 'expected': expected, 'record': result.record,
                         'mutated_source_sha256': sha(selected), 'replacement': [old, new]})
            assert result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', label
            if stage == 'test':
                output = (W / (label + '.stdout')).read_text()
                assert 'test result: FAILED.' in output and 'panicked at' in output, label
    assert sha(S / 'owner.rs') == record['source_sha256']
    assert sha(S / 'tests.rs') == record['tests_sha256']
    record.update(status='pass', semantic_omissions_detected=len(mutations), maintained_source_unchanged=True)
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Filesystem policy mutation check:', record['status'], str(W))
