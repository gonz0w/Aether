# SPDX-License-Identifier: BSD-2-Clause
"""Build the scoped block conformance client with explicitly pinned SDK inputs."""
import hashlib
import json
import os
from pathlib import Path
import struct


def build(sdk_path, tools_lock, out, mode, command, regions=False, rust_worker=False):
    sdk = Path(sdk_path).resolve()
    lock = Path(tools_lock).resolve()
    tools = json.loads(lock.read_text())['tools']
    receipt = json.loads((sdk / 'evidence.json').read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    lib = sdk / 'stage/usr/lib'
    if sha(lib / 'libc.a') != receipt['libc_archive_sha256'] or not receipt.get('libc_patches'):
        raise RuntimeError('strict SDK mismatch')
    for name in ['clang', 'lld']:
        if sha(Path(tools[name]['path']).resolve()) != tools[name]['sha256']:
            raise RuntimeError('tool pin mismatch: ' + name)
    out.mkdir(exist_ok=False)
    cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl', '--sysroot=' + str(sdk / 'empty-root')]
    for name, source in [('worker', 'user/native-block/rust-start.c' if rust_worker else 'user/native-block/region-worker.c' if regions else 'user/native-block/worker.c'), ('adapter', 'user/native-memory/adapter.c')]:
        command(cc + ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding',
                      '-fno-builtin', '-fstack-protector-strong', '-nostdinc', '-isystem', str(sdk / 'stage/usr/include'),
                      '-DBLOCK_' + mode.upper(), '-c', source, '-o', str(out / (name + '.o'))], mode + '-' + name)
    rust_library = []
    if rust_worker:
        rust_library = [str(out / 'libblock.a')]
        command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
                 '--crate-type=staticlib', '-C', 'opt-level=s', '-C', 'panic=abort',
                 '-C', 'relocation-model=static', '--cfg', 'block_' + mode,
                 'user/native-block/rust-worker.rs', '-o', rust_library[0]], mode + '-rust-worker')
    command(cc + ['-fuse-ld=' + tools['lld']['path'], '-nostdlib', '-static', '-Wl,-z,noexecstack', '-Wl,--no-undefined',
                  str(lib / 'crt1.o'), str(lib / 'crti.o'), str(out / 'worker.o'), str(out / 'adapter.o'),
                  *rust_library, str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(out / 'worker.elf')], mode + '-link')
    command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=s',
             '-C', 'lto=fat', '-C', 'codegen-units=1', '-C', 'panic=abort', '-C', 'relocation-model=static',
             '-C', 'link-arg=-Tuser/native-launch/linker.ld', '-C', 'link-arg=--oformat=binary',
             '--cfg', 'block_' + mode, 'user/native-block/region-owner.rs' if regions else 'user/native-block/owner.rs', '-o', str(out / 'owner.raw')], mode + '-owner')
    worker, owner = (out / 'worker.elf').read_bytes(), (out / 'owner.raw').read_bytes()
    envelope = out / 'native-block.bin'
    envelope.write_bytes(struct.pack('<8sII', b'AENBD002' if regions else b'AENBD001', len(worker), len(owner)) + os.urandom(32) + worker + owner)
    (out / 'sdk.json').write_text(json.dumps({'sdk_receipt': sha(sdk / 'evidence.json'), 'libc': sha(lib / 'libc.a'),
                                           'tools_lock': sha(lock), 'tools': tools}, indent=2) + '\n')
    return envelope
