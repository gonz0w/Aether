# SPDX-License-Identifier: BSD-2-Clause
"""Separate approved bounded data retirement; old0/16 selection stays exact."""
from openzfs_fs_mixed import mixed_lifetime_hooks, mixed_lifetime_record


def bulk_lifetime_hooks(text):
    return mixed_lifetime_hooks(text).replace('"pool-mixed-lifetime.inc"', '"pool-bulk-lifetime.inc"', 1)


def bulk_lifetime_record(text):
    selected = mixed_lifetime_record(text)
    changes = (
        ('"pool-mixed-lifetime.h"', '"pool-bulk-lifetime.h"'),
        ('pool_mixed_retire', 'pool_bulk_retire'),
        ('(expected != 0 && expected != 16)', '(expected > 4096)'),
        ('''int aether_pool_service16_retire(int error, uint64_t target,
                                uint64_t staged, uint64_t state)
{
    return pool_bulk_retire(error, target, staged, state, 16);
}''', '''int aether_pool_service_bytes_retire(int error, uint64_t target,
                                    uint64_t staged, uint64_t state,
                                    uint64_t expected)
{
    if (!expected || expected > 4096)
        return EINVAL;
    return pool_bulk_retire(error, target, staged, state, (unsigned)expected);
}'''),
        ('No caller-selectable staging class or arbitrary-length exported boundary.',
         'Write length is bound to the completed request, in1..4096; namespace uses0.'),
    )
    for old, new in changes:
        if old not in selected:
            raise ValueError('bulk retirement context changed: ' + old)
        selected = selected.replace(old, new)
    return selected
