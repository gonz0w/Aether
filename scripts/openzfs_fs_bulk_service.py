# SPDX-License-Identifier: BSD-2-Clause
"""Fixed AF04 data workload; independent original-file and fresh-media oracle."""
from openzfs_fs_mixed_service import owner as mixed_owner, probe as mixed_probe


def validate_profile(selected, mixed, waiting, writer, reader, service):
    if not isinstance(selected,bool):raise ValueError('bulk selector must be boolean')
    if not selected:
        if isinstance(service,dict) and service.get('bulk',False):raise ValueError('bulk delivery requires explicit profile')
        return
    if not mixed or writer == reader or (writer and not waiting) or (reader and (waiting or service is not None)):
        raise ValueError('bulk requires exact mixed waiting writer or independent recovery')
    if isinstance(service,dict) and service.get('bulk',False) is not True:raise ValueError('bulk delivery/profile mismatch')


def owner(text, waiting=True):
    if waiting is not True:raise ValueError('bulk owner requires primary waits')
    selected=mixed_owner(text,True)
    changes=(('"mixed-wait-service.h"','"bulk-service.h"'),
        ('aether_fs_mixed_wait_run(','aether_fs_bulk_run('),
        ('#define FS_REQUESTS 29','#define FS_REQUESTS 30'),
        ('#define FS_PARTIAL_REQUESTS 28','#define FS_PARTIAL_REQUESTS 7'),
        ('completion.requests != 5','completion.requests != 6'))
    for old,new in changes:
        if selected.count(old)!=1:raise ValueError('bulk owner exact context: '+old)
        selected=selected.replace(old,new,1)
    return selected


def probe(text, reader=False, empty=False, case='normal'):
    if not isinstance(reader,bool) or not isinstance(empty,bool) or case not in ('normal','lost-reply','partial-request','close-failure') or (not reader and empty!=(case in ('lost-reply','partial-request'))):
        raise ValueError('bulk requires exact fixed role/outcome')
    # The partial write body never reaches the engine: only its preceding create
    # is durable. Reuse the independent empty-file oracle without changing it.
    selected=mixed_probe(text,reader,empty,'lost-reply' if not reader and case=='partial-request' else case)
    if not reader and case=='partial-request':
        if selected.count('#define AETHER_FS_SERVICE_CASE 1')!=1:raise ValueError('bulk partial case context')
        selected=selected.replace('#define AETHER_FS_SERVICE_CASE 1','#define AETHER_FS_SERVICE_CASE 2',1)
    changes=(('FS_MIXED_EMPTY ? 0 : 16','FS_MIXED_EMPTY ? 0 : 4096'),
        ('''                error = aether_zpl_read(view,file.object,file.generation,0,data,sizeof(data),&got);
                if (!error && got != sizeof(data)) error = EIO;
                for (unsigned i=0; !error && i<sizeof(data); ++i)
                    if (data[i] != 71+i) error = EIO;''',
         '''                for (unsigned offset=0; !error && offset<4096; offset+=sizeof(data)) {
                    error = aether_zpl_read(view,file.object,file.generation,offset,data,sizeof(data),&got);
                    if (!error && got != sizeof(data)) error = EIO;
                    for (unsigned i=0; !error && i<sizeof(data); ++i)
                        if (data[i] != (unsigned char)(71+offset+i)) error = EIO;
                }'''))
    for old,new in changes:
        if old not in selected:raise ValueError('bulk independent oracle context: '+old)
        selected=selected.replace(old,new)
    return selected
