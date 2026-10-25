# SPDX-License-Identifier: BSD-2-Clause
"""Bounded two-stream capture for trusted POSIX test workers."""
import io
import os
import selectors
import signal
import subprocess
import time


class OutputLimitError(RuntimeError):
    def __init__(self, limit, output, stderr):
        super().__init__(f'worker output limit exceeded ({limit} bytes)')
        self.output = output
        self.stderr = stderr


def text_output(raw):
    # Match subprocess text mode: default host encoding and universal newlines.
    with io.TextIOWrapper(io.BytesIO(raw)) as stream:
        return stream.read()


def run_capture(command, *, cwd, timeout=30, limit=4 * 1024 * 1024):
    deadline = time.monotonic() + timeout
    output, errors = bytearray(), bytearray()
    child = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True)
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ, output)
            selector.register(child.stderr, selectors.EVENT_READ, errors)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, timeout)
                for key, _ in selector.select(remaining):
                    available = limit - len(output) - len(errors)
                    block = os.read(key.fd, min(65536, available + 1))
                    if not block:
                        selector.unregister(key.fileobj)
                        continue
                    key.data.extend(block[:available])
                    if len(block) > available:
                        raise OutputLimitError(limit, bytes(output), bytes(errors))
        code = child.wait(timeout=max(0, deadline - time.monotonic()))
    except BaseException as error:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait()
        if isinstance(error, subprocess.TimeoutExpired):
            error.output, error.stderr = bytes(output), bytes(errors)
        raise
    finally:
        child.stdout.close()
        child.stderr.close()
    return subprocess.CompletedProcess(command, code, text_output(output), text_output(errors))
