# SPDX-License-Identifier: BSD-2-Clause
"""Fixed musl1.2.6 comparison selection for the owner-size experiment only."""
import hashlib
import io
from pathlib import Path
import tarfile

ARCHIVE_SHA = 'd585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a'
MEMBERS = {
    'src/string/memcmp.c': '826b1b5e84d3c0fb68be827c051f6dc0d67da17ee3a444e94be0e5360586916f',
    'COPYRIGHT': 'b870108ec5e7790e9f9919064f1b9421d62d5f9b0e6c230c6adf7ea2da62e97b',
}
HEADERS = {
    'string.h': '714a7724b0051be159c0fb7ec7f97c4ff9dd16c22e1be926c957f747cc6a8906',
    'features.h': '6d228e77b88b69f70f9157548b6ec673ffc6b998ce6035fbbee0caddb8442903',
    'bits/alltypes.h': 'a8990c268ef62ec2e6963e757a0efad856ed4fd3611f6c28e7df17962697cc4c',
}


def verified(data, digest, name):
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('owner comparison input changed: ' + name)
    return data


def prepare(system, work, run, tools):
    sdk = system / '.deps/native-current/sdk'
    archive = sdk / 'musl-1.2.6.tar.gz'
    archive_bytes = verified(archive.read_bytes(), ARCHIVE_SHA, str(archive))
    # Read only two exact regular members; never extract archive paths or links.
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as source:
        members = {}
        for name, digest in MEMBERS.items():
            info = source.getmember('musl-1.2.6/' + name)
            if not info.isfile():
                raise ValueError('owner comparison member is not regular: ' + name)
            members[name] = verified(source.extractfile(info).read(), digest, name)
    headers = {name: verified((sdk / 'stage/usr/include' / name).read_bytes(), digest, name)
               for name, digest in HEADERS.items()}
    directory = work / 'musl-compare'
    directory.mkdir()
    (directory / 'memcmp.c').write_bytes(members['src/string/memcmp.c'])
    (directory / 'COPYRIGHT').write_bytes(members['COPYRIGHT'])
    for name, data in headers.items():
        path = directory / 'include' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    clang = tools['clang']['path']
    common = ['-std=c17', '-Oz', '-ffreestanding', '-fno-builtin', '-fno-stack-protector',
              '-fno-asynchronous-unwind-tables', '-fno-unwind-tables', '-Wall', '-Wextra', '-Werror',
              '-Wno-empty-body', '-nostdinc', '-I' + str(directory / 'include')]
    # The single empty loop body is unchanged upstream code, hence this scoped
    # diagnostic suppression rather than an edit to the borrowed implementation.
    native = directory / 'memcmp.o'
    run('compare-native-build', [clang, *common, '--target=x86_64-unknown-none', '-mno-red-zone',
                                  '-c', directory / 'memcmp.c', '-o', native])
    host = directory / 'host.o'
    run('compare-host-build', [clang, *common, '-fsanitize=undefined', '-fno-sanitize-recover=all',
                              '-Dmemcmp=aether_owner_memcmp', '-c', directory / 'memcmp.c', '-o', host])
    oracle = system / 'sys-init/tests/owner_compare.c'
    run('compare-oracle-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
                                  '--style=file:' + str(system / 'userland/docs/quality/clang-format.yaml'), oracle])
    harness = directory / 'host-tests'
    host_flags = ['-std=c17', '-O2', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined',
                  '-fno-sanitize-recover=all']
    run('compare-host-link', [clang, *host_flags, oracle, host, '-o', harness])
    run('compare-host-tests', [harness])
    changed = members['src/string/memcmp.c'].replace(b'const unsigned char *l', b'const signed char *l')
    if changed == members['src/string/memcmp.c']:
        raise ValueError('signed-byte control did not change the source')
    (directory / 'signed.c').write_bytes(changed)
    run('compare-control-build', [clang, *common, '-Dmemcmp=aether_owner_memcmp',
                                 '-c', directory / 'signed.c', '-o', directory / 'signed.o'])
    run('compare-control-link', [clang, *host_flags, oracle, directory / 'signed.o', '-o', directory / 'signed-tests'])
    failure = run('compare-control-tests', [directory / 'signed-tests'], expected=1)
    if b'comparison ordering mismatch' not in failure:
        raise ValueError('signed-byte control did not fail the ordering oracle')
    llvm = Path(tools['readelf']['path']).parent
    symbols = run('compare-symbols', [llvm / 'llvm-nm', '--defined-only', native]).decode().splitlines()
    if len(symbols) != 1 or not symbols[0].endswith(' T memcmp'):
        raise ValueError('comparison object contains unexpected defined symbols')
    if run('compare-undefined', [llvm / 'llvm-nm', '--undefined-only', native]).strip():
        raise ValueError('comparison object has hidden dependencies or recursion')
    return native, dict(archive_sha256=ARCHIVE_SHA, members=MEMBERS, headers=HEADERS,
                        native_object_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
                        license='MIT', scope='explicit owner comparison selection only')
