#!/usr/bin/env python3
"""Run the five native supervision cases in a fresh isolated Aether checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from bounded_tools import run_completed
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--aether',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
a.work=a.work.resolve();a.native=a.native.resolve();a.aether=a.aether.resolve()
a.work.mkdir(parents=True,exist_ok=False)
def ignore(path,names):return set(names)&{'.git','.zig-cache','zig-out','__pycache__','.DS_Store'}
shutil.copytree(a.aether,a.work/'Aether',ignore=ignore)
kernel=a.work/'Aether';results=[];commands=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
sources={str(f.relative_to(kernel)):sha(f) for f in kernel.rglob('*') if f.is_file() and '.deps' not in f.relative_to(kernel).parts}
(a.work/'sources.json').write_text(json.dumps(sources,sort_keys=True,indent=2)+'\n')
for rel in ['prototypes/native-supervisor/main.rs','prototypes/native-supervisor/linker.ld','scripts/build-native-supervisor.py','scripts/bounded_tools.py','tests/native-supervision.py']:
 sources['sys-init/'+rel]=sha(ROOT/rel)
(a.work/'producer-sources.json').write_text(json.dumps(sources,sort_keys=True,indent=2)+'\n')
def run(cmd,label):
    proc=run_completed(cmd,a.work/(label+'.log'),__file__,cwd=kernel,timeout=120)
    commands.append(dict(argv=cmd,exit=proc.returncode));(a.work/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    return proc.returncode
for variant,flag,needle in [('pass',None,'AETHER NATIVE SUPERVISION PASS'),('wrong_detail',None,'native C profile rejected'),('fault_entry',None,'native supervisor terminated'),('pass','native-no-output','native C profile rejected'),('pass','native-skip-zero','native C profile rejected')]:
 name=flag or variant;out=a.work/'clients'/name
 if run([sys.executable,str(ROOT/'scripts/build-native-supervisor.py'),str(a.native),str(out),'--variant',variant],name+'-client'):raise SystemExit('client build failed')
 cmd=['zig','build','-Dsmp=false','-Dnative-c-image='+str(out/'supervised.bin'),'-p','zig-out/'+name,'--cache-dir','.zig-cache','--global-cache-dir','.zig-cache/global']
 if flag:cmd+=['-D'+flag+'=true']
 if run(cmd,name+'-build'):raise SystemExit('kernel build failed')
 code=run([sys.executable,'scripts/supervised_smoke.py','zig-out/'+name+'/aether.iso'],name+'-smoke')
 serial=kernel/'zig-out'/name/'native-serial.log';text=serial.read_text()
 expected = needle if name=='pass' else 'AETHER PANIC: '+needle
 if expected not in text.splitlines() or (code==0)!=(name=='pass') or (name!='pass' and 'AETHER NATIVE SUPERVISION PASS' in text):raise SystemExit('unexpected semantic outcome: '+name)
 shutil.copyfile(serial,a.work/(name+'-serial.log'))
 results.append(dict(case=name,result='pass',smoke_exit=code,expected=needle,image_sha256=sha(kernel/'zig-out'/name/'aether.iso'),native_sha256=sha(a.native),envelope_sha256=sha(out/'supervised.bin')))
 (a.work/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(name+': PASS',flush=True)
