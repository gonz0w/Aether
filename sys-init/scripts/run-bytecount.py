#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""One guarded direct bytecount seed/cold trial on a disposable disk."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil

from persistent_zsh_serial import capture

SOURCE = Path(__file__).with_name('run-persistent-zsh.py')
SPEC = importlib.util.spec_from_file_location('persistent_recipe', SOURCE)
recipe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recipe)
require = recipe.require


def observe(raw, transport, role):
    require(transport.get('status') == 'complete'
            and transport.get('terminal') == 'halt'
            and transport.get('host_stop_confirmed')
            and transport.get('group_absent')
            and transport.get('stdout_eof') and transport.get('stderr_eof')
            and transport.get('capture_complete')
            and transport.get('input_bytes') == 0
            and b'AETHER PANIC:' not in raw, 'incomplete bytecount capture or cleanup')
    terms = re.findall(recipe.TERMINAL, raw, re.M)
    expected = [(str(slot).encode(), b'1', b'1', b'0') for slot in range(3)]
    require(sorted(terms) == expected, 'bytecount domain exit mismatch')
    reclaims = re.findall(recipe.RECLAIM, raw, re.M)
    require(sorted(reclaims) == [(str(i).encode(), b'1') for i in range(3)],
            'bytecount reclaim mismatch')
    require(raw.count(b'AETHER NATIVE BLOCK PASS') == 1, 'missing export witness')
    owner = re.findall(rb'^AETHER BYTECOUNT OWNER v=1 requests=(\d+) child_status=0 exec_ready=1 child_reclaimed=1 '
                       rb'file_exec_bytes=42904 output_verified=1 mode_cleanup=0\r?$', raw, re.M)
    require(len(owner) == 1 and 0 < int(owner[0]) <= 96, 'missing bytecount Owner result')
    require(re.search(rb'^NATIVE init halted ticks=\d+ idle=\d+ reclaimed=3\r?$',
                      raw, re.M), 'missing final bytecount halt')
    return dict(role=role, file_exec_bytes=42904, output_hex='360a',
                export='confirmed', reclaims=3, namespace_requests=int(owner[0]))


def run(args):
    session = args.session.absolute()
    require(not session.is_symlink(), 'unsafe session')
    if args.role == 'seed':
        session.mkdir(mode=0o700)
    require(session.is_dir() and session.stat().st_uid == os.getuid()
            and session.stat().st_mode & 0o077 == 0, 'session must be private and owned')
    with (session / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stage = session / args.role
        stage.mkdir(mode=0o700)
        report = recipe.checked(args.image / 'image.json', args.image_report_sha256)
        record = recipe.read_json(report)
        require(record['status'] == 'prepared' and record['role'] == 'package-' + args.role,
                'wrong bytecount image role')
        image = recipe.checked(args.image / 'image/aether.iso', record['iso_sha256'])
        boot = recipe.read_json(recipe.ROOT / 'boot/dependencies.json')
        code = recipe.checked(args.firmware / 'code.fd', boot['firmware']['code']['unpacked_sha256'])
        variables = stage / 'vars.fd'
        shutil.copyfile(recipe.checked(args.firmware / 'vars.fd',
                        boot['firmware']['vars']['unpacked_sha256']), variables)
        qemu = recipe.regular(args.qemu)
        version = recipe.run_recorded([str(qemu), '--version'], stage / 'qemu-version.log',
                                      __file__, timeout=5, limit=65536, cwd=stage)
        require(version.splitlines()[0].split()[:4] ==
                [b'QEMU', b'emulator', b'version', boot['qemu'].encode()], 'unexpected QEMU')
        disk = session / 'native-namespace.raw'
        if args.role == 'seed':
            require(args.fixture is not None, 'seed needs the exact fixture')
            before = recipe.prepare_native_fixture(session, archive=recipe.regular(args.fixture))
        else:
            previous = recipe.read_json(session / 'seed/result.json')
            require(previous['status'] == 'passed' and previous['disk_identity'] == recipe.identity(disk),
                    'cold requires the stopped successful seed')
            before = recipe.written_native_media_snapshot(disk, expected_sha256=previous['disk_after']['sha256'])
        disk_id = recipe.identity(disk)
        argv = recipe.command(qemu, image, code, variables, disk)
        planned = dict(role=args.role, command=argv, disk_identity=disk_id, disk_before=before,
                       image_report_sha256=args.image_report_sha256, qemu_sha256=recipe.digest(qemu))
        recipe.write_json(stage / 'attempt.json', planned)
        raw, transport = capture(argv, file_limit=recipe.FIXTURE_BYTES + 8192,
                                 ready_marker=b'NATIVE MEMORY admitted slot=1 generation=1 ')
        (stage / 'uart.bin').write_bytes(raw)
        result = dict(**planned, transport=transport, status='failed',
                      uart_sha256=hashlib.sha256(raw).hexdigest())
        try:
            result['observed'] = observe(raw, transport, args.role)
            require(recipe.identity(disk) == disk_id, 'disk identity changed')
            result['disk_after'] = recipe.written_native_media_snapshot(disk)
            result['status'] = 'passed'
        except (OSError, ValueError) as error:
            result['error'] = str(error)
        recipe.write_json(stage / 'result.json', result)
        require(result['status'] == 'passed', result.get('error', 'bytecount failed'))
        print(args.role + ' bytecount passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=('seed', 'cold'))
    parser.add_argument('session', type=Path)
    for name in ('image', 'qemu', 'firmware'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--image-report-sha256', required=True)
    parser.add_argument('--fixture', type=Path)
    args = parser.parse_args()
    if args.role == 'cold' and args.fixture is not None:
        parser.error('cold has no fixture input')
    run(args)


if __name__ == '__main__':
    main()
