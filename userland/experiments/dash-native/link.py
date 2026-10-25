#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Relink pinned reference dash objects with native SDK; never execute the ELF."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments/command-runner'))
from process import clean_env,run


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    work=Path(tempfile.mkdtemp(prefix='dash-native-link-',dir=ROOT/'build'))
    report=dict(status='incomplete',native_execution='NOT RUN',commands=[],work=str(work))
    def save():
        (work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    def need(ok,text):
        if not ok:raise RuntimeError(text)
    print(work,flush=True);save()
    try:
        evidence=ROOT/'docs/evidence/dash-reference-2026-09-05'
        summary=json.loads((evidence/'summary.json').read_text())
        for n in ('libc-imports.json','build-evidence.json','COPYING.dash'):
            need(sha(evidence/n)==summary['records'][n],'reference receipt drift')
        reference=Path(summary['build'])
        objects=json.loads((evidence/'libc-imports.json').read_text())['objects']
        for n,h in objects.items():need(sha(reference/n)==h,'object drift: '+n)
        snapshot=ROOT/'build/toybox-close-consumer-q91nkwbt'
        intake=json.loads((snapshot/'intake.json').read_text())
        for n,h in intake['pins'].items():need(sha(snapshot/n)==h,'snapshot drift')
        base=snapshot/'producer/docs/evidence/toybox-native-link-2026-09-07'
        receipt=json.loads((base/'results.json').read_text());sdk=base/'inputs/sdk-stage'
        tools=receipt['tools']
        for t in tools.values():need(sha(Path(t['path']))==t['sha256'],'tool drift')
        for n,h in receipt['sdk_inputs'].items():need(sha(sdk/n)==h,'SDK drift')
        report.update(reference_summary_sha256=sha(evidence/'summary.json'),objects=objects,
                      sdk_inputs=receipt['sdk_inputs'],tools=tools,intake_sha256=sha(snapshot/'intake.json'),
                      driver_sha256=sha(Path(__file__)))
        def command(label,argv):
            result=run(argv,cwd=work,env=clean_env(work),work=work,label=label,timeout=180)
            report['commands'].append(result.record);save()
            need(result.record['complete'] and result.returncode==0,label+' failed')
            return result
        (work/'empty-root').mkdir()
        cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(work/'empty-root')]
        adapter=work/'adapter.o'
        command('adapter',cc+['-std=c17','-D_GNU_SOURCE','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                '-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'usr/include'),
                '-c',str(base/'inputs/adapter.c'),'-o',str(adapter)])
        lib=sdk/'usr/lib';elf=work/'dash-native-sdk-link.elf'
        command('link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack',
                '-Wl,--no-undefined','-Wl,-Map,'+str(work/'dash.map'),str(lib/'crt1.o'),str(lib/'crti.o')]
                +[str(reference/n) for n in sorted(objects)]+[str(adapter),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
        undefined=command('undefined',[tools['nm']['path'],'--extern-only','--undefined-only',str(elf)])
        need(not undefined.stdout.strip(),'unresolved externals')
        command('headers',[tools['readelf']['path'],'-h','-l',str(elf)])
        command('disassembly',[tools['objdump']['path'],'-d',str(elf)])
        data=elf.read_bytes();off=struct.unpack_from('<Q',data,32)[0];size,count=struct.unpack_from('<HH',data,54)
        headers=[struct.unpack_from('<IIQQQQQQ',data,off+i*size) for i in range(count)]
        need(data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<HH',data,16)==(2,62),'ELF identity')
        need(not any(h[0] in (2,3) or (h[0]==1 and h[1]&3==3) for h in headers),'dynamic or WX')
        pages={p for h in headers if h[0]==1 for p in range(h[3]//4096,(h[3]+h[6]+4095)//4096)}
        report.update(status='pass',elf_sha256=sha(elf),elf_bytes=len(data),load_pages=len(pages),headers=headers)
    except (OSError,RuntimeError,ValueError,KeyError) as error:report['error']=str(error)
    save();print(report['status'],flush=True)
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':
    raise SystemExit(main())
