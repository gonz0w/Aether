#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check AF09 preparation guards and independent reader offline; no guest."""
from pathlib import Path
import json
import runpy
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / 'userland/experiments/filesystem-service'
home = runpy.run_path(str(S / 'check-home-wire.py'))
reader = runpy.run_path(str(S / 'home_recovery_checks.py'))
TESTS = ('test_fs_home_prep.py', 'test_home_runtime.py', 'test_home_reader.py', 'test_fs_home_inputs.py')
SOURCES = (Path(__file__), ROOT / 'scripts/fs_home_launch.py', ROOT / 'scripts/home_runtime.py',
           ROOT / 'scripts/home_reader.py', ROOT / 'scripts/fs_home_inputs.py',
           *[ROOT / 'tests' / name for name in TESTS],
           S / 'home_recovery_checks.py', S / 'home-recovery-tests.c',
           *sorted((S / 'home-recovery-host').rglob('*.h')),
           ROOT / 'user/storage/openzfs-volume/home-recovery-probe.c',
           ROOT / 'user/storage/openzfs-volume/home-recovery-probe.h')


def check(record, work, proc, tools):
    deadline = time.monotonic() + 300
    pins = json.loads(home['PINS'].read_text())
    for name, tool in pins['tools'].items():
        home['verify'](tool['path'], tool['sha256'])
        tools[name] = tool
    env = proc.clean_env(work)
    for filename in TESTS:
        remaining = deadline - time.monotonic()
        home['require'](remaining > 0, 'preparation suite deadline')
        child_env = dict(env)
        nested = work / 'late-reader-children.json'
        if filename == 'test_home_reader.py':
            child_env['AETHER_HOME_READER_CHILDREN'] = str(nested)
        child = proc.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
            '-p', filename, '-v'], cwd=ROOT, env=child_env, work=work,
            label=Path(filename).stem, timeout=min(180, remaining))
        record['rows'].append(dict(label=filename, expected_exit=0, process=child.record,
            stdout=child.stdout.decode(errors='replace')[-7000:],
            stderr=child.stderr.decode(errors='replace')[-7000:]))
        if nested.is_file():
            record['late_reader_children'] = json.loads(nested.read_text())
        home['require'](child.returncode == 0 and child.record['complete']
            and child.record['cleanup'] == 'complete', filename)
    reader['check'](record, work, proc, tools, deadline)


if __name__ == '__main__':
    sys.exit(home['main'](check_function=check, program='aether-home-preparation-check',
        evidence=ROOT / 'userland/docs/evidence/filesystem-home-prep-2026-10-24/preparation',
        description=__doc__, example='PYTHONOPTIMIZE=1 python3 -B scripts/check_fs_home_prep.py',
        scope='Association, archive and late-reader guards plus original typed read-only oracle; no full engine/image or guest',
        extra_sources=SOURCES, limitations='Typed substitutes and controlled records do not qualify actual ZFS recovery, native resource peaks or a guest. Target composition and exact images are separate.'))
