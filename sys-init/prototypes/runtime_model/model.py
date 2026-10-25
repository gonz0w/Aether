"""Bounded policy model. Effects are requests; only injected events complete them."""
from collections import deque
from dataclasses import asdict, dataclass
import re


@dataclass(frozen=True)
class Service:
    name: str
    kind: str = 'daemon'
    milestone: str = 'started'
    requires: tuple = ()
    after: tuple = ()
    retries: int = 0
    delay: int = 1
    startup: int = 10
    stop: int = 5
    cleanup: int = 5
    supported: bool = True


@dataclass
class State:
    generation: int = 0
    desired: bool = False
    phase: str = 'absent'
    owned: bool = False
    launch_pending: bool = False
    started: bool = False
    ready: bool = False
    completed: bool = False
    cleanup: str = 'complete'
    outcome: str = 'pending'
    reason: str = ''
    terminal: str | None = None
    terminal_detail: int | None = None
    retries_used: int = 0
    retry_allowed: bool = False
    due: int | None = None
    deadline: int | None = None
    reclaim_sent: bool = False
    stop_sent: bool = False


@dataclass
class Operation:
    id: int
    kind: str
    scope: tuple
    deadline: int
    status: str = 'pending'
    cancelling: bool = False
    restart: str | None = None
    shutdown: bool = False


class Rejected(ValueError):
    pass


class Model:
    MAX_EVENTS = 256

    def __init__(self, services, *, epoch='boot-1', revision='config-1'):
        if not isinstance(services, (tuple, list)) or not 1 <= len(services) <= 8:
            raise Rejected('service bound')
        if not all(isinstance(s, Service) for s in services):
            raise Rejected('service type')
        self.spec = {s.name: s for s in services if isinstance(s.name, str)}
        if len(self.spec) != len(services):
            raise Rejected('duplicate/invalid service')
        for label in (epoch, revision):
            if not isinstance(label, str) or not 1 <= len(label) <= 64:
                raise Rejected('identity bound')
        edges = 0
        for s in services:
            if not re.fullmatch(r'[a-z][a-z0-9_-]{0,31}', s.name):
                raise Rejected('service name')
            if s.kind not in ('daemon', 'oneshot') or s.milestone not in ('started', 'notified-ready', 'completed'):
                raise Rejected('kind/milestone')
            if (s.kind == 'oneshot') != (s.milestone == 'completed'):
                raise Rejected('kind/evidence mismatch')
            if type(s.retries) is not int or not 0 <= s.retries <= 2 or (s.kind == 'oneshot' and s.retries):
                raise Rejected('retry bound')
            if any(type(n) is not int or not 1 <= n <= 1000000 for n in (s.delay, s.startup, s.stop, s.cleanup)):
                raise Rejected('time bound')
            if s.supported is not True:
                raise Rejected('required policy unsupported')
            if not isinstance(s.requires, tuple) or not isinstance(s.after, tuple):
                raise Rejected('edge type')
            edges += len(s.requires) + len(s.after)
            if edges > 16:
                raise Rejected('edge bound')
            for edge in s.requires:
                if not isinstance(edge, tuple) or len(edge) != 2:
                    raise Rejected('edge shape')
                provider, evidence = edge
                if not isinstance(provider, str) or provider not in self.spec:
                    raise Rejected('missing provider')
                p = self.spec[provider]
                allowed = ('completed',) if p.kind == 'oneshot' else ('started', 'notified-ready')
                if not isinstance(evidence, str) or evidence not in allowed or (evidence == 'notified-ready' and p.milestone != evidence):
                    raise Rejected('unsupported evidence')
            if any(not isinstance(p, str) or p not in self.spec for p in s.after):
                raise Rejected('missing ordering reference')
        visiting, visited = set(), set()

        def visit(name):
            if name in visiting:
                raise Rejected('cycle')
            if name in visited:
                return
            visiting.add(name)
            for dep in self.spec[name].after + tuple(p for p, _ in self.spec[name].requires):
                visit(dep)
            visiting.remove(name)
            visited.add(name)
        for name in self.spec:
            visit(name)
        self.epoch, self.revision = epoch, revision
        self.state = {n: State() for n in self.spec}
        self.now = 0
        self.events = 0
        self.closed = False
        self.operations = deque(maxlen=64)
        self.active = None
        self.next_id = 1
        self.records = deque(maxlen=64)
        self.dropped = 0
        self.effects = []

    def _begin(self, count=1):
        if self.events + count > self.MAX_EVENTS:
            raise Rejected('event bound')
        self.events += count
        self.effects = []

    def _record(self, code, name='', text=''):
        if len(self.records) == 64:
            self.dropped += 1
        self.records.append((self.events, self.now, code, name, text[:128]))

    def _effect(self, action, name):
        self.effects.append((action, name, self.state[name].generation))
        self._record(action, name)

    def _names(self, names):
        if not isinstance(names, (tuple, list)) or not 1 <= len(names) <= 8:
            raise Rejected('selection bound')
        if any(not isinstance(n, str) or n not in self.spec for n in names):
            raise Rejected('unknown service')
        return set(names)

    def _closure(self, scope):
        result = set(scope)
        for _ in range(8):
            result.update(p for n in tuple(result) for p, _ in self.spec[n].requires)
        return tuple(sorted(result))

    def _operation(self, kind, scope, budget, restart=None, shutdown=False):
        op = Operation(self.next_id, kind, tuple(sorted(scope)), self.now + budget,
                       restart=restart, shutdown=shutdown)
        self.next_id += 1
        self.operations.append(op)
        self.active = op
        return op

    @staticmethod
    def _budget(budget):
        if type(budget) is not int or not 1 <= budget <= 1000000:
            raise Rejected('operation budget')

    def start(self, names, budget=100):
        scope = self._closure(self._names(names))
        self._budget(budget)
        if self.closed:
            raise Rejected('shutdown admission closed')
        if self.active:
            if self.active.kind == 'start' and self.active.scope == scope and not self.active.cancelling:
                self._begin()
                return self.active.id, []
            raise Rejected('operation conflict')
        if any(self.state[n].cleanup in ('failed', 'unknown') or self.state[n].phase == 'unknown' for n in scope):
            raise Rejected('unresolved ownership')
        self._begin()
        op = self._operation('start', scope, budget)
        for n in scope:
            s = self.state[n]
            s.desired = True
            if not s.owned and s.phase != 'retry' and not s.completed:
                s.phase, s.outcome, s.reason = 'queued', 'pending', ''
                s.retries_used = 0
        self._pump()
        return op.id, list(self.effects)

    def stop(self, names, budget=100, *, shutdown=False, restart=None):
        scope = self._names(names)
        self._budget(budget)
        if type(shutdown) is not bool or (shutdown and scope != set(self.spec)):
            raise Rejected('shutdown scope')
        if restart is not None:
            if restart not in scope or len(scope) != 1 or self.spec[restart].kind != 'daemon' or self.state[restart].phase != 'running':
                raise Rejected('restart requires live daemon')
        # Admission validation is side-effect-free, including retry-pending consumers.
        for n, s in self.state.items():
            if n not in scope and s.desired and any(p in scope for p, _ in self.spec[n].requires):
                raise Rejected('required consumer outside stop scope')
        if self.active and (self.active.kind != 'start' or not set(self.active.scope) <= scope):
            if (self.active.kind == 'stop' and set(self.active.scope) == scope
                    and self.active.restart == restart and self.active.shutdown == shutdown):
                self._begin()
                return self.active.id, []
            raise Rejected('operation conflict')
        self._begin()
        if self.active:
            self.active.status = 'cancelled'
        op = self._operation('stop', scope, budget, restart, shutdown=shutdown)
        if shutdown:
            self.closed = True
        for n in scope:
            self._cancel(n)
        self._pump()
        return op.id, list(self.effects)

    def _cancel(self, n, origin=None):
        s = self.state[n]
        s.desired = s.ready = s.completed = s.retry_allowed = False
        s.due = None
        if not s.owned:
            s.phase, s.outcome = 'absent', 'failure'
        elif s.phase not in ('terminal', 'unknown'):
            s.phase = 'stopping'
            s.deadline = (self.now if origin is None else min(origin, s.deadline if s.deadline is not None else origin)) + self.spec[n].stop

    def _evidence(self, n, kind):
        s = self.state[n]
        if kind == 'completed':
            return s.completed
        return s.desired and s.phase == 'running' and (s.started if kind == 'started' else s.ready)

    def _milestone(self, n):
        return self._evidence(n, self.spec[n].milestone)

    def _launch(self, n, replacement=False):
        s, spec = self.state[n], self.spec[n]
        if replacement:
            s.retries_used += 1
        s.generation += 1
        s.phase, s.owned, s.launch_pending = 'starting', True, True
        s.started = s.ready = s.completed = False
        s.cleanup, s.outcome = 'pending', 'pending'
        s.terminal, s.terminal_detail, s.reason = None, None, ''
        s.reclaim_sent = s.stop_sent = s.retry_allowed = False
        s.due = None
        s.deadline = self.now + spec.startup
        self._effect('launch', n)

    def _failed(self, n, reason, terminal=True, permanent=False, origin=None):
        s, spec = self.state[n], self.spec[n]
        s.reason, s.ready = reason, False
        s.retry_allowed = s.desired and not permanent and spec.kind == 'daemon' and s.retries_used < spec.retries
        s.outcome = 'pending' if s.retry_allowed else 'failure'
        if terminal:
            s.phase, s.terminal, s.launch_pending = 'terminal', reason, False
            s.cleanup = 'pending'  # Fresh terminal evidence permits a new reclaim after force/loss.
            s.deadline = self.now + spec.cleanup
        else:
            s.phase = 'stopping'
            s.deadline = (self.now if origin is None else origin) + spec.stop
        self._record(reason, n)

    def _pump(self):
        # Each pass can advance at least one of at most eight graph nodes.
        for _ in range(9):
            changed = False
            for n in sorted(self.spec):
                s, spec = self.state[n], self.spec[n]
                if s.phase == 'terminal' and s.owned and not s.reclaim_sent:
                    s.reclaim_sent = True
                    self._effect('reclaim', n)
                if s.phase == 'stopping' and s.owned and not s.launch_pending and not s.stop_sent:
                    consumers = [c for c in self.spec if any(p == n for p, _ in self.spec[c].requires)]
                    if any(self.state[c].owned and not self.state[c].desired for c in consumers):
                        continue
                    s.stop_sent = True
                    self._effect('stop', n)
                if (s.phase == 'retry' and s.desired and self.now >= s.due
                        and all(self._evidence(p, k) for p, k in spec.requires)):
                    self._launch(n, replacement=True)
                    changed = True
                if s.phase != 'queued' or not s.desired:
                    continue
                if not self.active or self.active.kind != 'start' or self.active.cancelling:
                    continue
                failed = [p for p, k in spec.requires if not self._evidence(p, k) and self.state[p].outcome == 'failure']
                if failed:
                    s.phase, s.outcome, s.reason = 'absent', 'failure', 'dependency-failed'
                    changed = True
                    continue
                if any(not self._evidence(p, k) for p, k in spec.requires):
                    continue
                if any(p in self.active.scope and self.state[p].outcome == 'pending' for p in spec.after):
                    continue
                self._launch(n)
                changed = True
            if not changed:
                break
        op = self.active
        if not op:
            return
        if any(self.state[n].cleanup in ('failed', 'unknown') for n in op.scope):
            op.status = 'incomplete'
        elif op.kind == 'stop' or op.cancelling:
            if any(self.state[n].owned for n in op.scope if not self.state[n].desired):
                return
            op.status = 'failed' if op.cancelling else 'success'
            if op.restart and op.status == 'success':
                n = op.restart
                op.kind, op.restart = 'start', None
                s = self.state[n]
                s.desired, s.phase, s.outcome, s.retries_used = True, 'queued', 'pending', 0
                op.status = 'pending'
                self._pump()
                return
        elif all(self._milestone(n) for n in op.scope):
            op.status = 'success'
        elif all(self._milestone(n) or (self.state[n].outcome == 'failure' and not self.state[n].owned) for n in op.scope):
            op.status = 'failed'
        else:
            return
        self.active = None

    def _validate_batch(self, events, now):
        """Validate observation data without changing time, ownership or counters."""
        if not isinstance(events, (tuple, list)) or len(events) > 4:
            raise Rejected('batch bound')
        if now is None:
            now = self.now
        if type(now) is not int or not self.now <= now <= 1000000000:
            raise Rejected('clock')
        kinds = {'launched', 'launch_failed', 'denied', 'ready', 'exit', 'fault', 'stopped', 'cleaned', 'cleanup_failed', 'lost', 'log'}
        for e in events:
            if not isinstance(e, tuple) or len(e) != 5:
                raise Rejected('event shape')
            kind, n, generation, epoch, value = e
            if not isinstance(kind, str) or not isinstance(n, str) or kind not in kinds or n not in self.spec or type(generation) is not int or generation < 0:
                raise Rejected('event identity')
            if not isinstance(epoch, str) or len(epoch) > 64:
                raise Rejected('event epoch')
            if type(value) is not int and not (isinstance(value, str) and len(value) <= 128):
                raise Rejected('event value')
            if kind in ('exit', 'stopped') and (type(value) is not int or not 0 <= value <= 255):
                raise Rejected('exit value' if kind == 'exit' else 'stopped value')
        return now

    def batch(self, events=(), *, now=None):
        """One observation cut; completions cannot invent effects that were never requested."""
        now = self._validate_batch(events, now)
        self._begin(max(1, len(events)))
        self.now = now
        op = self.active
        if op and now >= op.deadline and not op.cancelling:
            if op.kind == 'start':
                op.cancelling = True
                for n in op.scope:
                    if not self._milestone(n):
                        self._cancel(n, op.deadline)
            else:
                # Overall stop budget expired: resource ownership is not silently released.
                for n in op.scope:
                    if self.state[n].owned:
                        self.state[n].cleanup = 'unknown'
        for n, s in self.state.items():
            if s.deadline is None or now < s.deadline or not s.owned:
                continue
            if s.phase in ('starting', 'running') and not self._milestone(n):
                self._failed(n, 'startup-timeout', terminal=False, origin=s.deadline)
            if s.phase == 'stopping' and now >= s.deadline:
                # Force is only a request. It still needs terminal and cleanup evidence.
                self._effect('force', n)
                s.phase, s.cleanup = 'unknown', 'unknown'
                s.deadline = None
            elif s.phase == 'terminal' and now >= s.deadline:
                s.cleanup, s.deadline = 'unknown', None
        priority = {'exit': 0, 'fault': 0, 'stopped': 0, 'denied': 0, 'launch_failed': 0, 'lost': 0,
                    'launched': 1, 'cleanup_failed': 2, 'cleaned': 2, 'ready': 3, 'log': 4}
        for kind, n, generation, epoch, value in sorted(events, key=lambda e: (priority[e[0]], e[1], e[0])):
            s = self.state[n]
            if epoch != self.epoch or generation != s.generation:
                self._record('stale', n)
                continue
            if kind == 'log':
                self._record('service-output', n, str(value))
            elif kind == 'launched' and s.launch_pending:
                s.launch_pending = False
                s.started = True
                if s.phase == 'starting':
                    s.phase = 'running'
                    if self.spec[n].milestone == 'started':
                        s.outcome = 'success'
                # Stopping/unknown launches remain owned; never revive admission.
                elif s.phase == 'unknown':
                    self._effect('force', n)
            elif kind in ('exit', 'fault', 'stopped', 'launch_failed', 'denied') and s.owned and s.phase != 'terminal':
                s.terminal_detail = value if kind in ('exit', 'stopped') else None
                if kind == 'exit' and value == 0 and s.reason != 'startup-timeout':
                    s.phase, s.terminal = 'terminal', 'exit-0'
                    s.cleanup = 'pending'
                    s.launch_pending = s.ready = s.retry_allowed = False
                    s.completed = self.spec[n].kind == 'oneshot' and s.desired
                    s.outcome = 'success' if s.completed else 'failure'
                    s.deadline = now + self.spec[n].cleanup
                else:
                    self._failed(n, 'startup-timeout' if s.reason == 'startup-timeout' else kind, permanent=(kind == 'denied'))
            elif kind == 'lost' and s.owned:
                s.phase, s.cleanup, s.ready = 'unknown', 'unknown', False
                s.reason = 'observation-lost'
            elif kind in ('cleaned', 'cleanup_failed') and s.reclaim_sent and s.owned:
                if kind == 'cleanup_failed':
                    s.cleanup, s.reason = 'failed', 'cleanup-failed'
                elif s.cleanup == 'pending':
                    s.owned, s.cleanup, s.deadline = False, 'complete', None
                    if s.retry_allowed and s.desired:
                        s.phase, s.due = 'retry', now + self.spec[n].delay
                    elif not s.desired:
                        s.phase = 'absent'
            elif kind == 'ready' and s.phase == 'running' and s.desired and s.deadline is not None and now < s.deadline and self.spec[n].milestone == 'notified-ready':
                s.ready, s.outcome = True, 'success'
        self._pump()
        return list(self.effects)

    def status(self, name):
        if name not in self.state:
            raise Rejected('unknown service')
        return dict(asdict(self.state[name]), epoch=self.epoch, revision=self.revision,
                    health='unknown', dropped=self.dropped,
                    dependency_loss=tuple(p for p, k in self.spec[name].requires if not self._evidence(p, k)),
                    operation=self.active.id if self.active else None)
