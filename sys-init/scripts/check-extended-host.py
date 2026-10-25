#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run or replay the bounded EHT-01 trusted-host campaign; no native execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


aggregate = module('extended_aggregate', 'check-all.py')
records = module('extended_records', 'check-native-evidence.py')
IMPLEMENTATION = ('scripts/check-extended-host.py', 'scripts/check-all.py', 'scripts/check-native-evidence.py')
LIMITS = dict(workers=8, worker_seconds=60, campaign_seconds=600,
              worker_output_bytes=4194304, cleanup_grace_seconds=1)


def digest(path):
    return aggregate.snapshot_digest(path, aggregate.SOURCE_FILE_LIMIT)[0]


def implementations():
    return {name: digest(ROOT / name) for name in IMPLEMENTATION}


def corpus_paths():
    return sorted(['prototypes/host_runtime/runtime.py', 'prototypes/host_runtime/descriptors.py',
                   'prototypes/runtime_model/model.py', 'scripts/check-host-runtime.py',
                   'scripts/bounded_capture.py', 'docs/examples/host-descriptor.py'] +
                  [str(p.relative_to(ROOT)) for p in (ROOT / 'tests').glob('test_host*.py')])


def load_plan(path, expected_hash=None):
    raw = records.read_metadata(path, path.parent)
    identity = hashlib.sha256(raw).hexdigest()
    if expected_hash is not None and identity != expected_hash:
        raise ValueError('plan identity changed')
    plan = records.parse_receipt(raw)
    records.catalog_fields(plan, 'schema id status scope test_ids sources seeds ordering limits owner freshness_days scheduling')
    if (plan['schema'] != 'sys-init-extended-host-plan-v1' or plan['id'] != 'EHT-01'
            or plan['status'] != 'planned' or plan['ordering'] != 'sys-init-eht-order-v1'
            or plan['scheduling'] != 'not-configured' or type(plan['freshness_days']) is not int
            or plan['freshness_days'] != 7):
        raise ValueError('unsupported extended plan')
    for name in ('scope', 'owner'):
        records.catalog_text(plan[name])
    if plan['limits'] != LIMITS or any(type(v) is not int for v in plan['limits'].values()):
        raise ValueError('unsupported extended limits')
    for name, count in (('test_ids', 54), ('seeds', 8)):
        values = plan[name]
        if not isinstance(values, list) or len(values) != count:
            raise ValueError('invalid extended collection')
        for value in values:
            records.catalog_text(value)
        if len(set(values)) != count:
            raise ValueError('duplicate extended item')
    for seed in plan['seeds']:
        records.report_digest(seed)
    records.receipt_digests(plan['sources'])
    if sorted(plan['sources']) != corpus_paths():
        raise ValueError('incomplete corpus input map')
    for name, expected in plan['sources'].items():
        if digest(ROOT / name) != expected:
            raise ValueError('corpus source changed: ' + name)
    return plan, identity


def ordered_ids(plan, seed):
    if seed not in plan['seeds']:
        raise ValueError('seed absent from plan')
    def rank(kind, name):
        return hashlib.sha256(('sys-init-eht-order-v1\n' + seed + '\n' + kind + '\n' + name).encode()).hexdigest()
    classes = {name.rsplit('.', 1)[0] for name in plan['test_ids']}
    return [name for cls in sorted(classes, key=lambda c: (rank('class', c), c))
            for name in sorted((n for n in plan['test_ids'] if n.rsplit('.', 1)[0] == cls),
                               key=lambda n: (rank('test', n), n))]


def leaves(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from leaves(item)
        else:
            yield item


class TrackedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed_ids = []

    def startTest(self, test):
        self.executed_ids.append(test.id())
        super().startTest(test)


def worker(path, seed, plan_hash):
    plan, identity = load_plan(path, plan_hash)
    implementation = implementations()
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_host*.py',
                                                top_level_dir=str(ROOT / 'tests'))
    tests = list(leaves(suite))
    by_id = {test.id(): test for test in tests}
    if len(by_id) != len(tests) or sorted(by_id) != sorted(plan['test_ids']):
        raise ValueError('host discovery differs from plan')
    order = ordered_ids(plan, seed)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2, failfast=True,
                                    resultclass=TrackedResult).run(unittest.TestSuite(by_id[name] for name in order))
    load_plan(path, identity)
    if implementations() != implementation:
        raise ValueError('implementation changed in worker')
    evidence = dict(schema='sys-init-extended-host-worker-v1', seed=seed, plan_sha256=identity,
                    sources=plan['sources'], implementation=implementation, discovered=len(tests),
                    executed=result.testsRun, ids=result.executed_ids, skipped=len(result.skipped),
                    failures=len(result.failures), errors=len(result.errors), successful=result.wasSuccessful())
    print(json.dumps(evidence), flush=True)
    return 0 if result.wasSuccessful() and not result.skipped and result.testsRun == len(order) else 1


def validate_worker(raw, plan, identity, seed, implementation):
    value = records.parse_receipt(raw)
    records.catalog_fields(value, 'schema seed plan_sha256 sources implementation discovered executed ids skipped failures errors successful')
    if (value['schema'] != 'sys-init-extended-host-worker-v1' or value['seed'] != seed
            or value['plan_sha256'] != identity or value['sources'] != plan['sources']
            or value['implementation'] != implementation or value['ids'] != ordered_ids(plan, seed)
            or value['successful'] is not True):
        raise ValueError('extended worker identity/order mismatch')
    for key, expected in (('discovered', 54), ('executed', 54), ('skipped', 0), ('failures', 0), ('errors', 0)):
        if type(value[key]) is not int or value[key] != expected:
            raise ValueError('incomplete extended worker')
    return value


def campaign(path, directory, seed=None):
    started = time.monotonic()
    deadline = started + LIMITS['campaign_seconds']
    report = dict(schema='sys-init-extended-host-v1', result='running', mode='replay' if seed else 'campaign',
                  platform=platform.platform(), python=sys.version, executable=sys.executable,
                  started_unix=time.time(), limits=LIMITS, attempts=[], native='not-run')
    destination = directory / 'results.json'
    selected = []
    interrupted = False
    try:
        aggregate.publish_report(destination, report)
        plan, identity = load_plan(path)
        implementation = implementations()
        selected = [seed] if seed else plan['seeds']
        if any(s not in plan['seeds'] for s in selected):
            raise ValueError('seed absent from plan')
        report.update(plan_sha256=identity, sources=plan['sources'], implementation=implementation, seeds=selected)
        for index, current in enumerate(selected):
            load_plan(path, identity)
            if implementations() != implementation:
                raise ValueError('implementation changed')
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError('campaign deadline expired')
            command = [sys.executable, str(Path(__file__).resolve()), '--worker', '--plan', str(path),
                       '--seed', current, '--plan-sha256', identity]
            attempt = dict(seed=current, expected_ids=ordered_ids(plan, current), result='running', command=command)
            report['attempts'].append(attempt)
            aggregate.publish_report(destination, report)
            outcome = aggregate.run_check('seed-' + str(index), command, directory,
                                          timeout=min(60, remaining), limit=4194304)
            attempt.update(outcome)
            attempt['cleanup'] = ('direct-child-reaped; owned-group cleanup attempted' if outcome['result'] in
                                  ('timeout', 'output-limit', 'interrupted') else 'direct-child-reaped' if
                                  outcome['result'] in ('pass', 'fail') else 'not-established')
            for stream in ('stdout', 'stderr'):
                attempt[stream + '_sha256'] = digest(directory / outcome[stream]) if directory.is_relative_to(ROOT) else hashlib.sha256(records.read_metadata(directory / outcome[stream], directory)).hexdigest()
            if outcome['result'] == 'pass':
                try:
                    attempt['worker'] = validate_worker(records.read_metadata(directory / outcome['stdout'], directory),
                                                         plan, identity, current, implementation)
                except ValueError:
                    attempt['result'] = 'invalid-evidence'
                    raise
            else:
                interrupted = outcome['result'] == 'interrupted'
                raise ValueError('extended worker ' + outcome['result'])
            aggregate.publish_report(destination, report)
        load_plan(path, identity)
        if implementations() != implementation or time.monotonic() > deadline:
            raise ValueError('campaign identity/deadline changed')
        report['result'] = 'pass'
    except (OSError, ValueError, KeyboardInterrupt) as error:
        interrupted = interrupted or isinstance(error, KeyboardInterrupt)
        report.update(result='fail', error=dict(type=type(error).__name__, message=str(error)[:4096]))
    report['unattempted_seeds'] = selected[len(report['attempts']):]
    report['seconds'] = time.monotonic() - started
    report['finished_unix'] = time.time()
    try:
        aggregate.publish_report(destination, report)
        print(json.dumps(dict(schema=report['schema'], result=report['result'], report=str(destination))), flush=True)
    except OSError as error:
        aggregate.silence_failed_stream(sys.stdout)
        aggregate.report_diagnostic('extended report/delivery failed', error)
        return 130 if interrupted else 1
    return 130 if interrupted else 0 if report['result'] == 'pass' else 1


def main():
    parser = aggregate.Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='sys-init extended host 1')
    parser.add_argument('--plan', type=Path, default=ROOT / 'docs/extended-host-plan.json')
    parser.add_argument('--output-root', type=Path, default=ROOT / 'out/extended-host')
    parser.add_argument('--seed', help='replay exactly one seed from the plan')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--plan-sha256', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.worker:
            if not args.seed or not args.plan_sha256:
                parser.error('worker requires seed and plan identity')
            return worker(args.plan.resolve(), args.seed, args.plan_sha256)
        args.output_root.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix='run-', dir=args.output_root.resolve()))
        return campaign(args.plan.resolve(), directory, args.seed)
    except (OSError, ValueError, KeyboardInterrupt) as error:
        aggregate.report_diagnostic('extended host failed', error)
        return 130 if isinstance(error, KeyboardInterrupt) else 1


if __name__ == '__main__':
    raise SystemExit(main())
