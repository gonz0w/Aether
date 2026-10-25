#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare an explicit AF08 directory engine; never execute a guest or repin AF07."""
import argparse
import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT, verify
from fs_launch_intake import intake as baseline_intake
import fs_metadata_launch as launch
import openzfs_fs_metadata_service as metadata

SCHEMA = 'aether-fs-context-launch-v1'
SOURCE = ROOT/'userland/experiments/filesystem-service'
CHECKER = SOURCE/'check-directory-contexts.py'
digest = metadata.digest
REQUIRED = dict(launch.REQUIRED, aether_zpl_context='launch-engine.o')


def checked(directory):
    directory = Path(directory).absolute()
    if (directory.parent != ROOT/'userland/build' or directory.is_symlink()
            or not directory.name.startswith('filesystem-directory-contexts-')):
        raise ValueError('AF08 requires an owned focused qualification')
    report = json.loads((directory/'results.json').read_text())
    if (report.get('status') != 'pass' or report.get('native_executed') is not False
            or report.get('cwd_wire') is not True or report.get('profile') != 'in-place'
            or report.get('checker_sha256') != digest(CHECKER)
            or len(report.get('semantic_controls', [])) != 9
            or len(report.get('compatibility_rejections', [])) != 3
            or report.get('native_service_object', {}).get('protocol') != 'AFSRPC08'):
        raise ValueError('AF08 missing selected host/target/entry coverage')
    inputs = {str(CHECKER): digest(CHECKER)}
    for name, expected in (report['sources'] | report['rust_native_libraries']
                           | report['original_header_inputs']).items():
        if not Path(name).is_absolute() or digest(Path(name)) != expected:
            raise ValueError('AF08 source/runtime/header changed: '+name)
        inputs[name] = expected
    for tool in report['tools'].values():
        if digest(Path(tool['path'])) != tool['sha256']:
            raise ValueError('AF08 tool changed')
        inputs[tool['path']] = tool['sha256']
    obj = directory/'filesystem-contexts.o'
    if digest(obj) != report['native_service_object']['sha256']:
        raise ValueError('AF08 native service object changed')
    return directory, report, inputs


def intake(directory, seal):
    root, members = launch.closure(directory, seal)
    record = json.loads((root/'build.json').read_text())
    if (record.get('schema') != SCHEMA or record.get('status') != 'pass'
            or record.get('executed') is not False or record.get('protocol') != 'AFSRPC08'
            or record.get('owner_manifest_sha256') != launch.OWNER_SEAL
            or record.get('baseline_service_manifest_sha256') != metadata.SEAL
            or record.get('elf_sha256') != members.get('filesystem.elf')
            or record.get('elf_bytes') != (root/'filesystem.elf').stat().st_size
            or set(record.get('origins', {})) != REQUIRED.keys()
            or any(Path(record['origins'][name]).name != origin for name, origin in REQUIRED.items())
            or not record.get('structural_loader', '').startswith('ELF structural pages=')
            or record.get('limits') != dict(mutations=9, requests=96, engine_pages=8192,
                writer_seconds=60, writer_ticks=6000, reader_seconds=30, reader_ticks=3000)):
        raise ValueError('AF08 engine identity/profile/coverage')
    launch.check_frames(record.get('local_frames', {}))
    if (not record.get('inputs') or not record.get('commands')
            or any(row.get('status') != 'pass' for row in record['commands'])
            or not all(isinstance(record.get(key), str) and re.fullmatch('[0-9a-f]{64}',record[key])
                for key in ('qualification_sha256','service_object_sha256'))):
        raise ValueError('AF08 missing consumed closure')
    for name, expected in record['inputs'].items():
        if not Path(name).is_absolute() or digest(Path(name)) != expected:
            raise ValueError('AF08 consumed input changed: '+name)
    for member in ('SOURCE.md', 'preparation.json', 'notices/LICENSE',
                   'notices/openzfs/LICENSE', 'notices/openzfs/COPYRIGHT',
                   'notices/openzfs/NOTICE', 'notices/COPYRIGHT.musl'):
        if member not in members:
            raise ValueError('AF08 missing provenance/notices')
    return dict(schema='aether-fs-context-launch-result-v1', manifest_sha256=seal, elf=str(root/'filesystem.elf'),
        elf_sha256=members['filesystem.elf'], members=len(members), executed=False,
        native_acceptance=False, protocol='AFSRPC08', scope='Explicit linked candidate only')


def build(destination, qualification):
    destination = launch.validate_destination(destination)
    if not destination.name.startswith('fs-launch-af08-'):
        raise ValueError('AF08 requires unused .deps/fs-launch-af08-* output')
    directory, report, inputs = checked(qualification)
    owner = copy.deepcopy(launch.owner_intake())
    baseline = baseline_intake(launch.CURRENT)
    verify()
    tools = json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']
    temporary = Path(tempfile.mkdtemp(prefix='fs-context-launch-', dir=ROOT/'zig-out'))
    work = temporary/'launch'; work.mkdir()
    result = dict(schema=SCHEMA, status='preparing', executed=False, protocol='AFSRPC08',
        commands=[], inputs=dict(owner['inputs']) | inputs, tools=tools,
        owner_manifest_sha256=launch.OWNER_SEAL,
        baseline_service_manifest_sha256=metadata.SEAL,
        qualification_sha256=digest(directory/'results.json'),
        service_object_sha256=report['native_service_object']['sha256'],
        limits=dict(mutations=9, requests=96, engine_pages=8192,
            writer_seconds=60, writer_ticks=6000, reader_seconds=30, reader_ticks=3000))
    for folder in ('kernel', 'user', 'scripts'):
        result['inputs'].update({str(p): digest(p) for p in (ROOT/folder).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'})
    print('[RUNNING] Preparing AF08 engine '+ascii(str(destination))[1:-1]+'; no guest execution',file=sys.stderr,flush=True)
    destination.mkdir()

    def command(argv, log, rejection=None):
        args = list(map(str, argv))
        row = dict(argv=args, expected_rejection=rejection, timeout_seconds=180)
        result['commands'].append(row)
        try:
            with Path(log).open('w') as stream:
                run = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
            text = Path(log).read_text(errors='replace')
            bad = (run.returncode == 0 or rejection not in text) if rejection else run.returncode != 0
            row.update(exit_code=run.returncode, status='failed' if bad else 'pass')
            if bad:
                raise RuntimeError('AF08 build failed: '+str(log))
            return text
        except subprocess.TimeoutExpired:
            row.update(status='timeout', cleanup='subprocess.run killed and waited for compiler')
            raise
        finally:
            if Path(log).is_file():
                text = Path(log).read_text(errors='replace')
                row.update(log_sha256=digest(Path(log)), tail=text[-4000:] if row.get('status') != 'pass' else text[-160:])

    try:
        preparation = metadata.prepare_engine(temporary/'base', command, tools)
        selected = work/'filesystem-metadata.o'
        shutil.copyfile(directory/'filesystem-contexts.o', selected)
        owner['service']['object'] = str(selected)
        launch.compose(temporary/'base', preparation, owner, work, destination,
                       command, result, context_provider=True)
        llvm = Path(tools['clang']['path']).parent
        symbols = command([llvm/'llvm-nm', '--defined-only', destination/'filesystem.elf'], work/'context-symbols.log')
        if len(re.findall(r'^\S+ T aether_zpl_context$', symbols, re.M)) != 1:
            raise ValueError('AF08 missing original context getter')
        result['origins'] = launch.origins((work/'launch.map').read_text(), REQUIRED)
        for name, expected in result['inputs'].items():
            if digest(Path(name)) != expected:
                raise ValueError('AF08 input changed during build: '+name)
        if checked(directory)[1] != report or baseline_intake(launch.CURRENT) != baseline:
            raise ValueError('AF08 qualification/baseline changed')
        (destination/'SOURCE.md').write_text('# AF08 physical-directory engine candidate\n\n'
            'Explicit checked Rust AFSRPC08 service and original OpenZFS C getter;\n'
            'unchanged sealed launch-owner ABI. Exact inputs/commands in build.json.\n'
            'BSD-2-Clause applies to original Aether work; OpenZFS CDDL and all\n'
            'original mixed notices remain. Musl/Rust/compiler terms are preserved.\n'
            'Rebuild with scripts/fs_context_launch.py --checked owned-output.\n'
            'No VM, persistence, independent build or public release acceptance.\n')
        result.update(status='pass', elf_sha256=digest(destination/'filesystem.elf'),
                      elf_bytes=(destination/'filesystem.elf').stat().st_size)
    except BaseException as error:
        result.update(status='failed', error=str(error))
        raise
    finally:
        result['cleanup'] = dict(native_attempted=False,
            removed_generated_members=sum(p.is_file() for p in temporary.rglob('*')))
        shutil.rmtree(temporary)
        if result['status'] != 'pass':
            for p in destination.iterdir():
                if p.is_dir(): shutil.rmtree(p)
                else: p.unlink()
        (destination/'build.json').write_text(json.dumps(result, indent=2)+'\n')
    members = sorted(p for p in destination.rglob('*') if p.is_file())
    (destination/'SHA256SUMS').write_text(''.join(digest(p)+'  '+str(p.relative_to(destination))+'\n' for p in members))
    return intake(destination, digest(destination/'SHA256SUMS'))


def main():
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            self.exit(64, '[ERROR] '+ascii(message)[1:-1]+'\n')
    parser=Parser(description=__doc__,epilog='Example: --checked userland/build/OWNED_CHECK --output .deps/fs-launch-af08-NAME. Private candidate only; no VM, default pin update or release acceptance.')
    parser.add_argument('--version',action='version',version='aether-fs-context-launch 1')
    parser.add_argument('--output', required=True, type=Path,help='unused .deps/fs-launch-af08-* candidate directory')
    parser.add_argument('--checked', required=True, type=Path,help='owned passing check-directory-contexts.py output')
    args=parser.parse_args()
    print(json.dumps(build(args.output,args.checked)))


if __name__=='__main__':
    try: main()
    except ValueError as error:
        print('[BLOCKED] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(2)
    except (OSError,RuntimeError,subprocess.SubprocessError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(1)
