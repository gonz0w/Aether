"""Bounded real-child adapter for the existing policy model; not PID 1 or sandboxing."""
from collections import deque
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import subprocess
import time
import uuid

from prototypes.runtime_model.model import Model, Service, Rejected


@dataclass(frozen=True)
class ReadinessDiagnostic:
    """Bounded internal observation; contains no service-supplied payload bytes."""
    code: str
    service: str
    generation: int
    received_bytes: int


@dataclass(frozen=True)
class Command:
    argv: tuple
    executable_sha256: str
    environment: tuple = ()


class HostRuntime:
    """Explicitly authorized trusted foreground children; no arbitrary descendant containment."""
    def __init__(self, services, commands, *, cwd):
        self.model = Model(services, epoch='host-' + uuid.uuid4().hex)
        if set(commands) != set(self.model.spec):
            raise Rejected('command ownership mismatch')
        self.commands = dict(commands)
        self.cwd = Path(cwd).resolve(strict=True)
        if not self.cwd.is_dir():
            raise Rejected('working directory')
        self.children = {}
        self.ready = {}
        self.pending = deque()
        self.log = deque(maxlen=128)
        self.diagnostics = deque(maxlen=128)
        self.closed = False
        self.lost_children = set()
        self.started = time.monotonic()
        for command in self.commands.values():
            self._validate(command)

    @staticmethod
    def _validate(command):
        if not isinstance(command, Command) or not isinstance(command.argv, tuple) or not 1 <= len(command.argv) <= 16:
            raise Rejected('structured argv required')
        if any(not isinstance(a, str) or '\0' in a or len(a.encode()) > 4096 for a in command.argv):
            raise Rejected('argument bounds')
        executable = Path(command.argv[0])
        if not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
            raise Rejected('absolute executable required')
        if hashlib.sha256(executable.read_bytes()).hexdigest() != command.executable_sha256:
            raise Rejected('changed executable')
        if len(command.environment) > 16:
            raise Rejected('environment bound')
        environment = dict(command.environment)
        if len(environment) != len(command.environment) or 'AETHER_READY_FD' in environment:
            raise Rejected('reserved/duplicate environment')
        if any(not isinstance(k, str) or not k or '=' in k or '\0' in k or not isinstance(v, str) or '\0' in v or len(v.encode()) > 4096 for k,v in environment.items()):
            raise Rejected('environment')

    def now(self):
        return max(self.model.now, int((time.monotonic() - self.started) * 1000))

    def event(self, kind, name, generation, value=0):
        self._require_open()
        self.pending.append((kind, name, generation, self.model.epoch, value))
        if len(self.pending) > 64:
            raise RuntimeError('pending observation bound')

    def _poll(self, child):
        # Sole, single-threaded waiter. Popen's ECHILD fallback invents exit zero.
        if child in self.lost_children:
            raise ChildProcessError('child wait ownership lost')
        if child.returncode is None:
            try:
                pid, status = os.waitpid(child.pid, os.WNOHANG)
            except ChildProcessError:
                self.lost_children.add(child)
                raise
            if pid:
                child.returncode = os.waitstatus_to_exitcode(status)
        return child.returncode

    def dispatch(self, effects):
        self._require_open()
        for action, name, generation in effects:
            key = (name, generation)
            self.log.append((action, name, generation))
            if action == 'launch':
                command = self.commands[name]
                read = write = None
                try:
                    self._validate(command)
                    environment = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', **dict(command.environment)}
                    if self.model.spec[name].milestone == 'notified-ready':
                        read, write = os.pipe()
                        os.set_blocking(read, False)
                        environment['AETHER_READY_FD'] = str(write)
                    child = subprocess.Popen(command.argv, cwd=self.cwd, env=environment,
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        close_fds=True, pass_fds=() if write is None else (write,))
                    self.children[key] = child
                    if read is not None:
                        self.ready[key] = [read, bytearray()]
                        read = None
                    self.event('launched', name, generation)
                except (OSError, Rejected):
                    self.event('launch_failed', name, generation)
                finally:
                    if read is not None: os.close(read)
                    if write is not None: os.close(write)
            elif action in ('stop','force'):
                child = self.children.get(key)
                if child in self.lost_children: continue
                if child is not None and self._poll(child) is None:
                    try:
                        child.terminate() if action == 'stop' else child.kill()
                    except ProcessLookupError:
                        pass  # Observation, not request success, establishes termination.
            elif action == 'reclaim':
                child = self.children.get(key)
                if child in self.lost_children:
                    self.event('cleanup_failed', name, generation)
                    continue
                if child is not None and self._poll(child) is None:
                    self.event('cleanup_failed', name, generation)
                    continue
                if child is not None: child.wait()
                self.children.pop(key, None)
                self._close_ready(key)
                self.event('cleaned', name, generation)
            else:
                raise RuntimeError('unsupported model effect: '+action)

    def _close_ready(self, key):
        value = self.ready.pop(key, None)
        if value is not None: os.close(value[0])

    def _require_open(self):
        if self.closed:
            raise Rejected('host runtime closed')

    def pump(self, *, sync_clock=False):
        self._require_open()
        # Observe at most four events per cut, preserving the model's explicit bound.
        events = []
        while self.pending and len(events) < 4:
            events.append(self.pending.popleft())
        for key, child in list(self.children.items()):
            if len(events) >= 4: break
            if child in self.lost_children: continue
            name,generation = key
            state = self.model.state[name]
            try:
                code = self._poll(child)
            except ChildProcessError:
                events.append(('lost', name, generation, self.model.epoch, 0))
                self._close_ready(key)
                continue
            if code is not None and state.generation == generation and state.phase != 'terminal':
                events.append(('exit' if code >= 0 else 'fault', name, generation, self.model.epoch, code if code >= 0 else -code))
                self._close_ready(key)
                continue
            ready = self.ready.get(key)
            if code is None and ready is not None:
                try: data = os.read(ready[0], 6-len(ready[1]))
                except BlockingIOError: continue
                ready[1].extend(data)
                if ready[1] == b'READY\n':
                    events.append(('ready', name, generation, self.model.epoch, 0))
                    self._close_ready(key)
                elif not data or not b'READY\n'.startswith(ready[1]):
                    diagnostic_code = ('SYSINIT-READY-MALFORMED' if data else
                            'SYSINIT-READY-INCOMPLETE' if ready[1] else 'SYSINIT-READY-CLOSED')
                    self.diagnostics.append(ReadinessDiagnostic(diagnostic_code, name, generation, len(ready[1])))
                    self.log.append(('invalid-ready', name, generation))
                    self._close_ready(key)
                    try: child.terminate()
                    except ProcessLookupError: pass
        now = self.now()
        deadlines = [v for s in self.model.state.values() for v in (s.deadline,s.due) if v is not None and v > self.model.now]
        if self.model.active is not None and self.model.active.deadline > self.model.now:
            deadlines.append(self.model.active.deadline)
        if events or (deadlines and now >= min(deadlines)) or (sync_clock and now > self.model.now):
            self.dispatch(self.model.batch(events, now=now))
        return bool(events)

    def start(self, names, budget=3000):
        self.pump(sync_clock=True)
        ident,effects = self.model.start(names,budget=budget)
        self.dispatch(effects)
        return ident

    def stop(self, names, budget=3000, shutdown=False):
        self.pump(sync_clock=True)
        ident,effects = self.model.stop(names,budget=budget,shutdown=shutdown)
        self.dispatch(effects)
        return ident

    def until(self, predicate, timeout=5):
        end = time.monotonic()+timeout
        while not predicate():
            if time.monotonic() >= end: raise TimeoutError('host fixture watchdog')
            if not self.pump(): time.sleep(.005)

    def close(self):
        # Emergency cleanup is scoped only to Popen objects created by this adapter.
        self.closed = True
        self.pending.clear()
        errors=[]
        for key,child in list(self.children.items()):
            try:
                if self._poll(child) is None: child.kill()
                child.wait(timeout=2)
            except (OSError,subprocess.TimeoutExpired) as error:
                if isinstance(error, ChildProcessError): self._close_ready(key)
                errors.append(str(error))
                continue
            self._close_ready(key)
            self.children.pop(key, None)
        if errors: raise RuntimeError('owned-child cleanup failed: '+repr(errors))
