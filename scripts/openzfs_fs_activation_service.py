# SPDX-License-Identifier: BSD-2-Clause
"""Private root readiness over the existing runtime workload and native ABI."""
from pathlib import Path
from deps import ROOT
from openzfs_fs_runtime_service import owner as runtime_owner


def validate_profile(selected, runtime, writer, service):
    if not isinstance(selected, bool) or (selected and not (runtime and writer and service is not None)):
        raise ValueError('activation requires the explicit runtime service writer')
    if isinstance(service, dict) and service.get('activation', False) is not selected:
        raise ValueError('activation delivery/profile mismatch')


def owner(text, waiting=True):
    selected = runtime_owner(text, waiting)
    for old, new in [('"runtime-service.h"', '"activation-service.h"'),
                     ('aether_fs_runtime_run(', 'aether_fs_activation_run(')]:
        if selected.count(old) != 1:
            raise ValueError('activation owner exact context: ' + old)
        selected = selected.replace(old, new, 1)
    return selected


def driver(text):
    changes = [('use core::arch::asm;', 'use core::arch::asm;\n#[path = "' +
                str(ROOT / 'user/storage/service-runtime/fs-activation-client.rs') + '"]\nmod activation;'),
               ('        if stale == 0 { connection.exercise(); }',
                '        let mut polls = 1000000u32;\n        if stale == 0 { check(activation::ready(owner, &mut polls)); connection.exercise(); }'),
               ('for _ in 0..1000000 {', 'while polls != 0 {\n            polls -= 1;')]
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('activation controller exact context: ' + old)
        text = text.replace(old, new, 1)
    return text


def linker():
    return Path('user/storage/service-runtime/activation-linker.ld')
