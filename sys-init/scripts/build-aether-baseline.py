#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the pinned ABI22 developer baseline offline; optionally test one cycle/halt."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import select
import shlex
import shutil
import signal
import stat
import struct
import subprocess
import sys
import tarfile
import time
from bounded_tools import run_tool

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'docs/aether-baseline.lock.json'
VERSION = 'sys-init-aether-baseline 0.1.0'


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
    """Validate all members before creating any staged source file."""
    files, total = {}, 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if (name.is_absolute() or '..' in name.parts or '\\' in member.name
                    or str(name) != member.name or len(member.name) > 512):
                raise ValueError('invalid archive path')
            if member.isdir():
                continue
            if not member.isfile() or member.name in files or member.name not in expected:
                raise ValueError('unexpected archive member')
            total += member.size
            if member.size > MAX_INPUT or total > MAX_INPUT or len(files) >= 1024:
                raise ValueError('archive exceeds source budget')
            data = archive.extractfile(member).read(member.size + 1)
            if len(data) != member.size or digest(data) != expected[member.name]:
                raise ValueError('archive member differs')
            files[member.name] = data
    if set(files) != set(expected):
        raise ValueError('archive membership differs')
    return files


def envelope(raw, owner):
    if len(raw) < 80 or raw[:8] != b'AENSI001' or raw[24:32] != bytes(8):
        raise ValueError('invalid ABI22 envelope')
    sizes = struct.unpack_from('<4I', raw, 8)
    if not all(sizes) or len(raw) != 80 + sum(sizes) or not 0 < len(owner) <= 16384:
        raise ValueError('invalid envelope sizes')
    result = bytearray(raw[:80 + sum(sizes[:3])])
    struct.pack_into('<I', result, 20, len(owner))
    return bytes(result) + owner


def preflight(dependencies, tools_path=None):
    lock_raw = ordinary(LOCK)
    lock = json.loads(lock_raw)
    lock['consumed_sha256'] = digest(lock_raw)
    captured = {n: verified(ROOT / n, h) for n, h in lock['files'].items()}
    sources = archive_files(captured['docs/evidence/si07-loop-2026-10-03/consumer-sources.tar.gz'],
                            json.loads(captured['docs/evidence/si07-loop-2026-10-03/consumer-sources.json']))
    for name, pin in lock['maintained'].items():
        sources['user/native-command/' + Path(name).name] = verified(ROOT / name, pin)
    deps = json.loads(captured['docs/evidence/si07-loop-2026-10-03/dependencies.json'])
    staged_deps = {}
    for name, pin in deps.items():
        data = verified(dependencies / name.removeprefix('.deps/'), pin['sha256'])
        if len(data) != pin['bytes']:
            raise ValueError('dependency length differs')
        staged_deps[name] = data
    tools = lock['tools'] if tools_path is None else json.loads(ordinary(tools_path))
    if set(tools) != set(lock['tools']):
        raise ValueError('tool selection differs')
    for name, pin in tools.items():
        if pin['sha256'] != lock['tools'][name]['sha256']:
            raise ValueError('tool identity differs')
        verified(Path(pin['path']), pin['sha256'], 256 * 1024 * 1024)
    return lock, captured, sources, staged_deps, tools


def smoke(output, stage, qemu, probe=True, cycles=1):
    variables = output / 'smoke-vars.fd'
    shutil.copyfile(stage / '.deps/firmware/vars.fd', variables)
    argv = [qemu, '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64',
            '-smp', '1', '-m', '256M', '-drive',
            f'if=pflash,format=raw,readonly=on,file={stage / ".deps/firmware/code.fd"}',
            '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(output / 'aether.iso'),
            '-boot', 'd', '-nic', 'none', '-vga', 'std', '-display', 'none',
            '-serial', 'stdio', '-monitor', 'none', '-no-reboot', '-no-shutdown']
    result = {'argv': argv, 'status': 'incomplete'}
    data, writes, start = bytearray(), 0, time.monotonic()
    with (output / 'qemu.log').open('wb') as log:
        child = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=log, start_new_session=True)
        try:
            while time.monotonic() - start < 90:
                if select.select([child.stdout], [], [], 0.05)[0]:
                    block = os.read(child.stdout.fileno(), 4096)
                    if not block:
                        raise RuntimeError('guest ended before halt')
                    data.extend(block)
                    if len(data) > 4 * 1024 * 1024:
                        raise ValueError('serial output exceeds budget')
                if b'panic' in data.lower() or b'SI07 fixture failure\n' in data:
                    raise RuntimeError('guest rejected baseline')
                if data.count(b'SI07 request-ready\n') > writes:
                    if writes >= cycles + 1:
                        raise RuntimeError('unexpected request boundary')
                    child.stdin.write(b'r' if writes < cycles else b'h')
                    child.stdin.flush()
                    writes += 1
                match = re.search(rb'NATIVE init halted ticks=(\d+) idle=(\d+) reclaimed=(\d+)\n', data)
                if match:
                    ticks, idle, reclaims = map(int, match.groups())
                    terms = re.findall(rb'NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)\n', data)
                    expected = [(str(slot).encode(), str(gen).encode(), b'1',
                                 str(17 if slot == 1 else 0).encode())
                                for gen in range(1, cycles + 1) for slot in (2, 0, 1)]
                    if (writes != cycles + 1 or (probe and (ticks < 3005 or idle < 3000))
                            or reclaims != 3 * cycles
                            or data.count(b'SI07 command-complete\n') != cycles
                            or terms != expected or (not probe and b'SI07 idle-ready\n' in data)):
                        raise RuntimeError('guest outcome differs')
                    result.update(status='pass', ticks=ticks, idle=idle, reclaims=reclaims)
                    break
            else:
                raise TimeoutError('guest did not halt within 90 seconds')
        except BaseException as error:
            result['error'] = repr(error)
            raise
        finally:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=3)
            child.stdin.close()
            child.stdout.close()
            result.update(returncode=child.returncode, seconds=time.monotonic() - start)
            (output / 'serial.log').write_bytes(data)
            (output / 'smoke.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def build(output, dependencies, tools_path=None, test=False, service_table=False, supervised=False):
    try:
        output.relative_to(ROOT / 'out')
        if '..' in output.parts:
            raise ValueError('output cannot contain parent traversal')
        if output.exists() or any(p.is_symlink() for p in [output, *output.parents]):
            raise ValueError('output must be fresh and have no symlink components')
        lock, captured, sources, deps, tools = preflight(dependencies, tools_path)
        if not supervised:
            # Preserve qualified baseline/table bytes while evolving supervision.
            for name in lock.get('compatibility_sources', []):
                sources['user/native-command/' + Path(name).name] = captured[name]
        profile = lock['supervised'] if supervised else lock['service_table'] if service_table else lock
        output.mkdir()
    except (ValueError, OSError) as error:
        raise Blocked(str(error)) from error
    # Fresh output is owned by this invocation.
    report = {'schema': 'sys-init-aether-baseline-result-v1', 'status': 'incomplete',
              'profile': profile['profile'], 'lock_sha256': lock['consumed_sha256'],
              'tools': tools, 'commands': [], 'smoke': 'not requested'}
    save = lambda: (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    try:
        stage = output / 'source'
        for name, data in {**sources, **deps}.items():
            p = stage / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        bindir = stage / 'tools'
        bindir.mkdir(exist_ok=True)
        compiler = Path(tools['rustc']['path'])
        library = compiler.parent.parent / 'lib'
        for name, executable in [('rustc', str(compiler)), ('python3', tools['python']['path'])]:
            p = bindir / name
            prefix = 'export DYLD_LIBRARY_PATH=' + shlex.quote(str(library)) + '\n' if name == 'rustc' else ''
            p.write_text('#!/bin/sh\n' + prefix + 'exec ' + shlex.quote(executable) + ' "$@"\n')
            p.chmod(0o755)
        environment = dict(os.environ)
        environment.pop('DYLD_LIBRARY_PATH', None)
        environment.update(LC_ALL='C', PATH=os.pathsep.join([str(bindir), str(Path(tools['xorriso']['path']).parent), '/usr/bin', '/bin']),
                           AETHER_RUNNER_STARTUP=str(stage / 'user/native-command/startup.bin'))
        # The startup record belongs to the pinned runner; use its retained bytes.
        raw_envelope = captured['docs/evidence/si07-loop-2026-10-03/normal/native-c.bin']
        startup = captured['docs/evidence/si07-owner-2026-10-03/positive-2/startup.bin']
        (stage / 'user/native-command/startup.bin').write_bytes(startup)
        def run(label, argv, rust=False):
            entry = {'label': label, 'argv': argv, 'status': 'running'}
            report['commands'].append(entry)
            save()
            env = environment.copy()
            if rust:
                env['DYLD_LIBRARY_PATH'] = str(library)
            print(label + ': running', file=sys.stderr)
            try:
                run_tool(argv, env, output / (label + '.log'), cwd=stage)
                entry['status'] = 'pass'
            except BaseException as error:
                entry.update(status='fail', error=repr(error))
                raise
            finally:
                save()
        flags = ['--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=s',
                 '-C', 'panic=abort', '-C', 'relocation-model=static', '-C', 'lto=fat',
                 '-C', 'codegen-units=1', '-C', 'link-arg=-Tuser/native-connections/large-linker.ld']
        cfg = sum((['--cfg', n] for n in ['coexist', 'program', 'command_runner', 'runner_success',
                                        'runner_startup', 'init_sustained', 'init_sustained_v2']), [])
        if service_table:
            cfg += ['--cfg', 'init_service_table']
        if supervised:
            cfg += ['--cfg', 'init_supervised']
        for kind in ['raw', 'elf']:
            run('owner-' + kind, [str(compiler)] + flags + (['-C', 'link-arg=--oformat=binary'] if kind == 'raw' else [])
                + ['user/native-connections/supervisor.rs'] + cfg + ['-o', str(output / ('owner.' + kind))], True)
            prefix = profile.get('owner_prefix', 'docs/evidence/si07-loop-2026-10-03/normal/owner')
            expected = captured[prefix + '.' + kind]
            if ordinary(output / ('owner.' + kind)) != expected:
                raise ValueError('owner differs from qualified baseline')
        (output / 'native-c.bin').write_bytes(envelope(raw_envelope, ordinary(output / 'owner.raw')))
        run('kernel-image', [tools['zig']['path'], 'build', '--cache-dir', '.zig-cache',
                            '--global-cache-dir', '.zig-cache/global', '-Dsmp=false',
                            '-Dnative-init-sustained=true', '-Dnative-c-image=' + str(output / 'native-c.bin'),
                            '-p', str(output / 'image')])
        shutil.copyfile(output / 'image/aether.iso', output / 'aether.iso')
        report['artifacts'] = {n: {'sha256': digest(ordinary(output / n)), 'bytes': (output / n).stat().st_size}
                               for n in ['owner.raw', 'owner.elf', 'native-c.bin', 'aether.iso']}
        report['stack'] = profile['stack']  # Exact linked bytes permit scoped inspection reuse.
        if test:
            print('native-smoke: running', file=sys.stderr)
            report['smoke'] = smoke(output, stage, tools['qemu']['path'], probe=not service_table)
        for name, pin in tools.items():
            verified(Path(pin['path']), pin['sha256'], 256 * 1024 * 1024)
        for name, pin in lock['maintained'].items():
            verified(ROOT / name, pin)
        if digest(ordinary(LOCK)) != lock['consumed_sha256']:
            raise ValueError('baseline lock changed during build')
        for name, pin in lock['files'].items():
            verified(ROOT / name, pin)
        report['status'] = 'pass'
    except BaseException as error:
        report.update(status='fail', error=repr(error))
        raise
    finally:
        save()
    return report


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, 'error: ' + message + '\n')


def main():
    parser = Parser(description=__doc__, epilog='Developer console: r runs bytecount; h halts between cycles. Existing startup idle probe takes about 30 seconds.')
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('output', type=Path, help='fresh private output directory; parent must exist')
    parser.add_argument('--dependencies', type=Path, required=True, help='offline .deps directory matching the baseline lock')
    parser.add_argument('--tools', type=Path, help='JSON tool paths with the exact locked executable hashes')
    parser.add_argument('--supervised', action='store_true', help='with --service-table, allow one cleaned pre-effect command retry')
    parser.add_argument('--service-table', action='store_true', help='explicit ABI22 inert-table profile without the startup test probe')
    parser.add_argument('--smoke', action='store_true', help='boot one useful command cycle and authorized halt')
    args = parser.parse_args()
    if args.supervised and not args.service_table:
        parser.error('--supervised requires --service-table')
    try:
        result = build(args.output.absolute(), args.dependencies.absolute(), args.tools, args.smoke, args.service_table, args.supervised)
    except Blocked as error:
        print('blocked: ' + str(error), file=sys.stderr)
        return 2
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print('failed: ' + str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('cancelled: build interrupted', file=sys.stderr)
        return 130
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
