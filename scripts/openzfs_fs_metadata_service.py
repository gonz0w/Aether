# SPDX-License-Identifier: BSD-2-Clause
"""Separate AF07 intake and checked consuming source selection; no default repin."""
import json
from pathlib import Path
import re
import shutil

from deps import ROOT
from fs_launch import origins, recipe
from fs_launch_intake import digest
from service_runtime_smoke import sealed

SEAL = '98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8'
OBJECT = 'b5729862346409392064045af6f953484d3d6fbf9cad2b279840907003222f7b'
DELIVERY = ROOT / 'userland/build/service-deliveries/filesystem-service-metadata-2026-10-21-v1'
VOLUME = ROOT/'user/storage/openzfs-volume'
SERVICE = ROOT/'user/storage/service-runtime'
CASES = ('normal', 'lost-reply', 'partial-request', 'close-failure')
METADATA_REPLIES = ('metadata-header-loss', 'metadata-first-body-loss', 'metadata-second-body-loss')
METADATA_PROVIDERS = ('metadata-nanos', 'metadata-identity', 'metadata-errno', 'metadata-completion')
FAILURE_GROUPS = dict(inherited=CASES[1:], replies=METADATA_REPLIES,
                      providers=METADATA_PROVIDERS, retirement=('metadata-nanos',))


def validate_case(case):
    if type(case) is not str or case not in CASES+METADATA_REPLIES+METADATA_PROVIDERS:
        raise ValueError('AF07 requires a fixed failure case')
    return case


def intake(delivery=DELIVERY):
    root = Path(delivery).absolute()
    members = sealed(root, SEAL, 77)
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('AF07 member symlink')
        if path.is_file(): actual.add(str(path.relative_to(root)))
    if actual != members.keys() | {'SHA256SUMS'}:
        raise ValueError('AF07 member closure')
    if members.get('objects/filesystem-metadata.o') != OBJECT:
        raise ValueError('AF07 object identity')
    record = json.loads((root/'inputs.json').read_text())
    build = json.loads((root/'build.json').read_text())
    if (record.get('format') != 'aether-userland-af07-inputs-v1'
            or any(build.get(k,{}).get('status') != 'pass' for k in ('minimum','current'))
            or build.get('native_executed') is not False or build.get('full_engine_linked') is not False):
        raise ValueError('AF07 host/object scope')
    inputs = {str(root/'SHA256SUMS'): SEAL, **{str(root/n):h for n,h in members.items()}}
    source_hashes = {Path(name).name:checksum for name,checksum in record['sources'].items()}
    if len(source_hashes) != len(record['sources']):
        raise ValueError('AF07 ambiguous source names')
    required = {'owner.rs','bridge.rs','service.rs','native-service.rs','activation.rs',
                'metadata.rs','metadata-lib.rs','metadata-policy.rs','metadata-service.rs',
                'metadata-service.h','namespace-policy.rs','namespace-bridge.rs',
                'directory-bridge.rs','names-service.rs','bulk-service.rs','channel.rs','mixed-bridge.rs'}
    if not required <= {p.name for p in (root/'source').iterdir()}:
        raise ValueError('AF07 missing runtime source')
    # The producer records a wider checkout inventory than its57 source snapshots.
    # Omitted ancillary checkers/old launch-owner are not selected by this entry.
    for path in (root/'source').iterdir():
        checksum = source_hashes.get(path.name)
        if digest(path) != checksum:
            raise ValueError('AF07 source snapshot: '+path.name)
    for name, checksum in record['change']['engine_headers'].items():
        if digest(VOLUME/name) != checksum or digest(root/'ffi'/name) != checksum:
            raise ValueError('AF07 engine header: '+name)
        inputs[str(VOLUME/name)] = checksum
    engine = record['change']['producer']
    for name in ('user/storage/openzfs-volume/zpl-metadata.c',
                 'scripts/openzfs_volume.py','scripts/openzfs_fs_service.py'):
        if digest(ROOT/name) != engine[name]:
            raise ValueError('AF07 engine prerequisite: '+name)
        inputs[str(ROOT/name)] = engine[name]
    old = record['inherited_af06_inputs']
    for key in ('producer_namespace_files','producer_directory_files',
                'producer_mixed_retirement_files','producer_bulk_retirement_files','producer_wait_files'):
        for name, checksum in old[key].items():
            if digest(ROOT/name) != checksum:
                raise ValueError('AF07 inherited engine closure: '+name)
            inputs[str(ROOT/name)] = checksum
    for name, checksum in ({v['path']:v['sha256'] for v in record['tools'].values()}
            | record['rust_native_libraries'] | record['clang_resource_headers']).items():
        if not Path(name).is_absolute() or digest(Path(name)) != checksum:
            raise ValueError('AF07 tool/dependency: '+name)
        inputs[name] = checksum
    return dict(root=str(root), manifest_sha256=SEAL, members=77, object=str(root/'objects/filesystem-metadata.o'),
                inputs=inputs, native_accepted=False, protocol='AFSRPC07', rights=31,
                metadata_bytes=112, metadata_frames=2, limits=dict(mutations=9,requests=96,
                    writer_seconds=60,writer_ticks=6000,reader_seconds=30,reader_ticks=3000,
                    controller_bytes=8192,observer_bytes=8192,stack_bytes=4096,engine_pages=8192))


def replace(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('AF07 source context: '+old)
    return text.replace(old,new)


def provider(text, owner):
    """Both inputs are owned AF06 preparation copies, never sealed-source edits."""
    text = replace(text,'#include "zpl-directories.c"','#include "zpl-metadata.c"')
    text = replace(text,'#include "fs-mixed-owner.inc"','#include "af07-owner.inc"')
    owner = replace(owner,'"directories-service.h"','"metadata-service.h"')
    owner = replace(owner,'aether_fs_directories_run(','aether_fs_metadata_run(')
    owner = replace(owner,'writer, 15, 1000, 1000,','writer, 31, 1000, 1000,')
    return text,owner


def client(text, case='normal'):
    validate_case(case)
    text = replace(text,'AFSRPC06','AFSRPC07')
    text = replace(text,"        b'f' => b\"files\",","        b'o' => b\"zstd\",\n        b'f' => b\"files\",")
    text = replace(text,'const JOBS: [[u8; 6]; 26]','const JOBS: [[u8; 6]; 32]')
    text = replace(text,"[1, 1, b'f', 15, 1, 0]","[1, 1, b'f', 31, 1, 0]")
    text = replace(text,"    [1, 2, b'p', 6, 2, 0],","    [1, 2, b'p', 22, 2, 0],\n    [12, 3, 0, 0, 0, 0],")
    text = replace(text,'    [5, 3, 0, 0, 0, 0],','    [5, 3, 0, 0, 0, 0],\n    [12, 3, 0, 0, 1, 0],')
    text = replace(text,"    [1, 2, b'q', 2, 2, 0],","    [1, 2, b'q', 2, 2, 0],\n    [12, 4, 0, 0, 0, 13],")
    text = replace(text,'    [3, 2, 0, 0, 0, 0],','    [3, 2, 0, 0, 0, 0],\n    [1, 1, b\'o\', 18, 2, 0],\n    [12, 8, 0, 0, 2, 0],\n    [3, 8, 0, 0, 0, 0],')
    text = replace(text,"} else if a == b'q' {","} else if a == b'o' {\n                                            780248\n                                        } else if a == b'q' {")
    text = replace(text,'                    match op {','                    match op {\n                        12 => self.metadata_body(&raw, kind),')
    text = replace(text,'check(token == 8 && txg > 790);','check(token == 9 && txg > 790);')
    text = replace(text,'for _ in 0..if cfg!(fs_storage_lifetime) { 63 } else { 64 } {',
                   'for index in 0..58 {')
    start = '                    raw = self.directory_message(6, 1);'
    custom = '''                    if index < 6 {
                        raw = self.directory_message(12, if index == 4 { 99 } else if index == 5 { 8 } else { 1 });
                        if index == 1 { raw[..8].copy_from_slice(b"AFSRPC06"); }
                        if index == 2 { put(&mut raw, 2, self.request ^ 1); }
                        if index == 3 { put(&mut raw, 4, 1); }
                        self.directory_send(&mut raw, 0, 0);
                        self.directory_receive(&mut raw, if index == 0 { 0 } else if index == 1 || index == 3 { 22 } else { 9 });
                        if index == 0 { self.metadata_body(&raw, 3); }
                        continue;
                    }
'''
    text = replace(text,start,custom+start)
    if case in METADATA_REPLIES:
        text = replace(text,'                    if index < 6 {',
            '                    if index == 0 { self.metadata_loss('+str(METADATA_REPLIES.index(case))+'); return; }\n'
            +'                    if index < 6 {')
        text = replace(text,'impl Connection {','impl Connection {\n'+(SERVICE/'fs-metadata-loss.inc').read_text())
    elif case in METADATA_PROVIDERS:
        if case == 'metadata-errno':
            custom = '''                    if index < 2 {
                        raw = self.directory_message(12, 1);
                        self.directory_send(&mut raw, 0, 0);
                        self.directory_receive(&mut raw, if index == 0 { 5 } else { 0 });
                        if index == 1 { self.metadata_body(&raw, 3); }
                        continue;
                    }
'''
        elif case == 'metadata-completion':
            custom = '''                    if index == 0 {
                        raw = self.directory_message(12, 1);
                        self.directory_send(&mut raw, 0, 0);
                        check(channel::frame(self.receive, &mut raw, false).is_ok());
                        check(get(&raw, 0) == u64::from_le_bytes(*MAGIC)
                            && get(&raw, 1) as i64 == -5 && get(&raw, 2) == self.request
                            && (get(&raw, 3) | get(&raw, 4) | get(&raw, 5) | get(&raw, 7)) == 0
                            && get(&raw, 6) == 3);
                        return;
                    }
'''
        else:
            custom = '''                    if index == 0 {
                        raw = self.directory_message(12, 1);
                        self.directory_send(&mut raw, 0, 0);
                        self.directory_receive(&mut raw, 5);
                        return;
                    }
'''
        text = replace(text,'                    if index < 6 {',custom+'                    if index < 6 {')
    body = '#[cfg(not(any(fs_partial_request, fs_lost_reply)))]\n'+(SERVICE/'fs-metadata-body.inc').read_text()
    text = replace(text,'impl Connection {','impl Connection {\n'+body)
    return text


def paths(text):
    return re.sub(r'#\[path = "([^"]+)"\]',lambda m:'#[path = '+json.dumps(str((SERVICE/m[1]).resolve()))+']',text)


def controller(text, output, diagnostic=False, case='normal'):
    validate_case(case)
    if type(diagnostic) is not bool:
        raise ValueError('AF07 diagnostic must be boolean')
    selected_client=client((SERVICE/'fs-directories-client.rs').read_text(),case)
    if case in ('lost-reply', 'partial-request'):
        # These controls commit only mkdir, never the remaining eight mutations.
        text = replace(text,'u64::from_le_bytes(target) > 790','u64::from_le_bytes(target) > 782')
    original = paths((SERVICE/'fs-service-client.rs').read_text())
    original = replace(original,str(SERVICE/'fs-directories-client.rs'),str(output/'af07-client.rs'))
    if case in METADATA_REPLIES:
        original=replace(original,'if cfg!(fs_lost_reply) && _healthy {',
                         'if cfg!(fs_metadata_loss) && _healthy {',count=2)
    if diagnostic:
        # Fixed numeric assertion identity only: no new I/O, state, pointer,
        # retained observation or mutation. Never turn an error into success.
        sites=[]
        def numbered(source,label):
            def site(match):
                line=source.count('\n',0,match.start())+1
                code=1000+len(sites)
                sites.append(dict(code=code,source=label,line=line,
                    text=source[match.start():].splitlines()[0][:160]))
                return 'check_site('+str(code)+', '
            return re.sub(r'\bcheck\(',site,source)
        selected_client=numbered(selected_client,'af07-client.rs')
        original=replace(original,'use super::check;','use super::check_site;')
        original=numbered(original,'af07-connection.rs')
        text=replace(text,'fn check(ok: bool) {\n    if !ok {\n        end(401);\n    }\n}',
            'fn check_site(site: u64, ok: bool) {\n    if !ok { end(site); }\n}')
        text=numbered(text,'controller.rs')
        (output/'assertion-sites.json').write_text(json.dumps(sites,indent=2)+'\n')
    (output/'af07-client.rs').write_text(selected_client)
    (output/'af07-connection.rs').write_text(original)
    return replace(text,str(SERVICE/'fs-service-client.rs'),str(output/'af07-connection.rs'))


def prepare_engine(stage, command, tools, recovery=False, case='normal', empty=False):
    """Prepare actual old objects; explicit AF07 recomposition follows separately."""
    from openzfs_elapsed import prepare
    from openzfs_failure import runtime_archive
    from openzfs_fs_service import intake as old_intake
    import service_runtime_smoke as runtime
    validate_case(case)
    if type(recovery) is not bool or type(empty) is not bool or (empty and not recovery) or (recovery and case != 'normal'):
        raise ValueError('AF07 exact writer or independent recovery selection required')
    stage.mkdir()
    rows = []
    def tracked(args, log, rejection=None):
        result = command(args,log,rejection=rejection)
        if not rejection: rows.append(dict(argv=list(map(str,args)),exit_code=0))
        return result
    dep = ROOT/'.deps/native-utc-v3'
    selected = None if recovery else old_intake(
        ROOT / 'userland/build/service-deliveries/filesystem-service-directories-2026-10-20-v1',
        mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=True,directories=True)
    diagnostic = stage/'diagnostic';diagnostic.mkdir()
    result = runtime_archive(diagnostic,dep,tools,tracked)
    builder_case=case if case in CASES else 'normal'
    port = prepare(stage/'port',tracked,entropy=True,allocation=True,resources=True,
        arc=True,startup=True,volume=True,volume_utc=True,utc_runtime=dep/'runtime',
        volume_pool=True,pool_diagnostics=True,diagnostic_cc=result['backend_compiler_prefix'],
        volume_pool_namespace=True,volume_namespace_ipc=not recovery,
        volume_pool_zpl_write=not recovery,volume_pool_zpl_recover=recovery,
        volume_recovery_diagnostic=recovery,volume_recovery_writer_60s=recovery,
        volume_fs_service=selected,volume_fs_mixed=True,namespace_wait=not recovery,
        volume_fs_bulk=True,volume_fs_runtime=True,volume_fs_names=True,volume_fs_directories=True,
        volume_fs_service_case=builder_case,volume_fs_mixed_empty=empty)
    (port/'failure-runtime').mkdir()
    shutil.copyfile(diagnostic/'failure-runtime/libaether_runtime.a',port/'failure-runtime/libaether_runtime.a')
    sdk=ROOT/'.deps/native-current/sdk'
    cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl',
        '--sysroot='+str(sdk/'empty-root'),'-std=c11','-D_GNU_SOURCE','-O2','-Wall','-Wextra',
        '-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc',
        '-isystem',str(sdk/'stage/usr/include'),'-I',str(dep/'runtime')]
    composition=runtime.compose_engine(port,tracked,cc,tools,True,'pool-import',
        volume=True,utc=True,runtime=dep,pool=True,diagnostics=True,pool_namespace=True,
        pool_zpl_write=not recovery,pool_zpl_recover=recovery,fs_service=not recovery,
        fs_service_mixed=True,fs_service_wait=not recovery,fs_service_bulk=True,
        fs_service_runtime=True,fs_service_activation=not recovery,
        fs_service_names=True,fs_service_directories=True,fs_service_case=builder_case)
    return dict(commands=rows,composition=composition,old_service=selected,
                case=case,builder_case=builder_case,recovery_empty=empty,output=str(stage))


def metadata_provider(text, owner, case):
    """Fixed read-only getter faults; preserve the old base and original body."""
    validate_case(case)
    if case not in METADATA_REPLIES+METADATA_PROVIDERS:
        return text,owner
    fault=0 if case in METADATA_REPLIES else METADATA_PROVIDERS.index(case)+1
    text=replace(text,'#include "af07-owner.inc"',
        '#define AF07_METADATA_FAULT '+str(fault)+'\n#include "metadata-fault.inc"\n#include "af07-owner.inc"')
    start=owner.index('#if AETHER_FS_SERVICE_CASE == 1')
    end=owner.index('#endif',start)+len('#endif')
    if case in METADATA_REPLIES:
        fields='error != 5 || completion.requests != 38 || completion.stop != 2 || completion.error != -32'
    elif case == 'metadata-errno':
        fields='error || completion.requests != 96 || completion.stop || completion.error'
    else:
        fields='error != 5 || completion.requests != 38 || completion.stop != 5 || completion.error != -5'
    expected=5 if case=='metadata-errno' else 4
    selected='''    if ('''+fields+''' || completion.ready != 1 ||
        completion.reader_close || completion.writer_close || af07_fault_error ||
        af07_gets != '''+str(expected)+''')
        return error ? error : EIO;'''
    owner=owner[:start]+selected+owner[end:]
    return text,owner


def original_getter(mapping, symbols, expected):
    """Wrapped definitions may lack a map's global alias; require real section/nm."""
    sections=[line.split() for line in mapping.splitlines()
              if line.split()[-1:] and line.split()[-1].endswith(':(.text.aether_zpl_getattr)')]
    definitions=[line.split() for line in symbols.splitlines()
                 if line.split()[-1:]==['aether_zpl_getattr']]
    if len(sections)!=1 or len(definitions)!=1:
        raise ValueError('AF07 wrapped original getter definition')
    section,definition=sections[0],definitions[0]
    if (len(section)<5 or len(definition)!=4 or definition[2]!='T'
            or section[-1].split(':(',1)[0]!=str(expected)
            or int(definition[0],16)!=int(section[0],16)
            or int(definition[1],16)!=int(section[2],16) or int(definition[1],16)==0):
        raise ValueError('AF07 wrapped original getter definition')
    return str(expected)


def retirement_sources(writer, startup):
    """Relocate two existing observations in disposable copies; preserve all work."""
    writer=replace(writer,"    aether_engine_utc_phase('D');", "    aether_engine_utc_phase('J');")
    writer=replace(writer,'    dmu_buf_user_evict_wait();',
        "    dmu_buf_user_evict_wait();\n    aether_engine_utc_phase('D');")
    startup=replace(startup,"    engine_observe('J');\n",'')
    return writer,startup


def recompose(stage, record, selected, command, tools, case=None, retirement=False):
    """Replace one provider/object in actual recipes; independently inspect origins."""
    case=validate_case(record['case'] if case is None else case)
    if retirement and case!='metadata-nanos':
        raise ValueError('AF07 retirement diagnostic requires the fixed nanos case')
    if case != record['case'] and not (case in METADATA_REPLIES+METADATA_PROVIDERS and record['case']=='normal'):
        raise ValueError('AF07 case does not match its verified preparation')
    port=Path(record.get('output',stage))/'port';work=stage/'af07';work.mkdir()
    body,owner=provider((port/'zpl-mutation-selected.c').read_text(),(port/'fs-mixed-owner.inc').read_text())
    body,owner=metadata_provider(body,owner,case)
    wrapped=case in METADATA_REPLIES+METADATA_PROVIDERS
    source=work/'metadata-provider.c';source.write_text(body)
    (work/'af07-owner.inc').write_text(owner)
    compile=recipe(record,'zpl-mutation.o');cc=compile[:compile.index('-c')]
    command(cc+['-I'+str(work),'-I'+str(Path(selected['root'])/'source'),'-c',source,
        '-o',work/'metadata-provider.o'],work/'provider.log')
    frames=(work/'metadata-provider.su').read_text()
    if 'dynamic' in frames or max(int(row.split('\t')[1]) for row in frames.splitlines())>8192:
        raise ValueError('AF07 C local frame bound')
    partial=recipe(record,'selected-libzpool.o')
    if retirement:
        writer,startup=retirement_sources((VOLUME/'spa-zpl-write.inc').read_text(),
                                         (SERVICE/'engine-startup.c').read_text())
        (work/'spa-zpl-write.inc').write_text(writer)
        spa_source=port/'spa-active.c'
        spa_copy=work/'retirement-spa.c'
        spa_body=spa_source.read_text()
        import_body=(VOLUME/'spa-import.inc').read_text()
        if (spa_body.count('#include "spa-import.inc"')!=1
                or import_body.count('#include "spa-zpl-write.inc"')!=1):
            raise ValueError('AF07 retirement SPA include context')
        # Preserve both include levels: quoted includes resolve relative to
        # their containing file, so the import copy must also live here.
        (work/'spa-import.inc').write_text(import_body)
        spa_copy.write_text(spa_body)
        spa_compile=recipe(record,'spa-active-selected.o')
        if spa_compile.count(str(spa_source))!=1:
            raise ValueError('AF07 retirement SPA recipe context')
        spa_compile=[str(spa_copy) if arg==str(spa_source) else
            arg.replace(str(spa_source)+'=',str(spa_copy)+'=')
                if arg.startswith('-fmacro-prefix-map=') else arg for arg in spa_compile]
        spa_compile[spa_compile.index('-o')+1]=str(work/'retirement-spa.o')
        command(spa_compile,work/'retirement-spa.log')
        preprocess=list(spa_compile);preprocess[preprocess.index('-c')]='-E'
        preprocess[preprocess.index('-o')+1]=str(work/'retirement-spa.i')
        command(preprocess,work/'retirement-preprocess.log')
        expanded=(work/'retirement-spa.i').read_text()
        probe=expanded[expanded.rindex('int aether_spa_import_probe(void)'):]
        wait=probe.index('    dmu_buf_user_evict_wait();')
        if not (probe.index("aether_engine_utc_phase('S')")<wait
                <probe.index("aether_engine_utc_phase('D')")<probe.index('error = spa_export(')
                <probe.index("aether_engine_utc_phase('J')")):
            raise ValueError('AF07 retirement selected preprocessed stages')
        if partial.count(str(port/'spa-active-selected.o'))!=1:
            raise ValueError('AF07 retirement SPA link context')
        partial=[str(work/'retirement-spa.o') if arg==str(port/'spa-active-selected.o') else arg for arg in partial]
        startup_copy=work/'retirement-startup.c';startup_copy.write_text(startup)
        startup_compile=recipe(record,'engine-startup.o')
        if startup_compile.count(str(SERVICE/'engine-startup.c'))!=1:
            raise ValueError('AF07 retirement startup recipe context')
        startup_compile=[str(startup_copy) if arg==str(SERVICE/'engine-startup.c') else arg for arg in startup_compile]
        startup_compile.insert(1,'-I'+str(SERVICE))
        startup_compile[startup_compile.index('-o')+1]=str(work/'retirement-startup.o')
        command(startup_compile,work/'retirement-startup.log')
    old=record['old_service']['object']
    if partial.count(old)!=1 or partial.count(str(port/'zpl-mutation.o'))!=1:
        raise ValueError('AF07 exact object replacement context')
    partial=[selected['object'] if arg==old else str(work/'metadata-provider.o') if arg==str(port/'zpl-mutation.o')
        else '-Map='+str(work/'partial.map') if arg.startswith('-Map=') else arg for arg in partial]
    partial[-1]=str(work/'metadata-libzpool.o')
    if wrapped:partial.insert(1,'--wrap=aether_zpl_getattr')
    command(partial,work/'partial.log')
    required = {'aether_fs_metadata_run':'filesystem-metadata.o',
        'aether_zpl_getattr':'metadata-provider.o','aether_pool_namespace_write':'metadata-provider.o'}
    if retirement:
        required.update(aether_spa_import_probe='retirement-spa.o',
                        spa_import='retirement-spa.o',spa_export='retirement-spa.o')
    if case == 'close-failure': required['__wrap_aether_zpl_close']='metadata-provider.o'
    if wrapped:
        required.pop('aether_zpl_getattr');required['__wrap_aether_zpl_getattr']='metadata-provider.o'
    bound=origins((work/'partial.map').read_text(),required)
    nm=Path(tools['clang']['path']).parent/'llvm-nm'
    if wrapped:
        command([nm,'--print-size','--defined-only',work/'metadata-libzpool.o'],work/'partial-symbols.log')
        bound['aether_zpl_getattr']=original_getter((work/'partial.map').read_text(),
            (work/'partial-symbols.log').read_text(),work/'metadata-provider.o')
    engine=recipe(record,'selected-engine.o')
    engine=[str(work/'metadata-libzpool.o') if arg==str(port/'selected-libzpool.o') else arg for arg in engine]
    engine[-1]=str(work/'metadata-engine.o');command(engine,work/'engine.log')
    link=recipe(record,'engine.elf')
    if retirement:
        if link.count(str(port/'engine-startup.o'))!=1:
            raise ValueError('AF07 retirement startup link context')
        link=[str(work/'retirement-startup.o') if arg==str(port/'engine-startup.o') else arg for arg in link]
    link=[str(work/'metadata-engine.o') if arg==str(port/'selected-engine.o') else
        '-Map='+str(work/'metadata.map') if arg.startswith('-Map=') else arg for arg in link]
    link[-1]=str(work/'engine.elf');command(link,work/'link.log')
    required = {'aether_fs_metadata_run':'metadata-engine.o',
        'aether_zpl_getattr':'metadata-engine.o','aether_pool_namespace_write':'metadata-engine.o',
        'spa_import':'metadata-engine.o','spa_export':'metadata-engine.o'}
    if retirement:
        required.update(aether_spa_import_probe='metadata-engine.o',
                        main='retirement-startup.o',aether_engine_utc_phase='retirement-startup.o')
    if case == 'close-failure': required['__wrap_aether_zpl_close']='metadata-engine.o'
    if wrapped:
        required.pop('aether_zpl_getattr');required['__wrap_aether_zpl_getattr']='metadata-engine.o'
    final=origins((work/'metadata.map').read_text(),required)
    nm=Path(tools['clang']['path']).parent/'llvm-nm';elf=work/'engine.elf'
    close_identity = None
    getter_identity = None
    if wrapped:
        command(cc+['-c',VOLUME/'zpl-metadata.c','-o',work/'original-getter.o'],work/'original-getter.log')
        for label,obj in (('original',work/'original-getter.o'),('af07',work/'metadata-provider.o')):
            command([nm.parent/'llvm-objcopy','--dump-section=.text.aether_zpl_getattr='+str(work/(label+'-getter.bin')),
                obj,work/'objcopy-output.o'],work/(label+'-getter.log'))
        original=(work/'original-getter.bin').read_bytes()
        if not original or original != (work/'af07-getter.bin').read_bytes():
            raise ValueError('AF07 changed original getter section')
        getter_identity=dict(bytes=len(original),sha256=digest(work/'original-getter.bin'))
        command([nm,'--print-size','--defined-only',elf],work/'final-symbols.log')
        final['aether_zpl_getattr']=original_getter((work/'metadata.map').read_text(),
            (work/'final-symbols.log').read_text(),work/'metadata-engine.o')
    if case == 'close-failure':
        for label,obj in (('original',port/'zpl-mutation.o'),('af07',work/'metadata-provider.o')):
            command([nm.parent/'llvm-objcopy','--dump-section=.text.aether_zpl_close='+str(work/(label+'-close.bin')),obj],work/(label+'-close.log'))
        original=(work/'original-close.bin').read_bytes()
        if not original or original != (work/'af07-close.bin').read_bytes():
            raise ValueError('AF07 changed original consuming close')
        close_identity=dict(bytes=len(original),sha256=digest(work/'original-close.bin'))
    command([nm,'--undefined-only',elf],work/'imports.log')
    if any(line.split()[-1]!='_DYNAMIC' for line in (work/'imports.log').read_text().splitlines() if line.strip()):
        raise ValueError('AF07 unresolved engine import')
    command([nm,'--defined-only',elf],work/'symbols.log')
    if any(line.split()[-1]=='aether_fs_directories_run' for line in (work/'symbols.log').read_text().splitlines()):
        raise ValueError('AF07 old service unexpectedly retained')
    command([nm.parent/'llvm-readelf','-rW',elf],work/'relocs.log')
    if (work/'relocs.log').read_text().strip()!='There are no relocations in this file.':
        raise ValueError('AF07 relocations')
    shutil.copyfile(port/'image-check.zig',work/'image-check.zig')
    command(['zig','run','--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
        '-O','ReleaseSafe','--dep','native_elf','-Mroot='+str(work/'image-check.zig'),
        '-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')],work/'loader.log')
    shutil.copyfile(elf,stage/'engine.elf')
    return dict(partial_origins=bound,final_origins=final,local_frames=frames,
                elf_sha256=digest(elf),elf_bytes=elf.stat().st_size,
                structural_loader=(work/'loader.log').read_text().strip(),
                source_sha256=digest(source),owner_sha256=digest(work/'af07-owner.inc'),
                case=case,original_close=close_identity,original_getter=getter_identity,
                verified_preparation_case=record['case'],retirement_diagnostic=retirement)
