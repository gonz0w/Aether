# SPDX-License-Identifier: BSD-2-Clause
"""Private delegated-directory owner and independently checked bounded hierarchy."""
import hashlib
from deps import ROOT
from openzfs_fs_names_service import FIRST, SECOND, owner as names_owner
from openzfs_fs_namespace import PROBE

ENGINE_FILES = {'user/storage/openzfs-volume/zpl-directories.c': 'c46d737d6344e883e9e5121bbba4305a26c41d09aa24d2d278a1d7f9157165d8', 'user/storage/openzfs-volume/zpl-directories.h': '5f624fd6655c1be938dbabe2a7e54410b8dca93b3d642b9ed6fede74a41ba552'}


def validate_profile(selected, names, reader, service):
    if not isinstance(selected, bool) or not isinstance(names, bool) or not isinstance(reader, bool) or (selected and not names):
        raise ValueError('directories require names selection')
    if isinstance(service, dict) and service.get('directories', False) is not selected:
        raise ValueError('directories delivery/profile mismatch')
    if selected and ((reader and service is not None) or (not reader and service is None)):
        raise ValueError('directories require selected writer or independent reader')


def owner(text, waiting=True):
    selected = names_owner(text, waiting)
    for old, new in [('"names-service.h"', '"directories-service.h"'),
                     ('aether_fs_names_run(', 'aether_fs_directories_run(')]:
        if selected.count(old) != 1:
            raise ValueError('directories owner context: ' + old)
        selected = selected.replace(old, new, 1)
    return selected


def probe(text, reader=False, empty=False, case='normal', storage_lifetime=False):
    from storage_lifetime import validate
    validate(storage_lifetime, True, reader, case)
    if hashlib.sha256(text.encode()).hexdigest() != PROBE:
        raise ValueError('directories original probe identity')
    if not isinstance(reader, bool) or not isinstance(empty, bool) or case not in ('normal','lost-reply','partial-request','close-failure') or (not reader and empty != (case in ('lost-reply','partial-request'))):
        raise ValueError('directories exact role/outcome required')
    # Preserve the qualified original full-file hash/read/EOF implementation.
    prefix = text[:text.index('static int namespace_absent(')]
    prefix = prefix.replace('#include "zpl-mutate.c"', '#include "zpl-directories.c"')
    return (('#define AETHER_DIRECTORY_LAST 1791290160\n' if storage_lifetime else '') + '#define AETHER_FS_SERVICE_LIFETIMES 1\n#define AETHER_FS_SERVICE_CASE ' +
            str(0 if reader else ('normal','lost-reply','partial-request','close-failure').index(case)) +
            '\n#define MNS_READER ' + str(int(reader)) + '\n#define DIR_EMPTY ' + str(int(empty)) +
            '\n#define DIR_FIRST "' + FIRST + '"\n#define DIR_SECOND "' + SECOND + '"\n' + prefix +
            (ROOT/'user/storage/openzfs-volume/directory-oracle.inc').read_text())
