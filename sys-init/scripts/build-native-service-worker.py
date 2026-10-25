#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the bounded provider-return worker from explicitly pinned local inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import selectors
import signal
import time

ROOT = Path(__file__).resolve().parents[1]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

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
    def error(self, message): self.exit(64, self.prog + ': ' + message + '\n')

def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--version', action='version', version='sys-init native service worker 1')
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--tools-lock', type=Path, required=True)
    parser.add_argument('--receipt-pin', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    sdk = args.sdk.resolve()
    lock = args.tools_lock.resolve()
    receipt_path = sdk / 'evidence.json'
    receipt = json.loads(receipt_path.read_text())
    if sha(receipt_path) != args.receipt_pin or receipt.get('probe_variant') != 'io':
        raise ValueError('trusted I/O SDK receipt required')
    if sha(lock) != receipt['tools_lock_sha256']:
        raise ValueError('tools lock mismatch')
    if sha(sdk / 'stage/usr/lib/libc.a') != receipt['libc_archive_sha256']:
        raise ValueError('libc archive mismatch')

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.chmod(output, 0o700)
    inputs = output / 'inputs'
    inputs.mkdir()
    shutil.copytree(sdk / 'stage/usr/include', inputs / 'include')
    for name in ('crt1.o', 'crti.o', 'crtn.o', 'libc.a'):
        shutil.copyfile(sdk / 'stage/usr/lib' / name, inputs / name)
    for source, name in ((receipt_path, 'sdk-evidence.json'),
                         (lock, 'tools.lock.json'),
                         (ROOT / 'prototypes/native-supervisor/service_worker.c', 'service_worker.c'),
                         (Path(__file__), 'build-native-service-worker.py')):
        shutil.copyfile(source, inputs / name)

    pins = {str(path.relative_to(output)): sha(path)
            for path in inputs.rglob('*') if path.is_file()}
    tools = json.loads((inputs / 'tools.lock.json').read_text())['tools']
    used = ('clang', 'lld', 'nm', 'readelf', 'objdump')
    for name in used:
        if sha(Path(tools[name]['path'])) != tools[name]['sha256']:
            raise ValueError('tool changed: ' + name)

    empty = output / 'empty-root'
    temp = output / 'tmp'
    empty.mkdir(); temp.mkdir()
    environment = {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LC_ALL': 'C', 'TMPDIR': str(temp)}
    commands = []
    attempts = []
    def run(command, label):
        commands.append(command)
        attempt = dict(command=command, log=label + '.log', result='running',
                       timeout_seconds=180, output_limit_bytes=4 * 1024 * 1024)
        attempts.append(attempt)
        record = output / 'attempts.json'
        record.write_text(json.dumps(attempts, indent=2) + '\n')
        try:
            data = run_tool(command, environment, output / (label + '.log'))
            attempt.update(result='pass', exit=0)
            return data
        except BaseException as error:
            attempt.update(result='fail', error_type=type(error).__name__,
                           error=str(error))
            raise
        finally:
            record.write_text(json.dumps(attempts, indent=2) + '\n')

    cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
          '--sysroot=' + str(empty)]
    common = ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror',
              '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc',
              '-isystem', str(inputs / 'include')]
    worker = output / 'service-worker.elf'
    obj = output / 'service-worker.o'
    run(cc + common + ['-c', str(inputs / 'service_worker.c'), '-o', str(obj)], 'compile')
    lib = inputs
    run(cc + ['-fuse-ld=' + tools['lld']['path'], '-nostdlib', '-static',
              '-Wl,-z,noexecstack', '-Wl,--no-undefined',
              '-Wl,-Map,' + str(output / 'service-worker.map'),
              str(lib / 'crt1.o'), str(lib / 'crti.o'), str(obj),
              str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(worker)], 'link')

    elf = worker.read_bytes()
    if elf[:7] != b'\x7fELF\x02\x01\x01' or struct.unpack_from('<HH', elf, 16) != (2, 62):
        raise ValueError('ELF target mismatch')
    phoff = struct.unpack_from('<Q', elf, 32)[0]
    size, count = struct.unpack_from('<HH', elf, 54)
    headers = [struct.unpack_from('<IIQQQQQQ', elf, phoff + index * size)
               for index in range(count)]
    if any(h[0] in (2, 3) or (h[0] == 1 and h[1] & 3 == 3) for h in headers):
        raise ValueError('unsafe ELF layout')
    if not any(h[0] == 7 for h in headers) or not any(h[0] == 0x6474e551 and not h[1] & 1 for h in headers):
        raise ValueError('TLS/NX missing')
    if run([tools['nm']['path'], '--undefined-only', '--extern-only', str(worker)], 'undefined').strip():
        raise ValueError('undefined external symbol')
    if b'There are no relocations' not in run([tools['readelf']['path'], '-r', str(worker)], 'relocations'):
        raise ValueError('relocations remain')
    run([tools['objdump']['path'], '-d', str(worker)], 'disassembly')
    if any(sha(output / name) != digest for name, digest in pins.items()):
        raise ValueError('captured input changed')
    if any(sha(Path(tools[name]['path'])) != tools[name]['sha256'] for name in used):
        raise ValueError('tool changed during build')

    report = dict(schema='sys-init-native-service-worker-v1', result='pass',
                  sdk_receipt_sha256=args.receipt_pin,
                  tools_lock_sha256=sha(inputs / 'tools.lock.json'),
                  libc_sha256=sha(inputs / 'libc.a'), inputs=pins,
                  inputs_unchanged=True, tools_used=list(used), commands=commands,
                  worker_sha256=sha(worker), program_headers=headers)
    (output / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(worker)

if __name__ == '__main__': main()
