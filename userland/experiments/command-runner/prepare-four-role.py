#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Verify new four-role decoder and link opt-in native parent; no boot claim."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from process import run, clean_env

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='four-role-', dir=ROOT / 'build'))
    report = dict(status='incomplete', work=str(work), commands=[])
    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(str(work), flush=True)
    save()
    try:
        pin = ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
        receipt = json.loads(pin.read_text())
        sdk = ROOT / 'build/native-c-5olokhku'
        actual = {str(p.relative_to(sdk)):sha(p) for p in (sdk / 'stage').rglob('*') if p.is_file()}
        if actual != receipt['sdk_inputs']:
            raise RuntimeError('SDK differs')
        tools = receipt['tools']
        for tool in tools.values():
            if sha(Path(tool['path'])) != tool['sha256']:
                raise RuntimeError('tool drift')
        sources = [HERE / n for n in ['four-role.c','four-role.h','four-role-io.c',
            'four-role-runner.c','four-role-controls.c','FOUR-ROLE-PLAN.md','prepare-four-role.py',
            'native-io.h','runner-parse.c','runner-parse.h','runner-result.c','runner-result.h','process.py']]
        sources += [HERE.parent / 'native-channel/channel.c', HERE.parent / 'native-channel/channel.h', pin]
        report.update(sources={str(p):sha(p) for p in sources}, sdk_inputs=actual, tools=tools)
        def command(label, argv):
            result = run(argv,cwd=work,env=clean_env(work),work=work,label=label,timeout=180)
            report['commands'].append(result.record)
            save()
            if not result.record['complete'] or result.returncode:
                raise RuntimeError(label + ' failed')
            return result
        clang = tools['clang']['path']
        host_sdk = '/Applications/Xcode-beta.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk'
        command('host-build',[clang,'--no-default-config','-isysroot',host_sdk,'-std=c17','-Wall','-Wextra','-Werror',
            '-fsanitize=undefined','-fno-sanitize-recover=all',str(HERE/'four-role.c'),str(HERE/'four-role-controls.c'),'-o',str(work/'controls')])
        command('host-controls',[str(work/'controls')])
        cc=[clang,'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
        flags=['-D_POSIX_C_SOURCE=200809L','-std=c17','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
            '-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include'),'-DNATIVE_RUNNER_STARTUP']
        objs=[]
        for n in ['four-role','four-role-io','four-role-runner','runner-parse','runner-result','channel']:
            source=HERE/(n+'.c') if n!='channel' else HERE.parent/'native-channel/channel.c'
            obj=work/(n+'.o');objs.append(str(obj))
            command(n,cc+flags+(['-D__aether_io=__aether_channel_io'] if n=='channel' else [])+['-c',str(source),'-o',str(obj)])
        lib=sdk/'stage/usr/lib';elf=work/'parent.elf'
        command('link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',str(lib/'crt1.o'),str(lib/'crti.o')]+objs+[str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
        command('headers',[tools['readelf']['path'],'-h','-l',str(elf)])
        undefined=command('undefined',[tools['nm']['path'],'--extern-only','--undefined-only',str(elf)])
        if undefined.stdout.strip():
            raise RuntimeError('undefined externals')
        for p,h in report['sources'].items():
            if sha(Path(p))!=h:raise RuntimeError('source drift')
        report.update(status='pass',elf=dict(path=str(elf),sha256=sha(elf)),native_execution='NOT RUN')
    except (OSError,RuntimeError,ValueError,KeyError) as error:
        report['error']=str(error)
    save()
    print(report['status'],flush=True)
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':
    raise SystemExit(main())
