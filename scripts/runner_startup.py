# SPDX-License-Identifier: BSD-2-Clause
"""Encode the opt-in AERUN001 bootstrap carrier (not native kernel argv)."""
import struct


def encode(arguments):
    if not 1 <= len(arguments) <= 6:
        raise ValueError('runner startup requires 1..6 arguments')
    values = [value.encode('utf-8') for value in arguments]
    if values[0] != b'aether-run':
        raise ValueError('runner argv[0] must be aether-run')
    if any(len(value) > 31 or b'\0' in value for value in values):
        raise ValueError('runner argument exceeds byte bound or contains NUL')
    return (struct.pack('<8sI20x', b'AERUN001', len(values))
            + b''.join(value.ljust(32, b'\0') for value in values)
            + bytes((6 - len(values)) * 32))
