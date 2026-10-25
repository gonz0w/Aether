#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare explicit current AF07 inputs offline; never execute a guest."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from deps import ROOT
from source_paths import relocate

sys.path.insert(0, str(ROOT/'sys-init/scripts'))
from bounded_tools import run_tool

SELECTION = ROOT/'docs/native-af07-inputs-v1.json'
ORIGINAL = ROOT/'sys-init/docs/evidence/filesystem-af07-owner-2026-10-21'
ORIGINAL_SEAL = '8f99308958df2552b527bc6abf07a78ea6b8a8bb670fd706139d1cab5c5ddd96'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pairs(items):
    result = {}
    for name, value in items:
        if name in result:
            raise ValueError('duplicate input selection field')
        result[name] = value
    return result


def selection():
    if SELECTION.is_symlink() or SELECTION.stat().st_size > 65536:
        raise ValueError('AF07 selection path/size')
    data = json.loads(SELECTION.read_text(), object_pairs_hook=pairs)
    if set(data) != {'format', 'scope', 'engine', 'activation'} or data['format'] != 'aether-private-af07-inputs-v1':
        raise ValueError('AF07 selection format')
    for name, fields in [('engine', {'directory', 'seal'}), ('activation', {'directory', 'seal', 'elf', 'raw'})]:
        row = data[name]
        if not isinstance(row, dict) or set(row) != fields or not isinstance(row.get('directory'), str):
            raise ValueError('AF07 selection fields')
        path = Path(row['directory'])
        if path.is_absolute() or '..' in path.parts or str(path) != row['directory']:
            raise ValueError('AF07 selection directory')
        for field in fields-{'directory'}:
            if not isinstance(row[field], str) or not re.fullmatch('[0-9a-f]{64}', row[field]):
                raise ValueError('AF07 selection digest')
    return data


def checked_members(root, seal):
    """The historical format seals exact bytes, never live compatibility."""
    root = Path(root)
    if root.resolve() != root or root.is_symlink() or digest(root/'sha256.json') != seal:
        raise ValueError('AF07 activation manifest identity')
    members = json.loads((root/'sha256.json').read_text(), object_pairs_hook=pairs)
    if not isinstance(members, dict) or not 1 <= len(members) <= 100:
        raise ValueError('AF07 activation member count')
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('AF07 activation symlink')
        if path.is_file():
            actual.add(str(path.relative_to(root)))
    if actual != set(members) | {'sha256.json'}:
        raise ValueError('AF07 activation member closure')
    for name, row in members.items():
        path = Path(name)
        if (path.is_absolute() or '..' in path.parts or str(path) != name or
                set(row) != {'sha256', 'bytes'} or type(row['bytes']) is not int or
                not 0 <= row['bytes'] <= 4*1024*1024 or
                (root/path).stat().st_size != row['bytes'] or digest(root/path) != row['sha256']):
            raise ValueError('AF07 activation member identity')
    return members


def output_path(destination, prefix):
    destination = Path(destination).absolute()
    if (destination.parent != ROOT/'.deps' or destination.parent.resolve() != destination.parent or
            not destination.name.startswith(prefix) or destination.exists() or destination.is_symlink()):
        raise ValueError('requires unused .deps/'+prefix+'* destination')
    return destination


def activation(destination):
    """Recompile unchanged ABI29 activation as a fresh dependency, not evidence."""
    destination = output_path(destination, 'fs-init-af07-')
    checked_members(ORIGINAL, ORIGINAL_SEAL)
    before = json.loads((ORIGINAL/'preparation.json').read_text())
    for name, expected in before['sources'].items():
        if digest(ROOT/'sys-init'/name) != expected:
            raise ValueError('activation source changed; new implementation review required: '+name)
    tools = {str(relocate(name)): value for name, value in before['tools'].items()}
    for path, expected in tools.items():
        if digest(path) != expected:
            raise ValueError('activation tool changed: '+path)
    destination.mkdir()
    record = {k: before[k] for k in ('sources', 'engine_members')}
    record.update(date='2026-10-23', scope='Fresh offline ABI29 activation rebuild; not native acceptance or ABI31 shell',
                  old_and_external_inputs={}, tools=tools, commands=[], native_acceptance=False)
    # Preserve all immutable provenance. Only a fresh inspection of the actual
    # rebuilt pair can replace the obsolete host stack-inspector identity.
    for name, expected in before['old_and_external_inputs'].items():
        path = relocate(name)
        actual = digest(path)
        if path != ROOT/'scripts/owner_stack.py' and actual != expected:
            raise ValueError('activation external input changed: '+str(path))
        record['old_and_external_inputs'][str(path)] = actual
    for path in (Path(__file__), ROOT/'scripts/fs_init_af07.py', ROOT/'sys-init/scripts/bounded_tools.py'):
        record['old_and_external_inputs'][str(path)] = digest(path)
    env = dict(os.environ)
    rust = Path(next(c['argv'][0] for c in before['commands'] if c['label']=='native-elf'))
    env['DYLD_LIBRARY_PATH'] = str(rust.parent.parent/'lib')
    wanted = {name for name in ('format-init.rs', 'format-policy.rs', 'format-tests.rs',
        'host-compile', 'host-tests', 'clippy-False', 'clippy-True', 'native-elf', 'native-raw')}
    try:
        for old in before['commands']:
            if old['label'] not in wanted:
                continue
            args = []
            for arg in old['argv']:
                arg = arg.replace('/Users/cam/DEV/sys-init/docs/evidence/filesystem-af07-owner-2026-10-21', str(destination))
                arg = arg.replace('/Users/cam/DEV/sys-init/', str(ROOT/'sys-init')+'/')
                args.append(arg)
            log = destination/(old['label']+'.log')
            row = dict(label=old['label'], argv=args, timeout=60, output_limit=4*1024*1024)
            record['commands'].append(row)
            try:
                run_tool(args, env, log, timeout=60, cwd=ROOT/'sys-init')
                row['exit_code'] = 0
            finally:
                if log.is_file():
                    row.update(log_sha256=digest(log), tail=log.read_text(errors='replace')[-1000:])
                    log.unlink()
        from fs_init_intake import intake
        record['inspection'] = intake(destination/'owner.elf', destination/'owner.raw',
                                       digest(destination/'owner.elf'), digest(destination/'owner.raw'))
        if record['inspection']['raw_bytes'] != 2072 or record['inspection']['stack']['entry_stack_bytes'] != 1096:
            raise ValueError('activation geometry changed')
        record['artifacts'] = {name: dict(sha256=digest(destination/name), bytes=(destination/name).stat().st_size)
                               for name in ('owner.elf', 'owner.raw')}
        for name, expected in record['sources'].items():
            path = ROOT/'sys-init'/name
            if digest(path) != expected:
                raise ValueError('activation source changed during rebuild')
            shutil.copyfile(path, destination/Path(name).name)
        for name, expected in record['old_and_external_inputs'].items():
            if digest(name) != expected:
                raise ValueError('activation external changed during rebuild')
        record.update(all_inputs_unchanged=True, status='pass')
    except BaseException as error:
        record.update(status='failed', error=str(error), all_inputs_unchanged=False)
        raise
    finally:
        # Keep the selected active dependency only; no test executable/metadata.
        for name in ('tests', 'policy.rmeta', 'test.rmeta'):
            (destination/name).unlink(missing_ok=True)
        (destination/'preparation.json').write_text(json.dumps(record, indent=2)+'\n')
    files = {str(p.relative_to(destination)): dict(sha256=digest(p), bytes=p.stat().st_size)
             for p in sorted(destination.iterdir()) if p.is_file()}
    (destination/'sha256.json').write_text(json.dumps(files, indent=2)+'\n')
    checked_members(destination, digest(destination/'sha256.json'))
    return dict(directory=str(destination.relative_to(ROOT)), seal=digest(destination/'sha256.json'),
                elf=digest(destination/'owner.elf'), raw=digest(destination/'owner.raw'))


def guarded(destination, engine_directory, engine_seal, paths=False, dup2=False, checked=None, cwd=False):
    """Build one matching ABI31 dependency from current checked providers."""
    if type(cwd) is not bool or (cwd and not (paths and dup2)):
        raise ValueError('guarded CWD requires paths and dup2')
    if type(paths) is not bool or type(dup2) is not bool or (dup2 and not paths):
        raise ValueError('guarded dup2 requires canonical paths')
    if checked is not None and (not isinstance(checked,dict) or set(checked)!={'producer','provider','owner'}):
        raise ValueError('guarded checked provider set')
    if cwd:
        from fs_context_launch import intake as engine_intake
    else:
        from fs_metadata_launch import intake as engine_intake
    from fs_session import FLAGS
    import struct
    destination = output_path(destination, 'fs-owner-af08-' if cwd else 'fs-owner-af07-')
    engine = engine_intake(engine_directory, engine_seal)
    destination.mkdir()
    record = dict(format='aether-guarded-af08-inputs-v1' if cwd else 'aether-guarded-af07-inputs-v1', status='preparing', native_executed=False,
                  profile='AENFS005/AENMX010/ABI31', file_wire='AEFP0003' if cwd else 'AEFP0002' if dup2 else 'AEFP0001' if paths else 'AEFD0001', path_probe=paths, dup2_wire=dup2, cwd_wire=cwd, commands=[], inputs={}, tools={},
                  engine=dict(directory=str(Path(engine_directory).relative_to(ROOT)), seal=engine_seal,
                              elf_sha256=engine['elf_sha256']))
    owned = []
    def command(label, args):
        log = destination/(label+'.log')
        row = dict(label=label, argv=list(map(str,args)), timeout=180, output_limit=4*1024*1024)
        record['commands'].append(row)
        try:
            data=run_tool(row['argv'],dict(os.environ),log,timeout=180,cwd=ROOT)
            row['exit_code']=0
            return data.decode()
        finally:
            if log.is_file():
                row.update(log_sha256=digest(log),tail=log.read_text(errors='replace')[-1200:])
                log.unlink()
    def build_output(label,script,extra=()):
        if checked is None:
            output=command(label,[sys.executable,'-B',ROOT/script,*extra])
            if label=='owner':
                row=json.loads(output.splitlines()[-1]);path=Path(row['report']).parent
            else:
                if label=='producer' and cwd:
                    row=json.loads(output.splitlines()[-1]);path=Path(row['report']).parent
                    return_path=True
                else:
                    return_path=False
                fields=output.splitlines()[-1].split(' ',1)
                if not return_path:
                    if fields[0]!='pass' or len(fields)!=2:raise ValueError('provider did not pass')
                    path=Path(fields[1])
        else:
            path=Path(checked[label]).absolute()
            record['commands'].append(dict(label=label,action='consume-explicit-checked-output',path=str(path)))
        expected_parent=ROOT/('sys-init/out' if label=='owner' else 'userland/build')
        if path.parent!=expected_parent or path.is_symlink() or not path.is_dir():
            raise ValueError('unowned provider output')
        if checked is None:owned.append(path)
        report=json.loads((path/'results.json').read_text())
        if bool(report.get('cwd_wire',False))!=cwd:
            raise ValueError('provider CWD selection')
        if report['status']!='pass' or bool(report.get('path_wire',False))!=paths:
            raise ValueError('provider status/path selection')
        if label=='producer' and (report.get('profile')!='in-place' or bool(report.get('file16',False))!=dup2):
            raise ValueError('provider FILE geometry selection')
        if label in ('provider','owner') and bool(report.get('dup2_wire',False))!=dup2:
            raise ValueError('provider dup2 selection')
        if label=='provider' and (bool(report.get('path_probe',False))!=paths or not report.get('helper_sha256')):
            raise ValueError('provider fixed helper selection')
        checker=ROOT/script
        if report.get('checker_sha256',digest(checker))!=digest(checker):
            raise ValueError('provider checker drift')
        record['inputs'][str(checker)]=digest(checker)
        record.setdefault('reports',{})[label]=digest(path/'results.json')
        return path,report
    try:
        producer,q=build_output('producer','userland/experiments/filesystem-service/'+('check-directory-contexts.py' if cwd else 'check-process-descriptors.py'), [] if cwd else ['--in-place',*(['--paths'] if paths else []),*(['--replace','--file16'] if dup2 else [])])
        provider,p=build_output('provider','userland/experiments/filesystem-service/check-fork-stage.py',['--exec',*(['--paths','--path-probe'] if paths else []),*(['--dup2'] if dup2 else []),*(['--cwd'] if cwd else [])])
        owner,o=build_output('owner','sys-init/scripts/check-broker-init.py',
            ['--libraries',producer,'--compact-compare','--unified-route','--compose-owner','--guarded-stack','--exec-provider',provider,*(['--paths'] if paths else []),*(['--dup2'] if dup2 else []),*(['--cwd'] if cwd else [])])
        if (o.get('producer_result_sha256') != digest(producer/'results.json')
                or o.get('exec_provider',{}).get('report_sha256') != digest(provider/'results.json')):
            raise ValueError('guarded checked provider/owner association')
        record['measurement']=o['owner_measurement']
        if (record['measurement']['code_budget']!=49152 or not record['measurement']['code_fits'] or
                not record['measurement']['resident_fits'] or record['measurement']['stack']['status']!='pass'):
            raise ValueError('guarded owner fit')
        for report,base in ((q,ROOT/'userland/experiments/filesystem-service'),
                            (p,ROOT/'userland/experiments/filesystem-service'),(o,ROOT)):
            for name,expected in report['sources'].items():
                path=base/name
                if digest(path)!=expected:raise ValueError('changed guarded provider source')
                record['inputs'][str(path)]=expected
            for tool in report['tools'].values():record['tools'][tool['path']]=tool['sha256']
        record['inputs'][str(ROOT/'userland/experiments/filesystem-service/check-fork-stage.py')]=p['checker_sha256']
        record['inputs'][str(ROOT/'sys-init/scripts/check-broker-init.py')]=digest(ROOT/'sys-init/scripts/check-broker-init.py')
        zig=Path(p['aether_parser']['zig']['path'])
        record['tools'][str(zig)]=p['aether_parser']['zig']['sha256']
        record['tools'][sys.executable]=digest(sys.executable)
        record['rust_native_libraries']=o['rust_native_libraries']
        expected_artifacts={owner/'owner.elf':record['measurement']['elf_sha256'],
                            owner/'owner.bin':record['measurement']['raw_sha256'],
                            provider/'helper.elf':p['helper_sha256'],
                            provider/'shell.elf':p['complete_shell_link']['sha256']}
        if any(digest(path)!=expected for path,expected in expected_artifacts.items()):
            raise ValueError('checked artifact drift')
        for name,source in [('owner.elf',owner/'owner.elf'),('owner.bin',owner/'owner.bin'),
                            ('shell.elf',provider/'shell.elf'),('helper.elf',provider/'helper.elf')]:
            shutil.copyfile(source,destination/name)
        a=(destination/'shell.elf').read_bytes();b=(destination/'helper.elf').read_bytes()
        code=(destination/'owner.bin').read_bytes();e=(Path(engine_directory)/'filesystem.elf').read_bytes()
        nested=struct.pack('<8sIIIIQ',b'AENMX010',len(a),len(a),len(b),len(code),0)+bytes(range(80))+a+a+b+code
        envelope=struct.pack('<8sII',b'AENFS005',len(e),len(nested))+bytes(range(32))+e+nested
        (destination/'envelope.bin').write_bytes(envelope)
        (destination/'admit.zig').write_text('const std=@import("std");const c=@import("composition");test "actual selected guarded inputs"{const b=try c.parseOwnerStack(@embedFile("envelope.bin"));try std.testing.expectEqual(@as(usize,'+str(len(code))+'),b.session.supervisor.len);try std.testing.expectError(error.InvalidComposition,c.parseOwnerData(@embedFile("envelope.bin")));}')
        command('admit',['zig','test','--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
            '--dep','composition','-Mroot='+str(destination/'admit.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')])
        record['flags']=[*FLAGS,'native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']
        command('kernel',['zig','build','-p',destination/'build','--cache-dir',ROOT/'.zig-cache',
            '--global-cache-dir',ROOT/'.zig-cache/global','-Dsmp=false','-Dnative-c-image='+str(destination/'envelope.bin'),
            *['-D'+flag+'=true' for flag in record['flags']]])
        record['kernel_build']=dict(sha256=digest(destination/'build/bin/aether'),native_executed=False)
        for directory in ('kernel','scripts','user'):
            for path in (ROOT/directory).rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts and path.name!='.DS_Store':
                    record['inputs'][str(path)]=digest(path)
        record['inputs'][str(ROOT/'build.zig')]=digest(ROOT/'build.zig')
        for name,expected in record['inputs'].items():
            if digest(name)!=expected:raise ValueError('guarded input changed before publication')
        for name,expected in (record['tools'] | record['rust_native_libraries']).items():
            if digest(name)!=expected:raise ValueError('guarded tool/runtime changed before publication')
        if engine_intake(engine_directory,engine_seal)!=engine:raise ValueError('guarded engine changed')
        record['artifacts']={name:dict(bytes=(destination/name).stat().st_size,sha256=digest(destination/name))
            for name in ('owner.elf','owner.bin','shell.elf','helper.elf','envelope.bin')}
        record.update(status='prepared',scope='Active experimental inputs only; no native authority, execution, persistence or shell qualification')
    except BaseException as error:
        record.update(status='failed',error=str(error));raise
    finally:
        for path in owned:shutil.rmtree(path)
        shutil.rmtree(destination/'build',ignore_errors=True)
        (destination/'admit.zig').unlink(missing_ok=True)
        (destination/'inputs.json').write_text(json.dumps(record,indent=2)+'\n')
    paths=sorted(p for p in destination.iterdir() if p.is_file())
    (destination/'SHA256SUMS').write_text(''.join(digest(p)+'  '+p.name+'\n' for p in paths))
    return dict(directory=str(destination.relative_to(ROOT)),seal=digest(destination/'SHA256SUMS'),
                code_bytes=record['measurement']['code_bytes'],native_executed=False)


def main():
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            self.exit(64, 'af07-inputs: '+ascii(message)[1:-1]+'\n')
    parser = Parser(description=__doc__, epilog='Private active dependencies only. No VM, grant, runtime acceptance or released pin update.')
    parser.add_argument('--version', action='version', version='aether-af07-inputs 1')
    parser.add_argument('--engine-output', required=True, type=Path)
    parser.add_argument('--activation-output', required=True, type=Path)
    parser.add_argument('--guarded-output',type=Path,help='also prepare the current ABI31 owner/shell/helper input set')
    parser.add_argument('--paths',action='store_true',help='prepare separate AEFP0001 owner and fixed read-probe helper; requires --guarded-output')
    parser.add_argument('--dup2',action='store_true',help='prepare matched16-slot FILE/startup/public dup2 probe; requires --paths')
    parser.add_argument('--select', action='store_true', help='select both new experimental dependencies after successful verification')
    args = parser.parse_args()
    if args.dup2 and not args.paths:
        parser.error('--dup2 requires --paths')
    if args.paths and not args.guarded_output:
        parser.error('--paths requires --guarded-output')
    from fs_metadata_launch import build, destination_path
    destination_path(args.engine_output)
    output_path(args.activation_output,'fs-init-af07-')
    if args.guarded_output:output_path(args.guarded_output,'fs-owner-af07-')
    (ROOT/'zig-out').mkdir(exist_ok=True)
    selected = selection()
    selected['activation'] = activation(args.activation_output)
    result = build(args.engine_output)
    selected['engine'] = dict(directory=str(Path(result['elf']).parent.relative_to(ROOT)), seal=result['manifest_sha256'])
    if args.select:
        temporary = SELECTION.with_suffix('.tmp')
        if temporary.exists() or temporary.is_symlink():
            raise ValueError('selection publication conflict')
        temporary.write_text(json.dumps(selected, indent=2)+'\n')
        temporary.replace(SELECTION)
    output=dict(status='prepared',selection=selected,selected=args.select,native_executed=False)
    if args.guarded_output:
        output['guarded']=guarded(args.guarded_output,Path(result['elf']).parent,result['manifest_sha256'],paths=args.paths,dup2=args.dup2)
    print(json.dumps(output))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('[FAIL] '+ascii(str(error))[1:-1], file=sys.stderr)
        raise SystemExit(1)
