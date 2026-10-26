# SPDX-License-Identifier: BSD-2-Clause
"""Explicit AF09 engine source/association validation and offline composition."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import sys
import tempfile
import time

from deps import ROOT
from fs_metadata_launch import closure

SOURCE = ROOT / 'userland/experiments/filesystem-service'
SCHEMA = 'aether-fs-home-launch-v1'
PROFILE = tuple('fs_' + name for name in (
    'namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime', 'activation',
    'names', 'directories', 'metadata', 'directory_contexts', 'home', 'home_wire',
    'home_native', 'home_activation', 'home_probe_three'))
LIMITS = dict(mutations=9, requests=96, engine_pages=8192, writer_seconds=60,
              writer_ticks=6000, reader_seconds=30, reader_ticks=3000)
REQUIRED = {
    'main': 'launch-home-owner.o',
    'aether_fs_home_launch_serve': 'launch-home-owner.o',
    'aether_fs_home_engine_run': 'home-engine.o',
    'aether_fs_home_engine_import': 'home-import.o',
    **{name: 'home-engine-linked.o' for name in (
        'aether_fs_home_run', 'spa_import', 'spa_export', 'aether_zpl_mkdir',
        'aether_zpl_create', 'aether_zpl_write', 'aether_zpl_getattr', 'aether_zpl_context')},
}
PARTIAL = {
    'aether_fs_home_run': 'filesystem-home.o',
    **{name: 'home-provider.o' for name in (
        'aether_zpl_mkdir', 'aether_zpl_create', 'aether_zpl_write',
        'aether_zpl_getattr', 'aether_zpl_context')},
    'aether_pool_label_config': 'pool-home-label.o',
}
FORBIDDEN = {
    'aether_fs_service_run', 'aether_fs_namespace_run', 'aether_fs_mixed_run',
    'aether_fs_metadata_run', 'aether_fs_directories_run', 'aether_fs_activation_run',
    'aether_fs_engine_run', 'aether_fs_engine_import', 'aether_fs_launch_serve',
    'aether_fs_owner_probe', 'aether_pool_namespace_write', 'aether_spa_import_probe',
}
LINK_DENIALS = frozenset((
    'undefined symbol: aether_volume_bind',
    'duplicate symbol: __aether_io',
    'undefined symbol: aether_runtime_init'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate AF09 JSON field: ' + str(key))
        result[key] = value
    return result


def read_json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError('AF09 JSON input path/size')
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def verify_inputs(inputs, generated=None):
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError('AF09 missing input map')
    generated = generated or {}
    for name, expected in inputs.items():
        path = Path(name)
        if not path.is_absolute() or not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('AF09 input identity shape')
        if path.is_file():
            if digest(path) != expected:
                raise ValueError('AF09 input changed: ' + name)
        elif generated.get(name) != expected:
            raise ValueError('AF09 input unavailable; not a known generated source: ' + name)
    return dict(inputs)


def generated_sources(report):
    recipes = report.get('home_c_source_recipes', [])
    if not recipes:
        return {}
    selector = SOURCE / 'home_native_source.py'
    if report.get('sources', {}).get(str(selector)) != digest(selector):
        raise ValueError('AF09 C selector source changed')
    generator = runpy.run_path(str(selector))
    work = Path(report.get('work', ''))
    if (work.parent != ROOT / 'userland/build' or not work.name.startswith('filesystem-home-')
            or len(recipes) != 2):
        raise ValueError('AF09 generated-source work identity')
    result = {}
    for row in recipes:
        original = Path(row['original'])
        if not original.is_relative_to(ROOT):
            raise ValueError('AF09 original C outside repository')
        key = original.relative_to(ROOT).as_posix()
        if row['sha256'] != generator['ORIGINALS'].get(key):
            raise ValueError('AF09 original C pin')
        body, edits = generator['render'](original)
        wanted_edits = [dict(old=old, new=new) for old, new in edits]
        output = work / 'home-c' / ('home-' + original.name)
        checksum = hashlib.sha256(body.encode()).hexdigest()
        if (row['output'] != str(output) or row['output_sha256'] != checksum
                or row['edits'] != wanted_edits or str(output) in result):
            raise ValueError('AF09 generated C recipe/identity')
        result[str(output)] = checksum
    return result


def checked_receipt(path, role):
    schemas = dict(producer='aether-home-native-evidence-v1',
                   probe='aether-home-probe-evidence-v1',
                   owner='aether-home-owner-evidence-v1')
    if role not in schemas:
        raise ValueError('AF09 unknown receipt role')
    report = read_json(path)
    if (report.get('schema') != schemas[role] or report.get('status') != 'pass'
            or report.get('native_executed') is not False
            or report.get('final_input_verification') != 'pass'
            or report.get('cleanup') != 'complete' or not report.get('rows')):
        raise ValueError('AF09 receipt status/profile/cleanup')
    for row in report['rows']:
        process = row.get('process', {})
        expected = row.get('expected_exit', 0)
        if (process.get('exit') != expected or process.get('complete') is not True
                or process.get('cleanup') != 'complete'):
            raise ValueError('AF09 receipt incomplete child')
    if role == 'producer' and (len(report['rows']) < 156
            or len(report.get('policy_controls', [])) != 4
            or len(report.get('home_entry_controls', [])) != 3
            or len(report.get('controls', [])) != 1):
        raise ValueError('AF09 producer missing required coverage')
    if role == 'probe' and (len(report.get('home_probe_controls', [])) != 4
            or report.get('home_probe_selection', {}).get('provider_attempts') != 3):
        raise ValueError('AF09 helper missing fixed workload coverage')
    if role == 'probe':
        selection = dict(wire='AEFW0001', write_wire=True, path_wire=True, dup2_wire=True,
            cwd_wire=False, libc_file_write=False, provider_attempts=3,
            payload_hex=b'AF09-HOME-WRITE\n'.hex(), marker_hex=b'AF09-HOME-WR\n'.hex())
        clock = report.get('home_probe_clock', {})
        expected_clock = dict(selection='fs_home_probe_three', utc_min=1791290040,
            utc_max=1791290100, half_open=True, expected_red=False,
            production_counter=False, native_executed=False)
        if (report.get('home_probe_selection') != selection
                or any(clock.get(k) != v for k, v in expected_clock.items())
                or len(clock.get('methods', [])) != 2
                or report.get('home_probe_clock_final_input_verification') != 'pass'):
            raise ValueError('AF09 helper/count/clock selection changed')
    # Reject changed retained bytes before reconstructing disposed C inputs.
    retained = {name: expected for name, expected in report['sources'].items()
                if Path(name).is_file()}
    if retained:
        verify_inputs(retained)
    generated = generated_sources(report)
    inputs = verify_inputs(report['sources'], generated)
    inputs.update(verify_inputs(report['rust_native_libraries']))
    for tool in report['tools'].values():
        inputs.update(verify_inputs({tool['path']: tool['sha256']}))
    inputs[str(Path(path).absolute())] = digest(path)
    return report, inputs


def strong_symbols(symbols):
    rows = [line.split() for line in symbols.splitlines() if line.split()]
    for name in REQUIRED:
        matches = [row for row in rows if row[-1] == name]
        if len(matches) != 1 or len(matches[0]) != 3 or matches[0][1] != 'T':
            raise ValueError('AF09 required strong definition: ' + name)
    if any(row[-1] in FORBIDDEN for row in rows):
        raise ValueError('AF09 retained old service/launch symbol')


def relink(argv, replacements, output, mapping):
    """Replace only explicitly counted inputs in an original retained recipe."""
    argv = list(map(str, argv))
    if len(argv) < 3 or argv[-2] != '-o' or argv.count('-o') != 1:
        raise ValueError('AF09 recipe output shape')
    if any(argv.count(str(old)) != 1 for old in replacements):
        raise ValueError('AF09 exact single recipe replacement')
    result = []
    for arg in argv[:-2]:
        if arg in replacements:
            result.extend(map(str, replacements[arg]))
        elif arg.startswith('-Map='):
            result.append('-Map=' + str(mapping))
        else:
            result.append(arg)
    return result + ['-o', str(output)]


def check_frames(frames):
    names = {'pool-home-label.su', 'home-provider.su', 'home-engine.su', 'home-import.su'}
    if set(frames) != names:
        raise ValueError('AF09 four C frame units required')
    for text in frames.values():
        rows = [line.split('\t') for line in text.splitlines() if line.strip()]
        if not rows or any(len(row) != 3 or row[2] != 'static'
                           or not row[1].isdigit() or int(row[1]) > 8192 for row in rows):
            raise ValueError('AF09 C local frame bound; not full stack proof')


def prepare_base(stage, command, tools, recovered=False, on_backend=None):
    """Use retained original objects with a checked single-backend overlay."""
    from home_runtime import runtime_archive
    from openzfs_elapsed import prepare
    from openzfs_fs_service import intake as service_intake
    import service_runtime_smoke as runtime
    if type(recovered) is not bool:
        raise ValueError('AF09 explicit reader selection')
    stage.mkdir()
    rows = []
    def tracked(args, log, rejection=None):
        text = command(args, log, rejection=rejection)
        if rejection is None:
            rows.append(dict(argv=list(map(str, args)), exit_code=0))
        return text
    dependency = ROOT / '.deps/native-utc-v3'
    selected = None if recovered else service_intake(
        ROOT / 'userland/build/service-deliveries/filesystem-service-directories-2026-10-20-v1',
        mixed=True, waiting=True, bulk=True, runtime=True, activation=True, names=True, directories=True)
    diagnostic = stage / 'diagnostic'
    diagnostic.mkdir()
    backend = runtime_archive(diagnostic, dependency, tools, tracked)
    if on_backend is not None:
        on_backend(backend, diagnostic)
    port = prepare(stage / 'port', tracked, entropy=True, allocation=True, resources=True,
        arc=True, startup=True, volume=True, volume_utc=True, utc_runtime=dependency / 'runtime',
        volume_pool=True, pool_diagnostics=True, diagnostic_cc=backend['backend_compiler_prefix'],
        volume_pool_namespace=True, volume_namespace_ipc=not recovered,
        volume_pool_zpl_write=not recovered, volume_pool_zpl_recover=recovered,
        volume_recovery_diagnostic=recovered, volume_recovery_writer_60s=recovered,
        volume_fs_service=selected, volume_fs_mixed=True, namespace_wait=not recovered,
        volume_fs_bulk=True, volume_fs_runtime=True, volume_fs_names=True, volume_fs_directories=True)
    (port / 'failure-runtime').mkdir()
    shutil.copyfile(diagnostic / 'failure-runtime/libaether_runtime.a',
                    port / 'failure-runtime/libaether_runtime.a')
    if digest(port / 'failure-runtime/libaether_runtime.a') != backend['archive_sha256']:
        raise ValueError('AF09 copied runtime archive changed')
    if on_backend is not None:
        on_backend(backend, diagnostic, port / 'failure-runtime/libaether_runtime.a')
    sdk = ROOT / '.deps/native-current/sdk'
    cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
        '--sysroot=' + str(sdk / 'empty-root'), '-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall',
        '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin', '-fstack-protector-strong',
        '-nostdinc', '-isystem', str(sdk / 'stage/usr/include'), '-I', str(dependency / 'runtime')]
    composition = runtime.compose_engine(port, tracked, cc, tools, True, 'pool-import',
        volume=True, utc=True, runtime=dependency, pool=True, diagnostics=True, pool_namespace=True,
        pool_zpl_write=not recovered, pool_zpl_recover=recovered, fs_service=not recovered,
        fs_service_mixed=True, fs_service_wait=not recovered, fs_service_bulk=True,
        fs_service_runtime=True, fs_service_activation=not recovered, fs_service_names=True,
        fs_service_directories=True)
    return dict(commands=rows, composition=composition, old_service=selected, backend=backend,
                case='normal', recovered=recovered, recovery_empty=False, output=str(stage))


def bind_runtime(backend, owned, retained, generated, artifact_root=None, copied=None):
    """Keep the exact runtime inputs alive through the final consuming link."""
    for name, expected in backend['inputs'].items():
        target = generated if Path(name).is_relative_to(owned) else retained
        if name in target and target[name] != expected:
            raise ValueError('AF09 conflicting runtime input identity')
        target[name] = expected
    verify_inputs(backend['inputs'])
    artifacts = {}
    if artifact_root is not None:
        artifacts = {
            str(artifact_root / 'failure-runtime-build/original-backend.o'): backend['original_backend_sha256'],
            str(artifact_root / 'failure-runtime-build/backend.o'): backend['selected_backend_sha256'],
            str(artifact_root / 'failure-runtime/libaether_runtime.a'): backend['archive_sha256']}
    if copied is not None:
        artifacts[str(copied)] = backend['archive_sha256']
    verify_inputs(artifacts or backend['inputs'])
    for name, expected in artifacts.items():
        if name in generated and generated[name] != expected:
            raise ValueError('AF09 conflicting runtime artifact identity')
        generated[name] = expected


def command_arguments(argv, tools):
    """Resolve only named retained tools; a recipe cannot select another Rust."""
    args = list(map(str, argv))
    if not args:
        raise ValueError('AF09 empty compiler command')
    if args[0] == 'rustc':
        if len(args) > 1 and args[1].startswith('+'):
            if args[1] != '+1.98.0':
                raise ValueError('AF09 unpinned Rust recipe')
            del args[1]
        args[0] = tools['rustc']['path']
    elif args[0] == 'zig':
        args[0] = tools['zig']['path']
    if not Path(args[0]).is_absolute():
        raise ValueError('AF09 compiler executable must be absolute')
    return args


def compose(base, preparation, artifacts, work, destination, command, result):
    from fs_launch import labels, origins, recipe
    import openzfs_fs_metadata_service as metadata
    port = base / 'port'
    generated = work / 'home-c'
    generated.mkdir()
    generator = runpy.run_path(str(SOURCE / 'home_native_source.py'))
    result['home_c_source_recipes'] = generator['generate'](generated)
    (work / 'namespace-home-label.inc').write_text(labels((metadata.VOLUME / 'namespace-label.inc').read_text()))
    (work / 'pool-home-label.c').write_text(metadata.replace((metadata.VOLUME / 'pool-label.c').read_text(),
        '#include "namespace-label.inc"', '#include "namespace-home-label.inc"'))
    cc = recipe(preparation, 'zpl-mutation.o')
    cc = cc[:cc.index('-c')]
    command(cc + ['-std=c17', '-fstack-usage', '-c', metadata.VOLUME / 'zpl-context.c', '-o', work / 'home-provider.o'], work / 'provider.log')
    label_cc = recipe(preparation, 'pool-label.o')
    label_cc = label_cc[:label_cc.index('-c')]
    command(label_cc + ['-std=c17', '-I' + str(work), '-fstack-usage', '-c', work / 'pool-home-label.c',
                       '-o', work / 'pool-home-label.o'], work / 'label.log')
    startup = recipe(preparation, 'engine-startup.o')
    includes = ['-std=c17', '-I' + str(SOURCE), '-I' + str(metadata.VOLUME),
                '-I' + str(ROOT / 'user/storage/service-runtime')]
    command(startup[:startup.index('-c')] + includes + ['-fstack-usage', '-c',
        generated / 'home-filesystem-engine.c', '-o', work / 'home-engine.o'], work / 'startup.log')
    command(label_cc + includes + ['-fstack-usage', '-c', generated / 'home-filesystem-import.c',
        '-o', work / 'home-import.o'], work / 'import.log')
    partial = relink(recipe(preparation, 'selected-libzpool.o'), {
        preparation['old_service']['object']: [artifacts['service']],
        str(port / 'zpl-mutation.o'): [work / 'home-provider.o'],
        str(port / 'pool-label.o'): [work / 'pool-home-label.o']},
        work / 'home-libzpool.o', work / 'partial.map')
    command(partial, work / 'partial.log')
    result['partial_origins'] = origins((work / 'partial.map').read_text(), PARTIAL)
    command(relink(recipe(preparation, 'selected-engine.o'), {
        str(port / 'selected-libzpool.o'): [work / 'home-libzpool.o']},
        work / 'home-engine-linked.o', work / 'engine.map'), work / 'engine.log')
    final = relink(recipe(preparation, 'engine.elf'), {
        str(port / 'engine-startup.o'): [artifacts['launch'], work / 'home-engine.o', work / 'home-import.o'],
        str(port / 'selected-engine.o'): [work / 'home-engine-linked.o']},
        destination / 'filesystem.elf', work / 'launch.map')
    command(final, work / 'link.log')
    result['origins'] = origins((work / 'launch.map').read_text(), REQUIRED)
    elf = destination / 'filesystem.elf'
    tools = result['tools']
    strong_symbols(command([tools['nm']['path'], '--defined-only', elf], work / 'symbols.log'))
    imports = command([tools['nm']['path'], '-u', elf], work / 'imports.log')
    if any(line.split()[-1] != '_DYNAMIC' for line in imports.splitlines() if line.strip()):
        raise ValueError('AF09 unresolved engine import')
    if command([tools['readelf']['path'], '-rW', elf], work / 'relocations.log').strip() != 'There are no relocations in this file.':
        raise ValueError('AF09 runtime relocations')
    result['segments'] = command([tools['readelf']['path'], '-lW', elf], work / 'segments.log')
    shutil.copyfile(elf, work / 'filesystem.elf')
    (work / 'image-check.zig').write_text(metadata.replace((port / 'image-check.zig').read_text(),
        '@embedFile("engine.elf")', '@embedFile("filesystem.elf")'))
    result['structural_loader'] = command([tools['zig']['path'], 'run', '--cache-dir', ROOT / '.zig-cache',
        '--global-cache-dir', ROOT / '.zig-cache/global', '-O', 'ReleaseSafe', '--dep', 'native_elf',
        '-Mroot=' + str(work / 'image-check.zig'), '-Mnative_elf=' + str(ROOT / 'kernel/native_elf.zig')], work / 'loader.log').strip()
    result['local_frames'] = {p.name: p.read_text() for p in work.glob('*.su')}
    check_frames(result['local_frames'])
    result['map_sha256'] = digest(work / 'launch.map')


class CleanupTrackedProcess:
    """Keep stop unconfirmed if the owned runner cannot return its receipt."""
    def __init__(self, proc, record):
        self.proc = proc
        self.record = record

    def clean_env(self, work):
        return self.proc.clean_env(work)

    def run(self, *args, **kwargs):
        previous = self.record.get('process_cleanup_unresolved', False)
        self.record['process_cleanup_unresolved'] = True
        result = self.proc.run(*args, **kwargs)
        if result.record.get('cleanup') == 'complete' and not previous:
            self.record.pop('process_cleanup_unresolved')
        return result


def process_cleanup_unresolved(record, primary=None):
    return (record.get('process_cleanup_unresolved', False)
        or getattr(primary, 'process_cleanup_unresolved', False)
        or any('process' in row and row['process'].get('cleanup') != 'complete'
               for key in ('rows', 'commands') for row in record.get(key, [])))


def retain_unresolved(record, paths, primary=None):
    """Carry nested intake retention through the original exception."""
    retained = sorted(set(record.get('retained_paths', [])
        + list(getattr(primary, 'cleanup_retained_paths', []))
        + [str(path) for path in paths if path is not None]))
    record.update(status='failed', process_cleanup_unresolved=True, retained_paths=retained)
    if primary is not None:
        primary.process_cleanup_unresolved = True
        primary.cleanup_retained_paths = retained
    return retained


def validate_record(record):
    wanted = dict(schema=SCHEMA, status='pass', executed=False, native_acceptance=False,
                  protocol='AFSRPC09', service_result_bytes=320, launch_state_bytes=384,
                  root_rights=3, home_rights=15, source_rights=15, provider_attempts=3,
                  utc_min=1791290040, utc_max_exclusive=1791290100,
                  rtc='2026-10-06T12:34:00,clock=vm')
    if (process_cleanup_unresolved(record)
            or any(record.get(key) != value for key, value in wanted.items())
            or record.get('executed') is not False or record.get('native_acceptance') is not False
            or record.get('flags') != list(PROFILE) or record.get('limits') != LIMITS):
        raise ValueError('AF09 engine profile/authority/bounds/coverage')
    for key, expected in (('origins', REQUIRED), ('partial_origins', PARTIAL)):
        rows = record.get(key, {})
        if set(rows) != set(expected) or any(Path(rows[name]).name != origin for name, origin in expected.items()):
            raise ValueError('AF09 engine object origins')
    for row in record.get('rows', []):
        if 'process' in row:
            process = row['process']
            if (process.get('complete') is not True
                    or type(process.get('exit')) is not int
                    or process['exit'] != row.get('expected_exit', 0)):
                raise ValueError('AF09 incomplete or unexpected imported child outcome')
    def checked_command(row):
        if row.get('status') != 'pass' or type(row.get('exit_code')) is not int:
            return False
        if 'process' in row and row['process'].get('complete') is not True:
            return False
        marker = row.get('expected_rejection')
        if marker is None:
            return row['exit_code'] == 0
        return (isinstance(marker, str) and marker in LINK_DENIALS and row['exit_code'] == 1
                and row.get('rejection_verified') is True)
    denials = [row.get('expected_rejection') for row in record.get('commands', [])
               if row.get('expected_rejection') is not None]
    if (not record.get('inputs') or not record.get('commands')
            or any(not checked_command(row) for row in record['commands'])
            or len(denials) != len(LINK_DENIALS) or set(denials) != LINK_DENIALS
            or not record.get('structural_loader', '').startswith('ELF structural pages=')):
        raise ValueError('AF09 missing successful consumed closure')
    for key in ('qualification_sha256', 'probe_qualification_sha256', 'service_object_sha256', 'elf_sha256'):
        if not isinstance(record.get(key), str) or not re.fullmatch('[0-9a-f]{64}', record[key]):
            raise ValueError('AF09 malformed artifact/qualification identity')
    if type(record.get('elf_bytes')) is not int or not 0 < record['elf_bytes'] <= 8 * 1024 * 1024:
        raise ValueError('AF09 engine ELF extent')


def intake(directory, seal):
    root, members = closure(directory, seal)
    record = read_json(root / 'build.json')
    validate_record(record)
    if (members.get('filesystem.elf') != record['elf_sha256']
            or (root / 'filesystem.elf').stat().st_size != record['elf_bytes']):
        raise ValueError('AF09 actual engine artifact correspondence')
    needed = {'SOURCE.md', 'preparation.json', 'notices/LICENSE',
              'notices/openzfs/LICENSE', 'notices/openzfs/COPYRIGHT',
              'notices/openzfs/NOTICE', 'notices/COPYRIGHT.musl'}
    if not needed <= members.keys():
        raise ValueError('AF09 missing provenance/notices')
    verify_inputs(record['inputs'])
    return dict(schema='aether-fs-home-launch-result-v1', protocol='AFSRPC09',
                manifest_sha256=seal, elf=str(root / 'filesystem.elf'),
                elf_sha256=members['filesystem.elf'], executed=False,
                native_acceptance=False, members=len(members))


def build(destination, qualification, probe_qualification):
    """Compose an explicit dependency; never launch the native image."""
    from fs_launch import validate_destination
    from deps import verify
    destination = validate_destination(destination)
    if not destination.name.startswith('fs-launch-af09-'):
        raise ValueError('AF09 requires an unused .deps/fs-launch-af09-* destination')
    producer, inputs = checked_receipt(qualification, 'producer')
    probe, probe_inputs = checked_receipt(probe_qualification, 'probe')
    inputs.update(probe_inputs)
    reconstructed = generated_sources(producer)
    # Disposed checked C bodies are recipes, not retained dependency files.
    for name in reconstructed:
        inputs.pop(name, None)
    verify()
    tools = read_json(ROOT / '.deps/native-current/sdk/tools.lock.json')['tools']
    rust_pins = read_json(ROOT / 'userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json')
    tools.update(rust_pins['tools'])
    zig = shutil.which('zig')
    if not zig:
        raise ValueError('AF09 required Zig compiler unavailable')
    tools['zig'] = dict(path=str(Path(zig).resolve()), sha256=digest(zig))
    for tool in tools.values():
        inputs.update(verify_inputs({tool['path']: tool['sha256']}))
    helper_path = ROOT / 'userland/experiments/command-runner/process.py'
    spec = __import__('importlib.util', fromlist=['']).spec_from_file_location('af09_owned_process', helper_path)
    proc = __import__('importlib.util', fromlist=['']).module_from_spec(spec)
    sys.modules[spec.name] = proc
    spec.loader.exec_module(proc)
    inputs[str(helper_path)] = digest(helper_path)
    # Preserve the exact current source closure used by this composition.
    for directory in ('kernel', 'user', 'scripts'):
        inputs.update({str(p): digest(p) for p in sorted((ROOT / directory).rglob('*'))
                       if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'})
    inputs[str(ROOT / '.deps/native-current/current-inputs.json')] = digest(ROOT / '.deps/native-current/current-inputs.json')
    for name, expected in read_json(ROOT / '.deps/native-current/current-inputs.json')['files'].items():
        path = ROOT / '.deps/native-current' / name
        if path.resolve() != path or not path.is_relative_to(ROOT / '.deps/native-current'):
            raise ValueError('AF09 original dependency path')
        result_input = verify_inputs({str(path): expected})
        inputs.update(result_input)
    temporary = Path(tempfile.mkdtemp(prefix='filesystem-home-engine-', dir=ROOT / 'userland/build'))
    work = temporary / 'launch'
    work.mkdir()
    result = dict(schema=SCHEMA, status='preparing', executed=False, native_acceptance=False,
        protocol='AFSRPC09', service_result_bytes=320, launch_state_bytes=384,
        root_rights=3, home_rights=15, source_rights=15, provider_attempts=3,
        utc_min=1791290040, utc_max_exclusive=1791290100, rtc='2026-10-06T12:34:00,clock=vm',
        flags=list(PROFILE), limits=dict(LIMITS), commands=[], rows=[], inputs=inputs, tools=tools,
        qualification_sha256=digest(qualification), probe_qualification_sha256=digest(probe_qualification),
        qualification_path=str(Path(qualification).absolute()), probe_qualification_path=str(Path(probe_qualification).absolute()),
        qualified_generated_inputs=reconstructed,
        scope='Offline linked AF09 dependency and real kernel loader admission; no guest or persistence acceptance')
    evidence = ROOT / 'userland/docs/evidence/filesystem-home-prep-2026-10-24/engine'
    evidence.mkdir(parents=True, exist_ok=True)
    number = 1
    while True:
        receipt = evidence / ('attempt-%02d.json' % number)
        try:
            receipt.touch(exist_ok=False)
            break
        except FileExistsError:
            number += 1
    deadline = time.monotonic() + 1800
    proc = CleanupTrackedProcess(proc, result)
    env = proc.clean_env(temporary)
    generated_runtime = {}
    destination_owned = False
    def command(argv, log, rejection=None):
        requested = list(map(str, argv))
        args = command_arguments(requested, tools)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('AF09 target composition deadline')
        child_env = dict(env)
        if args[0] in [tools[name]['path'] for name in ('rustc', 'clippy-driver', 'rustfmt')]:
            child_env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
        run = proc.run(args, cwd=ROOT, env=child_env, work=temporary,
                       label='engine-%04d' % len(result['commands']), timeout=min(180, remaining))
        # The retained preparer reads its named compiler dependency logs. Keep
        # those owned files as well as the compact owned-process receipt.
        log = Path(log)
        if not log.is_absolute():
            log = temporary / log
        if not log.resolve().is_relative_to(temporary):
            raise ValueError('AF09 compiler log outside owned work')
        log.write_bytes(run.stdout + run.stderr)
        text = (run.stdout + run.stderr).decode(errors='replace')
        bad = ((rejection not in LINK_DENIALS or run.returncode != 1 or rejection not in text)
               if rejection else run.returncode != 0)
        bad = bad or not run.record['complete'] or run.record['cleanup'] != 'complete'
        result['commands'].append(dict(argv=args, requested_argv=requested, status='failed' if bad else 'pass',
            exit_code=run.returncode, expected_rejection=rejection, process=run.record,
            rejection_verified=bool(rejection) and not bad,
            log_sha256=hashlib.sha256(run.stdout + run.stderr).hexdigest(),
            tail=text[-7000:] if bad else text[-160:]))
        if bad:
            raise RuntimeError('AF09 build child failed: ' + str(log))
        return text
    try:
        destination.mkdir()
        destination_owned = True
        artifacts = runpy.run_path(str(SOURCE / 'home_engine_build.py'))['build'](
            work, proc, tools, deadline, result)
        if process_cleanup_unresolved(result):
            raise RuntimeError('AF09 imported builder cleanup unconfirmed')
        result['service_object_sha256'] = digest(artifacts['service'])
        preparation = prepare_base(temporary / 'base', command, tools,
            on_backend=lambda backend, artifact_root, copied=None: bind_runtime(backend, temporary,
                result['inputs'], generated_runtime, artifact_root=artifact_root, copied=copied))
        result['backend'] = preparation['backend']
        verify_inputs(generated_runtime)
        compose(temporary / 'base', preparation, artifacts, work, destination, command, result)
        upstream = ROOT / '.deps/native-current/baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1'
        notices = [(upstream / n, Path('openzfs') / n) for n in ('LICENSE', 'COPYRIGHT', 'NOTICE')]
        notices += [(p, Path('openzfs') / p.relative_to(upstream)) for p in sorted(upstream.glob('module/**/THIRDPARTYLICENSE*'))]
        notices += [(ROOT / '.deps/native-current/sdk/COPYRIGHT.musl', Path('COPYRIGHT.musl')),
                    (ROOT / 'LICENSE', Path('LICENSE'))]
        # Original Rust payload notices remain in its verified service delivery.
        baseline = ROOT / 'userland/build/service-deliveries/filesystem-service-metadata-2026-10-21-v1/notices'
        notices += [(p, p.relative_to(baseline)) for p in sorted(baseline.rglob('*')) if p.is_file()]
        for source, name in notices:
            result['inputs'][str(source)] = digest(source)
            target = destination / 'notices' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and digest(target) != digest(source):
                raise ValueError('AF09 notice collision')
            shutil.copyfile(source, target)
        (destination / 'SOURCE.md').write_text('# AF09 home engine candidate\n\n'
            'Original Aether work retains BSD-2-Clause; OpenZFS retains CDDL and mixed\n'
            'upstream notices, musl/Rust/compiler payloads retain their terms.\n'
            'Pinned OpenZFS:71a9f9578616a90c3c14bb59629fb4d31bfd68d1.\n'
            'Exact retained inputs, scoped generation recipes and commands: build.json.\n'
            'Rebuild with scripts/fs_home_launch.py --checked PRODUCER --probe-checked PROBE.\n'
            'Recomposition of retained SDK objects is not an independent SDK rebuild.\n'
            'No guest, persistence or release acceptance. Modified CDDL source must\n'
            'accompany any separately authorized public distribution.\n')
        (destination / 'preparation.json').write_text(__import__('json').dumps(dict(
            executed=False, backend=preparation['backend'], original_commands=len(preparation['commands'])), indent=2) + '\n')
        verify_inputs(result['inputs'])
        verify_inputs(generated_runtime)
        result['runtime_generated_inputs'] = generated_runtime
        result['runtime_final_input_verification'] = 'pass'
        checked_receipt(qualification, 'producer')
        checked_receipt(probe_qualification, 'probe')
        result.update(status='pass', final_input_verification='pass', elf_sha256=digest(destination / 'filesystem.elf'),
                      elf_bytes=(destination / 'filesystem.elf').stat().st_size)
        validate_record(result)
        # Final publication and intake stay inside the same failure boundary.
        result['cleanup'] = dict(native_attempted=False,
            removed_generated_members=sum(p.is_file() for p in temporary.rglob('*')))
        shutil.rmtree(temporary)
        result['cleanup']['owned_work'] = 'removed'
        (destination / 'build.json').write_text(json.dumps(result, indent=2) + '\n')
        members = sorted(p for p in destination.rglob('*') if p.is_file())
        (destination / 'SHA256SUMS').write_text(''.join(digest(p) + '  ' + str(p.relative_to(destination)) + '\n' for p in members))
        candidate = intake(destination, digest(destination / 'SHA256SUMS'))
    except BaseException as error:
        result.update(status='failed', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        primary = sys.exception()
        unresolved = process_cleanup_unresolved(result, primary)
        if unresolved:
            retained = retain_unresolved(result,
                [temporary, destination if destination_owned else None], primary)
            result['cleanup'] = dict(status='unresolved', native_attempted=False,
                owned_outputs_retained=True, retained_paths=retained)
            result.setdefault('error', 'AF09 child cleanup unconfirmed')
        else:
            if temporary.exists():
                result['cleanup'] = dict(native_attempted=False, removed_generated_members=sum(p.is_file() for p in temporary.rglob('*')))
                try:
                    shutil.rmtree(temporary)
                    result['cleanup']['owned_work'] = 'removed'
                except OSError as error:
                    result.update(status='failed', cleanup_error=str(error))
                    result['cleanup']['owned_work'] = 'failed'
            if result['status'] != 'pass':
                if destination_owned and destination.exists():
                    try:
                        shutil.rmtree(destination)
                    except OSError as error:
                        result['destination_cleanup_error'] = str(error)
        try:
            receipt.write_text(json.dumps(result, indent=2) + '\n')
        except BaseException as error:
            if not unresolved and destination_owned and destination.exists():
                try:
                    shutil.rmtree(destination)
                except OSError:
                    pass  # Primary receipt failure remains explicit to caller.
            if primary is None:
                raise
            primary.add_note('AF09 receipt write failed: ' + str(error))
        if unresolved and primary is None:
            error = RuntimeError('AF09 child cleanup unconfirmed; inspect ' + str(receipt))
            retain_unresolved(result, [], error)
            raise error
    if result['status'] != 'pass':
        raise RuntimeError('AF09 final cleanup failed; inspect ' + str(receipt))
    return dict(candidate, receipt=str(receipt))


def main():
    import argparse
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            self.exit(64, '[ERROR] ' + ascii(message)[1:-1] + '\n')
    parser = Parser(description=__doc__, epilog='Offline preparation only. Keep the retained receipt; correct a failed prerequisite before a new explicit output. Guest execution requires a fresh disposition.')
    parser.add_argument('--version', action='version', version='aether-fs-home-launch 1')
    parser.add_argument('--checked', required=True, type=Path, help='current passing native-home producer receipt')
    parser.add_argument('--probe-checked', required=True, type=Path, help='current passing helper/count/UTC-window receipt')
    parser.add_argument('--output', required=True, type=Path, help='unused .deps/fs-launch-af09-* dependency')
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.checked, args.probe_checked)))


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print('[BLOCKED] ' + ascii(str(error))[1:-1], file=sys.stderr)
        raise SystemExit(2)
    except (OSError, RuntimeError) as error:
        print('[ERROR] ' + ascii(str(error))[1:-1], file=sys.stderr)
        raise SystemExit(1)
