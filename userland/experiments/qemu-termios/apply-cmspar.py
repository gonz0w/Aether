#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Apply only the reviewed QEMU10.0.11 CMSPAR diff to its exact source input."""
import difflib
import hashlib
from pathlib import Path
import sys

SOURCE_SHA256 = '6b053f45e1000c606dd1092ecfec98d887e22fb5cfb67f8701fbc75413ee2ba0'


def apply(source, patch):
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise RuntimeError('original QEMU source identity mismatch')
    original = raw.decode('utf-8')
    anchor = '\t{ TARGET_CRTSCTS, TARGET_CRTSCTS, CRTSCTS, CRTSCTS },\n'
    if original.count(anchor) != 1:
        raise RuntimeError('CMSPAR patch anchor mismatch')
    row = ('#if defined(TARGET_CMSPAR) && defined(CMSPAR)\n'
           '        { TARGET_CMSPAR, TARGET_CMSPAR, CMSPAR, CMSPAR },\n'
           '#endif\n')
    revised = original.replace(anchor, anchor + row)
    diff = ''.join(difflib.unified_diff(original.splitlines(True), revised.splitlines(True),
                                      fromfile='a/linux-user/syscall.c',
                                      tofile='b/linux-user/syscall.c'))
    if diff.encode() != patch.read_bytes():
        raise RuntimeError('approved CMSPAR diff mismatch')
    source.write_bytes(revised.encode())
    return hashlib.sha256(source.read_bytes()).hexdigest()


if __name__ == '__main__':
    print(apply(Path(sys.argv[1]), Path(sys.argv[2])))
