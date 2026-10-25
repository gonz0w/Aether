# SPDX-License-Identifier: BSD-2-Clause
"""Pure trusted cut model. Synthetic origin/adapter, not native authority or retirement."""
from dataclasses import dataclass

MAX_SERIAL = (1 << 64) - 1


class CutError(ValueError):
    pass


@dataclass(frozen=True, eq=False)
class Source:
    owner: object
    attempt: int
    token: tuple
    worker: int
    phase: int
    content: tuple


@dataclass(frozen=True, eq=False)
class Cut:
    serial: int
    members: tuple


@dataclass(frozen=True)
class Receipt:
    cut: Cut
    journal_serial: int
    before: tuple
    after: tuple


@dataclass
class _Record:
    cut: Cut
    before: tuple
    ticket: object
    state: str = 'reserved'
    receipt: object = None
    returned: object = None


def _state(value):
    return (type(value) is tuple and len(value) == 2
            and all(type(v) is int and 0 <= v <= 3 for v in value))


class CutCoordinator:
    """Owns a synthetic adapter by convention; bypassing this owner is outside scope.

    Adapter: phases (two integers), reserve(20), cancel(ticket), apply(ticket, cut).
    apply returns Receipt only after phase changes and synthetic effect capture.
    A raised reserve must leave adapter state unchanged. Post-reservation failure
    is retained closed, never treated as a retryable ordinary denial.
    """
    def __init__(self, owner, sources, adapter):
        if type(sources) is not tuple or not 1 <= len(sources) <= 6:
            raise CutError('sources')
        keys = set()
        bindings = {}
        for source in sources:
            if (type(source) is not Source or source.owner is not owner
                    or type(source.attempt) is not int or source.attempt not in (0, 1)
                    or type(source.phase) is not int or source.phase not in (1, 2, 3)
                    or type(source.worker) is not int or not 1 <= source.worker <= MAX_SERIAL
                    or type(source.token) is not tuple or len(source.token) != 10
                    or any(type(v) is not int or not 0 <= v <= MAX_SERIAL for v in source.token)
                    or type(source.content) is not tuple or not 1 <= len(source.content) <= 9
                    or any(type(v) is not int or not -(1 << 63) <= v <= MAX_SERIAL for v in source.content)
                    or (source.attempt, source.phase) in keys):
                raise CutError('source')
            binding = (source.token, source.worker)
            if source.attempt in bindings and bindings[source.attempt] != binding:
                raise CutError('inconsistent binding')
            bindings[source.attempt] = binding
            keys.add((source.attempt, source.phase))
        if not _state(adapter.phases) or adapter.phases != (0, 0):
            raise CutError('nonempty adapter')
        self.owner, self.sources, self.adapter = owner, sources, adapter
        self.records = []
        self.next_serial = 1
        self.active = None
        self.closed = False
        self.running = False

    def _owner(self, owner):
        if self.running:
            raise CutError('reentry')
        if owner is not self.owner:
            raise CutError('owner')

    def _invoke(self, method, *args):
        self.running = True
        try:
            return method(*args)
        finally:
            self.running = False

    def _members(self, members):
        if (type(members) is not tuple or not 1 <= len(members) <= 2
                or any(not any(s is known for known in self.sources) for s in members)
                or any(a.attempt >= b.attempt for a, b in zip(members, members[1:]))):
            raise CutError('membership')

    def _phases(self, members):
        if not _state(self.adapter.phases) or any(self.adapter.phases[s.attempt] != s.phase - 1 for s in members):
            raise CutError('phase')

    def _record(self, owner, cut):
        self._owner(owner)
        for record in self.records:
            if cut is record.cut:
                return record
        raise CutError('cut identity')

    def reserve(self, owner, members):
        self._owner(owner)
        if self.closed:
            raise CutError('closed')
        self._members(members)
        for record in self.records:
            if record.state != 'cancelled' and record.cut.members == members:
                return record.cut
        if self.active is not None:
            raise CutError('busy')
        self._phases(members)
        if len(self.records) == 6 or self.next_serial > MAX_SERIAL:
            raise CutError('full')
        cut = Cut(self.next_serial, members)
        before = self.adapter.phases
        record = _Record(cut, before, None)
        self.records.append(record)
        try:
            record.ticket = self._invoke(self.adapter.reserve, 20)
        except BaseException:
            self.records.pop()
            raise
        try:
            self.active = record
            self.next_serial += 1
        except BaseException:
            self.closed = True
            raise
        return cut

    def inspect(self, owner, cut):
        record = self._record(owner, cut)
        return record.state, record.receipt

    def cancel(self, owner, cut):
        record = self._record(owner, cut)
        if self.closed or record is not self.active or record.state != 'reserved':
            raise CutError('not reserved')
        try:
            self._invoke(self.adapter.cancel, record.ticket)
        except BaseException:
            self.closed = True
            record.state = 'unknown'
            raise
        record.state = 'cancelled'
        self.active = None

    def apply(self, owner, cut):
        record = self._record(owner, cut)
        if self.closed:
            raise CutError('closed')
        if record.state == 'applied':
            return record.receipt
        if record is not self.active or record.state != 'reserved':
            raise CutError('not reserved')
        self._members(cut.members)
        self._phases(cut.members)
        if self.adapter.phases != record.before:
            raise CutError('changed application state')
        expected = list(record.before)
        for source in cut.members:
            expected[source.attempt] = source.phase
        record.state = 'applying'
        try:
            receipt = self._invoke(self.adapter.apply, record.ticket, cut)
            record.returned = receipt
            if (type(receipt) is not Receipt or receipt.cut is not cut
                    or type(receipt.journal_serial) is not int
                    or not 1 <= receipt.journal_serial <= MAX_SERIAL
                    or not _state(receipt.before) or not _state(receipt.after)
                    or receipt.before != record.before or receipt.after != tuple(expected)
                    or not _state(self.adapter.phases) or self.adapter.phases != tuple(expected)):
                raise CutError('application not captured')
        except BaseException:
            record.state = 'unknown'
            self.closed = True
            raise
        record.receipt = receipt
        record.state = 'applied'
        self.active = None
        return receipt
