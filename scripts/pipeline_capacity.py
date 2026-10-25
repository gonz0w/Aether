# SPDX-License-Identifier: BSD-2-Clause
"""Private five-worker capacity witness; not a shell or release acceptance test."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import tarfile

from evidence import compact_run
from deps import ROOT
from native_smoke import run


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def suite(sdk, lock, selected_case=None):
    sdk = Path(sdk).resolve()
    lock = Path(lock).resolve()
    tools = json.loads(lock.read_text())['tools']
    for name in ('clang', 'lld', 'nm'):
        if sha(Path(tools[name]['path']).resolve()) != tools[name]['sha256']:
            raise RuntimeError('tool digest mismatch: ' + name)
    receipt = json.loads((sdk / 'evidence.json').read_text())
    if sha(sdk / 'stage/usr/lib/libc.a') != receipt['libc_archive_sha256']:
        raise RuntimeError('libc digest mismatch')
    output = Path(tempfile.mkdtemp(prefix='pipeline-capacity-', dir=ROOT / 'zig-out'))
    # Finder metadata is not a build input and can change while QEMU runs.
    sources = {str(path.relative_to(ROOT)): sha(path) for parent in ('kernel', 'user', 'scripts')
               for path in (ROOT / parent).rglob('*') if path.is_file() and '__pycache__' not in path.parts
               and path.name != '.DS_Store'}
    sources['build.zig'] = sha(ROOT / 'build.zig')
    report = dict(status='incomplete', sources=sources, tools=tools, tools_lock_sha256=sha(lock),
                  libc_receipt_sha256=sha(sdk / 'evidence.json'), commands=[], cases=[])
    if selected_case is not None:
        report['selected_case'] = selected_case
    print('[RUNNING] Evidence:', output, flush=True)

    def save():
        (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')

    def command(arguments, name):
        report['commands'].append(arguments)
        save()
        with (output / (name + '.log')).open('wb') as log:
            subprocess.run(arguments, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)

    try:
        cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
              '--sysroot=' + str(sdk / 'empty-root')]
        flags = ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding',
                 '-fno-builtin', '-fstack-protector-strong', '-nostdinc', '-isystem', str(sdk / 'stage/usr/include')]
        for name, source in [('worker', 'user/native-capacity/worker.c'), ('adapter', 'user/native-memory/adapter.c')]:
            command(cc + flags + ['-c', source, '-o', str(output / (name + '.o'))], name)
        lib = sdk / 'stage/usr/lib'
        image = output / 'worker.elf'
        command(cc + ['-fuse-ld=' + tools['lld']['path'], '-nostdlib', '-static', '-Wl,-z,noexecstack',
                      '-Wl,--no-undefined', str(lib / 'crt1.o'), str(lib / 'crti.o'),
                      str(output / 'worker.o'), str(output / 'adapter.o'), str(lib / 'libc.a'),
                      str(lib / 'crtn.o'), '-o', str(image)], 'worker-link')
        owner = output / 'owner.raw'
        command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=s',
                 '-C', 'panic=abort', '-C', 'relocation-model=static', '-C', 'lto=fat', '-C', 'codegen-units=1',
                 '-C', 'link-arg=-Tuser/native-connections/large-linker.ld', '-C', 'link-arg=--oformat=binary',
                 'user/native-capacity/owner.rs', '-o', str(owner)], 'owner')
        worker = image.read_bytes()
        code = owner.read_bytes()
        assert 0 < len(code) <= 16384
        header = struct.pack('<8sIIIIQ', b'AENMX004', len(worker), len(worker), len(worker), len(code), 0)
        entropy = b''.join(bytes([slot + 1]) * 16 for slot in range(5))
        payload = header + entropy + worker * 3 + code
        wrong_entropy = bytearray(payload)
        wrong_entropy[96:112] = bytes(16)
        cases = [
            ('five-workers', payload, True, None, ()),
            ('wrong-entropy', bytes(wrong_entropy), True, b'native C profile rejected',
             (b'NATIVE terminal slot=4 generation=1 kind=1 detail=73', b'NATIVE supervisor result=2607 reclaimed=0')),
            ('short-header', payload[:80] + payload[112:], True, b'invalid launch envelope', ()),
            ('old-envelope-enabled', b'AENMX003' + payload[8:], True, b'native C profile rejected', ()),
            ('new-envelope-disabled', payload, False, b'native C profile rejected', ()),
        ]
        # Version005 grows only the private supervisor code ceiling; old004 stays bounded.
        def wide_payload(owner_code, magic=b'AENMX005'):
            return (struct.pack('<8sIIIIQ', magic, len(worker), len(worker), len(worker), len(owner_code), 0)
                    + entropy + worker * 3 + owner_code)

        for length in (16385, 20481, 24576):
            cases.append(('five-workers-wide-' + str(length), wide_payload(code.ljust(length, b'\0')),
                          True, None, ()))
        wide = wide_payload(code.ljust(24576, b'\0'))
        cases += [
            ('wide-disabled', wide, False, b'native C profile rejected', ()),
            ('wide-over-limit', wide_payload(code.ljust(24577, b'\0')), True, b'invalid launch envelope', ()),
            ('wide-truncated', wide[:-1], True, b'invalid launch envelope', ()),
            ('old-owner-over-limit', wide_payload(code.ljust(16385, b'\0'), b'AENMX004'),
             True, b'invalid launch envelope', ()),
        ]
        # Tiny hostile supervisor programs test the added mapping, not its lifecycle.
        for label, address, tail, fault in [
            ('wide-code-write', 0x405000, b'\xc6\x00\x00\x0f\x0b', b'vector=14 rip=40000a error=7'),
            ('wide-code-execute', 0x405000, b'\xff\xe0', b'vector=6 rip=405000 error=0'),
            ('wide-stack-execute', 0x800000, b'\xff\xe0', b'vector=14 rip=800000 error=15'),
            ('wide-unmapped-execute', 0x406000, b'\xff\xe0', b'vector=14 rip=406000 error=14'),
        ]:
            probe = bytearray(24576)
            prefix = b'\x48\xb8' + struct.pack('<Q', address) + tail
            probe[:len(prefix)] = prefix
            probe[20480:20482] = b'\x0f\x0b'
            cases.append((label, wide_payload(bytes(probe)), True, b'native supervisor terminated',
                          (b'NATIVE fault ' + fault,)))
        pipe_image = output / 'pipe-worker.elf'
        pipe_object = output / 'pipe-worker.o'
        command(cc + flags + ['-DPIPE_DISPATCH', '-c', 'user/native-capacity/worker.c', '-o', str(pipe_object)], 'pipe-worker')
        base_link = next(arguments for arguments in report['commands'] if str(image) in arguments)
        command([str(pipe_image) if value == str(image) else str(pipe_object) if value == str(output / 'worker.o')
                 else value for value in base_link], 'pipe-worker-link')
        base_owner = next(arguments for arguments in report['commands'] if str(owner) in arguments)
        pipe_worker = pipe_image.read_bytes()
        # ABI21 resource qualification only: this is not the composed dash session.
        session_images = {}
        for label, defines in [('session', ['-DSESSION_LIFETIME']),
                               ('session-stale', ['-DSESSION_LIFETIME', '-DSESSION_STALE_ID'])]:
            obj = output / (label + '-worker.o')
            elf = output / (label + '-worker.elf')
            command(cc + flags + defines + ['-c', 'user/native-capacity/worker.c', '-o', str(obj)], label + '-worker')
            command([str(elf) if value == str(image) else str(obj) if value == str(output / 'worker.o')
                     else value for value in base_link], label + '-worker-link')
            session_images[label] = elf.read_bytes()
        session_owners = {}
        for label, configs in [('session', ['--cfg', 'session_lifetime']),
                               ('session-legacy', ['--cfg', 'session_lifetime', '--cfg', 'session_legacy'])]:
            raw = output / (label + '-owner.raw')
            args = [str(raw) if value == str(owner) else value for value in base_owner] + configs
            command(args, label + '-owner')
            linked = args.copy()
            raw_format = linked.index('link-arg=--oformat=binary')
            del linked[raw_format - 1:raw_format + 1]
            linked[linked.index(str(raw))] = str(output / (label + '-owner.elf'))
            command(linked, label + '-owner-link')
            session_owners[label] = raw.read_bytes()

        def session_payload(worker_code, owner_code, magic=b'AENMX007'):
            return (struct.pack('<8sIIIIQ', magic, len(worker_code), len(worker_code), len(worker_code), len(owner_code), 0)
                    + entropy + worker_code * 3 + owner_code)

        session = session_payload(session_images['session'], session_owners['session'])
        reserved_session = bytearray(session)
        reserved_session[24] = 1
        cases += [
            ('session-lifetime', session, True, None, ()),
            ('session-stale-identity', session_payload(session_images['session-stale'], session_owners['session']),
             True, b'native C profile rejected', (b'NATIVE supervisor result=2608 reclaimed=6',)),
            ('session-legacy-limit', session_payload(session_images['session'], session_owners['session-legacy'], b'AENMX005'),
             True, b'native C profile rejected', (b'NATIVE supervisor result=2603 reclaimed=6',)),
            ('session-disabled', session, False, b'native C profile rejected', ()),
            ('session-truncated', session[:-1], True, b'invalid launch envelope', ()),
            ('session-reserved', bytes(reserved_session), True, b'invalid launch envelope', ()),
            ('session-old-owner', session_payload(session_images['session'], code), True,
             b'native C profile rejected', (b'NATIVE supervisor result=2600 reclaimed=0',)),
            ('session-owner-over-limit', session_payload(session_images['session'], session_owners['session'].ljust(24577, b'\0')),
             True, b'invalid launch envelope', ()),
        ]
        stop_image = output / 'stop-worker.elf'
        stop_object = output / 'stop-worker.o'
        command(cc + flags + ['-DPIPE_DISPATCH', '-DPIPE_STOP_REQUEST', '-c',
                             'user/native-capacity/worker.c', '-o', str(stop_object)], 'stop-worker')
        command([str(stop_image) if value == str(image) else str(stop_object) if value == str(output / 'worker.o')
                 else value for value in base_link], 'stop-worker-link')
        archive_path = sdk.parent / 'musl-audit/musl-1.2.6.tar.gz'
        assert sha(archive_path) == receipt['source_sha256']
        fork_root = output / 'public-fork'
        fork_root.mkdir()
        with tarfile.open(archive_path) as archive:
            for member in archive.getmembers():
                relative = member.name.removeprefix('musl-1.2.6/')
                selected = (relative == 'COPYRIGHT' or relative in ('src/process/fork.c', 'src/process/_Fork.c', 'src/process/waitpid.c', 'src/linux/wait3.c', 'src/linux/wait4.c') or
                            relative.endswith('.h') and relative.startswith(('src/internal/', 'src/include/', 'include/', 'arch/x86_64/', 'arch/generic/')))
                if not member.isfile() or not selected:
                    continue
                assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
                target = fork_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        assert sha(archive_path) == receipt['source_sha256']
        report['fork_source_sha256'] = sha(archive_path)
        report['fork_inputs'] = {str(p.relative_to(fork_root)): sha(p) for p in fork_root.rglob('*') if p.is_file()}
        (fork_root / 'syscall_arch.h').write_text((fork_root / 'arch/x86_64/syscall_arch.h').read_text().replace('"syscall"', '"int $0x81"').replace('"a"(n)', '"a"(n + 0x10000)'))
        original = (fork_root / 'src/process/_Fork.c').read_text()
        assert original.count('ret = __syscall(SYS_fork);') == 1
        patched = 'long __aether_fork_stage(void);\n' + original.replace('ret = __syscall(SYS_fork);', 'ret = __aether_fork_stage();')
        (fork_root / '_Fork.c').write_text(patched)
        assert patched.count('__post_Fork(ret);') == 1
        (fork_root / '_Fork-no-repair.c').write_text(patched.replace('__post_Fork(ret);', 'if (ret) __post_Fork(ret);'))
        private = [item for part in ('src/internal', 'arch/x86_64', 'arch/generic') for item in ('-isystem', str(fork_root / part))]
        fork_flags = ['-include', str(fork_root / 'src/include/features.h'), '-I', str(fork_root / 'src/include'), '-I', str(fork_root), *private, '-Dhidden=__attribute__((__visibility__("hidden")))']
        upstream_flags = [v for v in flags if v not in ('-Wextra', '-Werror')]
        for name, source in [('fork', fork_root / 'src/process/fork.c'), ('_Fork', fork_root / '_Fork.c'), ('_Fork-no-repair', fork_root / '_Fork-no-repair.c')]:
            command(cc + upstream_flags + fork_flags + ['-c', str(source), '-o', str(fork_root / (name + '.o'))], 'public-' + name)
        command(cc + flags + private + ['-Dhidden=__attribute__((__visibility__("hidden")))', '-DREBIND_LIBC_REPAIR', '-c', 'user/native-connections/rebind.c', '-o', str(fork_root / 'rebind.o')], 'public-rebind')
        wait_source = (fork_root / 'src/process/waitpid.c').read_text()
        assert wait_source.count('sys_wait4_cp(pid, status, options, 0)') == 1
        wait_path = fork_root / 'waitpid.c'
        wait_path.write_text('long __aether_waitpid(int, int *, int);\n' + wait_source.replace('sys_wait4_cp(pid, status, options, 0)', '__syscall_ret(__aether_waitpid(pid, status, options))'))
        command(cc + upstream_flags + fork_flags + ['-include', str(fork_root / 'src/internal/syscall.h'), '-c', str(wait_path), '-o', str(fork_root / 'waitpid.o')], 'public-waitpid')
        wait4_source = (fork_root / 'src/linux/wait4.c').read_text()
        assert wait4_source.count('__sys_wait4(pid, status, options, dest)') == 1 and wait4_source.count('\n\tint r;') == 1
        (fork_root / 'wait4.c').write_text('long __aether_waitpid(int, int *, int);\n' + wait4_source.replace('__sys_wait4(pid, status, options, dest)', '__aether_waitpid(pid, status, options)').replace('\n\tint r;', '\n\tif (ru) return __syscall_ret(-ENOTSUP);\n\tint r;'))
        for name, source in [('wait3', fork_root / 'src/linux/wait3.c'), ('wait4', fork_root / 'wait4.c')]:
            command(cc + upstream_flags + fork_flags + ['-include', str(fork_root / 'src/internal/syscall.h'), '-c', str(source), '-o', str(fork_root / (name + '.o'))], 'public-' + name)
        libc_adapter = output / 'libc-adapter.o'
        command(cc + flags + ['-D__aether_io=capacity_memory_io', '-c', 'user/native-memory/adapter.c',
                             '-o', str(libc_adapter)], 'libc-adapter')
        early_images = {}
        for label, defines in [('early', []), ('early-exit', ['-DPIPE_READER_EXIT']), ('copy', ['-DPIPE_COPY']), ('exec', ['-DPIPE_COPY', '-DPIPE_EXEC']),
                               ('replacement', ['-DPIPE_REPLACEMENT']), ('libc-source', ['-DPIPE_COPY', '-DPIPE_EXEC', '-DPIPE_LIBC']),
                               ('libc', []), ('stdout', ['-DPIPE_STDOUT']), ('inherited-output', ['-DPIPE_STDOUT', '-DPIPE_INHERITED_OUTPUT']), ('stdio', ['-DPIPE_STDOUT', '-DPIPE_INHERITED_OUTPUT', '-DPIPE_STDIO']), ('fork-source', ['-DPIPE_COPY', '-DPIPE_EXEC', '-DPIPE_LIBC', '-DPIPE_PUBLIC_FORK']),
                               ('fork-no-repair', ['-DPIPE_COPY', '-DPIPE_EXEC', '-DPIPE_LIBC', '-DPIPE_PUBLIC_FORK']),
                               ('live', []), ('live-bad', ['-DPIPE_LIVE_BAD_SNAPSHOT']), ('parent', ['-DPIPE_PARENT_OPS']), ('interleave', ['-DPIPE_PARENT_OPS', '-DPIPE_INTERLEAVE']), ('wait-any', ['-DPIPE_PARENT_OPS', '-DPIPE_INTERLEAVE', '-DPIPE_WAIT_ANY']), ('inherit-source', ['-DPIPE_PARENT_OPS', '-DPIPE_INTERLEAVE', '-DPIPE_WAIT_ANY', '-DPIPE_INHERITED_OUTPUT']), ('stdio-source', ['-DPIPE_PARENT_OPS', '-DPIPE_INTERLEAVE', '-DPIPE_WAIT_ANY', '-DPIPE_INHERITED_OUTPUT', '-DPIPE_STDIO']), ('exec-source', ['-DPIPE_PARENT_OPS', '-DPIPE_INTERLEAVE', '-DPIPE_WAIT_ANY', '-DPIPE_INHERITED_OUTPUT', '-DPIPE_STDIO', '-DPIPE_EXEC_REQUEST'])]:
            early_image = output / (label + '-worker.elf')
            early_object = output / (label + '-worker.o')
            command(cc + flags + ['-DPIPE_DISPATCH', *([] if label in ('copy', 'exec', 'replacement', 'libc-source', 'libc', 'stdout', 'inherited-output', 'stdio', 'fork-source', 'fork-no-repair', 'live', 'live-bad', 'parent', 'interleave', 'wait-any', 'inherit-source', 'stdio-source', 'exec-source') else ['-DPIPE_EARLY_READER']), *defines, '-c',
                                 'user/native-capacity/live-worker.c' if label in ('live', 'live-bad', 'parent', 'interleave', 'wait-any', 'inherit-source', 'stdio-source', 'exec-source') else 'user/native-capacity/libc-worker.c' if label in ('libc', 'stdout', 'inherited-output', 'stdio') else 'user/native-capacity/worker.c', '-o', str(early_object)], label + '-worker')
            link = [str(early_image) if value == str(image) else str(early_object) if value == str(output / 'worker.o')
                    else str(libc_adapter) if label in ('libc', 'stdout', 'inherited-output', 'stdio', 'live', 'live-bad', 'parent', 'interleave', 'wait-any', 'inherit-source', 'stdio-source', 'exec-source') and value == str(output / 'adapter.o') else value for value in base_link]
            if label in ('fork-source', 'fork-no-repair', 'live', 'live-bad', 'parent', 'interleave', 'wait-any', 'inherit-source', 'stdio-source', 'exec-source'):
                at = link.index(str(lib / 'libc.a'))
                link[at:at] = [str(fork_root / 'fork.o'), str(fork_root / ('_Fork-no-repair.o' if label == 'fork-no-repair' else '_Fork.o')), str(fork_root / 'rebind.o')]
            if label in ('parent', 'interleave', 'wait-any', 'inherit-source', 'stdio-source', 'exec-source'):
                link.insert(link.index(str(lib / 'libc.a')), str(fork_root / 'waitpid.o'))
            if label in ('wait-any', 'inherit-source', 'stdio-source', 'exec-source'):
                at = link.index(str(lib / 'libc.a'))
                link[at:at] = [str(fork_root / 'wait3.o'), str(fork_root / 'wait4.o')]
            command(link, label + '-worker-link')
            early_images[label] = early_image.read_bytes()
        # Reuse immutable upstream objects; this calls a builtin, not dash main.
        dash = ROOT / 'user/native-command/dash-inputs'
        objects = json.loads((dash / 'libc-imports.json').read_text())['objects']
        for name, digest in objects.items():
            if sha(dash / name) != digest:
                raise RuntimeError('dash object drift: ' + name)
        report['dash_objects'] = objects
        helper = ROOT / 'user/native-command/dash-helper-inputs'
        helper_pin = json.loads((helper / 'pin.json').read_text())
        if sha(helper / 'helper.c') != helper_pin['sha256']:
            raise RuntimeError('consumer helper source drift')
        report['consumer_helper'] = helper_pin
        consumer_obj = output / 'consumer-helper.o'
        command(cc + flags + ['-Dmain=consumer_helper_main', '-c', str(helper / 'helper.c'),
                              '-o', str(consumer_obj)], 'consumer-helper')
        for label in ('dash', 'dash-byte', 'autonomous-replacement', 'stop-replacement', 'remap-replacement', 'helper-replacement', 'consumer-replacement', 'consumer-skip-replacement', 'consumer-parent-replacement', 'consumer-early-replacement'):
            obj = output / (label + '-worker.o')
            target = output / (label + '-worker.elf')
            command(cc + flags + ['-DPIPE_STDOUT', '-DPIPE_INHERITED_OUTPUT', '-DPIPE_STDIO',
                                 '-DPIPE_DASH_PRINTF', '-Dmain=__wrap_main',
                                 *(['-DPIPE_AUTONOMOUS'] if label in ('autonomous-replacement', 'stop-replacement', 'remap-replacement', 'helper-replacement', 'consumer-replacement', 'consumer-skip-replacement', 'consumer-parent-replacement', 'consumer-early-replacement') else []),
                                 *(['-DPIPE_DASH_BAD_BYTE'] if label == 'dash-byte' else []),
                                 *(['-DPIPE_OVERLAP_STOP'] if label == 'stop-replacement' else []),
                                 *(['-DPIPE_PREEXEC_REMAP'] if label in ('remap-replacement', 'helper-replacement', 'consumer-replacement', 'consumer-skip-replacement', 'consumer-parent-replacement', 'consumer-early-replacement') else []),
                                 *(['-DPIPE_HELPER_ARGS'] if label in ('helper-replacement', 'consumer-replacement', 'consumer-skip-replacement', 'consumer-parent-replacement', 'consumer-early-replacement') else []),
                                 *(['-DPIPE_CONSUMER_HELPER'] if label.startswith('consumer-') else []),
                                 *(['-DPIPE_SHELL_EARLY'] if label == 'consumer-early-replacement' else []),
                                 *(['-DPIPE_CONSUMER_SKIP'] if label == 'consumer-skip-replacement' else []),
                                 *(['-DPIPE_DASH_PARENT'] if label in ('consumer-parent-replacement', 'consumer-early-replacement') else []),
                                 '-c', 'user/native-capacity/libc-worker.c', '-o', str(obj)], label + '-worker')
            link = [str(target) if value == str(image) else str(obj) if value == str(output / 'worker.o')
                    else str(libc_adapter) if value == str(output / 'adapter.o') else value for value in base_link]
            at = link.index(str(lib / 'libc.a'))
            link[at:at] = ([str(consumer_obj)] if label.startswith('consumer-') else
                           [str(dash / name) for name in sorted(objects)])
            command(link + ['-Wl,--wrap=main'], label + '-worker-link')
            early_images[label] = target.read_bytes()
        pipeline_inputs = ROOT / 'user/native-command/dash-pipeline-inputs'
        pipeline_pin = json.loads((pipeline_inputs / 'pin.json').read_text())
        if sha(pipeline_inputs / pipeline_pin['script']) != pipeline_pin['sha256']:
            raise RuntimeError('consumer pipeline script drift')
        report['consumer_pipeline'] = pipeline_pin
        pipeline_script = (pipeline_inputs / pipeline_pin['script']).read_text()
        early_pin = json.loads((pipeline_inputs / 'early-pin.json').read_text())
        if sha(pipeline_inputs / early_pin['script']) != early_pin['sha256']:
            raise RuntimeError('consumer early-reader script drift')
        report['consumer_early_reader'] = early_pin
        early_script = (pipeline_inputs / early_pin['script']).read_text()
        for label in ('builtin', 'builtin-byte', 'autonomous', 'wait-io', 'wait-probes', 'stop-probes', 'preexec-io', 'remap', 'remap-cloexec', 'remap-alias', 'remap-helper', 'remap-helper-wire', 'remap-helper-natural', 'remap-helper-natural-main', 'remap-helper-natural-main-byte', 'remap-helper-natural-main-fds', 'remap-helper-natural-main-fds-alias', 'remap-helper-natural-main-fds-parent', 'remap-helper-natural-main-fds-parent-serial', 'remap-helper-natural-main-fds-parent-serial-byte', 'remap-helper-natural-main-fds-parent-serial-grant', 'remap-helper-natural-main-fds-parent-byte', 'remap-helper-natural-main-fds-parent-alias', 'remap-helper-natural-main-fds-parent-env', 'remap-helper-natural-main-fds-parent-early', 'remap-helper-natural-main-fds-parent-early-errno', 'remap-helper-natural-main-fds-parent-no-signals'):
            obj = output / (label + '-worker.o')
            target = output / (label + '-worker.elf')
            command(cc + flags + ['-DPIPE_PARENT_OPS', '-DPIPE_INTERLEAVE', '-DPIPE_WAIT_ANY',
                                 '-DPIPE_INHERITED_OUTPUT', '-DPIPE_STDIO', '-DPIPE_EXEC_REQUEST',
                                 '-DPIPE_COPIED_BUILTIN', '-Dmain=__wrap_main',
                                 *(['-DPIPE_WAIT_PROBES'] if label in ('wait-probes', 'stop-probes', 'preexec-io', 'remap', 'remap-cloexec', 'remap-alias', 'remap-helper', 'remap-helper-wire', 'remap-helper-natural', 'remap-helper-natural-main', 'remap-helper-natural-main-byte', 'remap-helper-natural-main-fds', 'remap-helper-natural-main-fds-alias', 'remap-helper-natural-main-fds-parent', 'remap-helper-natural-main-fds-parent-serial', 'remap-helper-natural-main-fds-parent-serial-byte', 'remap-helper-natural-main-fds-parent-serial-grant', 'remap-helper-natural-main-fds-parent-byte', 'remap-helper-natural-main-fds-parent-alias', 'remap-helper-natural-main-fds-parent-env', 'remap-helper-natural-main-fds-parent-early', 'remap-helper-natural-main-fds-parent-early-errno', 'remap-helper-natural-main-fds-parent-no-signals') else []),
                                 *(['-DPIPE_WAIT_IO'] if label in ('wait-io', 'wait-probes', 'stop-probes', 'preexec-io', 'remap', 'remap-cloexec', 'remap-alias', 'remap-helper', 'remap-helper-wire', 'remap-helper-natural', 'remap-helper-natural-main', 'remap-helper-natural-main-byte', 'remap-helper-natural-main-fds', 'remap-helper-natural-main-fds-alias', 'remap-helper-natural-main-fds-parent', 'remap-helper-natural-main-fds-parent-serial', 'remap-helper-natural-main-fds-parent-serial-byte', 'remap-helper-natural-main-fds-parent-serial-grant', 'remap-helper-natural-main-fds-parent-byte', 'remap-helper-natural-main-fds-parent-alias', 'remap-helper-natural-main-fds-parent-env', 'remap-helper-natural-main-fds-parent-early', 'remap-helper-natural-main-fds-parent-early-errno', 'remap-helper-natural-main-fds-parent-no-signals') else []),
                                 *(['-DPIPE_AUTONOMOUS'] if label in ('autonomous', 'wait-io', 'wait-probes', 'stop-probes', 'preexec-io', 'remap', 'remap-cloexec', 'remap-alias', 'remap-helper', 'remap-helper-wire', 'remap-helper-natural', 'remap-helper-natural-main', 'remap-helper-natural-main-byte', 'remap-helper-natural-main-fds', 'remap-helper-natural-main-fds-alias', 'remap-helper-natural-main-fds-parent', 'remap-helper-natural-main-fds-parent-serial', 'remap-helper-natural-main-fds-parent-serial-byte', 'remap-helper-natural-main-fds-parent-serial-grant', 'remap-helper-natural-main-fds-parent-byte', 'remap-helper-natural-main-fds-parent-alias', 'remap-helper-natural-main-fds-parent-env', 'remap-helper-natural-main-fds-parent-early', 'remap-helper-natural-main-fds-parent-early-errno', 'remap-helper-natural-main-fds-parent-no-signals') else []),
                                 *(['-DPIPE_DASH_BAD_BYTE'] if label.endswith('-byte') else []),
                                 *(['-DPIPE_OVERLAP_STOP'] if label == 'stop-probes' else []),
                                 *(['-DPIPE_PREEXEC_IO'] if label == 'preexec-io' or label.startswith('remap') else []),
                                 *(['-DPIPE_PREEXEC_REMAP'] if label.startswith('remap') else []),
                                 *(['-DPIPE_REMAP_CLOEXEC'] if label == 'remap-cloexec' else []),
                                 *(['-DPIPE_REMAP_ALIAS'] if label == 'remap-alias' else []),
                                 *(['-DPIPE_HELPER_ARGS'] if label.startswith('remap-helper') else []),
                                 *(['-DPIPE_HELPER_BAD_WIRE'] if label == 'remap-helper-wire' else []),
                                 *(['-DPIPE_WAIT_NATURAL'] if label.startswith('remap-helper-natural') else []),
                                 *(['-DPIPE_DASH_MAIN'] if label.startswith('remap-helper-natural-main') else []),
                                 *(['-DPIPE_NATURAL_FDS'] if '-main-fds' in label else []),
                                 *(['-DPIPE_NATURAL_ALIAS'] if label.endswith('-fds-alias') else []),
                                 *(['-DPIPE_DASH_PARENT', '-DAETHER_PIPELINE_SCRIPT=' + json.dumps(early_script if '-parent-early' in label else pipeline_script)] if '-fds-parent' in label else []),
                                 *(['-DPIPE_PARENT_SERIAL'] if '-parent-serial' in label else []),
                                 *(['-DPIPE_PARENT_BAD_BYTE'] if label.endswith('-parent-byte') else []),
                                 *(['-DPIPE_PARENT_ALIAS'] if label.endswith('-parent-alias') else []),
                                 *(['-DPIPE_SHELL_EARLY'] if '-parent-early' in label else []),
                                 *(['-DPIPE_PARENT_ENV'] if label.endswith('-parent-env') else []),
                                 '-c', 'user/native-capacity/live-worker.c', '-o', str(obj)], label + '-worker')
            link = [str(target) if value == str(image) else str(obj) if value == str(output / 'worker.o')
                    else str(libc_adapter) if value == str(output / 'adapter.o') else value for value in base_link]
            at = link.index(str(lib / 'libc.a'))
            link[at:at] = [str(dash / name) for name in sorted(objects)] + [
                str(fork_root / name) for name in ('fork.o', '_Fork.o', 'rebind.o', 'waitpid.o', 'wait3.o', 'wait4.o')]
            if label.startswith('remap-helper-natural-main'):
                main = ROOT / 'user/native-command/dash-main-inputs'
                main_pin = json.loads((main / 'pin.json').read_text())
                if sha(main / 'main.o') != main_pin['sha256']:
                    raise RuntimeError('native dash main object drift')
                report['dash_main'] = main_pin
                link[link.index(str(dash / 'obj/src/main.o'))] = str(main / 'main.o')
                link += ['-Wl,--wrap=_exit']
                if '-fds-parent' in label:
                    jobs = ROOT / 'user/native-command/dash-fork-inputs'
                    jobs_pin = json.loads((jobs / 'pin.json').read_text())
                    if sha(jobs / 'jobs.o') != jobs_pin['sha256']:
                        raise RuntimeError('native dash jobs object drift')
                    report['dash_jobs'] = jobs_pin
                    link[link.index(str(dash / 'obj/src/jobs.o'))] = str(jobs / 'jobs.o')
                if '-parent-serial' in label:
                    native_input = ROOT / 'user/native-command/dash-input-native'
                    input_pin = json.loads((native_input / 'pin.json').read_text())
                    if sha(native_input / 'input.o') != input_pin['sha256']:
                        raise RuntimeError('native dash input object drift')
                    report['dash_input'] = input_pin
                    link[link.index(str(dash / 'obj/src/input.o'))] = str(native_input / 'input.o')
            command(link + ['-Wl,--wrap=main'], label + '-worker-link')
            early_images[label] = target.read_bytes()
        report['owner_sizes'] = {'five-workers': len(code)}
        for label, config, failure in [('pipe-dispatch', None, None),
                                       ('pipe-wrong-route', 'pipeline_wrong_route', 2723),
                                       ('pipe-reapply', 'pipeline_reapply', 2726),
                                       ('pipe-stop-request', 'pipeline_stop_request', None),
                                       ('pipe-stop-reply', 'pipeline_stop_reply', None),
                                       ('pipe-keep-frame', 'pipeline_stop_request', 2724),
                                       ('pipe-early-reader', 'pipeline_early_reader', None),
                                       ('pipe-early-exit', 'pipeline_early_reader', None),
                                       ('pipe-wrong-errno', 'pipeline_early_reader', 2726),
                                       ('pipe-copy', 'pipeline_copy', None),
                                       ('pipe-bad-snapshot', 'pipeline_copy', 2731),
                                       ('pipe-exec', 'pipeline_exec', None),
                                       ('pipe-exec-leak', 'pipeline_exec', 2734),
                                       ('pipe-exec-stop-admit', 'pipeline_exec', None),
                                       ('pipe-exec-stop-table', 'pipeline_exec', None),
                                       ('pipe-exec-keep-holder', 'pipeline_exec', 2736),
                                       ('pipe-exec-libc', 'pipeline_exec', None),
                                       ('pipe-exec-libc-leak', 'pipeline_exec', 2734),
                                       ('pipe-exec-fork', 'pipeline_exec', None),
                                       ('pipe-exec-fork-no-repair', 'pipeline_exec', 2607),
                                       ('pipe-exec-live', 'pipeline_exec', None),
                                       ('pipe-exec-live-bad', 'pipeline_exec', 2731),
                                       ('pipe-exec-parent', 'pipeline_exec', None),
                                       ('pipe-exec-parent-status', 'pipeline_exec', 2730),
                                       ('pipe-exec-interleave', 'pipeline_exec', None),
                                       ('pipe-exec-interleave-retain', 'pipeline_exec', 2731),
                                       ('pipe-exec-wait-any', 'pipeline_exec', None),
                                       ('pipe-exec-wait-early', 'pipeline_exec', 2730),
                                       ('pipe-exec-stdout', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-grant', 'pipeline_exec', 2734),
                                       ('pipe-exec-stdout-drop', 'pipeline_exec', 2743),
                                       ('pipe-exec-stdout-inherit', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-retain', 'pipeline_exec', 2726),
                                       ('pipe-exec-stdout-stdio', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-stdin-retain', 'pipeline_exec', 2726),
                                       ('pipe-exec-stdout-stderr-drop', 'pipeline_exec', 2743),
                                       ('pipe-exec-stdout-request', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-errno', 'pipeline_exec', 2730),
                                       ('pipe-exec-stdout-request-dash', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-dash-byte', 'pipeline_exec', 2726),
                                       ('pipe-exec-stdout-request-builtin', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-byte', 'pipeline_exec', 2726),
                                       ('pipe-exec-stdout-request-builtin-auto', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-token', 'pipeline_exec', 2726),
                                       ('pipe-exec-stdout-request-builtin-auto-wait', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipeline_exec', 2750),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipeline_exec', 2750),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-recollect', 'pipeline_exec', 2750),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-starve', 'pipeline_exec', 2760),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-stop', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-stop-skip-stop', 'pipeline_exec', 2770),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-stop-keep-frame', 'pipeline_exec', 2772),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-stop-admit', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-stop-admit-skip-stop', 'pipeline_exec', 2770),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-stop-admit-keep-frame', 'pipeline_exec', 2772),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-wait-stop', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-wait-stop-skip-stop', 'pipeline_exec', 2780),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-wait-stop-lose-collection', 'pipeline_exec', 2781),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-wait-stop-keep-reply', 'pipeline_exec', 2782),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-reject', 'pipeline_exec', 2790),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-cloexec', 'pipeline_exec', 2733),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-alias', 'pipeline_exec', 2733),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-wire', 'pipeline_exec', 2746),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-skip', 'pipeline_exec', 2743),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-late', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-late-require-live', 'pipeline_exec', 2751),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-byte', 'pipeline_exec', 2743),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-alias', 'pipeline_exec', 2733),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-byte', 'pipeline_exec', 2743),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-alias', 'pipeline_exec', 2733),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-env', 'pipeline_exec', 2746),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-early', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-early-errno', 'pipeline_exec', 2726),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-no-signals', 'pipeline_exec', 2730),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-serial', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-serial-byte', 'pipeline_exec', None),
                                       ('pipe-exec-stdout-request-builtin-auto-wait-probes-overlap-preexec-io-remap-helper-consumer-natural-main-fds-parent-serial-grant', 'pipeline_exec', 2795),
                                       ]:
            case_name = label
            overlap = '-overlap' in label
            if overlap:
                label = 'pipe-exec-stdout-request-builtin-auto-wait-probes'
            variant = output / (case_name + '.raw')
            arguments = [str(variant) if value == str(owner) else value for value in base_owner]
            arguments += ['--cfg', 'pipeline_dispatch']
            if '-parent-serial' in case_name:
                arguments += ['--cfg', 'pipeline_serial']
                if case_name.endswith('-byte'):
                    arguments += ['--cfg', 'pipeline_serial_bad_byte']
                if case_name.endswith('-grant'):
                    arguments += ['--cfg', 'pipeline_serial_bad_grant']
            if '-parent-early' in case_name:
                arguments += ['--cfg', 'pipeline_shell_early']
                if case_name.endswith('-errno'):
                    arguments += ['--cfg', 'pipeline_wrong_errno']
            if '-fds-parent' in case_name:
                arguments += ['--cfg', 'pipeline_dash_parent']
            if '-main-fds' in case_name:
                arguments += ['--cfg', 'pipeline_natural_fds']
            if '-natural-main' in case_name:
                arguments += ['--cfg', 'pipeline_dash_main']
            if '-consumer-natural' in case_name:
                arguments += ['--cfg', 'pipeline_wait_natural']
                if '-natural-late' in case_name:
                    arguments += ['--cfg', 'pipeline_wait_late']
                if case_name.endswith('-require-live'):
                    arguments += ['--cfg', 'pipeline_wait_require_live']
            if overlap:
                arguments += ['--cfg', 'pipeline_exec_overlap']
                if '-overlap-preexec-io' in case_name:
                    arguments += ['--cfg', 'pipeline_exec_io']
                    if '-io-remap' in case_name:
                        arguments += ['--cfg', 'pipeline_exec_remap']
                    if '-remap-helper' in case_name:
                        arguments += ['--cfg', 'pipeline_helper_args']
                    if case_name.endswith('-reject'):
                        arguments += ['--cfg', 'pipeline_exec_io_reject']
                if '-overlap-wait-stop' in case_name:
                    arguments += ['--cfg', 'pipeline_wait_stop']
                    for suffix, flag in [('skip-stop', 'pipeline_wait_skip_stop'),
                                         ('lose-collection', 'pipeline_wait_lose_collection'),
                                         ('keep-reply', 'pipeline_wait_keep_reply')]:
                        if case_name.endswith('-' + suffix):
                            arguments += ['--cfg', flag]
                if '-overlap-stop' in case_name:
                    arguments += ['--cfg', 'pipeline_exec_overlap_stop']
                    if '-overlap-stop-admit' in case_name:
                        arguments += ['--cfg', 'pipeline_exec_overlap_stop_admit']
                    if case_name.endswith('-skip-stop'):
                        arguments += ['--cfg', 'pipeline_exec_overlap_skip_stop']
                    if case_name.endswith('-keep-frame'):
                        arguments += ['--cfg', 'pipeline_exec_overlap_keep_frame']
                if case_name.endswith('-starve'):
                    arguments += ['--cfg', 'pipeline_exec_starve']
            if config:
                arguments += ['--cfg', config]
            if label == 'pipe-keep-frame':
                arguments += ['--cfg', 'pipeline_keep_frame']
            if case_name.endswith('-parent-early-errno'):
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=98',) + context
            if case_name.endswith('-no-signals'):
                context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=138',) + context
            if label == 'pipe-wrong-errno':
                arguments += ['--cfg', 'pipeline_wrong_errno']
            if label == 'pipe-bad-snapshot':
                arguments += ['--cfg', 'pipeline_bad_snapshot']
            if config == 'pipeline_exec':
                arguments += ['--cfg', 'pipeline_copy']
            if label in ('pipe-exec-leak', 'pipe-exec-libc-leak'):
                arguments += ['--cfg', 'pipeline_exec_leak']
            if label == 'pipe-exec-stop-admit':
                arguments += ['--cfg', 'pipeline_exec_stop_admit']
            if label in ('pipe-exec-stop-table', 'pipe-exec-keep-holder'):
                arguments += ['--cfg', 'pipeline_exec_stop_table']
            if label == 'pipe-exec-keep-holder':
                arguments += ['--cfg', 'pipeline_exec_keep_holder']
            if label in ('pipe-exec-libc', 'pipe-exec-libc-leak', 'pipe-exec-fork', 'pipe-exec-fork-no-repair', 'pipe-exec-live', 'pipe-exec-live-bad', 'pipe-exec-parent', 'pipe-exec-parent-status', 'pipe-exec-interleave', 'pipe-exec-interleave-retain', 'pipe-exec-wait-any', 'pipe-exec-wait-early', 'pipe-exec-stdout', 'pipe-exec-stdout-grant', 'pipe-exec-stdout-drop', 'pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                arguments += ['--cfg', 'pipeline_libc']
            if label in ('pipe-exec-live', 'pipe-exec-live-bad', 'pipe-exec-parent', 'pipe-exec-parent-status', 'pipe-exec-interleave', 'pipe-exec-interleave-retain', 'pipe-exec-wait-any', 'pipe-exec-wait-early', 'pipe-exec-stdout', 'pipe-exec-stdout-grant', 'pipe-exec-stdout-drop', 'pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                arguments += ['--cfg', 'pipeline_live']
            if label in ('pipe-exec-parent', 'pipe-exec-parent-status', 'pipe-exec-interleave', 'pipe-exec-interleave-retain', 'pipe-exec-wait-any', 'pipe-exec-wait-early', 'pipe-exec-stdout', 'pipe-exec-stdout-grant', 'pipe-exec-stdout-drop', 'pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                arguments += ['--cfg', 'pipeline_factory']
            if label.startswith(('pipe-exec-interleave', 'pipe-exec-wait-', 'pipe-exec-stdout')):
                arguments += ['--cfg', 'pipeline_interleave']
            if label.startswith(('pipe-exec-wait-', 'pipe-exec-stdout')):
                arguments += ['--cfg', 'pipeline_wait_any']
            if label == 'pipe-exec-wait-early':
                arguments += ['--cfg', 'pipeline_wait_early']
            if label == 'pipe-exec-interleave-retain':
                arguments += ['--cfg', 'pipeline_keep_parent']
            if label == 'pipe-exec-parent-status':
                arguments += ['--cfg', 'pipeline_wait_status']
            if label.startswith('pipe-exec-stdout'):
                arguments += ['--cfg', 'pipeline_stdout']
            if label == 'pipe-exec-stdout-grant':
                arguments += ['--cfg', 'pipeline_stdout_grant']
            if label == 'pipe-exec-stdout-drop':
                arguments += ['--cfg', 'pipeline_stdout_drop']
            if label in ('pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                arguments += ['--cfg', 'pipeline_stdout_inherit']
            if label == 'pipe-exec-stdout-retain':
                arguments += ['--cfg', 'pipeline_stdout_retain']
            if label in ('pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                arguments += ['--cfg', 'pipeline_stdio']
            if label == 'pipe-exec-stdout-stdin-retain':
                arguments += ['--cfg', 'pipeline_stdin_retain']
            if label == 'pipe-exec-stdout-stderr-drop':
                arguments += ['--cfg', 'pipeline_stderr_drop']
            if label.startswith('pipe-exec-stdout-request'):
                arguments += ['--cfg', 'pipeline_exec_request']
            if label == 'pipe-exec-stdout-request-errno':
                arguments += ['--cfg', 'pipeline_exec_errno']
            if label.startswith('pipe-exec-stdout-request-builtin'):
                arguments += ['--cfg', 'pipeline_builtin']
            if label.startswith('pipe-exec-stdout-request-builtin-auto'):
                arguments += ['--cfg', 'pipeline_autonomous']
            if label == 'pipe-exec-stdout-request-builtin-auto-token':
                arguments += ['--cfg', 'pipeline_obsolete_release']
            if label.startswith('pipe-exec-stdout-request-builtin-auto-wait'):
                arguments += ['--cfg', 'pipeline_wait_io']
            if label.endswith('auto-wait-zero'):
                arguments += ['--cfg', 'pipeline_wait_zero']
            if 'auto-wait-probes' in label:
                arguments += ['--cfg', 'pipeline_wait_probes']
            if label.endswith('probes-scope'):
                arguments += ['--cfg', 'pipeline_wait_scope_errno']
            if label.endswith('probes-recollect'):
                arguments += ['--cfg', 'pipeline_wait_recollect']
            if config == 'pipeline_exec':
                arguments = [value.replace('user/native-connections/large-linker.ld', 'user/native-capacity/linker.ld')
                             for value in arguments]
            command(arguments, case_name + '-owner')
            variant_code = variant.read_bytes()
            assert 0 < len(variant_code) <= (24576 if config == 'pipeline_exec' else 16384)
            report['owner_sizes'][case_name] = len(variant_code)
            selected_worker = stop_image.read_bytes() if config == 'pipeline_stop_request' else pipe_worker
            if config == 'pipeline_early_reader':
                selected_worker = early_images['early-exit' if label == 'pipe-early-exit' else 'early']
            if config == 'pipeline_copy':
                selected_worker = early_images['copy']
            if config == 'pipeline_exec':
                selected_worker = early_images['exec']
            second_worker = early_images['replacement'] if config == 'pipeline_exec' else selected_worker
            if label in ('pipe-exec-libc', 'pipe-exec-libc-leak', 'pipe-exec-fork', 'pipe-exec-fork-no-repair', 'pipe-exec-live', 'pipe-exec-live-bad', 'pipe-exec-parent', 'pipe-exec-parent-status', 'pipe-exec-interleave', 'pipe-exec-interleave-retain', 'pipe-exec-wait-any', 'pipe-exec-wait-early', 'pipe-exec-stdout', 'pipe-exec-stdout-grant', 'pipe-exec-stdout-drop', 'pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                selected_worker, second_worker = early_images['libc-source'], early_images['libc']
            if label in ('pipe-exec-fork', 'pipe-exec-fork-no-repair'):
                selected_worker = early_images['fork-no-repair' if label.endswith('no-repair') else 'fork-source']
            if label in ('pipe-exec-live', 'pipe-exec-live-bad', 'pipe-exec-parent', 'pipe-exec-parent-status', 'pipe-exec-interleave', 'pipe-exec-interleave-retain', 'pipe-exec-wait-any', 'pipe-exec-wait-early', 'pipe-exec-stdout', 'pipe-exec-stdout-grant', 'pipe-exec-stdout-drop', 'pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                selected_worker = early_images['live-bad' if label.endswith('-bad') else 'live']
            if label in ('pipe-exec-parent', 'pipe-exec-parent-status', 'pipe-exec-interleave', 'pipe-exec-interleave-retain', 'pipe-exec-wait-any', 'pipe-exec-wait-early', 'pipe-exec-stdout', 'pipe-exec-stdout-grant', 'pipe-exec-stdout-drop', 'pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                selected_worker = early_images['interleave' if label.startswith('pipe-exec-interleave') else 'parent']
            if label.startswith(('pipe-exec-wait-', 'pipe-exec-stdout')):
                selected_worker = early_images['wait-any']
            if label.startswith('pipe-exec-stdout'):
                second_worker = early_images['stdout']
            if label in ('pipe-exec-stdout-inherit', 'pipe-exec-stdout-retain', 'pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                selected_worker, second_worker = early_images['inherit-source'], early_images['inherited-output']
            if label in ('pipe-exec-stdout-stdio', 'pipe-exec-stdout-stdin-retain', 'pipe-exec-stdout-stderr-drop', 'pipe-exec-stdout-request', 'pipe-exec-stdout-request-errno', 'pipe-exec-stdout-request-dash', 'pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-byte', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-token', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-zero', 'pipe-exec-stdout-request-builtin-auto-wait-probes', 'pipe-exec-stdout-request-builtin-auto-wait-probes-scope', 'pipe-exec-stdout-request-builtin-auto-wait-probes-recollect'):
                selected_worker, second_worker = early_images['stdio-source'], early_images['stdio']
            if label.startswith('pipe-exec-stdout-request'):
                selected_worker = early_images['exec-source']
            if label.startswith('pipe-exec-stdout-request-dash'):
                second_worker = early_images['dash-byte' if label.endswith('-byte') else 'dash']
            if label.startswith('pipe-exec-stdout-request-builtin'):
                selected_worker = early_images['builtin-byte' if label.endswith('-byte') else 'builtin']
            if label.startswith('pipe-exec-stdout-request-builtin-auto'):
                selected_worker, second_worker = early_images['autonomous'], early_images['autonomous-replacement']
            if label.startswith('pipe-exec-stdout-request-builtin-auto-wait'):
                selected_worker = early_images['wait-io']
            if 'auto-wait-probes' in label:
                selected_worker = early_images['wait-probes']
            if '-overlap-stop' in case_name:
                selected_worker, second_worker = early_images['stop-probes'], early_images['stop-replacement']
            if '-overlap-preexec-io' in case_name:
                selected_worker = early_images['preexec-io']
            if '-io-remap' in case_name:
                source = ('remap-helper' if '-helper-consumer' in case_name else
                          'remap' + case_name.split('-io-remap', 1)[1])
                selected_worker, second_worker = early_images[source], early_images[
                    'helper-replacement' if '-remap-helper' in case_name else 'remap-replacement']
            if '-consumer-natural' in case_name:
                selected_worker = early_images['remap-helper-natural']
            if '-natural-main' in case_name:
                selected_worker = early_images['remap-helper-natural-main' +
                                               case_name.split('-natural-main', 1)[1]]
            if '-helper-consumer' in case_name:
                second_worker = early_images['consumer-skip-replacement' if case_name.endswith('-skip')
                                             else 'consumer-replacement']
            if '-fds-parent' in case_name:
                second_worker = early_images['consumer-early-replacement' if '-parent-early' in case_name else 'consumer-parent-replacement']
            pipe_header = struct.pack('<8sIIIIQ', b'AENMX005' if config == 'pipeline_exec' else b'AENMX004', len(selected_worker), len(second_worker), len(selected_worker), len(variant_code), 0)
            pipe_payload = pipe_header + entropy + selected_worker + second_worker + selected_worker + variant_code
            context = (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),) if failure else ()
            if label == 'pipe-wrong-errno':
                context = (b'NATIVE terminal slot=3 generation=1 kind=1 detail=97',) + context
            if label in ('pipe-exec-leak', 'pipe-exec-libc-leak'):
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=105',) + context
            if label == 'pipe-exec-fork-no-repair':
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=115',) + context
            if label in ('pipe-exec-stdout-request-dash-byte', 'pipe-exec-stdout-request-builtin-byte'):
                context = (b'NATIVE terminal slot=3 generation=1 kind=1 detail=111',) + context
            if label == 'pipe-exec-stdout-request-builtin-auto-token':
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=129',) + context
            if label.endswith(('probes-scope', 'probes-recollect')):
                context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=131',) + context
            if label.endswith('auto-wait-zero'):
                context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=121',) + context
            if label == 'pipe-exec-stdout-request-errno':
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=127',) + context
            if label == 'pipe-exec-stdout-stdin-retain':
                context = (b'NATIVE terminal slot=3 generation=1 kind=1 detail=126',) + context
            if label == 'pipe-exec-stdout-retain':
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=124',) + context
            if label == 'pipe-exec-stdout-grant':
                context = (b'NATIVE terminal slot=4 generation=1 kind=1 detail=105',) + context
            if label == 'pipe-exec-wait-early':
                context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=123',) + context
            if label == 'pipe-exec-parent-status':
                context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=121',) + context
            if '-parent-serial' in case_name:
                pipe_payload = b'AENMX006' + pipe_payload[8:]
            cases.append((case_name, pipe_payload, True, b'native C profile rejected' if failure else None, context))
            if case_name.endswith('-parent-serial'):
                cases.append((case_name + '-disabled', pipe_payload, False, b'native C profile rejected', ()))
            if label == 'pipe-exec':
                assert len(variant_code) <= 16384
                cases.append(('pipe-exec-legacy-envelope', b'AENMX004' + pipe_payload[8:], True, None, ()))
        from session_smoke import build_cases, check_session, consumer_inputs, CASES
        cases += build_cases(command, cc, flags, output, report, entropy)
        session_names = {'session-' + row[0] for row in CASES}
        from recovery_smoke import check_recovery, consumer_inputs as recovery_inputs, CASES as RECOVERY_CASES
        cases += build_cases(command, cc, flags, output, report, entropy, recovery=True)
        recovery_names = {'recovery-' + row[0] for row in RECOVERY_CASES}
        from failed_exec_smoke import check_failed_exec, consumer_inputs as failed_exec_inputs, CASES as EXEC_CASES
        cases += build_cases(command, cc, flags, output, report, entropy, failed_exec=True)
        exec_names = {'failed-exec-' + row[0] for row in EXEC_CASES}
        from scratch_smoke import check_scratch, consumer_inputs as scratch_inputs, CASES as SCRATCH_CASES
        cases += build_cases(command, cc, flags, output, report, entropy, scratch=True)
        scratch_names = {'scratch-' + row[0] for row in SCRATCH_CASES}
        from serial_session import run_serial, CASES as SERIAL_CASES
        cases += build_cases(command, cc, flags, output, report, entropy, serial=True)
        serial_names = {'serial-session-' + row[0] for row in SERIAL_CASES}
        if selected_case is not None:
            cases = [case for case in cases if case[0] == selected_case]
            if not cases:
                raise ValueError('unknown selected case: ' + selected_case)
        for name, data, enabled, panic, context in cases:
            profile = 'pipe-exec-stdout-request-builtin-auto-wait-probes' if '-overlap' in name else name
            print('[RUNNING]', name, flush=True)
            case = output / name
            case.mkdir()
            envelope = case / 'native-c.bin'
            envelope.write_bytes(data)
            options = ['-Dsmp=false', '-Dnative-memory=true', '-Dnative-runner-local=true', '-Dnative-parent-identity=true']
            if name in ('pipe-copy', 'pipe-bad-snapshot') or name.startswith('pipe-exec'):
                options += ['-Dnative-process-freeze=true', '-Dnative-process-copy=true']
            if '-fds-parent' in name and not name.endswith('-no-signals'):
                options += ['-Dnative-signal-actions=true', '-Dnative-signal-public=true', '-Dnative-copy-signals=true']
            if name.startswith('pipe-exec'):
                options += ['-Dnative-process-exec=true']
            if name in session_names | recovery_names | exec_names | scratch_names | serial_names:
                options += ['-Dnative-process-freeze=true', '-Dnative-process-copy=true',
                            '-Dnative-process-exec=true', '-Dnative-signal-actions=true',
                            '-Dnative-signal-public=true', '-Dnative-copy-signals=true']
            if enabled:
                options.append('-Dnative-pipeline-capacity=true')
            started = datetime.datetime.now(datetime.timezone.utc)
            command(['zig', 'build', *options, '-Dnative-c-image=' + str(envelope), '-p', str(case),
                     '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global')], name)
            if name in serial_names:
                run_serial(case / 'aether.iso', name.removeprefix('serial-session-'))
            elif '-parent-serial' in name and not name.endswith('-disabled'):
                from console_smoke import pipeline_dash_run
                try:
                    pipeline_dash_run(case / 'aether.iso', bad_grant=name.endswith('-grant'))
                except RuntimeError as error:
                    if not name.endswith('-byte') or str(error) != 'pipeline UART output mismatch':
                        raise
                    print('PASS: host rejected deliberately corrupted serial output', flush=True)
                else:
                    if name.endswith('-byte'):
                        raise RuntimeError('corrupted serial output escaped host oracle')
            else:
                run(case / 'aether.iso', expected_panic=panic, panic_context=context, marker=b'AETHER NATIVE CONNECTIONS PASS')
            if name in session_names:
                serial = (case / 'native-serial.log').read_text()
                try:
                    check_session(serial, name.removeprefix('session-'), consumer_inputs())
                except RuntimeError as error:
                    if name != 'session-bad-byte' or str(error) != 'SESSION stream mismatch':
                        raise
                    print('PASS: host rejected deliberately corrupted session output', flush=True)
                else:
                    if name == 'session-bad-byte':
                        raise RuntimeError('corrupted session output escaped host oracle')
            if name in scratch_names:
                try:
                    check_scratch((case / 'native-serial.log').read_text(), name.removeprefix('scratch-'), scratch_inputs())
                except RuntimeError as error:
                    if name not in ('scratch-bad-byte', 'scratch-bad-read') or str(error) != 'SCRATCH-SESSION stream mismatch':
                        raise
                    print('PASS: host rejected deliberately corrupted scratch output', flush=True)
                else:
                    if name in ('scratch-bad-byte', 'scratch-bad-read'):
                        raise RuntimeError('corrupted scratch output escaped host oracle')
            if name in exec_names:
                serial = (case / 'native-serial.log').read_text()
                try:
                    check_failed_exec(serial, name.removeprefix('failed-exec-'), failed_exec_inputs())
                except RuntimeError as error:
                    if name != 'failed-exec-bad-byte' or str(error) != 'EXEC-SESSION stream mismatch':
                        raise
                    print('PASS: host rejected deliberately corrupted failed-exec output', flush=True)
                else:
                    if name == 'failed-exec-bad-byte':
                        raise RuntimeError('corrupted failed-exec output escaped host oracle')
            if name in recovery_names:
                serial = (case / 'native-serial.log').read_text()
                try:
                    check_recovery(serial, name.removeprefix('recovery-'), recovery_inputs())
                except RuntimeError as error:
                    if name != 'recovery-bad-byte' or str(error) != 'RECOVERY stream mismatch':
                        raise
                    print('PASS: host rejected deliberately corrupted recovery output', flush=True)
                else:
                    if name == 'recovery-bad-byte':
                        raise RuntimeError('corrupted recovery output escaped host oracle')
            if not panic and name not in session_names | recovery_names | exec_names | scratch_names | serial_names:
                serial = (case / 'native-serial.log').read_text()
                assert f'NATIVE supervisor result=100 reclaimed={30 if name == "session-lifetime" else 15}' in serial
                cancelled = name in ('pipe-exec-stop-admit', 'pipe-exec-stop-table')
                assert serial.count('NATIVE MEMORY admitted slot=') == (30 if name == 'session-lifetime' else 15 if '-parent-early' in name else 9 if cancelled else 6 if name == 'pipe-copy' else 12 if profile in ('pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-probes') else 15)
                if '-parent-early' not in name and profile in ('pipe-exec-stdout-request-builtin', 'pipe-exec-stdout-request-builtin-auto', 'pipe-exec-stdout-request-builtin-auto-wait', 'pipe-exec-stdout-request-builtin-auto-wait-probes'):
                    for slot, count in enumerate((3, 3, 0, 3, 3)):
                        assert serial.count(f'NATIVE MEMORY admitted slot={slot} ') == count
                for generation in range(1, 16 if name == 'session-lifetime' else 4):
                    for slot in range(2 if name == 'session-lifetime' else 5):
                        stopped = ((cancelled and slot >= 2) or (name.startswith('five-workers') and (generation, slot) == (2, 4)) or
                                   (name in ('pipe-stop-request', 'pipe-stop-reply') and slot == 2) or
                                   ('-overlap-stop' in name and slot == 4) or
                                   ('-overlap-wait-stop' in name and slot == 0))
                        if not stopped:
                            assert f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={42 if slot == 2 and "-parent-early" in name else 0}' in serial
                if name == 'session-lifetime':
                    assert serial.count('NATIVE terminal slot=') == 30
                    assert serial.count('NATIVE supervisor result=100 reclaimed=30') == 1
                    for slot in (0, 1):
                        assert serial.count(f'NATIVE MEMORY admitted slot={slot} ') == 15
                symbols = subprocess.check_output([tools['nm']['path'], str(case / 'bin/aether')], text=True)
                values = {line.split()[-1]: int(line.split()[0], 16) for line in symbols.splitlines()
                          if len(line.split()) == 3 and line.split()[-1] in ('kernel_start', 'kernel_end')}
                span = values['kernel_end'] - values['kernel_start']
                assert span <= 8 * 2 * 1024 * 1024
                report['kernel_mapping_bytes'] = span
                report['owner_bytes'] = len(code)
            report['cases'].append(dict(name=name, status='pass', start_utc=started.isoformat(),
                                        seconds=(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),
                                        envelope_sha256=sha(envelope), iso_sha256=sha(case / 'aether.iso'),
                                        serial_sha256=sha(case / 'native-serial.log')))
            if name == 'recovery-bad-byte':
                report['cases'][-1]['expected_host_rejection'] = 'RECOVERY stream mismatch'
            if name == 'session-bad-byte':
                report['cases'][-1]['expected_host_rejection'] = 'SESSION stream mismatch'
            if name.endswith('-parent-serial-byte'):
                report['cases'][-1]['expected_host_rejection'] = 'pipeline UART output mismatch'
            save()
        assert all(sha(ROOT / name) == digest for name, digest in sources.items())
        report['status'] = 'pass'
        print('[PASS] Five-worker capacity:', output, flush=True)
    finally:
        save()
        compact_run(output, report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--case', help='Run one exact case; recorded as selected coverage')
    arguments = parser.parse_args()
    suite(arguments.libc_build, arguments.tools_lock, arguments.case)
