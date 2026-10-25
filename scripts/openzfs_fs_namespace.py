# SPDX-License-Identifier: BSD-2-Clause
"""Exact one-attempt AFSRPC02 intake and original namespace oracle adaptation."""
import hashlib
import json
import os
from pathlib import Path

from deps import ROOT
from openzfs_fs_bridge import C_INPUTS, UTC_SHA256

SEAL = '9d504603cac15be48e6a45dd266baae27c23b1851477a5fa1d27e44a4e0dc7d3'
OPERATIONS = ('create', 'rename', 'remove')
PROBE = '08e3bd215f6830d25aff61c27e19c23d7fecf9dde34de25388cae51217152bc8'
OWNER = '7c67d4295e5fa8ba6c84597e3550c16eaba0efbd193215365ca77030151763bb'
MUTATOR = {
    'user/storage/openzfs-volume/zpl-mutate.c': 'ca1b55b5674573745f5cbac38dac5acf0d3609bb649ab34680b2e721852655c5',
    'user/storage/openzfs-volume/zpl-mutate.h': '5c0536af864584f002528b643c29dccc6f7180ad16feeac58814e8c273b58cbe',
}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def intake(delivery):
    root = Path(os.path.abspath(delivery))
    if root.resolve() != root or not root.is_dir():
        raise ValueError('namespace service requires real delivery')
    seal = root / 'SHA256SUMS'
    if seal.is_symlink() or sha(seal) != SEAL:
        raise ValueError('namespace service manifest identity')
    inputs = {str(seal): SEAL}
    names = set()
    for line in seal.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = root / name
        if Path(name).is_absolute() or '..' in Path(name).parts or name in names:
            raise ValueError('namespace service member path')
        if path.resolve() != path or not path.is_file() or sha(path) != digest:
            raise ValueError('namespace service member identity: '+name)
        names.add(name)
        inputs[str(path)] = digest
    if (len(names) != 36 or any(p.is_symlink() for p in root.rglob('*')) or
            {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} != names | {'SHA256SUMS'}):
        raise ValueError('namespace service member closure')
    recorded = json.loads((root/'inputs.json').read_text())
    expected = {n:h for n,h in C_INPUTS.items() if n.endswith(('zpl-read.c','zpl-read.h','zpl-write.c','zpl-write.h'))} | MUTATOR
    if recorded['producer_namespace_files'] != expected:
        raise ValueError('namespace service original C contract closure')
    for name,digest in (C_INPUTS | MUTATOR).items():
        if sha(ROOT/name) != digest:
            raise ValueError('namespace service original C drift: '+name)
        inputs[str(ROOT/name)] = digest
    for name in ('zpl-read.h','zpl-write.h','zpl-mutate.h'):
        if sha(root/'ffi'/name) != sha(ROOT/'user/storage/openzfs-volume'/name):
            raise ValueError('namespace service packaged ABI mismatch')
    if sha(root/'ffi/utc.h') != UTC_SHA256 or sha(ROOT/'.deps/native-utc-v3/runtime/utc.h') != UTC_SHA256:
        raise ValueError('namespace service UTC drift')
    inputs[str(ROOT/'.deps/native-utc-v3/runtime/utc.h')] = UTC_SHA256
    for name in ('user/storage/namespace-channel.rs','user/storage/namespace-wire.rs'):
        digest = recorded['producer_files'][name]
        if sha(ROOT/name) != digest:
            raise ValueError('namespace service channel drift')
        inputs[str(ROOT/name)] = digest
    tool_inputs = {v['path']:v['sha256'] for v in recorded['tools'].values()}
    for name,digest in (tool_inputs | recorded['rust_native_libraries'] | recorded['clang_resource_headers']).items():
        if sha(name) != digest:
            raise ValueError('namespace service tool/dependency drift: '+name)
        inputs[name] = digest
    for name in ('openzfs_fs_namespace.py','openzfs_fs_service.py','openzfs_volume.py','openzfs_elapsed.py','service_runtime_smoke.py'):
        path=ROOT/'scripts'/name
        inputs[str(path)]=sha(path)
    return {'namespace': True, 'manifest_sha256': SEAL, 'root': str(root), 'inputs': inputs,
            'object':str(root/'objects/filesystem-namespace.o'), 'header_directory':str(root/'source'),
            'scope':'one-attempt namespace producer candidate, not operational service acceptance'}


def owner(text):
    if hashlib.sha256(text.encode()).hexdigest() != OWNER:
        raise ValueError('namespace service original owner drift')
    text=text.replace('#include "native-service.h"','#include "namespace-service.h"',1)
    text=text.replace('#define FS_REQUESTS 11','#define FS_REQUESTS 5',1)
    text=text.replace('aether_fs_service_run(spa, dataset, sizeof(dataset) - 1, reader,\n                                      writer, 7, &completion)',
                      'aether_fs_namespace_run(spa, dataset, sizeof(dataset) - 1, reader,\n                                      writer, 9, 1000, 1000, &completion)',1)
    if 'aether_fs_namespace_run(' not in text:
        raise ValueError('namespace service entry call context')
    return text.replace('completion.stop ||','completion.stop != 6 ||')


def validate_profile(operation, mutation, writer, reader, service, lifetimes=False, case='normal'):
    if operation is None:
        if isinstance(service,dict) and service.get('namespace',False):
            raise ValueError('filesystem service namespace requires explicit matching operation')
        return
    if (not isinstance(operation,str) or operation not in OPERATIONS or operation != mutation
            or lifetimes or case not in ('normal','lost-reply','close-failure')
            or not ((writer and not reader and service is not None)
                    or (reader and not writer and service is None))):
        raise ValueError('filesystem service namespace requires exact one-attempt role/profile')
    if isinstance(service,dict) and service.get('namespace',False) is not True:
        raise ValueError('filesystem service namespace delivery/profile mismatch')


def probe(text, operation, reader=False, case='normal'):
    if operation not in OPERATIONS or not isinstance(reader,bool):
        raise ValueError('namespace service requires exact operation/role')
    if hashlib.sha256(text.encode()).hexdigest() != PROBE:
        raise ValueError('namespace service original namespace probe drift')
    text=text.replace('"aether-created"','"new"').replace('"aether-renamed"','"renamed"')
    if not reader:
        old='#if MNS_KIND == 1\n    aether_zpl_node created = {0};\n#endif\n'
        if text.count(old)!=1:raise ValueError('namespace service created context')
        text=text.replace(old,'',1)
        begin=text.index('#if MNS_KIND == 1\n        error =')
        end=text.index('        *assigned = result.txg;',begin)
        text=text[:begin]+'''        aether_zpl_close(&view);
        error = aether_fs_owner_probe(spa, &result);
'''+text[end:]
        text=text.replace('extern void aether_engine_utc_phase(unsigned char);',
                          'extern void aether_engine_utc_phase(unsigned char);\n#include "fs-namespace-owner.inc"',1)
    if case not in ('normal','lost-reply','close-failure'):
        raise ValueError('namespace service requires fixed interruption case')
    number={'normal':0,'lost-reply':1,'close-failure':3}[case]
    return (('#define AETHER_FS_SERVICE_CASE '+str(number)+'\n' if number and not reader else '')+
            '#define MNS_KIND '+str(OPERATIONS.index(operation)+1)+'\n#define MNS_READER '+str(int(reader))+'\n'+text)


def partial_origins(mapping, symbols=None, close_failure=False):
    required={n:'zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close',
        'aether_zpl_root','aether_zpl_lookup','aether_zpl_read','aether_zpl_write',
        'aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
    required['aether_fs_namespace_run']='filesystem-namespace.o'
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
            if last in found or current is None or not current.endswith('/'+required[last]):
                raise ValueError('namespace service partial origin: '+last)
            found[last]=current
    if close_failure and 'aether_zpl_close' not in found:
        definitions=[line.split() for line in (symbols or '').splitlines() if line.split()[-1:]==['aether_zpl_close']]
        if (len(sections)!=1 or len(definitions)!=1 or len(definitions[0])!=4 or
            definitions[0][2]!='T' or not sections[0][0].endswith('/zpl-mutation.o') or
            int(definitions[0][0],16)!=int(sections[0][1],16) or
            int(definitions[0][1],16)!=int(sections[0][2],16) or int(definitions[0][1],16)==0):
            raise ValueError('namespace service original consuming close')
        found['aether_zpl_close']=sections[0][0]
    if set(found)!=set(required):raise ValueError('namespace service missing original symbols')
    return found
