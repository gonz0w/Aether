#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Compile the pinned shared OpenZFS engine support objects from source."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_tools import run_tool

OPENZFS = (
    'zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1',
    'bd042e3e172d3194c5c5230bf427a54acaf8718f9981789ddd81ad18e8ab46a8',
)
ZLIB = (
    'zlib-1.3.2',
    'bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16',
)
TIRPC = (
    'libtirpc-1.3.6',
    'bbd26a8f0df5690a62a47f6aa30f797f3ef8d02560d1bc449a83066b5a1d3508',
)
SDK_TREE_SHA256 = '42d77bdc51cad2eb2f05a5cc39d63f675d5897681d688c37c623024658ff0e14'
# Preserve the established target configuration, including the features that
# select compiled implementations. This does not probe the host system.
CONFIG_ENABLED = """
ENABLE_NLS HAVE_AES HAVE_AIO_H HAVE_AVX HAVE_AVX2 HAVE_AVX512BW
HAVE_AVX512CD HAVE_AVX512DQ HAVE_AVX512ER HAVE_AVX512F HAVE_AVX512IFMA
HAVE_AVX512PF HAVE_AVX512VBMI HAVE_AVX512VL HAVE_BACKTRACE HAVE_DCGETTEXT
HAVE_DLFCN_H HAVE_EXECVPE HAVE_FORMAT_OVERFLOW HAVE_GETTEXT HAVE_GETTID
HAVE_IMPLICIT_FALLTHROUGH HAVE_INFINITE_RECURSION HAVE_INTTYPES_H
HAVE_KERNEL_INFINITE_RECURSION HAVE_LIBAIO HAVE_LIBBLKID HAVE_LIBCRYPTO
HAVE_LIBTIRPC HAVE_LIBUDEV HAVE_LIBUUID HAVE_MAKEDEV_IN_SYSMACROS
HAVE_MLOCKALL HAVE_MOUNT_SETATTR HAVE_MOVBE HAVE_PCLMULQDQ HAVE_SSE
HAVE_SSE2 HAVE_SSE3 HAVE_SSE4_1 HAVE_SSE4_2 HAVE_SSSE3 HAVE_STATX
HAVE_STATX_MNT_ID HAVE_STDINT_H HAVE_STDIO_H HAVE_STDLIB_H HAVE_STRINGS_H
HAVE_STRING_H HAVE_STRLCAT HAVE_STRLCPY HAVE_SYS_STAT_H HAVE_SYS_TYPES_H
HAVE_UDEV_DEVICE_GET_IS_INITIALIZED HAVE_UNISTD_H HAVE_VAES
HAVE_VPCLMULQDQ HAVE_XSAVE HAVE_XSAVEOPT HAVE_XSAVES HAVE_ZLIB SYSTEM_LINUX
ZFS_DEBUG
""".split()
CONFIG_VALUES = {
    'LIBFETCH_DYNAMIC': '0', 'LIBFETCH_IS_FETCH': '0', 'LIBFETCH_IS_LIBCURL': '0',
    'LIBFETCH_SONAME': '""', 'LT_OBJDIR': '".libs/"',
    'SPL_META_ALIAS': 'ZFS_META_ALIAS', 'SPL_META_RELEASE': 'ZFS_META_RELEASE',
    'SPL_META_VERSION': 'ZFS_META_VERSION', 'ZFS_META_ALIAS': '"zfs-2.4.4-1"',
    'ZFS_META_AUTHOR': '"OpenZFS"', 'ZFS_META_KVER_MAX': '"7.2"',
    'ZFS_META_KVER_MIN': '"4.18"', 'ZFS_META_LICENSE': '"CDDL"',
    'ZFS_META_NAME': '"zfs"', 'ZFS_META_RELEASE': '"1"', 'ZFS_META_VERSION': '"2.4.4"',
}
BASELINE = {
    '39.o': 'module/zcommon/zfs_fletcher_aarch64_neon.c',
    '138.o': 'module/zfs/vdev_raidz_math_aarch64_neonx2.c',
}
SPL = {'6.o': 'strlcat.c', '7.o': 'strlcpy.c', '9.o': 'tunables.c'}
ZSTD = (
    'common/entropy_common.c', 'common/error_private.c', 'common/fse_decompress.c',
    'common/pool.c', 'common/zstd_common.c', 'compress/fse_compress.c',
    'compress/hist.c', 'compress/huf_compress.c', 'compress/zstd_compress_literals.c',
    'compress/zstd_compress_sequences.c', 'compress/zstd_compress_superblock.c',
    'compress/zstd_compress.c', 'compress/zstd_double_fast.c', 'compress/zstd_fast.c',
    'compress/zstd_lazy.c', 'compress/zstd_ldm.c', 'compress/zstd_opt.c',
    'decompress/huf_decompress.c', 'decompress/zstd_ddict.c',
    'decompress/zstd_decompress.c', 'decompress/zstd_decompress_block.c',
)
CRYPTO = (
    'aes/aes_amd64.S', 'aes/aes_aesni.S', 'modes/gcm_pclmulqdq.S',
    'modes/aesni-gcm-x86_64.S', 'modes/aesni-gcm-avx2-vaes.S',
    'modes/ghash-x86_64.S', 'sha2/sha256-x86_64.S', 'sha2/sha512-x86_64.S',
    'blake3/blake3_avx2.S', 'blake3/blake3_avx512.S',
    'blake3/blake3_sse2.S', 'blake3/blake3_sse41.S',
)
ZLIB_SOURCES = (
    'adler32', 'crc32', 'deflate', 'infback', 'inffast', 'inflate', 'inftrees',
    'trees', 'zutil', 'compress', 'uncompr',
)
XDR_SOURCES = ('xdr', 'xdr_mem', 'xdr_array', 'xdr_float', 'xdr_reference', 'xdr_sizeof')
SDK_LINK_INPUTS = ('crt1.o', 'crti.o', 'crtn.o', 'libc.a')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def regular_tree(root):
    paths = sorted(root.rglob('*'))
    if any(path.is_symlink() or not (path.is_dir() or path.is_file()) for path in paths):
        raise ValueError(f'expected regular files and directories under {root.name}')
    members = {path.relative_to(root).as_posix(): digest(path) for path in paths if path.is_file()}
    rows = ''.join(f'{checksum}  {name}\n' for name, checksum in members.items())
    return hashlib.sha256(rows.encode()).hexdigest()


def unpack(archive, pin, destination, components=()):
    name, expected = pin
    root = destination / name
    count = 0
    size = 0
    with archive.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != expected:
            raise ValueError(f'{name} archive hash differs')
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode='r|*') as tar:
            for member in tar:
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != name:
                    raise ValueError(f'{name} archive contains an unexpected path')
                parts = path.parts[1:]
                if not member.isfile() or not parts or (components and parts[0] not in components):
                    continue
                count += 1
                size += member.size
                if count > 4096 or member.size > 16 * 1024**2 or size > 64 * 1024**2:
                    raise ValueError(f'{name} source selection exceeds extraction bounds')
                target = root.joinpath(*parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, target.open('xb') as output:
                    shutil.copyfileobj(source, output)
    if count == 0:
        raise ValueError(f'{name} contains no source files')
    return root


def prepare_openzfs(archive, work):
    tree = unpack(archive, OPENZFS, work, ('include', 'lib', 'module'))
    generated = work / 'include'
    (generated / 'sys').mkdir(parents=True)
    config = {name: '1' for name in CONFIG_ENABLED}
    config.update(CONFIG_VALUES)
    (generated / 'zfs_config.h').write_text(
        ''.join(f'#define {name} {value}\n' for name, value in sorted(config.items())))
    (generated / 'zfs_gitrev.h').write_text('#define\tZFS_META_GITREV "unknown"\n')
    vfs = (tree / 'lib/libspl/include/os/linux/sys/vfs.h').read_bytes()
    line = b'#include <linux/fs.h>\n'
    if vfs.count(line) != 1:
        raise ValueError('OpenZFS vfs include anchor changed')
    (generated / 'sys/vfs.h').write_bytes(vfs.replace(line, b''))
    return tree, generated


def build(args):
    compiler = args.clang.resolve(strict=True)
    compiler_sha = digest(compiler)
    if compiler_sha != args.clang_sha256:
        raise ValueError('clang executable hash differs')
    sdk = args.sdk.resolve(strict=True)
    if regular_tree(sdk) != SDK_TREE_SHA256:
        raise ValueError('guarded musl SDK stage hash differs')
    work = args.work.resolve()
    work.mkdir(mode=0o700)
    for name in ('logs', 'tmp', 'empty-root'):
        (work / name).mkdir()
    environment = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work / 'tmp')}
    deadline = time.monotonic() + 180

    def run(argv, label):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('support compile reached its deadline')
        return run_tool([str(arg) for arg in argv], environment, work / 'logs' / label,
                        timeout=min(30, remaining), limit=256 * 1024, cwd=work)

    resource = Path(run([compiler, '--no-default-config', '-print-resource-dir'],
                        'clang-resource.log').decode().strip()) / 'include'
    resource = resource.resolve(strict=True)
    resource_sha = regular_tree(resource)
    tree, generated = prepare_openzfs(args.openzfs, work)
    zlib = unpack(args.zlib, ZLIB, work)
    tirpc = unpack(args.tirpc, TIRPC, work, ('src', 'tirpc', 'COPYING'))
    base = [
        compiler, '--no-default-config', '--target=x86_64-linux-musl',
        f'--sysroot={work / "empty-root"}', '-O2', '-D_GNU_SOURCE',
        '-fstack-protector-strong', '-nostdinc', '-isystem', sdk / 'include',
        f'-ffile-prefix-map={work}=/build/aether/openzfs-support',
        f'-ffile-prefix-map={sdk}=/build/aether/sdk',
        f'-ffile-prefix-map={resource}=/toolchain/clang/include',
    ]
    zfs = [
        *base, '-std=gnu99', '-D_REENTRANT', '-D_FILE_OFFSET_BITS=64',
        '-D_LARGEFILE64_SOURCE', '-DDEBUG', '-UNDEBUG', '-DZFS_DEBUG',
        '-DLIB_ZPOOL_BUILD', '-fno-strict-aliasing',
        '-include', generated / 'zfs_config.h',
    ]
    for directory in ('include', 'module/icp/include', 'lib/libspl/include',
                      'lib/libspl/include/os/linux', 'include/os/linux/zfs'):
        zfs += ['-I', tree / directory]
    support = ['-I', generated, '-isystem', resource, *zfs[1:]]
    support.insert(0, compiler)
    zstd = [*support, '-include', tree / 'module/zstd/include/zstd_compat_wrapper.h',
            '-fno-vectorize', '-fno-slp-vectorize']
    zipped = [*base, '-std=c11', '-D_LARGEFILE64_SOURCE', '-DZ_HAVE_UNISTD_H', '-I', zlib]
    xdr = [*base, '-std=gnu99', '-I', tirpc / 'tirpc']

    objects = {}
    def compile_one(name, source, flags):
        output = work / name
        output.parent.mkdir(parents=True, exist_ok=True)
        run([*flags, '-c', source, '-o', output], name.replace('/', '-') + '.log')
        with output.open('rb') as stream:
            head = stream.read(20)
        if len(head) != 20 or head[:7] != b'\x7fELF\x02\x01\x01' or head[16:] != b'\x01\x00\x3e\x00':
            raise ValueError(f'{name} is not an x86_64 ELF relocatable object')
        objects[name] = {'sha256': digest(output), 'source': source.relative_to(work).as_posix(),
                         'source_sha256': digest(source)}

    for name, source in BASELINE.items():
        compile_one(f'baseline/closure/{name}', tree / source, zfs)
    for name, source in SPL.items():
        compile_one(f'support/{name}', tree / 'lib/libspl' / source, support)
    for index, source in enumerate(ZSTD, start=57):
        compile_one(f'support/{index}.o', tree / 'module/zstd/lib' / source, zstd)
    for index, source in enumerate(CRYPTO, start=1):
        compile_one(f'support/compression/crypto-{index}.o', tree / 'module/icp/asm-x86_64' / source, support)
    for name in ZLIB_SOURCES:
        compile_one(f'support/compression/zlib-{name}.o', zlib / f'{name}.c', zipped)
    for name in XDR_SOURCES:
        compile_one(f'xdr/{name}.o', tirpc / 'src' / f'{name}.c', xdr)

    if digest(compiler) != compiler_sha or regular_tree(resource) != resource_sha or regular_tree(sdk) != SDK_TREE_SHA256:
        raise ValueError('compiler or SDK changed during support build')
    receipt = {
        'schema': 'r1-openzfs-support-v1',
        'sources': dict(openzfs=OPENZFS[1], zlib=ZLIB[1], libtirpc=TIRPC[1]),
        'clang_sha256': compiler_sha, 'clang_headers_sha256': resource_sha,
        'sdk_stage_sha256': SDK_TREE_SHA256,
        'sdk_link_inputs': {name: digest(sdk / 'lib' / name) for name in SDK_LINK_INPUTS},
        'config_sha256': {path.relative_to(generated).as_posix(): digest(path)
                          for path in sorted(generated.rglob('*')) if path.is_file()},
        'objects': objects,
    }
    (work / 'support.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    return len(objects)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('work', 'clang', 'sdk', 'openzfs', 'zlib', 'tirpc'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--clang-sha256', required=True)
    args = parser.parse_args()
    try:
        count = build(args)
    except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as error:
        parser.exit(1, f'OpenZFS support build failed: {error}\n')
    print(f'Built {count} support objects')


if __name__ == '__main__':
    main()
