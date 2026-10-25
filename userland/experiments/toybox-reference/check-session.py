# SPDX-License-Identifier: BSD-2-Clause
from pathlib import Path
import hashlib,json,shutil,sys,tempfile
from build import Parser
parser = Parser(description="Host-only Toybox session checks; Python 3.12+.")
parser.add_argument("--version", action="version", version="toybox-session-check 0.1.0")
parser.parse_args()
root=Path.cwd();out=Path(tempfile.mkdtemp(prefix='toybox-session-',dir=root/'build'));print(out,flush=True)
sys.path.insert(0,str(root/'experiments/command-runner'))
from process import run,clean_env
sources=[root/'experiments/toybox-reference'/n for n in ('session.c','session.h','session-controls.c','vector.c','vector.h','finalizer.c','finalizer.h')]
sources += [root/'docs/evidence/toybox-session-2026-09-06/change-review.md',Path(__file__).resolve(),root/'experiments/command-runner/process.py']
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
check('format',['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang-format','--dry-run','--Werror','--style=file:docs/quality/clang-format.yaml']+[str(out/p.name) for p in sources[:7]])
flags=[ref['path'],'-std=c17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=all','-I',str(out)]
def build(name,p):
 check(name+'-compile',flags+[str(p),str(out/'session-controls.c'),str(out/'vector.c'),str(out/'finalizer.c'),'-o',str(out/name)])
build('control',out/'session.c')
r=check('control',[str(out/'control')]);assert r.stdout==b'PASS: 4096 session scenarios and 4 boundary controls\n' and not r.stderr
text=(out/'session.c').read_text()
mutants={'forget-initial-poison':('if (s->io.poisoned || s->io.busy)', 'if (s->io.busy)'),
         'lose-close-poison':('c->state->io.poisoned = 1;', 'c->state->io.poisoned = 0;'),
         'allow-post-finish-write':('if (s->finish.started)\n        return (struct tv_reply){1, 0, -EBADF};', 'if (0)\n        return (struct tv_reply){1, 0, -EBADF};')}
for name,(old,new) in mutants.items():
 assert text.count(old)==1,name
 p=out/(name+'.c');p.write_text(text.replace(old,new));build(name,p)
 r=check(name,[str(out/name)],False);assert b'Assertion failed' in r.stderr,name
for p,h in hashes.items():assert sha(Path(p))==h
(out/'summary.json').write_text(json.dumps({'status':'pass','scope':'Host UBSan callback candidate, not native','matrix_cases':4096,'boundary_controls':4,'mutants_rejected':list(mutants),'inputs':hashes,'python':sys.version},indent=2)+'\n')
print('PASS: 4096 scenarios, 4 boundary controls, 3 semantic mutants')
