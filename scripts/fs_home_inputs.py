#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build and admit the fixed AF09 owner/shell/helper dependency offline."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import shutil
import shlex
import struct
import sys
import tarfile
import tempfile
import time

from deps import ROOT
import fs_home_launch as launch

SCHEMA = 'aether-guarded-af09-inputs-v1'
ARTIFACTS = ('owner.elf', 'owner.bin', 'shell.elf', 'helper.elf', 'envelope.bin')
PROFILE = dict(envelope='AENFS005', nested='AENMX010', abi=31, protocol='AFSRPC09',
    file_wire='AEFW0001', write_wire=True, paths=True, dup2=True, cwd=False,
    libc_file_write=False, selection='fs_home_probe_three', provider_attempts=3,
    utc_min=1791290040, utc_max_exclusive=1791290100, rtc='2026-10-06T12:34:00,clock=vm')
BOUNDS = dict(domains=7, channels=12, backing_bytes=35*1024*1024,
    owner_code=49152, owner_resident=8192, owner_stack=8192, owner_usable_stack=8184,
    owner_workspace=4096, owner_backing_pages=128, engine_backing_pages=8192,
    engine_loader_pages=2048, process_loader_pages=128, engine_file_bytes=8*1024*1024,
    process_file_bytes=1024*1024, writer_seconds=60, writer_ticks=6000,
    reader_seconds=30, reader_ticks=3000, capture_bytes=65536)
PROCESS_PIN = '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
OWNER_CENSUS = ('native-home.rs', 'native-home-tests.rs', 'launch-home-owner.rs',
                'launch-home-owner-tests.rs', 'home-native-fixture.c')
FIELDS = {'format','status','native_executed','profile','bounds','engine',
    'producer_receipt','owner_receipt','owner_reuse','measurement','admission',
    'artifacts','inputs','tools','commands','kernel_build','final_input_verification'}
S = ROOT/'userland/experiments/filesystem-service'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return launch.read_json(path)


def sha_string(value):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def verify_map(inputs, generated=None):
    generated = generated or {}
    if not isinstance(inputs,dict) or not inputs:
        raise ValueError('AF09 guarded missing input map')
    for name, expected in inputs.items():
        path=Path(name)
        if not path.is_absolute() or not sha_string(expected):
            raise ValueError('AF09 guarded input map shape')
        if path.is_file():
            if digest(path)!=expected:
                raise ValueError('AF09 guarded input changed: '+name)
        elif generated.get(name)!=expected:
            raise ValueError('AF09 guarded unavailable input: '+name)
    return dict(inputs)


def literal(path,name):
    nodes=[n.value for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Assign)
           and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
    if len(nodes)!=1:raise ValueError('AF09 guarded unique recipe literal: '+name)
    return ast.literal_eval(nodes[0])


def owner_generated(report):
    """Recreate only the 47 disposed receipt23 input leaves, without extracting."""
    from source_paths import relocate
    work=Path(report.get('work',''))
    if ('..' in work.parts or relocate(work).parent!=ROOT/'userland/build'
            or not work.name.startswith('filesystem-home-')):
        raise ValueError('AF09 owner historical work identity')
    return _owner_generated_leaves(report,work)


def _owner_generated_leaves(report,work):
    from source_paths import relocate
    compare=ROOT/'sys-init/scripts/owner_compare.py'
    checker=S/'check-file-writes.py'
    for path in (compare,checker):
        recorded=[expected for name,expected in report.get('sources',{}).items()
                  if relocate(name)==path]
        if recorded!=[digest(path)]:
            raise ValueError('AF09 owner historical recipe changed')
    recipe=runpy.run_path(str(compare))
    sdk=ROOT/'.deps/native-current/sdk'
    archive=sdk/'musl-1.2.6.tar.gz'
    recipe['verified'](archive.read_bytes(),recipe['ARCHIVE_SHA'],str(archive))
    with tarfile.open(fileobj=io.BytesIO(archive.read_bytes()),mode='r:gz') as source:
        bodies={}
        for name,expected in recipe['MEMBERS'].items():
            infos=[m for m in source.getmembers() if m.name=='musl-1.2.6/'+name]
            if len(infos)!=1 or not infos[0].isfile():raise ValueError('AF09 owner tar member')
            bodies[name]=recipe['verified'](source.extractfile(infos[0]).read(),expected,name)
    values={'memcmp.c':bodies['src/string/memcmp.c']}
    for name,expected in recipe['HEADERS'].items():
        values['include/'+name]=recipe['verified']((sdk/'stage/usr/include'/name).read_bytes(),expected,name)
    body=values['memcmp.c'];old=b'const unsigned char *l'
    if body.count(old)!=1:raise ValueError('AF09 owner signed comparison anchor')
    values['signed.c']=body.replace(old,b'const signed char *l')
    generated={str(work/'musl-compare'/name):hashlib.sha256(body).hexdigest() for name,body in values.items()}
    controls=literal(checker,'c_controls')
    if len(controls)!=6 or len({row[0] for row in controls})!=6:
        raise ValueError('AF09 owner six C control recipes')
    names=('fd-file-write-tests.c','fd-facade.h','fd-client.h','fd-protocol.h',
           'fd-file-write.h','fd-client.c','fd-facade.c')
    for label,filename,before,after,_ in controls:
        if filename not in names:raise ValueError('AF09 owner C control source')
        for name in names:
            body=(S/name).read_text()
            if name==filename:
                if body.count(before)!=1:raise ValueError('AF09 owner C control anchor')
                body=body.replace(before,after,1)
            generated[str(work/('FILE-C-control-'+label)/name)]=hashlib.sha256(body.encode()).hexdigest()
    unavailable={name:expected for name,expected in report['sources'].items() if not Path(name).is_file()}
    if len(generated)!=47 or unavailable!=generated:
        raise ValueError('AF09 owner exact disposed input identities')
    return generated


def checked_producer(path):
    report,inputs=launch.checked_receipt(path,'producer')
    for name in launch.generated_sources(report):inputs.pop(name)
    return report,inputs


COMPONENT_SELECTION = 'aether-af09-owner-component-selection-v1'
COMPONENT_REUSE = 'aether-af09-owner-component-reuse-v1'
COMPONENT_IMPL = ('sys-init/prototypes/native-filesystem-session/owner_runtime.rs',
    'sys-init/prototypes/native-filesystem-session/owner_control.rs',
    'sys-init/prototypes/native-filesystem-session/native_owner_control.rs',
    'sys-init/prototypes/native-filesystem-session/home_owner_tests.rs',
    'sys-init/prototypes/native-filesystem-session/owner_exec_tests.rs',
    'sys-init/tests/native_owner_runtime.rs',
    'userland/experiments/filesystem-service/client.rs',
    'userland/experiments/filesystem-service/process-descriptors.rs',
    'sys-init/scripts/check-home-owner.py')


def component_require(ok, message):
    if not ok:raise ValueError('AF09 current owner '+message)


def component_selector(value):
    component_require(isinstance(value,dict) and set(value)=={'path','sha256'} and
        isinstance(value['path'],str) and sha_string(value['sha256']), 'selection identity')
    path=Path(value['path'])
    component_require(path.is_absolute() and '..' not in path.parts and path.resolve()==path and
        not path.is_symlink() and path.is_file() and path.stat().st_size<=8192 and
        digest(path)==value['sha256'], 'selection path/hash')
    return dict(value)


def owner_component_selection(reuse):
    component_require(isinstance(reuse,dict), 'reuse metadata')
    if 'format' not in reuse and 'selection' not in reuse:return None
    component_require(reuse.get('format')==COMPONENT_REUSE and 'selection' in reuse, 'reuse selection format')
    return component_selector(reuse['selection'])


def component_controls(report):
    checker=ROOT/'sys-init/scripts/check-home-owner.py'
    module=ast.parse(checker.read_text())
    check=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='check']
    component_require(len(check)==1,'maintained checker function')
    bindings={n.targets[0].id:ast.literal_eval(n.value) for n in check[0].body
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
        and n.targets[0].id in ('test','independent')}
    values=[n.value for n in check[0].body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id=='controls' for t in n.targets)]
    component_require(len(values)==1 and set(bindings)=={'test','independent'},'maintained control recipe')
    class Names(ast.NodeTransformer):
        def visit_Name(self,node):
            component_require(node.id in bindings,'control literal name')
            return ast.Constant(bindings[node.id])
    recipes=ast.literal_eval(Names().visit(values[0]))
    expected=[];owner=ROOT/'sys-init/prototypes/native-filesystem-session'
    for label,filename,before,after,test,marker in recipes:
        body=(owner/filename).read_text();component_require(body.count(before)==1,'control source anchor')
        expected.append(dict(label=label,file=filename,before=before,after=after,
            test='home_tests::'+test,marker=marker,
            sha256=hashlib.sha256(body.replace(before,after,1).encode()).hexdigest()))
    component_require(len(expected)==13 and report.get('home_owner_controls')==expected,'named owner control identities')
    return expected


def component_row(report,label):
    rows=[row for row in report['rows'] if row['label']==label]
    component_require(len(rows)==1,'required command '+label)
    return rows[0]


def component_control_rows(report):
    controls=component_controls(report)
    counts={'peer_controls':7,'home_init_controls':6,'semantic_controls':6,
        'mutation_controls':6,'process_write_controls':6,'file_controls':11}
    semantic=literal(S/'check-home-wire.py','controls')
    additions=[n for n in ast.walk(ast.parse((S/'check-home-wire.py').read_text())) if isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Name) and n.target.id=='controls']
    component_require(len(additions)==1 and isinstance(additions[0].op,ast.Add),'semantic control extension')
    semantic+=ast.literal_eval(additions[0].value)
    component_require(len(semantic)==6 and report.get('semantic_controls')==[dict(label=label,test=test,before=before,after=after,required_marker=marker)
        for label,filename,before,after,test,marker in semantic],'semantic control recipes')
    semantic_files={label:filename for label,filename,_,_,_,_ in semantic}
    paths=[p for folder in (ROOT/'sys-init/prototypes/native-filesystem-session',S)
        for p in folder.iterdir() if p.suffix in ('.rs','.c','.h')]
    for field,count in counts.items():
        values=report.get(field)
        component_require(isinstance(values,list) and len(values)==count and
            all(isinstance(c,dict) and isinstance(c.get('label'),str) for c in values) and
            len({c['label'] for c in values})==count,'control coverage '+field)
        for c in values:
            component_require(all(isinstance(c.get(k),str) and c[k] for k in ('before','after')),'control recipe fields')
            candidates=[p for p in paths if ('file' not in c or p.name==c['file'])
                and (field!='semantic_controls' or p.name==semantic_files[c['label']])
                and p.read_text().count(c['before'])==1]
            expected=c.get('sha256',c.get('mutated_sha256'))
            if expected is not None:
                component_require(sha_string(expected),'control mutation identity')
                candidates=[p for p in candidates if hashlib.sha256(p.read_text().replace(c['before'],c['after'],1).encode()).hexdigest()==expected]
            component_require(len(candidates)==1,'control source identity '+c['label'])
        controls+=values
    for c in controls:
        marker=c.get('marker',c.get('required_marker'));test=c.get('test','')
        component_require(isinstance(marker,str) and marker and isinstance(test,str),'control marker identity')
        matching=[r for r in report['rows'] if c['label'] in r['label'] and r['expected_exit']!=0 and
            marker in r['stdout']+r['stderr'] and test in r['stdout']+r['stderr']]
        component_require(bool(matching),'named semantic rejection '+c['label'])
    typed=report.get('native_deadline_controls');before='deadline.map_or(0, super::Deadline::get)';after='{ let _ = deadline; 0 }'
    body=(ROOT/'sys-init/prototypes/native-filesystem-session/native_owner_control.rs').read_text()
    component_require(body.count(before)==1 and typed==[dict(label='typed-park-rdx',before=before,after=after,
        sha256=hashlib.sha256(body.replace(before,after,1).encode()).hexdigest(),marker='TYPED_PARK_RDX')],'typed RDX control identity')
    positive=component_row(report,'typed-park-tests');negative=component_row(report,'typed-park-rdx-rejected')
    component_require(positive['expected_exit']==0 and '2 passed; 0 failed' in positive['stdout'] and
        negative['expected_exit']==101 and '1 failed' in negative['stdout'] and 'TYPED_PARK_RDX' in negative['stderr'],'typed RDX observations')
    expected=[]
    for stage in ('host','native'):
        trap=component_row(report,stage+'-host-trap-denied')
        component_require(trap['expected_exit']==1 and 'owner control host trap requires host tests and forbids native target' in trap['stderr'],'host trap guard')
        for name,kind,error in (('client','filesystem_client::Client<T>','filesystem_client::Error'),
                               ('process','filesystem_remote_descriptors::ProcessFiles<T>','filesystem_remote_descriptors::ProcessError')):
            source='#![no_std]\npub fn leak<T:filesystem_service::Channel>(value:&mut '+kind+')->Result<(),'+error+'>{value.configure_channel(|channel|Ok(channel))}\n'
            expected.append(dict(stage=stage,type=name,sha256=hashlib.sha256(source.encode()).hexdigest()))
            denied=component_row(report,stage+'-'+name+'-transport-loan-denied')
            component_require(denied['expected_exit']==1 and 'E0308' in denied['stderr'] and 'configure_channel' in denied['stderr'],'transport loan denial')
    component_require(report.get('transport_configuration_denials')==expected,'transport loan source identities')
    tests=component_row(report,'home-owner-tests')
    component_require(tests['expected_exit']==0 and '16 passed; 0 failed' in tests['stdout'],'actual current owner positive cases')


def current_owner_receipt(path,component):
    selected=component_selector(component);proof=read_json(selected['path'])
    component_require(isinstance(proof,dict) and set(proof)=={'format','receipt','role_metadata'} and
        proof['format']==COMPONENT_SELECTION,'selection wrapper format')
    receipt=proof['receipt'];path=Path(path).absolute()
    component_require(isinstance(receipt,dict) and set(receipt)=={'path','sha256'} and
        receipt['path']==str(path) and sha_string(receipt['sha256']) and path.resolve()==path and
        path.is_file() and not path.is_symlink() and digest(path)==receipt['sha256'],'component receipt identity')
    report=read_json(path)
    component_require(isinstance(report,dict) and report.get('scope')=='actual maintained check-home-owner.check full component gate; no guest' and
        report.get('source')==str(ROOT/'sys-init/scripts/check-home-owner.py') and report.get('status')=='pass' and
        report.get('native_executed') is False and report.get('cleanup')=='complete' and
        report.get('limits')==dict(aggregate_seconds=300,leaf_seconds=180,stream_bytes=4194304) and
        isinstance(report.get('elapsed_seconds'),(int,float)) and 0<report['elapsed_seconds']<=300,'component coverage/status')
    work=Path(report.get('work',''))
    component_require(work.parent==Path('/private/tmp') and '..' not in work.parts and
        re.fullmatch(r'af61-component-01-[a-z0-9_]+',work.name) is not None,'component work identity')
    rows=report.get('rows');actual=report.get('actual_processes')
    component_require(isinstance(rows,list) and len(rows)==911 and isinstance(actual,list) and len(actual)==911,'complete component commands')
    tools=report.get('tools');sources=report.get('sources')
    component_require(isinstance(tools,dict) and set(tools)=={'rustc','rustfmt','clippy-driver','objdump','size','rust-lld','clang','clang-format','nm','readelf','lld'} and isinstance(sources,dict) and len(sources)==1097 and
        all(isinstance(n,str) and Path(n).is_absolute() and '..' not in Path(n).parts and sha_string(h) for n,h in sources.items()),'component source/tool maps')
    for index,row in enumerate(rows):
        component_require(isinstance(row,dict) and isinstance(row.get('label'),str) and isinstance(row.get('process'),dict) and
            row['process']==actual[index] and type(row.get('expected_exit')) is int and
            isinstance(row.get('stdout'),str) and len(row['stdout'])<=7000 and isinstance(row.get('stderr'),str) and len(row['stderr'])<=5000,'ordered process agreement')
        p=row['process'];argv=p.get('argv');tool=p.get('tool')
        component_require(p.get('cwd') in (str(ROOT/'sys-init'),str(ROOT/'userland')) and p.get('complete') is True and p.get('cleanup')=='complete' and p.get('failure') is None and
            type(p.get('exit')) is int and p['exit']==row['expected_exit'] and
            isinstance(p.get('timeout_seconds'),(int,float)) and 0<p['timeout_seconds']<=180 and
            isinstance(argv,list) and argv and all(isinstance(a,str) for a in argv) and
            isinstance(tool,dict) and tool.get('path')==argv[0] and sha_string(tool.get('sha256')),'complete child outcome')
        executable=Path(argv[0]);component_require(executable.is_absolute() and '..' not in executable.parts,'child executable identity')
        if not executable.is_relative_to(work):
            component_require(any(t.get('path')==str(executable) and t.get('sha256')==tool['sha256'] for t in tools.values() if isinstance(t,dict)),'retained executable pin')
    component_require(type(report.get('diagnostic_bytes')) is int and
        sum(len(r['stdout'].encode())+len(r['stderr'].encode()) for r in rows)<=report['diagnostic_bytes']<=4194304,'bounded retained diagnostics')
    frozen={str(ROOT/n) for n in COMPONENT_IMPL}
    component_require(isinstance(report.get('frozen_implementation'),dict) and set(report['frozen_implementation'])==frozen and
        all(sources.get(n)==h and Path(n).resolve()==Path(n) and digest(n)==h for n,h in report['frozen_implementation'].items()),'frozen owner implementation')
    role=proof['role_metadata'];roles=ROOT/'kernel/arch/x86_64/native_fs_roles.zig';reader=ROOT/'sys-init/scripts/owner_measure.py'
    component_require(isinstance(role,dict) and set(role)=={'path','before_sha256','current_sha256','code_limit','reader'} and
        role['path']==str(roles) and role['before_sha256']==sources.get(str(roles)) and
        sha_string(role['current_sha256']) and role['current_sha256']==digest(roles) and role['code_limit']==49152 and
        isinstance(role['reader'],dict) and role['reader']==dict(path=str(reader),sha256=sources.get(str(reader))) and
        role['reader']['sha256']==digest(reader),'reviewed role metadata identity')
    component_require(re.findall(r'^pub const owner_stack_code_limit = (\d+);',roles.read_text(),re.M)==['49152'] and
        reader.read_text().count("re.search(r'pub const owner_stack_code_limit = (\\d+);', roles.read_text())")==1,'unchanged owner code-limit reader')
    for row in rows:
        if Path(row['process']['argv'][0]).name in ('rustc','clippy-driver','clang'):
            component_require(not any('native_fs_roles.zig' in arg for arg in row['process']['argv']),'role file was actual compiler input')
    harness=Path('/private/tmp/af61-component.py');text=report.get('harness_source')
    component_require(isinstance(text,str) and sources.get(str(harness))==hashlib.sha256(text.encode()).hexdigest(),'retained harness source identity')
    reduced=dict(report,sources={n:h for n,h in sources.items() if n!=str(harness)})
    generated=_owner_generated_leaves(reduced,work)
    current={n:h for n,h in reduced['sources'].items() if n not in generated};current[str(roles)]=role['current_sha256']
    verify_map(current)
    for tool in tools.values():
        component_require(isinstance(tool,dict) and isinstance(tool.get('path'),str) and sha_string(tool.get('sha256')),'tool identity shape')
        verify_map({tool['path']:tool['sha256']})
    compiler=Path(tools['rustc']['path']);native=compiler.parent.parent/'lib/rustlib/x86_64-unknown-none/lib'
    libraries={str(p) for p in native.glob('*.rlib')}
    component_require(len(libraries)==3 and libraries<={n for n in current} and
        isinstance(report.get('libraries'),dict) and len(report['libraries'])==74 and
        all(sha_string(h) for h in report['libraries'].values()),'native library input/output coverage')
    component_control_rows(report)
    measure=report.get('home_owner_measurement');stack=measure.get('stack',{}) if isinstance(measure,dict) else {}
    component_require(isinstance(measure,dict) and measure.get('code_budget')==49152 and measure.get('code_fits') is True and
        0<measure.get('code_bytes',0)<=49152 and measure.get('resident_fits') is True and measure.get('native_executed') is False and
        0<measure.get('runtime_bytes',0)<=4096 and measure.get('workspace_bytes')==4096 and measure.get('mapped_bytes')==8192 and
        stack.get('status')=='pass' and stack.get('usable_stack_bytes')==8184 and 0<stack.get('entry_stack_bytes',0)<=8184,'retained current owner fit')
    current.update({str(path):receipt['sha256'],selected['path']:selected['sha256'],str(Path(__file__).resolve()):digest(__file__)})
    impact=dict(format=COMPONENT_REUSE,scope='retained current owner component coverage with reviewed metadata impact',
        children=911,fresh_host_qualification=False,selection=selected,role_metadata=role,
        reconstructed_generated=generated,retained_harness=dict(path=str(harness),sha256=sources[str(harness)],executed=False),
        fresh_measurement='home_owner_build.build on current real sources')
    verify_map(current)
    return report,current,impact


def owner_receipt(path,producer,*,component=None):
    if component is not None:return current_owner_receipt(path,component)
    report=read_json(path)
    if (report.get('schema')!='aether-home-owner-evidence-v1' or report.get('status')!='pass'
            or report.get('native_executed') is not False or report.get('cleanup')!='complete'
            or report.get('final_input_verification')!='pass' or len(report.get('rows',[]))!=891
            or len(report.get('home_owner_controls',[]))!=9):
        raise ValueError('AF09 historical owner coverage/status')
    for row in report['rows']:
        process=row.get('process',{})
        if (process.get('complete') is not True or process.get('cleanup')!='complete'
                or process.get('exit')!=row.get('expected_exit',0)):
            raise ValueError('AF09 historical owner incomplete child')
    generated=owner_generated(report)
    sources=dict(report['sources'])
    excluded={}
    for filename in OWNER_CENSUS:
        name=str(S/filename)
        if name not in sources or producer.get('sources',{}).get(name)!=digest(name):
            raise ValueError('AF09 census exclusion requires fresh producer coverage')
        excluded[name]=dict(historical_sha256=sources.pop(name),current_sha256=digest(name),
            impact='Census only in owner host receipt; not an owner crate/C translation unit. Fresh native producer covers current bytes.')
    # A bounded traversal of actual receipt compiler argv independently rejects
    # any excluded file that was a direct compile input. The owner builder also
    # records rustc dep-info for the freshly rebuilt real owner graph.
    for row in report['rows']:
        argv=row['process'].get('argv',[])
        if argv and Path(argv[0]).name in ('rustc','clippy-driver','clang') and any(arg in excluded for arg in argv):
            raise ValueError('AF09 excluded census file was a compiler input')
    inputs=verify_map(sources,generated)
    for name in generated:inputs.pop(name)
    inputs.update(verify_map(report['rust_native_libraries']))
    for tool in report['tools'].values():inputs.update(verify_map({tool['path']:tool['sha256']}))
    inputs[str(Path(path).absolute())]=digest(path)
    impact=dict(scope='historical host coverage with explicit input impact',children=891,
        fresh_host_qualification=False,excluded_census=excluded,
        reconstructed_generated=generated,generated_recipes=dict(compare=str(ROOT/'sys-init/scripts/owner_compare.py'),
        c_controls=str(S/'check-file-writes.py')),fresh_measurement='home_owner_build.build on current real sources')
    return report,inputs,impact


def envelope(engine,shell,helper,owner):
    if not (0<len(engine)<=8*1024*1024 and 0<len(shell)<=1024*1024
            and 0<len(helper)<=1024*1024 and 0<len(owner)<=49152):
        raise ValueError('AF09 guarded envelope extent')
    nested=struct.pack('<8sIIIIQ',b'AENMX010',len(shell),len(shell),len(helper),len(owner),0)+bytes(range(80))+shell+shell+helper+owner
    return struct.pack('<8sII',b'AENFS005',len(engine),len(nested))+bytes(range(32))+engine+nested


def checked_members(directory,seal):
    root=Path(directory).absolute()
    if root.is_symlink() or not root.is_dir() or not sha_string(seal):raise ValueError('AF09 guarded dependency path/seal')
    root=root.resolve()
    manifest=root/'SHA256SUMS'
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size>4096 or digest(manifest)!=seal:
        raise ValueError('AF09 guarded manifest identity')
    members={}
    for line in manifest.read_text().splitlines():
        if not re.fullmatch(r'[0-9a-f]{64}  [a-z.]+',line):raise ValueError('AF09 guarded member shape')
        expected,name=line.split('  ',1)
        if name in members:raise ValueError('AF09 guarded duplicate member')
        members[name]=expected
    wanted=set(ARTIFACTS)|{'inputs.json'}
    if set(members)!=wanted or {p.name for p in root.iterdir()}!=wanted|{'SHA256SUMS'}:
        raise ValueError('AF09 guarded exact member closure')
    total=0
    for name,expected in members.items():
        path=root/name
        ceiling=16*1024*1024 if name=='inputs.json' else 12*1024*1024 if name=='envelope.bin' else 1024*1024
        if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=ceiling or digest(path)!=expected:
            raise ValueError('AF09 guarded member identity/extent')
        total+=path.stat().st_size
    if total>24*1024*1024:raise ValueError('AF09 guarded total dependency extent')
    return members


def kernel_flags():
    from fs_session import FLAGS
    return [*FLAGS,'native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']


def validate_record(record):
    if (not isinstance(record,dict) or set(record)!=FIELDS or record.get('format')!=SCHEMA
            or record.get('status')!='prepared' or record.get('native_executed') is not False
            or record.get('profile')!=PROFILE or record.get('bounds')!=BOUNDS
            or record.get('final_input_verification')!='pass'):
        raise ValueError('AF09 guarded exact profile/status/fields')
    for name,keys in [('engine',{'directory','seal','elf_sha256'}),('producer_receipt',{'path','sha256'}),('owner_receipt',{'path','sha256'})]:
        row=record[name]
        if not isinstance(row,dict) or set(row)!=keys or any(not sha_string(row[k]) for k in keys-{'directory','path'}):
            raise ValueError('AF09 guarded association identity')
    relative=Path(record['engine']['directory'])
    if (relative.as_posix()!=record['engine']['directory'] or relative.is_absolute() or relative.parent!=Path('.deps') or not relative.name.startswith('fs-launch-af09-')):
        raise ValueError('AF09 guarded engine selection')
    owner_component_selection(record['owner_reuse'])
    measurement=record['measurement'];stack=measurement.get('stack',{})
    if (measurement.get('code_budget')!=49152 or measurement.get('code_fits') is not True
            or not 0<measurement.get('code_bytes',0)<=49152 or measurement.get('resident_fits') is not True
            or measurement.get('native_executed') is not False
            or not 0<measurement.get('runtime_bytes',0)<=4096 or not 0<measurement.get('alignment',0)<=4096
            or measurement.get('mapped_bytes')!=8192 or measurement.get('workspace_bytes')!=4096
            or stack.get('status')!='pass' or stack.get('usable_stack_bytes')!=8184
            or not 0<stack.get('entry_stack_bytes',0)<=8184):raise ValueError('AF09 guarded owner fit')
    pages=record['admission']
    if (set(pages)!={'engine_pages','shell_pages','helper_pages','owner_bytes'}
            or any(type(n) is not int for n in pages.values())
            or not 16<pages['engine_pages']<=2048 or not 16<pages['shell_pages']<=128
            or not 16<pages['helper_pages']<=128 or pages['owner_bytes']!=measurement['code_bytes']):
        raise ValueError('AF09 guarded measured new loader geometry')
    if set(record['artifacts'])!=set(ARTIFACTS):raise ValueError('AF09 guarded artifact coverage')
    for name,row in record['artifacts'].items():
        if (set(row)!={'sha256','bytes'} or not sha_string(row['sha256'])
                or type(row['bytes']) is not int or row['bytes']<=0):raise ValueError('AF09 guarded artifact identity')
    if not record['inputs'] or not record['tools'] or not record['commands']:raise ValueError('AF09 guarded consumed closure missing')
    for command in record['commands']:
        p=command.get('process',{})
        if command.get('status')!='pass' or p.get('complete') is not True or p.get('cleanup')!='complete' or p.get('exit')!=command.get('expected_exit',0):
            raise ValueError('AF09 guarded successful child missing')
    if (set(record['kernel_build'])!={'sha256','native_executed','flags'}
            or record['kernel_build'].get('native_executed') is not False
            or record['kernel_build'].get('flags')!=kernel_flags()
            or not sha_string(record['kernel_build'].get('sha256'))):raise ValueError('AF09 guarded actual kernel build')


def owned_runner():
    path=ROOT/'userland/experiments/command-runner/process.py'
    if digest(path)!=PROCESS_PIN:raise ValueError('AF09 guarded owned-process pin')
    import importlib.util
    spec=importlib.util.spec_from_file_location('af09_inputs_process',path)
    proc=importlib.util.module_from_spec(spec);sys.modules[spec.name]=proc;spec.loader.exec_module(proc)
    return proc


def rust_wrapper(path):
    """Private named Rust descendant: fixed compiler and private LLVM only."""
    compiler=Path(path)
    library=compiler.parent.parent/'lib'
    return ('#!/bin/sh\ncase "${1-}" in\n'
        '  +1.98.0) shift ;;\n'
        '  +*) printf "%s\\n" "unsupported pinned Rust selector" >&2; exit 64 ;;\n'
        'esac\nDYLD_LIBRARY_PATH='+shlex.quote(str(library))+' exec '+shlex.quote(str(compiler))+' "$@"\n')


def kernel_environment(work,tools,record,command):
    """Bind build.zig's named descendants without importing the caller's PATH."""
    from deps import LOCK
    work=Path(work);folder=work/'tool-bin';folder.mkdir()
    defaults={'python3':Path(sys.executable).resolve(),
        'xorriso':Path('/opt/homebrew/bin/xorriso'),
        'qemu':Path('/opt/homebrew/bin/qemu-system-x86_64')}
    for name in ('python3','xorriso','qemu'):
        selected=tools.get(name)
        path=Path(selected['path']) if selected else defaults[name]
        if not path.is_absolute() or not path.is_file():
            raise ValueError('AF09 required named tool unavailable: '+name)
        path=path.resolve()
        actual=digest(path)
        if selected and selected['sha256']!=actual:
            raise ValueError('AF09 named tool changed: '+name)
        tools[name]=dict(path=str(path),sha256=actual)
    if digest(tools['rustc']['path'])!=tools['rustc']['sha256']:
        raise ValueError('AF09 pinned Rust compiler changed')
    for name in ('python3','rustc','xorriso','qemu'):
        record.setdefault('inputs',{})[tools[name]['path']]=tools[name]['sha256']
    bindings={}
    for name in ('python3','xorriso'):
        target=Path(tools[name]['path'])
        link=folder/name;link.symlink_to(target)
        bindings[name]=dict(link=str(link),path=str(target),sha256=tools[name]['sha256'])
    body=rust_wrapper(tools['rustc']['path'])
    wrapper=folder/'rustc';wrapper.write_text(body);wrapper.chmod(0o755)
    routing=dict(environment=dict(PATH=str(folder)+':/usr/bin:/bin'),bindings=bindings,
        rust_compiler=dict(tools['rustc']),rust_wrapper=dict(path=str(wrapper),body=body,sha256=digest(wrapper)),
        generator_sha256=digest(__file__),prospective_qemu=dict(tools['qemu'],expected_version=LOCK['qemu'],executed=False),
        versions=dict(python='3.14.7',rust='1.98.0',xorriso=LOCK['xorriso']))
    verify_kernel_environment(routing)
    python=command('kernel-python-version',[tools['python3']['path'],'--version']).strip()
    rust=command('kernel-rust-version',[tools['rustc']['path'],'--version']).split()
    optical=command('kernel-xorriso-version',[tools['xorriso']['path'],'-version'])
    if python!='Python 3.14.7' or len(rust)<2 or rust[1]!='1.98.0' or ('xorriso version   :  '+LOCK['xorriso']) not in optical:
        raise ValueError('AF09 named descendant version differs from pinned build profile')
    verify_kernel_environment(routing)
    record['kernel_tool_routing']=routing
    return routing


def verify_kernel_environment(routing):
    for item in routing['bindings'].values():
        if Path(item['link']).resolve()!=Path(item['path']).resolve() or digest(item['path'])!=item['sha256']:
            raise ValueError('AF09 named descendant binding changed')
    compiler=routing['rust_compiler'];wrapper=routing['rust_wrapper']
    body=rust_wrapper(compiler['path'])
    if (digest(compiler['path'])!=compiler['sha256'] or wrapper['body']!=body
            or hashlib.sha256(body.encode()).hexdigest()!=wrapper['sha256']
            or Path(wrapper['path']).is_symlink() or digest(wrapper['path'])!=wrapper['sha256']
            or digest(routing['prospective_qemu']['path'])!=routing['prospective_qemu']['sha256']):
        raise ValueError('AF09 named Rust recipe/compiler or prospective emulator changed')


def routing_receipt(record):
    rows=[row for row in record['commands'] if row.get('label')=='actual-kernel-build']
    if len(rows)!=1 or not isinstance(rows[0].get('tool_routing'),dict):
        raise ValueError('AF09 actual kernel named-tool routing receipt missing')
    from deps import LOCK
    routing=rows[0]['tool_routing'];compiler=record['tools']['rustc']
    body=rust_wrapper(compiler['path'])
    wrapper_path=Path(routing.get('rust_wrapper',{}).get('path',''))
    environment=routing.get('environment',{})
    if (not wrapper_path.is_absolute() or wrapper_path.name!='rustc'
            or environment!={'PATH':str(wrapper_path.parent)+':/usr/bin:/bin'}
            or routing.get('versions')!=dict(python='3.14.7',rust='1.98.0',xorriso=LOCK['xorriso'])
            or routing.get('prospective_qemu')!=dict(record['tools']['qemu'],expected_version=LOCK['qemu'],executed=False)
            or rows[0]['process'].get('environment',{}).get('PATH')!=environment['PATH']
            or 'DYLD_LIBRARY_PATH' in rows[0]['process'].get('environment',{})):
        raise ValueError('AF09 sealed named descendant environment/version differs')
    if (routing.get('rust_compiler')!=compiler or routing.get('rust_wrapper',{}).get('body')!=body
            or routing['rust_wrapper'].get('sha256')!=hashlib.sha256(body.encode()).hexdigest()
            or routing.get('generator_sha256')!=digest(__file__)
            or 'DYLD_LIBRARY_PATH' in routing.get('environment',{})):
        raise ValueError('AF09 sealed named-tool recipe/identity differs')
    for name in ('python3','xorriso'):
        expected=record['tools'][name];item=routing.get('bindings',{}).get(name,{})
        if item.get('link')!=str(wrapper_path.parent/name) or any(item.get(key)!=expected[key] for key in ('path','sha256')):
            raise ValueError('AF09 sealed named descendant identity differs')


def command_runner(work,proc,tools,deadline,record):
    if not isinstance(proc,launch.CleanupTrackedProcess):
        proc=launch.CleanupTrackedProcess(proc,record)
    routing=None
    def command(label,args):
        nonlocal routing
        if label=='actual-kernel-build' and routing is None:
            routing=kernel_environment(work,tools,record,command)
        remaining=deadline-time.monotonic()
        if remaining<=0:raise RuntimeError('AF09 guarded cumulative target deadline')
        args=list(map(str,args))
        env=proc.clean_env(work)
        if routing is not None:
            verify_kernel_environment(routing);env.update(routing['environment'])
        result=proc.run(args,cwd=ROOT,env=env,work=work,
            label='inputs-%04d-%s'%(len(record.setdefault('commands',[])),label),timeout=min(180,remaining))
        good=result.returncode==0 and result.record['complete'] and result.record['cleanup']=='complete'
        record['commands'].append(dict(label=label,status='pass' if good else 'failed',process=result.record,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr_sha256=hashlib.sha256(result.stderr).hexdigest(),
            tail=(result.stdout+result.stderr).decode(errors='replace')[-7000:] if not good else
                (result.stdout+result.stderr).decode(errors='replace')[-1000:]))
        if routing is not None:
            verify_kernel_environment(routing)
            if label=='actual-kernel-build':record['commands'][-1]['tool_routing']=routing
        if not good:raise RuntimeError('AF09 guarded child failed: '+label)
        return (result.stdout+result.stderr).decode(errors='replace')
    return command


def admit(root,engine,work,command,tools):
    """Run current kernel parsers on final ELF bytes and the exact envelope."""
    stage=work/'admission';stage.mkdir()
    for name,source in [('engine.elf',engine),('shell.elf',root/'shell.elf'),('helper.elf',root/'helper.elf')]:
        shutil.copyfile(source,stage/name)
    shutil.copyfile(root/'envelope.bin',stage/'envelope.bin')
    # Separate native_elf and composition modules avoid loading the same Zig
    # file in two module namespaces. Both children consume the same final bytes.
    (stage/'elf.zig').write_text(r'''const std=@import("std");const elf=@import("native_elf");
fn pages(image: *const elf.Image) usize {var n:usize=16;for(image.segments[0..image.count])|s|{n+=(s.address%4096+s.memsz+4095)/4096;}return n;}
fn check(comptime name:[]const u8, limits:elf.Limits) !usize {
const raw=@embedFile(name);const image=try elf.parseWithLimits(raw,limits);const n=pages(&image);
try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(raw,.{.file_bytes=limits.file_bytes,.pages=n-1}));
const bad=try std.heap.page_allocator.dupe(u8,raw);defer std.heap.page_allocator.free(bad);const ph=std.mem.readInt(u64,bad[32..40],.little);const count=std.mem.readInt(u16,bad[56..58],.little);var tls:?usize=null;var load:?usize=null;
for(0..count)|i|{const at=ph+i*56;const k=std.mem.readInt(u32,bad[at..][0..4],.little);if(k==7)tls=at;if(k==1)load=at;}
try std.testing.expect(tls!=null and load!=null);
std.mem.writeInt(u32,bad[tls.?..][0..4],0,.little);try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(bad,limits));
@memcpy(bad,raw);std.mem.writeInt(u32,bad[load.?+4..][0..4],7,.little);try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(bad,limits));return n;}
pub fn main() !void {const e=try check("engine.elf",elf.large_limits);const s=try check("shell.elf",.{});const h=try check("helper.elf",.{});std.debug.print("AF09_PAGES {d} {d} {d}\n",.{e,s,h});}
''')
    text=command('actual-elf-parser',[tools['zig']['path'],'run','--cache-dir',work/'zig-cache',
        '--global-cache-dir',ROOT/'.zig-cache/global','-O','ReleaseSafe','--dep','native_elf',
        '-Mroot='+str(stage/'elf.zig'),'-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')])
    found=re.findall(r'^AF09_PAGES (\d+) (\d+) (\d+)$',text,re.M)
    if len(found)!=1:raise ValueError('AF09 guarded actual parser page observation')
    (stage/'composition.zig').write_text(r'''const std=@import("std");const c=@import("composition");
pub fn main() !void {const raw=@embedFile("envelope.bin");const b=try c.parseOwnerStack(raw);
try std.testing.expectEqualSlices(u8,@embedFile("engine.elf"),b.engine);
try std.testing.expectEqualSlices(u8,@embedFile("shell.elf"),b.session.images[0]);
try std.testing.expectEqualSlices(u8,@embedFile("shell.elf"),b.session.images[1]);
try std.testing.expectEqualSlices(u8,@embedFile("helper.elf"),b.session.images[2]);
try std.testing.expectError(error.InvalidComposition,c.parseOwnerData(raw));
const bad=try std.heap.page_allocator.dupe(u8,raw);defer std.heap.page_allocator.free(bad);@memcpy(bad[0..8],"AENFS004");try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(bad));
@memcpy(bad,raw);const n=48+b.engine.len;@memcpy(bad[n..][0..8],"AENMX009");try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(bad));
@memcpy(bad,raw);bad[n+24]=1;try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(bad));
try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(raw[0..raw.len-1]));
std.debug.print("AF09_COMPOSITION {d}\n",.{b.session.supervisor.len});}
''')
    text=command('actual-composition-parser',[tools['zig']['path'],'run','--cache-dir',work/'zig-cache',
        '--global-cache-dir',ROOT/'.zig-cache/global','-O','ReleaseSafe','--dep','composition',
        '-Mroot='+str(stage/'composition.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')])
    owner=re.findall(r'^AF09_COMPOSITION (\d+)$',text,re.M)
    if len(owner)!=1:raise ValueError('AF09 guarded composition observation')
    e,s,h=map(int,found[0])
    return dict(engine_pages=e,shell_pages=s,helper_pages=h,owner_bytes=int(owner[0]))


def owner_pair(root,measurement,command,tools):
    """Reinspect the actual raw-owner pair; it is deliberately not process ELF."""
    elf=(root/'owner.elf').read_bytes();raw=(root/'owner.bin').read_bytes()
    if (len(elf)<64 or elf[:8]!=b'\x7fELF\x02\x01\x01\x00'
            or struct.unpack_from('<HHI',elf,16)!=(2,62,1)
            or struct.unpack_from('<Q',elf,24)[0]!=0x400000):raise ValueError('AF09 owner ELF identity')
    offset=struct.unpack_from('<Q',elf,32)[0];stride,count=struct.unpack_from('<HH',elf,54)
    if stride!=56 or not 0<count<=16 or offset+stride*count>len(elf):raise ValueError('AF09 owner program extent')
    loads=[]
    for i in range(count):
        kind,flags,at,address,_,length,memory,_=struct.unpack_from('<IIQQQQQQ',elf,offset+i*stride)
        if kind not in (1,6,0x6474e551,0x6474e552) or at+length>len(elf):raise ValueError('AF09 owner program kind/extent')
        if kind==1:
            if flags!=5 or address!=0x400000 or length!=memory:raise ValueError('AF09 owner RX raw layout')
            loads.append(elf[at:at+length])
    shoff=struct.unpack_from('<Q',elf,40)[0];shstride,shnum,shnames=struct.unpack_from('<HHH',elf,58)
    if shstride!=64 or not 0<shnum<=256 or shoff+shstride*shnum>len(elf) or not 0<shnames<shnum:
        raise ValueError('AF09 owner section table')
    sections=[struct.unpack_from('<IIQQQQIIQQ',elf,shoff+i*shstride) for i in range(shnum)]
    names=sections[shnames]
    if names[1]!=3 or names[4]+names[5]>len(elf):raise ValueError('AF09 owner section names')
    strings=elf[names[4]:names[4]+names[5]];allocated=[]
    for section in sections:
        name,kind,flags,address,at,length,_,_,_,_=section
        if kind!=8 and at+length>len(elf):raise ValueError('AF09 owner section extent')
        if flags&2 and length:
            if name>=len(strings) or strings.find(b'\0',name)<0:raise ValueError('AF09 owner section label')
            label=strings[name:strings.index(b'\0',name)]
            if label!=b'.text' or kind!=1 or address!=0x400000 or length!=len(raw):
                raise ValueError('AF09 owner extra allocated/writable section')
            allocated.append(elf[at:at+length])
    if allocated!=[raw]:raise ValueError('AF09 owner unique text section')
    if loads!=[raw] or len(raw)!=measurement['code_bytes']:raise ValueError('AF09 owner ELF/raw correspondence')
    if (measurement.get('elf_sha256')!=digest(root/'owner.elf')
            or measurement.get('raw_sha256')!=digest(root/'owner.bin')):raise ValueError('AF09 owner measured artifact identity')
    if command('owner-pair-imports',[tools['nm']['path'],'--undefined-only',root/'owner.elf']).strip():
        raise ValueError('AF09 owner unresolved import')
    assembly=command('owner-pair-stack',[tools['objdump']['path'],'-d','--no-show-raw-insn',
        '--x86-asm-syntax=intel',root/'owner.elf'])
    from owner_stack import inspect
    stack=inspect(assembly,root/'owner.elf',stack_bytes=8192)
    if stack['entry_stack_bytes']!=measurement['stack']['entry_stack_bytes']:
        raise ValueError('AF09 owner actual conservative stack correspondence')


def output_path(destination):
    destination=Path(destination).absolute()
    if (destination.parent!=ROOT/'.deps' or destination.parent.resolve()!=destination.parent
            or not destination.name.startswith('fs-owner-af09-') or destination.exists() or destination.is_symlink()):
        raise ValueError('AF09 guarded requires unused .deps/fs-owner-af09-* output')
    return destination


def merge_dependency_inputs(record,probe):
    inputs=record.setdefault('inputs',{})
    inputs.update(probe['sources']);inputs.update(record['home_probe_native_headers'])
    for dep in record['home_probe_dependencies']:
        root=Path(dep['path']);manifest=root/'SHA256SUMS'
        inputs[str(manifest)]=digest(manifest)
        for line in manifest.read_text().splitlines():
            expected,name=line.split('  ',1);inputs[str(root/name)]=expected
    return inputs


def required_sources():
    paths={Path(__file__).resolve(),ROOT/'tests/test_fs_home_inputs.py',ROOT/'build.zig'}
    manifest=ROOT/'build.zig.zon'
    if manifest.exists() or manifest.is_symlink():
        paths.add(manifest)
    for directory in ('kernel','user','scripts'):
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.name!='.DS_Store')
    builder=runpy.run_path(str(ROOT/'sys-init/scripts/home_owner_build.py'))
    owner=ROOT/'sys-init/prototypes/native-filesystem-session'
    original=ROOT/'sys-init/scripts/check-home-owner.py'
    observation=ROOT/'sys-init/scripts/check-file-write-observations.py'
    roots=[S/filename for _,filename,_ in literal(original,'producer_crates')]
    roots += [owner/filename for _,filename,_ in literal(observation,'OWNER_CRATES')]
    roots += [owner/'native_owner.rs',owner/'owner_entry.rs']
    paths.update(builder['rust_sources'](roots))
    paths.update((ROOT/'sys-init/scripts/home_owner_build.py',ROOT/'sys-init/tests/home_owner_build_tests.py',
        original,observation,ROOT/'sys-init/scripts/owner_compare.py',ROOT/'sys-init/scripts/owner_measure.py',
        ROOT/'sys-init/tests/owner_compare.c',ROOT/'docs/native-fs-owner-stack-v1.json'))
    probe=runpy.run_path(str(S/'home_probe_build.py'))
    paths.update(S/name for name in probe['NAMES'])
    paths.update((S/'home_probe_build.py',S/'check-home-wire.py',ROOT/'userland/experiments/command-runner/process.py'))
    return paths


def intake(directory,seal,*,deadline=None):
    root=Path(directory).absolute()
    members=checked_members(root,seal)
    record=read_json(root/'inputs.json');validate_record(record)
    for name,row in record['artifacts'].items():
        if members[name]!=row['sha256'] or (root/name).stat().st_size!=row['bytes']:
            raise ValueError('AF09 guarded artifact/record correspondence')
    engine=launch.intake(ROOT/record['engine']['directory'],record['engine']['seal'])
    if engine['elf_sha256']!=record['engine']['elf_sha256']:raise ValueError('AF09 guarded engine association')
    if read_json(ROOT/record['engine']['directory']/'build.json')['qualification_sha256']!=digest(record['producer_receipt']['path']):
        raise ValueError('AF09 guarded engine/producer receipt association')
    producer,producer_inputs=checked_producer(record['producer_receipt']['path'])
    selection=owner_component_selection(record['owner_reuse'])
    _,owner_inputs,impact=owner_receipt(record['owner_receipt']['path'],producer,**({'component':selection} if selection is not None else {}))
    if impact!=record['owner_reuse']:raise ValueError('AF09 guarded historical reuse impact drift')
    associations={**producer_inputs,**owner_inputs}
    if any(record['inputs'].get(name)!=expected for name,expected in associations.items()):
        raise ValueError('AF09 guarded receipt input map coverage')
    for key in ('producer_receipt','owner_receipt'):
        if digest(record[key]['path'])!=record[key]['sha256']:raise ValueError('AF09 guarded receipt identity')
    if not {str(p) for p in required_sources()} <= record['inputs'].keys():
        raise ValueError('AF09 guarded complete consumed source map coverage')
    verify_map(record['inputs'])
    for tool in record['tools'].values():verify_map({tool['path']:tool['sha256']})
    routing_receipt(record)
    actual=envelope(Path(engine['elf']).read_bytes(),(root/'shell.elf').read_bytes(),
        (root/'helper.elf').read_bytes(),(root/'owner.bin').read_bytes())
    if (root/'envelope.bin').read_bytes()!=actual:raise ValueError('AF09 guarded exact envelope artifact correspondence')
    audit_dir=ROOT/'userland/docs/evidence/filesystem-home-prep-2026-10-24/guarded-inputs/intake'
    audit_dir.mkdir(parents=True,exist_ok=True)
    audit_path=next_receipt(audit_dir)
    receipt=dict(status='running',commands=[],inputs=record['inputs'],native_executed=False,directory=str(root),seal=seal)
    work=None;work_identity=None
    try:
        work=Path(tempfile.mkdtemp(prefix='fs-home-intake-',dir=ROOT/'userland/build'))
        work_identity=directory_identity(work)
        intake_deadline=min(time.monotonic()+300,deadline) if deadline is not None else time.monotonic()+300
        command=command_runner(work,owned_runner(),record['tools'],intake_deadline,receipt)
        owner_pair(root,record['measurement'],command,record['tools'])
        if admit(root,Path(engine['elf']),work,command,record['tools'])!=record['admission']:
            raise ValueError('AF09 guarded actual parser geometry changed')
        verify_map(record['inputs'])
        if checked_members(root,seal)!=members:raise ValueError('AF09 guarded dependency changed during intake')
        if time.monotonic()>intake_deadline:raise RuntimeError('AF09 guarded intake deadline after verification')
        receipt.update(status='pass',final_input_verification='pass')
    except BaseException as error:
        receipt.update(status='failed',error=type(error).__name__+': '+str(error));raise
    finally:
        primary=sys.exception();errors=[]
        if launch.process_cleanup_unresolved(receipt,primary):
            launch.retain_unresolved(receipt,[work,root],primary)
        elif work is not None:remove_owned(work,work_identity,errors,'intake-work')
        finish_attempt(receipt,audit_path,errors,primary)
    return dict(format=SCHEMA,directory=str(root),seal=seal,engine=record['engine'],
        admission=record['admission'],measurement=record['measurement'],native_executed=False)


def _build(destination,engine_directory,engine_seal,producer_receipt,owner_qualification,detail,receipt,*,owner_component=None):
    """Construct one selected dependency under the outer attempt receipt."""
    destination=output_path(destination)
    engine_directory=Path(engine_directory).absolute()
    engine=launch.intake(engine_directory,engine_seal)
    producer,inputs=checked_producer(producer_receipt)
    _,owner_inputs,impact=owner_receipt(owner_qualification,producer,**({'component':owner_component} if owner_component is not None else {}));inputs.update(owner_inputs)
    if read_json(engine_directory/'build.json')['qualification_sha256']!=digest(producer_receipt):
        raise ValueError('AF09 guarded engine/producer receipt association')
    engine_record=read_json(engine_directory/'build.json')
    inputs.update(engine_record['inputs'])
    inputs[str(engine_directory/'SHA256SUMS')]=engine_seal
    inputs.update({str(engine_directory/name):expected for name,expected in launch.closure(engine_directory,engine_seal)[1].items()})
    tools=dict(producer['tools'])
    for name,tool in engine_record['tools'].items():
        if name in tools and tools[name]!=tool:raise ValueError('AF09 guarded tool selection conflict')
        tools[name]=tool
    if 'zig' not in tools:raise ValueError('AF09 guarded engine lacks pinned Zig')
    inputs[str(Path(__file__).resolve())]=digest(__file__)
    inputs[str(ROOT/'tests/test_fs_home_inputs.py')]=digest(ROOT/'tests/test_fs_home_inputs.py')
    inputs[str(ROOT/'userland/experiments/command-runner/process.py')]=PROCESS_PIN
    # Freeze the actual native kernel build graph before any child runs. The
    # dependency contains hashes, not copies of these current source trees.
    for directory in ('kernel','user','scripts'):
        inputs.update({str(p):digest(p) for p in sorted((ROOT/directory).rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store'})
    inputs.update({str(p):digest(p) for p in required_sources()})
    verify_map(inputs)
    work=Path(tempfile.mkdtemp(prefix='fs-home-inputs-',dir=ROOT/'userland/build'))
    detail['work']=str(work)
    detail['work_identity']=directory_identity(work)
    detail.update(status='preparing',native_executed=False,inputs=inputs,tools=tools,rows=[],commands=[],
        destination=str(destination),producer_receipt=str(Path(producer_receipt).absolute()),owner_receipt=str(Path(owner_qualification).absolute()),
        owner_reuse=impact,work=str(work))
    deadline=time.monotonic()+1800
    proc=launch.CleanupTrackedProcess(owned_runner(),detail)
    command=command_runner(work,proc,tools,deadline,detail)
    destination.mkdir();detail['destination_created']=True
    detail['destination_identity']=directory_identity(destination)
    try:
        owner_builder=runpy.run_path(str(ROOT/'sys-init/scripts/home_owner_build.py'))
        owner=owner_builder['build'](ROOT,work,proc,tools,deadline,detail)
        probe=runpy.run_path(str(S/'home_probe_build.py'))['build'](work,proc,tools,deadline,detail)
        if launch.process_cleanup_unresolved(detail):
            raise RuntimeError('AF09 guarded imported cleanup unconfirmed')
        merge_dependency_inputs(detail,probe)
        # Imported builders return owned artifacts and retain all original
        # processes. Promote their outcomes without erasing expected denials.
        for row in detail['rows']:
            p=row['process'];expected=row.get('expected_exit',0)
            if p['exit']!=expected or not p['complete'] or p['cleanup']!='complete':
                raise RuntimeError('AF09 guarded imported builder child')
        for name,source in [('owner.elf',owner['elf']),('owner.bin',owner['raw']),('shell.elf',probe['shell']),('helper.elf',probe['helper'])]:
            shutil.copyfile(source,destination/name)
        (destination/'envelope.bin').write_bytes(envelope(Path(engine['elf']).read_bytes(),
            (destination/'shell.elf').read_bytes(),(destination/'helper.elf').read_bytes(),(destination/'owner.bin').read_bytes()))
        owner_pair(destination,owner['measurement'],command,tools)
        admission=admit(destination,Path(engine['elf']),work,command,tools)
        flags=kernel_flags()
        command('actual-kernel-build',[tools['zig']['path'],'build','-p',work/'kernel-build',
            '--cache-dir',work/'zig-cache','--global-cache-dir',ROOT/'.zig-cache/global','-Dsmp=false',
            '-Dnative-c-image='+str(destination/'envelope.bin'),*['-D'+f+'=true' for f in flags]])
        kernel=dict(sha256=digest(work/'kernel-build/bin/aether'),native_executed=False,flags=flags)
        verify_map(detail['inputs'])
        launch.intake(engine_directory,engine_seal)
        launch.checked_receipt(producer_receipt,'producer');owner_receipt(owner_qualification,producer,**({'component':owner_component} if owner_component is not None else {}))
        commands=list(detail['commands'])
        for row in detail['rows']:
            commands.append(dict(label=row['label'],status='pass',process=row['process'],expected_exit=row.get('expected_exit',0)))
        selected=dict(format=SCHEMA,status='prepared',native_executed=False,profile=dict(PROFILE),bounds=dict(BOUNDS),
            engine=dict(directory=str(engine_directory.relative_to(ROOT)),seal=engine_seal,elf_sha256=engine['elf_sha256']),
            producer_receipt=dict(path=str(Path(producer_receipt).absolute()),sha256=digest(producer_receipt)),
            owner_receipt=dict(path=str(Path(owner_qualification).absolute()),sha256=digest(owner_qualification)),owner_reuse=impact,
            measurement=owner['measurement'],admission=admission,
            artifacts={n:dict(sha256=digest(destination/n),bytes=(destination/n).stat().st_size) for n in ARTIFACTS},
            inputs=detail['inputs'],tools=tools,commands=commands,kernel_build=kernel,final_input_verification='pass')
        validate_record(selected)
        (destination/'inputs.json').write_text(json.dumps(selected,indent=2)+'\n')
        (destination/'SHA256SUMS').write_text(''.join(digest(destination/n)+'  '+n+'\n' for n in sorted((*ARTIFACTS,'inputs.json'))))
        seal=digest(destination/'SHA256SUMS')
        # Intake reparses the final retained bytes; publication never relies on
        # a pre-copy artifact or a parser report from the original builder.
        result=intake(destination,seal,deadline=deadline)
        if time.monotonic()>deadline:raise RuntimeError('AF09 guarded target deadline after verification')
        detail.update(status='pass',final_input_verification='pass',result=result,artifacts=selected['artifacts'])
    except BaseException as error:
        detail.update(status='failed',error=type(error).__name__+': '+str(error))
        raise
    return dict(result,receipt=str(receipt))


def directory_identity(path):
    st=Path(path).lstat()
    if Path(path).is_symlink() or not Path(path).is_dir():raise ValueError('AF09 owned directory identity')
    return [st.st_dev,st.st_ino]


def remove_owned(path,identity,errors,label):
    try:
        if not path.exists() and not path.is_symlink():return
        if identity is None or directory_identity(path)!=identity:
            raise ValueError('owned directory identity changed; foreign output preserved')
        shutil.rmtree(path)
    except BaseException as error:
        errors.append(dict(label=label,path=str(path),error=type(error).__name__+': '+str(error)))


def finish_attempt(detail,receipt,errors,primary):
    unresolved=launch.process_cleanup_unresolved(detail,primary)
    detail['cleanup']='unresolved' if unresolved else 'failed' if errors else 'complete'
    if unresolved:
        launch.retain_unresolved(detail,[],primary)
        detail.setdefault('error','AF09 child cleanup unconfirmed')
    if errors:
        detail['status']='failed';detail['cleanup_errors']=errors
        detail.setdefault('error','AF09 owned cleanup failed')
    try:receipt.write_text(json.dumps(detail,indent=2)+'\n')
    except BaseException as error:
        if errors:error.add_note('AF09 cleanup failures: '+json.dumps(errors))
        if primary is None:raise
        primary.add_note('AF09 receipt write failed: '+type(error).__name__+': '+str(error))
    if errors or unresolved:
        message=('AF09 child cleanup unconfirmed' if unresolved else 'AF09 owned cleanup failed')+'; see '+str(receipt)
        if primary is None:
            error=RuntimeError(message)
            if unresolved:launch.retain_unresolved(detail,[],error)
            raise error
        primary.add_note(message)


def next_receipt(directory):
    indices=[int(p.stem.split('-')[-1]) for p in directory.glob('attempt-*.json')]
    path=directory/('attempt-%02d.json'%(max(indices,default=0)+1))
    with path.open('x') as stream:stream.write('{"status":"starting"}\n')
    return path


def build(destination,engine_directory,engine_seal,producer_receipt,owner_qualification,*,owner_component=None):
    evidence=ROOT/'userland/docs/evidence/filesystem-home-prep-2026-10-24/guarded-inputs/build'
    evidence.mkdir(parents=True,exist_ok=True)
    receipt=next_receipt(evidence)
    detail=dict(status='preflight',native_executed=False,destination=str(destination),commands=[])
    try:
        return _build(destination,engine_directory,engine_seal,producer_receipt,owner_qualification,detail,receipt,**({'owner_component':owner_component} if owner_component is not None else {}))
    except BaseException as error:
        detail.update(status='failed',error=type(error).__name__+': '+str(error))
        raise
    finally:
        primary=sys.exception()
        errors=[]
        if launch.process_cleanup_unresolved(detail,primary):
            paths=[detail.get('work')]
            if detail.get('destination_created'):paths.append(detail['destination'])
            launch.retain_unresolved(detail,paths,primary)
        else:
            if detail.get('work'):
                remove_owned(Path(detail['work']),detail.get('work_identity'),errors,'work')
            if errors:detail['status']='failed'
            if detail.get('destination_created') and detail['status']!='pass':
                remove_owned(Path(detail['destination']),detail.get('destination_identity'),errors,'destination')
        try:
            finish_attempt(detail,receipt,errors,primary)
        except BaseException as error:
            # A receipt publication error also makes a newly built dependency
            # unsuccessful. Its ownership flag is independent of mkdir failure.
            if primary is None and detail['status']=='pass' and detail.get('destination_created'):
                detail.update(status='failed',error='receipt publication failed: '+type(error).__name__+': '+str(error))
                remove_owned(Path(detail['destination']),detail.get('destination_identity'),errors,'destination')
                detail['cleanup']='failed' if errors else 'complete'
                if errors:detail['cleanup_errors']=errors
                try:receipt.write_text(json.dumps(detail,indent=2)+'\n')
                except BaseException as write_error:error.add_note('Failure receipt unavailable: '+str(write_error))
            raise


def main():
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            self.print_usage(sys.stderr);self.exit(64,'[ERROR] '+ascii(message)[1:-1]+'\n')
    parser=Parser(description=__doc__,epilog='Offline preparation only. Keep the compact receipt; correct failed prerequisites before a new output. Guest execution requires a fresh disposition.')
    parser.add_argument('--version',action='version',version='aether-fs-home-inputs 1')
    parser.add_argument('--engine',required=True,type=Path)
    parser.add_argument('--engine-seal',required=True)
    parser.add_argument('--producer-receipt',required=True,type=Path)
    parser.add_argument('--owner-receipt',required=True,type=Path)
    parser.add_argument('--owner-component-proof',type=Path,help='explicit retained current-component selection wrapper; paired hash required')
    parser.add_argument('--owner-component-proof-sha256',help='expected SHA256 of paired current-component wrapper')
    parser.add_argument('--output',required=True,type=Path,help='unused .deps/fs-owner-af09-* dependency')
    args=parser.parse_args()
    if (args.owner_component_proof is None)!=(args.owner_component_proof_sha256 is None):
        parser.error('current owner component proof and hash must be paired')
    selection=None
    if args.owner_component_proof is not None:
        if not sha_string(args.owner_component_proof_sha256):parser.error('invalid paired component SHA256')
        selection=dict(path=str(args.owner_component_proof.absolute()),sha256=args.owner_component_proof_sha256)
    print(json.dumps(build(args.output,args.engine,args.engine_seal,args.producer_receipt,args.owner_receipt,**({'owner_component':selection} if selection is not None else {}))))


if __name__=='__main__':
    try:main()
    except ValueError as error:
        print('[BLOCKED] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(2)
    except (OSError,RuntimeError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(1)
