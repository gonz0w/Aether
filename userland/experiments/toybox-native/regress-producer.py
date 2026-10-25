#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run the complete captured producer command suite with owned outer cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'experiments/command-runner'))
from process import clean_env,run


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,required=True)
    parser.add_argument('--execution-receipt',type=Path,help='Explicit captured wrapper receipt; defaults to finalizer receipt')
    args=parser.parse_args()
    snapshot=args.snapshot.resolve();kernel=snapshot/'producer'
    work=Path(tempfile.mkdtemp(prefix='cat-producer-regression-',dir=ROOT/'build'))
    report=dict(status='incomplete',work=str(work),commands=[])
    def save():
        (work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(work,flush=True);save()
    try:
        intake=json.loads((snapshot/'intake.json').read_text())
        for name,h in intake['pins'].items():
            if sha(snapshot/name)!=h:raise RuntimeError('snapshot drift: '+name)
        base=kernel/'docs/evidence/toybox-native-link-2026-09-07'
        baseline=json.loads((base/'results.json').read_text())
        sdk=work/'sdk';shutil.copytree(base/'inputs/sdk-stage',sdk/'stage')
        shutil.copyfile(base/'inputs/sdk-receipt.json',sdk/'evidence.json')
        (sdk/'empty-root').mkdir()
        for name,h in baseline['sdk_inputs'].items():
            if sha(sdk/'stage'/name)!=h:raise RuntimeError('SDK drift')
        host=json.loads((ROOT/'experiments/command-runner/host-tools.lock.json').read_text())
        for t in [*host.values(),*baseline['tools'].values()]:
            if sha(Path(t['path']))!=t['sha256']:raise RuntimeError('tool drift')
        env=clean_env(work);env['PATH']=str(snapshot/'tools')+':/usr/bin:/bin'
        wrapper=snapshot/'tools/rustc'
        execution=([args.execution_receipt.resolve()] if args.execution_receipt else
                   list(snapshot.glob('finalize-execution-*/execution.json')))
        if len(execution)!=1:raise RuntimeError('ambiguous wrapper pin')
        if sha(wrapper)!=json.loads(execution[0].read_text())['rust_wrapper_sha256']:
            raise RuntimeError('Rust wrapper drift')
        before=set((kernel/'zig-out').glob('command-runner-suite-*'))
        argv=[sys.executable,'-B','scripts/launch_smoke.py','--command-runner','--libc-build',str(sdk),
              '--tools-lock',str(base/'inputs/tools.lock.json')]
        report.update(intake_sha256=sha(snapshot/'intake.json'),driver_sha256=sha(Path(__file__)),
                      host_tools=host,tools=baseline['tools'],sdk_inputs=baseline['sdk_inputs'],
                      execution_receipt=str(execution[0]),execution_receipt_sha256=sha(execution[0]),
                      environment=env,rust_wrapper_sha256=sha(wrapper))
        save()
        result=run(argv,cwd=kernel,env=env,work=work,label='command-suite',timeout=1800,
                   file_limit=512*1024**2)
        report['commands'].append(result.record);save()
        if not result.record['complete'] or result.returncode:
            raise RuntimeError('command suite failed')
        created=set((kernel/'zig-out').glob('command-runner-suite-*'))-before
        if len(created)!=1:raise RuntimeError('ambiguous producer output')
        path=created.pop()/'results.json';native=json.loads(path.read_text())
        if native['status']!='pass' or len(native['cases'])!=213:
            raise RuntimeError('expected213 passing native cases')
        for name,h in intake['pins'].items():
            if sha(snapshot/name)!=h:raise RuntimeError('source drift during execution')
        report.update(status='pass',native_receipt=str(path),native_receipt_sha256=sha(path),
                      native_cases=len(native['cases']))
    except (OSError,RuntimeError,ValueError,KeyError) as error:
        report['error']=str(error)
    save();print(report['status'],flush=True)
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':
    raise SystemExit(main())
