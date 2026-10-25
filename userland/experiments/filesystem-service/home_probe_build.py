# SPDX-License-Identifier: BSD-2-Clause
"""Rebuild fixed AF09 shell/helper from verified retained inputs; no guest."""
from pathlib import Path
import hashlib
import json
import time

S = Path(__file__).resolve().parent
R = S.parents[1]
CORE = ('fd-client', 'fd-facade', 'fd-routing', 'fd-table', 'fd-write',
        'fd-pipe', 'fd-replace', 'fd-session', 'fd-redirect', 'fd-native', 'fd-context')
UNITS = (*CORE, 'fd-startup', 'fd-fork-frame', 'fd-fork-stage', 'fd-native-trap',
         'fd-startup-native', 'fd-libc', 'fd-libc-bindings', 'fd-shell-entry',
         'fd-fork-native', 'fd-exec', 'fd-exec-native')
FLAGS = ('--no-default-config', '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
         '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes', '-Wmissing-prototypes',
         '-Werror', '-DAEFD_PATH_WIRE', '-DAEFD_DUP2_WIRE', '-DAEFD_WRITE_WIRE')
PROFILE = dict(selection='fs_home_probe_three', provider_attempts=3, utc_min=1791290040,
    utc_max=1791290100, utc_half_open=True, rtc_base='2026-10-06T12:34:00')
DEPENDENCIES = (
    (R / 'build/service-deliveries/filesystem-fork-frame-2026-10-22-v1',
     'ec3697b200ca5a92aeb12c42b0f89a5c9744a6fbd85f8203991fa765763663e8'),
    (R / 'build/session-deliveries/filesystem-abi29-linked-2026-10-21-v2',
     'e559c2ef5a0675c6c243aa3cc517bf5c34fd78ae5ef90a8ca3f3e99b04999081'))
NAMES = tuple(dict.fromkeys([*(u + '.c' for u in UNITS),
    'fd-home-probe-adapter.c', 'fd-home-probe.c', 'fd-command-entry.c',
    'startup-identity-vendor.h', 'native-trap-vendor.h',
    *[p.name for p in sorted(S.glob('fd-*.h'))]]))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def verify(root, digest):
    require(sha(root / 'SHA256SUMS') == digest, 'dependency manifest pin: ' + str(root))
    members = {}
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        p = Path(name)
        require(not p.is_absolute() and '..' not in p.parts and name not in members,
                'dependency member shape')
        member = root / p
        require(not member.is_symlink() and member.resolve().is_relative_to(root.resolve()),
                'dependency member escape: ' + name)
        require(sha(member) == expected, 'dependency member changed: ' + name)
        members[name] = expected
    # The dependency's immutable manifest is the authority for its consumed bytes.
    return dict(path=str(root), manifest_sha256=digest, members=len(members))


def build(work, proc, tools, deadline, record):
    """Return actual artifact paths; the caller owns work and all cleanup."""
    env = proc.clean_env(work)
    folder = work / 'home-probe-native'
    folder.mkdir()
    public = folder / 'public-fork'
    public.mkdir()
    sources = {str(S / name): sha(S / name) for name in NAMES}
    sources[str(Path(__file__))] = sha(Path(__file__))
    record['home_probe_sources'] = sources
    record['home_probe_flags'] = list(FLAGS)
    record['home_probe_profile'] = dict(PROFILE)
    record['home_probe_dependencies'] = [verify(root, pin) for root, pin in DEPENDENCIES]
    bundle = DEPENDENCIES[1][0] / 'bundle'
    record['home_probe_dependencies'].append(verify(bundle,
        '70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942'))
    include = R / 'build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include'
    expected = json.loads((DEPENDENCIES[0][0] / 'dependency.json').read_text())['native_header_pins']
    historical = '/Users/cam/DEV/Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include/'
    if expected and all(name.startswith(historical) for name in expected):
        expected = {str(include / name[len(historical):]): digest for name, digest in expected.items()}
    actual = {str(p): sha(p) for p in sorted(include.rglob('*')) if p.is_file()}
    require(actual and actual == expected, 'retained native header closure')
    record['home_probe_native_headers'] = actual
    for name in ('clang', 'lld', 'nm', 'readelf'):
        require(sha(tools[name]['path']) == tools[name]['sha256'], 'tool pin: ' + name)
    selected_tools = {name: dict(tools[name]) for name in ('clang', 'lld', 'nm', 'readelf')}
    record['home_probe_tools'] = selected_tools

    def run(label, argv):
        remaining = deadline - time.monotonic()
        require(remaining > 0, 'target deadline before ' + label)
        result = proc.run(list(map(str, argv)), cwd=R, env=env, work=work,
                          label=label, timeout=min(180, remaining))
        record.setdefault('rows', []).append(dict(label=label, expected_exit=0, process=result.record,
            stdout=result.stdout.decode(errors='replace')[-7000:], stderr=result.stderr.decode(errors='replace')[-7000:]))
        require(result.returncode == 0 and result.record['complete'] and result.record['cleanup'] == 'complete', label)
        return result

    flags = [*FLAGS, '--target=x86_64-unknown-none', '-ffreestanding', '-fno-builtin',
        '-O2', '-fstack-usage', '-nostdinc', '-isystem', str(include), '-DAEFD_FORK_BINDINGS',
        '-DAEFD_EXEC_BINDINGS', '-I' + str(S)]
    try:
        for unit in (*UNITS, 'fd-home-probe-adapter', 'fd-home-probe', 'fd-command-entry'):
            run('home-target-' + unit, [tools['clang']['path'], *flags, '-c', S / (unit + '.c'),
                '-o', folder / (unit + '.o')])
        recipe_path = bundle / 'recipe.json'
        recipe = json.loads(recipe_path.read_text())
        record['home_probe_recipe_sha256'] = sha(recipe_path)
        selected = {'fork-compile', '_Fork-compile', 'rebind-compile', 'waitpid-compile',
            'wait3-compile', 'wait4-compile', 'memory-compile'}
        chosen = [step for step in recipe['commands'] if step['name'] in selected]
        require(len(chosen) == len(selected) and {step['name'] for step in chosen} == selected,
                'unique retained fork recipes')
        def expand(arg):
            return arg.replace('@bundle', str(bundle)).replace('@output', str(folder))
        for step in chosen:
            require(step['argv'][0] == tools['clang']['path'], 'recipe compiler identity')
            if step['name'] == 'rebind-compile':
                require('-DREBIND_LIBC_REPAIR' in step['argv'] and not any('REBIND_SKIP' in a for a in step['argv']),
                    'retained rebind ordering flags')
            run('home-recipe-' + step['name'], [expand(a) for a in step['argv']])
        def link_inputs(name, excluded):
            steps = [step['argv'] for step in recipe['commands'] if step['name'] == name]
            require(len(steps) == 1, 'unique original link: ' + name)
            return [expand(a) for a in steps[0] if a.endswith(('.o', '.a')) and a not in excluded]
        shell_inputs = link_inputs('parent-link', ('@output/parent-runtime.o', '@output/parent-application.o'))
        helper_inputs = link_inputs('helper-link', ('@output/helper-runtime.o', '@output/helper-application.o', '@output/helper-body.o'))
        shell = folder / 'shell.elf'
        helper = folder / 'helper.elf'
        common = [tools['lld']['path'], '-static', '--no-undefined', '-z', 'noexecstack', '--wrap=main', '--wrap=_exit']
        run('home-complete-shell-link', [*common, *[folder / (u + '.o') for u in UNITS], *shell_inputs, '-o', shell])
        run('home-complete-helper-link', [*common, *[folder / (u + '.o') for u in UNITS if u != 'fd-shell-entry'],
            folder / 'fd-command-entry.o', folder / 'fd-home-probe-adapter.o', folder / 'fd-home-probe.o',
            *[public / name for name in ('fork.o', '_Fork.o', 'rebind.o', 'waitpid.o', 'wait3.o', 'wait4.o')],
            *helper_inputs, '-o', helper])
        artifacts = {}
        for label, path in (('shell', shell), ('helper', helper)):
            undefined = run('home-' + label + '-undefined', [tools['nm']['path'], '--undefined-only', path])
            require({line.split()[-1] for line in undefined.stdout.decode().splitlines()} == {'_DYNAMIC'},
                'unexpected complete imports: ' + label)
            relocs = run('home-' + label + '-relocations', [tools['readelf']['path'], '-r', path])
            require(b'There are no relocations in this file.' in relocs.stdout, 'runtime relocation: ' + label)
            inspected = run('home-' + label + '-elf', [tools['readelf']['path'], '-h', '-l', path])
            require(b'ELF64' in inspected.stdout and b'X86-64' in inspected.stdout and b'TLS' in inspected.stdout,
                'complete ELF/TLS: ' + label)
            require(path.stat().st_size <= 1024 * 1024, 'ordinary process ELF limit: ' + label)
            artifacts[label] = dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)
        frames = []
        for path in sorted(folder.glob('*.su')):
            for line in path.read_text().splitlines():
                parts = line.split('\t')
                require(len(parts) == 3 and parts[2] == 'static', 'nonstatic target frame')
                frames.append(dict(function=parts[0], bytes=int(parts[1])))
        record['home_probe_target'] = dict(artifacts=artifacts, local_frames=frames,
            scope='Actual complete shell/helper links with initialized TLS; native peak, kernel admission and guest execution remain separate.')
        return dict(shell=shell, helper=helper, sources=sources, flags=list(flags),
            dependencies=record['home_probe_dependencies'], artifacts=artifacts, tools=selected_tools, profile=dict(PROFILE))
    finally:
        require(all(sha(path) == digest for path, digest in sources.items()), 'home probe source changed during build')
        require({str(p): sha(p) for p in sorted(include.rglob('*')) if p.is_file()} == expected,
            'native headers changed during build')
        for root, pin in DEPENDENCIES:
            verify(root, pin)
        verify(bundle, '70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942')
        require(all(sha(tool['path']) == tool['sha256'] for tool in selected_tools.values()),
            'home probe tools changed during build')
        record['home_probe_source_verification'] = 'pass'
