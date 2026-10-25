#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Optional Python host transport for the six-artifact supervised experiment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat
import struct
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
# Fixed, explicitly selected owner profiles; not an extensible plugin registry.
PROFILES = {
    'supervised': (b'AENSUP01', None),
    'memory': (b'AENFD001', {'native-memory': True, 'smp': False}),
    'launch': (b'AENEX001', {'native-memory': False, 'smp': False}),
    'channel': (b'AENCH001', {'native-memory': False, 'smp': False}),
    'connections': (b'AENMX001', {'native-memory': False, 'smp': False, 'native-coexist-small-pool': False}),
    'connections-small-pool': (b'AENMX001', {'native-memory': False, 'smp': False, 'native-coexist-small-pool': True}),
    'coexist': (b'AENCO001', {'native-memory': False, 'smp': False, 'native-coexist-small-pool': False}),
    'coexist-small-pool': (b'AENCO001', {'native-memory': False, 'smp': False, 'native-coexist-small-pool': True}),
    'process': (b'AENFS001', {'native-memory': False, 'smp': False}),
    'files': (b'AENFS001', {'native-memory': False, 'smp': False}),
    'files-writable': (b'AENFS001', {'native-memory': False, 'smp': False}),
    'files-writable-memory': (b'AENFS001', {'native-memory': True, 'smp': False}),
}
NAMES=('aether','protection.bin','display.bin','lifecycle.bin','smp-supervisor.bin','native-c.bin')
def check(ok,reason):
    if not ok: raise ValueError(reason)
def pin(value): check(isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value),'invalid SHA256 pin')
def regular(path):
    mode=path.lstat();check(stat.S_ISREG(mode.st_mode) and mode.st_nlink==1,'regular unlinked file required')
def digest(path):
    regular(path);return hashlib.sha256(path.read_bytes()).hexdigest()
def elf_header(raw):
    check(len(raw)>=64 and raw[:7]==b'\x7fELF\x02\x01\x01' and struct.unpack_from('<HH',raw,16)==(2,62),'native ELF header')
def envelope(path, magic=b'AENSUP01'):
    regular(path)
    dual=magic in (b'AENEX001',b'AENCH001',b'AENFS001',b'AENCO001')
    triple=magic==b'AENMX001'
    maximum=3*1048576+8192+80 if triple else 2*1048576+4096+56 if dual else 1048576+4096+48
    check(48<path.stat().st_size<=maximum,'envelope bounds')
    raw=path.read_bytes()
    if triple:
        check(len(raw)>=80,'three-image header')
        actual,first,second,third,supervisor,reserved1,reserved2=struct.unpack_from('<8s6I',raw)
        check(actual==magic and reserved1==reserved2==0 and all(64<=n<=1048576 for n in (first,second,third)) and 1<=supervisor<=8192 and len(raw)==80+first+second+third+supervisor,'three-image envelope')
        offset=80
        for size in (first,second,third):elf_header(raw[offset:offset+size]);offset+=size
    elif dual:
        check(len(raw)>=56,'dual-image header')
        actual,first,second,supervisor,reserved=struct.unpack_from('<8sIIII',raw)
        check(actual==magic and reserved==0 and 64<=first<=1048576 and 64<=second<=1048576 and 1<=supervisor<=4096 and len(raw)==56+first+second+supervisor,'dual-image envelope')
        elf_header(raw[56:56+first]);elf_header(raw[56+first:56+first+second])
    else:
        actual,csize,ssize=struct.unpack_from('<8sII',raw)
        check(actual==magic and 64<=csize<=1048576 and 0<ssize<=4096 and len(raw)==48+csize+ssize,'supervised envelope')
        elf_header(raw[48:48+csize])
def verify(bundle,receipt_pin):
    pin(receipt_pin);check(bundle.is_dir() and not bundle.is_symlink(),'bundle directory')
    check({p.name for p in bundle.iterdir()}=={'receipt.json',*NAMES},'bundle inventory')
    check(digest(bundle/'receipt.json')==receipt_pin,'receipt pin mismatch')
    record=json.loads((bundle/'receipt.json').read_text())
    check(isinstance(record,dict),'receipt object')
    profiles=[name for name in PROFILES if record.get('format')=='aether-'+name+'-transport-v1']
    check(len(profiles)==1,'receipt format');profile=profiles[0]
    magic,required=PROFILES[profile]
    fields={'format','base_receipt_sha256','files','authenticity','activation'}
    if required is not None:fields.add('required_kernel_options')
    if profile in ('files-writable','files-writable-memory'):fields.add('service_mode')
    check(set(record)==fields,'receipt fields')
    if profile in ('files-writable','files-writable-memory'):check(record['service_mode']=='volatile-scratch-v1','service mode')
    if required is not None:
        options=record['required_kernel_options']
        check(isinstance(options,dict) and set(options)==set(required) and all(options[k] is v for k,v in required.items()),'kernel options')
    check(record['authenticity']=='not-proven' and record['activation']=='unsupported','receipt profile')
    check(isinstance(record['files'],dict),'receipt files object')
    pin(record['base_receipt_sha256']);check(set(record['files'])==set(NAMES),'receipt inventory')
    for name in NAMES:check(digest(bundle/name)==record['files'][name],'payload pin mismatch')
    envelope(bundle/'native-c.bin',magic)
    return record

def stage(root,base_pin,native,native_pin,*,memory=False,profile=None):
    profile=profile or ('memory' if memory else 'supervised')
    check(profile in PROFILES and (not memory or profile=='memory'),'stage profile')
    magic,required=PROFILES[profile]
    pin(base_pin);pin(native_pin)
    subprocess.run(['sh',str(HERE/'aether-boot-v2.sh'),'verify',str(root),base_pin],check=True)
    check(digest(native)==native_pin,'native pin mismatch');envelope(native,magic)
    dest=root/('aether-'+profile+'-v1');check(not dest.exists() and not dest.is_symlink(),'bundle already exists')
    pending=Path(tempfile.mkdtemp(prefix='.supervised-',dir=root))
    try:
        for name in NAMES:
            src=native if name=='native-c.bin' else root/'aether-boot-v2/boot'/name
            regular(src);shutil.copyfile(src,pending/name)
        # Revalidate the source and the copies against the externally pinned base receipt.
        subprocess.run(['sh',str(HERE/'aether-boot-v2.sh'),'verify',str(root),base_pin],check=True)
        original={line.split('=',1)[0]:line.split('=',1)[1] for line in (root/'aether-boot-v2/receipt.kv').read_text().splitlines()}
        hashes={n:digest(pending/n) for n in NAMES}
        for name in NAMES:check(hashes[name]==(native_pin if name=='native-c.bin' else original[name+'_sha256']),'copied input changed')
        record=dict(format='aether-'+profile+'-transport-v1',base_receipt_sha256=base_pin,files=hashes,authenticity='not-proven',activation='unsupported')
        if required is not None:record['required_kernel_options']=dict(required)
        if profile in ('files-writable','files-writable-memory'):record['service_mode']='volatile-scratch-v1'
        (pending/'receipt.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
        receipt=digest(pending/'receipt.json');verify(pending,receipt);pending.rename(dest)
        return receipt
    finally:
        if pending.exists():shutil.rmtree(pending)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
    s=sub.add_parser('stage',aliases=['stage-memory','stage-launch','stage-channel','stage-files','stage-files-writable','stage-files-writable-memory','stage-process','stage-coexist','stage-coexist-small-pool','stage-connections','stage-connections-small-pool']);s.add_argument('root',type=Path);s.add_argument('base_pin');s.add_argument('native',type=Path);s.add_argument('native_pin')
    v=sub.add_parser('verify');v.add_argument('bundle',type=Path);v.add_argument('receipt_pin');a=p.parse_args()
    try:
        if a.operation.startswith('stage'):print(stage(a.root,a.base_pin,a.native,a.native_pin,profile=a.operation.removeprefix('stage-') if a.operation!='stage' else 'supervised'))
        else:verify(a.bundle,a.receipt_pin);print('aether-supervised-verified')
    except (OSError,ValueError,subprocess.CalledProcessError) as error:p.exit(1,'aether-supervised-error: '+str(error)+'\n')
