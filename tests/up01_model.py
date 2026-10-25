# SPDX-License-Identifier: BSD-2-Clause
"""UP-01 host-only ownership oracle; not a service, native ABI or POSIX adapter.

Session objects are supplied by a trusted router in this model. No request may
choose a caller. Successful I/O counts model already-validated backend replies.
"""
from copy import deepcopy
from dataclasses import dataclass

READ, WRITE = 1, 2
FD_LIMIT, OPEN_LIMIT, GENERATIONS = 16, 2, 3


class Rejected(Exception):
    pass


@dataclass(frozen=True)
class Session:
    slot: int
    generation: int


@dataclass(frozen=True)
class Reference:
    owner: Session
    fd: int
    generation: int


@dataclass
class OpenFile:
    position: int = 0
    references: int = 1


class Owner:
    def __init__(self):
        self.parent = Session(0, 1)
        self.tables = {self.parent: {}}
        self.child_generation = 0
        self.fd_generations = {}
        self.opens = {}
        self.next_open = 0
        self.closed = []
        self.poisoned = False

    def table(self, caller):
        if caller not in self.tables:
            raise Rejected('stale session')
        return self.tables[caller]

    def resolve(self, caller, ref):
        table = self.table(caller)
        if ref.owner != caller or table.get(ref.fd, (None,))[0] != ref:
            raise Rejected('foreign or stale reference')
        return table[ref.fd]

    def publish(self, caller, fd, object_id, rights):
        table = self.table(caller)
        if fd not in range(FD_LIMIT) or fd in table:
            raise Rejected('descriptor unavailable')
        key = (caller, fd)
        generation = self.fd_generations.get(key, 0) + 1
        if generation > GENERATIONS:
            raise Rejected('descriptor generation exhausted')
        ref = Reference(caller, fd, generation)
        self.fd_generations[key] = generation
        table[fd] = (ref, object_id, rights)
        return ref

    def open(self, caller, fd, rights):
        # Only this model's bootstrap parent has an explicit open namespace.
        self.table(caller)
        if caller != self.parent or self.poisoned or rights not in (READ, WRITE, READ | WRITE):
            raise Rejected('open denied')
        if len(self.opens) == OPEN_LIMIT:
            raise Rejected('open capacity')
        object_id = self.next_open
        ref = self.publish(caller, fd, object_id, rights)
        self.next_open += 1
        self.opens[object_id] = OpenFile()
        return ref

    def admit(self, caller, entries, *, native_accepted=True):
        """Atomically model explicit bootstrap inheritance after native admission.

        entries are (source reference, child FD, restricted rights). A rejected
        launch publishes neither child session nor refs. No fork/exec semantics.
        """
        if caller != self.parent or self.poisoned:
            raise Rejected('admission denied')
        self.table(caller)
        if len(self.tables) != 1 or self.child_generation == GENERATIONS:
            raise Rejected('child capacity')
        if len(entries) > FD_LIMIT:
            raise Rejected('inheritance bound')
        candidate = deepcopy(self)
        child = Session(1, self.child_generation + 1)
        candidate.tables[child] = {}
        refs = []
        for source, fd, rights in entries:
            _, object_id, allowed = candidate.resolve(caller, source)
            if rights not in (READ, WRITE, READ | WRITE) or rights & ~allowed:
                raise Rejected('rights widening')
            refs.append(candidate.publish(child, fd, object_id, rights))
            candidate.opens[object_id].references += 1
        if not native_accepted:
            raise Rejected('native launch rejected')
        candidate.child_generation += 1
        self.__dict__ = candidate.__dict__
        return child, refs

    def complete_io(self, caller, ref, right, count, *, reply='ok'):
        _, object_id, allowed = self.resolve(caller, ref)
        if self.poisoned:
            raise Rejected('connection poisoned')
        if right not in (READ, WRITE) or not allowed & right:
            raise Rejected('access denied')
        if reply == 'unknown':
            self.poisoned = True
            raise Rejected('unobserved mutation; no replay')
        if reply != 'ok' or count not in range(17):
            raise Rejected('invalid completion')
        opened = self.opens[object_id]
        if opened.position + count > 64:
            raise Rejected('position bound')
        before = opened.position
        opened.position += count
        return before

    def close(self, caller, ref):
        _, object_id, _ = self.resolve(caller, ref)
        del self.tables[caller][ref.fd]
        opened = self.opens[object_id]
        opened.references -= 1
        if opened.references == 0:
            # This is one close obligation, not proof of backend completion.
            self.closed.append(object_id)
            del self.opens[object_id]

    def exit(self, caller):
        for ref, _, _ in list(self.table(caller).values()):
            self.close(caller, ref)
        del self.tables[caller]
