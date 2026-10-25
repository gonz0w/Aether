#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run native I/O stop, semantic controls and original-client compatibility."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, self.prog+': '+message+'\n')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_sdk(sdk, pin, retained=False, readiness=False, authority=False, peer=False):
    if sha(sdk / 'evidence.json') != pin:
        raise ValueError('SDK receipt pin mismatch')
    receipt = json.loads((sdk / 'evidence.json').read_text())
    raw = (sdk / 'native-c.bin').read_bytes()
    if receipt['probe_variant'] != ('io-peer' if peer else 'io-authority' if authority else 'io-readiness' if readiness else 'io-retained' if retained else 'io') or not 40 < len(raw) <= 1024*1024+40 or raw[:8] != b'AENATC01':
        raise ValueError('bounded I/O envelope required')
    artifacts = {a['name']: a['sha256'] for a in receipt['artifacts']}
    if (hashlib.sha256(raw).hexdigest() != receipt['envelope_sha256']
            or hashlib.sha256(raw[40:]).hexdigest() != artifacts['startup']):
        raise ValueError('SDK envelope/ELF mismatch')
    return raw



def capture_client(client):
    """Freeze the builder and every local import used by its CLI."""
    sources = ['scripts/build-native-supervisor.py', 'scripts/bounded_tools.py', 'prototypes/native-supervisor/main.rs',
               'prototypes/native-supervisor/io.rs', 'prototypes/native-supervisor/io_stop.rs',
               'prototypes/native-supervisor/io_peer.rs', 'prototypes/native-supervisor/io_authority.rs', 'prototypes/native-supervisor/io_readiness.rs', 'prototypes/native-supervisor/io_retained.rs', 'prototypes/native-supervisor/linker.ld', 'tests/native-io-stop.py']
    for name in sources:
        target = client / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)

def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='sys-init native I/O stop fixture 1')
    parser.add_argument('--aether', type=Path, required=True, help='trusted kernel source tree with pinned boot dependencies')
    parser.add_argument('--sdk', type=Path, required=True, help='I/O SDK from a verified producer build')
    parser.add_argument('--receipt-pin', required=True, help='externally retained SHA-256 of SDK evidence.json')
    parser.add_argument('--work', type=Path, required=True, help='new private work directory; must not exist')
    profile = parser.add_mutually_exclusive_group()
    profile.add_argument('--peer', action='store_true', help='run known-live-peer readiness cases')
    profile.add_argument('--authority', action='store_true', help='run worker-local readiness authority cases')
    profile.add_argument('--readiness', action='store_true', help='run readiness/terminal ordering cases')
    profile.add_argument('--retained', action='store_true', help='use sys-init retained-output worker and stop/fault controls')
    args = parser.parse_args()
    # Match the new developer command usage contract without recoding old runners.
    sdk, kernel_source = args.sdk.resolve(), args.aether.resolve()
    raw = validate_sdk(sdk, args.receipt_pin, args.retained, args.readiness, args.authority, args.peer)
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    os.chmod(work, 0o700)
    (work / 'native-c.bin').write_bytes(raw)
    shutil.copyfile(sdk / 'evidence.json', work / 'sdk-evidence.json')
    if sha(work / 'sdk-evidence.json') != args.receipt_pin:
        raise ValueError('SDK changed during capture')
    ignore = lambda p, names: set(names) & {'.git', '.jj', '.zig-cache', 'zig-out', '__pycache__', '.DS_Store'}
    kernel = work / 'Aether'
    shutil.copytree(kernel_source, kernel, ignore=ignore)
    client = work / 'sys-init'
    capture_client(client)
    pins = {str(p.relative_to(work)): sha(p) for tree in (kernel, client)
            for p in tree.rglob('*') if p.is_file()}
    (work / 'sources.json').write_text(json.dumps(pins, sort_keys=True, indent=2)+'\n')
    report = dict(schema='sys-init-native-peer-v1' if args.peer else 'sys-init-native-authority-v1' if args.authority else 'sys-init-native-readiness-v1' if args.readiness else 'sys-init-native-io-retained-v1' if args.retained else 'sys-init-native-io-stop-v1', result='running', cases=[], commands=[],
                  sdk_receipt_sha256=args.receipt_pin, native_sha256=sha(work/'native-c.bin'),
                  native_memory=False, smp=False)
    def save(): (work / 'results.json').write_text(json.dumps(report, indent=2)+'\n')
    def run(command, name):
        with (work / (name+'.log')).open('wb') as log:
            child = subprocess.Popen(command, cwd=kernel, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = child.wait(timeout=120)
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
                try: os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                child.wait()
                outcome = 'interrupted' if isinstance(error, KeyboardInterrupt) else 'timeout'
                report['commands'].append(dict(argv=command, outcome=outcome))
                report['result'] = outcome
                save()
                if outcome == 'interrupted': raise SystemExit(130)
                raise
        report['commands'].append(dict(argv=command, exit=code))
        save()
        return code
    save()
    try:
        cases = [('stop', 'io-stop', None, True),
                 ('wrong-detail', 'io-stop-wrong-detail', None, False),
                 ('skip-zero', 'io-stop', 'native-skip-zero', False),
                 ('original-io', 'io', None, True)]
        if args.retained:
            cases = [('retained-stop','io-retained-stop',None,True),
                     ('retained-fault','io-retained-fault',None,True),
                     ('wrong-kind','io-retained-wrong-kind',None,False),
                     ('skip-zero','io-retained-stop','native-skip-zero',False)]
        if args.readiness:
            cases = [(name, 'io-'+name, None, True) for name in
                     ('unready-exit','unready-fault','unready-stop','ready-exit','ready-fault')]
            cases += [('invent-ready','io-invent-ready',None,False),
                      ('skip-zero','io-ready-exit','native-skip-zero',False)]
        if args.authority:
            cases = [('authority','io-authority',None,True),
                     ('allow-notify','io-authority-allow',None,False),
                     ('skip-zero','io-authority','native-skip-zero',False)]
        if args.peer:
            cases = [('peer','io-peer',None,True),('peer-reverse','io-peer-reverse',None,True),
                     ('wrong-peer','io-peer-wrong',None,False),('skip-zero','io-peer','native-skip-zero',False)]
        for name, variant, flag, positive in cases:
            output = work / 'clients' / name
            command = [sys.executable, str(client/'scripts/build-native-supervisor.py'),
                       str(work/'native-c.bin'), str(output), '--variant', variant]
            if run(command, name+'-client') != 0: raise RuntimeError('client build failed: '+name)
            command = ['zig','build','-Dsmp=false','-Dnative-memory=false',
                       '-Dnative-c-image='+str(output/'supervised.bin'),'-p','zig-out/'+name,
                       '--cache-dir','.zig-cache','--global-cache-dir','.zig-cache/global']
            if flag: command.append('-D'+flag+'=true')
            if run(command, name+'-build') != 0: raise RuntimeError('kernel build failed: '+name)
            code = run([sys.executable,'scripts/io_smoke.py','zig-out/'+name+'/aether.iso'],name+'-smoke')
            serial = kernel/'zig-out'/name/'native-serial.log'
            shutil.copyfile(serial,work/(name+'-serial.log'))
            lines = serial.read_text().splitlines()
            marker = 'AETHER NATIVE IO PASS' if positive else 'AETHER PANIC: native C profile rejected'
            if code != (0 if positive else 1) or marker not in lines or (not positive and 'AETHER NATIVE IO PASS' in lines):
                raise RuntimeError('wrong semantic outcome: '+name)
            if name == 'wrong-detail' and 'NATIVE supervisor result=244 reclaimed=0' not in lines:
                raise RuntimeError('wrong-detail control failed outside its intended assertion')
            if name == 'wrong-peer' and 'NATIVE supervisor result=607 reclaimed=0' not in lines:
                raise RuntimeError('wrong-peer failed outside intended assertion')
            if name == 'allow-notify' and 'NATIVE supervisor result=501 reclaimed=0' not in lines:
                raise RuntimeError('allow-notify failed outside intended assertion')
            if name == 'invent-ready' and 'NATIVE supervisor result=407 reclaimed=0' not in lines:
                raise RuntimeError('invent-ready failed outside intended assertion')
            if name == 'wrong-kind' and 'NATIVE supervisor result=307 reclaimed=0' not in lines:
                raise RuntimeError('wrong-kind failed outside intended assertion')
            if name in ('retained-fault','wrong-kind','unready-fault','ready-fault') and not any('NATIVE fault vector=6 ' in line for line in lines):
                raise RuntimeError('real invalid-opcode fault missing')
            report['cases'].append(dict(case=name, result='pass', smoke_exit=code, marker=marker,
                 image_sha256=sha(kernel/'zig-out'/name/'aether.iso'),
                 envelope_sha256=sha(output/'supervised.bin'), serial_sha256=sha(serial)))
            save()
            print('[OK] '+name, file=sys.stderr, flush=True)
        if any(sha(work/name) != h for name,h in pins.items()): raise RuntimeError('frozen source changed')
        report.update(result='pass', sources_unchanged=True)
    except Exception as error:
        report.update(result='fail', error=str(error))
        raise
    finally:
        save()
    print(json.dumps(dict(result=report['result'], report=str(work/'results.json'))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
