# SPDX-License-Identifier: BSD-2-Clause
from pathlib import Path
import hashlib,json,shutil,sys,tempfile
from build import Parser
parser = Parser(description="Host-only Toybox finalizer checks; Python 3.12+.")
parser.add_argument("--version", action="version", version="toybox-finalizer-check 0.1.0")
parser.parse_args()
root=Path.cwd();out=Path(tempfile.mkdtemp(prefix='toybox-finalizer-',dir=root/'build'));print(out,flush=True)
sys.path.insert(0,str(root/'experiments/command-runner'))
from process import run,clean_env
sources=[root/'experiments/toybox-reference'/n for n in ('finalizer.c','finalizer.h','finalizer-controls.c')]
sources += [root/'docs/evidence/toybox-finalizer-2026-09-06/change-review.md',Path(__file__).resolve(),root/'experiments/command-runner/process.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in sources}
for p in sources:shutil.copy2(p,out/p.name)
(out/'inputs.json').write_text(json.dumps(hashes,indent=2)+'\n')
ref=json.loads((root/'experiments/musl-reference/tools.lock.json').read_text())['tools']['clang'];assert sha(Path(ref['path']))==ref['sha256']
env=clean_env(out)
def check(label,argv,success=True):
 r=run(argv,cwd=root,env=env,work=out,label=label,timeout=60)
 assert r.record['complete'] and ((r.returncode==0) if success else r.returncode!=0),label
 return r
check('format',['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang-format','--dry-run','--Werror','--style=file:docs/quality/clang-format.yaml']+[str(out/p.name) for p in sources[:3]])
flags=[ref['path'],'-std=c17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=all','-I',str(out)]
def build(name,p):
 check(name+'-compile',flags+[str(p),str(out/'finalizer-controls.c'),'-o',str(out/name)])
build('control',out/'finalizer.c')
r=check('control',[str(out/'control')]);assert r.stdout==b'PASS: 2560 finalizer scenarios and 6 invalid-input controls\n' and not r.stderr
text=(out/'finalizer.c').read_text()
mutants={'lost-status':('s->status = status <= 255 ? status : 1;','s->status = 0;'),
         'ignore-unknown':('return result != TF_UNKNOWN;','return 1;'),
         'close-order':('!close_role(s, ops, ctx, 0) || !close_role(s, ops, ctx, 1)','!close_role(s, ops, ctx, 1) || !close_role(s, ops, ctx, 0)')}
for name,(old,new) in mutants.items():
 assert text.count(old)==1,name
 p=out/(name+'.c');p.write_text(text.replace(old,new));build(name,p)
 r=check(name,[str(out/name)],False);assert b'Assertion failed' in r.stderr,name
for p,h in hashes.items():assert sha(Path(p))==h
(out/'summary.json').write_text(json.dumps({'status':'pass','scope':'Host UBSan callback candidate, not native','matrix_cases':2560,'invalid_controls':6,'mutants_rejected':list(mutants),'inputs':hashes,'python':sys.version},indent=2)+'\n')
print('PASS: 2560 scenarios, 6 invalid controls, 3 semantic mutants')
