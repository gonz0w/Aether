#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent native broker consumer; no POSIX process or inheritance adoption."""
import argparse,hashlib,json,os,re,shutil,struct,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--aether',type=Path,required=True)
p.add_argument('--sdk',type=Path,required=True)
p.add_argument('--restore-from',type=Path,action='append',default=[],help='private source donor matched against the completed producer receipt')
a=p.parse_args();sdk=a.sdk.resolve();owner=a.aether.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
work=Path(tempfile.mkdtemp(prefix='native-broker-userland-',dir=ROOT/'build'));print(work,flush=True)
ignored={'.git','.zig-cache','zig-out','__pycache__','.DS_Store'}
shutil.copytree(owner,work/'Aether',ignore=lambda path,names:set(names)&ignored)
kernel=work/'Aether'
sources={str(p.relative_to(kernel)):sha(p) for p in kernel.rglob('*') if p.is_file() and '.deps' not in p.relative_to(kernel).parts}
for name,h in sources.items():need(sha(owner/name)==h,'source changed during capture: '+name)
producer=kernel/'docs/evidence/native-process-2026-09-05'
summary=json.loads((producer/'summary.json').read_text())
need(sha(producer/'process/results.json')==summary['suites']['process']['report_sha256'],'producer report mismatch')
producer_report=json.loads((producer/'process/results.json').read_text())
restored={}
for name,h in producer_report['sources'].items():
    if Path(name).name=='.DS_Store':continue
    target=kernel/name
    if target.is_file() and sha(target)==h:continue
    candidates=[producer/'source'/name]+[donor.resolve()/name for donor in a.restore_from]
    donor=next((p for p in candidates if p.is_file() and sha(p)==h),None)
    need(donor is not None,'no receipt-matched source donor: '+name)
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(donor,target)
    restored[name]={'donor':str(donor),'sha256':h}
# Contract documentation has its own retained producer source copy.
contract='docs/NATIVE-PROCESS.md'
if sha(kernel/contract)!=sha(producer/'source'/contract):
    shutil.copy2(producer/'source'/contract,kernel/contract)
    restored[contract]={'donor':str(producer/'source'/contract),'sha256':sha(kernel/contract)}
sources={str(p.relative_to(kernel)):sha(p) for p in kernel.rglob('*') if p.is_file() and '.deps' not in p.relative_to(kernel).parts}
for name in ['user/native-process/supervisor.rs','user/native-process/helper.c','user/native-launch/namespace.rs','docs/NATIVE-PROCESS.md']:
    need(sha(kernel/name)==sha(producer/'source'/name),'producer source differs: '+name)
local={str(p):sha(p) for p in HERE.iterdir() if p.is_file()}
r={'schema':'aether-userland.native-broker.v1','status':'incomplete','scope':'independent requester with owner broker/worker, empty inheritance only; no fork/exec/waitpid or file-service coexistence','kernel_source_root':str(owner),'kernel_sources':sources,'local_sources':local,'receipt_matched_restorations':restored,'producer_sources_verified':len(producer_report['sources'])-sum(Path(n).name=='.DS_Store' for n in producer_report['sources']),'producer_summary_sha256':sha(producer/'summary.json'),'producer_report_sha256':sha(producer/'process/results.json'),'commands':[],'cases':[]}
def save():(work/'evidence.json').write_text(json.dumps(r,indent=2)+'\n')
def run(label,cmd):
    result=subprocess.run(cmd,cwd=kernel,capture_output=True,timeout=180)
    (work/(label+'.log')).write_bytes(result.stdout+result.stderr)
    r['commands'].append({'label':label,'argv':cmd,'cwd':str(kernel),'exit':result.returncode});save()
    need(result.returncode==0,label+' failed; '+str(work));return result.stdout
save()
try:
    output=run('requester-prepare',[sys.executable,str(HERE/'prepare.py'),'--sdk',str(sdk)])
    prepared=Path(output.decode().splitlines()[0]);receipt=json.loads((prepared/'evidence.json').read_text());need(receipt['status']=='pass','requester build incomplete')
    r['requester_build']={'output':str(prepared),'receipt_sha256':sha(prepared/'evidence.json')}
    reference=json.loads(Path(receipt['sdk_pin']).read_text());tools=reference['tools'];r['tools']=tools
    r['boot_dependency_manifest']=json.loads((kernel/'.deps/manifest.json').read_text())
    for label,cmd in [('zig-version',['zig','version']),('rust-version',['rustc','+1.98.0','--version']),('qemu-version',['qemu-system-x86_64','--version'])]:run(label,cmd)
    cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
    flags=['-std=c11','-D_GNU_SOURCE','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include')]
    run('worker-compile',cc+flags+['-DHELPER=2','-c','user/native-process/helper.c','-o',str(work/'worker.o')])
    run('adapter-compile',cc+flags+['-c','user/native-memory/adapter.c','-o',str(work/'adapter.o')])
    lib=sdk/'stage/usr/lib';worker=work/'worker.elf'
    run('worker-link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,-Map,'+str(work/'worker.map'),str(lib/'crt1.o'),str(lib/'crti.o'),str(work/'worker.o'),str(work/'adapter.o'),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(worker)])
    need(not run('worker-undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(worker)]).strip(),'worker unresolved')
    need(not re.search(rb'\bsyscall\b',run('worker-disassembly',[tools['objdump']['path'],'-d',str(worker)])),'Linux transport')
    run('worker-headers',[tools['readelf']['path'],'-h','-l',str(worker)])
    brokers={}
    for name,cfg in [('broker',None),('allow-inheritance','allow_inherit'),('wide-scope','wide_scope'),('repeat-collect','repeat_collect')]:
        raw=work/(name+'.raw')
        cmd=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-C','opt-level=2','-C','panic=abort','-C','relocation-model=static','-C','lto=fat','-C','codegen-units=1','-C','link-arg=-Tuser/native-launch/linker.ld','-C','link-arg=--oformat=binary','user/native-process/supervisor.rs','-o',str(raw)]
        if cfg:cmd+=['--cfg',cfg]
        run(name+'-compile',cmd);need(0<raw.stat().st_size<=4096,'broker code bound');brokers[name]=raw
    sys.path.insert(0,str(kernel/'scripts'));from native_smoke import run as smoke
    entropy=os.urandom(32)
    cases=[('positive','requester','broker',None,3),('allow-inheritance','requester','allow-inheritance',51,2),('wide-scope','requester','wide-scope',52,2),('repeat-collect','requester','repeat-collect',66,2),('partial-request','partial','broker',41,1),('requester-exit','early-exit','broker',42,2)]
    for name,client,broker,detail,reclaims in cases:
        dest=work/name;dest.mkdir();first=Path(receipt['artifacts'][client]['path']);second=worker;raw=brokers[broker]
        need(sha(first)==receipt['artifacts'][client]['sha256'],'requester changed')
        payload=dest/'native-c.bin';payload.write_bytes(struct.pack('<8sIIII',b'AENFS001',first.stat().st_size,second.stat().st_size,raw.stat().st_size,0)+entropy+first.read_bytes()+second.read_bytes()+raw.read_bytes())
        run(name+'-kernel',['zig','build','-Dsmp=false','-Dnative-c-image='+str(payload),'-p',str(dest),'--cache-dir',str(kernel/'.zig-cache'),'--global-cache-dir',str(kernel/'.zig-cache/global')])
        context=(f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail}'.encode(),f'NATIVE supervisor result=903 reclaimed={reclaims}'.encode()) if detail else ()
        r['commands'].append({'label':name+'-smoke','function':'native_smoke.run','module_sha256':sources['scripts/native_smoke.py'],'image':str(dest/'aether.iso'),'expected_panic':'native C profile rejected' if detail else None,'panic_context':[x.decode() for x in context],'marker':'AETHER NATIVE FILE SERVICE PASS'});save()
        smoke(dest/'aether.iso',expected_panic=b'native C profile rejected' if detail else None,panic_context=context,marker=b'AETHER NATIVE FILE SERVICE PASS')
        lines=(dest/'native-serial.log').read_text().splitlines()
        if detail:need('AETHER NATIVE FILE SERVICE PASS' not in lines,'negative pass marker')
        else:
            for line in ['NATIVE terminal slot=1 generation=1 kind=1 detail=17','NATIVE terminal slot=1 generation=2 kind=1 detail=33','NATIVE terminal slot=0 generation=1 kind=1 detail=29','NATIVE supervisor result=100 reclaimed=3']:need(line in lines,'missing outcome: '+line)
        r['cases'].append({'case':name,'result':'pass','negative':detail is not None,'requester_sha256':sha(first),'worker_sha256':sha(worker),'broker_sha256':sha(raw),'envelope_sha256':sha(payload),'iso_sha256':sha(dest/'aether.iso'),'serial_sha256':sha(dest/'native-serial.log')});save();print(name+': PASS',flush=True)
    for name,h in sources.items():need(sha(kernel/name)==h,'captured source changed: '+name)
    for name,h in local.items():need(sha(Path(name))==h,'consumer source changed')
    for name,h in receipt['local_sources'].items():need(sha(Path(name))==h,'requester input changed')
    need({str(p.relative_to(sdk)):sha(p) for p in (sdk/'stage').rglob('*') if p.is_file()}==reference['sdk_inputs'],'SDK changed')
    r['artifacts']={'worker.elf':sha(worker),**{p.name:sha(p) for p in brokers.values()}};r['status']='pass'
finally:save()
