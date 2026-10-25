#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Opt-in package transport/reboot of an externally pinned userland witness."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--producer', type=Path, required=True)
p.add_argument('--results-sha256', required=True)
p.add_argument('--sources-sha256', required=True)
p.add_argument('--root', type=Path, required=True)
a = p.parse_args()
producer = a.producer.resolve()
root = a.root.absolute()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)

require(sha(producer/'results.json') == a.results_sha256, 'producer result pin')
require(sha(producer/'sources.json') == a.sources_sha256, 'producer source pin')
results = json.loads((producer/'results.json').read_text())
require(len(results) == 9 and all(r['result'] == 'pass' for r in results), 'nine accepted memory outcomes required')
positive = [r for r in results if r['case'] == 'pass']
require(len(positive) == 1 and positive[0]['smoke_exit'] == 0, 'positive witness missing')
positive = positive[0]
kernel = producer/'Aether'
iso = kernel/'zig-out/pass/aether.iso'
require(sha(iso) == positive['image_sha256'], 'tested image changed')
sources = json.loads((producer/'sources.json').read_text())
# Execute only the pinned producer image/smoke tools; their dependency checker
# separately verifies boot dependencies and installed xorriso/QEMU identities.
for name in ('scripts/image.py', 'scripts/io_smoke.py', 'scripts/deps.py',
             'scripts/emulator.py', 'boot/dependencies.json', 'boot/limine.conf', 'LICENSE'):
    require(sha(kernel/name) == sources[name], 'producer tool/input changed: '+name)
root.mkdir(mode=0o700, parents=False, exist_ok=False)
commands = []
def run(argv, label, cwd=REPO):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=120)
    (root/(label+'.log')).write_bytes(result.stdout)
    commands.append(dict(argv=[str(x) for x in argv], cwd=str(cwd), exit=result.returncode))
    (root/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    require(result.returncode == 0, 'failed '+label+'; inspect retained log')
    return result.stdout

run(['make', '-s', '-f', 'mk/pkg.mk', 'ROOT='+str(root), 'init-root'], 'init')
# Extraction from the pinned accepted image binds all six inputs, not merely
# an envelope from an unverified build directory.
run(['xorriso', '-osirrox', 'on', '-indev', iso, '-extract', '/boot', root/'accepted-boot'], 'extract')
boot = root/'accepted-boot'
names = ('aether', 'protection.bin', 'display.bin', 'lifecycle.bin', 'smp-supervisor.bin')
require(sha(boot/'native-c.bin') == positive['envelope_sha256'], 'accepted envelope mismatch')
run(['sh', 'mk/aether-boot-v2.sh', 'stage', root,
     *[boot/n for n in names], *[sha(boot/n) for n in names], a.sources_sha256], 'base-stage')
base_pin = sha(root/'aether-boot-v2/receipt.kv')
run([sys.executable, 'mk/aether-supervised.py', 'stage-memory', root, base_pin,
     boot/'native-c.bin', positive['envelope_sha256']], 'memory-stage')
bundle = root/'aether-memory-v1'
receipt_pin = sha(bundle/'receipt.json')
run([sys.executable, 'mk/aether-supervised.py', 'verify', bundle, receipt_pin], 'memory-verify')
for name in (*names, 'native-c.bin'):
    require(sha(bundle/name) == sha(boot/name), 'staged input mismatch: '+name)
image = root/'boot-check/aether.iso'
run([sys.executable, kernel/'scripts/image.py', bundle/'aether', image,
     *[bundle/n for n in names[1:]], bundle/'native-c.bin'], 'image', kernel)
run([sys.executable, kernel/'scripts/io_smoke.py', image], 'smoke', kernel)
serial = image.parent/'native-serial.log'
lines = serial.read_text().splitlines()
for generation in (1, 2):
    require(f'NATIVE MEMORY admitted slot=0 generation={generation} used=24 remaining=104' in lines, 'memory admission missing')
    require(f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0' in lines, 'generation success missing')
require('NATIVE supervisor result=100 reclaimed=2' in lines and 'AETHER NATIVE IO PASS' in lines, 'cleanup/acceptance missing')
require(not any(line.startswith('AETHER PANIC:') for line in lines), 'unexpected panic')
(root/'result.json').write_text(json.dumps(dict(
    result='pass', scope='Pinned userland memory witness transported and rebooted; not native pkg-mgr',
    producer=str(producer), producer_results_sha256=a.results_sha256,
    producer_sources_sha256=a.sources_sha256, receipt_sha256=receipt_pin,
    image_sha256=sha(image), serial_sha256=sha(serial),
    harness_sha256=sha(Path(__file__)), transport_sha256=sha(REPO/'mk/aether-supervised.py'),
), indent=2)+'\n')
print('PASS: pinned native-memory transport, two generations and terminal cleanup; retained '+str(root))
