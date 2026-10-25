# SPDX-License-Identifier: BSD-2-Clause
"""Owned, bounded host tool runs; no target/runtime dependency."""
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

def run_tool(command, environment, log_path, timeout=180, limit=4 * 1024 * 1024, *, cwd=None):
    """Bound trusted tool output and duration; retain the accepted output prefix."""
    end = time.monotonic() + timeout
    with log_path.open('wb') as log:
        child = subprocess.Popen(command, env=environment, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, start_new_session=True, cwd=cwd)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(child.stdout, selectors.EVENT_READ)
                total = 0
                while selector.get_map():
                    remaining = end - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(command, timeout)
                    for key, _ in selector.select(remaining):
                        block = os.read(key.fd, min(65536, limit - total + 1))
                        if not block:
                            selector.unregister(key.fileobj)
                            continue
                        log.write(block[:limit - total])
                        total += len(block)
                        if total > limit:
                            raise ValueError('tool output limit exceeded')
                code = child.wait(timeout=max(0, end - time.monotonic()))
                if code:
                    raise subprocess.CalledProcessError(code, command)
        except BaseException:
            # Only this invocation's owned group; tools must not detach.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
            raise
        finally:
            child.stdout.close()
    return log_path.read_bytes()


def run_recorded(command, log_path, caller, timeout=180, limit=4 * 1024 * 1024, *, cwd=None):
    sources = [Path(__file__).resolve(), Path(caller).resolve()]
    record = dict(command=command, cwd=str(Path.cwd() if cwd is None else Path(cwd).resolve()),
                  result='running', timeout_seconds=timeout,
                  output_limit=limit, sources={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                              for p in sources})
    receipt = log_path.with_suffix(log_path.suffix + '.json')
    def save():
        receipt.write_text(json.dumps(record, indent=2) + '\n')
    save()
    try:
        raw = run_tool(command, os.environ, log_path, timeout, limit, cwd=cwd)
        record.update(result='pass', returncode=0)
        return raw
    except subprocess.TimeoutExpired:
        record['result'] = 'timeout'
        raise
    except subprocess.CalledProcessError as error:
        record.update(result='fail', returncode=error.returncode)
        raise
    except ValueError as error:
        record.update(result='output-limit', error=str(error))
        raise
    except OSError as error:
        record.update(result='infra-error', error=str(error))
        raise
    except BaseException:
        record['result'] = 'interrupted'
        raise
    finally:
        save()


def run_completed(command, log_path, caller, *, cwd=None, timeout=120, limit=4 * 1024 * 1024):
    """Return actual nonzero tool exits for caller-owned semantic test oracles.

    Timeout, overflow and infrastructure failures still raise; no invented exit
    status may stand in for an expected guest rejection.
    """
    try:
        raw = run_recorded(command, log_path, caller, timeout, limit, cwd=cwd)
        return subprocess.CompletedProcess(command, 0, raw)
    except subprocess.CalledProcessError as error:
        return subprocess.CompletedProcess(command, error.returncode, log_path.read_bytes())
