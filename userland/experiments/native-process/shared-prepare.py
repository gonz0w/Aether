#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build broker requester candidates only; never boot or claim native acceptance."""
import argparse,hashlib,json,re,struct,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--sdk',type=Path,required=True)
a=p.parse_args();sdk=a.sdk.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
pin=ROOT/'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
reference=json.loads(pin.read_text());tools=reference['tools']
for name,t in tools.items():need(sha(Path(t['path']))==t['sha256'],'changed tool: '+name)
def inventory():return {str(p.relative_to(sdk)):sha(p) for p in (sdk/'stage').rglob('*') if p.is_file()}
need(not any(p.is_symlink() for p in (sdk/'stage').rglob('*')),'SDK symlink')
need(inventory()==reference['sdk_inputs'],'SDK differs from tested pin')
need(sha(sdk/'evidence.json')==reference['libc_receipt_sha256'],'SDK receipt changed')
inputs=[HERE/'shared-client.c',HERE/'shared-prepare.py',HERE.parent/'native-channel/channel.c',HERE.parent/'native-channel/channel.h']
local={str(p):sha(p) for p in inputs}
work=Path(tempfile.mkdtemp(prefix='shared-clients-',dir=ROOT/'build'));print(work,flush=True)
r={'schema':'aether-userland.shared-clients-build.v1','status':'incomplete','scope':'four source-rebuilt client ELFs; linking and inspection only, no native execution or producer acceptance','sdk_pin':str(pin),'sdk_pin_sha256':sha(pin),'local_sources':local,'commands':[],'artifacts':{}}
def save():(work/'evidence.json').write_text(json.dumps(r,indent=2)+'\n')
def run(label,cmd):
    result=subprocess.run(cmd,capture_output=True,timeout=180)
    (work/(label+'.log')).write_bytes(result.stdout+result.stderr)
    r['commands'].append({'label':label,'argv':cmd,'exit':result.returncode});save()
    need(result.returncode==0,label+' failed');return result.stdout
save()
try:
    cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
    flags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include')]
    r['profile']='shared-files'
    run('channel',cc+flags+['-c',str(inputs[2]),'-o',str(work/'channel.o')])
    lib=sdk/'stage/usr/lib'
    for name,flag in [('parent',[]),('child',['-DCHILD_CLIENT']),('parent-first',['-DPARENT_FIRST']),('child-parent-first',['-DCHILD_CLIENT','-DPARENT_FIRST'])]:
        obj=work/(name+'.o');elf=work/(name+'.elf')
        run(name+'-compile',cc+flags+flag+['-c',str(inputs[0]),'-o',str(obj)])
        run(name+'-link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,-Map,'+str(work/(name+'.map')),str(lib/'crt1.o'),str(lib/'crti.o'),str(obj),str(work/'channel.o'),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
        need(not run(name+'-undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(elf)]).strip(),'undefined symbol')
        need(not re.search(rb'\bsyscall\b',run(name+'-disassembly',[tools['objdump']['path'],'-d',str(elf)])),'Linux syscall instruction')
        run(name+'-headers',[tools['readelf']['path'],'-h','-l',str(elf)])
        data=elf.read_bytes();offset=struct.unpack_from('<Q',data,32)[0];width,count=struct.unpack_from('<HH',data,54)
        headers=[struct.unpack_from('<IIQQQQQQ',data,offset+i*width) for i in range(count)]
        need(data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<HH',data,16)==(2,62),'ELF type/machine')
        need(len(data)<=1048576 and any(h[0]==7 and h[1]==4 and 0<h[6]<=4096 for h in headers),'size/TLS bound')
        need(not any(h[0] in (2,3) or (h[0]==1 and h[1]&3==3) for h in headers),'dynamic/WX segment')
        need(any(h[0]==0x6474e551 and not h[1]&1 for h in headers),'missing NX stack')
        r['artifacts'][name]={'path':str(elf),'sha256':sha(elf),'bytes':len(data)}
    need(inventory()==reference['sdk_inputs'],'SDK changed during build')
    for name,h in local.items():need(sha(Path(name))==h,'source changed during build')
    r['status']='pass';print('PASS: four inspected client ELFs; native execution pending')
finally:save()
