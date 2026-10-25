# SPDX-License-Identifier: BSD-2-Clause
"""Focused AF08 physical-directory checks; no native execution or pin update."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import platform
import sys
import tempfile
import types

class Parser(argparse.ArgumentParser):
    def error(self,message):
        self.print_usage(sys.stderr)
        self.exit(64,'[ERROR] '+ascii(message)[1:-1]+'\n')


parser=Parser(description=__doc__,epilog='Host/target checks only. Results schema aether-directory-context-check-v1 contains status/report; no native execution. Run from userland with python3 -B experiments/filesystem-service/check-directory-contexts.py.')
parser.add_argument('--version',action='version',version='aether-directory-context-check 1')
parser.parse_args()

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
ROOT = R.parent
P = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(P) == 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d'
pins = json.loads(P.read_text()); tools = pins['tools']
for tool in tools.values():
    assert sha(tool['path']) == tool['sha256']
for path, digest in pins['rust_native_libraries'].items():
    assert sha(path) == digest
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
ubsan=Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
assert sha(ubsan)=='7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
proc = types.ModuleType('owned'); exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-directory-contexts-', dir=R / 'build'))
env = proc.clean_env(W)
record = dict(status='incomplete', work=str(W), rows=[], sources={}, tools=tools,
              python=sys.version, host=platform.platform(), interpreter=dict(path=sys.executable,sha256=sha(sys.executable)), checker_sha256=sha(Path(__file__)), native_executed=False, profile='in-place', path_wire=True, file16=True, cwd=True, cwd_wire=True, rust_native_libraries=pins['rust_native_libraries'])


def run(label, argv, expected=0, timeout=60):
    child_env = dict(env)
    if any(str(argv[0]) == tools[name]['path'] for name in ('rustc', 'rustfmt', 'clippy-driver')):
        child_env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    child_env['AEFD_C_REQUESTS'] = str(W/'requests.bin')
    child_env['AEFD_RUST_REPLIES'] = str(W/'replies.bin')
    result = proc.run(list(map(str, argv)), cwd=R, env=child_env, work=W, label=label, timeout=timeout)
    row = dict(label=label, expected=expected, process=result.record,
               stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
               stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    record['rows'].append(row)
    if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
        row.update(stdout_tail=result.stdout.decode(errors='replace')[-1800:], stderr_tail=result.stderr.decode(errors='replace')[-1800:])
        raise RuntimeError(label)
    return result


def deps(directory, names):
    return ['-Ldependency='+str(directory), *[arg for name in names for arg in
            ('--extern', name+'='+str(directory/('lib'+name+'.rlib')))]]


try:
    for name,digest in pins['clang_resource_headers'].items():
        assert sha(name)==digest,name
    for path in [*S.glob('*.rs'), *S.glob('fd-*.c'), *S.glob('fd-*.h'), S/'directory-file-codec.c', S/'directory-context-fixture.c', S/'directory-context-engine-tests.c', ROOT/'user/storage/openzfs-volume/zpl-context.c', ROOT/'user/storage/openzfs-volume/zpl-context.inc', ROOT/'user/storage/openzfs-volume/zpl-context.h']:
        record['sources'][str(path)] = sha(path)
    checked_rust=['owner.rs','bridge.rs','service.rs','client.rs','remote-descriptors.rs','fd-protocol.rs','directory-context-tests.rs','directory-context-ffi-tests.rs']
    run('rustfmt',[tools['rustfmt']['path'],'--edition=2021','--check',*[S/name for name in checked_rust]])
    checked_c=[ROOT/'user/storage/openzfs-volume'/name for name in ('zpl-context.c','zpl-context.h','zpl-context.inc')] + [S/name for name in ('directory-context-engine-tests.c','directory-context-fixture.c','directory-file-codec.c','fd-protocol.h','fd-client.c','fd-context.c','fd-context.h','fd-libc-bindings.c','fd-libc-tests.c')]
    run('clang-format',[tools['clang-format']['path'],'--dry-run','--Werror','--style=file:'+str(R/'docs/quality/clang-format.yaml'),*checked_c])
    cflags = ['-std=c17', '-D_DEFAULT_SOURCE', '-Wall', '-Wextra', '-Werror', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all']
    run('engine-body-build', [tools['clang']['path'], *cflags, S/'directory-context-engine-tests.c', '-o', W/'engine-tests'])
    result = run('engine-body-tests', [W/'engine-tests'])
    assert b'24 scenarios pass' in result.stdout
    # Recover the pinned original-header recipe from the active dependency. Its
    # missing old per-run overlay dirs are not silently followed or recreated.
    receipt = ROOT/'.deps/fs-launch-af07-2026-10-23-v13/build.json'
    frozen = json.loads(receipt.read_text())
    old = next(c['argv'] for c in frozen['commands'] if '-c' in c['argv'] and any(str(a).endswith('/metadata-provider.o') for a in c['argv']))
    command = old[:old.index('-c')]
    missing = [a for a in command if a.startswith('-I/') and not Path(a[2:]).exists()]
    command = [a for a in command if a not in missing]
    record['original_header_recipe'] = dict(receipt_sha256=sha(receipt), omitted_missing_old_overlay_dirs=missing,
        scope='Compile against actual pinned engine headers; not a reproduced complete engine/runtime closure')
    run('original-header-build', [*command, '-MMD', '-MF', W/'context.d', '-c', ROOT/'user/storage/openzfs-volume/zpl-context.c', '-o', W/'context.o'])
    header_paths = (W/'context.d').read_text().replace('\\\n', ' ').split(':', 1)[1].split()
    record['original_header_inputs'] = {name:sha(name) for name in header_paths}
    record['original_context_object_sha256'] = sha(W/'context.o')
    flags = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
    for option in ('namespace','lifetimes','mixed','wait','bulk','runtime','activation','names','directories','metadata','directory_contexts','paths','process_views','cwd','cwd_wire','replace','file16','path_wire','dup2_wire','in_place'):
        flags += ['--cfg','fs_'+option]
    crates = [('filesystem_metadata','metadata-lib.rs',[]), ('filesystem_policy','owner.rs',['filesystem_metadata']),
              ('filesystem_service','service.rs',['filesystem_policy']), ('filesystem_client','client.rs',['filesystem_service']),
              ('filesystem_bridge','bridge.rs',['filesystem_policy','filesystem_metadata']),
              ('filesystem_activation','activation.rs',['filesystem_policy','filesystem_service']),
              ('filesystem_remote_descriptors','remote-descriptors.rs',['filesystem_client','filesystem_service']),
              ('filesystem_fd_protocol','fd-protocol.rs',['filesystem_client','filesystem_service','filesystem_remote_descriptors'])]
    for stage, native in [('host',False),('native',True)]:
        folder=W/stage;folder.mkdir()
        extra=['--target=x86_64-unknown-none','-Cpanic=abort','-Copt-level=2','-Crelocation-model=static','-Ccodegen-units=1'] if native else []
        for name, source, imports in crates:
            run(stage+'-'+name,[tools['rustc']['path'],*flags,*extra,*deps(folder,imports),
                *(['-Funsafe-code'] if name in ('filesystem_policy','filesystem_service','filesystem_fd_protocol','filesystem_activation') else []),
                '--crate-type=lib','--crate-name='+name,S/source,
                *(['--emit=link='+str(folder/('lib'+name+'.rlib'))+',obj='+str(folder/(name+'.o'))] if native else ['-o',folder/('lib'+name+'.rlib')])])
    def remove_cfg(original, names):
        return [value for i,value in enumerate(original) if value not in names and not (value=='--cfg' and i+1<len(original) and original[i+1] in names)]
    record['compatibility_rejections']=[]
    for stage in ('host','native'):
        old=remove_cfg(flags,{'fs_cwd_wire'})
        extra=['--target=x86_64-unknown-none','-Cpanic=abort'] if stage=='native' else []
        rejected=run(stage+'-reject-old-file-wire',[tools['rustc']['path'],*old,*extra,*deps(W/stage,['filesystem_client','filesystem_service','filesystem_remote_descriptors']),
            '--crate-type=lib','--crate-name=wrong_wire',S/'fd-protocol.rs','-o',W/(stage+'-wrong.rlib')],expected=1)
        assert b'E0080' in rejected.stderr and b'CWD requires' in rejected.stderr
        record['compatibility_rejections'].append(stage+'-old-FILE')
    rejected=run('reject-cwd-without-dup2',[tools['clang']['path'],*cflags,'-DAEFD_CWD_WIRE','-fsyntax-only',S/'directory-file-codec.c'],expected=1)
    assert b'AEFD_CWD_WIRE requires AEFD_DUP2_WIRE' in rejected.stderr
    record['compatibility_rejections'].append('C-CWD-without-dup2')
    record['native_library_sha256']=sha(W/'native/libfilesystem_remote_descriptors.rlib')
    for compiler in ('rustc','clippy-driver'):
        run(compiler+'-process-tests',[tools[compiler]['path'],*flags,*deps(W/'host',['filesystem_policy','filesystem_service','filesystem_client']),
            '--test',S/'remote-descriptors.rs','-o',W/(compiler+'-process-tests')])
    result=run('process-tests',[W/'rustc-process-tests','--test-threads=1'],timeout=30)
    record['process_tests_output']=result.stdout.decode()[-2000:]
    run('ffi-fixture-build',[tools['clang']['path'],*cflags,'-I'+str(ROOT/'user/storage/openzfs-volume'),'-I'+str(R/'experiments/native-utc'),'-c',S/'directory-context-fixture.c','-o',W/'ffi.o'])
    for compiler in ('rustc','clippy-driver'):
        run(compiler+'-ffi-tests',[tools[compiler]['path'],*flags,*deps(W/'host',['filesystem_policy','filesystem_bridge']),
            '--test',S/'directory-context-ffi-tests.rs','-Clink-arg='+str(W/'ffi.o'),'-Clink-arg=/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib','-Clink-arg=-Wl,-rpath,/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin','-o',W/(compiler+'-ffi-tests')])
    for compiler in ('rustc','clippy-driver'):
        run(compiler+'-entry-tests',[tools[compiler]['path'],*flags,*deps(W/'host',['filesystem_policy','filesystem_bridge','filesystem_service','filesystem_activation']),
            '--test',S/'native-service.rs','-Clink-arg='+str(W/'ffi.o'),'-Clink-arg='+str(ubsan),'-Clink-arg=-Wl,-rpath,'+str(ubsan.parent),'-o',W/(compiler+'-entry-tests')])
        run(compiler+'-native-entry',[tools[compiler]['path'],*flags,*deps(W/'native',['filesystem_policy','filesystem_bridge','filesystem_service','filesystem_activation']),
            '--target=x86_64-unknown-none','-Cpanic=abort','-Copt-level=2','-Crelocation-model=static','-Ccodegen-units=1',
            '--crate-type=lib','--crate-name=filesystem_native_service',S/'native-service.rs','--emit=obj','-o',W/(compiler+'-entry.o')])
    result=run('entry-tests',[W/'rustc-entry-tests','--test-threads=1'])
    record['entry_tests_output']=result.stdout.decode()[-2000:]
    run('native-service-link',[tools['lld']['path'],'-r',W/'rustc-entry.o',*[W/'native'/(name+'.o') for name in ('filesystem_metadata','filesystem_policy','filesystem_bridge','filesystem_service','filesystem_activation')],'-o',W/'filesystem-contexts.o'])
    symbols=run('native-service-symbols',[tools['nm']['path'],'--defined-only',W/'filesystem-contexts.o']).stdout.decode()
    assert sum(line.split()[-1:]==['aether_fs_metadata_run'] for line in symbols.splitlines())==1
    imports=run('native-service-imports',[tools['nm']['path'],'--undefined-only',W/'filesystem-contexts.o']).stdout.decode()
    assert 'aether_zpl_context' in imports
    record['native_service_object']=dict(sha256=sha(W/'filesystem-contexts.o'),imports=imports,protocol='AFSRPC08',executed=False)
    result=run('ffi-tests',[W/'rustc-ffi-tests','--test-threads=1'])
    record['ffi_tests_output']=result.stdout.decode()
    run('file-codec-build',[tools['clang']['path'],*cflags,'-DAEFD_PATH_WIRE','-DAEFD_DUP2_WIRE','-DAEFD_CWD_WIRE',S/'directory-file-codec.c','-o',W/'codec'])
    run('file-codec-requests',[W/'codec','emit',W/'requests.bin'])
    for compiler in ('rustc','clippy-driver'):
        run(compiler+'-context-tests',[tools[compiler]['path'],*flags,*deps(W/'host',['filesystem_policy','filesystem_service','filesystem_client','filesystem_remote_descriptors','filesystem_fd_protocol']),
                '-Funsafe-code','--test',S/'directory-context-tests.rs','-o',W/(compiler+'-tests')])
    result=run('context-tests',[W/'rustc-tests','--test-threads=1'],timeout=30)
    record['context_tests_output']=result.stdout.decode()[-2000:]
    run('file-codec-replies',[W/'codec','check',W/'replies.bin'])
    core=['fd-client','fd-facade','fd-routing','fd-table','fd-write','fd-pipe','fd-replace','fd-session','fd-redirect','fd-native','fd-context','fd-startup']
    selected=['-DAEFD_PATH_WIRE','-DAEFD_DUP2_WIRE','-DAEFD_CWD_WIRE']
    run('public-libc-binding-build',[tools['clang']['path'],*cflags,*selected,'-DAEFD_LIBC_HOST_TEST','-c',S/'fd-libc-bindings.c','-o',W/'bindings.o'])
    run('public-libc-build',[tools['clang']['path'],*cflags,*selected,*[S/(u+'.c') for u in core],S/'fd-libc.c',S/'fd-libc-tests.c',W/'bindings.o','-o',W/'libc'])
    result=run('public-libc-tests',[W/'libc'],timeout=30)
    assert b'104 actual libc binding host scenarios pass' in result.stdout
    record['libc_tests_output']=result.stdout.decode()
    controls = [
        ('context-right', 'directory-context-policy.rs', '!opened.rights.contains(Rights::READ)', 'false', 'policy_rejects_foreign_handles_missing_rights_and_files_before_provider'),
        ('context-retire', 'directory-context-policy.rs', 'self.retire();', 'let _ = ();', 'malformed_provider_context_is_zeroed_and_retires_owner'),
        ('context-version', 'directory-context-service.rs', 'raw[..8] != MAGIC[..]', 'false', 'service_rejects_old_version_reserved_tokens_and_rights_before_getter'),
        ('context-reserved', 'directory-context-service.rs', 'raw[32..].iter().any(|b| *b != 0)', 'false', 'service_rejects_old_version_reserved_tokens_and_rights_before_getter'),
        ('context-padding', 'directory-context-client.rs', 'frame[count..].iter().any(|b| *b != 0)', 'false', 'every_path_frame_loss_padding_and_malformed_path_retires_without_partial_output'),
        ('context-retire-client', 'client.rs', 'self.shutdown();\n        Err(error)', 'Err(error)', 'every_path_frame_loss_padding_and_malformed_path_retires_without_partial_output'),
        ('file-version', 'fd-protocol.rs', 'raw[..8] != MAGIC[..]', 'false', 'bad_file_version_reserved_bytes_body_padding_and_lost_reply_retire'),
        ('file-padding', 'fd-protocol.rs', 'workspace[word(raw, 5) as usize..needed]\n                    .iter()\n                    .any(|&b| b != 0)', 'false', 'bad_file_version_reserved_bytes_body_padding_and_lost_reply_retire'),
        ('file-drop', 'fd-protocol.rs', 'self.connection.abort(self.files);', 'let _ = &mut self.files; self.workspace.fill(0);', 'bad_file_version_reserved_bytes_body_padding_and_lost_reply_retire'),
    ]
    record['semantic_controls']=[]
    for label, file, old, new, test in controls:
        folder=W/label;folder.mkdir()
        source=folder/'source';source.mkdir()
        for path in S.glob('*.rs'):
            contents=path.read_text()
            if path.name==file:
                assert contents.count(old)==1,(label,old)
                contents=contents.replace(old,new,1)
            (source/path.name).write_text(contents)
        (source/'vendor').mkdir()
        shutil.copy2(S/'vendor/abi29-startup.rs',source/'vendor/abi29-startup.rs')
        for name, file, imports in crates:
            if name=='filesystem_bridge':continue
            run(label+'-'+name,[tools['rustc']['path'],*flags,*deps(folder,imports),
                '--crate-type=lib','--crate-name='+name,source/file,'-o',folder/('lib'+name+'.rlib')])
        run(label+'-build',[tools['rustc']['path'],*flags,*deps(folder,['filesystem_policy','filesystem_service','filesystem_client','filesystem_remote_descriptors','filesystem_fd_protocol']),
            '-Funsafe-code','--test',source/'directory-context-tests.rs','-o',folder/'tests'])
        rejected=run(label+'-reject',[folder/'tests','--exact',test,'--nocapture'],expected=101,timeout=15)
        assert b'1 failed' in rejected.stdout and b'assertion' in rejected.stderr and test.encode() in rejected.stdout,label
        record['semantic_controls'].append(dict(label=label,test=test))
    for name,digest in record['sources'].items():
        assert sha(name)==digest,name
    for tool in tools.values():
        assert sha(tool['path'])==tool['sha256']
    for name,digest in (pins['rust_native_libraries'] | pins['clang_resource_headers'] | record['original_header_inputs']).items():
        assert sha(name)==digest,name
    assert sha(ubsan)=='7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
    assert sha(Path(__file__))==record['checker_sha256']
    record['status']='pass'
except BaseException as error:
    record.update(status='failed',error=repr(error));raise
finally:
    (W/'results.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(schema='aether-directory-context-check-v1',status=record['status'],report=str(W/'results.json'))))
