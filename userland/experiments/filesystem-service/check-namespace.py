# SPDX-License-Identifier: BSD-2-Clause
"""Offline host/object namespace service checks; never launches a guest."""
import ast
import hashlib
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
import types
import time

if sys.argv[1:] not in ([], ['--mixed'], ['--mixed-wait'], ['--bulk'], ['--runtime'], ['--activation'], ['--names'], ['--directories']):
    print('usage: check-namespace.py [--mixed|--mixed-wait|--bulk|--runtime|--activation|--names|--directories]',file=sys.stderr)
    raise SystemExit(64)
directories = sys.argv[1:] == ['--directories']
names = directories or sys.argv[1:] == ['--names']
activation = names or sys.argv[1:] == ['--activation']
runtime = activation or sys.argv[1:] == ['--runtime']
bulk = runtime or sys.argv[1:] == ['--bulk']
waiting = bulk or sys.argv[1:] == ['--mixed-wait']
mixed = waiting or sys.argv[1:] == ['--mixed']
OBJECT = 'filesystem-directories.o' if directories else 'filesystem-names.o' if names else 'filesystem-activation.o' if activation else 'filesystem-runtime.o' if runtime else 'filesystem-bulk.o' if bulk else 'filesystem-mixed-wait.o' if waiting else 'filesystem-mixed.o' if mixed else 'filesystem-namespace.o'
ENTRY = 'aether_fs_directories_run' if directories else 'aether_fs_names_run' if names else 'aether_fs_activation_run' if activation else 'aether_fs_runtime_run' if runtime else 'aether_fs_bulk_run' if bulk else 'aether_fs_mixed_wait_run' if waiting else 'aether_fs_mixed_run' if mixed else 'aether_fs_namespace_run'
HEADER = 'directories-service.h' if directories else 'names-service.h' if names else 'activation-service.h' if activation else 'runtime-service.h' if runtime else 'bulk-service.h' if bulk else 'mixed-wait-service.h' if waiting else 'mixed-service.h' if mixed else 'namespace-service.h'
S = Path(__file__).resolve().parent
R = S.parents[1]
AETHER = R.parent
INPUTS = S / ('directories-inputs.json' if directories else 'runtime-inputs.json' if runtime else 'bulk-inputs.json' if bulk else 'mixed-wait-inputs.json' if waiting else 'mixed-inputs.json' if mixed else 'namespace-inputs.json')
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
inputs = json.loads(INPUTS.read_text())
for name, digest in inputs['engine_files'].items():
    assert sha(AETHER / name) == digest, name
prior = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
assert sha(prior) == inputs['transport_inputs_sha256']
prior_inputs = json.loads(prior.read_text())
tools = prior_inputs['tools']
dependency_inputs = prior_inputs['rust_native_libraries'] | prior_inputs['clang_resource_headers']
for name,digest in dependency_inputs.items():assert sha(name)==digest,name
for item in tools.values():
    assert sha(item['path']) == item['sha256']
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('namespace_owned_process')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-runtime-' if runtime else 'filesystem-bulk-' if bulk else 'filesystem-mixed-wait-' if waiting else 'filesystem-mixed-' if mixed else 'filesystem-namespace-', dir=R/'build'))
rows = []
sources = {str(f.relative_to(R)): sha(f) for f in S.iterdir() if f.suffix in ('.rs','.c','.h','.py','.json')}
record = dict(status='running', root=str(W), sources=sources, inputs=inputs,
              rows=rows, native_executed=False, full_engine_linked=False, mixed=mixed, waiting=waiting, bulk=bulk, runtime=runtime, activation=activation, names=names, directories=directories, dependency_inputs=dependency_inputs)
env = {'PATH':'/usr/bin:/bin', 'HOME':str(W), 'TMPDIR':str(W)}


def run(label, args, expected=0):
    argv = list(map(str,args)); start=time.monotonic()
    selected = ({**env, 'DYLD_LIBRARY_PATH':str(Path(tools['rustc']['path']).parent.parent/'lib')}
                if Path(argv[0]).name in ('rustc','rustfmt','clippy-driver') else env)
    r = proc.run(argv, cwd=R, env=selected, work=W, label=label, timeout=60)
    out = r.stdout+r.stderr
    rows.append(dict(name=label, argv=argv, exit_code=r.returncode, expected=expected,
        seconds=round(time.monotonic()-start,3), process=r.record, sha256=hashlib.sha256(out).hexdigest(),
        tail=out.decode(errors='replace')[-5000:]))
    (W/'results.json').write_text(json.dumps(record,indent=2)+'\n')
    assert r.returncode==expected and r.record['complete'] and r.record['cleanup']=='complete', (label,out.decode(errors='replace')[-8000:])
    return r


COMMON = ['--edition=2021','-Dwarnings','-Dunsafe_op_in_unsafe_fn','--cfg','fs_namespace'] + (['--cfg','fs_lifetimes','--cfg','fs_mixed'] if mixed else []) + (['--cfg','fs_wait'] if waiting else []) + (['--cfg','fs_bulk'] if bulk else []) + (['--cfg','fs_runtime'] if runtime else []) + (['--cfg','fs_activation'] if activation else []) + (['--cfg','fs_names'] if names else []) + (['--cfg','fs_directories'] if directories else [])
CRATES = [('filesystem_policy','owner.rs',[]),
          ('filesystem_bridge','bridge.rs',['filesystem_policy']),
          ('filesystem_service','service.rs',['filesystem_policy'])] + ([('filesystem_activation','activation.rs',['filesystem_policy','filesystem_service'])] if activation else [])


def dependencies(directory, names):
    args = ['-Ldependency='+str(directory)]
    for name in names:args += ['--extern',name+'='+str(directory/('lib'+name+'.rlib'))]
    return args


def host(directory, label, lint=True, fixture=None):
    for name,source,deps in CRATES:
        run(label+'-'+name,[tools['rustc']['path'],*COMMON,
            *dependencies(directory,deps),*(['-Funsafe-code'] if name!='filesystem_bridge' else []),'--crate-name='+name,'--crate-type=lib',
            directory/source,'-o',directory/('lib'+name+'.rlib')])
    dep = dependencies(directory,[c[0] for c in CRATES])
    for name,tool in [('tests','rustc'),('clippy','clippy-driver')]:
        if name=='clippy' and not lint:continue
        run(label+'-'+name,[tools[tool]['path'],*COMMON,*dep,'--test',directory/'native-service.rs',
            '-Clink-arg='+str(fixture or W/'fixture.o'),'-o',directory/name])


try:
    for name in sources:
        source=R/name
        if source.suffix in ('.rs','.c','.h','.py','.json'):
            shutil.copyfile(source,W/source.name)
    rust_sources=[S/n for n in ('owner.rs','bridge.rs','service.rs','native-service.rs',
                  'namespace-policy.rs','namespace-bridge.rs','namespace-service-tests.rs',
                  *(['mixed-bridge.rs','mixed-service-tests.rs','created-identity-tests.rs'] if mixed else []), *(['channel.rs'] if waiting else []), *(['bulk-service.rs','bulk-service-tests.rs'] if bulk else []), *(['runtime-service-tests.rs','runtime-counter-tests.rs','runtime-bridge-tests.rs'] if runtime else []), *(['activation.rs','activation-tests.rs'] if activation else []), *(['names-service.rs','names-service-tests.rs'] if names else []), *(['directory-bridge.rs','directory-service-tests.rs'] if directories else []))]
    run('rustfmt',[tools['rustfmt']['path'],'--edition=2021','--check',*rust_sources])
    run('c-format',[tools['clang-format']['path'],'--dry-run','--Werror',
        '--style=file:docs/quality/clang-format.yaml',S/('directory-fixture.c' if directories else 'runtime-fixture.c' if runtime else 'bulk-fixture.c' if bulk else 'mixed-fixture.c' if mixed else 'namespace-fixture.c'),S/HEADER])
    sdk=run('host-sdk',['/usr/bin/xcrun','--show-sdk-path']).stdout.decode().strip()
    record['host_sdk']=sdk
    headers=AETHER/'user/storage/openzfs-volume'
    utc=R/'docs/evidence/filesystem-bridge-2026-10-18'
    run('typed-c-fixture',[tools['clang']['path'],'-isysroot',sdk,'-std=c17',
        '-Wall','-Wextra','-Werror','-I'+str(headers),'-I'+str(utc),'-I'+str(S),
        *(['-DAETHER_FS_NAMES'] if names else []),'-c',S/('directory-fixture.c' if directories else 'runtime-fixture.c' if runtime else 'bulk-fixture.c' if bulk else 'mixed-fixture.c' if mixed else 'namespace-fixture.c'),'-o',W/'fixture.o'])
    host(W,'namespace')
    if activation:
        run('activation-wrapper-codegen',[tools['rustc']['path'],*COMMON,*dependencies(W,['filesystem_policy','filesystem_service']),'-Funsafe-code','--test',W/'activation.rs','-o',W/'activation-tests'])
        run('activation-wrapper-tests',[W/'activation-tests','--test-threads=1'])
    if runtime:
        run('runtime-policy-counter-codegen',[tools['rustc']['path'],*COMMON,'--test',W/'owner.rs','-o',W/'policy-counters'])
        run('runtime-policy-counters',[W/'policy-counters','--test-threads=1'])
        run('runtime-bridge-counter-codegen',[tools['rustc']['path'],*COMMON,*dependencies(W,['filesystem_policy']),
            '--test',W/'bridge.rs','-Clink-arg='+str(W/'fixture.o'),'-o',W/'bridge-counters'])
        run('runtime-bridge-counters',[W/'bridge-counters','--test-threads=1'])
    observed=run('namespace-tests',[W/'tests','--test-threads=1'])
    assert ('23 passed; 0 failed' if directories else '29 passed; 0 failed' if names else '21 passed; 0 failed' if activation else '18 passed; 0 failed' if runtime else '16 passed; 0 failed' if bulk else '20 passed; 0 failed' if waiting else '17 passed; 0 failed' if mixed else '8 passed; 0 failed') in observed.stdout.decode()
    if runtime:
        for omit in (False,True):
            folder=W/('request-overflow-omitted' if omit else 'request-overflow');folder.mkdir()
            for f in W.glob('*.rs'):
                body=f.read_text()
                if f.name==('names-service.rs' if names else 'bulk-service.rs'):
                    assert body.count('let mut requests = 0usize;')==1
                    body=body.replace('let mut requests = 0usize;','let mut requests = usize::MAX - 1;')
                    if omit:body=body.replace('requests.checked_add(1)','Some(requests.wrapping_add(1))')
                (folder/f.name).write_text(body)
            host(folder,folder.name,lint=False)
            dep=dependencies(folder,[c[0] for c in CRATES])
            run(folder.name+'-probe-codegen',[tools['rustc']['path'],*COMMON,'--cfg','runtime_request_probe',*dep,
                '--test',folder/'native-service.rs','-Clink-arg='+str(W/'fixture.o'),'-o',folder/'probe'])
            probe=run(folder.name+'-probe',[folder/'probe','tests::request_counter_exhaustion_closes_before_next_provider_effect','--exact','--test-threads=1'],expected=101 if omit else 0)
            assert ('RUNTIME_REQUEST_OVERFLOW' in probe.stdout.decode()) if omit else ('1 passed; 0 failed' in probe.stdout.decode())
    mutants={
        'directory-right':[('namespace-policy.rs','!parent.rights.contains(Rights::MUTATE_DIR)','false')],
        'remove-alias':[('namespace-policy.rs','if removing\n','if false && removing\n')],
        'shared-budget':[('namespace-policy.rs','if self.write_used {','if false {')],
        'close-before-reply':[('namespace-policy.rs','        #[cfg(not(fs_mixed))]\n        self.retire();','        // deliberately omitted one-attempt retirement')],
        'original-progress':[('service.rs','            put(&mut reply, 4, value.txg);','            put(&mut reply, 4, 0);')],
    }
    if mixed:
        mutants.update({
            'shared-budget':[('namespace-policy.rs','            self.writes += 1;','            // omitted shared namespace attempt')],
            'close-before-reply':[('mixed-bridge.rs','        unsafe { aether_zpl_close(&mut owned) };','        if !owned.is_null() { owned = core::ptr::null_mut(); } if false { unsafe { aether_zpl_close(&mut owned) }; }')],
            'root-cache':[('namespace-policy.rs','                    self.root = root;','                    // omitted cached root publication')],
            'failed-current-progress':[('service.rs','            if dispatched','            if (false && dispatched)')],
        })
    if waiting:
        mutants.update({
            'wait-omitted':[('channel.rs','let status = self.0.wait(writing);','let status = 0;')],
            'wait-error':[('channel.rs','if status != 0 {','if false && status != 0 {')],
            'wait-offset':[('channel.rs','offset += count as usize;','offset += 0 * count as usize;')],
            'wait-clear':[('channel.rs','                        bytes.fill(0);','                        // omitted error-frame clearing')],
        })
    if bulk:
        mutants['failed-current-progress']=[('bulk-service.rs','            if dispatched','            if false && dispatched')]
        mutants.update({
            'body-before-dispatch':[('bulk-service.rs','receive_body(&mut channel, &mut body, length)','if false { receive_body(&mut channel, &mut body, length) } else { Ok::<(), i64>(()) }')],
            'body-padding':[('bulk-service.rs','if frame[count..].iter().any(|b| *b != 0) {','if false && frame[count..].iter().any(|b| *b != 0) {')],
            'read-body':[('bulk-service.rs','send_body(&mut channel, &body[..word(&reply, 5) as usize])','if false { send_body(&mut channel, &body[..word(&reply, 5) as usize]) } else { Ok::<(), i64>(()) }')],
            'length-retirement':[('mixed-bridge.rs','bytes.len() as u64','4096 + 0 * bytes.len() as u64')],
        })
    if runtime:
        mutants.pop('shared-budget')
        mutants.update({
            'runtime-policy-width':[('owner.rs','pub type MutationCount = usize;','pub type MutationCount = u8;')],
            'runtime-bridge-eight':[('namespace-bridge.rs','if self.consumed || self.writes == policy::MUTATION_LIMIT {\n                return Ok(Completion {','if self.consumed || self.writes == 8 {\n                return Ok(Completion {')],
        })
    if activation:
        mutants.update({
            'activation-skip-publish':[('activation.rs','let status = (self.publish)();','let status = 0; if false { (self.publish)(); }')],
            'activation-ignore-error':[('activation.rs','if status != 0 {','if false && status != 0 {')],
            'activation-late-publish':[('activation.rs','let status = (self.publish)();','self.inner.send(frame)?; let status = (self.publish)();')],
        })
    if names:
        for label in ('failed-current-progress','body-before-dispatch','read-body'):
            mutants[label]=[('names-service.rs',old,new) for _,old,new in mutants[label]]
        mutants['original-progress']=[('names-service.rs','put(&mut reply, 4, value.txg);','put(&mut reply, 4, 0);')]
        mutants.update({
            'names-limit':[('names-service.rs','first > 255','first > 16')],
            'names-before-effect':[('names-service.rs','first + second)','0 * first + 0 * second)')],
            'names-inline':[('names-service.rs','raw[48..].iter().any(|byte| *byte != 0)','false')],
            'names-policy-cap':[('namespace-policy.rs','if cfg!(fs_names) { 255 } else { 16 }','16')],
            'names-second-cap':[('names-service.rs','second > 255','second > 16')],
        })
    if directories:
        # Exercise controls against this profile's actual-entry cases. Existing
        # qualified AF05/activation omissions retain their separate coverage.
        mutants = {label:replacements for label,replacements in mutants.items()
            if label in ('directory-right','remove-alias','original-progress',
                         'close-before-reply','root-cache','wait-omitted',
                         'wait-error','wait-offset','wait-clear',
                         'body-before-dispatch','body-padding','read-body',
                         'length-retirement','names-limit','names-before-effect',
                         'names-inline','names-policy-cap','names-second-cap',
                         'activation-skip-publish','activation-ignore-error',
                         'activation-late-publish','runtime-policy-width',
                         'runtime-bridge-eight')}
        mutants.update({
            'actual-parent-refresh':[('namespace-policy.rs',
                '.directory(parent.node)', '.root()')],
            'directory-generation':[('directory-bridge.rs',
                'current.identity() != directory.identity()', 'false'),
                ('namespace-policy.rs','&& root.identity() == parent.node.identity()', '')],
        })
    if mixed:
        mutants.update({
            'created-identity':[('namespace-policy.rs','node.identity() != expected.identity()', 'false')],
            'created-progress':[('namespace-policy.rs','let progress = result.map(|value| value.completion);', 'let progress = result.map(|value| Completion { txg: 0, ..value.completion });')],
            'created-capacity':[('namespace-policy.rs','.position(Option::is_none)', '.position(|_| true)')],
            'created-parent-aliases':[('namespace-policy.rs','self.root = refreshed;', '// omitted created parent cache'), ('namespace-policy.rs','open.node = refreshed;', '// omitted created parent aliases')],
        })
    for label,replacements in mutants.items():
        folder=W/label;folder.mkdir()
        for f in W.glob('*.rs'):
            text=f.read_text()
            for name,old,new in replacements:
                if f.name==name:
                    assert text.count(old)==1,(label,old)
                    text=text.replace(old,new,1)
            (folder/f.name).write_text(text)
        host(folder,label,lint=False)
        rejected=run('reject-'+label,[folder/'tests','--test-threads=1'],expected=101)
        assert 'test result: FAILED.' in rejected.stdout.decode()
    n=W/'native';n.mkdir()
    native=['--target=x86_64-unknown-none','-Cpanic=abort','-Copt-level=2',
            '-Crelocation-model=static','-Ccodegen-units=1']
    for name,source,deps in [*CRATES,('filesystem_native_service','native-service.rs',[c[0] for c in CRATES])]:
        for label,tool in [('object','rustc'),('clippy','clippy-driver')]:
            run('native-'+label+'-'+name,[tools[tool]['path'],*COMMON,*native,
                *dependencies(n,deps),*(['-Funsafe-code'] if name in ('filesystem_policy','filesystem_service','filesystem_activation') else []),'--crate-name='+name,'--crate-type=lib',S/source,
                '--emit=link='+str(n/('lib'+name+'.rlib'))+',obj='+str(n/(name+'.o'))])
    run('native-link',[tools['lld']['path'],'-r',*sorted(n.glob('*.o')),'-o',W/OBJECT])
    definitions=run('native-symbols',[tools['nm']['path'],'--defined-only',W/OBJECT]).stdout.decode()
    imports=run('native-imports',[tools['nm']['path'],'--undefined-only',W/OBJECT]).stdout.decode()
    assert sum(line.split()[-1:]==[ENTRY] for line in definitions.splitlines())==1
    assert not any(line.split()[-1:]==['aether_fs_service_run'] for line in definitions.splitlines())
    for name in ('aether_zpl_open_write','aether_zpl_close','aether_zpl_root','aether_zpl_lookup',
                 'aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename',
                 'aether_zpl_remove','aether_utc_read'):
        assert name in imports,name
    if directories:
        for symbol in ('aether_zpl_directory','aether_zpl_mkdir','aether_zpl_rmdir'):
            assert symbol in imports,symbol
    if mixed:
        assert 'aether_pool_namespace0_retire' in imports and ('aether_pool_service_bytes_retire' if bulk else 'aether_pool_service16_retire') in imports
        assert 'aether_pool_lifetime_retire' not in imports
        assert not any(line.split()[-1:]==['aether_fs_namespace_run'] for line in definitions.splitlines())
    else:assert '_retire' not in imports
    if names:
        assert not any(line.split()[-1:]==['aether_fs_activation_run'] for line in definitions.splitlines())
    if activation:
        assert not any(line.split()[-1:]==['aether_fs_runtime_run'] for line in definitions.splitlines())
    if runtime:
        assert not any(line.split()[-1:]==['aether_fs_bulk_run'] for line in definitions.splitlines())
    if bulk:
        assert 'aether_pool_service16_retire' not in imports
        assert not any(line.split()[-1:]==['aether_fs_mixed_wait_run'] for line in definitions.splitlines())
    if waiting:
        assert not any(line.split()[-1:]==['aether_fs_mixed_run'] for line in definitions.splitlines())
    layout=W/'layout.c'
    layout.write_text('#include "'+HEADER+'"\n' +
        '_Static_assert(sizeof(struct aether_fs_service_result)==72,"size");\n'
        '_Static_assert(_Alignof(struct aether_fs_service_result)==8,"align");\n'
        '_Static_assert(offsetof(struct aether_fs_service_result,txg)==48,"txg");\n'
        'int (*entry)(void*,const unsigned char*,size_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,struct aether_fs_service_result*)='+ENTRY+';\n')
    run('native-c-layout',[tools['clang']['path'],'--target=x86_64-unknown-none','-ffreestanding',
        '-std=c17','-Wall','-Wextra','-Werror','-I'+str(S),'-c',layout,'-o',W/'layout.o'])
    packed=run('native-c-packed-reject',[tools['clang']['path'],'--target=x86_64-unknown-none',
        '-ffreestanding','-std=c17','-fpack-struct=1','-I'+str(S),'-c',layout,'-o',W/'bad-layout.o'],expected=1)
    assert 'static assertion failed' in packed.stderr.decode()
    if activation:
        for label,old,new,oracle in (
            ('activation-greeting','word(frame, 2) != self.epoch','false','ACTIVATION_GREETING'),
            ('activation-retry','if self.failed {','if false && self.failed {','ACTIVATION_NO_RETRY'),
        ):
            changed=(W/'activation.rs').read_text();assert changed.count(old)==1
            source=W/(label+'.rs');source.write_text(changed.replace(old,new,1))
            run(label+'-codegen',[tools['rustc']['path'],*COMMON,*dependencies(W,['filesystem_policy','filesystem_service']),'-Funsafe-code','--test',source,'-o',W/label])
            rejection=run(label,[W/label,'--test-threads=1'],expected=101)
            assert oracle in rejection.stdout.decode(),label
        legacy=W/'legacy-runtime';legacy.mkdir()
        for source in W.glob('*.rs'):shutil.copyfile(source,legacy/source.name)
        original_common=COMMON
        COMMON=[value for index,value in enumerate(COMMON) if value not in ('fs_activation','fs_names','fs_directories') and not(value=='--cfg' and index+1<len(COMMON) and COMMON[index+1] in ('fs_activation','fs_names','fs_directories'))]
        try:
            legacy_fixture = None
            if directories:
                legacy_fixture = W/'legacy-fixture.o'
                args = next(row['argv'] for row in rows if row['name']=='typed-c-fixture')
                args = [str(S/'runtime-fixture.c') if value==str(S/'directory-fixture.c') else
                        str(legacy_fixture) if value==str(W/'fixture.o') else value
                        for value in args if value!='-DAETHER_FS_NAMES']
                run('legacy-typed-c-fixture', args)
            host(legacy,'legacy-runtime',lint=False,fixture=legacy_fixture)
            legacy_tests=run('legacy-runtime-tests',[legacy/'tests','--test-threads=1'])
            assert '18 passed; 0 failed' in legacy_tests.stdout.decode()
            for name,source,deps in [*CRATES[:3],('filesystem_native_service','native-service.rs',[c[0] for c in CRATES[:3]])]:
                for label,tool in [('object','rustc'),('clippy','clippy-driver')]:
                    run('legacy-native-'+label+'-'+name,[tools[tool]['path'],*COMMON,*native,*dependencies(legacy,deps),*(['-Funsafe-code'] if name in ('filesystem_policy','filesystem_service') else []),'--crate-name='+name,'--crate-type=lib',S/source,'--emit=link='+str(legacy/('lib'+name+'.rlib'))+',obj='+str(legacy/(name+'.o'))])
            run('legacy-native-link',[tools['lld']['path'],'-r',*sorted(legacy.glob('*.o')),'-o',legacy/'filesystem-runtime.o'])
            expected='c83c527993738d87be0293ef71175a6cb5b40e4093e86b5c1e6a7aab7ff1205a'
            observed=sha(legacy/'filesystem-runtime.o')
            record['legacy_runtime']=dict(entry_tests=18,object_sha256=observed,prior_object_sha256=expected,exact_object=observed==expected)
            prior=R/'build/service-deliveries/filesystem-service-runtime-2026-10-20-v1/objects/filesystem-runtime.o'
            assert sha(prior)==expected
            # Compare the entire original file, masking only LLVM bitcode. This
            # is object-code compatibility, not a bitcode/LTO or native replay.
            normalized=[]
            for label,obj in [('prior',prior),('live',legacy/'filesystem-runtime.o')]:
                table=run('legacy-sections-'+label,[tools['readelf']['path'],'-SW',obj]).stdout.decode()
                matches=re.findall(r'\]\s+\.llvmbc\s+PROGBITS\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',table)
                assert len(matches)==1
                offset,length=(int(v,16) for v in matches[0]);data=bytearray(obj.read_bytes())
                assert offset>0 and length>0 and offset+length<=len(data)
                data[offset:offset+length]=bytes(length);normalized.append(data)
            assert len(normalized)==2
            # Active source line metadata can change while old seals remain exact.
            record['legacy_runtime']['non_bitcode_object_exact']=normalized[0]==normalized[1]
            record['legacy_runtime']['limitation']='Active source/panic locations and embedded bitcode may differ; old sealed bytes are unchanged. Host legacy behavior passes; no fresh legacy native or LTO reproduction claimed.'

        finally:COMMON=original_common
    for name,digest in sources.items():assert sha(R/name)==digest,name
    for name,digest in inputs['engine_files'].items():assert sha(AETHER/name)==digest,name
    for name,digest in dependency_inputs.items():assert sha(name)==digest,name
    for item in tools.values():assert sha(item['path'])==item['sha256']
    record.update(status='pass',entry_tests=23 if directories else 29 if names else 21 if activation else 18 if runtime else 16 if bulk else 20 if waiting else 17 if mixed else 8,semantic_omissions=len(mutants)+(2 if activation else 0),
        imports=imports,object_sha256=sha(W/OBJECT))
except BaseException as error:
    record.update(status='failed',error=repr(error))
    raise
finally:
    (W/'results.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Filesystem namespace check:',record['status'],W)
