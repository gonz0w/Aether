# SPDX-License-Identifier: BSD-2-Clause
"""Bounded foreground serial transfer for the persistent Zsh recipe."""

from contextlib import contextmanager
import os
import re
import resource
import select
import signal
import subprocess
import termios
import time
import tty


FIRST_PROMPT_SECONDS = 60
SESSION_SECONDS = 330
TOTAL_SECONDS = 360
STOP_SECONDS = 9
PROMPT = b'AETHER-ZSH> '
STARTUP_FAILURE = b'AETHER PANIC: native supervisor terminated'
HALT = re.compile(rb'(?:\A|\n)NATIVE init halted ticks=[0-9]+ idle=[0-9]+ '
                  rb'reclaimed=[0-9]+\nAETHER NATIVE BLOCK PASS\n')
LIMITS = {'stdout': 65536, 'stderr': 4 * 1024 * 1024}


@contextmanager
def terminal(manual):
    if not manual:
        yield
        return
    if not os.isatty(0) or not os.isatty(1):
        raise ValueError('manual serial input requires a foreground terminal')
    if os.ttyname(0) != os.ttyname(1) or os.tcgetpgrp(0) != os.getpgrp():
        raise ValueError('manual serial input requires foreground ownership')
    mode = termios.tcgetattr(0)
    blocking = os.get_blocking(1)
    try:
        tty.setraw(0, termios.TCSANOW)
        os.set_blocking(1, False)
        yield
    finally:
        try:
            os.set_blocking(1, blocking)
        finally:
            termios.tcsetattr(0, termios.TCSANOW, mode)
            # Leave queued guest keystrokes out of the restored host shell.
            termios.tcflush(0, termios.TCIFLUSH)


@contextmanager
def interrupts():
    pending = []
    saved = {}
    try:
        def remember(signum, _):
            if not pending:
                pending.append(signum)

        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            saved[signum] = signal.signal(signum, remember)
        yield pending
    finally:
        for signum, handler in saved.items():
            signal.signal(signum, handler)


def set_child_limits(file_limit):
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))


def group_absent(pid):
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        return True
    return False


def exited(child):
    # Peek without reaping. An exited leader may still have group members and
    # its unreaped PID protects the ownership of the original process group.
    return os.waitid(os.P_PID, child.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None


class Transfer:
    def __init__(self, child, record, manual):
        self.child = child
        self.record = record
        self.manual = manual
        self.sources = {child.stdout.fileno(): 'stdout', child.stderr.fileno(): 'stderr'}
        self.data = {name: bytearray() for name in LIMITS}
        self.overflow = set()
        self.displayed = 0
        self.pending = b''
        self.input_fd = child.stdin.fileno() if child.stdin is not None else None

    @property
    def uart(self):
        return self.data['stdout']

    def pump(self, deadline, *, operator_input=False, display=True):
        reads = list(self.sources)
        writes = []
        if operator_input and not self.pending:
            reads.append(0)
        if self.pending:
            writes.append(self.input_fd)
        if display and self.manual and self.displayed < len(self.uart):
            writes.append(1)
        readable, writable, _ = select.select(reads, writes, [], min(.05, max(0, deadline - time.monotonic())))
        if time.monotonic() >= deadline:
            return
        for fd in readable:
            self.read(fd)
        for fd in writable:
            self.write(fd)

    def read(self, fd):
        try:
            block = os.read(fd, 4096)
        except BlockingIOError:
            return
        if fd == 0:
            if not block:
                raise OSError('operator input ended before guest shutdown')
            self.pending = block
            return
        name = self.sources[fd]
        if not block:
            del self.sources[fd]
            self.record[name + '_eof'] = True
            return
        buffer = self.data[name]
        room = LIMITS[name] - len(buffer)
        buffer.extend(block[:room])
        if len(block) > room:
            self.overflow.add(name)

    def write(self, fd):
        try:
            if fd == 1:
                self.displayed += os.write(fd, self.uart[self.displayed:self.displayed + 4096])
            else:
                count = os.write(fd, self.pending)
                self.pending = self.pending[count:]
                self.record['input_bytes'] += count
                if not self.manual:
                    self.record['input_stages'][-1]['accepted_bytes'] += count
        except BlockingIOError:
            return


def run_session(transfer, started, deadline, manual, failure, inputs, pending_signal):
    record = transfer.record
    prompt_by = started + FIRST_PROMPT_SECONDS
    active_until = min(deadline, started + SESSION_SECONDS) - STOP_SECONDS
    prompt_cursor = 0
    stage = 0
    while True:
        if pending_signal:
            raise RuntimeError('host signal ' + str(pending_signal[0]))
        if transfer.overflow:
            raise ValueError('serial capture limit exceeded')
        now = time.monotonic()
        if now >= active_until:
            raise TimeoutError('serial session deadline')
        if 'first_prompt_offset' not in record and now >= prompt_by:
            raise TimeoutError('first prompt or startup failure deadline')

        raw = transfer.uart
        lines = raw.split(b'\n')[:-1]
        panics = [line for line in lines if line.startswith(b'AETHER PANIC:')]
        if panics:
            if failure and panics == [STARTUP_FAILURE] and PROMPT not in raw:
                return 'startup-failure'
            raise RuntimeError('unexpected guest panic')
        if HALT.search(raw):
            if failure or stage != len(inputs) or transfer.pending:
                raise RuntimeError('guest halt before selected input completed')
            return 'halt'
        if not transfer.sources or exited(transfer.child):
            raise RuntimeError('emulator exited before terminal marker')

        prompt = raw.find(PROMPT, prompt_cursor)
        if prompt >= 0:
            if failure:
                raise RuntimeError('unexpected prompt during storage startup failure')
            if 'first_prompt_offset' not in record:
                record.update(first_prompt_offset=prompt, first_prompt_seconds=now - started)
            if stage < len(inputs):
                if transfer.pending or raw.find(PROMPT, prompt + len(PROMPT)) >= 0:
                    raise RuntimeError('guest prompt repeated before input was accepted')
                record['input_stages'].append({'prompt_offset': prompt, 'uart_offset': len(raw),
                                               'input_bytes': len(inputs[stage]), 'accepted_bytes': 0})
                transfer.pending = inputs[stage]
                stage += 1
            prompt_cursor = prompt + len(PROMPT)
        until = active_until if 'first_prompt_offset' in record else min(active_until, prompt_by)
        transfer.pump(until, operator_input=manual and 'first_prompt_offset' in record)


def stop(child, transfer, record, owned, deadline):
    """Stop the original group before reaping and distinguish stop from EOF."""
    if child.stdin is not None:
        child.stdin.close()
    if transfer is not None:
        transfer.pending = b''
    for signum in (signal.SIGTERM, signal.SIGKILL):
        if (transfer is None or not transfer.sources) and exited(child):
            break
        if owned:
            try:
                os.killpg(child.pid, signum)
                record['stop_signal_sent'] = True
            except ProcessLookupError:
                pass
            except PermissionError:
                # Some hosts reject a group signal after its leader exits.
                # Reap only once and still require the group to be absent.
                if not exited(child):
                    raise
        phase_end = min(deadline, time.monotonic() + 3)
        while time.monotonic() < phase_end:
            if (transfer is None or not transfer.sources) and exited(child):
                break
            if transfer is None:
                time.sleep(min(.05, max(0, phase_end - time.monotonic())))
            else:
                transfer.pump(phase_end, display=False)
        if (transfer is None or not transfer.sources) and exited(child):
            break
    record['returncode'] = child.wait(timeout=max(0, deadline - time.monotonic()))
    record['group_absent'] = group_absent(child.pid)
    record['host_stop_confirmed'] = record['group_absent']
    if transfer is not None:
        while transfer.sources and time.monotonic() < deadline:
            transfer.pump(deadline, display=False)
        while transfer.manual and transfer.displayed < len(transfer.uart) and time.monotonic() < deadline:
            transfer.pump(deadline)


def capture(argv, *, file_limit, manual=False, failure=False, inputs=()):
    """Run one reviewed command. Return observed UART and host transport facts."""
    if (manual and failure) or ((manual or failure) and inputs):
        raise ValueError('select one serial input mode')
    if any(type(item) is not bytes or not 1 <= len(item) <= 71 or not item.endswith(b'\r')
           for item in inputs):
        raise ValueError('invalid fixed serial input')
    if signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL:
        raise ValueError('default SIGCHLD required for direct-child ownership')

    started = time.monotonic()
    deadline = started + TOTAL_SECONDS
    child = transfer = None
    owned = False
    record = dict(status='failed', terminal=None, group_absent=False, host_stop_confirmed=False,
                  stdout_eof=False, stderr_eof=False, stop_signal_sent=False, input_bytes=0,
                  input_stages=[], qemu_process_file_limit=file_limit)
    try:
        with interrupts() as pending_signal, terminal(manual):
            try:
                child = subprocess.Popen(argv, stdin=subprocess.PIPE if manual or inputs else subprocess.DEVNULL,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         start_new_session=True, close_fds=True, preexec_fn=lambda: set_child_limits(file_limit),
                                         env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
                record['pid'] = child.pid
                transfer = Transfer(child, record, manual)
                pgid, sid = os.getpgid(child.pid), os.getsid(child.pid)
                record.update(pgid=pgid, sid=sid)
                owned = pgid == sid == child.pid and child.pid != os.getpgrp()
                if not owned:
                    raise RuntimeError('emulator did not enter its own group and session')
                if child.stdin is not None:
                    os.set_blocking(child.stdin.fileno(), False)
                record['terminal'] = run_session(transfer, started, deadline, manual, failure, inputs, pending_signal)
            except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
                record['error'] = str(error)
            finally:
                if child is not None:
                    try:
                        stop_by = min(deadline, started + SESSION_SECONDS, time.monotonic() + STOP_SECONDS)
                        stop(child, transfer, record, owned, stop_by)
                    except (OSError, subprocess.SubprocessError) as error:
                        record['stop_error'] = str(error)
                    finally:
                        child.stdout.close()
                        child.stderr.close()
    except (OSError, ValueError) as error:
        record['terminal_error'] = str(error)

    raw = bytes(transfer.uart) if transfer is not None else b''
    if transfer is not None:
        record['capture_overflow'] = sorted(transfer.overflow)
        record['stderr_hex'] = bytes(transfer.data['stderr'][-4096:]).hex()
        record['stderr_bytes'] = len(transfer.data['stderr'])
        if manual:
            record['display_complete'] = transfer.displayed == len(raw)
    record['elapsed_seconds'] = time.monotonic() - started
    record['capture_complete'] = (
        transfer is not None and not transfer.overflow and record['stdout_eof'] and record['stderr_eof']
    )
    if (record['terminal'] and record['host_stop_confirmed'] and record['capture_complete']
            and record['stop_signal_sent'] and record.get('display_complete', True)
            and not any(key in record for key in ('error', 'stop_error', 'terminal_error'))
            and record['elapsed_seconds'] < TOTAL_SECONDS):
        record['status'] = 'complete'
    return raw, record
