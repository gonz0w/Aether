#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Measure two pinned Toybox applets with the existing package helper providers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import re
import struct
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_tools import run_tool


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()



def apply_hash_patch(tree, run):
    """Only the selected builtin SHA source; archive and other applets stay exact."""
    source = tree / 'lib/hash.c'
    patch = HERE / 'sha256-read-error.patch'
    expected = dict(before_sha256='38dac9744df94223f789998eb103873d3831cd4d759381cf00895ebf7e90ff95', after_sha256='5909c0d8b76580dff7b5746b84c6635a7fb5d8003fe0fe9063c03d3d16dcc107', patch_sha256='9cf739236d2661b8e14e37da024b715b19d6eefca2668e7e9b41cea3dfbccb96')
    if sha(source) != expected['before_sha256'] or sha(patch) != expected['patch_sha256']:
        raise ValueError('selected SHA read-error patch input changed')
    patch_tool = Path('/usr/bin/patch')
    if sha(patch_tool) != '095358520e36285ea9f57b2bd24219cb8ee9e80f9dc58bcd6074b8c5e9ba1c7d':
        raise ValueError('existing pinned patch utility changed')
    run([patch_tool, '-p1', '--batch', '--forward', '-i', patch], tree,
        {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
    if sha(source) != expected['after_sha256']:
        raise ValueError('selected SHA read-error patch output changed')
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('sdk', 'archive', 'tools-lock', 'work'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--applet', choices=('dirname', 'sha256sum'), help='build only the affected provider')
    args = parser.parse_args()
    work = args.work.resolve()
    if not work.is_relative_to(ROOT / 'userland/build'):
        parser.error('work must be a fresh directory under userland/build')
    work.mkdir(mode=0o700)
    (work / 'tmp').mkdir()
    report = dict(scope='target build fit only; no native execution', commands=[], candidates={})

    def save():
        (work / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')

    def run(argv, cwd, env):
        argv = list(map(str, argv))
        label = f'{len(report["commands"]):03d}-{Path(argv[0]).name}'
        row = dict(argv=argv, cwd=str(cwd), log=label + '.log', status='running')
        report['commands'].append(row)
        save()
        try:
            result = run_tool(argv, dict(env, TMPDIR=str(work / 'tmp')), work / row['log'],
                              timeout=180, limit=4 * 1024 * 1024, cwd=cwd)
        except Exception:
            row['status'] = 'failed'
            save()
            raise
        row['status'] = 'passed'
        save()
        return result

    try:
        lock = json.loads(args.tools_lock.read_text())['tools']
        tools = {name: Path(lock[name]['path']) for name in ('clang', 'lld', 'ar', 'ranlib', 'nm', 'objdump', 'objcopy', 'zig')}
        for name, path in tools.items():
            if sha(path) != lock[name]['sha256']:
                raise ValueError('tool differs from supplied lock: ' + name)
        source = json.loads((HERE.parent / 'toybox-reference/source.lock.json').read_text())
        if sha(args.archive) != source['sha256']:
            raise ValueError('Toybox archive differs from source pin')
        gsed = json.loads((HERE.parent / 'toybox-reference/host-tools.lock.json').read_text())['gsed']
        if sha(Path(gsed['path'])) != gsed['sha256']:
            raise ValueError('generator sed differs from existing pin')
        sdk = args.sdk.resolve()
        sdk_receipt = json.loads((sdk / 'sdk.json').read_text())
        for name, expected in sdk_receipt['members'].items():
            if sha(sdk / 'stage/usr' / name) != expected:
                raise ValueError('guarded SDK changed: ' + name)
        report.update(source=source, tools={name: lock[name] for name in tools}, gsed=gsed,
                      sdk_receipt_sha256=sha(sdk / 'sdk.json'), sdk_stage_sha256=sdk_receipt['sdk_stage_sha256'],
                      consumer_sha256=sha(ROOT / 'pkg-mgr/mk/verify-metadata.sh'),
                      builder_sha256=sha(Path(__file__)))
        env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}
        host_sdk = run(['/usr/bin/xcrun', '--show-sdk-path'], work, env).decode().splitlines()[-1]
        if not Path(host_sdk).is_dir():
            raise ValueError('host generator SDK path is unavailable')
        # Use the unchanged current helper builder, including its actual stdio,
        # process startup, FILE binding, finalizer and memory providers.
        spec = importlib.util.spec_from_file_location('r1_source', ROOT / 'userland/experiments/filesystem-service/r1-zsh-source.py')
        r1 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(r1)
        r1.BUILD, r1.SDK, r1.TOOLS = work, sdk, tools
        r1.LLVM, r1.LLD, r1.run = tools['clang'].parent, tools['lld'], run
        profile = dict(filesystem=True, external=True, home_redirection=True, login_startup=True,
                       home_cwd=True, home_cwd_exec=True, operator_note=True)
        baseline = r1.build_helper_profile('provider-baseline', profile, sdk / 'musl-1.2.6', work,
                                          sdk / 'stage/usr/lib', sdk / 'stage/usr/include', bytecount=True)
        report['baseline'] = dict(bytes=baseline.stat().st_size, sha256=sha(baseline))
        provider = baseline.parent / 'providers'
        providers = sorted(provider.glob('*.o'))
        # The exact helper link lists _Fork separately; glob includes it once.
        wraps = ['--wrap=' + name for name in ('main', '_exit', '_Exit', 'getuid', 'geteuid',
                                               'getgid', 'getegid', 'access', 'getcwd', 'chdir')]
        lib = sdk / 'stage/usr/lib'
        common = [str(tools['clang']), '--no-default-config', '--target=x86_64-linux-musl',
                  '-nostdinc', '-isystem', str(sdk / 'stage/usr/include'), '-Oz',
                  '-ffreestanding', '-fno-builtin', '-fstack-protector-strong',
                  '-ffunction-sections', '-fdata-sections', '-fstack-usage',
                  '-funsigned-char', '-fno-strict-aliasing', '-Werror=implicit-function-declaration',
                  '-Wno-pointer-sign', '-Wno-string-plus-int', '-Wno-invalid-source-encoding',
                  '-ffile-prefix-map=' + str(ROOT) + '=/src/aether',
                  '-ffile-prefix-map=' + str(work) + '=/build/aether']
        host = [str(tools['clang']), '--no-default-config', '--target=arm64-apple-macos',
                '-isysroot', host_sdk]
        hostcc = work / 'hostcc'
        hostcc.write_text('#!/bin/sh\nexec ' + shlex.join(host) + ' "$@"\n')
        hostcc.chmod(0o755)
        targetcc = work / 'targetcc'
        targetcc.write_text('#!/bin/sh\nexec ' + shlex.join(common) + ' "$@"\n')
        targetcc.chmod(0o755)
        view = work / 'kernel-view'
        view.mkdir()
        for name in ('native_elf.zig', 'native_launch.zig', 'arch'):
            (view / name).symlink_to(ROOT / 'kernel' / name)
        (view / 'facade.zig').write_text('pub const elf=@import("native_elf.zig");\n'
                                       'pub const launch=@import("native_launch.zig");\n')
        for applet in (args.applet,) if args.applet else ('dirname', 'sha256sum'):
            case = work / applet
            case.mkdir()
            with tarfile.open(args.archive) as archive:
                archive.extractall(case, filter='data')
            tree = case / ('toybox-' + source['version'])
            if applet == 'sha256sum':
                report['sha256_read_error_patch'] = apply_hash_patch(tree, run)
            config = HERE / ('miniconfig-' + applet)
            selected = dict(env, CC=str(targetcc), HOSTCC=str(hostcc), CPUS='2',
                            SED=gsed['path'], VERSION=source['version'], NOSTRIP='1', NOBUILD='1',
                            KCONFIG_ALLCONFIG=str(config), KCONFIG_CONFIG='.config',
                            GENDIR='generated', UNSTRIPPED=str(case / 'generators'),
                            OUTNAME=str(case / 'not-built'), CFLAGS='',
                            LDOPTIMIZE='-Wl,--gc-sections', LDFLAGS='-static')
            run(['/bin/bash', 'scripts/genconfig.sh', '-n'], tree, selected)
            generated = tree / '.config'
            text = generated.read_text()
            if text.splitlines().count('CONFIG_TOYBOX=y') != 1:
                raise ValueError('standalone hidden TOYBOX anchor changed')
            generated.write_text(text.replace('CONFIG_TOYBOX=y', '# CONFIG_TOYBOX is not set'))
            run(['/bin/bash', 'scripts/make.sh'], tree, selected)
            active = [line for line in generated.read_text().splitlines() if line.endswith('=y')]
            if 'CONFIG_TOYBOX_LIBCRYPTO=y' in active:
                raise ValueError('selected SHA patch requires the builtin hash implementation')
            unexpected = [line for line in active if not line.startswith(('CONFIG_' + applet.upper() + '=', 'CONFIG_TOYBOX_', 'CONFIG_IS_'))]
            if unexpected:
                raise ValueError('unselected applets: ' + str(unexpected))
            # Preprocess the actual applet table, rather than infer selection.
            table = case / 'table.c'
            table.write_text('#include "generated/config.h"\n#define NEWTOY(name,...) APPLET(name)\n#define OLDTOY(name,...) APPLET(name)\n#include "generated/newtoys.h"\n')
            effective = run([*common, '-I' + str(tree), '-E', '-P', table], tree, env).decode().strip()
            if effective != 'APPLET(' + applet + ')':
                raise ValueError('unexpected effective applet table: ' + effective)
            source_files = [tree / 'main.c', tree / ('toys/posix/dirname.c' if applet == 'dirname' else 'toys/lsb/md5sum.c'),
                            *sorted((tree / 'lib').glob('*.c'))]
            objects = []
            for number, path in enumerate(source_files):
                obj = case / (f'{number:02d}-' + path.stem + '.o')
                run([*common, '-I' + str(tree), '-DTOYBOX_VERSION="0.8.14"', '-c', path, '-o', obj], tree, env)
                objects.append(obj)
            binary = case / (applet + '.elf')
            run([tools['lld'], '-static', '--no-undefined', '--gc-sections', '-z', 'noexecstack',
                 *wraps, '-Map=' + str(case / 'target.map'), lib / 'crt1.o', lib / 'crti.o',
                 *objects, *providers, lib / 'libc.a', lib / 'crtn.o', '-o', binary], case, env)
            checker = case / 'check.zig'
            checker.write_text('''const std=@import("std");
const kernel=@import("kernel");
pub fn main() !void {
    const image=try kernel.elf.parseApplication(@embedFile("APPLET.elf"));
    try kernel.launch.layout(&image);
    const pages=try kernel.launch.backingPages(&image);
    std.debug.print("{{\\"backing_pages\\":{d},\\"segments\\":{d},\\"stack_bytes\\":65536}}\\n", .{pages,image.count});
}
'''.replace('APPLET', applet))
            geometry = run([tools['zig'], 'run', '-OReleaseSafe', '--cache-dir', work / 'cache',
                            '--global-cache-dir', work / 'global', '--dep', 'kernel',
                            '-Mroot=' + str(checker), '-Mkernel=' + str(view / 'facade.zig')], case, env)
            undefined = run([tools['nm'], '--undefined-only', '--extern-only', binary], case, env).decode().strip()
            if undefined:
                raise ValueError('linked candidate has unresolved symbols: ' + undefined)
            imports = run([tools['nm'], '--undefined-only', *objects], case, env).decode()
            (case / 'object-imports.txt').write_text(imports)
            disassembly = run([tools['objdump'], '-d', '--no-show-raw-insn', '--x86-asm-syntax=intel', binary], case, env).decode()
            if re.search(r'^\s*[0-9a-f]+:\s+syscall\b', disassembly, re.M):
                raise ValueError('Linux syscall instruction in linked native candidate')
            symbols = run([tools['nm'], '--defined-only', '--format=posix', binary], case, env).decode()
            linked = {line.split()[0] for line in symbols.splitlines()
                      if len(line.split()) > 1 and line.split()[1] in ('t', 'T')}
            row = dict(bytes=binary.stat().st_size, sha256=sha(binary), active_config=active,
                       effective_table=effective, config_sha256=sha(generated),
                       geometry=json.loads(geometry), undefined_symbols=[], syscall_instruction_sites=0)
            frames = []
            for path in (*case.glob('*.su'), *provider.glob('*.su')):
                for line in path.read_text().splitlines():
                    identity, size, kind = line.split('\t')
                    name = identity.rsplit(':', 1)[-1]
                    if name in linked:
                        frames.append(dict(function=name, bytes=int(size), kind=kind))
            row['largest_linked_source_local_frames'] = sorted(frames, key=lambda item: item['bytes'], reverse=True)[:12]
            row['stack_limitations'] = 'Source local frames only; no complete musl/indirect-call stack or heap peak proof'
            stripped = case / (applet + '.stripped.elf')
            run([tools['objcopy'], '--strip-all', binary, stripped], case, env)
            before, after = binary.read_bytes(), stripped.read_bytes()
            offset = struct.unpack_from('<Q', before, 32)[0]
            count = struct.unpack_from('<H', before, 56)[0]
            changed = []
            for number in range(count):
                a = struct.unpack_from('<IIQQQQQQ', before, offset + number * 56)
                b = struct.unpack_from('<IIQQQQQQ', after, offset + number * 56)
                if a != b:
                    raise ValueError('strip changed a program header')
                if a[0] in (1, 7):
                    changes = [a[2] + i for i in range(a[5]) if before[a[2] + i] != after[a[2] + i]]
                    if a[0] == 7 and changes:
                        raise ValueError('strip changed TLS bytes')
                    changed.extend(changes)
            if any(at not in (*range(40, 48), *range(58, 64)) for at in changed):
                raise ValueError('strip changed loaded bytes outside section metadata in ELF header')
            checker.write_text(checker.read_text().replace(applet + '.elf', applet + '.stripped.elf'))
            stripped_geometry = run([tools['zig'], 'run', '-OReleaseSafe', '--cache-dir', work / 'cache',
                                     '--global-cache-dir', work / 'global', '--dep', 'kernel',
                                     '-Mroot=' + str(checker), '-Mkernel=' + str(view / 'facade.zig')], case, env)
            if json.loads(stripped_geometry) != row['geometry']:
                raise ValueError('strip changed actual parser geometry')
            row['stripped'] = dict(bytes=stripped.stat().st_size, sha256=sha(stripped),
                                   intake_48k_fits=stripped.stat().st_size <= 49152,
                                   program_headers_identical=True, tls_bytes_identical=True,
                                   load_byte_changes_only_section_metadata_at=changed)
            report['candidates'][applet] = row
            save()
        report['status'] = 'linked; native runtime unsupported by current package bindings'
        save()
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = type(error).__name__ + ': ' + str(error)
        save()
        raise
    print(json.dumps({name: dict(bytes=row['bytes'], stripped=row['stripped'],
                                     geometry=row['geometry']) for name, row in report['candidates'].items()}, indent=2))


if __name__ == '__main__':
    main()
