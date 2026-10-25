# SPDX-License-Identifier: BSD-2-Clause
"""Separate checked lifetime; fixed nine-mutation/96-request native experiment."""
from openzfs_fs_bulk_service import owner as bulk_owner, probe as bulk_probe


def validate_profile(selected, bulk, service):
    if not isinstance(selected,bool) or (selected and not bulk):
        raise ValueError('runtime requires explicit bulk selection')
    if isinstance(service,dict) and service.get('runtime',False) is not selected:
        raise ValueError('runtime delivery/profile mismatch')


def owner(text, waiting=True):
    selected=bulk_owner(text,waiting)
    changes=(('"bulk-service.h"','"runtime-service.h"'),
        ('aether_fs_bulk_run(','aether_fs_runtime_run('),
        ('#define FS_REQUESTS 30','#define FS_REQUESTS 96'),
        ('#define FS_CLOSES 9','#define FS_CLOSES 10'),
        ('if (fs_injected < 8)','if (fs_injected < 9)'),
        ('Eight success-only cycle closes','Nine success-only cycle closes'))
    for old,new in changes:
        if selected.count(old)!=1:raise ValueError('runtime owner exact context: '+old)
        selected=selected.replace(old,new,1)
    return selected


def probe(text, reader=False, empty=False, case='normal'):
    selected=bulk_probe(text,reader,empty,case)
    changes=(('file.size != (FS_MIXED_EMPTY ? 0 : 4096)','file.size != (FS_MIXED_EMPTY ? 0 : 8192)'),
        ('if (size != (FS_MIXED_EMPTY ? 0 : 4096)','if (size != (FS_MIXED_EMPTY ? 0 : 8192)'),
        ('FS_MIXED_EMPTY ? 0 : 4096,&byte','FS_MIXED_EMPTY ? 0 : 8192,&byte'),
        ('offset<4096','offset<8192'),
        ('(unsigned char)(71+offset+i)','(unsigned char)((offset<4096 ? 71 : 91)+offset+i)'))
    for old,new in changes:
        if selected.count(old)!=1:raise ValueError('runtime independent oracle context: '+old)
        selected=selected.replace(old,new,1)
    # Last staged request remains4096 even though final file size is8192.
    return selected
