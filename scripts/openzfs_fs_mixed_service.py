# SPDX-License-Identifier: BSD-2-Clause
"""Exact mixed-service intake and bounded original namespace oracle adaptation."""
import hashlib
import json
import os
from pathlib import Path

from deps import ROOT
from openzfs_fs_bridge import C_INPUTS, UTC_SHA256
from openzfs_fs_namespace import MUTATOR, OWNER, probe as namespace_probe, sha

DIRECTORIES_SEAL = 'e01e269a91a96bac3a428fb1197dc862032838dcb94602c0c6042ef9e8e5c4fa'
NAMES_SEAL = '99cb2e36ad13e108761ca513aed53cc4681ce9b8033aa4663c1faf0aec091e78'
ACTIVATION_SEAL = '8b87bad17f02fafc41982c94d0f4f8120b89a15df9c632ba763d76236d755fb3'
SEAL = 'e07aeeff522094d4994c90ec63ea68c6fb2ca2f6163d994c6e8a54a3f43181a9'
RUNTIME_SEAL = '34cde46be6e486d220f3b4e5da018232ab0ccba608e08e481abb3d83dc22aeba'
BULK_SEAL = 'b09125af433e5431a5bd7e40f0266cb1e242a043722cfad43abbd03dce2e4e91'
WAIT_SEAL = 'd37083501c788adad04e8dc4da936656180dd4d2108a97f411bbd35cf876395b'
RETIREMENT_FILES = {
    'user/storage/openzfs-volume/pool-lifetime.inc': '0e0aab003a0b7acc919eccafd70c810e06f1d07615081644c65c9cded9d31fc8',
}


def intake(delivery, waiting=False, bulk=False, runtime=False, activation=False, names=False, directories=False):
    if not isinstance(directories,bool) or (directories and not names):raise ValueError('directories require names')
    if not isinstance(names,bool) or (names and not activation):raise ValueError('names require activation')
    if not isinstance(activation,bool) or (activation and not runtime):raise ValueError('activation requires runtime selection')
    if not isinstance(runtime,bool) or (runtime and not bulk):raise ValueError('runtime requires explicit bulk selection')
    if not isinstance(bulk,bool) or (bulk and not waiting):raise ValueError('bulk requires explicit mixed wait selection')
    if not isinstance(waiting,bool):raise ValueError('mixed wait selector must be boolean')
    expected_seal=DIRECTORIES_SEAL if directories else NAMES_SEAL if names else ACTIVATION_SEAL if activation else RUNTIME_SEAL if runtime else BULK_SEAL if bulk else WAIT_SEAL if waiting else SEAL
    root=Path(os.path.abspath(delivery))
    if root.resolve()!=root or not root.is_dir():raise ValueError('mixed service requires real delivery')
    seal=root/'SHA256SUMS'
    if seal.is_symlink() or sha(seal)!=expected_seal:raise ValueError('mixed service manifest identity')
    inputs={str(seal):expected_seal};members=set()
    for line in seal.read_text().splitlines():
        digest,name=line.split(maxsplit=1);path=root/name
        if Path(name).is_absolute() or '..' in Path(name).parts or name in members:raise ValueError('mixed service member path')
        if path.resolve()!=path or not path.is_file() or sha(path)!=digest:raise ValueError('mixed service member identity: '+name)
        members.add(name);inputs[str(path)]=digest
    if len(members)!=(67 if directories else 61 if names else 58 if activation else 55 if runtime else 49 if bulk else 43 if waiting else 41) or any(p.is_symlink() for p in root.rglob('*')) or {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}!=members|{'SHA256SUMS'}:
        raise ValueError('mixed service member closure')
    recorded=json.loads((root/'inputs.json').read_text())
    expected={n:h for n,h in C_INPUTS.items() if n.endswith(('zpl-read.c','zpl-read.h','zpl-write.c','zpl-write.h'))}|MUTATOR
    if recorded['producer_namespace_files']!=expected:raise ValueError('mixed service original C closure')
    retirement=recorded['producer_mixed_retirement_files']
    if set(retirement)!={'user/storage/openzfs-volume/pool-lifetime.inc','user/storage/openzfs-volume/pool-vdev-hooks.inc','user/storage/openzfs-volume/pool-mixed-lifetime.h','scripts/openzfs_fs_mixed.py'} or any(retirement[n]!=h for n,h in RETIREMENT_FILES.items()):
        raise ValueError('mixed service typed retirement closure')
    if bulk:
        extra=recorded.get('producer_bulk_retirement_files',{})
        if set(extra)!={'scripts/openzfs_fs_bulk.py','user/storage/openzfs-volume/pool-bulk-lifetime.h'}:raise ValueError('bulk typed retirement closure')
        retirement=retirement|extra
    if directories:
        from openzfs_fs_directories_service import ENGINE_FILES
        if recorded.get('producer_directory_files')!=ENGINE_FILES:
            raise ValueError('directories engine contract closure')
        retirement=retirement|ENGINE_FILES
    for name,digest in (C_INPUTS|MUTATOR|retirement).items():
        if sha(ROOT/name)!=digest:raise ValueError('mixed service C/retirement drift: '+name)
        inputs[str(ROOT/name)]=digest
    for name in ('zpl-read.h','zpl-write.h','zpl-mutate.h','pool-mixed-lifetime.h', *(['pool-bulk-lifetime.h'] if bulk else []), *(['zpl-directories.h'] if directories else [])):
        if sha(root/'ffi'/name)!=sha(ROOT/'user/storage/openzfs-volume'/name):raise ValueError('mixed service packaged ABI mismatch')
    if sha(root/'ffi/utc.h')!=UTC_SHA256 or sha(ROOT/'.deps/native-utc-v3/runtime/utc.h')!=UTC_SHA256:raise ValueError('mixed service UTC drift')
    inputs[str(ROOT/'.deps/native-utc-v3/runtime/utc.h')]=UTC_SHA256
    for name in ('user/storage/namespace-channel.rs','user/storage/namespace-wire.rs'):
        digest=recorded['producer_files'][name]
        if sha(ROOT/name)!=digest:raise ValueError('mixed service channel drift')
        inputs[str(ROOT/name)]=digest
    tool_inputs={v['path']:v['sha256'] for v in recorded['tools'].values()}
    for name,digest in (tool_inputs|recorded['rust_native_libraries']|recorded['clang_resource_headers']).items():
        if sha(name)!=digest:raise ValueError('mixed service tool/dependency drift: '+name)
        inputs[name]=digest
    if waiting:
        if (recorded.get('native_profile')!='AENBD004/ABI26' or recorded.get('entry')!=('aether_fs_directories_run' if directories else 'aether_fs_names_run' if names else 'aether_fs_activation_run' if activation else 'aether_fs_runtime_run' if runtime else 'aether_fs_bulk_run' if bulk else 'aether_fs_mixed_wait_run') or
                recorded.get('selected_cfgs')!=['fs_namespace','fs_lifetimes','fs_mixed','fs_wait']+(['fs_bulk'] if bulk else [])+(['fs_runtime'] if runtime else [])+(['fs_activation'] if activation else [])+(['fs_names'] if names else [])+(['fs_directories'] if directories else []) or
                set(recorded.get('producer_wait_files',{}))!={'user/storage/namespace-channel.rs','user/storage/namespace-wait-channel.rs'}):
            raise ValueError('mixed wait exact ABI/provisioning closure')
        for name,digest in recorded['producer_wait_files'].items():
            if sha(ROOT/name)!=digest:raise ValueError('mixed wait adapter drift: '+name)
            inputs[str(ROOT/name)]=digest
    if activation and (recorded.get('supervisor_code_limit')!=8192 or recorded.get('readiness')!='validated-root-utc-before-greeting/live-retained-instance'):
        raise ValueError('activation readiness/code contract')
    if runtime and (recorded.get('lifetime')!='checked-monotonic' or recorded.get('native_workload')!={'mutations':9,'requests':96}):raise ValueError('runtime lifetime/workload contract')
    if bulk and (recorded.get('protocol')!=('AFSRPC06' if directories else 'AFSRPC05' if names else 'AFSRPC04') or recorded.get('maximum_payload')!=4096):raise ValueError('bulk exact data framing contract')
    if names and (recorded.get('maximum_component')!=255 or recorded.get('maximum_rename')!=510):raise ValueError('names exact capacity contract')
    if directories and recorded.get('directory_operations')!={'mkdir':10,'rmdir':11,'mkdir_mode':'0700','parent':'delegated handle/expected generation'}:raise ValueError('directories exact operations')
    for name in (*(['openzfs_fs_directories_service.py'] if directories else []), 'openzfs_fs_names_service.py','openzfs_fs_activation_service.py','openzfs_fs_runtime_service.py','openzfs_fs_mixed_service.py','openzfs_fs_bulk_service.py','openzfs_fs_bulk.py','openzfs_fs_namespace.py','openzfs_fs_service.py','openzfs_volume.py','openzfs_elapsed.py','service_runtime_smoke.py'):
        path=ROOT/'scripts'/name;inputs[str(path)]=sha(path)
    return {'mixed':True,'manifest_sha256':expected_seal,'root':str(root),'inputs':inputs,
            **({'waiting':True} if waiting else {}),**({'bulk':True} if bulk else {}),**({'runtime':True} if runtime else {}),**({'activation':True} if activation else {}),**({'names':True} if names else {}),**({'directories':True} if directories else {}),'object':str(root/('objects/filesystem-directories.o' if directories else 'objects/filesystem-names.o' if names else 'objects/filesystem-activation.o' if activation else 'objects/filesystem-runtime.o' if runtime else 'objects/filesystem-bulk.o' if bulk else 'objects/filesystem-mixed-wait.o' if waiting else 'objects/filesystem-mixed.o')),'header_directory':str(root/'source'),
            'scope':'checked lifetime; fixed9/96 native candidate; not operational service acceptance' if runtime else 'fixed8 mixed producer candidate; not operational service acceptance'}


def owner(text,waiting=False):
    if hashlib.sha256(text.encode()).hexdigest()!=OWNER:raise ValueError('mixed service original owner drift')
    changes=(('#include "native-service.h"','#include "mixed-service.h"'),
        ('#define FS_REQUESTS 39','#define FS_REQUESTS 29'),
        ('#define FS_PARTIAL_REQUESTS 38','#define FS_PARTIAL_REQUESTS 28'),
        ('aether_fs_service_run(spa, dataset, sizeof(dataset) - 1, reader,\n                                      writer, 7, &completion)',
         'aether_fs_mixed_run(spa, dataset, sizeof(dataset) - 1, reader,\n                                writer, 15, 1000, 1000, &completion)'))
    for old,new in changes:
        if text.count(old)!=1:raise ValueError('mixed service owner call/count context')
        text=text.replace(old,new,1)
    if waiting:
        text=text.replace('"mixed-service.h"','"mixed-wait-service.h"').replace('aether_fs_mixed_run(','aether_fs_mixed_wait_run(')
    return text


def probe(text,reader=False,empty=False,case='normal'):
    if not isinstance(reader,bool) or not isinstance(empty,bool) or case not in ('normal','lost-reply','partial-request','close-failure') or (not reader and empty!=(case=='lost-reply')):
        raise ValueError('mixed service requires exact fixed role/outcome')
    # Same original probe and independent full-file/namespace/allocation/ACL
    # bodies. Adapt only final16-byte content/timestamps and service invocation.
    selected=namespace_probe(text,'create',reader,'normal' if case=='partial-request' else case)
    selected=selected.replace('"new"','"p"').replace('"renamed"','"q"').replace('"fs-namespace-owner.inc"','"fs-mixed-owner.inc"')
    changes=(
        ('file.size || file.mode != 0100600','file.size != (FS_MIXED_EMPTY ? 0 : 16) || file.mode != 0100600'),
        ('if (size || project || acl_count != 3 ||','if (size != (FS_MIXED_EMPTY ? 0 : 16) || project || acl_count != 3 ||'),
        ('mtime[1] >= 1000000000 || memcmp(mtime, crtime, 16) ||\n        memcmp(mtime, atime, 16)',
         'mtime[1] >= 1000000000 || crtime[0] < 1791290040 || crtime[0] > 1791290100 ||\n        crtime[1] >= 1000000000 || mtime[0] < crtime[0] ||\n        (mtime[0] == crtime[0] && mtime[1] < crtime[1]) || memcmp(crtime, atime, 16)'),
        ('''            unsigned char byte = 0;
            size_t got = 99;
            error = aether_zpl_read(view, file.object, file.generation, 0,
                                    &byte, 1, &got);
            if (!error && got)
                error = EIO;''',
         '''            unsigned char data[16] = {0}, byte = 0;
            size_t got = 99;
            if (!FS_MIXED_EMPTY) {
                error = aether_zpl_read(view,file.object,file.generation,0,data,sizeof(data),&got);
                if (!error && got != sizeof(data)) error = EIO;
                for (unsigned i=0; !error && i<sizeof(data); ++i)
                    if (data[i] != 71+i) error = EIO;
            }
            if (!error) error = aether_zpl_read(view,file.object,file.generation,
                FS_MIXED_EMPTY ? 0 : 16,&byte,1,&got);
            if (!error && got) error = EIO;'''),
    )
    for old,new in changes:
        if selected.count(old)!=1:raise ValueError('mixed service independent oracle context')
        selected=selected.replace(old,new,1)
    if not reader:
        old='!result.txg || result.bytes_staged ||'
        if selected.count(old)!=1:raise ValueError('mixed service original progress context')
        selected=selected.replace(old,'!result.txg || result.bytes_staged != (FS_MIXED_EMPTY ? 0 : 16) ||',1)
    if case=='partial-request' and not reader:selected='#define AETHER_FS_SERVICE_CASE 2\n'+selected
    return '#define AETHER_FS_SERVICE_LIFETIMES 1\n#define FS_MIXED_EMPTY '+str(int(empty))+'\n'+selected


def partial_origins(mapping,symbols=None,close_failure=False,waiting=False,bulk=False,runtime=False,activation=False,names=False,directories=False):
    required={n:'zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close','aether_zpl_root',
        'aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
    required.update(aether_fs_mixed_run='filesystem-mixed.o',aether_pool_namespace0_retire='vdev-selected.o',aether_pool_service16_retire='vdev-selected.o')
    if waiting:
        required.pop('aether_fs_mixed_run')
        required['aether_fs_mixed_wait_run']='filesystem-mixed-wait.o'
    if bulk:
        if not waiting:raise ValueError('bulk origins require waiting')
        required.pop('aether_fs_mixed_wait_run')
        required.pop('aether_pool_service16_retire')
        required.update(aether_fs_bulk_run='filesystem-bulk.o',aether_pool_service_bytes_retire='vdev-selected.o')
    if runtime:
        if not bulk:raise ValueError('runtime origins require bulk')
        required.pop('aether_fs_bulk_run');required['aether_fs_runtime_run']='filesystem-runtime.o'
    if activation:
        if not runtime:raise ValueError('activation origins require runtime')
        required.pop('aether_fs_runtime_run');required['aether_fs_activation_run']='filesystem-activation.o'
    if names:
        if not activation:raise ValueError('names origins require activation')
        required.pop('aether_fs_activation_run');required['aether_fs_names_run']='filesystem-names.o'
    if directories:
        if not names:raise ValueError('directory origins require names')
        required.pop('aether_fs_names_run');required['aether_fs_directories_run']='filesystem-directories.o'
        required.update({n:'zpl-mutation.o' for n in ('aether_zpl_directory','aether_zpl_mkdir','aether_zpl_rmdir')})
    if close_failure:required['__wrap_aether_zpl_close']='zpl-mutation.o'
    found={};current=None;sections=[]
    for line in mapping.splitlines():
        fields=line.split()
        if len(fields)<5:continue
        last=fields[-1]
        if ':(' in last:
            current=last.split(':(',1)[0]
            if last.endswith(':(.text.aether_zpl_close)'):sections.append((current,fields[0],fields[2]))
        elif last in required:
            if last in found or current is None or not current.endswith('/'+required[last]):raise ValueError('mixed service partial origin: '+last)
            found[last]=current
    if close_failure and 'aether_zpl_close' not in found:
        definitions=[line.split() for line in (symbols or '').splitlines() if line.split()[-1:]==['aether_zpl_close']]
        if len(sections)!=1 or len(definitions)!=1 or len(definitions[0])!=4 or definitions[0][2]!='T' or not sections[0][0].endswith('/zpl-mutation.o') or int(definitions[0][0],16)!=int(sections[0][1],16) or int(definitions[0][1],16)!=int(sections[0][2],16) or int(definitions[0][1],16)==0:
            raise ValueError('mixed service original consuming close')
        found['aether_zpl_close']=sections[0][0]
    if set(found)!=set(required):raise ValueError('mixed service missing original symbols')
    return found


def validate_profile(selected,writer,reader,service,lifetimes=False,namespace=None,empty=False,case='normal'):
    if not isinstance(selected,bool) or not isinstance(empty,bool):raise ValueError('mixed service selectors must be boolean')
    if not selected:
        if empty or (isinstance(service,dict) and service.get('mixed',False)):
            raise ValueError('mixed service delivery/empty selection requires explicit profile')
        return
    if lifetimes or namespace is not None or case not in ('normal','lost-reply','partial-request','close-failure') or not ((writer and not reader and service is not None and not empty) or (reader and not writer and service is None and case=='normal')):
        raise ValueError('mixed service requires exact exclusive writer/recovery profile')
    if isinstance(service,dict) and service.get('mixed',False) is not True:raise ValueError('mixed service delivery/profile mismatch')
