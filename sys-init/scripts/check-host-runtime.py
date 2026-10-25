#!/usr/bin/env python3
"""Bounded watchdog for real trusted-child fixtures; never runs host services."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bounded_capture import OutputLimitError, run_capture


def validate_suite_result(raw):
    """Require machine evidence; unittest exit zero alone also permits zero tests."""
    result = json.loads(raw)
    if not isinstance(result, dict) or set(result) != {'discovered', 'tests', 'successful', 'skipped'}:
        raise ValueError('invalid suite evidence')
    if any(type(result[k]) is not int for k in ('discovered', 'tests', 'skipped')):
        raise ValueError('invalid suite counts')
    if result['tests'] <= 0 or result['tests'] != result['discovered']:
        raise ValueError('empty or incomplete host suite')
    if result['successful'] is not True or result['skipped'] != 0:
        raise ValueError('host suite failed or skipped required cases')
    return result['tests']


def suite_worker():
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_host*.py', top_level_dir=str(ROOT / 'tests'))
    discovered = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    evidence = dict(discovered=discovered, tests=result.testsRun,
                    successful=result.wasSuccessful(), skipped=len(result.skipped))
    raw = json.dumps(evidence)
    validate_suite_result(raw)
    print(raw)


def main():
    started = time.monotonic()
    try:
        worker = run_capture([sys.executable, str(Path(__file__).resolve()), '--suite-worker'],
                             cwd=ROOT, timeout=30)
    except (subprocess.TimeoutExpired, OutputLimitError) as error:
        sys.stderr.write((error.stderr or b'').decode(errors='replace'))
        message = ('Host runtime fixture watchdog expired' if isinstance(error, subprocess.TimeoutExpired)
                   else 'Host runtime fixture output limit exceeded')
        print(message, file=sys.stderr)
        return 1
    stdout, stderr = worker.stdout, worker.stderr
    sys.stderr.write(stderr)
    if worker.returncode:
        return worker.returncode
    try:
        count = validate_suite_result(stdout)
    except (ValueError, TypeError) as error:
        print('Host runtime evidence rejected: ' + str(error), file=sys.stderr)
        return 1
    files = ['prototypes/host_runtime/runtime.py', 'prototypes/host_runtime/descriptors.py',
             'prototypes/runtime_model/model.py', 'scripts/check-host-runtime.py',
             'scripts/bounded_capture.py']
    files += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'tests').glob('test_host*.py'))]
    print(json.dumps({'profile': 'trusted-host-children-v1', 'result': 'pass', 'tests': count,
                      'platform': platform.platform(), 'python': platform.python_version(),
                      'seconds': time.monotonic()-started,
                      'sources': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}},
                     sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    if sys.argv[1:] == ['--suite-worker']:
        sys.path.insert(0, str(ROOT))
        suite_worker()
    else:
        raise SystemExit(main())
