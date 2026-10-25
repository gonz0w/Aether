# SPDX-License-Identifier: BSD-2-Clause
"""Pinned upstream ZPL fixture intake, not a formatter or a native launcher."""
import hashlib
from pathlib import Path
import tarfile

from openzfs_elapsed import CURRENT

FIXTURE = CURRENT / ('baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/'
                     'tests/zfs-tests/tests/functional/compression/testpool_zstd.tar.gz')
FIXTURE_SHA256 = 'b5a4609e8b3575ca6ab9b7ed3b5db3b2967ca2f026df8b3ece901a6cfa513bcc'
FIXTURE_IMAGE_SHA256 = '6f3ded903a6bb2f9baaecc64359fe464910b4b7d003e5e7054768e54fe3f65d2'
FIXTURE_BYTES = 1024 * 1024 * 1024
MEMBER = 'testpool_zstd'

ACCOUNTING_SOURCE_SHA256 = '3b835e0bb5b0f17154bc2a4a971605709a74e1cec646e6022908dc086865eeee'
ACCOUNTING_PREFIX_SHA256 = 'cd061ab471a8830fa678d8f0f969651d58dea8166567be369d9b974d77a62cc0'


def recovery_label_source(text):
    """Select newer exported TXGs only; retain every other fixed-label rule."""
    anchor = '        txg != 782 ||'
    if text.count(anchor) != 1:
        raise ValueError('ZPL recovery label TXG context changed')
    return text.replace(anchor, '        txg <= 782 ||', 1)


def accounting_source(text):
    """Original file-info callback only; preserve CDDL notices and reject drift.

    The libzpool profile omits the normal kernel ZPL SA include closure. Supply
    those original definitions in a wrapper, without modifying the callback or
    importing the unrelated vnode quota-policy implementation that follows it.
    Caller owns generated output; no registry or engine operation happens here.
    """
    if hashlib.sha256(text.encode()).hexdigest() != ACCOUNTING_SOURCE_SHA256:
        raise ValueError('ZPL original accounting source hash mismatch')
    marker = '\nstatic void\nfuidstr_to_sid'
    if text.count(marker) != 1:
        raise ValueError('ZPL accounting prefix context changed')
    prefix = text.split(marker)[0] + '\n'
    if hashlib.sha256(prefix.encode()).hexdigest() != ACCOUNTING_PREFIX_SHA256:
        raise ValueError('ZPL original accounting prefix hash mismatch')
    return ('#include <sys/zfs_context.h>\n#include <sys/sa.h>\n'
            '#include <sys/zfs_znode.h>\n#include <sys/zfs_sa.h>\n'
            '#line 1 "module/zfs/zfs_quota.c"\n' + prefix)


def prepare_fixture(output, archive=FIXTURE):
    """Create one exclusive, readonly sparse copy; no archive paths are extracted.

    The developer supplies an existing private output directory. No devices,
    pool import or host services are accessed. A failed copy removes only its
    newly created file. The caller owns removal of a successful output after
    the reader and its process have stopped.
    """
    archive = Path(archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != FIXTURE_SHA256:
        raise ValueError('namespace fixture compressed hash mismatch')
    target = Path(output) / 'namespace-pool.img'
    with tarfile.open(archive, 'r:gz') as source:
        members = source.getmembers()
        if (len(members) != 1 or members[0].name != MEMBER or
                not members[0].isfile() or members[0].size != FIXTURE_BYTES):
            raise ValueError('namespace fixture requires its single pinned regular member')
        member = members[0]
        previous_end = 0
        for start, length in member.sparse or ():
            if start < previous_end or length < 0 or start + length > FIXTURE_BYTES:
                raise ValueError('namespace fixture sparse extent outside member')
            previous_end = start + length
        stream = source.extractfile(member)
        if stream is None:
            raise ValueError('namespace fixture has no member data')
        digest = hashlib.sha256()
        zero = bytes(1024 * 1024)
        # Exclusive creation also rejects an existing symlink without touching
        # its referent. Never unlink a target this call did not create.
        with stream, target.open('xb') as destination:
            try:
                copied = 0
                while copied < FIXTURE_BYTES:
                    chunk = stream.read(min(len(zero), FIXTURE_BYTES - copied))
                    if not chunk:
                        raise ValueError('namespace fixture truncated member')
                    digest.update(chunk)
                    copied += len(chunk)
                    if chunk == zero[:len(chunk)]:
                        destination.seek(len(chunk), 1)
                    else:
                        destination.write(chunk)
                if stream.read(1):
                    raise ValueError('namespace fixture excess member data')
                destination.truncate(FIXTURE_BYTES)
                destination.flush()
                with target.open('rb') as check:
                    actual = hashlib.file_digest(check, 'sha256').hexdigest()
                if actual != digest.hexdigest() or actual != FIXTURE_IMAGE_SHA256:
                    raise ValueError('namespace fixture copied image hash mismatch')
                target.chmod(0o444)
            except BaseException:
                target.unlink()
                raise
    return {'archive_sha256': FIXTURE_SHA256, 'member': MEMBER,
            'logical_bytes': FIXTURE_BYTES, 'image_sha256': actual,
            'output': str(target), 'scope': 'upstream fixture copy; no pool import or native qualification'}


def _native_media_snapshot(path):
    """Fixed delegated geometry only, streaming hashes and exact guards."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('namespace media unavailable or symlink')
    with path.open('rb') as stream:
        if stream.read(4096) != bytes([165]) * 4096:
            raise ValueError('namespace leading guard')
        region = hashlib.sha256()
        remaining = FIXTURE_BYTES
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError('namespace truncated region')
            region.update(chunk)
            remaining -= len(chunk)
        if stream.read(4096) != bytes([165]) * 4096 or stream.read(1):
            raise ValueError('namespace trailing guard or disk size')
        stream.seek(0)
        whole = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'status': 'captured', 'bytes': FIXTURE_BYTES + 8192,
            'sha256': whole, 'region_sha256': region.hexdigest(),
            'outside_region_canaries_match': True,
            'scope': 'fixed readonly host fixture bytes, not engine retirement or durability'}


def native_media_snapshot(path):
    """Pristine intake remains exact; changed media cannot use this admission."""
    result = _native_media_snapshot(path)
    if result['region_sha256'] != FIXTURE_IMAGE_SHA256:
        raise ValueError('namespace pinned region hash mismatch')
    return result


def written_native_media_snapshot(path, expected_sha256=None):
    """Inspect stopped private writer bytes; optionally enforce sealed identity.

    The caller must own the media and confirm VM termination first. This helper
    neither launches a VM nor proves export, transaction ordering or durability.
    It does not replace pristine admission. Future readonly intake must supply
    the exact writer-stop digest; None is inspection only, never run permission.
    """
    if expected_sha256 is not None and (
        not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or
        any(c not in '0123456789abcdef' for c in expected_sha256)
    ):
        raise ValueError('namespace written media requires a canonical SHA256')
    result = _native_media_snapshot(path)
    if result['region_sha256'] == FIXTURE_IMAGE_SHA256:
        raise ValueError('namespace written media still pristine')
    if expected_sha256 is not None and result['sha256'] != expected_sha256:
        raise ValueError('namespace written media sealed hash mismatch')
    result['scope'] = 'stopped writer host bytes only; not retirement or durability'
    result['sealed_identity_match'] = expected_sha256 is not None
    return result


def prepare_native_fixture(output):
    """One native READ region, fixed guards; dispose the intermediate raw copy."""
    raw = Path(prepare_fixture(output)['output'])
    disk = Path(output) / 'native-namespace.raw'
    try:
        with raw.open('rb') as source, disk.open('xb') as destination:
            try:
                destination.write(bytes([165]) * 4096)
                zero = bytes(1024 * 1024)
                while chunk := source.read(len(zero)):
                    if chunk == zero[:len(chunk)]:
                        destination.seek(len(chunk), 1)
                    else:
                        destination.write(chunk)
                destination.write(bytes([165]) * 4096)
                destination.flush()
                result = native_media_snapshot(disk)
                # Existing virtio driver rejects a hardware RO backend. The
                # guest receives READ1 only; compare the entire copy after stop.
                disk.chmod(0o644)
            except BaseException:
                disk.unlink()
                raise
    finally:
        raw.unlink()
    return {'output': str(disk), **result}
