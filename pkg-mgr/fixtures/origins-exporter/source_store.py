#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host-only object fixture; see docs/contracts/LOCAL-STORE.md."""
import contextlib
import hashlib
import os
import re
import secrets
import stat
import sys

MAX_SIZE = 16 * 1024 * 1024
CHUNK = 64 * 1024
MARKER = b'origins-private-store-v1\n'
HELP = '''Preserve and verify exact bytes in a private host fixture.
Usage: sh tools/source-store.sh COMMAND ARGUMENTS
Commands:
  init ROOT                    Create a new private store (must not exist).
  put ROOT SHA256 SIZE INPUT    Admit a regular file with expected identity.
  get ROOT SHA256 SIZE          Write verified raw bytes to stdout.
  verify ROOT SHA256 SIZE       Verify stored bytes without exporting them.
Options:
  --help                       Show this help.
  --version                    Show the fixture version.
Examples:
  sh tools/source-store.sh init /absolute/private-parent/store
Limits: absolute paths without links; 16 MiB objects; owner-controlled store.
No authenticity, extraction, installation or power-loss durability claim.
Recovery: docs/contracts/LOCAL-STORE.md; failed temporary files are retained.
'''


class StoreError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def reject(code, message):
    raise StoreError(code, message)


def components(path):
    if (not path.startswith('/') or len(path) > 4096
            or any(ord(c) < 32 or ord(c) > 126 for c in path)):
        reject('PATH-INVALID', 'Use an absolute printable ASCII path.')
    parts = path[1:].split('/')
    if any(p in ('', '.', '..') or len(p) > 255 for p in parts):
        reject('PATH-INVALID', 'Empty, dot or oversized path components reject.')
    return parts


def hold(stack, fd):
    stack.callback(os.close, fd)
    return fd


def directory(stack, name, parent=None, private=False):
    fd = hold(stack, os.open(name, os.O_RDONLY | os.O_DIRECTORY
                            | os.O_NOFOLLOW, dir_fd=parent))
    info = os.fstat(fd)
    if private and (info.st_uid != os.geteuid()
                    or stat.S_IMODE(info.st_mode) != 0o700):
        reject('ROOT-INVALID', 'Store directories must be owned and mode 0700.')
    return fd


def parent_dir(stack, path):
    parts = components(path)
    fd = directory(stack, '/')
    for name in parts[:-1]:
        fd = directory(stack, name, fd)
    return fd, parts[-1]


def regular(stack, name, parent, single_link=True):
    # NONBLOCK prevents FIFO opens from waiting before fstat can reject them.
    fd = hold(stack, os.open(name, os.O_RDONLY | os.O_NOFOLLOW
                            | os.O_NONBLOCK, dir_fd=parent))
    info = os.fstat(fd)
    if (not stat.S_ISREG(info.st_mode)
            or (single_link and info.st_nlink != 1)):
        reject('TYPE-INVALID', 'Expected a regular file with one link.')
    return fd


def write_all(fd, data):
    while data:
        count = os.write(fd, data)
        if count <= 0:
            raise OSError('Write made no progress')
        data = data[count:]


def copy_verified(source, destination, digest, size):
    if os.fstat(source).st_size != size:
        reject('IDENTITY-MISMATCH', 'Byte count does not match.')
    total = 0
    checksum = hashlib.sha256()
    while True:
        chunk = os.read(source, min(CHUNK, size - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > size:
            reject('IDENTITY-MISMATCH', 'Input grew beyond the expected size.')
        checksum.update(chunk)
        if destination is not None:
            write_all(destination, chunk)
    if total != size or checksum.hexdigest() != digest:
        reject('IDENTITY-MISMATCH', 'SHA-256 or byte count does not match.')


def identity(digest, size):
    if not re.fullmatch('[0-9a-f]{64}', digest):
        reject('IDENTITY-INVALID', 'SHA-256 must be 64 lowercase hex digits.')
    if not re.fullmatch('0|[1-9][0-9]{0,8}', size):
        reject('IDENTITY-INVALID', 'Size must be a canonical decimal integer.')
    count = int(size)
    if count > MAX_SIZE:
        reject('LIMIT-EXCEEDED', 'The fixture limit is 16777216 bytes.')
    return count


def store(stack, root):
    parent, name = parent_dir(stack, root)
    fd = directory(stack, name, parent, private=True)
    marker = regular(stack, '.origins-store', fd)
    if os.read(marker, len(MARKER) + 1) != MARKER:
        reject('ROOT-INVALID', 'Store marker is invalid.')
    objects = directory(stack, 'objects', fd, private=True)
    scratch = directory(stack, 'tmp', fd, private=True)
    return objects, scratch


def temporary(stack, parent):
    # Each attempt owns one exclusive file; failures retain it for diagnosis.
    name = 'attempt-' + secrets.token_hex(16)
    fd = hold(stack, os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL
                            | os.O_NOFOLLOW, 0o600, dir_fd=parent))
    return name, fd


def initialize(root):
    with contextlib.ExitStack() as stack:
        parent, name = parent_dir(stack, root)
        os.mkdir(name, 0o700, dir_fd=parent)
        fd = directory(stack, name, parent, private=True)
        for child in ('objects', 'tmp'):
            os.mkdir(child, 0o700, dir_fd=fd)
        marker = hold(stack, os.open('.origins-store', os.O_WRONLY | os.O_CREAT
                                    | os.O_EXCL, 0o600, dir_fd=fd))
        write_all(marker, MARKER)


def operate(command, root, digest, size, source_path=None):
    size = identity(digest, size)
    with contextlib.ExitStack() as stack:
        objects, scratch = store(stack, root)
        if command == 'put':
            parent, name = parent_dir(stack, source_path)
            source = regular(stack, name, parent)
        else:
            source = regular(stack, digest, objects, single_link=False)
        if command == 'verify':
            copy_verified(source, None, digest, size)
            return
        temp_name, temp = temporary(stack, scratch)
        copy_verified(source, temp, digest, size)
        if command == 'put':
            os.fchmod(temp, 0o400)
            try:
                os.link(temp_name, digest, src_dir_fd=scratch,
                        dst_dir_fd=objects, follow_symlinks=False)
            except FileExistsError:
                current = regular(stack, digest, objects, single_link=False)
                copy_verified(current, None, digest, size)
        else:
            # Export the verified private snapshot, not a reopened mutable input.
            os.lseek(temp, 0, os.SEEK_SET)
            while True:
                chunk = os.read(temp, CHUNK)
                if not chunk:
                    break
                write_all(sys.stdout.fileno(), chunk)
        os.unlink(temp_name, dir_fd=scratch)


def main(args):
    if args == ['--help']:
        print(HELP, end='')
        return 0
    if args == ['--version']:
        print('origins-source-store 0.1.0 (host fixture)')
        return 0
    arities = {'init': 2, 'put': 5, 'get': 4, 'verify': 4}
    if not args or len(args) != arities.get(args[0]):
        print('[BLOCKED] ORIGINS-USAGE: See --help.', file=sys.stderr)
        return 64
    command, root, *rest = args
    try:
        os.umask(0o077)
        if command == 'init':
            initialize(root)
        else:
            operate(command, root, *rest)
        if command != 'get':
            print('[OK] ' + command + ': ' + ascii(root))
        return 0
    except StoreError as error:
        print('[BLOCKED] ORIGINS-' + error.code + ': ' + str(error),
              file=sys.stderr)
        return 2
    except OSError as error:
        print('[FAILED] ORIGINS-IO-ERROR: ' + ascii(str(error))
              + '; retained state may need inspection. See LOCAL-STORE.md.',
              file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('[CANCELLED] ORIGINS-INTERRUPTED: Inspect retained state.',
              file=sys.stderr)
        return 130


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
