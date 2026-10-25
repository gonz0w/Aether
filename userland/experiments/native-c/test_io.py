#!/usr/bin/env python3
"""Native descriptor acceptance and semantic controls; isolated kernel build."""
import argparse,hashlib,json,shutil,subprocess,sys,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--aether',type=Path,required=True);p.add_argument('--sys-init',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--work',type=Path,required=True);args=p.parse_args()
work=args.work.resolve();sdk=args.sdk.resolve();init=args.sys_init.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,reason):
 if not ok:raise RuntimeError(reason)
evidence=json.loads((sdk/'evidence.json').read_text())
require(evidence['probe_variant']=='io','I/O variant required')
require(evidence['io_adapter_sha256']==sha(HERE/'native_io.c') and evidence['probe_sha256']==sha(HERE/'io_probe.c'),'consumer source changed; rebuild')
if evidence.get('native_memory'):
 require(all(sha(HERE/name)==pin for name,pin in evidence['memory_sources'].items()),'memory consumer source changed; rebuild')
artifacts={a['name']:a['sha256'] for a in evidence['artifacts']}
payloads=[('startup','native-c.bin'),('bad-dup','bad-dup.bin')]
if evidence.get('native_memory'):payloads += [('memory-retry','memory-retry.bin')]
for name,file in payloads:
 raw=(sdk/file).read_bytes();require(raw[:8]==b'AENATC01' and hashlib.sha256(raw[40:]).hexdigest()==artifacts[name],'native artifact mismatch')
require(sha(sdk/'native-c.bin')==evidence['envelope_sha256'],'native envelope changed')
work.mkdir(parents=True,exist_ok=False)
shutil.copytree(args.aether,work/'Aether',ignore=lambda p,n:set(n)&{'.git','.zig-cache','zig-out','__pycache__','.DS_Store'})
kernel=work/'Aether';sources={str(p.relative_to(kernel)):sha(p) for p in kernel.rglob('*') if p.is_file() and '.deps' not in p.relative_to(kernel).parts}
inputs=[HERE/'native_io.c',HERE/'io_probe.c',Path(__file__),init/'scripts/build-native-supervisor.py',init/'prototypes/native-supervisor/io.rs',init/'prototypes/native-supervisor/linker.ld']
if evidence.get('native_memory'):inputs += [HERE/'native_memory.c',HERE/'memory_probe.c']
input_pins={str(p):sha(p) for p in inputs};sources.update(input_pins)
(work/'sources.json').write_text(json.dumps(sources,sort_keys=True,indent=2)+'\n');results=[];commands=[]
def run(cmd,label):
 p=subprocess.run(cmd,cwd=kernel,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120);(work/(label+'.log')).write_bytes(p.stdout)
 commands.append(dict(argv=cmd,exit=p.returncode));(work/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');return p.returncode
cases = [('pass','native-c.bin',None),('bad-dup','bad-dup.bin',None),('no-output','native-c.bin','native-no-output'),('skip-zero','native-c.bin','native-skip-zero')]
if evidence.get('native_memory'):
 cases += [('memory-no-grant','native-c.bin','native-memory-no-grant'),('memory-skip-protect','native-c.bin','native-memory-skip-protect'),('memory-retry','memory-retry.bin','native-memory-deny-protect-once'),('memory-retry-control','memory-retry.bin',None),('memory-disabled','native-c.bin',None),('malformed-machine','native-c.bin',None),('malformed-wx','native-c.bin',None),('malformed-length','native-c.bin',None)]
for name,native,flag in cases:
 out=work/'clients'/name
 require(run([sys.executable,str(init/'scripts/build-native-supervisor.py'),str(sdk/native),str(out),'--variant','io'],name+'-client')==0,'client build failed')
 mutation = None
 if name.startswith('malformed-'):
  payload=out/'supervised.bin';raw=bytearray(payload.read_bytes());before=sha(payload)
  require(raw[:8]==b'AENFD001' and raw[48:52]==b'\x7fELF','unexpected producer format')
  if name=='malformed-machine':struct.pack_into('<H',raw,48+18,183)
  elif name=='malformed-length':struct.pack_into('<I',raw,8,0xffffffff)
  else:
   offset=48+struct.unpack_from('<Q',raw,48+32)[0];size,count=struct.unpack_from('<HH',raw,48+54)
   candidates=[offset+i*size for i in range(count) if struct.unpack_from('<I',raw,offset+i*size)[0]==1]
   require(bool(candidates),'no LOAD for mutation');struct.pack_into('<I',raw,candidates[0]+4,7)
  payload.write_bytes(raw);mutation=dict(kind=name,producer_envelope_sha256=before,mutated_envelope_sha256=sha(payload))
 cmd=['zig','build','-Dsmp=false','-Dnative-c-image='+str(out/'supervised.bin'),'-p','zig-out/'+name,'--cache-dir','.zig-cache','--global-cache-dir','.zig-cache/global']
 if evidence.get('native_memory') and name!='memory-disabled':cmd+=['-Dnative-memory=true']
 if flag:cmd+=['-D'+flag+'=true']
 require(run(cmd,name+'-build')==0,'kernel build failed')
 code=run([sys.executable,'scripts/io_smoke.py','zig-out/'+name+'/aether.iso'],name+'-smoke')
 serial=kernel/'zig-out'/name/'native-serial.log';text=serial.read_text();expected='AETHER NATIVE IO PASS' if name in ('pass','memory-retry') else ('AETHER PANIC: invalid supervised ELF' if name in ('malformed-machine','malformed-wx') else 'AETHER PANIC: native C profile rejected')
 require(expected in text.splitlines() and (code==0)==(name in ('pass','memory-retry')) and (name in ('pass','memory-retry') or 'AETHER NATIVE IO PASS' not in text),'wrong semantic outcome: '+name)
 if name.startswith('malformed-'):require('NATIVE MEMORY admitted' not in text and 'NATIVE terminal' not in text,'malformed artifact reached worker admission')
 if evidence.get('native_memory'):
  detail={'memory-no-grant':61,'memory-disabled':61,'memory-skip-protect':73,'memory-retry-control':81}.get(name)
  if detail is not None:require('NATIVE terminal slot=0 generation=1 kind=1 detail='+str(detail) in text.splitlines(),'wrong consumer rejection: '+name)
  if name in ('pass','memory-retry'):
   for generation in (1,2):require('NATIVE terminal slot=0 generation='+str(generation)+' kind=1 detail=0' in text.splitlines(),'missing successful generation')
   require('NATIVE supervisor result=100 reclaimed=2' in text.splitlines(),'missing supervised cleanup')
 shutil.copyfile(serial,work/(name+'-serial.log'))
 results.append(dict(mutation=mutation,case=name,result='pass',smoke_exit=code,expected=expected,native_sha256=sha(sdk/native),envelope_sha256=sha(out/'supervised.bin'),image_sha256=sha(kernel/'zig-out'/name/'aether.iso')))
 (work/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(name+': PASS',flush=True)
require(all(sha(Path(p))==pin for p,pin in input_pins.items()),'producer changed during run')
