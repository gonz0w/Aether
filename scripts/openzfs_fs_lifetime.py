# SPDX-License-Identifier: BSD-2-Clause
"""Unselected fixed16-byte service retirement preparation; no native launcher."""
import hashlib

from openzfs_pool import lifetime_write_hooks

RECORD_SHA256 = '0e0aab003a0b7acc919eccafd70c810e06f1d07615081644c65c9cded9d31fc8'


def service_lifetime_hooks(text):
    selected = lifetime_write_hooks(text)
    old = '#include "pool-lifetime.inc"'
    if selected.count(old) != 1:
        raise ValueError('service lifetime hook context')
    return selected.replace(old, '#include "pool-service-lifetime.inc"', 1)


def service_lifetime_record(text):
    # Preserve the reviewed epoch/borrow/error implementation. This is a fixed
    # private profile, never a client-selectable or arbitrary-size retirement API.
    if hashlib.sha256(text.encode()).hexdigest() != RECORD_SHA256:
        raise ValueError('service lifetime record source identity')
    changes = (
        ('#include "pool-lifetime.h"', '#include "pool-service-lifetime.h"'),
        ('int aether_pool_lifetime_retire(', 'int aether_pool_service16_retire('),
        ('staged != 4096', 'staged != 16'),
    )
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('service lifetime record context')
        text = text.replace(old, new, 1)
    return text
