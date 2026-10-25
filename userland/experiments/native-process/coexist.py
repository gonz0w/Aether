#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent pinned ABI 7 coexistence consumer; no POSIX inheritance adoption."""
import argparse,hashlib,json,os,re,shutil,struct,subprocess,sys,tempfile,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--aether',type=Path,required=True)
p.add_argument('--sdk',type=Path,required=True)
p.add_argument('--producer',type=Path,required=True,help='completed ABI 7 evidence directory')
a=p.parse_args();sdk=a.sdk.resolve();owner=a.aether.resolve();producer=a.producer.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
need(sha(producer/'summary.json')=='778be3796e2f4b55571104a40b2273844c1db47f064493afb886eae12e80d338','producer summary pin mismatch')
summary=json.loads((producer/'summary.json').read_text())
archive=producer/'producer-sources.tar.gz'
need(sha(archive)==summary['source_archive_sha256'],'source archive mismatch')
need(sha(producer/'coexist/results.json')==summary['suites']['coexist']['report_sha256'],'producer report mismatch')
work=Path(tempfile.mkdtemp(prefix='native-coexist-userland-',dir=ROOT/'build'));print(work,flush=True)
kernel=work/'Aether';kernel.mkdir();sources=summary['inputs']
# Only receipt-listed regular files may be materialized; no archive links or paths.
with tarfile.open(archive,'r:gz') as tar:
    members=tar.getmembers()
    need(len(members)==len(sources) and len({m.name for m in members})==len(members),'archive inventory/duplicates')
    for m in members:
        name=Path(m.name)
        need(m.isfile() and not name.is_absolute() and '..' not in name.parts and m.name in sources,'unsafe/unlisted archive member')
        data=tar.extractfile(m).read()
        need(hashlib.sha256(data).hexdigest()==sources[m.name],'archive member mismatch: '+m.name)
        target=kernel/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
shutil.copytree(owner/'.deps',kernel/'.deps')
local={str(p):sha(p) for p in HERE.iterdir() if p.is_file()}
r={'schema':'aether-userland.native-coexist.v1','status':'incomplete','scope':'independent ABI 7 requester routing file RPC through owner broker, two backend generations; no inherited FD or shell adoption','kernel_sources':sources,'local_sources':local,'producer_summary_sha256':sha(producer/'summary.json'),'producer_report_sha256':sha(producer/'coexist/results.json'),'producer_archive_sha256':sha(archive),'commands':[],'cases':[]}

def save():(work/'evidence.json').write_text(json.dumps(r,indent=2)+'\n')
def run(label,cmd):
    result=subprocess.run(cmd,cwd=kernel,capture_output=True,timeout=180)
    (work/(label+'.log')).write_bytes(result.stdout+result.stderr)
    r['commands'].append({'label':label,'argv':cmd,'cwd':str(kernel),'exit':result.returncode});save()
    need(result.returncode==0,label+' failed; '+str(work));return result.stdout
save()
try:
    output=run('requester-prepare',[sys.executable,str(HERE/'prepare.py'),'--sdk',str(sdk),'--coexist'])
    prepared=Path(output.decode().splitlines()[0]);receipt=json.loads((prepared/'evidence.json').read_text());need(receipt['status']=='pass','requester build incomplete')
    r['requester_build']={'output':str(prepared),'receipt_sha256':sha(prepared/'evidence.json')}
    reference=json.loads(Path(receipt['sdk_pin']).read_text());tools=reference['tools'];r['tools']=tools
    r['boot_dependency_manifest']=json.loads((kernel/'.deps/manifest.json').read_text())
    for label,cmd in [('zig-version',['zig','version']),('rust-version',['rustc','+1.98.0','--version']),('qemu-version',['qemu-system-x86_64','--version'])]:run(label,cmd)
    cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
    flags=['-std=c11','-D_GNU_SOURCE','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include')]
    run('worker-compile',cc+flags+['-DHELPER=2','-DCOEXIST','-c','user/native-process/helper.c','-o',str(work/'worker.o')])
    run('adapter-compile',cc+flags+['-c','user/native-memory/adapter.c','-o',str(work/'adapter.o')])
    lib=sdk/'stage/usr/lib';worker=work/'worker.elf'
    workers={}
    for variant,cfg in [('worker',None),('wrong-data','wrong_data')]:
        service=work/(variant+'.a');worker=work/(variant+'.elf')
        cmd=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','--crate-type=staticlib','-C','opt-level=2','-C','panic=abort','-C','relocation-model=static','user/native-files/service.rs','--cfg','writable','-o',str(service)]
        if cfg:cmd+=['--cfg',cfg]
        run(variant+'-service',cmd)
        run(variant+'-link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,-Map,'+str(work/(variant+'.map')),str(lib/'crt1.o'),str(lib/'crti.o'),str(work/'worker.o'),str(work/'adapter.o'),str(service),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(worker)])
        need(not run(variant+'-undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(worker)]).strip(),'worker unresolved')
        need(not re.search(rb'\bsyscall\b',run(variant+'-disassembly',[tools['objdump']['path'],'-d',str(worker)])),'Linux transport')
        run(variant+'-headers',[tools['readelf']['path'],'-h','-l',str(worker)])
        workers[variant]=worker
    brokers={}
    for name,cfg in [('broker',None),('repeat-collect','repeat_collect')]:
        raw=work/(name+'.raw')
        cmd=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-C','opt-level=s','--cfg','coexist','-C','panic=abort','-C','relocation-model=static','-C','lto=fat','-C','codegen-units=1','-C','link-arg=-Tuser/native-launch/linker.ld','-C','link-arg=--oformat=binary','user/native-process/supervisor.rs','-o',str(raw)]
        if cfg:cmd+=['--cfg',cfg]
        run(name+'-compile',cmd);need(0<raw.stat().st_size<=4096,'broker code bound');brokers[name]=raw
    sys.path.insert(0,str(kernel/'scripts'));from native_smoke import run as smoke
    entropy=os.urandom(32)
    cases=[('positive','requester','broker',None,3),('repeat-collect','requester','repeat-collect',66,2),('partial-request','partial','broker',41,1),('requester-exit','early-exit','broker',42,2),('small-pool','requester','broker',59,1),('wrong-data','requester','broker',78,2)]
    for name,client,broker,detail,reclaims in cases:
        dest=work/name;dest.mkdir();first=Path(receipt['artifacts'][client]['path']);worker=workers['wrong-data' if name=='wrong-data' else 'worker'];second=worker;raw=brokers[broker]
        need(sha(first)==receipt['artifacts'][client]['sha256'],'requester changed')
        payload=dest/'native-c.bin';payload.write_bytes(struct.pack('<8sIIII',b'AENCO001',first.stat().st_size,second.stat().st_size,raw.stat().st_size,0)+entropy+first.read_bytes()+second.read_bytes()+raw.read_bytes())
        run(name+'-kernel',['zig','build',*(['-Dnative-coexist-small-pool=true'] if name=='small-pool' else []),'-Dsmp=false','-Dnative-c-image='+str(payload),'-p',str(dest),'--cache-dir',str(kernel/'.zig-cache'),'--global-cache-dir',str(kernel/'.zig-cache/global')])
        context=(f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail}'.encode(),f'NATIVE supervisor result=903 reclaimed={reclaims}'.encode()) if detail else ()
        r['commands'].append({'label':name+'-smoke','function':'native_smoke.run','module_sha256':sources['scripts/native_smoke.py'],'image':str(dest/'aether.iso'),'expected_panic':'native C profile rejected' if detail else None,'panic_context':[x.decode() for x in context],'marker':'AETHER NATIVE COEXIST PASS'});save()
        smoke(dest/'aether.iso',expected_panic=b'native C profile rejected' if detail else None,panic_context=context,marker=b'AETHER NATIVE COEXIST PASS')
        lines=(dest/'native-serial.log').read_text().splitlines()
        if detail:need('AETHER NATIVE COEXIST PASS' not in lines,'negative pass marker')
        else:
            for line in ['NATIVE terminal slot=1 generation=1 kind=1 detail=17','NATIVE terminal slot=1 generation=2 kind=1 detail=17','NATIVE terminal slot=0 generation=1 kind=1 detail=29','NATIVE supervisor result=100 reclaimed=3']:need(line in lines,'missing outcome: '+line)
        r['cases'].append({'case':name,'result':'pass','negative':detail is not None,'requester_sha256':sha(first),'worker_sha256':sha(worker),'broker_sha256':sha(raw),'envelope_sha256':sha(payload),'iso_sha256':sha(dest/'aether.iso'),'serial_sha256':sha(dest/'native-serial.log')});save();print(name+': PASS',flush=True)
    for name,h in sources.items():need(sha(kernel/name)==h,'captured source changed: '+name)
    for name,h in local.items():need(sha(Path(name))==h,'consumer source changed')
    for name,h in receipt['local_sources'].items():need(sha(Path(name))==h,'requester input changed')
    need({str(p.relative_to(sdk)):sha(p) for p in (sdk/'stage').rglob('*') if p.is_file()}==reference['sdk_inputs'],'SDK changed')
    r['artifacts']={p.name:sha(p) for p in [*workers.values(),*brokers.values()]};r['status']='pass'
finally:save()
