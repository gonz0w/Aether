#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent watchdog controls, including a TERM-resistant descendant."""
import contextlib
import io
import importlib.util
from pathlib import Path
import subprocess
import signal
import sys
import tempfile
import time

spec = importlib.util.spec_from_file_location(
    'watchdog', Path(__file__).with_name('check-watchdog.py'))
watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watchdog)
with tempfile.TemporaryDirectory(prefix='pkg-watchdog-control-') as directory:
    root = Path(directory)
    log = root / 'suite.log'
    log.write_text('')
    assert watchdog.qualify(0, log) == 125
    log.write_text('All sixteen active fixture tests passed.\n')
    assert watchdog.qualify(0, log) == 125
    log.write_text(log.read_text() +
                   'All three pinned standards checks passed (not runtime conformance).\n')
    assert watchdog.qualify(0, log) == 0
    assert watchdog.qualify(7, log) == 7
    assert watchdog.run([sys.executable, '-c', 'print("known-pass")'], root, 5) == 0
    assert (root / 'suite.log').read_text().strip() == 'known-pass'
    assert watchdog.run([sys.executable, '-c', 'raise SystemExit(7)'], root, 5) == 7
    # The leader and descendant ignore TERM. A changing heartbeat demonstrates
    # a live descendant without relying on platform-specific zombie PID behavior.
    heartbeat = root / 'heartbeat'
    worker = root / 'worker.py'
    worker.write_text('''import signal, sys, time
from pathlib import Path
signal.signal(signal.SIGTERM, signal.SIG_IGN)
p = Path(sys.argv[1])
while True:
    p.write_text(str(time.monotonic_ns()))
    time.sleep(0.01)
''')
    leader = root / 'leader.py'
    leader.write_text('''import signal, subprocess, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2]])
while True: time.sleep(1)
''')
    assert watchdog.run([sys.executable, str(leader), str(worker),
                         str(heartbeat)], root, 2) == 124
    before = heartbeat.read_text()
    time.sleep(0.1)  # Observation window after cleanup, not startup synchronization.
    assert heartbeat.read_text() == before
    # A leader cannot report success while leaving a live background worker.
    heartbeat.unlink()
    leader.write_text("""import subprocess, sys, time
from pathlib import Path
subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2]])
while not Path(sys.argv[2]).exists(): time.sleep(0.01)
""")
    assert watchdog.run([sys.executable, str(leader), str(worker),
                         str(heartbeat)], root, 5) == 125
    # Signal the watchdog only after the worker publishes its ready heartbeat.
    heartbeat.unlink()
    harness = root / 'harness.py'
    harness.write_text(f"""import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('watchdog', {str(Path(__file__).with_name('check-watchdog.py').resolve())!r})
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
sys.exit(w.run([sys.executable, {str(worker)!r}, {str(heartbeat)!r}], Path({str(root)!r}), 10))
""")
    runner = subprocess.Popen([sys.executable, str(harness)])
    try:
        deadline = time.monotonic() + 5
        while not heartbeat.exists():
            if runner.poll() is not None or time.monotonic() >= deadline:
                raise AssertionError('signal control never became ready')
            time.sleep(0.01)
        runner.send_signal(signal.SIGTERM)
        assert runner.wait(timeout=5) == 143
        before = heartbeat.read_text()
        time.sleep(0.1)
        assert heartbeat.read_text() == before
    finally:
        if runner.poll() is None:
            runner.terminate()
            runner.wait(timeout=5)
    try:
        watchdog.run([str(root / 'missing-executable')], root, 5)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('missing executable was accepted')
    # Missing suite executable must leave a failed receipt, not just a printed root.
    failure_root = root / 'startup-failure'
    failure_root.mkdir()
    original_run = watchdog.run
    original_mkdtemp = watchdog.tempfile.mkdtemp
    output, diagnostic = io.StringIO(), io.StringIO()
    try:
        watchdog.tempfile.mkdtemp = lambda **kwargs: str(failure_root)
        watchdog.run = lambda command, directory, seconds: original_run(
            [str(root / 'missing-suite')], directory, seconds)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(diagnostic):
            assert watchdog.main() == 125
    finally:
        watchdog.run = original_run
        watchdog.tempfile.mkdtemp = original_mkdtemp
    receipt = (failure_root / 'result.txt').read_text()
    assert receipt.startswith('result=fail\nexit=125\n'), receipt
    assert 'deadline_seconds=600\n' in receipt
    assert (failure_root / 'suite.log').read_bytes() == b''
    assert 'check-run: infra-error:' in diagnostic.getvalue()
    assert f'check-run: fail; retained_root={failure_root.resolve()}' in output.getvalue()
    assert 'check-run: pass' not in output.getvalue()
print('PASS: completion-marker controls; watchdog success, exit propagation, timeout/descendant cleanup, leaked child, signal cleanup, missing executable and startup receipt')
