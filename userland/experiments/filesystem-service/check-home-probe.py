# SPDX-License-Identifier: BSD-2-Clause
"""Check the guarded AF09 FILE helper, launch count and bounded UTC; no guest or complete target fit."""
from pathlib import Path
import runpy
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
home = runpy.run_path(str(S / 'check-home-wire.py'))
producer = runpy.run_path(str(S / 'home_probe_build.py'))
clock = runpy.run_path(str(S / 'home_probe_clock_checks.py'))
C_SOURCES = tuple(S / (name + '.c') for name in producer['CORE'])
OWNED = tuple(S / name for name in ('fd-home-probe.c', 'fd-home-probe-tests.c',
    'fd-home-probe-adapter.c', 'fd-home-probe-adapter.h', 'home_probe_build.py'))


def check(record, work, proc, tools):
    deadline = time.monotonic() + 300
    require = home['require']
    pins = __import__('json').loads(home['PINS'].read_text())
    for name, tool in pins['tools'].items():
        home['verify'](tool['path'], tool['sha256'])
        tools[name] = tool
    for path, digest in pins['clang_resource_headers'].items():
        home['verify'](path, digest)
        record['sources'][path] = digest
    runtime = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    home['verify'](runtime, '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746')
    record['ubsan'] = dict(path=str(runtime), sha256=home['sha'](runtime))
    env = proc.clean_env(work)

    def run(label, argv, expected=0):
        remaining = deadline - time.monotonic()
        require(remaining > 0, 'host deadline before ' + label)
        child_env = dict(env)
        if str(argv[0]) in [tools[name]['path'] for name in ('rustc', 'rustfmt', 'clippy-driver')]:
            child_env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
        result = proc.run(list(map(str, argv)), cwd=home['R'], env=child_env, work=work,
            label=label, timeout=min(180, remaining))
        record['rows'].append(dict(label=label, expected_exit=expected, process=result.record,
            stdout=result.stdout.decode(errors='replace')[-7000:], stderr=result.stderr.decode(errors='replace')[-7000:]))
        require(result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', label)
        return result

    run('home-probe-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(home['R'] / 'docs/quality/clang-format.yaml'), *[p for p in OWNED if p.suffix in ('.c', '.h')]])
    run('home-probe-rustfmt', [tools['rustfmt']['path'], '--edition=2021', '--check',
        S / 'launch-home-owner.rs', S / 'launch-home-owner-tests.rs'])
    sdk = run('home-probe-host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
    require(bool(sdk), 'host SDK path')
    record['home_probe_host_sdk'] = sdk
    flags = [*producer['FLAGS'], '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
             '-isysroot', sdk, '-DAEFD_HOME_PROBE_HOST_TEST', '-I' + str(S)]
    def compile_host(label, substitutions=None):
        substitutions = substitutions or {}
        units = [*C_SOURCES, S / 'fd-home-probe-adapter.c', S / 'fd-home-probe.c', S / 'fd-home-probe-tests.c']
        binary = work / label
        run(label + '-build', [tools['clang']['path'], *flags,
            *[substitutions.get(p.name, p) for p in units], '-o', binary])
        return binary
    binary = compile_host('home-probe')
    checked = run('home-probe-tests', [binary])
    require(checked.stdout == b'11 real guarded home probe scenarios pass\n', 'eleven guarded helper scenarios')
    record['home_probe_controls'] = []
    controls = [
        ('guard', 'fd-home-probe-adapter.c', 'int64_t result = aefd_native_enter(&c->native);',
         'int64_t result = (c->native.active = 1, 0);', 'HOME_PROBE_GUARD'),
        ('map-alias', 'fd-home-probe-adapter.c', 'if (!valid) {', 'if (0 && !valid) {', 'HOME_PROBE_ALIAS'),
        ('final-close', 'fd-table.c', 'if (result == 0)\n        map->slots[fd] = (struct aefd_binding){0};\n    return result;',
         'if (result == 0)\n        map->slots[fd] = (struct aefd_binding){0};\n    return 0;', 'HOME_PROBE_FINAL_CLOSE'),
        ('attempt-offset', 'fd-home-probe.c', '!r->remote.offset && r->remote.txg',
         'r->remote.txg', 'HOME_PROBE_OFFSET_READ_EOF'),
    ]
    for label, filename, before, after, marker in controls:
        original = (S / filename).read_text()
        require(original.count(before) == 1, 'unique helper control: ' + label)
        changed = work / (label + '.c')
        changed.write_text(original.replace(before, after, 1))
        binary = compile_host('home-probe-' + label, {filename: changed})
        rejected = run('home-probe-' + label + '-reject', [binary], expected=1)
        require(marker.encode() in rejected.stderr, 'named helper semantic control: ' + label)
        record['home_probe_controls'].append(dict(label=label, file=filename, before=before, after=after,
            marker=marker, sha256=home['sha'](changed)))
    boundary = [arg for arg in home['COMMON'] if arg != '-Funsafe-code']
    for selected in (False, True):
        tag = 'three' if selected else 'foundation'
        extra = ['--cfg', 'fs_home_probe_three'] if selected else []
        for compiler in ('rustc', 'clippy-driver'):
            run(tag + '-' + compiler + '-launch-build', [tools[compiler]['path'], *boundary,
                '--cfg', 'fs_home_native', *extra, '--test', S / 'launch-home-owner.rs', '-o', work / (tag + '-' + compiler)])
        checked = run(tag + '-launch-tests', [work / (tag + '-rustc'), '--test-threads=1'])
        require(b'5 passed; 0 failed' in checked.stdout, 'five selected/unselected launch methods')
    original = (S / 'launch-home-owner.rs').read_text()
    before = '|| cfg!(fs_home_probe_three) && home.mutation_attempts != 3'
    require(original.count(before) == 1, 'unique selected count control')
    folder = work / 'launch-omit-three'
    folder.mkdir()
    for filename in ('launch-home-owner-tests.rs', 'home-native-result.rs'):
        shutil.copy2(S / filename, folder / filename)
    (folder / 'launch-home-owner.rs').write_text(original.replace(before, '|| false', 1))
    run('launch-omit-three-build', [tools['rustc']['path'], *boundary, '--cfg', 'fs_home_native',
        '--cfg', 'fs_home_probe_three', '--test', folder / 'launch-home-owner.rs', '-o', folder / 'tests'])
    rejected = run('launch-omit-three-reject', [folder / 'tests', '--exact',
        'tests::fixed_home_probe_requires_three_attempts_only_when_selected', '--nocapture'], expected=101)
    require(b'HOME_PROBE_THREE' in rejected.stderr and b'1 failed' in rejected.stdout, 'named count control')
    clock['check'](record, work, proc, tools, deadline)
    record['home_probe_selection'] = dict(wire='AEFW0001', write_wire=True, path_wire=True,
        dup2_wire=True, cwd_wire=False, libc_file_write=False, provider_attempts=3,
        payload_hex=b'AF09-HOME-WRITE\n'.hex(), marker_hex=b'AF09-HOME-WR\n'.hex())


if __name__ == '__main__':
    sys.exit(home['main'](check_function=check, program='aether-home-probe-check',
        evidence=home['R'] / 'docs/evidence/filesystem-home-prep-2026-10-24/probe', description=__doc__,
        example='python3 -B experiments/filesystem-service/check-home-probe.py',
        scope='Real guarded FILE helper/launch host tests and selected UTC host/target libraries; no guest or complete target fit',
        extra_sources=(SOURCE, *OWNED, *C_SOURCES, *[S / name for name in producer['NAMES']], *clock['EXTRA_SOURCES']),
        limitations='Target shell/helper composition is a separate imported build for guarded inputs. No guest, actual ZFS, native authority or peak fit is tested here.'))
