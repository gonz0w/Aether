#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the retained-output experiment against an explicitly trusted I/O SDK."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import selectors
import signal
import time

ROOT = Path(__file__).resolve().parents[1]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run_tool(command, environment, log_path, timeout=180, limit=4 * 1024 * 1024):
    """Bound trusted tool output and duration; retain the accepted output prefix."""
    end = time.monotonic() + timeout
    with log_path.open('wb') as log:
        child = subprocess.Popen(command, env=environment, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(child.stdout, selectors.EVENT_READ)
                total = 0
                while selector.get_map():
                    remaining = end - time.monotonic()
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(command, timeout)
                    for key, _ in selector.select(remaining):
                        block = os.read(key.fd, min(65536, limit - total + 1))
                        if not block:
                            selector.unregister(key.fileobj)
                            continue
                        log.write(block[:limit - total])
                        total += len(block)
                        if total > limit:
                            raise ValueError('tool output limit exceeded')
                code = child.wait(timeout=max(0, end - time.monotonic()))
                if code:
                    raise subprocess.CalledProcessError(code, command)
        except BaseException:
            # Only this invocation's owned group; tools must not detach.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
            raise
        finally:
            child.stdout.close()
    return log_path.read_bytes()

class Parser(argparse.ArgumentParser):
    def error(self, message): self.exit(64, self.prog+': '+message+'\n')

def main():
    p = Parser(description=__doc__)
    p.add_argument('--version', action='version', version='sys-init native I/O worker 1')
    for name in ('sdk', 'tools-lock', 'output'): p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--receipt-pin', required=True)
    profile = p.add_mutually_exclusive_group()
    profile.add_argument('--peer', action='store_true', help='build known-live-peer readiness worker')
    profile.add_argument('--authority', action='store_true', help='build caller-local readiness authority worker')
    profile.add_argument('--readiness', action='store_true', help='build controlled readiness/terminal ordering worker')
    a = p.parse_args()
    sdk = a.sdk.resolve()
    receipt = json.loads((sdk/'evidence.json').read_text())
    if sha(sdk/'evidence.json') != a.receipt_pin or receipt['probe_variant'] != 'io':
        raise ValueError('trusted I/O SDK receipt required')
    if sha(a.tools_lock) != receipt['tools_lock_sha256']:
        raise ValueError('SDK tools lock mismatch')
    if sha(sdk/'stage/usr/lib/libc.a') != receipt['libc_archive_sha256']:
        raise ValueError('SDK libc archive mismatch')
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False); os.chmod(out, 0o700)
    worker_name = 'io_peer_worker.c' if a.peer else 'io_worker.c'
    inputs = out/'inputs'; inputs.mkdir()
    shutil.copytree(sdk/'stage/usr/include', inputs/'include')
    for name in ('crt1.o', 'crti.o', 'crtn.o', 'libc.a'):
        shutil.copyfile(sdk/'stage/usr/lib'/name, inputs/name)
    for source, name in ((sdk/'native_io.o','native_io.o'), (sdk/'evidence.json','sdk-evidence.json'),
                         (a.tools_lock,'tools.lock.json'),
                         (ROOT/'prototypes/native-supervisor'/worker_name,worker_name),
                         (Path(__file__),'build-native-io-worker.py')):
        shutil.copyfile(source, inputs/name)
    if (sha(inputs/'sdk-evidence.json') != a.receipt_pin
            or sha(inputs/'tools.lock.json') != receipt['tools_lock_sha256']
            or sha(inputs/'libc.a') != receipt['libc_archive_sha256']):
        raise ValueError('SDK changed during capture')
    pins = {str(f.relative_to(out)):sha(f) for f in inputs.rglob('*') if f.is_file()}
    tools = json.loads((inputs/'tools.lock.json').read_text())['tools']
    used = ('clang','lld','nm','readelf','objdump')
    for key in used:
        if sha(Path(tools[key]['path'])) != tools[key]['sha256']: raise ValueError('tool changed: '+key)
    empty = out/'empty-root'; empty.mkdir(); tmp = out/'tmp'; tmp.mkdir()
    env = dict(PATH='/usr/bin:/bin:/usr/sbin:/sbin', LC_ALL='C', TMPDIR=str(tmp))
    commands = []
    attempts = []
    def run(command, name):
        commands.append(command)
        attempt = dict(name=name, command=command, result='running',
                       timeout_seconds=180, output_limit=4 * 1024 * 1024)
        attempts.append(attempt)
        def save():
            (out/'tool-attempts.json').write_text(json.dumps(attempts, indent=2)+'\n')
        save()
        try:
            raw = run_tool(command, env, out/(name+'.log'))
            attempt.update(result='pass', returncode=0)
            return raw
        except subprocess.TimeoutExpired:
            attempt['result'] = 'timeout'
            raise
        except subprocess.CalledProcessError as error:
            attempt.update(result='fail', returncode=error.returncode)
            raise
        except ValueError as error:
            attempt.update(result='output-limit', error=str(error))
            raise
        except OSError as error:
            attempt.update(result='infra-error', error=str(error))
            raise
        except BaseException:
            attempt['result'] = 'interrupted'
            raise
        finally:
            save()
    cc = [tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(empty)]
    run(cc+(['-DREADINESS_ORDERING','-DREADINESS_AUTHORITY'] if a.authority else ['-DREADINESS_ORDERING'] if a.readiness else [])+['-std=c11','-O2','-Wall','-Wextra','-Werror','-nostdinc','-isystem',str(inputs/'include'),
            '-fno-builtin','-fstack-protector-strong','-c',str(inputs/worker_name),'-o',str(out/'worker.o')], 'compile')
    run(cc+['-fuse-ld='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',
            '-Wl,-Map,'+str(out/'worker.map')]+[str(inputs/n) for n in ('crt1.o','crti.o')]+
            [str(out/'worker.o')]+[str(inputs/n) for n in ('native_io.o','libc.a','crtn.o')]+
            ['-o',str(out/'worker.elf')], 'link')
    elf = (out/'worker.elf').read_bytes()
    if elf[:7] != b'\x7fELF\x02\x01\x01' or struct.unpack_from('<HH',elf,16) != (2,62): raise ValueError('ELF target')
    phoff = struct.unpack_from('<Q',elf,32)[0]
    size, count = struct.unpack_from('<HH',elf,54)
    headers = [struct.unpack_from('<IIQQQQQQ',elf,phoff+i*size) for i in range(count)]
    if any(h[0] in (2,3) or (h[0]==1 and h[1]&3==3) for h in headers): raise ValueError('unsafe ELF')
    if not any(h[0]==7 for h in headers) or not any(h[0]==0x6474e551 and not h[1]&1 for h in headers): raise ValueError('TLS/NX missing')
    if run([tools['nm']['path'],'--undefined-only','--extern-only',str(out/'worker.elf')],'undefined').strip(): raise ValueError('undefined external')
    rel = run([tools['readelf']['path'],'-r',str(out/'worker.elf')],'relocations')
    if b'There are no relocations' not in rel: raise ValueError('relocations')
    run([tools['objdump']['path'],'-d',str(out/'worker.elf')],'disassembly')
    raw = (sdk/'native-c.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest() != receipt['envelope_sha256']: raise ValueError('SDK envelope changed')
    (out/'native-c.bin').write_bytes(b'AENATC01'+raw[8:40]+elf)
    if any(sha(out/n)!=h for n,h in pins.items()) or any(sha(Path(tools[k]['path']))!=tools[k]['sha256'] for k in used): raise ValueError('input changed')
    result = dict(probe_variant='io-peer' if a.peer else 'io-authority' if a.authority else 'io-readiness' if a.readiness else 'io-retained', scope='Local trusted SDK link; executable pins do not authenticate SDK provenance or host shared libraries. Bootstrap bytes are development-only.',
                  sdk_receipt_sha256=a.receipt_pin, inputs=pins, commands=commands, tools_used=list(used),
                  envelope_sha256=sha(out/'native-c.bin'), artifacts=[dict(name='startup',sha256=sha(out/'worker.elf'))],
                  program_headers=headers, inputs_unchanged=True)
    (out/'evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    print(out/'native-c.bin')

if __name__ == '__main__': main()
