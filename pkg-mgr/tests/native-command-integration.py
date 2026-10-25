#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Reconstruct and boot the pinned 53-case command handoff in private roots."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parent.parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / 'tests' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

P = load('command_preflight', 'native-command-preflight.py')
WATCH = load('command_watchdog', 'check-watchdog.py')
MARKER = 'AETHER NATIVE CONNECTIONS PASS'
NAMES = ('aether', 'protection.bin', 'display.bin', 'lifecycle.bin', 'smp-supervisor.bin')
TOOLS = ('image.py', 'native_smoke.py', 'deps.py', 'emulator.py')
SMOKE = '''import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from native_smoke import run
run(Path(sys.argv[2]),marker=b'AETHER NATIVE CONNECTIONS PASS',
expected_panic=b'native C profile rejected' if sys.argv[3]=='negative' else None,
panic_context=(sys.argv[4].encode(),) if sys.argv[3]=='negative' else ())
'''


def outcome(text, expected, name):
    lines = text.splitlines()
    terminals = [s for s in lines if s.startswith('NATIVE terminal slot=')]
    if name.startswith('uncertain-admission-'):
        # Successful admission does not require the child to terminate before abort.
        optional = 'NATIVE terminal slot=2 generation=1 kind=1 detail=0'
        P.require(terminals.count(optional) <= 1, 'duplicate optional child terminal')
        terminals = [s for s in terminals if s != optional]
        wanted = [s for s in expected['terminals'] if s != optional]
    else:
        wanted = expected['terminals']
    P.require(terminals == wanted, 'terminal mismatch: ' + name)
    P.require([s for s in lines if s.startswith('NATIVE supervisor result=')] == expected['supervisor'], 'supervisor mismatch: ' + name)
    panics = [s for s in lines if s.startswith('AETHER PANIC:')]
    P.require(panics == (['AETHER PANIC: native C profile rejected'] if expected['negative'] else []), 'panic mismatch: ' + name)
    P.require(lines.count(MARKER) == (0 if expected['negative'] else 1), 'marker mismatch: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('evidence', 'build', 'clients', 'aether', 'root'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = args.root.absolute()
    oracle_path = REPO / 'tests/native-command-oracles.json'
    oracle = P.read_json(oracle_path)
    receipt = P.read_json(args.evidence)
    preflight = P.preflight(args.evidence.absolute(), oracle['receipt_sha256'], args.build.absolute(), args.clients.absolute())
    P.require(set(oracle['cases']) == P.CASES, 'oracle case set mismatch')
    closure = {f'scripts/{n}': receipt['kernel_sources'][f'scripts/{n}'] for n in TOOLS}
    for name in ('LICENSE', 'boot/limine.conf', 'boot/dependencies.json'):
        closure[name] = receipt['kernel_sources'][name]
    for name, pin in receipt['boot_dependency_manifest']['files'].items():
        closure['.deps/' + name] = pin
    for name, pin in closure.items():
        P.checked(args.aether.absolute(), name, pin)
    for name in ('xorriso', 'qemu-system-x86_64'):
        selected = Path(shutil.which(name) or '').resolve()
        P.require(P.digest(selected) == receipt['host_tools'][name]['sha256'], 'host tool mismatch: ' + name)
    inputs = {str(p.relative_to(REPO)): P.digest(p) for p in (REPO/'mk').iterdir() if p.is_file()}
    for name in ('native-command-integration.py', 'native-command-preflight.py', 'native-command-oracles.json', 'check-watchdog.py'):
        inputs['tests/' + name] = P.digest(REPO/'tests'/name)
    root.mkdir(mode=0o700, exist_ok=False)
    (root/'preflight.json').write_text(json.dumps(preflight, indent=2)+'\n')
    tools = root/'tools'
    for name, pin in closure.items():
        destination = tools/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.aether/name, destination)
        P.require(P.digest(destination) == pin, 'copy drift')
    (tools/'.deps/manifest.json').write_text(json.dumps(receipt['boot_dependency_manifest']))
    started = time.monotonic()
    commands = []
    results = []
    def run(argv, label, cwd=REPO):
        remaining = 600 - (time.monotonic() - started)
        P.require(remaining > 0, 'whole integration deadline')
        logroot = root/('log-' + label)
        logroot.mkdir()
        previous = Path.cwd()
        try:
            os.chdir(cwd)
            status = WATCH.run([str(s) for s in argv], logroot, min(120, remaining))
        finally:
            os.chdir(previous)
        commands.append({'argv': [str(s) for s in argv], 'cwd': str(cwd), 'exit': status, 'log': str(logroot/'suite.log')})
        (root/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        P.require(status == 0, 'command failed: ' + label)
    for case in receipt['cases']:
        name = case['case']; expected = oracle['cases'][name]
        P.require(expected['negative'] is case['negative'], 'polarity mismatch')
        work = root/name; work.mkdir(mode=0o700)
        run(['make','-s','-f','mk/pkg.mk','ROOT='+str(work),'init-root'], name+'-init')
        iso = args.build/name/'aether.iso'
        run(['xorriso','-osirrox','on','-indev',iso,'-extract','/boot',work/'accepted-boot'], name+'-extract')
        run(['xorriso','-osirrox','on','-indev',iso,'-extract','/limine.conf',work/'accepted-config'], name+'-config')
        boot = work/'accepted-boot'
        P.require((work/'accepted-config').read_bytes() == (tools/'boot/limine.conf').read_bytes()+b'    module_path: boot():/boot/native-c.bin\n', 'config mismatch')
        P.require((boot/'LICENSE-Aether.txt').read_bytes() == (tools/'LICENSE').read_bytes(), 'license mismatch')
        P.require(P.digest(boot/'native-c.bin') == case['envelope_sha256'], 'envelope mismatch')
        run(['sh','mk/aether-boot-v2.sh','stage',work,*[boot/n for n in NAMES],*[P.digest(boot/n) for n in NAMES],oracle['receipt_sha256']], name+'-base')
        run([sys.executable,'mk/aether-supervised.py','stage-connections',work,P.digest(work/'aether-boot-v2/receipt.kv'),boot/'native-c.bin',case['envelope_sha256']], name+'-stage')
        bundle = work/'aether-connections-v1'; pin = P.digest(bundle/'receipt.json')
        run([sys.executable,'mk/aether-supervised.py','verify',bundle,pin], name+'-verify')
        P.require(all(P.digest(bundle/n)==P.digest(boot/n) for n in (*NAMES,'native-c.bin')), 'staged bytes changed')
        image = work/'boot-check/aether.iso'
        run([sys.executable,tools/'scripts/image.py',bundle/'aether',image,*[bundle/n for n in NAMES[1:]],bundle/'native-c.bin'], name+'-image', tools)
        run([sys.executable,'-c',SMOKE,tools/'scripts',image,'negative' if expected['negative'] else 'positive',expected['supervisor'][0]], name+'-boot', tools)
        serial = image.parent/'native-serial.log'
        outcome(serial.read_text(), expected, name)
        results.append({'case': name, 'result': 'expected-rejection' if expected['negative'] else 'pass', 'receipt_sha256': pin, 'image_sha256': P.digest(image), 'serial_sha256': P.digest(serial)})
        (root/'cases.json').write_text(json.dumps(results, indent=2)+'\n')
        print('PASS: '+name, flush=True)
    for name, pin in inputs.items():
        P.require(P.digest(REPO/name)==pin, 'package input drift')
    for name, pin in closure.items():
        P.require(P.digest(tools/name)==pin, 'tool input drift')
    P.preflight(args.evidence.absolute(), oracle['receipt_sha256'], args.build.absolute(), args.clients.absolute())
    (root/'result.json').write_text(json.dumps({'result':'pass','scope':'bounded 53-case package transport; no native package installation','inputs':inputs,'tool_closure':closure,'cases':results,'elapsed':time.monotonic()-started},indent=2)+'\n')
    print('PASS: all 53 package-staged command cases; retained '+str(root))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print('command-integration-error: '+str(error), file=sys.stderr)
        sys.exit(1)
