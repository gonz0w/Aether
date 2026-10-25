# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ private armed fork/child checks and real full-shell link; no native execution."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shlex
import shutil
import struct
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--exec',action='store_true',help='include the explicit immutable exec/readiness provider and actual command entry')
parser.add_argument('--paths',action='store_true',help='select the separate canonical root-path FILE codec/libc binding')
parser.add_argument('--path-probe',action='store_true',help='link the fixed persistent read helper; requires --exec --paths')
parser.add_argument('--dup2',action='store_true',help='select matched16-slot FILE/startup and public dup2; requires --exec --paths')
parser.add_argument('--cwd',action='store_true',help='select AF08 public physical chdir/getcwd; requires --dup2')
options=parser.parse_args()
if options.cwd and not options.dup2:parser.error('--cwd requires --dup2')
if options.dup2 and not (options.exec and options.paths):parser.error('--dup2 requires --exec --paths')
if options.path_probe and not (options.exec and options.paths):
    parser.error('--path-probe requires --exec --paths')
W = Path(tempfile.mkdtemp(prefix='filesystem-fork-stage-', dir=R / 'build'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, digest):
    if sha(root / 'SHA256SUMS') != digest:
        raise ValueError('manifest pin: ' + str(root))
    members = {}
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or name in members:
            raise ValueError('manifest shape')
        if sha(root / p) != expected:
            raise ValueError('member pin: ' + name)
        members[name] = expected
    return members


record = dict(status='incomplete', python=sys.version, host=platform.platform(),
              interpreter=dict(path=sys.executable, sha256=sha(Path(sys.executable))),
              checker_sha256=sha(Path(__file__)), sources={}, rows=[],
              native_executed=False, path_wire=options.paths, path_probe=options.path_probe, dup2_wire=options.dup2, cwd_wire=options.cwd)
shutil.copyfile(Path(__file__), W / 'checker.py')
try:
    predecessor = R / 'build/service-deliveries/filesystem-fork-frame-2026-10-22-v1'
    predecessor_pin = 'ec3697b200ca5a92aeb12c42b0f89a5c9744a6fbd85f8203991fa765763663e8'
    record['predecessor'] = verify(predecessor, predecessor_pin)
    source = W / 'source'
    shutil.copytree(predecessor / 'source', source)
    names = ['fd-protocol.h', 'fd-libc.c', 'fd-fork-stage.h', 'fd-fork-stage.c', 'fd-fork-native.c', 'fd-fork-stage-tests.c', 'fd-libc-bindings.c', 'fd-libc-tests.c', 'fd-shell-elf-tests.zig', 'vendor/native-elf-2026-10-22.zig']
    names += ['fd-client.c','fd-facade.c','fd-facade.h','fd-bindings.h','fd-table.c',
              'fd-replace.c','fd-replace.h','fd-session.c','fd-startup.c','fd-context.c','fd-context.h',
              'fd-fork-frame.c','fd-fork-frame-tests.c','fd-dup2-tests.c']
    if options.exec:
        names += ['fd-exec.c','fd-exec.h','fd-exec-native.c','fd-exec-tests.c','fd-command-entry.c','fd-shell-entry.c']
    if options.cwd:
        names += ['fd-cwd-read-probe.c','fd-cwd-probe-tests.c']
    if options.path_probe:
        names += ['fd-root-read-probe.c','fd-root-read-probe-tests.c','fd-dup2-probe-tests.c']
    for name in names:
        record['sources'][name] = sha(S / name)
        (source / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(S / name, source / name)
    manifest = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
    if sha(manifest) != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d':
        raise ValueError('tool manifest pin')
    pins = json.loads(manifest.read_text())
    tools = {name: pins['tools'][name] for name in
             ['clang', 'clang-format', 'nm', 'readelf', 'lld']}
    tools['objdump'] = dict(path='/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-objdump',
        sha256='57df889beb6133ffd405ffb84795941c068a13a09dba0a40546d3b740666b9b7')
    record['tools'] = tools
    record['resource_headers'] = pins['clang_resource_headers']
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('tool changed')
    for path, digest in record['resource_headers'].items():
        if sha(Path(path)) != digest:
            raise ValueError('resource header changed')
    runtime = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    runtime_pin = '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
    if sha(runtime) != runtime_pin:
        raise ValueError('UBSan runtime pin')
    record['ubsan'] = dict(path=str(runtime), sha256=runtime_pin)
    helper = R / 'experiments/command-runner/process.py'
    if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
        raise ValueError('process helper pin')
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)

    def run(label, argv, expected=0, timeout=60):
        result = proc.run(list(map(str, argv)), cwd=R, env=proc.clean_env(W),
                          work=W, label=label, timeout=timeout)
        record['rows'].append(dict(label=label, expected=expected, process=result.record))
        if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
            raise RuntimeError(label)
        return result

    run('format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(R / 'docs/quality/clang-format.yaml'),
        *[source / name for name in names if name.endswith(('.c', '.h'))]])
    flags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
             '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
             '-Wmissing-prototypes', '-Werror']
    if options.paths:
        flags += ['-DAEFD_PATH_WIRE']
    if options.dup2:
        flags += ['-DAEFD_DUP2_WIRE']
    if options.cwd:
        flags += ['-DAEFD_CWD_WIRE']
    host_flags = flags + ['-fsanitize=undefined', '-fno-sanitize-recover=all']
    core = ['fd-client', 'fd-facade', 'fd-routing', 'fd-table', 'fd-write',
            'fd-pipe', 'fd-replace', 'fd-session', 'fd-redirect', 'fd-native',
            'fd-context', 'fd-startup', 'fd-fork-frame', 'fd-fork-stage']
    if options.dup2:
        run('dup2-build',[tools['clang']['path'],*host_flags,
            source/'fd-client.c',source/'fd-facade.c',source/'fd-table.c',
            source/'fd-replace.c',source/'fd-dup2-tests.c','-o',W/'dup2-tests'])
        checked=run('dup2-tests',[W/'dup2-tests'],timeout=30)
        if checked.stdout != b'26 exact mixed dup2 cases pass\n':raise ValueError('missing dup2 matrix')
        record['dup2_controls']=[]
        for unit,label,old,new in [
            ('fd-client.c','accept-wrong-replace-target','reply.result != args[1]','(reply.result != args[1] && 0)'),
            ('fd-replace.c','keep-replacement-cloexec','struct aefd_binding previous = map->slots[target];\n    value.cloexec = 0;', 'struct aefd_binding previous = map->slots[target];\n    value.cloexec = 1;'),
            ('fd-replace.c','publish-after-unconsumed-close','result < 0 && map->slots[target].kind != AEFD_BIND_EMPTY','0 && result < 0 && map->slots[target].kind != AEFD_BIND_EMPTY'),
        ]:
            original=(source/unit).read_text()
            if original.count(old)!=1:raise ValueError('dup2 control anchor: '+label)
            changed=W/(label+'.c');changed.write_text(original.replace(old,new,1))
            run(label+'-build',[tools['clang']['path'],*host_flags,'-I'+str(source),
                *[changed if u==unit else source/u for u in ['fd-client.c','fd-facade.c','fd-table.c','fd-replace.c']],
                source/'fd-dup2-tests.c','-o',W/label])
            failed=run(label+'-reject',[W/label],expected=-6,timeout=30)
            if b'Assertion failed:' not in failed.stderr:raise ValueError('nonsemantic dup2 denial: '+label)
            record['dup2_controls'].append(dict(label=label,source_sha256=sha(changed)))
    if options.path_probe:
        run('path-probe-body-build',[tools['clang']['path'],*host_flags,
            '-Dmain=aefd_root_read_probe','-Dopen=aefd_probe_open','-Dread=aefd_probe_read',
            *(['-Ddup2=aefd_probe_dup2','-Dfcntl=aefd_probe_fcntl'] if options.dup2 else []),
            '-Dlseek=aefd_probe_seek','-Dclose=aefd_probe_close','-Dwrite=aefd_probe_write',
            '-c',source/'fd-root-read-probe.c','-o',W/'path-probe-host.o'])
        run('path-probe-tests-build',[tools['clang']['path'],*host_flags,
            source/('fd-dup2-probe-tests.c' if options.dup2 else 'fd-root-read-probe-tests.c'),W/'path-probe-host.o','-o',W/'path-probe-tests'])
        checked=run('path-probe-tests',[W/'path-probe-tests'],timeout=30)
        if (b'19 fixed dup2/read probe outcomes pass' if options.dup2 else b'10 fixed root-read probe outcomes pass') not in checked.stdout:
            raise ValueError('missing probe outcomes')
    if options.cwd:
        run('cwd-probe-body-build',[tools['clang']['path'],*host_flags,'-DAEFD_CWD_PROBE_HOST_TEST','-Dmain=aefd_cwd_read_probe',
            '-Dgetcwd=aefd_probe_getcwd','-Dchdir=aefd_probe_chdir','-c',source/'fd-cwd-read-probe.c','-o',W/'cwd-probe.o'])
        run('cwd-probe-build',[tools['clang']['path'],*host_flags,source/'fd-cwd-probe-tests.c',W/'cwd-probe.o','-o',W/'cwd-probe-tests'])
        observed=run('cwd-probe-tests',[W/'cwd-probe-tests'])
        if observed.stdout!=b'10 fixed physical CWD probe outcomes pass\n':raise ValueError('CWD probe outcomes')
    if options.exec:
        run('exec-host-build',[tools['clang']['path'],*host_flags,'-DAEFD_FORK_HOST_TEST','-I'+str(source),
            *[source/(u+'.c') for u in core],source/'fd-fork-native.c',source/'fd-exec.c',source/'fd-exec-tests.c',
            '-o',W/'exec-tests'])
        run('exec-host-tests',[W/'exec-tests',W/'exec-request.bin'])
        record['exec_controls']=[]
        original=(source/'fd-exec.c').read_text()
        for label,old,new in [
            ('ignore-exec-reply-sequence','aefd_word(raw, 1) != sequence','(aefd_word(raw, 1) != sequence && 0)'),
            ('accept-exec-return','result != -11 || !move(io, raw, 32, 0, &budget)',
             '(result != -11 && 0) || !move(io, raw, 32, 0, &budget)'),
        ]:
            if original.count(old)!=1:raise ValueError('exec control anchor: '+label)
            changed=W/(label+'.c')
            changed.write_text(original.replace(old,new,1))
            executable=W/label
            run(label+'-build',[tools['clang']['path'],*host_flags,'-DAEFD_FORK_HOST_TEST','-I'+str(source),
                *[source/(u+'.c') for u in core],source/'fd-fork-native.c',changed,source/'fd-exec-tests.c',
                '-o',executable])
            failed=run(label+'-reject',[executable],expected=-6)
            if b'Assertion failed:' not in failed.stderr:raise ValueError('nonsemantic exec rejection: '+label)
            record['exec_controls'].append(dict(label=label,source_sha256=sha(changed)))
    deps = run('host-headers', [tools['clang']['path'], '-std=c17', '-DAEFD_FORK_HOST_TEST', '-M',
        *[source / (u + '.c') for u in core + ['fd-libc', 'fd-libc-bindings', 'fd-libc-tests', 'fd-fork-stage-tests', 'fd-fork-native'] + (['fd-exec','fd-exec-tests'] if options.exec else [])]])
    headers = set()
    for line in deps.stdout.decode().replace('\\\n', ' ').splitlines():
        headers.update(shlex.split(line.split(':', 1)[1]))
    record['host_headers'] = {name: sha(Path(name)) for name in sorted(headers)}

    def build(label, implementation, native_implementation=None):
        run(label + '-build', [tools['clang']['path'], *host_flags, '-DAEFD_FORK_HOST_TEST',
            *[source / (u + '.c') for u in core if u != 'fd-fork-stage'], native_implementation or source / 'fd-fork-native.c',
            implementation, source / 'fd-fork-stage-tests.c',
            '-I' + str(source), '-o', W / label])

    build('stage', source / 'fd-fork-stage.c')
    tests = run('tests', [W / 'stage'], timeout=30)
    if not tests.stdout.endswith(b' armed fork/child cases pass\n'):
        raise ValueError('stage outcome')
    record['cases'] = int(tests.stdout.split()[0])
    if record['cases'] < 990:
        raise ValueError('missing stage cases')
    run('frame-build', [tools['clang']['path'], *host_flags, source / 'fd-native.c',
        source / 'fd-fork-frame.c', source / 'fd-fork-frame-tests.c', '-o', W / 'frames'])
    frames = run('frame-tests', [W / 'frames'], timeout=30)
    if frames.stdout != b'5847 fork-frame cases pass\n':
        raise ValueError('frame regression')
    run('libc-bindings', [tools['clang']['path'], *host_flags, '-DAEFD_LIBC_HOST_TEST',
        '-c', source / 'fd-libc-bindings.c', '-o', W / 'libc-bindings.o'])
    run('libc-build', [tools['clang']['path'], *host_flags,
        *[source / (u + '.c') for u in core if u not in ['fd-fork-stage', 'fd-fork-frame']],
        source / 'fd-libc.c', source / 'fd-libc-tests.c', W / 'libc-bindings.o', '-o', W / 'libc'])
    libc = run('libc-tests', [W / 'libc'], timeout=30)
    if libc.stdout != (b'104 actual libc binding host scenarios pass\n' if options.cwd else b'84 actual libc binding host scenarios pass\n' if options.dup2 else b'78 actual libc binding host scenarios pass\n'):
        raise ValueError('default libc regression')
    if options.dup2:
        original=(source/'fd-libc-bindings.c').read_text()
        old='int64_t result = aefd_context_replace(&shell.context, from, to);\n    if (shell.phase == 2 && !shell.context.client.live)'
        if original.count(old)!=1:raise ValueError('public dup2 control anchor')
        changed=W/'omit-public-dup2-stop.c';changed.write_text(original.replace(old,old.replace('if (shell.phase','if (0 && shell.phase'),1))
        run('public-dup2-stop-build',[tools['clang']['path'],*host_flags,'-DAEFD_LIBC_HOST_TEST','-I'+str(source),'-c',changed,'-o',W/'public-stop.o'])
        run('public-dup2-stop-link',[tools['clang']['path'],*host_flags,
            *[source/(u+'.c') for u in core if u not in ['fd-fork-stage','fd-fork-frame']],
            source/'fd-libc.c',source/'fd-libc-tests.c',W/'public-stop.o','-o',W/'public-stop'])
        failed=run('public-dup2-stop-reject',[W/'public-stop'],expected=-6,timeout=30)
        if b'Assertion failed:' not in failed.stderr:raise ValueError('nonsemantic public stop denial')
        record['dup2_controls'].append(dict(label='public-dup2-stop',source_sha256=sha(changed)))
    run('tls-libc-bindings', [tools['clang']['path'], *host_flags, '-DAEFD_LIBC_HOST_TEST',
        '-DAEFD_FORK_BINDINGS', '-c', source / 'fd-libc-bindings.c', '-o', W / 'tls-libc-bindings.o'])
    run('tls-libc-build', [tools['clang']['path'], *host_flags,
        '-DAEFD_FORK_HOST_TEST', '-DAEFD_FORK_BINDINGS',
        *[source / (u + '.c') for u in core], source / 'fd-fork-native.c',
        source / 'fd-libc.c', source / 'fd-libc-tests.c', W / 'tls-libc-bindings.o', '-o', W / 'tls-libc'])
    tls_libc = run('tls-libc-tests', [W / 'tls-libc'], timeout=30)
    if tls_libc.stdout != (b'104 actual libc binding host scenarios pass\n' if options.cwd else b'84 actual libc binding host scenarios pass\n' if options.dup2 else b'78 actual libc binding host scenarios pass\n'):
        raise ValueError('opt-in TLS startup/libc regression')
    original = (source / 'fd-fork-stage.c').read_text()
    controls = {
        'omit-child-quarantine': ('b->context.state = 4;\n    f->status = -5;', 'b->context.state = 1;\n    f->status = -5;'),
        'accept-unrebound-child': ('!rebind(rebind_context, f->parent, grants)', '(rebind(rebind_context, f->parent, grants) && 0)'),
        'omit-child-correspondence': ('if (!aefd_fork_child_match(', 'identity = (struct aether_fs_session_identity){2, 1, 1}; if (0 && !aefd_fork_child_match('),
        'lose-child-pointer-rebuild': ('if (aefd_context_init(', 'if (0 && aefd_context_init('),
        'omit-parent-unknown-retirement': ('aefd_client_abort(&f->boot.context.client);', '/* omitted abort */'),
        'omit-child-guard-transfer': ('b->context.native.active = 1;', 'b->context.native.active = 0;'),
        'omit-child-close': ('io.close(io.context);', '((void)io, (struct aefd_close_result){0, 0});'),
    }
    record['controls'] = []
    for label, (old, new) in controls.items():
        if original.count(old) != 1:
            raise ValueError('control target: ' + label)
        mutant = W / (label + '.c')
        mutant.write_text(original.replace(old, new, 1))
        build(label, mutant)
        failed = run(label + '-test', [W / label], expected=-6, timeout=30)
        if b'Assertion failed:' not in failed.stderr:
            raise ValueError('nonsemantic rejection: ' + label)
        record['controls'].append(dict(label=label, sha256=sha(mutant)))
    native_original = (source / 'fd-fork-native.c').read_text()
    for label, old, new in [
        ('omit-initial-tls-check', 'if (!aefd_fork_tls_valid())', 'if (0 && !aefd_fork_tls_valid())'),
        ('omit-child-tls-check', 'return aefd_fork_tls_valid() &&', 'return')]:
        if native_original.count(old) != 1:
            raise ValueError('TLS control target: ' + label)
        mutant = W / (label + '.c')
        mutant.write_text(native_original.replace(old, new, 1))
        build(label, source / 'fd-fork-stage.c', mutant)
        failed = run(label + '-test', [W / label], expected=-6, timeout=30)
        if b'Assertion failed:' not in failed.stderr:
            raise ValueError('nonsemantic TLS rejection: ' + label)
        record['controls'].append(dict(label=label, sha256=sha(mutant)))
    include = R / 'build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include'
    record['native_headers'] = {str(p): sha(p) for p in sorted(include.rglob('*')) if p.is_file()}
    expected_headers=json.loads((predecessor / 'dependency.json').read_text())['native_header_pins']
    historical='/Users/cam/DEV/Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include/'
    if expected_headers and all(name.startswith(historical) for name in expected_headers):
        expected_headers={str(include/name[len(historical):]):digest for name,digest in expected_headers.items()}
    if record['native_headers'] != expected_headers:
        raise ValueError('native header closure')
    native = W / 'native'
    native.mkdir()
    units = core + ['fd-native-trap', 'fd-startup-native', 'fd-libc', 'fd-libc-bindings', 'fd-shell-entry', 'fd-fork-native']
    if options.exec:
        units += ['fd-exec','fd-exec-native']
    for unit in units:
        run('native-' + unit, [tools['clang']['path'], *flags,
            '--target=x86_64-unknown-none', '-ffreestanding', '-fno-builtin',
            '-O2', '-fstack-usage', '-nostdinc', '-isystem', include,
            '-DAEFD_FORK_BINDINGS', *(['-DAEFD_EXEC_BINDINGS'] if options.exec else []), '-I' + str(source), '-c', source / (unit + '.c'),
            '-o', native / (unit + '.o')])
    run('native-link', [tools['lld']['path'], '-r',
        *[native / (u + '.o') for u in units], '-o', native / 'combined.o'])
    elf = run('native-elf', [tools['readelf']['path'], '-h', '-S', '-s', native / 'combined.o'])
    if b'ELF64' not in elf.stdout or b'X86-64' not in elf.stdout:
        raise ValueError('target object')
    assembly = run('native-fork-disassembly', [tools['objdump']['path'], '-dr', native / 'fd-fork-native.o'])
    if b'$0x23003' not in assembly.stdout or b'int\t$0x81' not in assembly.stdout:
        raise ValueError('missing actual park trap')
    symbols = run('native-imports', [tools['nm']['path'], '--undefined-only', native / 'combined.o'])
    record['native_imports'] = symbols.stdout.decode().splitlines()
    if {line.split()[-1] for line in record['native_imports']} != ({
            '__errno_location', '__real__exit', '__real_main', 'copy_rebind',
            'getauxval', 'memcpy', 'memmove', 'memset', 'memcmp'} | ({'strnlen'} if options.exec else set()) | ({'malloc'} if options.cwd else set())):
        raise ValueError('unexpected relocatable imports/allocator')

    frames = []
    for path in native.glob('*.su'):
        for line in path.read_text().splitlines():
            parts = line.split('\t')
            if len(parts) != 3 or parts[2] != 'static':
                raise ValueError('nonstatic frame')
            frames.append(dict(function=parts[0], bytes=int(parts[1])))
    if not frames:
        raise ValueError('missing stack evidence')
    record['static_frames'] = frames
    bss = run('native-bss', [tools['nm']['path'], '--print-size', native / 'fd-libc-bindings.o'])
    own = [line for line in bss.stdout.decode().splitlines() if line.split()[-1] == 'fork_shell']
    if len(own) != 1 or own[0].split()[2] != 'b':
        raise ValueError('missing single boot aggregate')
    record['binding_bss_bytes'] = int(own[0].split()[1], 16)
    if record['binding_bss_bytes'] != 5040:
        raise ValueError('unexpected aggregate size')
    run('default-native-bindings', [tools['clang']['path'], *flags,
        '--target=x86_64-unknown-none', '-ffreestanding', '-fno-builtin',
        '-O2', '-nostdinc', '-isystem', include, '-I' + str(source),
        '-c', source / 'fd-libc-bindings.c', '-o', native / 'default-bindings.o'])
    old_bss = run('default-binding-size', [tools['nm']['path'], '--print-size', native / 'default-bindings.o'])
    default = [line for line in old_bss.stdout.decode().splitlines() if line.split()[-1] == 'shell']
    if len(default) != 1 or int(default[0].split()[1], 16) != 4952 or b'fork_shell' in old_bss.stdout:
        raise ValueError('default binding ABI/layout changed')
    record['default_binding_bss_bytes'] = 4952
    linked = R / 'build/session-deliveries/filesystem-abi29-linked-2026-10-21-v2'
    record['linked_input'] = verify(linked, 'e559c2ef5a0675c6c243aa3cc517bf5c34fd78ae5ef90a8ca3f3e99b04999081')
    bundle = linked / 'bundle'
    record['linked_bundle'] = verify(bundle, '70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942')
    recipe = json.loads((bundle / 'recipe.json').read_text())
    def expand(arg):
        return arg.replace('@bundle', str(bundle)).replace('@output', str(W))
    (W / 'public-fork').mkdir()
    selected = {'fork-compile', '_Fork-compile', 'rebind-compile', 'waitpid-compile', 'wait3-compile', 'wait4-compile', 'memory-compile'}
    if options.exec:
        selected.add('serial-session-helper-body-compile')
    for step in recipe['commands']:
        if step['name'] in selected:
            if step['name'] == 'rebind-compile' and (
                    '-DREBIND_LIBC_REPAIR' not in step['argv'] or any('REBIND_SKIP' in arg for arg in step['argv'])):
                raise ValueError('pinned rebind ordering flags')
            run('shell-' + step['name'], [expand(arg) for arg in step['argv']])
    rebind_asm = run('pinned-rebind-disassembly', [tools['objdump']['path'], '-dr', W / 'public-fork/rebind.o'])
    if b'$0x100da' in rebind_asm.stdout:
        raise ValueError('duplicate child TID repair')
    old_link = next(s['argv'] for s in recipe['commands'] if s['name'] == 'parent-link')
    inputs = [expand(arg) for arg in old_link if arg.endswith(('.o', '.a')) and arg not in ('@output/parent-runtime.o', '@output/parent-application.o')]
    run('complete-shell-link', [tools['lld']['path'], '-static', '--no-undefined', '-z', 'noexecstack',
        '--wrap=main', '--wrap=_exit', *[native / (u + '.o') for u in units], *inputs, '-o', W / 'shell.elf'])
    if options.exec:
        run('command-entry-build',[tools['clang']['path'],*flags,'--target=x86_64-unknown-none',
            '-ffreestanding','-fno-builtin','-O2','-fstack-usage','-nostdinc','-isystem',include,
            '-DAEFD_FORK_BINDINGS','-I'+str(source),'-c',source/'fd-command-entry.c','-o',native/'fd-command-entry.o'])
        helper_inputs=[expand(arg) for arg in next(c['argv'] for c in recipe['commands']
            if c['name']=='helper-link') if arg.endswith(('.o','.a'))
            and arg not in ('@output/helper-runtime.o','@output/helper-application.o')]
        if options.path_probe:
            run('root-read-probe-native',[tools['clang']['path'],*flags,
                '--target=x86_64-unknown-none','-ffreestanding','-fno-builtin','-O2',
                '-fstack-usage','-nostdinc','-isystem',include,'-c',
                source/('fd-cwd-read-probe.c' if options.cwd else 'fd-root-read-probe.c'),'-o',native/'root-read-probe.o'])
            if helper_inputs.count(str(W/'helper-body.o')) != 1:
                raise ValueError('fixed helper body input identity')
            helper_inputs=[str(native/'root-read-probe.o') if v==str(W/'helper-body.o') else v for v in helper_inputs]
        run('complete-helper-link',[tools['lld']['path'],'-static','--no-undefined','-z','noexecstack',
            '--wrap=main','--wrap=_exit',*[native/(u+'.o') for u in units if u!='fd-shell-entry'],
            native/'fd-command-entry.o',*[W/'public-fork'/n for n in ['fork.o','_Fork.o','rebind.o','waitpid.o','wait3.o','wait4.o']],
            *helper_inputs,'-o',W/'helper.elf'])
        helper_symbols=run('helper-undefined',[tools['nm']['path'],'--undefined-only',W/'helper.elf'])
        if {line.split()[-1] for line in helper_symbols.stdout.decode().splitlines()}!={'_DYNAMIC'}:
            raise ValueError('unexpected helper import')
        record['helper_sha256']=sha(W/'helper.elf')
        record['exec_request_sha256']=sha(W/'exec-request.bin')
    full = run('complete-shell-inspect', [tools['readelf']['path'], '-h', '-l', '-s', W / 'shell.elf'])
    undefined = run('complete-shell-unresolved', [tools['nm']['path'], '--undefined-only', W / 'shell.elf'])
    old_undefined = run('baseline-static-symbols', [tools['nm']['path'], '--undefined-only', linked / 'artifacts/parent.elf'])
    relocation = run('complete-shell-relocations', [tools['readelf']['path'], '-r', W / 'shell.elf'])
    dynamic = [line.split() for line in full.stdout.decode().splitlines() if line.split() and line.split()[-1] == '_DYNAMIC']
    if (undefined.stdout != old_undefined.stdout or
            {line.split()[-1] for line in undefined.stdout.decode().splitlines()} != {'_DYNAMIC'} or
            len(dynamic) != 1 or dynamic[0][1:] != ['0000000000000000', '0', 'NOTYPE', 'LOCAL', 'HIDDEN', 'UND', '_DYNAMIC'] or
            b'There are no relocations in this file.' not in relocation.stdout or
            b'EXEC (Executable file)' not in full.stdout or
            any(line.strip().startswith(('INTERP ', 'DYNAMIC ')) for line in full.stdout.decode().splitlines())):
        raise ValueError('unexpected runtime import/dynamic binding')
    record['static_linker_symbol'] = dict(name='_DYNAMIC', value=0, binding='LOCAL HIDDEN UND',
        baseline_identical=True, relocations=False, interpreter=False,
        scope='Existing static lld zero-valued synthetic symbol, not an ignored unresolved runtime reference.')
    required = {'__aether_fork_stage', 'copy_rebind', '__post_Fork', 'fork', '_Fork'}
    defined = {line.split()[-1] for line in full.stdout.decode().splitlines()
               if len(line.split()) >= 8 and line.split()[3] == 'FUNC' and line.split()[6] != 'UND'}
    if not required <= defined:
        raise ValueError('missing actual public fork/stage/rebind symbols')
    raw = (W / 'shell.elf').read_bytes()
    phoff = struct.unpack_from('<Q', raw, 32)[0]
    phsize, phcount = struct.unpack_from('<HH', raw, 54)
    if raw[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<HH', raw, 16) != (2, 62) or phsize != 56:
        raise ValueError('ELF ABI')
    segments = [struct.unpack_from('<IIQQQQQQ', raw, phoff + i * phsize) for i in range(phcount)]
    loads = [h for h in segments if h[0] == 1]
    if not loads or any(h[1] & 3 == 3 or h[5] > h[6] or h[2] + h[5] > len(raw) for h in loads):
        raise ValueError('unsafe load geometry')
    if any(h[0] in (2, 3) for h in segments) or not any(h[0] == 0x6474e551 and not h[1] & 1 for h in segments):
        raise ValueError('dynamic binding/executable stack')
    pages = {page for h in loads for page in range(h[3] // 4096, (h[3] + h[6] + 4095) // 4096)}
    record['elf_geometry'] = dict(load_pages=len(pages), load_segments=len(loads), nx_stack=True, writable_executable=False,
        scope='Static PT_LOAD union only; excludes native loader/TLS/stack/heap/channel/peak fit and authority.')
    record['complete_shell_link'] = dict(status='linked', sha256=sha(W / 'shell.elf'),
        bytes=(W / 'shell.elf').stat().st_size, target_units=len(units),
        scope='Actual pinned dash32/CRT/libc/public-fork/copy_rebind plus new stage. Build-only; no matching owner/native execution/whole fit.')
    tls = [h for h in segments if h[0] == 7]
    if len(tls) != 1 or tls[0][1] != 4 or tls[0][5:7] != (4, 4) or raw[tls[0][2]:tls[0][2] + 4] != b'sses':
        raise ValueError('missing actual initialized TLS')
    tls_symbols = [line.split() for line in full.stdout.decode().splitlines()
                   if line.split() and line.split()[-1] == 'fork_tls']
    if len(tls_symbols) != 1 or tls_symbols[0][2:4] != ['4', 'TLS']:
        raise ValueError('missing real TLS symbol')
    if b'%fs:' not in assembly.stdout:
        raise ValueError('missing native TLS access')
    zig = Path('/opt/homebrew/Cellar/zig/0.16.0_1/bin/zig')
    zig_pin = '71cc3995a7586753ebf82c66dfb8bef43df446517550678781834586a960f8c9'
    parser = source / 'vendor/native-elf-2026-10-22.zig'
    parser_pin = 'e3a2b1133af03dc3d835f0cc0f9a4bd0f8911d33e4c05edbfad05f8da696ee67'
    if sha(zig) != zig_pin or sha(parser) != parser_pin:
        raise ValueError('Zig/parser pin')
    stage81 = R / 'build/service-deliveries/filesystem-fork-stage-2026-10-22-v1'
    verify(stage81, '7923584cb093e2c459ae45468ca1021dd92054e771d2de569ebcee15b3c143fe')
    shutil.copyfile(stage81 / 'artifacts/shell.elf', W / 'old-shell.elf')
    shutil.copyfile(parser, W / 'native_elf.zig')
    shutil.copyfile(source / 'fd-shell-elf-tests.zig', W / 'parser-tests.zig')
    run('parser-test-format', [zig, 'fmt', '--check', W / 'parser-tests.zig'])
    parsed = run('aether-elf-parser', [zig, 'test', W / 'parser-tests.zig',
        '--cache-dir', W / 'zig-cache', '--global-cache-dir', W / 'zig-global-cache'], timeout=60)
    if b'actual full shell with initialized TLS accepted under unchanged defaults' not in parsed.stderr or b'All ' not in parsed.stderr:
        raise ValueError('missing actual parser positive')
    record['aether_parser'] = dict(status='pass', source_sha256=parser_pin,
        zig=dict(path=str(zig), sha256=zig_pin), default_limits=True,
        old_stage81_rejected=True, malformed_tls_wx_rejected=True,
        pages_with_main_stack=len(pages) + 16,
        scope='Actual unchanged kernel ELF parser host execution, not native loader execution or whole fit.')
    if options.exec:
        # Same actual parser and malformed-image oracles, now over the image
        # selected by c003; a link alone does not establish loader admission.
        helper_tests=W/'helper-parser-tests.zig'
        helper_tests.write_text((W/'parser-tests.zig').read_text().replace('@embedFile("shell.elf")','@embedFile("helper.elf")'))
        checked=run('helper-aether-elf-parser',[zig,'test',helper_tests,
            '--cache-dir',W/'zig-cache','--global-cache-dir',W/'zig-global-cache'])
        if b'All ' not in checked.stderr:
            raise ValueError('missing actual helper parser positive')
        record['helper_parser']='pass; actual initialized TLS plus malformed TLS/WX/old-stage denials'
    record['tls'] = dict(filesz=4, memsz=4, template_hex='73736573',
        symbol='fork_tls', native_fs_access=True, initial_and_child_validation=True)
    verify(linked, 'e559c2ef5a0675c6c243aa3cc517bf5c34fd78ae5ef90a8ca3f3e99b04999081')
    verify(bundle, '70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942')
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source changed')
    for name, digest in record['host_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('host header changed')
    verify(predecessor, predecessor_pin)
    if sha(Path(__file__)) != record['checker_sha256']:
        raise ValueError('checker changed during qualification')
    record['status'] = 'pass'
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(record['status'], W)
