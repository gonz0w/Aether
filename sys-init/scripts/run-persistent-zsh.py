#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Boot the fixed sys-init Zsh recipe on an owned disposable disk."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from bounded_tools import run_recorded
from persistent_zsh_serial import capture

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from openzfs_namespace import FIXTURE_BYTES, prepare_native_fixture, written_native_media_snapshot

SAMPLE = b'aB3dE6gH9jK2mN5p' * 16
PREVIOUS = {'save': 'seed', 'cold': 'save'}
COMMANDS = {
    'seed': (
        b'umask 077; setopt noclobber; umask\r',
        b'[[ -o beep ]]; print -r -- "DEFAULT $? $$ $HOME $PWD"\r',
        b'print -rn $\'setopt no_beep;\\n\' > /home/.zprofile; print -r "WRITE $?"\r',
        b'IFS= read -r p < /home/.zprofile; print -r "PROFILE $? $$ $p"\r',
        b'exit 0\r',
    ),
    'save': (
        b'[[ ! -o beep ]]; print -r -- "HOME $? $$ $PWD"\r',
        b'x=aB3dE6gH9jK2mN5p; x=$x$x$x$x; x=$x$x$x$x; setopt noclobber\r',
        b'print -rn -- "$x" >/home/note; print -r -- "SAVED $?"\r',
        b'v=$(</home/note); print -r -- "READ $? ${#v}"\r',
        b'[[ $v == "$x" ]]; print -r -- "NOTE $? $$ $v"\r',
        b'(exec -c /home/probe)\r',
        b'print -r -- "STATUS $? $$ $PWD"\r',
        b'exit 0\r',
    ),
    'cold': (
        b'[[ ! -o beep ]]; print -r -- "HOME $? $$ $PWD"\r',
        b'x=aB3dE6gH9jK2mN5p; x=$x$x$x$x; x=$x$x$x$x; setopt noclobber\r',
        b'v=$(</home/note); print -r -- "READ $? ${#v}"\r',
        b'[[ $v == "$x" ]]; print -r -- "NOTE $? $$ $v"\r',
        b'exit 0\r',
    ),
    'failure': (),
}
READY_PROMPT = b'AETHER-ZSH> '
RECLAIM = rb'^NATIVE CLEANUP v=1 slot=(\d+) generation=(\d+) phase=7 '
TERMINAL = rb'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)\r?$'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def regular(path):
    path = path.absolute()
    require(not any(item.is_symlink() for item in (path, *path.parents))
            and path.is_file(), f'expected regular file: {path}')
    require(not any(character in str(path) for character in ',\r\n'), 'invalid QEMU path')
    return path


def checked(path, expected):
    path = regular(path)
    require(digest(path) == expected, f'input hash mismatch: {path}')
    return path


def identity(path):
    info = regular(path).stat()
    require(info.st_nlink == 1, 'disk must be exclusively linked')
    return [info.st_dev, info.st_ino]


def read_json(path):
    return json.loads(regular(path).read_text())


def write_json(path, record):
    with path.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')


def failure_disk(path):
    with path.open('xb') as stream:
        stream.write(bytes([165]) * 4096)
        stream.seek(FIXTURE_BYTES, 1)
        stream.write(bytes([165]) * 4096)


def observe(raw, transport, role, manual):
    require(transport.get('status') == 'complete' and transport.get('host_stop_confirmed')
            and all(transport.get(key) for key in ('group_absent', 'stdout_eof', 'stderr_eof')),
            'serial capture or host cleanup unknown')
    admits = re.findall(rb'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) ', raw, re.M)
    terms = re.findall(TERMINAL, raw, re.M)
    reclaims = re.findall(RECLAIM, raw, re.M)
    if role == 'failure':
        require(transport.get('terminal') == 'startup-failure' and admits == [(b'0', b'1')]
                and terms == [(b'0', b'1', b'1', b'5')] and READY_PROMPT not in raw
                and b'AETHER NATIVE BLOCK PASS' not in raw and transport.get('input_bytes') == 0,
                'expected engine startup refusal without shell admission')
        return dict(engine_exit=5, engine_reclaimed=reclaims == [(b'0', b'1')],
                    shell_admitted=False, export='unverified', clean_halt=False)

    required = [(b'0', b'1'), (b'1', b'1')]
    if role == 'save':
        required.append((b'2', b'1'))
    require(transport.get('terminal') == 'halt' and admits == required
            and sorted(reclaims) == required and b'AETHER PANIC:' not in raw
            and raw.count(b'AETHER NATIVE BLOCK PASS') == 1 and READY_PROMPT in raw,
            'expected app admissions, exact reclaims and clean halt')
    expected = [(slot, generation, b'1', b'23' if slot == b'2' else b'0')
                for slot, generation in required]
    require(sorted(terms) == expected, 'unexpected engine, shell or helper exit')
    owner = re.findall(rb'^AETHER ZSH OWNER v=\d+ requests=(\d+) .* mode_cleanup=0\r?$', raw, re.M)
    halt = re.findall(rb'^NATIVE init halted ticks=\d+ idle=\d+ reclaimed=(\d+)\r?$', raw, re.M)
    require(len(owner) == 1 and 0 < int(owner[0]) <= 96
            and halt == [str(len(required)).encode()], 'missing MODE restoration or halt receipt')
    if role == 'seed':
        require(b'PROFILE 0 9 setopt no_beep;' in raw, 'missing persisted profile write/read')
    else:
        require(re.search(rb'^NOTE 0 9 ' + SAMPLE + rb'\r?$', raw, re.M) is not None,
                'missing exact note readback; use the documented commands')
        require(re.search(rb'^READ 0 256\r?$', raw, re.M) is not None, 'missing note read status')
    if role == 'save':
        require(b'SAVED 0' in raw and b'STATUS 23 9 /home' in raw, 'missing save and helper results')
    return dict(engine_exit=0, engine_reclaimed=True, shell_admitted=True,
                export='confirmed', clean_halt=True, reclaims=len(required),
                namespace_requests=int(owner[0]), manual=manual)


def command(qemu, image, code, variables, disk):
    return [
        str(qemu), '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64',
        '-smp', '1', '-m', '256M', '-drive', f'if=pflash,format=raw,readonly=on,file={code}',
        '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(image),
        '-boot', 'd', '-nic', 'none', '-vga', 'std', '-display', 'none', '-monitor', 'none',
        '-serial', 'stdio', '-no-reboot', '-no-shutdown',
        '-object', 'rng-random,id=random,filename=/dev/urandom',
        '-device', 'virtio-rng-pci,rng=random,disable-modern=on,max-bytes=1048576,period=1000',
        '-rtc', 'base=2026-10-06T12:34:00,clock=vm',
        '-drive', f'if=none,id=work,format=raw,cache=writeback,file={disk}',
        '-device', 'virtio-blk-pci,drive=work,disable-modern=on',
    ]


def run(args):
    role, session = args.role, args.session.absolute()
    require(not args.manual or role == 'cold', 'manual input applies to cold readback')
    require((args.fixture is not None) == (role == 'seed'), 'fixture is required only for seed')
    require(not any(item.is_symlink() for item in (session, *session.parents)),
            'session path has symlink components')
    require(not any(character in str(session) for character in ',\r\n'), 'invalid session path')
    if role in ('seed', 'failure'):
        session.mkdir(mode=0o700)
    require(session.is_dir() and session.stat().st_uid == os.getuid()
            and session.stat().st_mode & 0o077 == 0, 'session must be private and owned')
    stage = session / role
    flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW
    with os.fdopen(os.open(session / '.lock', flags, 0o600), 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stage.mkdir(mode=0o700)
        execute(args, session, stage)


def execute(args, session, stage):
    role = args.role
    expected_image = 'seed' if role == 'seed' else 'note'
    report = checked(args.image / 'image.json', args.image_report_sha256)
    image_record = read_json(report)
    require(image_record['status'] == 'prepared' and image_record['role'] == expected_image,
            'image report is for a different boot role')
    image = checked(args.image / 'image/aether.iso', image_record['iso_sha256'])
    boot = read_json(ROOT / 'boot/dependencies.json')
    code = checked(args.firmware / 'code.fd', boot['firmware']['code']['unpacked_sha256'])
    variables = stage / 'vars.fd'
    shutil.copyfile(checked(args.firmware / 'vars.fd', boot['firmware']['vars']['unpacked_sha256']), variables)
    checked(variables, boot['firmware']['vars']['unpacked_sha256'])
    qemu = regular(args.qemu)
    version = run_recorded([str(qemu), '--version'], stage / 'qemu-version.log', __file__, timeout=5,
                           limit=65536, cwd=stage)
    require(version.splitlines()[0].split()[:4] == [b'QEMU', b'emulator', b'version',
                                                  boot['qemu'].encode()], 'unexpected QEMU version')
    disk = session / 'native-namespace.raw'
    if role == 'seed':
        start = prepare_native_fixture(session, archive=regular(args.fixture))
    elif role == 'failure':
        failure_disk(disk)
        start = {'sha256': digest(disk)}
    else:
        previous = read_json(session / PREVIOUS[role] / 'result.json')
        require(previous['status'] == 'passed' and previous['disk_identity'] == identity(disk)
                and previous['role'] == PREVIOUS[role], 'previous stopped disk identity mismatch')
        start = written_native_media_snapshot(disk, expected_sha256=previous['disk_after']['sha256'])
        if role == 'cold':
            require(previous['image_report_sha256'] == args.image_report_sha256,
                    'cold boot must use the same image as save')
    disk_id = identity(disk)
    argv = command(qemu, image, code, variables, disk)
    planned = dict(role=role, image_report_sha256=args.image_report_sha256,
                   qemu_sha256=digest(qemu), disk_identity=disk_id, disk_before=start, command=argv)
    write_json(stage / 'attempt.json', planned)
    raw, transport = capture(argv, file_limit=FIXTURE_BYTES + 8192, manual=args.manual, failure=role == 'failure',
                             inputs=() if args.manual else COMMANDS[role])
    (stage / 'uart.bin').write_bytes(raw)
    result = dict(**planned, transport=transport, status='failed',
                  uart_sha256=hashlib.sha256(raw).hexdigest())
    try:
        result['observed'] = observe(raw, transport, role, args.manual)
        require(identity(disk) == disk_id, 'disk replaced during boot')
        if role == 'failure':
            require(digest(disk) == start['sha256'], 'failed startup changed blank media')
            result['disk_after'] = start
        else:
            result['disk_after'] = written_native_media_snapshot(disk)
        result['status'] = 'passed'
    except (OSError, ValueError) as error:
        result['error'] = str(error)
    write_json(stage / 'result.json', result)
    require(result['status'] == 'passed', result.get('error', 'unknown boot result'))
    print(f'{role} passed; result in {stage / "result.json"}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=COMMANDS)
    parser.add_argument('session', type=Path)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--image-report-sha256', required=True)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--fixture', type=Path)
    parser.add_argument('--manual', action='store_true')
    args = parser.parse_args()
    try:
        run(args)
    except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as error:
        parser.exit(1, f'{args.role} stopped: {error}\n')


if __name__ == '__main__':
    main()
