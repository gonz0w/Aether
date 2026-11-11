#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build one offline persistent serial Zsh ISO from the selected sealed inputs."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import struct
import subprocess
import sys

from bounded_tools import run_tool

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 'aether-persistent-zsh-image-v1'
MAX_MEMBER = 16 * 1024 * 1024
SOURCE_ARTIFACT_LOCK = Path(__file__).with_name('r1-zsh-artifacts.json')
# The accepted #170 seal manifests identify all inputs and notices for each role.
PROFILES = {
    'seed': {
        'app': 'b080dfebc25ec679b38f370b00b2bd8ad289cee48fa701d7b01c6ee09236f843',
        'engine': '4274a6fbfb804827406e45d00fca2f841047c3d05d59370c27dad69cbe8a1a99',
        'envelope': '84e5232e2547958897d1b6639c43ac3df5da099cbc003b39c5d2660b5a90681e',
        'magic': b'AENFS006',
        'owner_limit': 81920,
    },
    'note': {
        'app': '8a37bf1f30cb3d3c627e1ef972b58ea65ac22dae553dda1a6e79ad2494cbe376',
        'engine': 'c7b28c36df45d3598fb6eaf7e2aebc6c2875d489aea0e3e7cc3a67eb1731e623',
        'envelope': 'dd531b981dbc484a97668dd0d955295c760a161f9900005a1a38182dc3b989dd',
        'magic': b'AENFS007',
        'owner_limit': 90112,
    },
}
BOOT_PINS = {
    'limine/BOOTX64.EFI': '17cf42c781afd2d631ca4a06a4f9f6e82af61fc03938180cd1b1d004ecdc7ad2',
    'limine/limine-uefi-cd.bin': 'f2177e5c9fe4fbcbe0ea1e74f14b49c3f7b0fbbc3c50d8d4c2d278ca280de6d6',
    'limine/LICENSE': 'f174b8ff78f6f8982a1fc992668f8486eb8cf598f6938923c22e9bb50f8338a8',
    'firmware/code.fd': '33090cc07675baa5190d9f1e84bf5176b33bcbfa9bacac522961150cdb6dbb2a',
    'firmware/vars.fd': '5d2ac383371b408398accee7ec27c8c09ea5b74a0de0ceea6513388b15be5d1e',
}
KERNEL_FLAGS = (
    'native-memory', 'native-memory-large', 'native-image-large', 'native-backing',
    'native-service-memory', 'native-threads', 'native-thread-pair', 'native-thread-reuse',
    'native-thread-origin', 'native-service-workers', 'native-clock', 'native-entropy',
    'native-rtc', 'native-service-block', 'native-service-cleanup-trace',
    'native-service-channel', 'native-service-channel-wait', 'native-service-activation',
    'native-service-zpl-budget', 'native-process-freeze', 'native-process-copy',
    'native-process-exec', 'native-signal-actions', 'native-signal-public',
    'native-copy-signals', 'native-runner-local', 'native-parent-identity',
    'native-pipeline-capacity', 'native-session-lifecycle', 'native-fs-session',
    'native-fs-session-init', 'native-fs-owner-data', 'native-fs-owner-stack',
    'native-fs-application-profile', 'native-zsh-terminfo', 'native-tty-mode-probe',
    'native-tty-signal-probe', 'native-signal-mask-delivery', 'native-zsh-external',
    'native-signal-suspend', 'native-zsh-file-exec', 'native-zsh-operator',
    'native-zsh-home-redirection',
)
KERNEL_SOURCES = (
    'build.zig', 'rust-toolchain.toml', 'LICENSE', 'boot/limine.conf', 'boot/dependencies.json',
    'scripts/deps.py', 'scripts/image.py', 'scripts/user.py', 'scripts/display.py',
    'scripts/lifecycle.py', 'scripts/smp_supervisor.py', 'user/protection/main.rs',
    'user/protection/linker.ld', 'user/display/main.rs', 'user/lifecycle/main.rs',
    'user/smp_supervisor/main.rs', 'sys-init/scripts/bounded_tools.py',
    'sys-init/scripts/build-persistent-zsh.py',
)


class Usage(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[ERROR] ' + ascii(message) + '\n')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_member(root, name, maximum=MAX_MEMBER):
    path = root / name
    if path.resolve(strict=True) != path:
        raise ValueError(f'input has a symlink component: {path}')
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= maximum:
        raise ValueError(f'input is not a bounded regular file: {path}')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if len(raw) != before.st_size or any(
        len({getattr(info, key) for info in (before, opened, after, path.stat())}) != 1
        for key in fields
    ):
        raise ValueError(f'input changed during read: {path}')
    return raw


def read_seal(root, expected, selected):
    manifest = read_member(root, 'SHA256SUMS', 65536)
    if digest(manifest) != expected:
        raise ValueError(f'seal does not match the selected role: {root}')
    payloads = {}
    members = set()
    for line in manifest.decode('ascii').splitlines():
        checksum, name = line.split('  ', 1)
        if name in members or not re.fullmatch(r'[A-Za-z0-9._/-]+', name):
            raise ValueError(f'invalid seal member: {name}')
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or path.as_posix() != name:
            raise ValueError(f'invalid seal path: {name}')
        members.add(name)
        raw = read_member(root, name)
        if digest(raw) != checksum:
            raise ValueError(f'seal member changed: {root / name}')
        if name in selected:
            payloads[name] = raw
    actual = {path.relative_to(root).as_posix() for path in root.rglob('*')
              if path.is_symlink() or not path.is_dir()}
    if actual != members | {'SHA256SUMS'} or set(payloads) != selected:
        raise ValueError(f'seal membership does not match: {root}')
    return payloads


def envelope(role, app_root, engine_root):
    profile = PROFILES[role]
    app = read_seal(app_root, profile['app'], {'zsh.elf', 'helper.elf', 'owner.bin'})
    engine = read_seal(engine_root, profile['engine'], {'filesystem.elf'})['filesystem.elf']
    return pack_envelope(role, engine, app, profile['envelope'])


def source_envelope(role, inputs):
    lock_bytes = read_member(SOURCE_ARTIFACT_LOCK.parent, SOURCE_ARTIFACT_LOCK.name, 65536)
    lock = json.loads(lock_bytes)
    if lock.get('schema') != 'aether-r1-source-zsh-v1':
        raise ValueError('invalid R1 source artifact lock')
    role_lock = lock['roles'][role]
    names = {'zsh.elf', 'helper.elf', 'owner.bin', 'filesystem.elf'}
    if set(role_lock['members']) != names:
        raise ValueError('incomplete R1 source artifact lock')
    payloads = {}
    for name in sorted(names):
        raw = read_member(inputs, name)
        if digest(raw) != role_lock['members'][name]:
            raise ValueError(f'source-built {role} input differs: {name}')
        payloads[name] = raw
    engine = payloads.pop('filesystem.elf')
    return pack_envelope(role, engine, payloads, role_lock['envelope']), digest(lock_bytes)


def pack_envelope(role, engine, app, expected):
    profile = PROFILES[role]
    shell, helper, owner = (app[name] for name in ('zsh.elf', 'helper.elf', 'owner.bin'))
    if (not 0 < len(engine) <= 8388608 or not 0 < len(shell) <= 1572864
            or not 0 < len(helper) <= 1572864 or not 0 < len(owner) <= profile['owner_limit']
            or shell == helper):
        raise ValueError(f'payload sizes or roles do not match {role}')
    nested = (struct.pack('<8sIIIIQ', b'AENMX011', len(shell), len(shell), len(helper),
                          len(owner), 0)
              + bytes(range(80)) + shell + shell + helper + owner)
    raw = struct.pack('<8sII', profile['magic'], len(engine), len(nested)) + bytes(range(32))
    raw += engine + nested
    if digest(raw) != expected:
        raise ValueError(f'composed envelope does not match the accepted {role} bytes')
    return raw


def boot_pins():
    root = ROOT / '.deps'
    manifest = json.loads(read_member(root, 'manifest.json', 65536))
    if (manifest['files'] != BOOT_PINS
            or manifest['lock'] != identity(ROOT / 'boot/dependencies.json')):
        raise ValueError('boot dependency manifest does not match the selected boot inputs')
    for name, expected in BOOT_PINS.items():
        if digest(read_member(root, name)) != expected:
            raise ValueError(f'boot dependency changed: {root / name}')
    return dict(BOOT_PINS)


def kernel_sources():
    paths = [ROOT / name for name in KERNEL_SOURCES]
    paths.extend(sorted(path for path in (ROOT / 'kernel').rglob('*') if path.is_file()))
    return {path.relative_to(ROOT).as_posix(): identity(path) for path in paths}


def tool_pins(args):
    paths = {name: getattr(args, name).resolve(strict=True)
             for name in ('zig', 'rustc', 'xorriso')}
    paths['python3'] = Path(sys.executable).resolve(strict=True)
    for path in paths.values():
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError(f'tool is not executable: {path}')
    # The pinned macOS rust-lld needs its adjacent Rust LLVM dylib in its search path.
    if sys.platform == 'darwin':
        paths['rust_llvm'] = paths['rustc'].parent.parent / 'lib/libLLVM.dylib'
    return {name: {'path': str(path), 'sha256': identity(path)} for name, path in paths.items()}


def check_source_geometry(role, work, zig, environment):
    view = work / 'kernel-view'
    view.mkdir()
    for name in ('native_fs_session.zig', 'native_elf.zig', 'native_launch.zig', 'arch'):
        (view / name).symlink_to(ROOT / 'kernel' / name)
    (view / 'facade.zig').write_text(
        'pub const session=@import("native_fs_session.zig");\n'
        'pub const elf=@import("native_elf.zig");\n'
        'pub const launch=@import("native_launch.zig");\n')
    parser = 'parseOperatorNoteApplication' if role == 'note' else 'parseHomeRedirectionApplication'
    check = work / 'check-source-image.zig'
    check.write_text('''
const std = @import("std");
const kernel = @import("kernel");
pub fn main() !void {
    const raw = @embedFile("envelope.bin");
    const bundle = try kernel.session.PARSER(raw);
    const engine = try kernel.elf.parseWithLimits(bundle.engine, kernel.elf.large_limits);
    const engine_pages = try kernel.launch.backingPages(&engine);
    if (engine_pages > 8192) return error.EngineBacking;
    var pages: [3]usize = undefined;
    for (bundle.session.images, 0..) |bytes, index| {
        const app = try kernel.elf.parseApplication(bytes);
        pages[index] = try kernel.launch.backingPages(&app);
        if (pages[index] > 640) return error.ApplicationBacking;
    }
    std.debug.print("engine_pages={d} app_pages={any} owner_bytes={d}\\n",
        .{ engine_pages, pages, bundle.session.supervisor.len });
}
'''.replace('PARSER', parser))
    output = run_tool(
        [zig, 'run', '-OReleaseSafe', '--cache-dir', str(work / 'cache'),
         '--global-cache-dir', str(work / 'global'), '--dep', 'kernel',
         '-Mroot=' + str(check), '-Mkernel=' + str(view / 'facade.zig')],
        environment, work / 'source-geometry.log', timeout=60, cwd=work)
    shutil.rmtree(view)
    return output.decode('ascii').strip()


def build(args, work, report):
    packed = work / 'envelope.bin'
    if args.source_inputs is None:
        raw = envelope(args.role, args.app_seal.resolve(strict=True),
                       args.engine_seal.resolve(strict=True))
        report.update(app_seal_sha256=PROFILES[args.role]['app'],
                      engine_seal_sha256=PROFILES[args.role]['engine'])
    else:
        raw, lock_sha = source_envelope(args.role, args.source_inputs.resolve(strict=True))
        report['source_artifact_lock_sha256'] = lock_sha
    packed.write_bytes(raw)
    report.update(
        envelope_sha256=identity(packed),
        boot_inputs=boot_pins(),
        kernel_sources=kernel_sources(),
        tools=tool_pins(args),
        firmware_code_sha256=BOOT_PINS['firmware/code.fd'],
        firmware_vars_sha256=BOOT_PINS['firmware/vars.fd'],
    )
    tools = report['tools']
    tool_bin = work / 'tools'
    tool_bin.mkdir()
    for name in ('python3', 'xorriso'):
        (tool_bin / name).symlink_to(tools[name]['path'])
    rustc = tool_bin / 'rustc'
    if 'rust_llvm' in tools:
        libraries = shlex.quote(str(Path(tools['rust_llvm']['path']).parent))
        compiler = shlex.quote(tools['rustc']['path'])
        rustc.write_text('#!/bin/sh\n'
                         f'export DYLD_LIBRARY_PATH={libraries}\n'
                         f'exec {compiler} "$@"\n', encoding='utf-8')
        rustc.chmod(0o700)
        report['rust_wrapper_sha256'] = identity(rustc)
    else:
        rustc.symlink_to(tools['rustc']['path'])
    temporary = work / 'tmp'
    temporary.mkdir()
    environment = dict(PATH=f'{tool_bin}:/usr/bin:/bin', LC_ALL='C', TMPDIR=str(temporary),
                       PYTHONDONTWRITEBYTECODE='1')
    zig = tools['zig']['path']
    report['zig_version'] = run_tool([zig, 'version'], environment, work / 'zig-version.log',
                                     timeout=10, limit=4096, cwd=ROOT).decode('ascii').strip()
    if report['zig_version'] != '0.16.0':
        raise ValueError('Zig version must be 0.16.0')
    if args.source_inputs is not None:
        environment.update(AETHER_R1_SOURCE_IMAGE='1', TZ='UTC')
        report['source_geometry'] = check_source_geometry(args.role, work, zig, environment)
    command = [zig, 'build', '-p', str(work / 'image'),
               '--cache-dir', str(work / 'cache'), '--global-cache-dir', str(work / 'global'),
               '-Dsmp=false', f'-Dnative-c-image={packed}']
    command.extend(f'-D{flag}=true' for flag in KERNEL_FLAGS)
    if args.role == 'note':
        command.append('-Dnative-zsh-operator-note=true')
    report['command'] = command
    run_tool(command, environment, work / 'build.log', timeout=180, cwd=ROOT)
    report['build_child_reaped'] = True
    report['build_output_drained'] = True
    if (kernel_sources() != report['kernel_sources'] or boot_pins() != report['boot_inputs']
            or tool_pins(args) != tools or identity(packed) != report['envelope_sha256']):
        raise ValueError('kernel sources or build inputs changed during image preparation')
    if args.source_inputs is not None and identity(SOURCE_ARTIFACT_LOCK) != report['source_artifact_lock_sha256']:
        raise ValueError('source artifact lock changed during image preparation')
    iso, kernel = work / 'image/aether.iso', work / 'image/bin/aether'
    if not iso.is_file() or not kernel.is_file():
        raise ValueError('build did not produce the required kernel and ISO')
    for path in ('cache', 'global', 'tools', 'tmp'):
        shutil.rmtree(work / path)
    report.update(status='prepared', iso_sha256=identity(iso), kernel_sha256=identity(kernel),
                  intermediate_cleanup='complete')


def main():
    parser = Usage(description=__doc__)
    parser.add_argument('--version', action='version', version=SCHEMA)
    parser.add_argument('role', choices=PROFILES)
    parser.add_argument('work', type=Path, help='new output directory')
    for name in ('zig', 'rustc', 'xorriso'):
        parser.add_argument(f'--{name}', required=True, type=Path)
    for name in ('app-seal', 'engine-seal', 'source-inputs'):
        parser.add_argument(f'--{name}', type=Path)
    args = parser.parse_args()
    if args.source_inputs is None:
        if args.app_seal is None or args.engine_seal is None:
            parser.error('supply both seals, or use --source-inputs')
    elif args.app_seal is not None or args.engine_seal is not None:
        parser.error('source inputs cannot be combined with seals')
    try:
        work = args.work.parent.resolve(strict=True) / args.work.name
        work.mkdir(mode=0o700)
    except OSError as error:
        print('[BLOCKED]', ascii(str(error)), file=sys.stderr)
        return 2
    report = dict(schema=SCHEMA, role=args.role, status='blocked')
    code = 0
    try:
        build(args, work, report)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        code = 1 if 'command' in report else 2
        report.update(status='failed' if code == 1 else 'blocked', error=str(error))
        print('[ERROR]' if code == 1 else '[BLOCKED]', ascii(str(error)), file=sys.stderr)
    except KeyboardInterrupt:
        code = 1
        report.update(status='failed', error='build interrupted')
        print('[ERROR] Build interrupted.', file=sys.stderr)
    (work / 'image.json').write_text(json.dumps(report, indent=2) + '\n', encoding='ascii')
    print(json.dumps(dict(status=report['status'], role=args.role, receipt=str(work / 'image.json'))))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
