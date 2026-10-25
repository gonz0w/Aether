#!/usr/bin/env python3
"""Optional target tests: consume sys-init clients in an isolated Aether snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bounded_tools import run_completed, run_recorded

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(aether, work):
    # Never use companion output/cache directories, even on repeated runs.
    work.mkdir(parents=True, exist_ok=False)
    source = work / 'aether'
    shutil.copytree(aether, source, ignore=shutil.ignore_patterns(
        '.git', '.jj', '.deps', '.zig-cache', 'zig-out', '.tmp', '__pycache__', '.DS_Store'))
    shutil.copytree(aether / '.deps', source / '.deps')
    source_hashes = {str(p.relative_to(source)): digest(p)
                     for p in sorted(source.rglob('*')) if p.is_file()}
    (work / 'source-sha256.json').write_text(json.dumps(source_hashes, indent=2) + '\n')
    results = []
    try:
        for variant in ['pass', 'wrong_detail', 'fault_entry']:
            build_output = run_recorded(['python3', str(ROOT / 'scripts/build-lifecycle.py'),
                            str(work / 'clients'), '--variant', variant],
                            work / (variant + '-client.log'), __file__, timeout=180)
            sys.stdout.write(build_output.decode())
            sys.stdout.flush()
            client = work / 'clients' / (variant + '.bin')
            output = work / variant
            command = ['zig', 'build', 'smoke', '-Dsmp=false',
                '-Dlifecycle-image=' + str(client), '-p', str(output),
                '--cache-dir', str(work / 'zig-cache'),
                '--global-cache-dir', str(work / 'global-cache')]
            result = run_completed(command, work / (variant + '-build.log'), __file__,
                                   cwd=source, timeout=120)
            serial = output / 'serial.log'
            log = serial.read_text() if serial.exists() else ''
            passed = 'AETHER LIFECYCLE V1 PASS' in log.splitlines()
            if variant == 'pass':
                valid = result.returncode == 0 and passed
            elif variant == 'wrong_detail':
                valid = result.returncode != 0 and not passed and 'LIFETIME exit=311 ' in log and 'AETHER PANIC:' in log
            else:
                valid = result.returncode != 0 and not passed and 'AETHER PANIC:' in log and 'supervisor' in log.lower()
            results.append({'variant': variant, 'command': command, 'cwd': str(source),
                'returncode': result.returncode, 'expected_outcome_observed': valid,
                'client_sha256': digest(client), 'client_bytes': client.stat().st_size,
                'artifacts': {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob('*'))
                              if p.is_file()}})
            print(variant, 'PASS' if valid else 'FAIL', flush=True)
            if not valid:
                raise RuntimeError(f'{variant}: see {work}; output:\n{result.stdout.decode(errors="replace")[-2500:]}\n{log[-1500:]}')
    finally:
        (work / 'results.json').write_text(json.dumps(results, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aether', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True, help='new, non-existing output directory')
    args = parser.parse_args()
    run(args.aether.resolve(), args.work.resolve())
