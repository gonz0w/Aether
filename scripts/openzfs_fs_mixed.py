# SPDX-License-Identifier: BSD-2-Clause
"""Explicit typed0/16 retirement for the separately approved fixed mixed profile."""
import hashlib

from openzfs_fs_lifetime import RECORD_SHA256
from openzfs_pool import lifetime_write_hooks


def mixed_lifetime_hooks(text):
    selected = lifetime_write_hooks(text)
    old = '#include "pool-lifetime.inc"'
    if selected.count(old) != 1:
        raise ValueError('mixed lifetime hook context')
    return selected.replace(old, '#include "pool-mixed-lifetime.inc"', 1)


def mixed_lifetime_record(text):
    if hashlib.sha256(text.encode()).hexdigest() != RECORD_SHA256:
        raise ValueError('mixed lifetime record source identity')
    changes = (
        ('#include "pool-lifetime.h"', '#include "pool-mixed-lifetime.h"'),
        ('int aether_pool_lifetime_retire(int operation_error, uint64_t target,\n'
         '                                uint64_t staged, uint64_t state)',
         'static int pool_mixed_retire(int operation_error, uint64_t target,\n'
         '                             uint64_t staged, uint64_t state,\n'
         '                             unsigned expected)'),
        ('operation_error || !target || staged != 4096 || state != 2',
         '(expected != 0 && expected != 16) || operation_error || !target || staged != expected || state != 2'),
    )
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('mixed lifetime record context')
        text = text.replace(old, new, 1)
    marker = 'unsigned aether_pool_hooks_check_ordered(void)'
    if text.count(marker) != 1:
        raise ValueError('mixed lifetime typed entry context')
    wrappers = '''/* Typed trusted-owner entries: original unmodified progress, consumed context.
 * No caller-selectable staging class or arbitrary-length exported boundary. */
int aether_pool_namespace0_retire(int error, uint64_t target,
                                 uint64_t staged, uint64_t state)
{
    return pool_mixed_retire(error, target, staged, state, 0);
}
int aether_pool_service16_retire(int error, uint64_t target,
                                uint64_t staged, uint64_t state)
{
    return pool_mixed_retire(error, target, staged, state, 16);
}
'''
    return text.replace(marker, wrappers + marker, 1)
