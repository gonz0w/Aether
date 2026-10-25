#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Record bounded owned-command timings alongside exact byte correctness."""
import hashlib
import json
from pathlib import Path
import platform
import runpy
import statistics
import sys
import time


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    env = process['clean_env'](work)
    env['LD_LIBRARY_PATH'] = '/inputs/lib'
    rows = []
    schedule = [('warmup', 65536, 0)] + [('measured', size, rep) for size in [65536, 1048576] for rep in range(1, 4)]
    for phase, size, rep in schedule:
        pattern = b' 12345\n'
        data = (pattern * ((size + len(pattern) - 1) // len(pattern)))[:size]
        expected = data.translate(None, b'\t\n\v\f\r ')
        start = time.perf_counter_ns()
        result = process['run'](['/inputs/patched', '/inputs/bin/tr', '-d', '[:space:]'],
            cwd=work, env=env, work=work, label=phase + '-' + str(size) + '-' + str(rep),
            timeout=10, input=data, file_limit=2 * 1024**2)
        elapsed = time.perf_counter_ns() - start
        passed = (result.record['complete'] and result.returncode == 0 and result.stdout == expected
                  and result.stderr == b'' and elapsed > 0)
        rows.append(dict(phase=phase, input_bytes=size, repeat=rep, elapsed_ns=elapsed,
            input_sha256=hashlib.sha256(data).hexdigest(), output_bytes=len(result.stdout),
            output_sha256=hashlib.sha256(result.stdout).hexdigest(),
            expected_sha256=hashlib.sha256(expected).hexdigest(), process=result.record,
            stderr_hex=result.stderr.hex(), passed=passed))
    summaries = []
    for size in [65536, 1048576]:
        samples = [r['elapsed_ns'] for r in rows if r['phase'] == 'measured' and r['input_bytes'] == size]
        median = statistics.median(samples)
        summaries.append(dict(input_bytes=size, samples_ns=samples, median_ns=median,
            min_ns=min(samples), max_ns=max(samples), input_mib_per_second=size / 1048576 / (median / 1e9)))
    passed = len(rows) == 7 and all(r['passed'] for r in rows)
    clock = time.get_clock_info('perf_counter')
    print(json.dumps(dict(status='pass' if passed else 'incomplete', python=sys.version,
        kernel=platform.uname()._asdict(), clock=dict(implementation=clock.implementation,
        resolution_seconds=clock.resolution, monotonic=clock.monotonic),
        metric='owned command elapsed; includes QEMU startup, file I/O, waiting and cleanup',
        performance_acceptance='not evaluated; no target threshold', results=rows, summaries=summaries), indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
