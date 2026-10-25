#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the locked ABI24 serial-shell candidate offline."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import subprocess
import sys
import tarfile
from bounded_tools import run_tool
from serial_session_smoke import smoke, qemu_args

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'docs/aether-session.lock.json'
VERSION = 'sys-init-aether-session 0.1.0'

# Bounded ordinary-file primitives shared in behavior with the ABI22 recipe.
class Blocked(ValueError):
    pass
MAX_INPUT = 16 * 1024 * 1024


def ordinary(path, maximum=MAX_INPUT):
    """Read bounded ordinary bytes; reject links and identity changes."""
    path = Path(path).absolute()
    for parent in [path, *path.parents]:
        if parent.is_symlink():
            raise ValueError('input has a symlink component')
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
        raise ValueError('input is not a bounded ordinary file')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if len(data) > maximum or any(getattr(before, k) != getattr(opened, k)
                                  or getattr(opened, k) != getattr(after, k)
                                  or getattr(after, k) != getattr(path.stat(), k) for k in fields):
        raise ValueError('input changed during read')
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verified(path, expected, maximum=MAX_INPUT):
    data = ordinary(path, maximum)
    if digest(data) != expected:
        raise ValueError('input hash differs: ' + str(path))
    return data


def archive_files(raw, expected):
    """Check every archive member; keep only the kit and normal image/payload."""
    selected, seen, total = {}, set(), 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or '..' in path.parts or '\\' in member.name
                    or str(path) != member.name or len(member.name) > 512
                    or not member.isfile() or member.name in seen or member.name not in expected):
                raise ValueError('invalid archive member')
            seen.add(member.name)
            total += member.size
            pin = expected[member.name]
            if (member.size != pin['bytes'] or member.size > MAX_INPUT
                    or total > 96 * 1024 * 1024 or len(seen) > 1024):
                raise ValueError('archive exceeds member budget')
            data = archive.extractfile(member).read(member.size + 1)
            if len(data) != member.size or digest(data) != pin['sha256']:
                raise ValueError('archive member differs')
            if member.name.startswith('kit/') or member.name in ('normal/aether.iso', 'normal/native-c.bin'):
                selected[member.name] = data
    if seen != set(expected):
        raise ValueError('archive membership differs')
    return selected


def envelope(raw, owner):
    if len(raw) < 112 or raw[:8] != b'AENMX009' or raw[24:32] != bytes(8):
        raise ValueError('invalid serial envelope')
    sizes = struct.unpack_from('<4I', raw, 8)
    if not all(sizes) or len(raw) != 112 + sum(sizes) or not 0 < len(owner) <= 16384:
        raise ValueError('invalid serial sizes')
    prefix = bytearray(raw[:112 + sum(sizes[:3])])
    struct.pack_into('<I', prefix, 20, len(owner))
    return bytes(prefix) + owner


def preflight(tools_path=None):
    lock_raw = ordinary(LOCK)
    lock = json.loads(lock_raw)
    if lock['schema'] != 'sys-init-aether-session-lock-v1':
        raise ValueError('unsupported recipe lock')
    captured = {n: verified(ROOT / n, h) for n, h in lock['files'].items()}
    sources = {n: verified(ROOT / n, h) for n, h in lock['maintained'].items()}
    staged = {}
    for name, metadata in lock['archives'].items():
        manifest = json.loads(captured[metadata])
        if digest(captured[name]) != manifest['archive_sha256']:
            raise ValueError('archive identity differs')
        staged.update(archive_files(captured[name], manifest['members']))
    tools = lock['tools'] if tools_path is None else json.loads(ordinary(tools_path))
    if set(tools) != set(lock['tools']):
        raise ValueError('tool selection differs')
    for name, pin in tools.items():
        if pin['sha256'] != lock['tools'][name]['sha256']:
            raise ValueError('tool identity differs')
        verified(pin['path'], pin['sha256'], 256 * 1024 * 1024)
        if not os.access(pin['path'], os.X_OK):
            raise ValueError('tool is not executable')
    return lock_raw, lock, captured, sources, staged, tools


def output_path(path):
    absolute = path.absolute()
    base = ROOT / 'out'
    if ('..' in path.parts or not absolute.is_relative_to(base)
            or absolute == base or absolute.exists()
            or any(p.is_symlink() for p in (absolute, *absolute.parents))
            or not absolute.parent.is_dir()):
        raise Blocked('output must be a fresh directory under existing out/')
    return absolute


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, 'error: ' + ascii(message) + '\n')


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--tools', type=Path, help='relocate tools without changing executable hashes')
    parser.add_argument('--smoke', choices=('immediate', 'delayed'), help='run the bounded shell workload')
    parser.add_argument('--version', action='version', version=VERSION)
    args = parser.parse_args(argv)
    output, report = None, {'schema': 'sys-init-aether-session-result-v1', 'status': 'blocked', 'commands': []}
    try:
        target = output_path(args.output)
        try:
            lock_raw, lock, captured, sources, staged, tools = preflight(args.tools)
        except (OSError, ValueError, tarfile.TarError) as error:
            raise Blocked(str(error)) from error
        target.mkdir()
        output = target
        report.update(status='running', profile=lock['profile'], lock_sha256=digest(lock_raw))
        for name, data in sources.items():
            path = output / 'source' / name.removeprefix('prototypes/native-session/')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for name, data in staged.items():
            path = output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        env = os.environ.copy()
        env.pop('DYLD_LIBRARY_PATH', None)
        def run(label, command, environment=env):
            print('aether-session: ' + label, file=sys.stderr)
            report['commands'].append({'phase': label, 'argv': command})
            run_tool(command, environment, output / (label + '.log'), cwd=ROOT)
        rustenv = env.copy()
        rustenv['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
        compile_args = [tools['rustc']['path'], '--edition=2024', '--target=x86_64-unknown-none',
            '-C', 'opt-level=s', '-C', 'panic=abort', '-C', 'relocation-model=static',
            '-C', 'lto=fat', '-C', 'codegen-units=1', '--cfg', 'pipeline_dash_parent',
            '--cfg', 'session_serial', '--cfg', 'session_lifecycle', '-C',
            'link-arg=-T' + str(output / 'source/owner.ld'), str(output / 'source/init.rs')]
        for suffix in ('elf', 'raw'):
            command = compile_args + ['-o', str(output / ('owner.' + suffix))]
            if suffix == 'raw':
                command += ['-C', 'link-arg=--oformat=binary']
            run('compile-' + suffix, command, rustenv)
            pin = lock['expected'][suffix]
            raw = verified(output / ('owner.' + suffix), pin['sha256'])
            if len(raw) != pin['bytes']:
                raise ValueError('owner length differs')
        report['stack_inspection_reuse'] = {'source': lock['stack'], 'sha256': lock['files'][lock['stack']],
                                            'basis': 'exact qualified ELF and raw byte equality'}
        payload = envelope(staged['normal/native-c.bin'], ordinary(output / 'owner.raw'))
        (output / 'native-c.bin').write_bytes(payload)
        xorriso = tools['xorriso']['path']
        run('compose', [xorriso, '-indev', str(output / 'normal/aether.iso'), '-outdev',
            str(output / 'aether.iso'), '-boot_image', 'any', 'replay', '-map',
            str(output / 'native-c.bin'), '/boot/native-c.bin', '-commit'])
        run('readback', [xorriso, '-osirrox', 'on', '-indev', str(output / 'aether.iso'),
                         '-extract', '/boot', str(output / 'readback')])
        receipt = json.loads(staged['kit/receipt.json'])
        for name in ('aether', 'lifecycle.bin', 'smp-supervisor.bin', 'display.bin', 'protection.bin'):
            pin = receipt['input_files']['image/' + name]
            data = verified(output / 'readback' / name, pin['sha256'])
            if len(data) != pin['bytes']:
                raise ValueError('boot component length differs')
        if ordinary(output / 'readback/native-c.bin') != payload:
            raise ValueError('payload readback differs')
        report['boot_readback'] = 'all six components; exact client/spare/entropy prefix preserved'
        qemu = tools['qemu-system-x86_64']['path']
        (output / 'console-vars.fd').write_bytes(staged['kit/vars.fd'])
        report['console_argv'] = qemu_args(qemu, output / 'aether.iso', output / 'kit/code.fd', output / 'console-vars.fd')
        if args.smoke:
            print('aether-session: smoke-' + args.smoke, file=sys.stderr)
            report['smoke'] = smoke(output, qemu, json.loads(captured[lock['workload']]), args.smoke == 'delayed')
        # Recheck immutable inputs and executable identities after tools/guest ran.
        current = preflight(args.tools)
        if current[0] != lock_raw or current[5] != tools:
            raise ValueError('recipe selection changed during build')
        report['artifacts'] = {n: {'sha256': digest(ordinary(output / n)), 'bytes': (output / n).stat().st_size}
                               for n in ('aether.iso', 'native-c.bin', 'owner.raw', 'owner.elf', 'kit/code.fd', 'kit/vars.fd')}
        report.update(status='pass', acceptance='candidate smoke' if args.smoke else 'build only; boot untested')
        code = 0
    except KeyboardInterrupt:
        report.update(status='cancelled', error='interrupted'); code = 130
    except Blocked as error:
        report.update(status='blocked', error=ascii(str(error))); code = 2
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, tarfile.TarError) as error:
        report.update(status='fail', error=ascii(str(error))); code = 1
    if output is not None:
        (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    if code:
        print('aether-session: ' + report['error'], file=sys.stderr)
    print(json.dumps(report, sort_keys=True))
    return code


if __name__ == '__main__':
    sys.exit(main())
