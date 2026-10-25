#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Bounded script semantics in Linux emulation, with explicit helper exec boundary."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import types
import sys
import tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
build=Path(sys.argv[1]).resolve()
e=json.loads((build/'evidence.json').read_text())
require(sha(build/'obj/src/dash')==e['elf_sha256'],'dash changed')
for name,digest in e['files'].items():require(sha(build/name)==digest,'build input changed: '+name)
sdk=Path(json.loads((ROOT/'experiments/musl-reference/evidence.json').read_text())['output'])
require({str(p.relative_to(sdk)):sha(p) for p in (sdk/'stage').rglob('*') if p.is_file()}==e['sdk_inputs'],'SDK changed')
tools=json.loads((ROOT/'experiments/musl-reference/tools.lock.json').read_text())['tools']
for name,tool in tools.items():require(sha(Path(tool['path']))==tool['sha256'],'tool changed: '+name)
out=Path(tempfile.mkdtemp(prefix='dash-cases-',dir=ROOT/'build'))
print(out,flush=True)
container_module=runpy.run_path(str(HERE/'container-process.py'))
descriptor=container_module['selected_descriptor'](out)
commands=[]
def run(name,cmd,status=0):
    case_work=out/(name+'-container')
    case_work.mkdir()
    client=container_module['Client'](descriptor,case_work)
    state=container_module['run_container'](client,e['image_id'],cmd,case_work,inputs=out)
    require(state['complete'],name+': container lifecycle incomplete; '+str(case_work))
    r=types.SimpleNamespace(returncode=state['guest_exit'],stdout=(case_work/'guest.stdout').read_bytes(),stderr=(case_work/'guest.stderr').read_bytes())
    (out/(name+'.stdout')).write_bytes(r.stdout)
    (out/(name+'.trace')).write_bytes(r.stderr)
    commands.append({'case':name,'argv':[descriptor['path'],'--url',descriptor['url'],'--identity',descriptor['identity'],'start','--attach',state['container_id']],'guest_argv':cmd,'container_receipt':str(case_work/'container.json'),'exit':r.returncode,'expected_exit':status})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(r.returncode==status,name+' status: '+str(r.returncode)+'; '+str(out))
    return r
shutil.copyfile(build/'obj/src/dash',out/'dash');(out/'dash').chmod(0o755)
helper_cmd=[str(build/'cc.py'),'-O2','-Wall','-Wextra','-Werror','-fstack-protector-strong',str(HERE/'helper.c'),'-o',str(out/'helper')]
host_build=runpy.run_path(str(HERE/'host-build.py'))
helper_result=host_build['compile_helper'](helper_cmd,out)
commands.append({'case':'helper-build','argv':helper_cmd,'exit':helper_result.returncode,'expected_exit':0})
(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
(out/'not-executable').write_text('exit 0\n');(out/'not-executable').chmod(0o644)
q='/usr/bin/qemu-x86_64 /inputs/helper'
cases=[
 ('argv',f'WITNESS=value {q} argv "a b" "*"\n',0,b'argv ok\n',None),
 ('wait',f'{q} status &\np=$!\nwait "$p"\ns=$?\n[ "$s" -eq 7 ] || exit 20\nprintf "wait ok\\n"\n',0,b'wait ok\n',None),
 ('pipeline',f'printf "pipe data\\n" | {q} copy | {q} copy\n',0,b'pipe data\n',None),
 ('substitution',f'x=$({q} argv "a b" "*")\n[ "$x" = "argv ok" ] || exit 21\nprintf "substitution ok\\n"\n',0,b'substitution ok\n',None),
 ('redirection',f'exec 3>/scratch/data\nexec 4>&3\nprintf A >&3\nprintf B >&4\nexec 3>&- 4>&-\n{q} copy </scratch/data\n',0,b'AB',None),
 ('fd-closure',f'{q} closed\ns=$?\n[ "$s" -eq 0 ] || exit 22\nprintf "closed ok\\n"\n',0,b'closed ok\n',None),
 ('fd-leak-control',f'exec 9>/scratch/leak\n{q} closed\ns=$?\n[ "$s" -eq 0 ] || exit 22\n',22,b'',None),
 ('early-reader',f'set -o pipefail\n{q} pump | {q} one\ns=$?\n[ "$s" -eq 42 ] || exit 23\nprintf "epipe ok\\n"\n',0,b'epipe ok\n',None),
 ('failed-exec','/inputs/missing\na=$?\n/inputs/not-executable\nb=$?\n[ "$a" -eq 127 ] && [ "$b" -eq 126 ] || exit 24\nprintf "exec errors ok\\n"\n',0,b'exec errors ok\n',b'Permission denied'),
 ('denied-redirection','(printf wrong >/inputs/denied)\ns=$?\n[ "$s" -ne 0 ] || exit 25\nprintf "denied ok\\n"\n',0,b'denied ok\n',b'cannot create'),
 ('signal-table','[ "$(kill -l 10)" = USR1 ] || exit 26\ntrap \'printf "signal ok\\n"\' USR1\nkill -USR1 $$\n',0,b'signal ok\n',None),
 ('syntax-error','if then\n',2,b'',b'Syntax error'),
]
base=['/usr/bin/qemu-x86_64','-strace','/inputs/dash']
results=[]
for name,script,status,stdout,diagnostic in cases:
    (out/(name+'.sh')).write_text(script)
    r=run(name,base+['/inputs/'+name+'.sh'],status)
    require(r.stdout==stdout,name+' output mismatch')
    if diagnostic:require(diagnostic in r.stderr,name+' diagnostic missing')
    calls=sorted(set(re.findall(rb'\b([a-z][a-z0-9_]+)\(',r.stderr)))
    results.append({'case':name,'exit':status,'stdout_sha256':sha(out/(name+'.stdout')),'trace_sha256':sha(out/(name+'.trace')),'script_sha256':sha(out/(name+'.sh')),'syscalls':[c.decode() for c in calls]})
(out/'evidence.json').write_text(json.dumps({'schema':'aether-userland.dash-cases.v1','scope':'QEMU Linux script tests; external helpers invoked through explicit native qemu executable, no binfmt assumption or Aether execution','output':str(out),'build_evidence_sha256':sha(build/'evidence.json'),'dash_sha256':sha(out/'dash'),'helper_sha256':sha(out/'helper'),'helper_source_sha256':sha(HERE/'helper.c'),'runner_sha256':sha(Path(__file__)),'container_adapter_sha256':sha(HERE/'container-process.py'),'container_client':descriptor,'host_build_sha256':sha(HERE/'host-build.py'),'process_helper_sha256':sha(ROOT/'experiments/command-runner/process.py'),'image_id':e['image_id'],'commands':commands,'results':results},indent=2)+'\n')
print('Twelve dash reference outcomes passed: '+str(out))
