#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build a separate fixed AF06 filesystem owner; execute no guest."""
import argparse
from contextlib import redirect_stdout
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT
from openzfs_fs_service import intake, recheck, sha

USERLAND = ROOT / 'userland'
DELIVERY = USERLAND / 'build/service-deliveries/filesystem-service-directories-2026-10-20-v1'
OWNER = USERLAND / 'experiments/filesystem-service/launch-owner.rs'
SERVICE = ROOT / 'user/storage/service-runtime'
VOLUME = ROOT / 'user/storage/openzfs-volume'


def validate_destination(destination):
    path = Path(destination).absolute()
    if (path.parent != ROOT / '.deps' or not path.name.startswith('fs-launch-')
            or path.exists() or path.is_symlink() or path.parent.resolve() != path.parent):
        raise ValueError('launch delivery requires an unused .deps/fs-launch-* destination')
    return path


def recipe(record, name):
    matches = [c['argv'] for c in record['commands'] if '-o' in c['argv'] and
               Path(c['argv'][c['argv'].index('-o')+1]).name == name and c.get('exit_code') == 0]
    if len(matches) != 1:
        raise ValueError('ambiguous/missing successful preparation recipe: '+name)
    return matches[0]


def labels(text):
    anchor = '        txg != 782 ||'
    if text.count(anchor) != 1:
        raise ValueError('bounded exported label context changed')
    return text.replace(anchor, '        txg < 782 ||', 1)


def origins(mapping, required):
    owner = None
    found = {}
    for line in mapping.splitlines():
        fields = line.split()
        if len(fields) < 5:
            continue
        item = fields[-1]
        if ':(' in item:
            owner = item.split(':(', 1)[0]
        elif item in required:
            if item in found or owner is None or Path(owner).name != required[item]:
                raise ValueError('launch symbol origin: '+item)
            found[item] = owner
    if set(found) != set(required):
        raise ValueError('missing launch symbol origins: '+str(set(required)-set(found)))
    return found


def compose(preparation, record, destination):
    destination = validate_destination(destination)
    selected = intake(DELIVERY, mixed=True, waiting=True, bulk=True, runtime=True,
                      activation=True, names=True, directories=True)
    if record.get('fs_service') != selected or record['cases'][0]['engine_entry_executed']:
        raise ValueError('launch requires the exact nonexecuted AF06 preparation')
    for name, digest in record['sources'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('preparation source drift: '+name)
    destination.mkdir()
    port = preparation / 'port'
    work = preparation / 'launch-owner'
    work.mkdir()
    result = dict(schema='aether-fs-launch-build-v1', status='incomplete',
                  executed=False, service_manifest_sha256=selected['manifest_sha256'],
                  commands=[], inputs={}, scope='Linked owner and structural loader only; not native/sys-init acceptance')
    consumed = [OWNER, SERVICE/'filesystem-engine.c', SERVICE/'filesystem-engine.h',
                SERVICE/'engine-observe.inc', VOLUME/'filesystem-import.c',
                ROOT/'.deps/native-current/current-inputs.json',
                ROOT/'.deps/native-current/sdk/tools.lock.json',
                ROOT/'kernel/native_elf.zig',
                ROOT/'user/storage/openzfs-elapsed/startup-fixture.h',
                ROOT/'user/storage/openzfs-elapsed/startup.h',
                ROOT/'.deps/native-utc-v3/runtime/utc.h',
                ROOT/'.deps/native-service-runtime-v3/runtime/runtime.h',
                VOLUME/'pool-label.c', VOLUME/'namespace-label.inc', Path(__file__)]
    upstream = ROOT/'.deps/native-current/baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1'
    notices = [upstream/'LICENSE', upstream/'COPYRIGHT', upstream/'NOTICE',
               *sorted(upstream.glob('module/**/THIRDPARTYLICENSE*')),
               ROOT/'.deps/native-current/sdk/COPYRIGHT.musl',
               ROOT/'LICENSE']
    # Source availability and upstream attribution remain separate obligations;
    # these notices do not relicense the engine or certify release distribution.
    consumed += notices
    consumed += [Path(p) for p in selected['inputs']]
    result['tools'] = record['tools']
    result['preparation_sources_sha256'] = hashlib.sha256(json.dumps(record['sources'], sort_keys=True).encode()).hexdigest()
    consumed += [Path(p) for p in recipe(record, 'engine.elf') if p.endswith(('.a','.o')) and not Path(p).is_relative_to(preparation)]
    result['inputs'] = {str(p): sha(p) for p in consumed}

    def command(argv, name):
        args = list(map(str, argv))
        run = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=180)
        text = run.stdout + run.stderr
        row = dict(argv=args, exit_code=run.returncode,
                   output_sha256=hashlib.sha256(text.encode()).hexdigest())
        result['commands'].append(row)
        if run.returncode:
            row['failure_tail'] = text[-6000:]
            raise RuntimeError('launch command failed: '+name+'\n'+text[-2000:])
        return text

    try:
        # Rebuild just the bounded label adapter. All other decoder checks stay exact.
        (work/'namespace-launch-label.inc').write_text(labels((VOLUME/'namespace-label.inc').read_text()))
        anchor = '#include "namespace-label.inc"'
        text = (VOLUME/'pool-label.c').read_text()
        if text.count(anchor) != 1:
            raise ValueError('label include context')
        (work/'pool-launch-label.c').write_text(text.replace(anchor, '#include "namespace-launch-label.inc"', 1))
        old_label = recipe(record, 'pool-label.o')
        cc = old_label[:old_label.index('-c')]
        command(cc + ['-I'+str(work), '-c', work/'pool-launch-label.c', '-o', work/'pool-launch-label.o'], 'label')
        includes = ['-I'+str(SERVICE), '-I'+selected['header_directory']]
        # The original API compile closure supplies the pinned OpenZFS headers.
        command(cc + includes + ['-fstack-usage', '-c', VOLUME/'filesystem-import.c', '-o', work/'filesystem-import.o'], 'import')
        startup = recipe(record, 'engine-startup.o')
        command(startup[:startup.index('-c')] + includes + ['-I'+str(VOLUME), '-I'+str(SERVICE),
                '-fstack-usage', '-c', SERVICE/'filesystem-engine.c', '-o', work/'filesystem-engine.o'], 'engine')
        command(['rustc', '+1.98.0', '--edition=2021', '--target=x86_64-unknown-none',
                 '--crate-type=lib', '--emit=obj', '-Copt-level=2', '-Cpanic=abort',
                 '-Crelocation-model=static', '-Cno-redzone=yes', '-Dwarnings',
                 '-Dunsafe_op_in_unsafe_fn', OWNER, '-o', work/'launch-owner.o'], 'owner')
        partial = recipe(record, 'selected-libzpool.o')
        old = str(port/'pool-label.o')
        if partial.count(old) != 1:
            raise ValueError('partial label input closure')
        partial = [str(work/'pool-launch-label.o') if p == old else p for p in partial]
        partial = [('-Map='+str(work/'service-partial.map')) if p.startswith('-Map=') else p for p in partial]
        partial[-1] = str(work/'launch-libzpool.o')
        command(partial, 'service-partial')
        result['service_origins'] = origins((work/'service-partial.map').read_text(),
            {'aether_fs_directories_run': 'filesystem-directories.o',
             'aether_pool_label_config': 'pool-launch-label.o'})
        engine = recipe(record, 'selected-engine.o')
        engine = [str(work/'launch-libzpool.o') if p == str(port/'selected-libzpool.o') else p for p in engine]
        engine[-1] = str(work/'launch-engine.o')
        command(engine, 'engine-partial')
        link = recipe(record, 'engine.elf')
        old = str(port/'engine-startup.o')
        link = [str(work/'launch-engine.o') if p == str(port/'selected-engine.o') else
                '-Map='+str(work/'launch.map') if p.startswith('-Map=') else p for p in link]
        link[link.index(old):link.index(old)+1] = list(map(str, [work/'launch-owner.o', work/'filesystem-engine.o', work/'filesystem-import.o']))
        link[-1] = str(destination/'filesystem.elf')
        command(link, 'link')
        result['origins'] = origins((work/'launch.map').read_text(), {
            'main':'launch-owner.o', 'aether_fs_launch_serve':'launch-owner.o',
            'aether_fs_engine_run':'filesystem-engine.o',
            'aether_fs_engine_import':'filesystem-import.o',
            'aether_fs_directories_run':'launch-engine.o',
            'spa_import':'launch-engine.o', 'spa_export':'launch-engine.o'})
        llvm = Path(record['tools']['clang']['path']).parent
        elf = destination/'filesystem.elf'
        symbols = command([llvm/'llvm-nm', '--defined-only', elf], 'symbols')
        forbidden = ('aether_fs_owner_probe', 'aether_pool_namespace_write', 'aether_spa_import_probe')
        if any(line.split()[-1] in forbidden for line in symbols.splitlines() if line.strip()):
            raise ValueError('fixture still live in launch ELF')
        imports = command([llvm/'llvm-nm', '-u', elf], 'imports')
        if any(line.split()[-1] != '_DYNAMIC' for line in imports.splitlines() if line.strip()):
            raise ValueError('unresolved launch imports')
        reloc = command([llvm/'llvm-readelf', '-rW', elf], 'relocations')
        if reloc.strip() != 'There are no relocations in this file.':
            raise ValueError('launch static relocations')
        result['segments'] = command([llvm/'llvm-readelf', '-lW', elf], 'segments')
        checker = (port/'image-check.zig').read_text()
        shutil.copyfile(elf, work/'filesystem.elf')
        checker = checker.replace('@embedFile("engine.elf")', '@embedFile("filesystem.elf")')
        (work/'image-check.zig').write_text(checker)
        result['structural_loader'] = command(['zig', 'run', '--cache-dir', ROOT/'.zig-cache',
            '--global-cache-dir', ROOT/'.zig-cache/global', '-O', 'ReleaseSafe', '--dep', 'native_elf',
            '-Mroot='+str(work/'image-check.zig'), '-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')], 'loader').strip()
        result['local_frames'] = {p.name: p.read_text() for p in work.glob('*.su')}
        if len(result['local_frames']) != 2 or any(
                'dynamic' in text or any(int(line.split('\t')[1]) > 8192 for line in text.splitlines())
                for text in result['local_frames'].values()):
            raise ValueError('launch local frame limit; not a full call-chain proof')
        result['map_sha256'] = sha(work/'launch.map')
        for name, digest in result['inputs'].items():
            if sha(name) != digest:
                raise ValueError('launch input drift: '+name)
        recheck(selected)
        shutil.copytree(DELIVERY/'notices', destination/'notices')
        for path in notices:
            name = ('openzfs/'+str(path.relative_to(upstream))) if path.is_relative_to(upstream) else path.name
            target = destination/'notices'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        (destination/'SOURCE.md').write_text(
            '# Filesystem launch candidate source\n\n'
            'Original first-party work: BSD-2-Clause. OpenZFS remains CDDL and\n'
            'retains its upstream mixed notices; musl/Rust/compiler notices apply\n'
            'to their own components. No whole-image relicensing.\n\n'
            'OpenZFS upstream: https://github.com/openzfs/zfs/tree/71a9f9578616a90c3c14bb59629fb4d31bfd68d1\n'
            'Exact input/tool hashes and build commands: build.json. Local original\n'
            'source and scoped transformations: Aether user/storage and scripts;\n'
            'Rust main: Aether-userland experiments/filesystem-service/launch-owner.rs.\n'
            'The pinned offline SDK and AF06 dependency remain required to rebuild.\n'
            'This is a local integration candidate, not public distribution approval;\n'
            'a public release must provide the matching modified CDDL source.\n')
        result.update(status='pass', elf_sha256=sha(elf), elf_bytes=elf.stat().st_size)
        return {key: result[key] for key in ('status','elf_sha256','elf_bytes','structural_loader','executed')}
    finally:
        (destination/'build.json').write_text(json.dumps(result, indent=2)+'\n')



def build(destination):
    import service_runtime_smoke as runtime
    destination = validate_destination(destination)
    pair = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-zpl-pair-launch-', dir=ROOT/'zig-out'))
    out = None
    try:
        with redirect_stdout(sys.stderr):
            out = runtime.suite(ROOT/'.deps/native-utc-v3/base', case='pool-import', fixed_reaper=True,
                engine_utc=True, utc_delivery=ROOT/'.deps/native-utc-v3', pool_create=True, pool_namespace=True,
                pool_diagnose='build', pool_zpl_write=True, _zpl_stage=pair/'writer', _zpl_writer_budget=True,
                namespace_ipc=True, _zpl_fs_service=DELIVERY, _zpl_fs_mixed=True, namespace_wait=True,
                _zpl_fs_bulk=True, _zpl_fs_runtime=True, _zpl_fs_activation=True, _zpl_fs_names=True,
                _zpl_fs_directories=True, _fs_launch_output=destination)
    finally:
        reports = list(pair.glob('*-build.json'))
        if reports:
            preparation = json.loads(reports[0].read_text())
            out = Path(preparation['output'])
            if destination.exists():
                (destination/'preparation.json').write_text(json.dumps({
                    'status':preparation['report']['status'], 'commands':len(preparation['report']['commands']),
                    'report_sha256':sha(out/'results.json'), 'executed':False},indent=2)+'\n')
        shutil.rmtree(pair)
        if out is not None:
            if (out.parent != ROOT/'zig-out' or out.resolve() != out or out.is_symlink()
                    or not out.name.startswith('thread-suite-service-runtime-')
                    or out.name.startswith('thread-suite-service-runtime-zpl-pair-')):
                raise ValueError('launch refuses unowned preparation cleanup')
            shutil.rmtree(out)
        if destination.exists() and (destination/'build.json').is_file():
            result = json.loads((destination/'build.json').read_text())
            if result['status'] == 'pass':
                members = sorted(p for p in destination.rglob('*') if p.is_file())
                (destination/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(destination))+'\n' for p in members))


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[ERROR] '+ascii(message)[1:-1]+'\n')


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.output)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1], file=sys.stderr)
        sys.exit(1)
    print(json.dumps({'schema':'aether-fs-launch-result-v1','output':str(args.output),'executed':False}))
