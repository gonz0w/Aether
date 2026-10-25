#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Combined Toybox Linux reference checks; Python 3.12+."""
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import uuid
from build import Parser, require, sha
from test import IMAGE, PODMAN
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import run, clean_env


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='toybox-composed 0.1.0')
    parser.parse_args()
    old = ROOT / 'build/toybox-reference-1nutoq_n'
    receipt = json.loads((old / 'evidence.json').read_text())
    prior = ROOT / 'docs/evidence/toybox-standalone-2026-09-06'
    require(sha(old / 'evidence.json') == sha(prior / 'builds/cat/evidence.json'), 'receipt drift')
    for name, digest in receipt['files'].items():
        require(sha(Path(name)) == digest, 'input drift')
    sdk = Path(json.loads((ROOT / 'experiments/musl-reference/evidence.json').read_text())['output'])
    for name, digest in receipt['sdk_inputs'].items():
        require(sha(sdk / name) == digest, 'SDK drift')
    for tool in receipt['tools'].values():
        require(sha(Path(tool['path'])) == tool['sha256'], 'tool drift')
    src = sdk / 'musl-1.2.6'
    original = src / 'src/stdio/__stdio_write.c'
    audit = json.loads((ROOT / 'docs/evidence/toybox-native-sdk-2026-09-06/summary.json').read_text())
    archive = ROOT / 'build/musl-audit/musl-1.2.6.tar.gz'
    require(sha(archive) == audit['archive_sha256'], 'archive drift')
    with tarfile.open(archive) as tar:
        require(tar.extractfile('musl-1.2.6/src/stdio/__stdio_write.c').read() == original.read_bytes(), 'source drift')
    out = Path(tempfile.mkdtemp(prefix='toybox-composed-', dir=ROOT / 'build'))
    print(out, flush=True)
    inputs = [Path(__file__), original, ROOT / 'experiments/command-runner/process.py',
              ROOT / 'docs/evidence/toybox-composed-2026-09-06/change-review.md']
    for n in ('composed.c', 'session.c', 'session.h', 'vector.c', 'vector.h', 'finalizer.c', 'finalizer.h', 'mask.c', 'mask.h', 'stdio-loop.h'):
        inputs.append(Path(__file__).with_name(n))
    for directory in ('src/include', 'src/internal', 'arch/x86_64', 'arch/generic', 'include'):
        inputs += [p for p in (src / directory).rglob('*') if p.is_file()]
        shutil.copytree(src / directory, out / 'musl' / directory)
    hashes = {str(p): sha(p) for p in inputs}
    for p in inputs[:14]:
        shutil.copy2(p, out / p.name)
    shutil.copy2(old / 'cc.py', out / 'cc.py')
    shutil.copy2(src / 'COPYRIGHT', out / 'COPYRIGHT')
    (out / 'inputs.json').write_text(json.dumps(hashes, indent=2) + '\n')
    text = original.read_text()
    require(text.count('syscall(SYS_writev,') == 1, 'stdio anchor')
    (out / 'stdio.c').write_text(text.replace('syscall(SYS_writev,', 'fixture_writev('))
    objects = sorted((old / 'toybox-0.8.14/generated/unstripped/obj').glob('*.o'))
    ordered = [p for p in objects if p.name.startswith('lib_')]
    ordered += [next(p for p in objects if p.name == n) for n in ('main.o', 'cat.o')]
    require(len(ordered) == len(objects), 'object inventory')
    shutil.copytree(old / 'toybox-0.8.14/generated/unstripped/obj', out / 'objects')
    hashes.update({str(p): sha(p) for p in objects})
    (out / 'inputs.json').write_text(json.dumps(hashes, indent=2) + '\n')
    env = clean_env(out)
    def checked(label, argv):
        r = run(argv, cwd=ROOT, env=env, work=out, label=label, timeout=60)
        require(r.record['complete'] and r.returncode == 0, label)
        return r
    names = ('composed', 'session', 'vector', 'finalizer', 'mask')
    checked('format', ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang-format', '--dry-run', '--Werror',
        '--style=file:docs/quality/clang-format.yaml'] + [str(out / (n+'.c')) for n in names])
    base = [str(out / 'cc.py'), '-std=c17', '-O1', '-Wall', '-Wextra', '-Werror', '-I', str(out)]
    for n in names:
        checked(n+'-compile', base + ['-c', str(out / (n+'.c')), '-o', str(out / (n+'.o'))])
    internal = ['-I'+str(out/'musl'/n) for n in ('src/include','src/internal','arch/x86_64','arch/generic')]
    checked('stdio-compile', base + internal + ['-Wno-sign-compare','-Wno-unused-parameter',
        '-include',str(out/'stdio-loop.h'),'-c',str(out/'stdio.c'),'-o',str(out/'stdio.o')])
    link = [str(out/'cc.py'),'-Wl,--gc-sections','-Wl,-z,noexecstack','-Wl,--no-undefined']
    objargs = [str(out/'objects'/p.name) for p in ordered]
    checked('control-link',link+objargs+['-o',str(out/'control')])
    require(sha(out/'control')==receipt['elf_sha256'],'baseline ELF mismatch')
    wraps = ['-Wl,--wrap='+n for n in ('main','umask','read','write','fflush','_exit')]
    added = [str(out/(n+'.o')) for n in names]+[str(out/'stdio.o')]
    checked('candidate-link',link+objargs+added+wraps+['-o',str(out/'candidate')])
    checked('headers',[receipt['tools']['readelf']['path'],'-h','-l',str(out/'candidate')])
    body=(out/'composed.c').read_text()
    require(body.count('return old;')==1,'mask mutant anchor')
    (out/'mask-mutant.c').write_text(body.replace('return old;','return 0;'))
    checked('mask-mutant-compile',base+['-c',str(out/'mask-mutant.c'),'-o',str(out/'mask-mutant.o')])
    mutant_added=[str(out/'mask-mutant.o')]+[str(out/(n+'.o')) for n in names if n!='composed']+[str(out/'stdio.o')]
    checked('mask-mutant-link',link+objargs+mutant_added+wraps+['-o',str(out/'mask-mutant')])

    report={'status':'incomplete','scope':'Combined Toybox Linux instrumentation; not native',
            'inputs':hashes,'image':IMAGE,'python':sys.version,'control_matches_original':True,
            'candidate_sha256':sha(out/'candidate'),'stdio_patch_sha256':sha(out/'stdio.c'),'cases':[]}
    def save():
        (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    payload=b'a\x00b\n'+bytes(range(128,140))
    obs=b'OBS masks=2 restored=77 flush=1 closes=012 consumed=7 poison=0 status=0\n'
    cases=[('empty','baseline',b'',[],0,b'',obs),
           ('binary','baseline',payload,[],0,payload,obs),
           ('buffered','baseline',b'a\nb\n',['-e'],0,b'a$\nb$\n',obs),
           ('lost','lost-ack',payload,[],1,payload[:2],b'OBS masks=2 restored=77 flush=1 closes= consumed=7 poison=1 status=1\n'),
           ('close-error','close-error',payload,[],1,payload,b'fixture cleanup\nOBS masks=2 restored=77 flush=1 closes=012 consumed=7 poison=0 status=1\n'),
           ('close-unknown','close-unknown',payload,[],1,payload,b'OBS masks=2 restored=77 flush=1 closes=0 consumed=7 poison=1 status=1\n'),
           ('diagnostic-error','diagnostic-error',payload,[],1,payload,b'OBS masks=2 restored=77 flush=1 closes=012 consumed=7 poison=0 status=1\n'),
           ('invalid-mask','invalid-mask',payload,[],120,b'',b'OBS init-rejected\n'),
           ('mask-mutant','baseline',payload,[],124,payload,b'')]
    save()
    for label,mode,data,args,status,output,diagnostic in cases:
        container='userland-composed-'+uuid.uuid4().hex
        argv=[PODMAN,'run','--name',container,'--rm','-i','--pull=never','--network=none','--read-only',
              '--cap-drop=all','--security-opt=no-new-privileges','--user=65534:65534','--memory=512m','--pids-limit=32',
              '--mount','type=bind,src='+str(out)+',dst=/inputs,ro=true','--env','LC_ALL=C','--env','TOYBOX_COMPOSED='+mode,
              '--entrypoint=/usr/bin/qemu-x86_64',IMAGE,'/inputs/'+('mask-mutant' if label=='mask-mutant' else 'candidate')]+args
        try:
            r=run(argv,cwd=ROOT,env=dict(env,HOME=os.environ['HOME']),work=out,label=label,timeout=60,input=data)
        finally:
            cleanup=run([PODMAN,'rm','--force','--ignore',container],cwd=ROOT,env=dict(env,HOME=os.environ['HOME']),
                        work=out,label=label+'-cleanup',timeout=15)
        ok=r.record['complete'] and cleanup.record['complete'] and cleanup.returncode==0 and r.returncode==status and r.stdout==output and r.stderr==diagnostic
        report['cases'].append({'name':label,'pass':bool(ok),'expected_status':status,'expected_stdout_hex':output.hex(),'expected_stderr':diagnostic.decode()})
        save()
        require(ok,label+' failed; see '+str(out))
    # Altered observer/status expectations cannot accept these actual outcomes.
    require(r.returncode != 0 and r.stderr != b'OBS masks=0\n','oracle control')
    for p,digest in hashes.items():
        require(sha(Path(p))==digest,'input changed')
    report.update(status='pass',wrong_status_and_trace_rejected=True)
    save()
    print('[PASS] eight combined Toybox cases, mask mutant and oracle controls')


if __name__ == '__main__':
    main()
