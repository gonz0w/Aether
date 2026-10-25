#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Re-stage pinned kernel launch/channel witnesses; never infer POSIX adoption."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

REPO = Path(__file__).resolve().parent.parent
CASES = {'connections': {'positive','small-pool','reserved','bad-third-machine','reject-partial','wrong-data'},
         'coexist': {'positive','repeat-collect','partial-request','requester-exit','small-pool','wrong-data'},
         'process': {'positive','allow-inheritance','wide-scope','repeat-collect','partial-request','requester-exit'},
         'launch': {'positive','wrong-image','bad-machine','reserved','bad-layout'},
         'channel': {'positive','writer-fault','writer-stop','wrong-count'},
         'files': {'positive','wrong-data','truncated-request'},
         'files-writable': {'positive','wrong-data','skip-zero','ignore-rights'},
         'files-writable-memory': {'positive','baseline-flush','corrupt-vector','leak-poll-errno'}}
TOOLS = ('image.py','native_smoke.py','deps.py','emulator.py')
SMOKE = '''import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from native_smoke import run
run(Path(sys.argv[2]),expected_panic=sys.argv[4].encode() if sys.argv[4] else None,
    panic_context=(sys.argv[5].encode(),) if sys.argv[5] else (),marker=sys.argv[3].encode())
'''
def require(ok, message):
    if not ok: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pinned(path, digest):
    require(sha(path)==digest,'input pin mismatch: '+str(path))
    return json.loads(path.read_text())

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--profile',choices=CASES,required=True)
p.add_argument('--producer-kind',choices=('kernel','userland-channel','userland-files','userland-fds','userland-failures','userland-libc','userland-stdio','userland-broker','userland-coexist','userland-connections','userland-shared','userland-inherited','userland-inherited-libc','userland-fileio-libc'),default='kernel')
p.add_argument('--evidence',type=Path,required=True);p.add_argument('--evidence-sha256',required=True)
p.add_argument('--tools-evidence',type=Path,required=True);p.add_argument('--tools-evidence-sha256',required=True)
p.add_argument('--aether',type=Path,required=True);p.add_argument('--root',type=Path,required=True)
a=p.parse_args();kernel=a.aether.resolve();root=a.root.absolute()
evidence=pinned(a.evidence,a.evidence_sha256);tool_evidence=pinned(a.tools_evidence,a.tools_evidence_sha256)
require(evidence['status']=='pass' and tool_evidence['status']=='pass','accepted evidence required')
require(a.profile!='files-writable' or a.producer_kind in ('userland-files','userland-fds','userland-failures','userland-libc','userland-stdio'),'writable profile requires independent userland evidence')
require((a.profile=='files-writable-memory') is (a.producer_kind=='userland-stdio'),'stdio requires explicit memory profile')
cases=evidence['cases'];expected_cases=CASES[a.profile];producer_commands=evidence['commands'];artifact_root=kernel/'zig-out'
require((a.profile=='process') is (a.producer_kind=='userland-broker'),'process requires independent broker evidence')
require((a.profile=='coexist') is (a.producer_kind=='userland-coexist'),'coexist requires independent coexistence evidence')
require((a.profile=='connections') is (a.producer_kind in ('userland-connections','userland-shared','userland-inherited','userland-inherited-libc','userland-fileio-libc')),'connections requires independent connections evidence')
if a.producer_kind in ('userland-broker','userland-coexist','userland-connections','userland-shared','userland-inherited','userland-inherited-libc','userland-fileio-libc'):
    schema='aether-userland.native-'+('fileio-libc' if a.producer_kind=='userland-fileio-libc' else 'inherited-libc' if a.producer_kind=='userland-inherited-libc' else 'inherited' if a.producer_kind=='userland-inherited' else 'shared' if a.producer_kind=='userland-shared' else a.profile if a.profile in ('coexist','connections') else 'broker')+'.v1'
    require(evidence.get('schema')==schema,'wrong broker schema')
    if a.producer_kind=='userland-shared':expected_cases={'positive','parent-first','frozen-offset','early-close','wide-rights','leak-close'}
    if a.producer_kind in ('userland-inherited','userland-inherited-libc','userland-fileio-libc'):expected_cases={'positive','parent-first','rejected-launch','partial-reservation','leaked-reservation','leaked-admission','allow-child-write','wrong-status','repeat-status'}
    if a.producer_kind=='userland-inherited-libc':expected_cases|={'wrong-errno','leak-errno','drop-read','corrupt-read','drop-close'}
    if a.producer_kind=='userland-fileio-libc':expected_cases={'positive','frozen-offset','zero-consumes','wide-rights','skip-write','wrong-errno','leak-errno','drop-read','corrupt-read','drop-close'}
    cases=[dict(c,name=c['case'],status=c['result']) for c in cases]
    producer_commands=[c['argv'] for c in producer_commands if 'argv' in c and c.get('exit')==0]
    artifact_root=kernel.parent
elif a.producer_kind!='kernel':
    consumer_profile={'userland-channel':'channel','userland-files':'files','userland-fds':'files','userland-failures':'files','userland-libc':'files','userland-stdio':'files'}[a.producer_kind]
    require((a.profile==consumer_profile or (a.profile in ('files-writable','files-writable-memory') and consumer_profile=='files')) and evidence.get('schema')=='aether-userland.native-'+consumer_profile+'.v1','wrong consumer schema/profile')
    expected_cases=(CASES['channel']|{'startup-copy','wrong-pattern'}) if consumer_profile=='channel' else {'positive','wrong-data','truncated','wrong-root'}
    if consumer_profile=='files':
        writable=a.profile in ('files-writable','files-writable-memory')
        require(evidence.get('writable',False) is writable,'consumer service mode mismatch')
        services=[c['argv'] for c in evidence['commands'] if c.get('name')=='service-rust' and c.get('exit')==0]
        require(len(services)==1 and any(services[0][i:i+2]==['--cfg','writable'] for i in range(len(services[0])-1)) is writable,'service build mode mismatch')
        if writable:expected_cases=CASES['files-writable']
        descriptors=a.producer_kind in ('userland-fds','userland-failures','userland-libc','userland-stdio')
        failures=a.producer_kind=='userland-failures';libc=a.producer_kind in ('userland-libc','userland-stdio');stdio=a.producer_kind=='userland-stdio'
        for field,value in (('descriptors',descriptors),('fd_failures',failures),('libc_files',libc),('stdio_files',stdio)):
            require(evidence.get(field,False) is value,'consumer mode mismatch: '+field)
        if descriptors:require(writable,'descriptor consumer requires writable profile')
        if failures:
            definitions={'lost-open':(1,None),'lost-write':(2,None),'malformed-close':(3,None),'close-error':(4,None),
                         'ignore-poison':(2,'IGNORE_POISON'),'leak-retain':(4,'LEAK_RETAIN'),'relax-reply':(3,'RELAX_REPLY')}
            expected_cases=set(definitions)
            for case,(number,mutation) in definitions.items():
                clients=[c['argv'] for c in evidence['commands'] if c.get('name')==case+'-compile' and c.get('exit')==0]
                flags={'-DFD_FAILURES','-DFAILURE_MODE='+str(number),'-DWRITABLE'}
                if mutation:flags.add('-D'+mutation)
                require(len(clients)==1 and {v for v in clients[0] if v.startswith('-D')}==flags,'failure client build mismatch: '+case)
        else:
            clients=[c['argv'] for c in evidence['commands'] if c.get('name')=='client-compile' and c.get('exit')==0]
            require(len(clients)==1,'client build required')
            flags=set(v for v in clients[0] if v.startswith('-D'))
            require(('-DDESCRIPTORS' in flags) is (descriptors and not libc) and ('-DLIBC_FILES' in flags) is libc and ('-DSTDIO_FILES' in flags) is stdio and '-DFD_FAILURES' not in flags,'client mode build mismatch')
            if descriptors:require('-DWRITABLE' in flags,'descriptor client requires writable build')
            if libc:
                require('-D_POSIX_C_SOURCE=200809L' in flags,'libc feature declaration required')
                expected_cases=CASES['files-writable-memory'] if stdio else {'positive','wrong-errno','ignore-flags','frozen-offset'}
            elif descriptors:expected_cases={'positive','frozen-offset','early-close','leak-close'}
    cases=[dict(c,name=c['case'],status=c['result']) for c in cases]
    producer_commands=[c['argv'] for c in producer_commands if 'argv' in c and c['exit']==0]
    artifact_root=Path(evidence['output']).resolve()
tool_sources=tool_evidence['kernel_sources'] if tool_evidence.get('schema') in ('aether-userland.native-channel.v1','aether-userland.native-files.v1','aether-userland.native-broker.v1','aether-userland.native-coexist.v1','aether-userland.native-connections.v1','aether-userland.native-shared.v1','aether-userland.native-inherited.v1','aether-userland.native-inherited-libc.v1','aether-userland.native-fileio-libc.v1') else tool_evidence['sources']
implementation_inputs={str(p.relative_to(REPO)):sha(p) for p in (REPO/'mk').iterdir() if p.is_file() and p.suffix in ('.sh','.py','.awk','.mk')}
implementation_inputs[str(Path(__file__).relative_to(REPO))]=sha(Path(__file__))
require(len(cases)==len(expected_cases) and {c['name'] for c in cases}==expected_cases and all(c['status']=='pass' for c in cases),'complete profile case set required')
# Verify every selected ISO before creating outputs. Commands are data used only
# to locate artifacts; no command from an evidence document is executed.
inputs={}
for case in cases:
    name=case['name']
    builds=[c for c in producer_commands if c[:2]==['zig','build'] and '-p' in c and Path(c[c.index('-p')+1]).name==name]
    require(len(builds)==1,'ambiguous producer build')
    build=builds[0]
    require('-Dsmp=false' in build and ('-Dnative-memory=true' in build) is (a.profile=='files-writable-memory') and '-Dnative-memory=false' not in build,'unexpected kernel configuration')
    if a.profile in ('coexist','connections'):
        require(('-Dnative-coexist-small-pool=true' in build) is (name=='small-pool') and '-Dnative-coexist-small-pool=false' not in build,'unexpected coexist pool configuration')
    iso=Path(build[build.index('-p')+1])/'aether.iso'
    require(iso.resolve().is_relative_to(artifact_root),'artifact outside selected producer output')
    require(sha(iso)==case['iso_sha256'],'accepted ISO changed')
    inputs[name]=iso
for name in TOOLS:
    require(sha(kernel/'scripts'/name)==tool_sources['scripts/'+name],'changed producer tool: '+name)
root.mkdir(mode=0o700,parents=False,exist_ok=False)
(root/'producer-results.json').write_text(json.dumps(evidence,indent=2)+'\n')
(root/'tool-results.json').write_text(json.dumps(tool_evidence,indent=2)+'\n')
commands=[]
def run(argv,label,*,cwd=REPO,accept=0):
    argv=[str(x) for x in argv]
    with (root/(label+'.log')).open('wb') as output:
        child=subprocess.Popen(argv,cwd=cwd,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=child.wait(timeout=120)
        finally:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            child.wait(timeout=10)
    commands.append(dict(argv=argv,cwd=str(cwd),exit=code))
    (root/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(code==accept,'unexpected result: '+label)
    return (root/(label+'.log')).read_text(errors='replace')

# Freeze the small build/smoke tool closure and local boot dependencies. Its own
# verifier checks dependency hashes; nothing invokes setup/download.
tools=root/'producer-tools';(tools/'scripts').mkdir(parents=True);(tools/'boot').mkdir()
for name in TOOLS:shutil.copyfile(kernel/'scripts'/name,tools/'scripts'/name)
shutil.copyfile(kernel/'boot/dependencies.json',tools/'boot/dependencies.json')
shutil.copyfile(kernel/'boot/limine.conf',tools/'boot/limine.conf')
shutil.copyfile(kernel/'LICENSE',tools/'LICENSE')
shutil.copytree(kernel/'.deps',tools/'.deps')
tool_pins={str(path.relative_to(tools)):sha(path) for path in tools.rglob('*') if path.is_file()}
(root/'tool-inputs.json').write_text(json.dumps(tool_pins,sort_keys=True,indent=2)+'\n')
results=[];names=('aether','protection.bin','display.bin','lifecycle.bin','smp-supervisor.bin')
for case in cases:
    name=case['name'];work=root/name;work.mkdir(mode=0o700)
    run(['make','-s','-f','mk/pkg.mk','ROOT='+str(work),'init-root'],name+'-init')
    run(['xorriso','-osirrox','on','-indev',inputs[name],'-extract','/boot',work/'accepted-boot'],name+'-extract')
    run(['xorriso','-osirrox','on','-indev',inputs[name],'-extract','/limine.conf',work/'accepted-config'],name+'-config')
    require((work/'accepted-config').read_bytes()==(tools/'boot/limine.conf').read_bytes()+b'    module_path: boot():/boot/native-c.bin\n','boot config changed')
    boot=work/'accepted-boot'
    require((boot/'LICENSE-Aether.txt').read_bytes()==(tools/'LICENSE').read_bytes(),'license differs from accepted image')
    require(sha(boot/'native-c.bin')==case['envelope_sha256'],'envelope mismatch')
    run(['sh','mk/aether-boot-v2.sh','stage',work,*[boot/n for n in names],*[sha(boot/n) for n in names],a.evidence_sha256],name+'-base')
    base_pin=sha(work/'aether-boot-v2/receipt.kv')
    transport_profile=a.profile+'-small-pool' if a.profile in ('coexist','connections') and name=='small-pool' else a.profile
    stage=[sys.executable,'mk/aether-supervised.py','stage-'+transport_profile,work,base_pin,boot/'native-c.bin',case['envelope_sha256']]
    bundle=work/('aether-'+transport_profile+'-v1')
    if name in ('bad-machine','reserved','bad-third-machine'):
        text=run(stage,name+'-rejected',accept=1)
        expected='native ELF header' if name in ('bad-machine','bad-third-machine') else 'three-image envelope' if a.profile=='connections' else 'dual-image envelope'
        require(expected in text and not bundle.exists(),'wrong structural rejection')
        results.append(dict(case=name,result='rejected-before-publication',reason=expected));continue
    run(stage,name+'-stage');receipt=sha(bundle/'receipt.json')
    run([sys.executable,'mk/aether-supervised.py','verify',bundle,receipt],name+'-verify')
    require(all(sha(bundle/n)==sha(boot/n) for n in (*names,'native-c.bin')),'transported bytes changed')
    image=work/'boot-check/aether.iso'
    run([sys.executable,tools/'scripts/image.py',bundle/'aether',image,*[bundle/n for n in names[1:]],bundle/'native-c.bin'],name+'-image',cwd=tools)
    panic='';context=''
    if name=='wrong-image':panic='native C profile rejected';context='NATIVE supervisor result=411 reclaimed=0'
    if name in ('wrong-count','wrong-pattern'):panic='native C profile rejected';context='NATIVE supervisor result=511 reclaimed=0'
    if name=='bad-layout':panic='invalid launch layout';context='AETHER M1 PASS'
    if name in ('wrong-data','truncated-request','truncated','wrong-root','skip-zero','ignore-rights','frozen-offset','early-close','leak-close','ignore-poison','leak-retain','relax-reply','wrong-errno','ignore-flags','baseline-flush','corrupt-vector','leak-poll-errno'):panic='native C profile rejected';context='NATIVE supervisor result=611 reclaimed=0'
    if a.profile in ('process','coexist') and name!='positive':
        panic='native C profile rejected';context='NATIVE supervisor result=903 reclaimed='+('1' if name in ('partial-request','small-pool') else '2')
    if a.profile=='connections' and a.producer_kind not in ('userland-shared','userland-inherited','userland-inherited-libc','userland-fileio-libc') and name not in ('positive','reserved','bad-third-machine'):
        panic='native C profile rejected';context='NATIVE supervisor result='+str({'small-pool':950,'reject-partial':959,'wrong-data':960}[name])+' reclaimed=0'
    if a.producer_kind=='userland-shared' and name not in ('positive','parent-first'):
        panic='native C profile rejected';context='NATIVE supervisor result='+('975' if name=='leak-close' else '970')+' reclaimed=0'
    if a.producer_kind in ('userland-inherited','userland-inherited-libc','userland-fileio-libc') and name not in ('positive','parent-first','rejected-launch','partial-reservation'):
        panic='native C profile rejected';context='NATIVE supervisor result=970 reclaimed=0'
    if a.producer_kind=='userland-fileio-libc' and name!='positive':
        panic='native C profile rejected';context='NATIVE supervisor result='+('985' if name=='skip-write' else '970')+' reclaimed=0'
    marker='AETHER NATIVE '+('FILE SERVICE' if a.profile in ('process','files','files-writable','files-writable-memory') else a.profile.upper())+' PASS'
    if a.profile=='coexist':marker='AETHER NATIVE COEXIST PASS'
    run([sys.executable,'-c',SMOKE,tools/'scripts',image,marker,panic,context],name+'-smoke',cwd=tools)
    serial=image.parent/'native-serial.log';lines=serial.read_text().splitlines()
    if not panic:require(marker in lines and 'NATIVE supervisor result=100 reclaimed='+('6' if a.profile=='connections' else '3') in lines,'cleanup missing')
    else:
        require(marker not in lines and 'AETHER PANIC: '+panic in lines,'negative accepted')
        details={'wrong-image':(1,92),'wrong-count':(1,103),'wrong-pattern':(1,103),'wrong-data':(1,211),'truncated-request':(0,121),'truncated':(0,121),'wrong-root':(1,150),'skip-zero':(1,219),'ignore-rights':(1,218),'frozen-offset':(1,207),'early-close':(1,213),'leak-close':(1,216),'ignore-poison':(1,195),'leak-retain':(1,193),'relax-reply':(1,189),'wrong-errno':(1,200),'ignore-flags':(1,201),'baseline-flush':(1,189),'corrupt-vector':(1,186),'leak-poll-errno':(1,196),'allow-inheritance':(0,51),'wide-scope':(0,52),'repeat-collect':(0,66),'partial-request':(0,41),'requester-exit':(0,42),'small-pool':(0,59),'wide-rights':(2,48),'leaked-reservation':(0,70),'leaked-admission':(0,70),'allow-child-write':(0,66),'wrong-status':(0,75),'repeat-status':(0,76),'leak-errno':(0,82),'drop-read':(0,122),'corrupt-read':(0,122),'drop-close':(0,122),'zero-consumes':(0,90)}
        if name in details and not (a.profile=='connections' and name=='small-pool') and not (a.producer_kind=='userland-shared' and name=='leak-close'):
            slot,detail=details[name]
            if a.producer_kind=='userland-fileio-libc' and name=='frozen-offset':slot,detail=2,91
            if a.producer_kind=='userland-fileio-libc' and name=='wide-rights':slot,detail=2,93
            if a.producer_kind in ('userland-inherited-libc','userland-fileio-libc') and name=='wrong-errno':slot,detail=0,80
            if a.producer_kind=='userland-shared' and name in ('frozen-offset','early-close'):slot,detail=0,50
            if a.profile=='connections' and name=='wrong-data':slot,detail=2,44
            if a.profile=='coexist' and name=='wrong-data':slot,detail=0,78
            if a.producer_kind=='userland-libc' and name=='frozen-offset':detail=205
            if a.producer_kind=='userland-files' and name=='wrong-data': detail=205 if a.profile in ('files-writable','files-writable-memory') else 171
            require(f'NATIVE terminal slot={slot} generation=1 kind=1 detail={detail}' in lines,'specific rejection missing')
    if a.profile in ('process','coexist') and name=='positive':
        for slot,generation,detail in ((1,1,17),(1,2,17 if a.profile=='coexist' else 33),(0,1,29)):
            require(f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={detail}' in lines,'broker terminal missing')
    if a.profile=='connections' and not panic:
        terminals=[line for line in lines if line.startswith('NATIVE terminal slot=')]
        order=((0,29),(2,29),(1,17)) if name=='parent-first' else ((2,29),(0,29),(1,17))
        expected=[f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={detail}' for generation in (1,2) for slot,detail in order]
        require(terminals==expected,'connections terminal ordering missing')
    results.append(dict(case=name,result='expected-rejection' if panic else 'pass',receipt_sha256=receipt,image_sha256=sha(image),serial_sha256=sha(serial)))
# Detect sibling/tool input drift, without mutating or rebuilding those siblings.
require(sha(a.evidence)==a.evidence_sha256 and sha(a.tools_evidence)==a.tools_evidence_sha256,'evidence changed during run')
require(all(sha(tools/name)==pin for name,pin in tool_pins.items()),'frozen tool changed during run')
require(all(sha(REPO/name)==pin for name,pin in implementation_inputs.items()),'package implementation changed during run')
require(all(sha(inputs[c['name']])==c['iso_sha256'] for c in cases),'accepted ISO changed during run')
(root/'result.json').write_text(json.dumps(dict(result='pass',profile=a.profile,producer_kind=a.producer_kind,scope='bounded profile transport, not POSIX or sys-init channel adoption',implementation_inputs=implementation_inputs,producer_results_sha256=a.evidence_sha256,tool_results_sha256=a.tools_evidence_sha256,transport_sha256=sha(REPO/'mk/aether-supervised.py'),harness_sha256=sha(Path(__file__)),cases=results),indent=2)+'\n')
print('PASS: '+a.profile+' transport and all '+str(len(results))+' case outcomes; retained '+str(root))
