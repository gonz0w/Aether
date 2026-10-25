#!/usr/bin/env python3
"""Measure bounded trusted-child workloads; no native or product speed claims."""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import resource
import statistics
import sys
import tempfile
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('development_checks', ROOT / 'scripts/check-all.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def summarize(values):
    if not values or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('nonempty finite nonnegative samples required')
    ordered = sorted(values)
    return dict(count=len(values), median=statistics.median(ordered),
                p95=ordered[math.ceil(.95 * len(ordered)) - 1], maximum=ordered[-1])


def cpu(who):
    usage = resource.getrusage(who)
    return usage.ru_utime + usage.ru_stime


def worker(count, directory, stall=False):
    sys.path.insert(0, str(ROOT))
    from prototypes.host_runtime.runtime import Command, HostRuntime
    from prototypes.runtime_model.model import Service
    executable = str(Path(sys.executable).resolve())
    pin = hashlib.sha256(Path(executable).read_bytes()).hexdigest()
    names = ['service' + str(i) for i in range(count)]
    code = ("import os,time; " + ('' if stall else
            "os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n'); ") + 'time.sleep(30)')
    services = [Service(n, milestone='notified-ready', startup=10000, stop=1000, cleanup=1000) for n in names]
    commands = {n: Command((executable, '-c', code), pin) for n in names}
    self_before, children_before = cpu(resource.RUSAGE_SELF), cpu(resource.RUSAGE_CHILDREN)
    tracemalloc.start()
    began = time.perf_counter_ns()
    rt = HostRuntime(services, commands, cwd=directory)
    constructed = time.perf_counter_ns()
    try:
        start = time.perf_counter_ns()
        rt.start(names, budget=15000)
        (directory / 'spawned.json').write_text(json.dumps(dict(children=len(rt.children))))
        rt.until(lambda: rt.model.active is None, timeout=12)
        ready = time.perf_counter_ns()
        if rt.model.operations[-1].status != 'success' or not all(rt.model.state[n].ready for n in names):
            raise RuntimeError('missing readiness witness')
        live = sum(rt._poll(c) is None for c in rt.children.values())
        if live != count:
            raise RuntimeError('child inventory mismatch at readiness')
        stop = time.perf_counter_ns()
        rt.stop(names, budget=5000)
        rt.until(lambda: rt.model.active is None and not rt.children and not rt.pending, timeout=6)
        drained = time.perf_counter_ns()
        if (rt.model.operations[-1].status != 'success' or rt.ready
                or any(s.owned or s.cleanup != 'complete' for s in rt.model.state.values())):
            raise RuntimeError('incomplete stop/reclamation')
    finally:
        rt.close()
    ended = time.perf_counter_ns()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(json.dumps(dict(result='pass', children=count, live_children_at_ready=live,
                         processes_in_workload=live+1, coordinator_processes_excluded=1,
                         construct_ms=(constructed-began)/1e6, start_ready_ms=(ready-start)/1e6,
                         stop_reap_ms=(drained-stop)/1e6, total_ms=(ended-began)/1e6,
                         manager_cpu_ms=(cpu(resource.RUSAGE_SELF)-self_before)*1000,
                         children_cpu_ms=(cpu(resource.RUSAGE_CHILDREN)-children_before)*1000,
                         manager_traced_peak_bytes=peak, children_remaining=len(rt.children))))


def main():
    parser = checks.Parser(description=__doc__, epilog='Example: python3 scripts/measure-host-runtime.py. '
                           'Requires POSIX Python host tooling; see docs/HOST-MEASUREMENTS.md.')
    parser.add_argument('--version', action='version', version='sys-init host measurements 1')
    parser.add_argument('--output-root', type=Path, default=ROOT / 'out/host-measurements',
                        help='parent for a new private run directory')
    parser.add_argument('--worker', type=int, choices=(1, 8), help=argparse.SUPPRESS)
    parser.add_argument('--directory', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--stall', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.directory is None: parser.error('worker requires a private directory')
        worker(args.worker, args.directory, args.stall)
        return 0
    if args.directory is not None or args.stall: parser.error('internal worker option without worker')
    args.output_root.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix='run-', dir=args.output_root.resolve()))
    paths = ['scripts/measure-host-runtime.py', 'scripts/check-all.py',
             'prototypes/host_runtime/runtime.py', 'prototypes/runtime_model/model.py']
    paths += [str(p.relative_to(ROOT)) for p in (ROOT / 'docs').glob('*.lock')]
    def fingerprints():
        return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    report = dict(schema='sys-init-host-measurements-v1', result='running',
                  command=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  python=sys.version, executable=sys.executable,
                  executable_sha256=hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest(),
                  platform=platform.platform(), machine=platform.machine(), processor=platform.processor(),
                  logical_cpus=os.cpu_count(), load_before=os.getloadavg(),
                  clock='perf_counter_ns', instrumentation='tracemalloc enabled for every worker',
                  cache_state='2 warmups per workload; fresh worker interpreter; host caches uncontrolled',
                  setup='worker imports, fixture definitions and initial interpreter pin excluded; runtime construction included separately',
                  memory='peak manager Python allocations since before construction; excludes imports, interpreter RSS and children',
                  cpu='getrusage user+system deltas; manager and reaped children separately',
                  native='not-run', source_sha256=fingerprints(), checks=[], samples=[], summary={})
    destination = directory / 'results.json'
    def save(): destination.write_text(json.dumps(report, indent=2) + '\n')
    def interrupted(record):
        if record['result'] != 'interrupted': return False
        report['result'] = 'interrupted'
        save()
        print(json.dumps(dict(schema=report['schema'], result='interrupted', report=str(destination))))
        return True
    save()
    for name in ('standards', 'experience', 'distribution'):
        record = checks.run_check(name, [sys.executable, str(ROOT / ('docs/check-'+name+'.py'))], directory)
        report['checks'].append(record)
        save()
        if interrupted(record): return 130
        if record['result'] != 'pass': break
    if all(r['result'] == 'pass' for r in report['checks']):
        for count in (1, 8):
            for index in range(12):
                name = f'children-{count}-{index:02d}'
                sample_dir = directory / name
                sample_dir.mkdir()
                command = [sys.executable, str(Path(__file__).resolve()), '--worker', str(count), '--directory', str(sample_dir)]
                record = checks.run_check(name, command, directory, timeout=20)
                sample = dict(role='warmup' if index < 2 else 'measured', children=count, run=record)
                if record['result'] == 'pass':
                    try:
                        value = json.loads((directory / record['stdout']).read_text())
                        if value['result'] != 'pass' or value['children_remaining'] != 0 or value['live_children_at_ready'] != count:
                            raise ValueError('invalid sample witness')
                        sample['values'] = value
                    except (ValueError, KeyError, TypeError) as error:
                        record.update(result='invalid-evidence', error=str(error))
                report['samples'].append(sample)
                save()
                if interrupted(record): return 130
            print(f'[INFO] {count} children: repetitions recorded', file=sys.stderr, flush=True)
        # Same worker, deliberately silent children; outer watchdog must censor it.
        negative_dir = directory / 'timeout-control'
        negative_dir.mkdir()
        report['negative_control'] = checks.run_check('timeout-control',
            [sys.executable, str(Path(__file__).resolve()), '--worker', '1', '--directory', str(negative_dir), '--stall'],
            directory, timeout=1)
        if interrupted(report['negative_control']): return 130
        report['negative_caught'] = (report['negative_control']['result'] == 'timeout'
                                    and (negative_dir / 'spawned.json').exists())
        metrics = ['construct_ms', 'start_ready_ms', 'stop_reap_ms', 'total_ms', 'manager_cpu_ms',
                   'children_cpu_ms', 'manager_traced_peak_bytes', 'processes_in_workload']
        for count in (1, 8):
            samples = [s for s in report['samples'] if s['role'] == 'measured' and s['children'] == count]
            successful = [s['values'] for s in samples if s['run']['result'] == 'pass']
            report['summary'][str(count)] = dict(failures=len(samples)-len(successful),
                successful=len(successful), metrics={m: summarize([v[m] for v in successful]) for m in metrics} if successful else {})
    report['sources_unchanged'] = report['source_sha256'] == fingerprints()
    report['result'] = ('pass' if len(report['samples']) == 24 and report.get('negative_caught')
                        and report['sources_unchanged'] and all(s['run']['result'] == 'pass' for s in report['samples']) else 'fail')
    save()
    print(json.dumps(dict(schema=report['schema'], result=report['result'], report=str(destination))))
    return 0 if report['result'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
