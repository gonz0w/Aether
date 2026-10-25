#!/usr/bin/env python3
"""Run offline development checks and retain a private report directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, self.prog + ': ' + message + '\n')


def require_complete(result, discovered):
    if discovered <= 0 or result.testsRun != discovered or result.skipped or not result.wasSuccessful():
        raise ValueError('empty, incomplete, skipped or failed required suite')


def evidence_worker():
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_harness*.py')
    discovered = suite.countTestCases()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    require_complete(result, discovered)
    print(json.dumps({'tests': result.testsRun, 'result': 'pass'}))


def run_check(name, argv, directory, timeout=60, limit=4 * 1024 * 1024):
    """Logs survive failure; watchdog expiry is distinct from assertion failure."""
    started = time.monotonic()
    manage_termination = threading.current_thread() is threading.main_thread()
    previous_termination = signal.getsignal(signal.SIGTERM) if manage_termination else None
    record = dict(name=name, command=argv, timeout_seconds=timeout, output_limit_bytes=limit,
                  cleanup_grace_seconds=1,
                  stdout=name + '.stdout', stderr=name + '.stderr')
    with (directory / record['stdout']).open('wb') as stdout, (directory / record['stderr']).open('wb') as stderr:
        try:
            child = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     start_new_session=True,
                                     env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            try:
                if manage_termination:
                    signal.signal(signal.SIGTERM, signal.default_int_handler)
                deadline = started + timeout
                total = 0
                with selectors.DefaultSelector() as selector:
                    selector.register(child.stdout, selectors.EVENT_READ, stdout)
                    selector.register(child.stderr, selectors.EVENT_READ, stderr)
                    while selector.get_map():
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise subprocess.TimeoutExpired(argv, timeout)
                        for key, _ in selector.select(remaining):
                            block = os.read(key.fd, min(65536, limit - total + 1))
                            if not block:
                                selector.unregister(key.fileobj)
                                continue
                            key.data.write(block[:limit - total])
                            total += len(block)
                            if total > limit:
                                raise OverflowError('gate output limit exceeded')
                code = child.wait(timeout=max(0, deadline - time.monotonic()))
                record.update(result='pass' if code == 0 else 'fail', returncode=code)
            except BaseException as error:
                if manage_termination:
                    signal.signal(signal.SIGTERM, signal.SIG_IGN)
                # Give responsive Python wrappers time to clean their own workers.
                try:
                    try:
                        os.killpg(child.pid, signal.SIGINT)
                    except ProcessLookupError:
                        pass
                    try:
                        child.wait(timeout=record['cleanup_grace_seconds'])
                    except subprocess.TimeoutExpired:
                        pass
                finally:
                    # Force cleanup of this invocation's remaining owned group.
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    child.wait()
                if isinstance(error, (subprocess.TimeoutExpired, KeyboardInterrupt, OverflowError)):
                    outcome = ('timeout' if isinstance(error, subprocess.TimeoutExpired) else
                               'interrupted' if isinstance(error, KeyboardInterrupt) else 'output-limit')
                    record.update(result=outcome, returncode=child.returncode)
                else:
                    raise
            finally:
                if manage_termination:
                    signal.signal(signal.SIGTERM, previous_termination)
                child.stdout.close()
                child.stderr.close()
        except OSError as error:
            record.update(result='error', error=str(error))
    record['seconds'] = time.monotonic() - started
    return record


SOURCE_FILE_LIMIT = 4 * 1024 * 1024
SOURCE_TOTAL_LIMIT = 64 * 1024 * 1024
SOURCE_ENTRY_LIMIT = 200000
SOURCE_COUNT_LIMIT = 10000


def snapshot_stat(path):
    anchor = ROOT.absolute()
    if not stat.S_ISDIR(anchor.lstat().st_mode):
        raise ValueError('invalid source root')
    parts = path.absolute().relative_to(anchor).parts
    if any(part in ('.', '..') for part in parts):
        raise ValueError('invalid source path')
    current = anchor
    for part in parts:
        current /= part
        if stat.S_ISLNK(current.lstat().st_mode):
            raise ValueError('source symlink rejected')
    return current.lstat()


def snapshot_paths():
    paths = set()
    pending = [ROOT / base for base in ('scripts', 'prototypes', 'tests', 'docs')]
    entries = 0
    while pending:
        directory = pending.pop()
        if not stat.S_ISDIR(snapshot_stat(directory).st_mode):
            raise ValueError('source directory required')
        with os.scandir(directory) as children:
            for child in children:
                entries += 1
                if entries > SOURCE_ENTRY_LIMIT:
                    raise ValueError('source traversal limit')
                path = Path(child.path)
                if child.name == 'archive':
                    continue
                mode = child.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    pending.append(path)
                elif not stat.S_ISREG(mode):
                    raise ValueError('source tree special file rejected')
                relative = path.relative_to(ROOT)
                selected = (child.name.endswith('.py')
                            or (path.parent == ROOT / 'docs' and child.name.endswith('.lock'))
                            or (relative.parts[:2] == ('docs', 'vendor') and child.name == 'SHA256SUMS'))
                if selected:
                    paths.add(path)
                    if len(paths) > SOURCE_COUNT_LIMIT:
                        raise ValueError('source count limit')
    paths.update(ROOT / name for name in (
        'prototypes/native-supervisor/sample_receipts.rs', 'tests/native_sample_receipts.rs',
        'prototypes/native-supervisor/pending_history.rs', 'tests/native_pending_history.rs',
        'prototypes/native-supervisor/cut_reservation.rs', 'tests/native_cut_reservation.rs',
        'docs/native-coverage.json', 'docs/static-tools.json', 'docs/native-boundaries.json',
        'docs/quality-inventory.json', 'docs/QUALITY-PROCESS.md', 'docs/STANDARDS-UPDATE-REVIEW.md',
        'AGENTS.md', 'CONTRIBUTING.md'))
    if len(paths) > SOURCE_COUNT_LIMIT:
        raise ValueError('source count limit')
    return sorted(paths)


def snapshot_digest(path, remaining):
    before = snapshot_stat(path)
    limit = min(SOURCE_FILE_LIMIT, remaining)
    if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
        raise ValueError('source type or byte limit')
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
    try:
        opened = os.fstat(fd)
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns')
        identity = lambda value: tuple(getattr(value, field) for field in fields)
        if not stat.S_ISREG(opened.st_mode) or identity(opened) != identity(before):
            raise ValueError('source changed before read')
        digest = hashlib.sha256(); size = 0
        while size <= limit:
            chunk = os.read(fd, min(65536, limit + 1 - size))
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        if size > limit:
            raise ValueError('source byte limit')
        if size != opened.st_size or identity(os.fstat(fd)) != identity(opened) or identity(snapshot_stat(path)) != identity(opened):
            raise ValueError('source changed during read')
        return digest.hexdigest(), size
    finally:
        os.close(fd)


def source_hashes():
    paths = snapshot_paths()
    hashes = {}; total = 0
    for path in paths:
        digest, size = snapshot_digest(path, SOURCE_TOTAL_LIMIT - total)
        total += size
        hashes[str(path.relative_to(ROOT))] = digest
    if snapshot_paths() != paths:
        raise ValueError('source membership changed')
    return hashes


def silence_failed_stream(stream):
    # Avoid a second buffered write failure during interpreter shutdown.
    try:
        fd = stream.fileno()
        replacement = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(replacement, fd)
        finally:
            os.close(replacement)
    except (AttributeError, OSError, ValueError):
        pass


def report_diagnostic(stage, error):
    try:
        print('development checks: ' + stage + ': ' + json.dumps(str(error)[:4096]),
              file=sys.stderr, flush=True)
    except OSError:
        silence_failed_stream(sys.stderr)


def publish_report(destination, report):
    fd, temporary = tempfile.mkstemp(prefix='.results-', suffix='.tmp', dir=destination.parent)
    try:
        with os.fdopen(fd, 'w') as output:
            json.dump(report, output, indent=2)
            output.write('\n')
        os.replace(temporary, destination)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def run_suite(directory, commands, historical=True):
    report = dict(schema='sys-init-development-checks-v1', result='running',
                  platform=platform.platform(), machine=platform.machine(),
                  python=sys.version, executable=sys.executable, cwd=str(ROOT),
                  source_sha256={}, checks=[], native='not-run',
                  historical_native_evidence='required' if historical else 'not-run')
    destination = directory / 'results.json'
    stage = 'initial-report'
    interrupted = False
    try:
        publish_report(destination, report)
        stage = 'initial-snapshot'
        before = source_hashes()
        report['source_sha256'] = before
        stage = 'snapshot-report'
        publish_report(destination, report)
        for name, argv in commands:
            stage = 'gate:' + name
            record = run_check(name, argv, directory)
            report['checks'].append(record)
            stage = 'gate-progress:' + name
            print(name + ': ' + record['result'], file=sys.stderr, flush=True)
            stage = 'gate-report:' + name
            publish_report(destination, report)
            if record['result'] != 'pass':
                break
        stage = 'final-snapshot'
        report['sources_unchanged'] = before == source_hashes()
    except (OSError, ValueError, KeyboardInterrupt) as error:
        interrupted = isinstance(error, KeyboardInterrupt)
        if stage.startswith('gate-progress:') and isinstance(error, OSError):
            silence_failed_stream(sys.stderr)
        report['sources_unchanged'] = False
        report['error'] = dict(stage=stage, type=type(error).__name__, message=str(error)[:4096])
    report['not_run'] = [name for name, _ in commands[len(report['checks']):]]
    report['result'] = ('pass' if 'error' not in report and not report['not_run']
                        and report['sources_unchanged']
                        and all(r['result'] == 'pass' for r in report['checks']) else 'fail')
    interrupted = interrupted or any(r['result'] == 'interrupted' for r in report['checks'])
    try:
        publish_report(destination, report)
    except (OSError, ValueError, KeyboardInterrupt) as error:
        interrupted = interrupted or isinstance(error, KeyboardInterrupt)
        report_diagnostic('report publication failed', error)
        return 130 if interrupted else 1
    try:
        print(json.dumps({'schema': report['schema'], 'result': report['result'], 'report': str(destination)}), flush=True)
    except OSError as error:
        silence_failed_stream(sys.stdout)
        report_diagnostic('summary delivery failed', error)
        return 130 if interrupted else 1
    return 130 if interrupted else 0 if report['result'] == 'pass' else 1


def main():
    parser = Parser(description=__doc__, epilog='Example: python3 scripts/check-all.py. '
                    'Requires a POSIX host, Python 3.10+ and installed Rust 1.98.0. Runs trusted child fixtures; '
                    'does not test native Aether. See docs/DEVELOPMENT-CHECKS.md.')
    parser.add_argument('--version', action='version', version='sys-init development checks 1')
    parser.add_argument('--current', action='store_true',
                        help='check current sources/host behavior without historical native bundle replay; not release evidence')
    parser.add_argument('--output-root', type=Path, default=ROOT / 'out/checks',
                        help='parent for a newly created private run directory')
    args = parser.parse_args()
    if os.name != 'posix':
        print('POSIX host required; unsupported hosts cannot pass', file=sys.stderr)
        return 2
    try:
        args.output_root.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix='run-', dir=args.output_root.resolve()))
    except (OSError, ValueError, KeyboardInterrupt) as error:
        report_diagnostic('output directory unavailable', error)
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    commands = [(name, [sys.executable, str(ROOT / ('docs/check-' + name + '.py'))])
                for name in ('standards', 'experience', 'distribution')]
    commands += [
        ('quality-process', [sys.executable, str(ROOT / 'scripts/check-quality-process.py')]),
        ('static', [sys.executable, str(ROOT / 'scripts/check-static.py')]),
        ('native-evidence', [sys.executable, str(ROOT / 'scripts/check-native-evidence.py')]),
        ('evidence', [sys.executable, str(Path(__file__).resolve()), '--evidence-worker']),
        ('sample-receipts', [sys.executable, str(Path(__file__).resolve()), '--sample-receipts-worker']),
        ('model', [sys.executable, str(ROOT / 'scripts/check-runtime-model.py'),
                   '--output', str(directory / 'model.json')]),
        ('host', [sys.executable, str(ROOT / 'scripts/check-host-runtime.py')]),
    ]
    if args.current:
        commands = [(name, argv) for name, argv in commands if name != 'native-evidence']
        print('[NOT RUN] Historical native bundle replay (--current); no native acceptance claim',
              file=sys.stderr)
    return run_suite(directory, commands, historical=not args.current)


if __name__ == '__main__':
    if sys.argv[1:] == ['--evidence-worker']:
        evidence_worker()
    elif sys.argv[1:] == ['--sample-receipts-worker']:
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_native_sample_receipts.py')
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
        require_complete(result, 14)
    else:
        raise SystemExit(main())
