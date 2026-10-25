#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Rebuild captured cat backends and compare complete native payload bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/command-runner'))
from process import clean_env, run


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    args = parser.parse_args()
    snapshot = args.snapshot.resolve()
    kernel = snapshot / 'producer'
    work = Path(tempfile.mkdtemp(prefix='cat-backend-', dir=ROOT / 'build'))
    report = dict(status='incomplete', commands=[], comparisons=[], work=str(work))
    def save():
        (work / 'results.json').write_text(json.dumps(report, indent=2)+'\n')
    def need(ok, message):
        if not ok:
            raise RuntimeError(message)
    print(work, flush=True)
    save()
    try:
        intake = json.loads((snapshot / 'intake.json').read_text())
        for name, digest in intake['pins'].items():
            need(sha(snapshot/name) == digest, 'snapshot drift: '+name)
        receipt_path = kernel/'docs/evidence/toybox-native-cat-2026-09-07/command-results.json'
        receipt = json.loads(receipt_path.read_text())
        base = kernel/'docs/evidence/toybox-native-link-2026-09-07'
        baseline = json.loads((base/'results.json').read_text())
        sdk = base/'inputs/sdk-stage'
        for name, digest in baseline['sdk_inputs'].items():
            need(sha(sdk/name) == digest, 'SDK drift')
        host = json.loads((ROOT/'experiments/command-runner/host-tools.lock.json').read_text())
        for tool in [*host.values(), *baseline['tools'].values()]:
            need(sha(Path(tool['path'])) == tool['sha256'], 'tool drift')
        report.update(intake_sha256=sha(snapshot/'intake.json'), recipe_receipt_sha256=sha(receipt_path),
                      driver_sha256=sha(Path(__file__)),host_tools=host,tools=baseline['tools'],
                      sdk_inputs=baseline['sdk_inputs'])
        labels = ['helper2.o','backend-adapter.o','cat-backend.a','cat-backend.elf',
                  'cat-empty-backend.a','cat-empty-backend.elf']
        env = clean_env(work)
        (work/'empty-root').mkdir()
        for label in labels:
            selected = [a for a in receipt['commands'] if isinstance(a,list) and '-o' in a
                        and Path(a[a.index('-o')+1]).name == label]
            need(len(selected)==1, 'ambiguous command: '+label)
            original = selected[0]
            old_work = str(Path(original[original.index('-o')+1]).parent)
            argv = [a.replace(old_work,str(work))
                    .replace('/Users/cam/DEV/Aether-userland/build/native-c-5olokhku/stage',str(sdk))
                    .replace('/Users/cam/DEV/Aether-userland/build/native-c-5olokhku/empty-root',str(work/'empty-root'))
                    for a in original]
            selected_env = dict(env)
            if argv[0]=='rustc':
                argv = [host['rustc']['path']]+[a for a in argv[1:] if a!='+1.98.0']
                selected_env['DYLD_LIBRARY_PATH']=str(Path(argv[0]).parents[1]/'lib')
            result=run(argv,cwd=kernel,env=selected_env,work=work,label=label,timeout=180,
                       file_limit=512*1024**2)
            report['commands'].append(result.record)
            save()
            need(result.record['complete'] and result.returncode==0,label+' failed')
        for pattern in ('toybox-native-finalize-*','toybox-native-cat-*'):
            for directory in sorted((kernel/'zig-out').glob(pattern)):
                path=directory/'results.json'
                if not path.exists():
                    continue
                results=json.loads(path.read_text())
                need(results['status']=='pass','incomplete native receipt')
                for case in results['cases']:
                    payload=directory/case['name']/'native-c.bin'
                    need(sha(payload)==case['envelope_sha256'],'payload drift')
                    data=payload.read_bytes()
                    magic,a,b,c,d,z1,z2=struct.unpack_from('<8sIIIIII',data)
                    need(magic==b'AENMX001' and not z1 and not z2 and len(data)==80+a+b+c+d,'envelope structure')
                    backend=data[80+a:80+a+b]
                    built=work/('cat-empty-backend.elf' if case['owner'].endswith('-empty') else 'cat-backend.elf')
                    need(backend==built.read_bytes(),'backend mismatch: '+case['name'])
                    report['comparisons'].append(dict(receipt=str(path),receipt_sha256=sha(path),
                        case=case['name'],backend_sha256=sha(built),bytes=b,status='identical'))
        need(len(report['comparisons'])==25,'expected 18 finalizer and7 cat payloads')
        for name, digest in intake['pins'].items():
            need(sha(snapshot/name)==digest,'source changed during build')
        report['status']='pass'
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        report['error']=str(error)
    save()
    print(report['status'],flush=True)
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':
    raise SystemExit(main())
