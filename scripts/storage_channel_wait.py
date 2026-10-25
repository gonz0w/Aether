# SPDX-License-Identifier: BSD-2-Clause
"""Private primary-only storage wait admission and native trace oracle."""
import re


def validate(selected, ipc, namespace, writer=False, reader=False, service=None, mutation=None, mixed=False):
    if not isinstance(selected, bool):
        raise ValueError('namespace wait selector must be boolean')
    if isinstance(service,dict) and service.get('waiting',False) and not selected:
        raise ValueError('mixed wait service requires explicit wait profile')
    if selected and service is not None:
        if not (ipc and namespace and writer and not reader and mixed and mutation is None):
            raise ValueError('mixed wait requires exclusive mixed service writer')
        if isinstance(service,dict) and service.get('waiting',False) is not True:
            raise ValueError('mixed wait service delivery/profile mismatch')
        return
    if selected and (not ipc or not namespace or writer or reader or service is not None or mutation is not None):
        raise ValueError('namespace wait requires exclusive read-only namespace IPC')


def trace(text):
    pending = set()
    counts = {'park': 0, 'wake': 0}
    owners = set()
    for line in text.splitlines():
        if not line.startswith('NATIVE STORAGE WAIT '):
            continue
        match = re.fullmatch(r'NATIVE STORAGE WAIT slot=(\d+) generation=(\d+) phase=(park|wake) status=(-?\d+)', line)
        if match is None:
            raise ValueError('storage wait trace syntax')
        owner, generation, phase, status = match.groups()
        key = int(owner), int(generation)
        if not ((key[0] == 0 and 1 <= key[1] <= 3) or key == (2, 0)) or int(status) != 0:
            raise ValueError('storage wait trace identity or outcome')
        if phase == 'park':
            if key in pending:
                raise ValueError('storage wait duplicate registration')
            pending.add(key)
            owners.add(key[0])
        else:
            if key not in pending:
                raise ValueError('storage wait foreign/duplicate completion')
            pending.remove(key)
        counts[phase] += 1
    if pending or owners != {0, 2} or counts['park'] != counts['wake']:
        raise ValueError('storage wait missing registration/completion')
    return {'primary_channel_waits': counts['park'], 'primary_channel_wakes': counts['wake'],
            'wait_scope': 'primary-only readiness hints; helper scheduling qualified separately'}
