# SPDX-License-Identifier: BSD-2-Clause
"""Explicit host requalification of the two reviewed filesystem artifacts only.

The selected record hash is a review/configuration trust anchor, not native
capability authority or proof that a command was executed. All recorded claims
remain scoped to host evidence and are rechecked against current inputs.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re

from fs_host_dependencies import PREFIXES, declaration
from source_paths import ROOT, dependency_input, relocate

ENV_PATH = 'AETHER_FS_CONSUMER_ASSOCIATION'
ENV_SHA = 'AETHER_FS_CONSUMER_ASSOCIATION_SHA256'
FORMAT = 'aether-fs-host-consumer-association-v1'
PINS = {'af06': ('aether-fs-launch-build-v1', 'b69fd748b4d4fda334126dba96744a73f2a4b03649d5e9b1033ae253d52cc558'),
        'af07': ('aether-fs-metadata-launch-build-v1', '5e5625d21ab596a194c43235244548e29e570106d058f452ac9bbbf6ed0a3250')}
KERNEL = ('kernel/native_elf.zig', 'kernel/native_launch.zig', 'kernel/native_fs_session.zig',
          'kernel/native_memory.zig', 'kernel/arch/x86_64/native_c.zig',
          'kernel/arch/x86_64/native_fs_roles.zig', 'kernel/arch/x86_64/backing_pool.zig')
PRODUCER_EDITS = ('scripts/fs_metadata_launch.py', 'scripts/fs_launch_intake.py',
                  'scripts/service_runtime_smoke.py', 'scripts/source_paths.py',
                  'scripts/openzfs_elapsed.py')
ALLOWED = {'af06': {'kernel/native_elf.zig', *PRODUCER_EDITS},
           'af07': {*KERNEL, *PRODUCER_EDITS, 'scripts/fs_home_inputs.py', 'scripts/fs_home_launch.py'}}
REQUIRED_INPUTS = (*KERNEL, *PRODUCER_EDITS, 'build.zig', 'scripts/fs_host_dependencies.py',
                   'scripts/fs_consumer_association.py', 'scripts/fs_session.py',
                   'tests/test_fs_consumer_association.py', 'tests/test_fs_application_profile.py',
                   'tests/test_fs_launch_intake.py', 'tests/test_fs_metadata_launch_intake.py',
                   'tests/test_fs_session.py', 'tests/test_fs_owner_stack.py', 'tests/test_fs_af07_inputs.py')
CASES = {'af06-parser': ('large-accepted', 'ordinary-denied', 'missing-tls-denied', 'wx-denied', 'oversized-tls-denied', 'omission-denied'),
         'af07-parser': ('large-accepted', 'ordinary-denied', 'missing-tls-denied', 'wx-denied', 'oversized-tls-denied', 'omission-denied'),
         'legacy-models': ('old-selectors', 'role-authority', 'stale-grant', 'exhaustion', 'cleanup'),
         'application-models': ('launch-exec-copy', 'preflight-omissions', 'rollback-zero', 'binding-reset-reclaim', 'build-selection', 'start-order'),
         'legacy-kernel': ('kernel-check', 'footprint')}
MARKERS = {scope: ['FS-HOST '+scope+' '+case+' PASS' for case in cases] for scope, cases in CASES.items()}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def pairs(values):
    result = {}
    for key, value in values:
        if key in result:
            raise ValueError('duplicate association field')
        result[key] = value
    return result


def require(ok, message):
    if not ok:
        raise ValueError('host association '+message)


def sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def current_source(path):
    path = Path(path)
    require('..' not in path.parts, 'current source parent traversal')
    if not path.is_relative_to(ROOT):
        return
    relative = path.relative_to(ROOT)
    retained = any(relative.as_posix() == prefix or relative.as_posix().startswith(prefix+'/') for prefix in PREFIXES)
    if relative.parts and not retained and (relative.parts[0] in ('kernel','user','scripts','tests','userland','sys-init','pkg-mgr') or path == ROOT/'build.zig'):
        require(path.resolve() == path, 'current source path substitution')


def mapping(value):
    require(isinstance(value, dict) and value and all(isinstance(n, str) and Path(n).is_absolute() and sha(h) for n, h in value.items()), 'input map')
    for name, expected in value.items():
        current_source(name)
        require(Path(name).is_file() and digest(name) == expected, 'live input changed: '+name)


def load(path, expected):
    path = Path(path)
    require(path.is_absolute() and path.resolve() == path and not path.is_symlink() and path.is_file(), 'record path')
    require(sha(expected) and path.stat().st_size <= 2*1024*1024 and digest(path) == expected, 'record identity/size')
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def _function(module, name):
    values = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == name]
    require(len(values) == 1, 'producer function '+name)
    return values[0]


def _dump(node):
    return ast.dump(node, include_attributes=False)


def producer_unchanged(relative, baseline, current):
    """Compare the entire module after only the exact reviewed transformations."""
    expected = ast.parse(baseline)
    actual = ast.parse(current)
    if relative == 'scripts/fs_metadata_launch.py':
        function = _function(expected, 'closure')
        before = ast.parse('root = Path(directory).absolute()').body[0]
        after = ast.parse('from fs_host_dependencies import retained_root\nroot = retained_root(Path(directory).absolute())').body
        indices = [i for i, n in enumerate(function.body) if _dump(n) == _dump(before)]
        require(len(indices) == 1, 'baseline closure prefix')
        function.body[indices[0]:indices[0]+1] = after
        expected.body = [n for n in expected.body if not isinstance(n, ast.FunctionDef) or n.name != 'intake']
        actual.body = [n for n in actual.body if not isinstance(n, ast.FunctionDef) or n.name != 'intake']
    elif relative == 'scripts/service_runtime_smoke.py':
        function = _function(expected, 'sealed')
        before = ast.parse('root = Path(root).absolute()').body[0]
        indices = [i for i, n in enumerate(function.body) if _dump(n) == _dump(before)]
        require(len(indices) == 1, 'baseline sealed prefix')
        function.body[indices[0]:indices[0]+1] = ast.parse('from fs_host_dependencies import retained_root\nroot = retained_root(Path(root).absolute())').body
    elif relative == 'scripts/source_paths.py':
        function = _function(expected, 'dependency_input')
        require(_dump(function.body[-1]) == _dump(ast.parse('return path').body[0]), 'baseline migration fallback')
        function.body[-1:] = ast.parse('from fs_host_dependencies import retained_input\nreturn retained_input(path)').body
    elif relative == 'scripts/openzfs_elapsed.py':
        function = _function(expected, 'route')
        indices = [i for i, n in enumerate(function.body) if isinstance(n, ast.For) and isinstance(n.iter, ast.Name) and n.iter.id == 'roots']
        require(len(indices) == 1, 'baseline three route roots')
        loop = function.body[indices[0]]
        require(_dump(loop.body[0]) == _dump(ast.parse("old = str(ROOT / 'zig-out' / name)").body[0]), 'baseline route prefix')
        loop.body[1:1] = ast.parse("legacy = '/Users/cam/DEV/Aether/zig-out/' + name\narg = re.sub(re.escape(legacy) + r'(?=/|$)', old, arg)").body
    elif relative == 'scripts/fs_launch_intake.py':
        added = ast.parse("def actual_digest(path):\n    with Path(path).open('rb') as stream:\n        return hashlib.file_digest(stream, 'sha256').hexdigest()\n").body[0]
        index = expected.body.index(_function(expected, 'digest'))
        expected.body.insert(index, added)
        expected.body = [n for n in expected.body if not isinstance(n, ast.FunctionDef) or n.name != 'intake']
        actual.body = [n for n in actual.body if not isinstance(n, ast.FunctionDef) or n.name != 'intake']
    else:
        raise ValueError('host association unreviewed producer module')
    require(_dump(expected) == _dump(actual), 'producer logic/import/global drift: '+relative)


def _evidence(data):
    evidence = data['evidence']
    require(isinstance(evidence, dict) and set(evidence) == set(CASES), 'evidence scopes')
    for scope, group in evidence.items():
        require(isinstance(group, dict) and set(group) == {'commands', 'markers'} and group['markers'] == MARKERS[scope], 'evidence marker contract')
        commands = group['commands']
        require(isinstance(commands, list) and 1 <= len(commands) <= 128, 'evidence command count')
        output = ''
        actual_kernel = False
        actual_parser = False
        for row in commands:
            require(isinstance(row, dict) and set(row) == {'argv','cwd','tool','inputs','expected_exit','exit','complete','cleanup','failure','timeout_seconds','stdout','stderr','stdout_sha256','stderr_sha256'}, 'evidence command fields')
            argv = row['argv']
            require(isinstance(argv, list) and argv and all(isinstance(a, str) and '\0' not in a for a in argv), 'evidence argv')
            require(isinstance(row['cwd'], str) and Path(row['cwd']).is_absolute(), 'evidence cwd')
            tool = row['tool']
            require(isinstance(tool, dict) and set(tool) == {'path','sha256'} and tool['path'] == argv[0] and Path(argv[0]).is_absolute() and sha(tool['sha256']) and data['inputs'].get(argv[0]) == tool['sha256'], 'evidence tool')
            require(isinstance(row['inputs'], dict) and row['inputs'] and all(data['inputs'].get(n) == h for n,h in row['inputs'].items()), 'evidence frozen inputs')
            require(type(row['exit']) is int and type(row['expected_exit']) is int and row['exit'] == row['expected_exit'] and row['complete'] is True and row['cleanup'] == 'complete' and row['failure'] is None and type(row['timeout_seconds']) in (int, float) and 0 < row['timeout_seconds'] <= 180, 'evidence process incomplete')
            for stream in ('stdout','stderr'):
                text = row[stream]
                require(isinstance(text, str) and len(text.encode()) <= 4*1024*1024 and hashlib.sha256(text.encode()).hexdigest() == row[stream+'_sha256'], 'evidence output identity/bound')
                output += text+'\n'
            require(not re.search(r':\d+:\d+: error:', row['stdout']+row['stderr']), 'compile failure is not semantic evidence')
            if row['exit'] == 0 and row['expected_exit'] == 0 and Path(argv[0]).name == 'zig' and argv[1:3] == ['build','kernel-check']:
                require(row['cwd'] == str(ROOT) and '-Dnative-fs-owner-stack=true' in argv and '-Dsmp=false' in argv and '-Dnative-fs-application-profile=true' not in argv, 'legacy kernel selection')
                actual_kernel = True
            if row['exit'] == 0 and row['expected_exit'] == 0 and Path(argv[0]).name == 'zig' and argv[1:2] in (['run'], ['test']) and '-Mnative_elf='+str(ROOT/'kernel/native_elf.zig') in argv:
                actual_parser = True
            if Path(argv[0]).name.startswith('python'):
                program = 2 if argv[1:2] == ['-B'] else 1
                unittest_command = argv[program:program+2] == ['-m','unittest']
                source_command = program < len(argv) and argv[program].endswith('.py') and Path(argv[program]).is_absolute() and argv[program] in row['inputs']
                require(unittest_command or source_command, 'bound Python checker source')
                if unittest_command:
                    require(row['cwd'] == str(ROOT), 'current model source root')
        if scope == 'legacy-kernel':
            require(actual_kernel, 'missing actual legacy kernel command')
        if scope.endswith('-parser'):
            require(actual_parser, 'missing current actual parser command')
        require(all(output.count(marker) == 1 for marker in MARKERS[scope]), 'missing/duplicate semantic evidence: '+scope)


def _producer(kind, root):
    root = Path(root)
    require(root.is_absolute() and root.resolve() == root and not root.is_symlink() and root.is_dir(), 'artifact root')
    schema, seal = PINS[kind]
    manifest = root/'SHA256SUMS'
    require(not manifest.is_symlink() and digest(manifest) == seal, 'artifact seal')
    members = {}
    for line in manifest.read_text().splitlines():
        fields = line.split('  ', 1)
        require(len(fields) == 2 and sha(fields[0]), 'artifact manifest syntax')
        checksum, name = fields
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts and path.parts and str(path) == name and name not in members and name != 'SHA256SUMS', 'artifact manifest member')
        member = root/path
        require(member.resolve() == member and member.is_file() and digest(member) == checksum, 'artifact member identity')
        members[name] = checksum
    require(len(members) == 30 and {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} == set(members)|{'SHA256SUMS'} and not any(p.is_symlink() for p in root.rglob('*')), 'artifact exact closure')
    record = json.loads((root/'build.json').read_text(), object_pairs_hook=pairs)
    require(record.get('schema') == schema and record.get('status') == 'pass' and record.get('executed') is False and record.get('elf_sha256') == members['filesystem.elf'], 'producer schema/scope')
    return record


def validate(data):
    require(isinstance(data, dict) and set(data) == {'format','native_executed','dependency_root','artifacts','inputs','baselines','evidence'}, 'record fields')
    require(data['format'] == FORMAT and data['native_executed'] is False and data['dependency_root'] == declaration(), 'format/native/dependency declaration')
    require(isinstance(data['artifacts'], dict) and set(data['artifacts']) == set(PINS), 'artifact pair')
    require(isinstance(data['baselines'], dict), 'producer baselines')
    mapping(data['inputs'])
    require(all(str(ROOT/name) in data['inputs'] for name in REQUIRED_INPUTS), 'required current consumer input')
    _evidence(data)
    expected_baselines = set()
    resolved = {}
    for kind, artifact in data['artifacts'].items():
        require(isinstance(artifact, dict) and set(artifact) == {'root','manifest_sha256','build_sha256','elf_sha256','changes'}, 'artifact fields')
        require(isinstance(artifact['root'], str) and all(sha(artifact[n]) for n in ('manifest_sha256','build_sha256','elf_sha256')) and isinstance(artifact['changes'], dict), 'artifact field types')
        root = Path(artifact['root'])
        require(artifact['manifest_sha256'] == PINS[kind][1] and digest(root/'build.json') == artifact['build_sha256'] and digest(root/'filesystem.elf') == artifact['elf_sha256'], 'artifact binding')
        producer = _producer(kind, root)
        changes = {}
        resolved[kind] = {}
        require(isinstance(producer.get('inputs'), dict) and producer['inputs'], 'producer input closure')
        for name, before in producer['inputs'].items():
            require(Path(name).is_absolute() and sha(before), 'producer input shape')
            path = dependency_input(name, before)
            current_source(path)
            require(path.is_file(), 'producer input unavailable: '+name)
            after = digest(path)
            resolved[kind][name] = after
            if after == before:
                continue
            public = relocate(name)
            require(public.is_relative_to(ROOT), 'external producer input changed')
            relative = public.relative_to(ROOT).as_posix()
            require(relative in ALLOWED[kind], 'unreviewed producer input changed: '+relative)
            require(data['inputs'].get(str(public)) == after, 'changed consumer absent from qualification')
            changes[relative] = {'producer':before, 'consumer':after}
            if relative in PRODUCER_EDITS:
                expected_baselines.add(relative)
                baseline = data['baselines'].get(relative)
                require(isinstance(baseline, dict) and set(baseline) == {'path','sha256'} and baseline['sha256'] == before and isinstance(baseline['path'], str) and Path(baseline['path']).is_absolute() and digest(baseline['path']) == before, 'producer baseline identity')
                producer_unchanged(relative, Path(baseline['path']).read_text(), public.read_text())
        require(artifact['changes'] == changes and changes, 'exact changed-consumer set')
        for tool in producer.get('tools', {}).values():
            require(digest(tool['resolved_path']) == tool['sha256'], 'producer tool drift')
    require(set(data['baselines']) == expected_baselines, 'exact producer proof set')
    return resolved


def verify_inputs(kind, root, expected, producer):
    """Return validated current inputs, or False when no record was selected."""
    path, expected_record = os.environ.get(ENV_PATH), os.environ.get(ENV_SHA)
    if path is None and expected_record is None:
        return False
    require(path is not None and expected_record is not None, 'explicit record path and hash required')
    data = load(path, expected_record)
    resolved = validate(data)
    artifact = data['artifacts'][kind]
    require(str(Path(root)) == artifact['root'] and expected == artifact['manifest_sha256'] and digest(Path(root)/'build.json') == artifact['build_sha256'] and producer == json.loads((Path(root)/'build.json').read_text(), object_pairs_hook=pairs), 'selected artifact/copy mismatch')
    return {str(relocate(name)): checksum for name, checksum in resolved[kind].items()}


def write(path, data):
    """Seal a finished host-evidence projection; never runs recorded commands."""
    validate(data)
    path = Path(path)
    require(path.is_absolute() and path.parent.resolve() == path.parent and not path.exists() and not path.is_symlink(), 'new record destination')
    with path.open('x') as stream:
        stream.write(json.dumps(data, indent=2)+'\n')
    return digest(path)
