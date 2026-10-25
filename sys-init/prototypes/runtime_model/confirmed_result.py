# SPDX-License-Identifier: BSD-2-Clause
"""Pure trusted ABI-6 return qualification; never execution or reconciliation."""
from dataclasses import dataclass
import re

from .effect_ledger import InvalidEffect

PROFILE = 'aether-init-abi6'
CALLS = {'launch': 0x23001, 'stop': 0x20007, 'reclaim': 0x20002}
ERRORS = {0x23001: (-13, -22, -16, -28, -14), 0x20007: (-13, -9),
          0x20002: (-13, -9, -16)}
FACTS = {0x23001: 'instance-admitted', 0x20007: 'target-terminal',
         0x20002: 'target-reclaimed'}


def _issued(journal, token):
    if journal.closed or journal.observe(token) != 'issued':
        raise InvalidEffect('not an open issued obligation')


@dataclass(frozen=True)
class BoundCall:
    journal: object
    owner: object
    producer: str
    token: tuple
    syscall: int
    target: int

    def __post_init__(self):
        if self.owner is None:
            raise InvalidEffect('owner')
        if type(self.producer) is not str or re.fullmatch(r'[0-9a-f]{64}', self.producer) is None:
            raise InvalidEffect('producer')
        _issued(self.journal, self.token)
        kind = self.token[7]
        if type(self.syscall) is not int or kind not in CALLS or self.syscall != CALLS[kind]:
            raise InvalidEffect('unsupported operation')
        if type(self.target) is not int or self.target not in {
                0xb0000000 | (generation << 8) | slot
                for generation in (1, 2, 3) for slot in (1, 2)}:
            raise InvalidEffect('native target')

    def qualify(self, reply, *, owner):
        if owner is not self.owner:
            raise InvalidEffect('owner mismatch')
        _issued(self.journal, self.token)
        fields = {'schema', 'profile', 'producer', 'token', 'syscall', 'target', 'result'}
        if type(reply) is not dict or set(reply) != fields:
            raise InvalidEffect('reply fields')
        for field, expected in (('schema', 'abi6-return-v1'), ('profile', PROFILE),
                                ('producer', self.producer)):
            if type(reply[field]) is not str or reply[field] != expected:
                raise InvalidEffect('reply identity')
        if type(reply['token']) is not tuple or reply['token'] != self.token:
            raise InvalidEffect('token mismatch')
        # Validate exact token scalar types as well as equality (bool is not an ID).
        self.journal.observe(reply['token'])
        for field, expected in (('syscall', self.syscall), ('target', self.target)):
            if type(reply[field]) is not int or reply[field] != expected:
                raise InvalidEffect('call mismatch')
        result = reply['result']
        if type(result) is not int or not -(1 << 63) <= result < (1 << 63):
            raise InvalidEffect('return bound')
        success = self.target if self.syscall == 0x23001 else 0
        if result == success:
            outcome, fact = 'executed', FACTS[self.syscall]
        elif result in ERRORS[self.syscall]:
            outcome, fact = 'rejected-before-effects', 'none'
        else:
            raise InvalidEffect('unsupported return')
        return ('confirmed-result-v1', outcome, self.syscall, result, self.target, fact)
