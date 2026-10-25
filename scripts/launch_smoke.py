# SPDX-License-Identifier: BSD-2-Clause
"""Build two strict-musl helpers and test bounded executable selection in QEMU."""
import hashlib
import json
import os
import re
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import tarfile
from evidence import compact_run
from deps import ROOT
from regression import Parser
from native_smoke import run
from console_smoke import run_dash_console, run_pipe_console
from runner_startup import encode as encode_runner_startup


def suite(sdk, lock, channel=False, files=False, writable=False, init=False, lookup=False, process=False, coexist=False, program=False, connections=False, shared_files=False, inherited_launch=False, file_io=False, command_runner=False, init_large=False, init_composed=False):
    init_large = init_large or init_composed
    init = init or init_large
    inherited_launch = inherited_launch or file_io
    shared_files = shared_files or inherited_launch
    connections = connections or shared_files or command_runner
    program = program or connections
    coexist = coexist or program
    process = process or coexist
    files = files or writable
    sdk = Path(sdk).resolve()
    tools = json.loads(Path(lock).read_text())['tools']
    receipt = json.loads((sdk / 'evidence.json').read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(sdk / 'stage/usr/lib/libc.a') != receipt['libc_archive_sha256'] or not receipt.get('libc_patches'):
        raise RuntimeError('strict libc receipt mismatch')
    for name in (('clang', 'lld', 'nm', 'objdump', 'readelf') if command_runner else ('clang', 'lld')):
        if sha(Path(tools[name]['path']).resolve()) != tools[name]['sha256']:
            raise RuntimeError('tool pin mismatch: ' + name)
    out = Path(tempfile.mkdtemp(prefix='command-runner-suite-' if command_runner else 'file-io-suite-' if file_io else 'inherited-launch-suite-' if inherited_launch else 'shared-files-suite-' if shared_files else 'connections-suite-' if connections else 'program-suite-' if program else 'coexist-suite-' if coexist else 'process-suite-' if process else 'lookup-suite-' if lookup else 'init-composed-suite-' if init_composed else 'init-large-suite-' if init_large else 'init-suite-' if init else 'writable-files-suite-' if writable else 'files-suite-' if files else 'channel-suite-' if channel else 'launch-suite-', dir=ROOT / 'zig-out'))
    report = {'profile': 'command-runner' if command_runner else 'file-io' if file_io else 'inherited-launch' if inherited_launch else 'shared-files' if shared_files else 'connections' if connections else 'program' if program else 'coexist' if coexist else 'process' if process else 'lookup' if lookup else 'init-composed' if init_composed else 'init-large' if init_large else 'init' if init else 'writable-files' if writable else 'files' if files else 'channel' if channel else 'launch', 'status': 'incomplete', 'commands': [], 'cases': [], 'libc_receipt_sha256': sha(sdk / 'evidence.json'),
              'libc_sha256': receipt['libc_archive_sha256'], 'tools': tools, 'tools_lock_sha256': sha(Path(lock))}
    report['sources'] = {str(p.relative_to(ROOT)): sha(p) for parent in ('kernel', 'user', 'scripts')
                         for p in (ROOT / parent).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    report['sources']['build.zig'] = sha(ROOT / 'build.zig')
    print('[RUNNING] Evidence:', out, file=sys.stderr, flush=True)
    def command(argv, label, extra_env=None):
        report['commands'].append(argv)
        if extra_env:
            report.setdefault('command_environment', {})[label] = extra_env
        with (out / (label + '.log')).open('wb') as log:
            subprocess.run(argv, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT,
                           timeout=180, env={**os.environ, **(extra_env or {})})
    try:
        cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl', '--sysroot=' + str(sdk / 'empty-root')]
        source = 'user/native-command' if command_runner else 'user/native-shared' if shared_files else 'user/native-connections' if connections else 'user/native-process' if process else 'user/native-init' if init else 'user/native-files' if files else 'user/native-channel' if channel else 'user/native-launch'
        flags = ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin',
                 '-fstack-protector-strong', '-nostdinc', '-isystem', str(sdk / 'stage/usr/include')]
        if writable: flags += ['-DWRITABLE']
        if coexist: flags += ['-DCOEXIST']
        if program: flags += ['-DPROGRAM']
        if file_io: flags += ['-DFILE_IO']
        if inherited_launch: flags += ['-DREQUESTED']
        command(cc + flags + (['-D__aether_io=__aether_raw_io'] if command_runner else []) + ['-c', 'user/native-memory/adapter.c', '-o', str(out / 'adapter.o')], 'adapter')
        service_command = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '--crate-type=staticlib',
                           '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static',
                           'user/native-files/service.rs', '-o', str(out / 'service.a')]
        if command_runner: service_command += ['--cfg', 'command_runner']
        if writable or coexist: service_command += ['--cfg', 'writable']
        if files or coexist: command(service_command, 'service')
        images = []
        lib = sdk / 'stage/usr/lib'
        for number in ((1, 2, 3) if program else (1, 2)):
            obj = out / f'helper{number}.o'
            target = out / f'helper{number}.elf'
            command(cc + flags + [f'-DHELPER={number}', '-c', source + ('/program.c' if number == 3 else '/helper.c'), '-o', str(obj)], f'helper{number}-compile')
            link_command = cc + ['-fuse-ld=' + tools['lld']['path'], '-nostdlib', '-static', '-Wl,-z,noexecstack', '-Wl,--no-undefined',
                          '-Wl,-Map,' + str(out / f'helper{number}.map'), str(lib / 'crt1.o'), str(lib / 'crti.o'),
                          str(obj), str(out / 'adapter.o')] + ([str(out / 'service.a')] if (files and number == 1) or (coexist and number == 2) else []) + [str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(target)]
            if command_runner and number == 3:
                command(cc + flags + ['-c', source + '/child-adapter.c', '-o', str(out / 'child-adapter.o')], 'child-adapter')
                link_command.insert(link_command.index(str(lib / 'libc.a')), str(out / 'child-adapter.o'))
            if command_runner and number == 2:
                # Backend uses only its explicit native bridge, but libc still needs the raw hook.
                command(cc + flags + ['-c', 'user/native-memory/adapter.c', '-o', str(out / 'backend-adapter.o')], 'backend-adapter')
                link_command=[str(out / 'backend-adapter.o') if v==str(out / 'adapter.o') else v for v in link_command]
            command(link_command, f'helper{number}-link')
            if (files and number == 1) or (coexist and number == 2): service_link = list(link_command)
            if process and number == 1: requester_link = list(link_command)
            images.append(target.read_bytes())
        supervisor = out / 'supervisor.raw'
        supervisor_command = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=2', '-C', 'panic=abort',
                 '-C', 'relocation-model=static', '-C', 'link-arg=-Tuser/native-launch/linker.ld', '-C', 'link-arg=--oformat=binary',
                 ('user/native-connections' if shared_files or command_runner else source) + '/supervisor.rs', '-o', str(supervisor)]
        if process: supervisor_command += ['-C', 'lto=fat', '-C', 'codegen-units=1']
        if coexist:
            supervisor_command = ['opt-level=s' if v == 'opt-level=2' else v for v in supervisor_command]
            supervisor_command += ['--cfg', 'coexist']
        if program:
            supervisor_command = [v.replace('user/native-launch/linker.ld', 'user/native-process/program-linker.ld') for v in supervisor_command]
            supervisor_command += ['--cfg', 'program']
        if command_runner: supervisor_command += ['--cfg', 'command_runner']
        if shared_files: supervisor_command += ['--cfg', 'shared_files']
        if file_io: supervisor_command += ['--cfg', 'file_io']
        if inherited_launch: supervisor_command += ['--cfg', 'requested']
        if lookup: supervisor_command += ['--cfg', 'lookup']
        if init_large:
            supervisor_command += ['--cfg', 'init_large']
            if init_composed: supervisor_command += ['--cfg', 'init_composed']
            second_linker = out / 'second-page.ld'
            second_linker.write_text((ROOT / 'user/native-launch/linker.ld').read_text().replace('0x400000', '0x403000' if init_composed else '0x401000'))
            supervisor_command = [v.replace('user/native-launch/linker.ld', str(second_linker)) for v in supervisor_command]
        def mapped_code(raw):
            if not 0 < len(raw) <= 4096: raise RuntimeError('supervisor image bound')
            return (b'\xe9\xfb\x0f\0\0' + bytes(4091)) * (3 if init_composed else 1) + raw if init_large else raw
        command(supervisor_command, 'supervisor')
        code = mapped_code(supervisor.read_bytes()) if init_large else supervisor.read_bytes()
        if not 0 < len(code) <= (16384 if init_composed else 8192 if program or init_large else 4096): raise RuntimeError('supervisor image bound')
        entropy = os.urandom(48 if program else 32)
        def envelope(a, b, c=None):
            if program:
                c = images[2] if c is None else c
                return struct.pack('<8sIIIIII',b'AENMX001' if connections else b'AENPG001',len(a),len(b),len(c),len(code),0,0)+entropy+a+b+c+code
            return struct.pack('<8sIIII', b'AENCO001' if coexist else b'AENIN003' if init_composed else b'AENIN002' if init_large else b'AENIN001' if init else b'AENFS001' if (files or process) else b'AENCH001' if channel else b'AENEX001', len(a), len(b), len(code), 0) + entropy + a + b + code
        base = envelope(*images)
        bad = bytearray(base); struct.pack_into('<H', bad, (80 if program else 56) + len(images[0]) + 18, 183)
        reserved = bytearray(base); reserved[20] = 1
        layout = bytearray(base)
        elf_start = 80 if program else 56
        phoff = struct.unpack_from('<Q', layout, elf_start + 32)[0]
        phnum = struct.unpack_from('<H', layout, elf_start + 56)[0]
        for i in range(phnum):
            h = elf_start + phoff + i * 56
            kind, segment_flags = struct.unpack_from('<II', layout, h)
            if kind == 1 and segment_flags == 5:
                old = struct.unpack_from('<Q', layout, h + 16)[0]
                entry = struct.unpack_from('<Q', layout, elf_start + 24)[0]
                new = 0x10000000 + old % 4096
                struct.pack_into('<Q', layout, h + 16, new)
                struct.pack_into('<Q', layout, elf_start + 24, new + entry - old)
                break
        else: raise RuntimeError('missing executable segment for layout control')
        cases = [
            ('positive', base, None, ()),
            ('wrong-image', envelope(images[0], images[0]), b'native C profile rejected', (b'NATIVE terminal slot=1 generation=1 kind=1 detail=92', b'NATIVE supervisor result=411 reclaimed=0')),
            ('bad-machine', bad, b'invalid launch ELF', ()),
            ('reserved', reserved, b'invalid launch envelope', ()),
            ('bad-layout', layout, b'invalid launch layout', ()),
        ]
        if lookup:
            for label, config, context in [
                ('wide-namespace','wide_namespace',(b'NATIVE supervisor result=431 reclaimed=0',)),
                ('wrong-binding','wrong_binding',(b'NATIVE terminal slot=0 generation=1 kind=1 detail=92', b'NATIVE supervisor result=411 reclaimed=0'))]:
                argv = list(supervisor_command)
                target = out / (label + '.raw'); argv[argv.index('-o') + 1] = str(target); argv += ['--cfg', config]
                command(argv, label + '-supervisor')
                variant = target.read_bytes()
                if not 0 < len(variant) <= 4096: raise RuntimeError('supervisor image bound')
                payload = struct.pack('<8sIIII', b'AENEX001', len(images[0]), len(images[1]), len(variant), 0) + entropy + images[0] + images[1] + variant
                cases.append((label, payload, b'native C profile rejected', context))
        if channel:
            cases = [('positive', base, None, ())]
            for label, config in [('writer-fault','fault_writer'), ('writer-stop','stop_writer'), ('wrong-count','bad_count')]:
                argv = list(supervisor_command)
                target = out / (label + '.raw')
                argv[-1] = str(target)
                argv += ['--cfg', config]
                command(argv, label + '-supervisor')
                variant = target.read_bytes()
                if not 0 < len(variant) <= 4096: raise RuntimeError('supervisor image bound')
                payload = struct.pack('<8sIIII', b'AENCH001', len(images[0]), len(images[1]), len(variant), 0) + entropy + images[0] + images[1] + variant
                cases.append((label, payload, b'native C profile rejected' if label == 'wrong-count' else None,
                              (b'NATIVE terminal slot=1 generation=1 kind=1 detail=103', b'NATIVE supervisor result=511 reclaimed=0') if label == 'wrong-count' else ()))
        if files:
            wrong_command = list(service_command); wrong_command[wrong_command.index('-o') + 1] = str(out / 'wrong-service.a'); wrong_command += ['--cfg', 'wrong_data']
            command(wrong_command, 'wrong-service')
            wrong_link = [str(out / 'wrong-service.a') if v == str(out / 'service.a') else v for v in service_link]
            wrong_link[-1] = str(out / 'wrong-service.elf')
            wrong_link = [v.replace('helper1.map', 'wrong-service.map') for v in wrong_link]
            command(wrong_link, 'wrong-service-link')
            cases = [('positive', base, None, ()),
                     ('wrong-data', envelope((out / 'wrong-service.elf').read_bytes(), images[1]), b'native C profile rejected',
                      (b'NATIVE terminal slot=1 generation=1 kind=1 detail=211', b'NATIVE supervisor result=611 reclaimed=0'))]
        if files:
            short_obj = out / 'truncated.o'
            command(cc + flags + ['-DHELPER=2', '-DTRUNCATED', '-c', source + '/helper.c', '-o', str(short_obj)], 'truncated-compile')
            short_link = [str(short_obj) if v == str(out / 'helper2.o') else v.replace('helper2.map', 'truncated.map') for v in link_command]
            short_link[-1] = str(out / 'truncated.elf')
            command(short_link, 'truncated-link')
            cases.append(('truncated-request', envelope(images[0], (out / 'truncated.elf').read_bytes()), b'native C profile rejected',
                          (b'NATIVE terminal slot=0 generation=1 kind=1 detail=121', b'NATIVE supervisor result=611 reclaimed=0')))
        if writable:
            for label, config, detail in [('skip-truncate-zero', 'skip_truncate_zero', 236), ('ignore-write-rights', 'ignore_write_rights', 240)]:
                variant_command = list(service_command)
                archive = out / (label + '.a')
                variant_command[variant_command.index('-o') + 1] = str(archive)
                variant_command += ['--cfg', config]
                command(variant_command, label + '-compile')
                variant_link = [str(archive) if v == str(out / 'service.a') else v.replace('helper1.map', label + '.map') for v in service_link]
                target = out / (label + '.elf'); variant_link[-1] = str(target)
                command(variant_link, label + '-link')
                cases.append((label, envelope(target.read_bytes(), images[1]), b'native C profile rejected',
                              (f'NATIVE terminal slot=1 generation=1 kind=1 detail={detail}'.encode(), b'NATIVE supervisor result=611 reclaimed=0')))
        if init:
            cases = [('positive', base, None, ())]
            for label, config, detail in [('bad-deadline','bad_deadline',701), ('bad-late','bad_late',702),
                                          ('owner-exit','owner_exit',0), ('owner-fault','owner_fault',0),
                                          ('sequential','sequential',0), ('sequential-reverse','sequential_reverse',0)]:
                argv = list(supervisor_command)
                target = out / (label + '.raw'); argv[argv.index('-o') + 1] = str(target); argv += ['--cfg', config]
                command(argv, label + '-supervisor')
                variant = target.read_bytes()
                if not 0 < len(variant) <= 4096: raise RuntimeError('supervisor image bound')
                variant = mapped_code(variant)
                payload = struct.pack('<8sIIII', b'AENIN003' if init_composed else b'AENIN002' if init_large else b'AENIN001', len(images[0]), len(images[1]), len(variant), 0) + entropy + images[0] + images[1] + variant
                cases.append((label, payload, b'native C profile rejected' if detail else None,
                              (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),) if detail else ()))
            cases.append(('skip-deadline', base, b'native C profile rejected', (b'NATIVE supervisor result=701 reclaimed=0',)))
            cases.append(('cleanup-no-zero', next(c[1] for c in cases if c[0] == 'owner-exit'), b'native init cleanup not zeroed',
                          (b'NATIVE init closing live=1 terminal=1 queued=2 wait=1',)))
        if init_large:
            capacity_magic = b'AENIN003' if init_composed else b'AENIN002'
            capacity_limit = 16384 if init_composed else 8192
            def capacity_payload(value, magic=capacity_magic):
                return struct.pack('<8sIIII', magic, len(images[0]), len(images[1]), len(value), 0) + entropy + b''.join(images) + value
            cases.append(('dirty-tail', base, b'native init code tail not zeroed', ()))
            short_command = [v.replace(str(second_linker), 'user/native-launch/linker.ld') for v in supervisor_command]
            short_target = out / 'first-page.raw'; short_command[short_command.index('-o')+1] = str(short_target)
            command(short_command, 'first-page-supervisor')
            short = short_target.read_bytes()
            for size in ((1, 4095, 4096, 8191, 8192, 8193, 12287, 12288, 16383, 16384) if init_composed else (4095, 4096, 8191, 8192)):
                chosen = short if size < len(code) else code
                if size == 1: continue
                if len(chosen) > size: raise RuntimeError('boundary fixture does not fit')
                cases.append((f'capacity-{size}', capacity_payload(chosen + bytes(size-len(chosen))), None, ()))
            for label, value, magic in [('capacity-zero', b'', capacity_magic), ('capacity-over', bytes(capacity_limit+1), capacity_magic), ('old-over', code, b'AENIN001')] + ([('old-v2-over', code, b'AENIN002')] if init_composed else []):
                cases.append((label, capacity_payload(value, magic), b'invalid launch envelope', ()))
            for label, raw in [('capacity-truncated', base[:-1]), ('capacity-extra', base+b'!'), ('capacity-reserved', bytes(reserved))]:
                cases.append((label, raw, b'invalid launch envelope', ()))
            huge = bytearray(base); struct.pack_into('<I', huge, 16, 0xffffffff)
            cases.append(('capacity-huge', huge, b'invalid launch envelope', ()))
            for label, instruction in [('code-write', bytes.fromhex('c6042500104000000f0b')), ('stack-execute', bytes.fromhex('b800008000ffe0'))]:
                if init_composed and label == 'code-write': instruction = bytes.fromhex('c6042500304000000f0b')
                probe = mapped_code(instruction)
                cases.append((label, capacity_payload(probe), None, ()))
        if init_composed:
            for label, instruction in [('code-write-page2', bytes.fromhex('c6042500104000000f0b')), ('code-write-page3', bytes.fromhex('c6042500204000000f0b')), ('stack-guard', bytes.fromhex('c60425fff f7f00000f0b'.replace(' ', '')))]:
                cases.append((label, capacity_payload(mapped_code(instruction)), None, ()))
        if process and not program:
            cases = [('positive', base, None, ())]
            for label, config, detail in ([('repeat-collect','repeat_collect',207)] if coexist else [('allow-inheritance','allow_inherit',202), ('wide-scope','wide_scope',203), ('repeat-collect','repeat_collect',207)]):
                argv = list(supervisor_command)
                target = out / (label + '.raw'); argv[argv.index('-o') + 1] = str(target); argv += ['--cfg', config]
                command(argv, label + '-supervisor')
                variant = target.read_bytes()
                if not 0 < len(variant) <= 4096: raise RuntimeError('supervisor image bound')
                payload = struct.pack('<8sIIII', b'AENCO001' if coexist else b'AENFS001', len(images[0]), len(images[1]), len(variant), 0) + entropy + images[0] + images[1] + variant
                cases.append((label, payload, b'native C profile rejected',
                              (f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail}'.encode(), b'NATIVE supervisor result=903 reclaimed=2')))
            for label, config, detail, reclaims in [('partial-request','TRUNCATED',41,1), ('requester-exit','EARLY_EXIT',42,2)]:
                obj = out / (label + '.o'); target = out / (label + '.elf')
                command(cc + flags + ['-DHELPER=1', '-D' + config, '-c', source + '/helper.c', '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else v.replace('helper1.map', label + '.map') for v in requester_link]
                argv[argv.index('-o') + 1] = str(target); command(argv, label + '-link')
                cases.append((label, envelope(target.read_bytes(), images[1]), b'native C profile rejected',
                              (f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail}'.encode(), f'NATIVE supervisor result=903 reclaimed={reclaims}'.encode())))
        if coexist and not program:
            cases = [c for c in cases if c[0] in ('positive','repeat-collect','partial-request','requester-exit')]
            cases.append(('small-pool', base, b'native C profile rejected', (b'NATIVE terminal slot=0 generation=1 kind=1 detail=204', b'NATIVE supervisor result=903 reclaimed=1')))
            argv=list(service_command); archive=out/'wrong-service.a'; argv[argv.index('-o')+1]=str(archive);argv+=['--cfg','wrong_data'];command(argv,'wrong-service')
            argv=[str(archive) if v==str(out/'service.a') else v.replace('helper2.map','wrong-service.map') for v in service_link]
            target=out/'wrong-service.elf';argv[argv.index('-o')+1]=str(target);command(argv,'wrong-service-link')
            cases.append(('wrong-file-data',envelope(images[0],target.read_bytes()),b'native C profile rejected',(b'NATIVE terminal slot=0 generation=1 kind=1 detail=223',b'NATIVE supervisor result=903 reclaimed=2')))
        if program and not connections:
            bad_third=bytearray(base);struct.pack_into('<H',bad_third,80+len(images[0])+len(images[1])+18,183)
            bad_reserved=bytearray(base);bad_reserved[28]=1
            cases=[('positive',base,None,()),
                   ('wrong-third',envelope(images[0],images[1],images[0]),b'native C profile rejected',(b'NATIVE terminal slot=2 generation=1 kind=1 detail=201',b'NATIVE supervisor result=933 reclaimed=0')),
                   ('bad-third-machine',bad_third,b'invalid launch ELF',()),
                   ('program-reserved',bad_reserved,b'invalid launch envelope',()),
                   ('program-truncated',base[:-1],b'invalid launch envelope',())]
            argv=list(supervisor_command);target=out/'skip-program-stop.raw';argv[argv.index('-o')+1]=str(target);argv+=['--cfg','program_skip_stop'];command(argv,'skip-program-stop-supervisor')
            variant=target.read_bytes()
            if not 0<len(variant)<=8192:raise RuntimeError('program supervisor image bound')
            payload=struct.pack('<8sIIIIII',b'AENPG001',len(images[0]),len(images[1]),len(images[2]),len(variant),0,0)+entropy+b''.join(images)+variant
            cases.append(('skip-program-stop',payload,b'native C profile rejected',(b'NATIVE supervisor result=936 reclaimed=0',)))
        if connections and not shared_files and not command_runner:
            bad_reserved=bytearray(base);bad_reserved[28]=1
            bad_third=bytearray(base);struct.pack_into('<H',bad_third,80+len(images[0])+len(images[1])+18,183)
            cases=[('positive',base,None,()),
                   ('small-pool',base,b'native C profile rejected',(b'NATIVE supervisor result=950 reclaimed=0',)),
                   ('reserved',bad_reserved,b'invalid launch envelope',()),
                   ('bad-third-machine',bad_third,b'invalid launch ELF',())]
            for label,config,detail in [('reject-partial','reject_partial',959),('wrong-data','wrong_data',960)]:
                argv=list(supervisor_command);target=out/(label+'.raw');argv[argv.index('-o')+1]=str(target);argv+=['--cfg',config];command(argv,label+'-supervisor')
                variant=target.read_bytes()
                if not 0<len(variant)<=8192:raise RuntimeError('connections supervisor image bound')
                payload=struct.pack('<8sIIIIII',b'AENMX001',len(images[0]),len(images[1]),len(images[2]),len(variant),0,0)+entropy+b''.join(images)+variant
                cases.append((label,payload,b'native C profile rejected',(f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)))
        if connections and not shared_files and not command_runner:
            for label, define, config, detail in (
                ('freeze-positive', None, None, None),
                ('freeze-stop', None, 'freeze_stop', None),
                ('freeze-disabled', 'FREEZE_DISABLED', 'freeze_disabled', None),
                ('freeze-unsupported', 'FREEZE_UNSUPPORTED', 'freeze_unsupported', None),
                ('freeze-skip', None, None, 1710),
                ('freeze-token', None, None, 1712),
            ):
                frozen_images = []
                for role in ('parent', 'dummy'):
                    obj = out / (label + '-' + role + '.o')
                    target = obj.with_suffix('.elf')
                    defines = ['-DFREEZE_DUMMY'] if role == 'dummy' else (['-D' + define] if define else [])
                    command(cc + flags + defines + ['-c', 'user/native-connections/freeze-client.c', '-o', str(obj)], label + '-' + role + '-compile')
                    argv = [str(obj) if v == str(out / 'helper3.o') else v.replace(str(out / 'helper3.map'), str(target.with_suffix('.map'))) for v in link_command]
                    argv[argv.index('-o') + 1] = str(target)
                    command(argv, label + '-' + role + '-link')
                    frozen_images.append(target.read_bytes())
                raw = out / (label + '.raw')
                argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                argv += ['--cfg', 'process_freeze'] + (['--cfg', config] if config else [])
                command(argv, label + '-supervisor')
                code = raw.read_bytes()
                if not 0 < len(code) <= 8192: raise RuntimeError('freeze supervisor bound')
                a, b = frozen_images
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(a), len(b), len(b), len(code), 0, 0) + entropy + a + b + b + code
                cases.append((label, payload, b'native C profile rejected' if detail else None,
                              (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),) if detail else ()))
        if connections and not shared_files and not command_runner:
            exec_obj = out / 'exec-client.o'; exec_elf = out / 'exec-client.elf'
            command(cc + flags + ['-c', 'user/native-connections/exec-client.c', '-o', str(exec_obj)], 'exec-client')
            argv = [str(exec_obj) if v == str(out / 'helper3.o') else v.replace(str(out / 'helper3.map'), str(out / 'exec-client.map')) for v in link_command]
            argv[argv.index('-o') + 1] = str(exec_elf)
            command(argv, 'exec-client-link')
            for label, detail in [('exec-positive', None), ('exec-early', 2031), ('exec-token', 2032), ('exec-copy', 2035)]:
                raw = out / (label + '.raw'); argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                command(argv + ['--cfg', 'process_exec'], label + '-supervisor')
                a = (out / 'freeze-positive-parent.elf').read_bytes()
                b = (out / 'freeze-positive-dummy.elf').read_bytes()
                c = exec_elf.read_bytes(); code = raw.read_bytes()
                if not 0 < len(code) <= 8192: raise RuntimeError('exec supervisor bound')
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(a), len(b), len(c), len(code), 0, 0) + entropy + a + b + c + code
                cases.append((label, payload, b'native C profile rejected' if detail else None,
                              (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),) if detail else ()))
        if connections and not shared_files and not command_runner:
            archive_path = sdk.parent / 'musl-audit/musl-1.2.6.tar.gz'
            if sha(archive_path) != receipt['source_sha256']:
                raise RuntimeError('rebind private-header source pin mismatch')
            headers = out / 'musl-headers'
            with tarfile.open(archive_path) as archive:
                for member in archive.getmembers():
                    relative = member.name.removeprefix('musl-1.2.6/')
                    if member.isfile() and (relative == 'COPYRIGHT' or relative.endswith('.h') and relative.startswith(('src/internal/', 'arch/x86_64/', 'arch/generic/'))):
                        if '..' in Path(relative).parts or Path(relative).is_absolute():
                            raise RuntimeError('unsafe rebind header path')
                        target = headers / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.extractfile(member).read())
            if sha(archive_path) != receipt['source_sha256']:
                raise RuntimeError('rebind private-header source changed')
            header_hashes = {str(p.relative_to(headers)): sha(p) for p in headers.rglob('*') if p.is_file()}
            (out / 'private-headers.json').write_text(json.dumps(header_hashes, indent=2) + '\n')
            private = [item for part in ('src/internal', 'arch/x86_64', 'arch/generic') for item in ('-isystem', str(headers / part))]
            for label, config, detail in (
                ('copy-positive', None, None),
                ('copy-signals', None, None),
                ('copy-signals-handler', None, None),
                ('copy-signals-handler-invalid', None, None),
                ('copy-signals-handler-invalid-skip', None, 1820),
                ('copy-signals-handler-register', None, 1820),
                ('copy-signals-handler-fp', None, 1820),
                ('copy-signals-handler-escape', None, None),
                ('copy-signals-handler-escape-mask', None, 1820),
                ('copy-signals-rollback', 'copy_rollback', None),
                ('copy-signals-disabled', None, 1800),
                ('copy-signals-drop', None, 1820),
                ('copy-signals-pending', None, 1820),
                ('copy-signals-parent', None, 1821),
                ('copy-rebind', None, None),
                ('copy-rebind-aux', None, 1820),
                ('copy-rebind-tid', None, 1820),
                ('copy-rebind-channel', None, 1820),
                ('copy-slot-tid', None, 1800),
                ('copy-rollback', 'copy_rollback', None),
                ('copy-share', None, 1821),
                ('copy-anonymous', None, 1820),
                ('copy-zero', 'copy_rollback', None),
            ):
                handler_defines = {
                    'copy-signals-handler-invalid': ['COPY_HANDLER_INVALID'],
                    'copy-signals-handler-invalid-skip': ['COPY_HANDLER_INVALID', 'COPY_HANDLER_SKIP_INVALID'],
                    'copy-signals-handler-register': ['COPY_HANDLER_REGISTER'],
                    'copy-signals-handler-fp': ['COPY_HANDLER_FP'],
                    'copy-signals-handler-escape': ['COPY_HANDLER_ESCAPE'],
                    'copy-signals-handler-escape-mask': ['COPY_HANDLER_ESCAPE', 'COPY_HANDLER_ESCAPE_MASK'],
                }.get(label, [])
                obj = out / (label + '.o'); target = obj.with_suffix('.elf')
                command(cc + flags + ['-D' + define for define in handler_defines] + (['-DCOPY_SIGNALS'] if label.startswith('copy-signals') else []) + (['-DCOPY_SIGNAL_HANDLER'] if label.startswith('copy-signals-handler') else []) + (['-DCOPY_REBIND'] if label.startswith('copy-rebind') else []) + (['-DCOPY_ROLLBACK'] if config else []) + ['-c', 'user/native-connections/copy-client.c', '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper3.o') else v.replace(str(out / 'helper3.map'), str(target.with_suffix('.map'))) for v in link_command]
                argv[argv.index('-o') + 1] = str(target)
                if label.startswith('copy-rebind'):
                    hook = out / (label + '-hook.o')
                    fault = {'copy-rebind-aux': 'REBIND_SKIP_AUX', 'copy-rebind-tid': 'REBIND_SKIP_TID', 'copy-rebind-channel': 'REBIND_SKIP_CHANNEL'}.get(label)
                    command(cc + flags + private + ['-Dhidden=__attribute__((__visibility__("hidden")))'] + (['-D' + fault] if fault else []) + ['-c', 'user/native-connections/rebind.c', '-o', str(hook)], label + '-hook')
                    argv.insert(argv.index(str(lib / 'libc.a')), str(hook))
                command(argv, label + '-link')
                raw = out / (label + '.raw'); argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                argv += ['--cfg', 'process_copy'] + (['--cfg', config] if config else [])
                command(argv, label + '-supervisor')
                a = target.read_bytes(); b = (out / 'freeze-positive-dummy.elf').read_bytes(); code = raw.read_bytes()
                if not 0 < len(code) <= 8192: raise RuntimeError('copy supervisor bound')
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(a), len(b), len(b), len(code), 0, 0) + entropy + a + b + b + code
                context = (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),) if detail else ()
                if label in ('copy-rebind-aux', 'copy-rebind-tid', 'copy-rebind-channel'):
                    code = {'copy-rebind-aux': 240, 'copy-rebind-tid': 241, 'copy-rebind-channel': 242}[label]
                    context = (f'NATIVE terminal slot=2 generation=1 kind=1 detail={code}'.encode(), *context)
                if label in ('copy-signals-disabled', 'copy-signals-drop', 'copy-signals-pending', 'copy-signals-parent'):
                    slot, status = {'copy-signals-disabled': (0, 246), 'copy-signals-drop': (2, 247), 'copy-signals-pending': (2, 248), 'copy-signals-parent': (0, 248)}[label]
                    context = (f'NATIVE terminal slot={slot} generation=1 kind=1 detail={status}'.encode(), *context)
                if label in ('copy-signals-handler-invalid-skip', 'copy-signals-handler-register', 'copy-signals-handler-fp', 'copy-signals-handler-escape-mask'):
                    status = 249 if label.endswith('escape-mask') else 250
                    context = (f'NATIVE terminal slot=2 generation=1 kind=1 detail={status}'.encode(), *context)
                if label == 'copy-slot-tid': context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=230', *context)
                if label == 'copy-share': context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=215', *context)
                if label == 'copy-anonymous': context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=218', *context)
                panic = b'native copy rollback not zeroed' if label == 'copy-zero' else b'native C profile rejected' if detail else None
                cases.append((label, payload, panic, context))
        if connections and not shared_files and not command_runner:
            archive = out / 'inherit-service.a'
            argv = list(service_command); argv[argv.index('-o') + 1] = str(archive)
            command(argv + ['--cfg', 'runner_streams'], 'inherit-service')
            backend_image = out / 'inherit-backend.elf'
            argv = [str(out / 'helper2.o') if v == str(out / 'helper3.o') else v.replace(str(out / 'helper3.map'), str(out / 'inherit-backend.map')) for v in link_command]
            argv[argv.index('-o') + 1] = str(backend_image)
            argv.insert(argv.index(str(lib / 'libc.a')), str(archive))
            command(argv, 'inherit-backend-link')
            scratch_backends = {}
            for mode in ('scratch', 'scratch-drop', 'scratch-epoch'):
                scratch_archive = out / (mode + '-service.a')
                scratch_image = out / (mode + '-backend.elf')
                scratch_command = list(service_command)
                scratch_command[scratch_command.index('-o') + 1] = str(scratch_archive)
                scratch_cfg = ['--cfg', 'scratch_drop_write'] if mode == 'scratch-drop' else ['--cfg', 'scratch_old_epoch'] if mode == 'scratch-epoch' else []
                command(scratch_command + ['--cfg', 'runner_streams', '--cfg', 'scratch_backend'] + scratch_cfg, mode + '-service')
                scratch_link = [str(scratch_archive) if v == str(archive) else str(scratch_image) if v == str(backend_image) else v.replace(str(out / 'inherit-backend.map'), str(out / (mode + '-backend.map'))) for v in argv]
                command(scratch_link, mode + '-backend-link')
                scratch_backends[mode] = scratch_image
            pending_backends = {}
            for mode in ('pending', 'pending-eof', 'console', 'console-repeat'):
                pending_archive = out / (mode + '-service.a')
                pending_backend = out / (mode + '-backend.elf')
                pending_link = [str(pending_archive) if v == str(archive) else str(pending_backend) if v == str(backend_image) else v.replace(str(out / 'inherit-backend.map'), str(out / (mode + '-backend.map'))) for v in argv]
                pending_command = list(service_command)
                pending_command[pending_command.index('-o') + 1] = str(pending_archive)
                command(pending_command + ['--cfg', 'runner_streams', '--cfg', 'shell_console' if mode.startswith('console') else 'stream_pending'] + (['--cfg', 'pending_eof'] if mode.endswith('-eof') else []) + (['--cfg', 'shell_repeat'] if mode == 'console-repeat' else []), mode + '-service')
                command(pending_link, mode + '-backend-link')
                pending_backends[mode] = pending_backend
            uncertain_archive = out / 'inherit-uncertain-service.a'
            uncertain_backend = out / 'inherit-uncertain-backend.elf'
            uncertain_link = [str(uncertain_archive) if v == str(archive) else str(uncertain_backend) if v == str(backend_image) else v.replace(str(out / 'inherit-backend.map'), str(out / 'inherit-uncertain-backend.map')) for v in argv]
            argv = list(service_command); argv[argv.index('-o') + 1] = str(uncertain_archive)
            command(argv + ['--cfg', 'runner_streams', '--cfg', 'inherit_backend_bad'], 'inherit-uncertain-service')
            command(uncertain_link, 'inherit-uncertain-backend-link')
            incomplete_backends = {}
            for mode in ('missing', 'partial', 'write', 'close', 'write-missing', 'write-partial', 'close-missing', 'close-partial'):
                variant_archive = out / ('inherit-' + mode + '-service.a')
                variant_backend = out / ('inherit-' + mode + '-backend.elf')
                argv = list(service_command); argv[argv.index('-o') + 1] = str(variant_archive)
                parts = mode.split('-')
                extra = []
                if parts[0] in ('write', 'close'):
                    extra += ['--cfg', 'inherit_backend_effect', '--cfg', 'inherit_backend_' + parts[0]]
                if parts[-1] in ('missing', 'partial'):
                    extra += ['--cfg', 'inherit_backend_incomplete']
                if parts[-1] == 'partial':
                    extra += ['--cfg', 'inherit_backend_partial']
                command(argv + ['--cfg', 'runner_streams', '--cfg', 'inherit_backend_bad'] + extra, 'inherit-' + mode + '-service')
                argv = [str(variant_archive) if v == str(uncertain_archive) else str(variant_backend) if v == str(uncertain_backend) else v.replace(str(out / 'inherit-uncertain-backend.map'), str(out / ('inherit-' + mode + '-backend.map'))) for v in uncertain_link]
                command(argv, 'inherit-' + mode + '-backend-link')
                incomplete_backends[mode] = variant_backend
            adapter = out / 'inherit-memory.o'
            command(cc + flags + ['-D__aether_io=__aether_unused_io', '-c', 'user/native-memory/adapter.c', '-o', str(adapter)], 'inherit-memory')
            obj = out / 'inherit-client.o'; target = out / 'inherit-client.elf'
            command(cc + flags + ['-c', 'user/native-connections/inherit-client.c', '-o', str(obj)], 'inherit-client-compile')
            argv = [str(obj) if v == str(out / 'helper3.o') else str(adapter) if v == str(out / 'adapter.o') else v.replace(str(out / 'helper3.map'), str(out / 'inherit-client.map')) for v in link_command]
            argv[argv.index('-o') + 1] = str(target)
            argv.insert(argv.index(str(lib / 'libc.a')), str(out / 'copy-rebind-hook.o'))
            command(argv, 'inherit-client-link')
            inherit_link = list(argv)
            # Real descriptor preparation around the native image gate.
            # Keep upstream execve/error conversion; stage only the native call.
            with tarfile.open(archive_path) as archive:
                original_exec = archive.extractfile('musl-1.2.6/src/process/execve.c').read().decode()
            if original_exec.count('syscall(SYS_execve, path, argv, envp)') != 1:
                raise RuntimeError('public exec staging patch mismatch')
            exec_source = out / 'public-execve.c'
            exec_source.write_text('long __aether_execve_stage(const char *, char *const [], char *const []);\n' + original_exec.replace('syscall(SYS_execve, path, argv, envp)', '__syscall_ret(__aether_execve_stage(path, argv, envp))'))
            (out / 'upstream-execve.c').write_text(original_exec)
            exec_object = out / 'public-execve.o'
            command(cc + [v for v in flags if v not in ('-Wextra', '-Werror')] + private + ['-iquote', str(headers / 'src/internal'), '-Dhidden=__attribute__((__visibility__("hidden")))', '-c', str(exec_source), '-o', str(exec_object)], 'public-execve')
            helper = ROOT / 'user/native-command/dash-helper-inputs'
            if sha(helper / 'helper.c') != json.loads((helper / 'pin.json').read_text())['sha256']:
                raise RuntimeError('consumer helper source drift')
            consumer_obj = out / 'dash-argv-helper.o'
            command(cc + flags + ['-Dmain=consumer_helper_main', '-c', str(helper / 'helper.c'), '-o', str(consumer_obj)], 'dash-argv-helper')
            script_input = ROOT / 'user/native-command/dash-argv-inputs'
            if sha(script_input / 'argv.sh') != json.loads((script_input / 'pin.json').read_text())['sha256']:
                raise RuntimeError('consumer argv script drift')
            literal = re.search(r'"WITNESS=value /inputs/helper[^\n]+', (ROOT / 'user/native-connections/shell-client.h').read_text()).group(0).rstrip(',')
            if json.loads(literal).encode() != (script_input / 'argv.sh').read_bytes():
                raise RuntimeError('consumer argv literal differs from pinned script')
            signal_input = ROOT / 'user/native-command/dash-signal-inputs'
            if sha(signal_input / 'signal-table.sh') != json.loads((signal_input / 'pin.json').read_text())['sha256']:
                raise RuntimeError('consumer signal script drift')
            text = (ROOT / 'user/native-connections/pipe-shell-client.h').read_text()
            body = text[text.index('    arguments[2] =', text.index('    pid_t self = getpid();')):]
            literals = re.findall(r'"(?:\\.|[^"\\])*"', body)
            if ''.join(json.loads(literal) for literal in literals).encode() != (signal_input / 'signal-table.sh').read_bytes():
                raise RuntimeError('consumer signal literal differs from pinned script')
            if sha(signal_input / 'workloads.json') != json.loads((signal_input / 'pin.json').read_text())['workloads_sha256']:
                raise RuntimeError('consumer workload manifest drift')
            manifest = json.loads((signal_input / 'workloads.json').read_text())
            if manifest['environment'] != {'WITNESS': 'value', 'LC_ALL': 'C', 'PATH': '/nonexistent'}:
                raise RuntimeError('consumer environment contract drift')
            for filename, macro in [('pipe-shell-client.h', 'FORK_DASH_SIGNAL'), ('shell-client.h', 'FORK_SHELL_ARGV')]:
                client_source = (ROOT / 'user/native-connections' / filename).read_text()
                directive = '#if defined(FORK_DASH_SIGNAL) || defined(FORK_DASH_PIPE_CONSUMER)' if filename == 'pipe-shell-client.h' else '#ifdef ' + macro
                block = re.search(re.escape(directive) + r'\s+char \*environment\[\] = \{(.*?)\};', client_source, re.DOTALL)
                if not block or re.findall(r'"([^"]*)"', block.group(1)) != ['PWD=/work', 'WITNESS=value', 'LC_ALL=C', 'PATH=/nonexistent']:
                    raise RuntimeError('consumer environment literal drift: ' + filename)
            for case in manifest['cases']:
                if case['id'] in ('DASH-argv', 'DASH-signal-table'):
                    path = script_input / 'argv.sh' if case['id'] == 'DASH-argv' else signal_input / 'signal-table.sh'
                    expected = b'argv ok\n' if case['id'] == 'DASH-argv' else b'signal ok\n'
                    if sha(path) != case['sha256'] or case['expected_exit'] != 0 or hashlib.sha256(expected).hexdigest() != case['stdout_sha256']:
                        raise RuntimeError('consumer script/output contract drift')
            closure_input = ROOT / 'user/native-command/dash-closure-inputs'
            closure_case = next(case for case in manifest['cases'] if case['id'] == 'DASH-fd-closure')
            closure_bytes = (closure_input / 'fd-closure.sh').read_bytes()
            closure_block = re.search(r'#(?:ifdef FORK_SHELL_CLOSED|elif defined\(FORK_SHELL_CLOSED\))\s+(.*?)#elif', (ROOT / 'user/native-connections/shell-client.h').read_text(), re.DOTALL).group(1)
            closure_literal = ''.join(json.loads(value) for value in re.findall(r'"(?:\\.|[^"\\])*"', closure_block))
            if (sha(closure_input / 'fd-closure.sh') != json.loads((closure_input / 'pin.json').read_text())['sha256']
                    or sha(closure_input / 'fd-closure.sh') != closure_case['sha256']
                    or closure_literal.encode() != closure_bytes
                    or closure_case['expected_exit'] != 0
                    or hashlib.sha256(b'closed ok\n').hexdigest() != closure_case['stdout_sha256']):
                raise RuntimeError('consumer closure input/output drift')
            failed_input = ROOT / 'user/native-command/dash-failed-inputs'
            failed_case = next(case for case in manifest['cases'] if case['id'] == 'DASH-failed-exec')
            if (sha(failed_input / 'failed-exec.sh') != json.loads((failed_input / 'pin.json').read_text())['sha256']
                    or sha(failed_input / 'failed-exec.sh') != failed_case['sha256']
                    or hashlib.sha256(b'exec errors ok\n').hexdigest() != failed_case['stdout_sha256']):
                raise RuntimeError('consumer failed-exec input/output drift')
            scratch_input = ROOT / 'user/native-command/dash-scratch-inputs'
            scratch_pin = json.loads((scratch_input / 'pin.json').read_text())
            if (sha(scratch_input / 'fd-leak-control.sh') != scratch_pin['sha256']
                    or scratch_pin['sha256'] != '1e66c6d1748a1789137bc200e9919c34296fadf8f4088ecea275c681a5f64f7d'
                    or scratch_pin['expected_exit'] != 22 or scratch_pin['helper_exit'] != 95
                    or scratch_pin['stdout_sha256'] != hashlib.sha256(b'').hexdigest()):
                raise RuntimeError('consumer scratch leak input/output drift')
            denied_pin = json.loads((scratch_input / 'denied-pin.json').read_text())
            denied_case = next(case for case in manifest['cases'] if case['id'] == 'DASH-denied-redirection')
            if (sha(scratch_input / 'denied-redirection.sh') != denied_pin['sha256']
                    or denied_pin['sha256'] != denied_case['sha256']
                    or denied_pin['stdout_sha256'] != denied_case['stdout_sha256']
                    or denied_pin['expected_exit'] != 0
                    or denied_pin['stdout_sha256'] != hashlib.sha256(b'denied ok\n').hexdigest()):
                raise RuntimeError('consumer denied redirection input/output drift')
            redirect_pin = json.loads((scratch_input / 'redirection-pin.json').read_text())
            if (sha(scratch_input / 'redirection.sh') != redirect_pin['sha256']
                    or redirect_pin['sha256'] != '7416d63f5cc70c188fc16bbea7e97b5ac6e7e28195dde021163d24785d54269f'
                    or redirect_pin['expected_exit'] != 0 or redirect_pin['helper_exit'] != 0
                    or redirect_pin['stdout_sha256'] != hashlib.sha256(b'AB').hexdigest()):
                raise RuntimeError('consumer scratch redirection input/output drift')
            substitution_input = ROOT / 'user/native-command/dash-substitution-inputs'
            substitution_pin = json.loads((substitution_input / 'pin.json').read_text())
            substitution_case = next(case for case in manifest['cases'] if case['id'] == 'DASH-substitution')
            if (sha(substitution_input / 'substitution.sh') != substitution_pin['sha256']
                    or substitution_pin['sha256'] != substitution_case['sha256']
                    or substitution_pin['expected_exit'] != 0
                    or substitution_pin['stdout_sha256'] != hashlib.sha256(b'substitution ok\n').hexdigest()
                    or substitution_pin['stdout_sha256'] != substitution_case['stdout_sha256']):
                raise RuntimeError('consumer substitution input/output drift')
            exec_stream_images = []
            for role in ('old', 'new', 'pad', 'skip', 'shared', 'peer-first', 'peer-fault', 'public-old', 'public-new', 'public-false', 'mask-old', 'mask-new', 'mask-failure', 'mask-success', 'mask-zero', 'fork-new', 'dispatch-new', 'dash-new', 'pending-new', 'console-new', 'repeat-new', 'pipe-new', 'pipe-serial-new', 'argv-new', 'argv-skip', 'argv-closed', 'argv-closed-leak', 'argv-wait', 'argv-files', 'argv-files-skip', 'pipe-consumer-new', 'pipe-consumer-skip'):
                exec_stream_obj = out / ('exec-stream-' + role + '.o')
                exec_stream_target = exec_stream_obj.with_suffix('.elf')
                command(cc + flags + (['-DPIPE_EXEC_CONSUMER'] if role.startswith('pipe-consumer-') else []) + (['-DPIPE_EXEC_SKIP_HELPER'] if role == 'pipe-consumer-skip' else []) + (['-DEXEC_REPLACEMENT'] if role not in ('old', 'public-old', 'public-false', 'mask-old', 'mask-failure', 'mask-zero') else []) + (['-DEXEC_TABLE_PAD'] if role == 'pad' else []) + (['-DEXEC_TABLE_SKIP'] if role == 'skip' else []) + (['-DEXEC_SHARED'] if role in ('shared', 'peer-first', 'peer-fault') else []) + (['-DEXEC_PEER_FIRST'] if role.startswith('peer-') else []) + (['-DEXEC_PEER_FAULT'] if role == 'peer-fault' else []) + (['-DEXEC_PUBLIC'] if (role.startswith(('public-', 'mask-')) or role in ('fork-new', 'dispatch-new', 'pending-new')) else []) + (['-DEXEC_PUBLIC_FALSE_RETURN'] if role == 'public-false' else []) + (['-DEXEC_MASK'] if role.startswith('mask-') or role in ('fork-new', 'dispatch-new', 'pending-new') else []) + (['-DEXEC_FORK'] if role in ('fork-new', 'dispatch-new', 'pending-new') else []) + (['-DEXEC_MASK_SKIP_FAILURE'] if role == 'mask-failure' else []) + (['-DEXEC_MASK_SKIP_SUCCESS'] if role == 'mask-success' else []) + (['-DEXEC_MASK_ZERO'] if role == 'mask-zero' else []) + (['-DEXEC_DISPATCH'] if role == 'dispatch-new' else []) + (['-DEXEC_PENDING'] if role == 'pending-new' else []) + (['-DFORK_CONSOLE'] if role in ('console-new', 'repeat-new') else []) + (['-DFORK_REPEAT'] if role == 'repeat-new' else []) + (['-DPIPE_EXEC_SERIAL'] if role == 'pipe-serial-new' else []) + (['-DFORK_SHELL_FILES'] if role.startswith('argv-files') else []) + (['-DFORK_SHELL_ARGV'] if role.startswith('argv-') else []) + (['-DFORK_SHELL_ARGV_SKIP'] if role in ('argv-skip', 'argv-files-skip') else []) + (['-DFORK_SHELL_CLOSED_LEAK'] if role == 'argv-closed-leak' else []) + (['-DFORK_NULL'] if role == 'argv-wait' else []) + ['-c', 'user/native-connections/pipe-exec-client.c' if role in ('pipe-new', 'pipe-serial-new', 'pipe-consumer-new', 'pipe-consumer-skip') else 'user/native-connections/dash-command.c' if role in ('dash-new', 'console-new', 'repeat-new', 'argv-new', 'argv-skip', 'argv-closed', 'argv-closed-leak', 'argv-wait', 'argv-files', 'argv-files-skip') else 'user/native-connections/exec-stream-client.c', '-o', str(exec_stream_obj)], 'exec-stream-' + role)
                linked = [str(exec_stream_obj) if v == str(out / 'inherit-client.o') else v.replace(str(out / 'inherit-client.map'), str(exec_stream_target.with_suffix('.map'))) for v in inherit_link]
                linked[linked.index('-o') + 1] = str(exec_stream_target)
                if role in ('public-old', 'public-false', 'mask-old', 'mask-failure', 'mask-zero'): linked.insert(linked.index(str(lib / 'libc.a')), str(exec_object))
                if role.startswith(('argv-', 'pipe-consumer-')): linked.insert(linked.index(str(lib / 'libc.a')), str(consumer_obj))
                command(linked, 'exec-stream-' + role + '-link')
                exec_stream_images.append(exec_stream_target.read_bytes())
            for label, config, detail in [
                ('exec-streams-mask', 'exec_public exec_mask', None),
                ('exec-streams-mask-zero', 'exec_public exec_mask exec_mask_zero', None),
                ('exec-streams-mask-failure', 'exec_public exec_mask exec_mask_failure', 1950),
                ('exec-streams-mask-success', 'exec_public exec_mask exec_mask_success', 1950),
                ('exec-streams-public', 'exec_public', None),
                ('exec-streams-public-return', 'exec_public exec_public_false', 1950),
                ('exec-streams-public-keep', 'exec_public exec_keep_fds', 2040),
                ('exec-streams-peer-close-missing', 'exec_shared exec_peer_first exec_peer_incomplete', None),
                ('exec-streams-peer-close-partial', 'exec_shared exec_peer_first exec_peer_incomplete exec_peer_partial', None),
                ('exec-streams-fault-close-missing', 'exec_shared exec_peer_first exec_peer_fault exec_peer_incomplete', None),
                ('exec-streams-fault-close-partial', 'exec_shared exec_peer_first exec_peer_fault exec_peer_incomplete exec_peer_partial', None),
                ('exec-streams-peer-close-pad', 'exec_shared exec_peer_first exec_peer_incomplete exec_peer_partial exec_peer_pad', 2100),
                ('exec-streams-fault-close-stop', 'exec_shared exec_peer_first exec_peer_fault exec_peer_incomplete exec_peer_skip_stop', 2101),
                ('exec-streams-peer-first', 'exec_shared exec_peer_first', None),
                ('exec-streams-peer-fault', 'exec_shared exec_peer_first exec_peer_fault', None),
                ('exec-streams-peer-close-live', 'exec_shared exec_peer_first exec_peer_fault exec_peer_close_live', 1952),
                ('exec-streams-peer-leak', 'exec_shared exec_peer_first exec_peer_fault exec_peer_leak', 2091),
                ('exec-streams-shared', 'exec_shared', None),
                ('exec-streams-shared-close', 'exec_shared exec_shared_early_close', 2080),
                ('exec-streams-shared-offset', 'exec_shared inherit_private_position', 1903),
                ('exec-streams', None, None), ('exec-streams-keep', 'exec_keep_fds', 2040), ('exec-streams-offset', 'exec_reset_offset', 1903),
                ('exec-streams-close-missing', 'exec_close_incomplete', None),
                ('exec-streams-close-partial', 'exec_close_incomplete exec_close_partial', None),
                ('exec-streams-close-pad', 'exec_close_incomplete exec_close_partial exec_close_pad', 2050),
                ('exec-streams-close-stop', 'exec_close_incomplete exec_close_skip_stop', 2051),
                ('exec-streams-boot-missing', 'exec_boot_incomplete', None),
                ('exec-streams-boot-partial', 'exec_boot_incomplete exec_boot_partial', None),
                ('exec-streams-table-missing', 'exec_boot_incomplete exec_boot_table', None),
                ('exec-streams-table-partial', 'exec_boot_incomplete exec_boot_table exec_boot_partial', None),
                ('exec-streams-table-pad', 'exec_boot_incomplete exec_boot_table exec_boot_partial exec_boot_pad', 2060),
                ('exec-streams-table-stop', 'exec_boot_incomplete exec_boot_table exec_boot_partial exec_close_skip_stop', 2051),
                ('exec-streams-eof-boot', 'exec_reject', None),
                ('exec-streams-eof-boot-partial', 'exec_reject exec_reject_partial', None),
                ('exec-streams-eof-table', 'exec_reject exec_reject_table', None),
                ('exec-streams-eof-table-partial', 'exec_reject exec_reject_table exec_reject_partial', None),
                ('exec-streams-malformed-boot', 'exec_reject exec_reject_malformed', None),
                ('exec-streams-malformed-table', 'exec_reject exec_reject_table exec_reject_malformed', None),
                ('exec-streams-malformed-skip', 'exec_reject exec_reject_table exec_reject_malformed exec_reject_skip_validation', 2070),
                ('exec-streams-eof-stop', 'exec_reject exec_reject_skip_stop', 2072),
            ]:
                raw = out / (label + '.raw'); exec_stream_command = list(supervisor_command)
                exec_stream_command[exec_stream_command.index('-o') + 1] = str(raw)
                command(exec_stream_command + ['--cfg', 'exec_streams'] + [v for cfg in (config.split() if config else []) for v in ('--cfg', cfg)], label + '-supervisor')
                a = exec_stream_images[14 if 'exec_mask_zero' in (config or '').split() else 12 if 'exec_mask_failure' in (config or '').split() else 10 if 'exec_mask' in (config or '').split() else 9 if 'exec_public_false' in (config or '').split() else 7 if 'exec_public' in (config or '').split() else 0]
                c = exec_stream_images[13 if 'exec_mask_success' in (config or '').split() else 11 if 'exec_mask' in (config or '').split() else 8 if 'exec_public' in (config or '').split() else 6 if 'exec_peer_fault' in (config or '').split() else 5 if 'exec_peer_first' in (config or '').split() else 4 if 'exec_shared' in (config or '').split() else 3 if 'exec_reject_skip_validation' in (config or '') else 2 if 'exec_boot_pad' in (config or '') else 1]
                exec_backend = incomplete_backends['close-partial' if any(flag in (config or '').split() for flag in ('exec_close_partial', 'exec_peer_partial')) else 'close-missing'] if any(flag in (config or '').split() for flag in ('exec_close_incomplete', 'exec_peer_incomplete')) else backend_image
                b = exec_backend.read_bytes(); code = raw.read_bytes()
                if not 0 < len(code) <= 8192: raise RuntimeError('exec stream supervisor bound')
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(a), len(b), len(c), len(code), 0, 0) + entropy + a + b + c + code
                context = (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),) if detail else ()
                if label in ('exec-streams-mask-failure', 'exec-streams-mask-success'): context = (f'NATIVE terminal slot=0 generation=1 kind=1 detail={221 if label.endswith("failure") else 222}'.encode(), *context)
                if label == 'exec-streams-public-return': context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=220', *context)
                if label in ('exec-streams-keep', 'exec-streams-public-keep'): context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=216', *context)
                cases.append((label, payload, b'native C profile rejected' if detail else None, context))
            # Build a private musl fork candidate from the verified source archive.
            fork_root = out / 'public-fork'
            fork_root.mkdir()
            with tarfile.open(archive_path) as archive:
                for name in ('fork.c', '_Fork.c', 'waitpid.c'):
                    (fork_root / name).write_bytes(archive.extractfile('musl-1.2.6/src/process/' + name).read())
                for name in ('wait3.c', 'wait4.c'):
                    (fork_root / name).write_bytes(archive.extractfile('musl-1.2.6/src/linux/' + name).read())
                for member in archive.getmembers():
                    name = member.name.removeprefix('musl-1.2.6/')
                    if member.isfile() and name.endswith('.h') and name.startswith(('src/include/', 'include/')):
                        if '..' in Path(name).parts or Path(name).is_absolute():
                            raise RuntimeError('unsafe public fork header path')
                        dest = fork_root / name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(archive.extractfile(member).read())
            fork_arch = fork_root / 'syscall_arch.h'
            fork_arch.write_text((headers / 'arch/x86_64/syscall_arch.h').read_text().replace('"syscall"', '"int $0x81"').replace('"a"(n)', '"a"(n + 0x10000)'))
            original_fork = (fork_root / '_Fork.c').read_text()
            if original_fork.count('ret = __syscall(SYS_fork);') != 1:
                raise RuntimeError('public fork staging patch mismatch')
            staged_fork = 'long __aether_fork_stage(void);\n' + original_fork.replace('ret = __syscall(SYS_fork);', 'ret = __aether_fork_stage();')
            (fork_root / '_Fork.c').write_text(staged_fork)
            (fork_root / '_Fork-no-repair.c').write_text(staged_fork.replace('__post_Fork(ret);', 'if (ret) __post_Fork(ret);'))
            # Upstream source keeps upstream diagnostics; first-party client remains strict.
            upstream_flags = [v for v in flags if v not in ('-Wextra', '-Werror')]
            fork_private = ['-include', str(fork_root / 'src/include/features.h'), '-I', str(fork_root / 'src/include'), '-I', str(fork_root), *private, '-Dhidden=__attribute__((__visibility__("hidden")))']
            for name in ('fork', '_Fork', '_Fork-no-repair'):
                command(cc + upstream_flags + fork_private + ['-c', str(fork_root / (name + '.c')), '-o', str(fork_root / (name + '.o'))], 'public-' + name)
            original_wait = (fork_root / 'waitpid.c').read_text()
            if original_wait.count('sys_wait4_cp(pid, status, options, 0)') != 1:
                raise RuntimeError('public waitpid patch mismatch')
            (fork_root / 'waitpid.c').write_text('long __aether_waitpid(int, int *, int);\n' + original_wait.replace('sys_wait4_cp(pid, status, options, 0)', '__syscall_ret(__aether_waitpid(pid, status, options))'))
            command(cc + upstream_flags + fork_private + ['-include', str(headers / 'src/internal/syscall.h'), '-c', str(fork_root / 'waitpid.c'), '-o', str(fork_root / 'waitpid.o')], 'public-waitpid')
            original_wait4 = (fork_root / 'wait4.c').read_text()
            if original_wait4.count('__sys_wait4(pid, status, options, dest)') != 1 or original_wait4.count('\n\tint r;') != 1:
                raise RuntimeError('public wait4 patch mismatch')
            native_wait4 = 'long __aether_waitpid(int, int *, int);\n' + original_wait4.replace('__sys_wait4(pid, status, options, dest)', '__aether_waitpid(pid, status, options)')
            (fork_root / 'wait4-bad-usage.c').write_text(native_wait4)
            (fork_root / 'wait4.c').write_text(native_wait4.replace('\n\tint r;', '\n\tif (ru) return __syscall_ret(-ENOTSUP);\n\tint r;'))
            for name in ('wait3', 'wait4', 'wait4-bad-usage'):
                command(cc + upstream_flags + fork_private + ['-include', str(headers / 'src/internal/syscall.h'), '-c', str(fork_root / (name + '.c')), '-o', str(fork_root / (name + '.o'))], 'public-' + name)
            fork_rebind = fork_root / 'rebind.o'
            command(cc + flags + private + ['-Dhidden=__attribute__((__visibility__("hidden")))', '-DREBIND_LIBC_REPAIR', '-c', 'user/native-connections/rebind.c', '-o', str(fork_rebind)], 'public-fork-rebind')
            inherit_cases = [
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-denied', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_denied', 'FORK_SHELL_FILES', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-denied-errno', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_denied files_denied_errno', 'FORK_SHELL_FILES', 2554),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-denied-output', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_denied files_denied_drop_output', 'FORK_SHELL_FILES', 2310),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-redirection', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_redirect', 'FORK_SHELL_FILES', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-redirection-write', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_redirect files_redirect_drop_write', 'FORK_SHELL_FILES', 2310),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-redirection-stdin', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_redirect files_redirect_keep_stdin', 'FORK_SHELL_FILES', 2131),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-redirection-skip', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_redirect shell_files_skip_helper', 'FORK_SHELL_FILES', 2310),

                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files', 'FORK_SHELL_FILES', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-grant', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_bad_grant', 'FORK_SHELL_FILES', 1980),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-description', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_drop_description', 'FORK_SHELL_FILES', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-skip', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv scratch_backend shell_files shell_files_skip_helper', 'FORK_SHELL_FILES', 2130),

                ('copy-inherit-public-fork-wait-suspend-frame', 'inherit_wait suspend_order suspend_before', 'FORK_WAIT_SUSPEND_FRAME', None),
                ('copy-inherit-public-fork-wait-suspend-frame-valid', 'inherit_wait suspend_order suspend_before', 'FORK_WAIT_SUSPEND_FRAME_VALID', 1950),
                ('copy-inherit-public-fork-wait-suspend-stale', 'inherit_wait suspend_order suspend_stale', 'FORK_WAIT_SUSPEND_STALE', None),
                ('copy-inherit-public-fork-wait-suspend-stale-post', 'inherit_wait suspend_order suspend_stale', 'FORK_WAIT_SUSPEND_STALE_POST', 1950),
                ('copy-inherit-public-fork-wait-suspend-stop', 'inherit_wait suspend_order suspend_stop', 'FORK_WAIT_SUSPEND', None),
                ('copy-inherit-public-fork-wait-suspend-stop-skip', 'inherit_wait suspend_order suspend_stop suspend_stop_skip', 'FORK_WAIT_SUSPEND', 2331),
                ('copy-inherit-public-fork-wait-suspend-ignore', 'inherit_wait suspend_order suspend_stop suspend_late_stop', 'FORK_WAIT_SUSPEND_IGNORE', None),
                ('copy-inherit-public-fork-wait-suspend-block', 'inherit_wait suspend_order suspend_stop suspend_late_stop', 'FORK_WAIT_SUSPEND_BLOCK', None),
                ('copy-inherit-public-fork-wait-suspend-repeat', 'inherit_wait suspend_order suspend_repeat', 'FORK_WAIT_SUSPEND_REPEAT', None),
                ('copy-inherit-public-fork-wait-suspend-repeat-post', 'inherit_wait suspend_order suspend_repeat', 'FORK_WAIT_SUSPEND_REPEAT_POST', 1950),
                ('copy-inherit-public-fork-wait-suspend-before', 'inherit_wait suspend_order suspend_before', 'FORK_WAIT_SUSPEND', None),
                ('copy-inherit-public-fork-wait-suspend-after', 'inherit_wait suspend_order', 'FORK_WAIT_SUSPEND', None),
                ('copy-inherit-public-fork-wait-suspend-skip', 'inherit_wait suspend_order', 'FORK_WAIT_SUSPEND_SKIP', 2330),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-signal-table', 'pipe_probe pipe_dash shell_dash dash_signal', 'FORK_DASH_SIGNAL', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-signal-table-post', 'pipe_probe pipe_dash shell_dash dash_signal', 'FORK_DASH_SIGNAL_NO_POST', 2175),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-signal-table-scope', 'pipe_probe pipe_dash shell_dash dash_signal', 'FORK_DASH_SIGNAL_SCOPE', 2176),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null', 'FORK_SHELL_NULL', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-wait', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null shell_wait', 'FORK_SHELL_NULL_WAIT', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-wait-disabled', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null shell_wait', 'FORK_SHELL_NULL_WAIT', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-fault', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_fault', 'FORK_SHELL_NULL_FAULT', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-fault-keep', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_fault null_stop_keep', 'FORK_SHELL_NULL_FAULT', 2322),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-fault-holders', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_fault null_stop_holders', 'FORK_SHELL_NULL_FAULT', 2323),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-handle', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_bad_handle', 'FORK_SHELL_NULL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-eof', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_bad_eof', 'FORK_SHELL_NULL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-stale', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_bad_stale', 'FORK_SHELL_NULL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-rollback', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_bad_rollback', 'FORK_SHELL_NULL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-mask', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null', 'FORK_SHELL_NULL_MASK', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-limit', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null null_bad_limit', 'FORK_SHELL_NULL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-table', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_null fork_exec_keep', 'FORK_SHELL_NULL', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_failed_exec', 'FORK_SHELL_FAILED_EXEC', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec-missing', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_failed_exec failed_missing_denied', 'FORK_SHELL_FAILED_EXEC', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec-denied', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_failed_exec failed_denied_missing', 'FORK_SHELL_FAILED_EXEC', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec-skip', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_failed_exec', 'FORK_FAILED_SKIP', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec-output', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_failed_exec failed_drop_output', 'FORK_SHELL_FAILED_EXEC', 2310),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-failed-exec-keep', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_failed_exec failed_keep_child', 'FORK_SHELL_FAILED_EXEC', 2153),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-closure', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_closed', 'FORK_SHELL_CLOSED', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-closure-leak', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_closed shell_closed_leak', 'FORK_SHELL_CLOSED', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-closure-status', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_closed shell_wait_status', 'FORK_SHELL_CLOSED', 2310),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv', 'FORK_SHELL_ARGV', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv-arg', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_argv_arg', 'FORK_SHELL_ARGV', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv-env', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_argv_env', 'FORK_SHELL_ARGV', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv-skip', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_argv shell_argv_skip', 'FORK_SHELL_ARGV', 2310),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-serial', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_dash_repeat shell_console pipe_exec_serial', 'FORK_DASH_PIPE_SERIAL_EXEC', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-serial-stale', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_dash_repeat shell_console pipe_exec_serial pipe_exec_serial_stale', 'FORK_DASH_PIPE_SERIAL_EXEC', 2184),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-serial-grant', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_dash_repeat shell_console pipe_exec_serial pipe_exec_serial_grant', 'FORK_DASH_PIPE_SERIAL_EXEC', 2176),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-consumer', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_consumer', 'FORK_DASH_PIPE_CONSUMER', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-consumer-args', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_consumer pipe_consumer_args', 'FORK_DASH_PIPE_CONSUMER', 2175),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-consumer-skip', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_consumer pipe_consumer_skip', 'FORK_DASH_PIPE_CONSUMER', 2175),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec', 'pipe_probe pipe_dash shell_dash pipe_exec', 'FORK_DASH_PIPE_EXEC', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-stale', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_exec_stale', 'FORK_DASH_PIPE_EXEC', 2184),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-drop', 'pipe_probe pipe_dash shell_dash pipe_exec pipe_exec_drop', 'FORK_DASH_PIPE_EXEC', 2176),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-serial', 'pipe_probe pipe_dash shell_dash pipe_dash_repeat shell_console', 'FORK_DASH_PIPE_SERIAL', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-serial-wrong', 'pipe_probe pipe_dash shell_dash pipe_dash_repeat shell_console', 'FORK_DASH_PIPE_SERIAL', 2182),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-serial-token', 'pipe_probe pipe_dash shell_dash pipe_dash_repeat shell_console pipe_repeat_token', 'FORK_DASH_PIPE_SERIAL', 2179),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-repeat', 'pipe_probe pipe_dash shell_dash pipe_dash_repeat', 'FORK_DASH_PIPE_REPEAT', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-repeat-token', 'pipe_probe pipe_dash shell_dash pipe_dash_repeat pipe_repeat_token', 'FORK_DASH_PIPE_REPEAT', 2179),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-repeat-receipt', 'pipe_probe pipe_dash shell_dash pipe_dash_repeat pipe_repeat_receipt', 'FORK_DASH_PIPE_REPEAT', 2180),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe', 'pipe_probe pipe_dash shell_dash', 'FORK_DASH_PIPE', None),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-header', 'pipe_probe pipe_dash shell_dash', 'FORK_DASH_PIPE_HEADER', 2174),
                ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-status', 'pipe_probe pipe_dash shell_dash pipe_dash_status', 'FORK_DASH_PIPE', 2176),
                ('copy-inherit-public-fork-wait-pipe', 'pipe_probe', 'FORK_PIPE', None),
                ('copy-inherit-public-fork-wait-pipe-signal', 'pipe_probe pipe_signal', 'FORK_PIPE_SIGNAL', None),
                ('copy-inherit-public-fork-wait-pipe-signal-block', 'pipe_probe pipe_signal', 'FORK_PIPE_SIGNAL_BLOCK', None),
                ('copy-inherit-public-fork-wait-pipe-signal-no-post', 'pipe_probe pipe_signal', 'FORK_PIPE_SIGNAL_NO_POST', 2172),
                ('copy-inherit-public-fork-wait-pipe-signal-no-poll', 'pipe_probe pipe_signal', 'FORK_PIPE_SIGNAL_NO_POLL', 2172),
                ('copy-inherit-public-fork-wait-pipe-stop', 'pipe_probe pipe_stop', 'FORK_PIPE_STOP', None),
                ('copy-inherit-public-fork-wait-pipe-stop-skip', 'pipe_probe pipe_stop pipe_stop_skip', 'FORK_PIPE_STOP', 2171),
                ('copy-inherit-public-fork-wait-pipe-stop-frame', 'pipe_probe pipe_stop pipe_stop_keep_frame', 'FORK_PIPE_STOP', 2166),
                ('copy-inherit-public-fork-wait-pipe-fault', 'pipe_probe pipe_fault', 'FORK_PIPE_FAULT', None),
                ('copy-inherit-public-fork-wait-pipe-fault-frame', 'pipe_probe pipe_fault pipe_fault_keep_frame', 'FORK_PIPE_FAULT', 2166),
                ('copy-inherit-public-fork-wait-pipe-fault-status', 'pipe_probe pipe_fault pipe_fault_as_exit', 'FORK_PIPE_FAULT', 2163),
                ('copy-inherit-public-fork-wait-pipe-lost', 'pipe_probe pipe_reply_lost', 'FORK_PIPE_REPLY_LOSS', None),
                ('copy-inherit-public-fork-wait-pipe-one', 'pipe_probe pipe_reply_one', 'FORK_PIPE_REPLY_LOSS', None),
                ('copy-inherit-public-fork-wait-pipe-short', 'pipe_probe pipe_reply_short', 'FORK_PIPE_REPLY_LOSS', None),
                ('copy-inherit-public-fork-wait-pipe-lost-retain', 'pipe_probe pipe_reply_lost pipe_reply_retain', 'FORK_PIPE_REPLY_LOSS', 2168),
                ('copy-inherit-public-fork-wait-pipe-reply', 'pipe_probe pipe_bad_reply', 'FORK_PIPE_BAD_REPLY', 2167),
                ('copy-inherit-public-fork-wait-pipe-eof', 'pipe_probe pipe_early_eof', 'FORK_PIPE', 2163),
                ('copy-inherit-public-fork-wait-pipe-retained', 'pipe_probe pipe_keep_writer', 'FORK_PIPE', 2164),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-repeat-redirect', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_repeat shell_redirect', 'FORK_CONSOLE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-repeat-redirect-stale', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_repeat shell_redirect', 'FORK_REDIRECT_STALE', 2150),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-repeat-redirect-exec-stale', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_repeat shell_redirect', 'FORK_REDIRECT_EXEC_STALE', 2120),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-repeat', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_repeat', 'FORK_CONSOLE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-repeat-token', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_repeat repeat_token', 'FORK_CONSOLE', 2151),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-repeat-boot', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_repeat repeat_boot', 'FORK_CONSOLE', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-resume', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_resume', 'FORK_CONSOLE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-resume-cleanup', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_resume', 'FORK_CONSOLE_OLD_CLEANUP', 2131),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-resume-exit', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console shell_resume', 'FORK_CONSOLE', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console', 'FORK_CONSOLE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-tee', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console', 'FORK_CONSOLE', 2140),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial-wrong', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_console', 'FORK_CONSOLE', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-pending', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude stream_pending', 'FORK_DISPATCH_LATE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-pending-reply', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude stream_pending pending_reply', 'FORK_DISPATCH_LATE', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-pending-eof', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude stream_pending', 'FORK_DISPATCH_LATE', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-pending-position', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude stream_pending pending_position', 'FORK_DISPATCH_LATE', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash', 'FORK_SHELL_COMMAND', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-legacy', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash', 'FORK_SHELL_COMMAND', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-keep', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash fork_exec_keep', 'FORK_SHELL_COMMAND', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-status', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_wait_status', 'FORK_SHELL_COMMAND', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash', 'FORK_SHELL', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-skip', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash', 'FORK_SHELL_SKIP', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-keep', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash fork_exec_keep', 'FORK_SHELL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-status', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch shell_prelude shell_dash shell_wait_status', 'FORK_SHELL', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude', 'FORK_PRELUDE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-wait', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude prefork_wait', 'FORK_PRELUDE', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch-prefork-foreign', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late shell_prelude prefork_foreign', 'FORK_PRELUDE', 1950),
                ('copy-inherit-public-fork-wait-exec-dispatch', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch', 'FORK_DISPATCH', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-late', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_late', 'FORK_DISPATCH_LATE', None),
                ('copy-inherit-public-fork-wait-exec-dispatch-foreign', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_foreign', 'FORK_DISPATCH', 2130),
                ('copy-inherit-public-fork-wait-exec-dispatch-early', 'inherit_wait fork_exec exec_mask exec_shared fork_dispatch dispatch_early', 'FORK_DISPATCH', 2130),
                ('copy-inherit-public-fork-wait-exec', 'inherit_wait fork_exec exec_mask exec_shared', 'FORK_EXEC', None),
                ('copy-inherit-public-fork-wait-exec-keep', 'inherit_wait fork_exec exec_mask exec_shared fork_exec_keep', 'FORK_EXEC', 1950),
                ('copy-inherit-public-fork-wait-exec-status', 'inherit_wait fork_exec exec_mask exec_shared inherit_wait_bad_status', 'FORK_EXEC', 1950),
                ('copy-inherit-public-fork', None, 'FORK_PUBLIC', None),
                ('copy-inherit-public-fork-wait', 'inherit_wait', 'FORK_WAIT', None),
                ('copy-inherit-public-fork-wait-high', 'inherit_wait inherit_wait_high', 'FORK_WAIT_HIGH', None),
                ('copy-inherit-public-fork-wait-fault', 'inherit_wait inherit_wait_fault', 'FORK_WAIT_FAULT', None),
                ('copy-inherit-public-fork-wait-signal', 'inherit_wait inherit_wait_signal', 'FORK_WAIT_SIGNAL', None),
                ('copy-inherit-public-fork-wait-fault-exit', 'inherit_wait inherit_wait_fault inherit_wait_as_exit', 'FORK_WAIT_FAULT', 1950),
                ('copy-inherit-public-fork-wait-signal-exit', 'inherit_wait inherit_wait_signal inherit_wait_as_exit', 'FORK_WAIT_SIGNAL', 1950),
                ('copy-inherit-public-fork-wait-broken-missing', 'inherit_wait inherit_wait_broken', 'FORK_WAIT_BROKEN', None),
                ('copy-inherit-public-fork-wait-broken-partial', 'inherit_wait inherit_wait_broken inherit_wait_partial', 'FORK_WAIT_BROKEN', None),
                ('copy-inherit-public-fork-wait-broken-body', 'inherit_wait inherit_wait_broken inherit_wait_body', 'FORK_WAIT_BROKEN_PARTIAL', None),
                ('copy-inherit-public-fork-wait-broken-ack-missing', 'inherit_wait inherit_wait_broken inherit_wait_ack', 'FORK_WAIT_BROKEN_ACK', None),
                ('copy-inherit-public-fork-wait-broken-ack-bad', 'inherit_wait inherit_wait_broken inherit_wait_ack inherit_wait_ack_bad', 'FORK_WAIT_BROKEN_ACK', None),
                ('copy-inherit-public-fork-wait-broken-replay', 'inherit_wait inherit_wait_broken', 'FORK_WAIT_BROKEN_REPLAY', 2024),
                ('copy-inherit-public-fork-wait-broken-ack-false', 'inherit_wait inherit_wait_broken inherit_wait_ack inherit_wait_ack_bad', 'FORK_WAIT_BROKEN_FALSE', 2023),
                ('copy-inherit-public-fork-wait4', 'inherit_wait', 'FORK_WAIT4', None),
                ('copy-inherit-public-fork-wait3', 'inherit_wait', 'FORK_WAIT3', None),
                ('copy-inherit-public-fork-wait3-fault', 'inherit_wait inherit_wait_fault', 'FORK_WAIT3_FAULT', None),
                ('copy-inherit-public-fork-wait3-broken-ack', 'inherit_wait inherit_wait_broken inherit_wait_ack inherit_wait_ack_bad', 'FORK_WAIT3_BROKEN', None),
                ('copy-inherit-public-fork-wait4-usage-bad', 'inherit_wait', 'FORK_WAIT4_USAGE_BAD', 1950),
                ('copy-inherit-public-fork-wait-null', 'inherit_wait', 'FORK_WAIT_NULL', None),
                ('copy-inherit-public-fork-wait-status', 'inherit_wait inherit_wait_bad_status', 'FORK_WAIT', 1950),
                ('copy-inherit-public-fork-wait-consume', 'inherit_wait inherit_wait_consume', 'FORK_WAIT', 1950),
                ('copy-inherit-public-fork-live', None, 'FORK_LIVE', None),
                ('copy-inherit-rollback-public-fork-live', 'inherit_rollback', 'FORK_LIVE', None),
                ('copy-inherit-prepare-public-fork-live', 'inherit_prepare', 'FORK_LIVE_DENY', None),
                ('copy-inherit-public-fork-live-order', None, 'FORK_LIVE_ORDER', 1950),
                ('copy-inherit-public-fork-live-no-post', None, 'FORK_LIVE_NO_POST', 1950),
                ('copy-inherit-public-fork-live-repair', None, 'FORK_LIVE', 1950),
                ('copy-inherit-rollback-public-fork', 'inherit_rollback', 'FORK_PUBLIC', None),
                ('copy-inherit-prepare-public-fork', 'inherit_prepare', 'FORK_DENY', None),
                ('copy-inherit-public-fork-flag', None, 'FORK_BAD_FLAG', 1950),
                ('copy-inherit-public-fork-repair', None, 'FORK_PUBLIC', 1950),
                ('copy-inherit', None, None, None),
                ('copy-inherit-scratch', 'scratch_backend', None, None),
                ('copy-inherit-scratch-exec-deny', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_last scratch_exec_deny', 'SCRATCH_EXEC_DENY', None),
                ('copy-inherit-scratch-exec-deny-close', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_last scratch_exec_deny scratch_exec_deny_close', 'SCRATCH_EXEC_DENY', 2510),
                ('copy-inherit-scratch-exec-deny-error', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_last scratch_exec_deny scratch_exec_deny_error', 'SCRATCH_EXEC_DENY', 1950),
                ('copy-inherit-scratch-exec-last', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_last', 'SCRATCH_EXEC_LAST', None),
                ('copy-inherit-scratch-exec-last-skip', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_last scratch_exec_last_skip', 'SCRATCH_EXEC_LAST', 2507),
                ('copy-inherit-scratch-exec-last-wrong', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_last scratch_exec_last_wrong', 'SCRATCH_EXEC_LAST', 1950),
                ('copy-inherit-scratch-exec', 'scratch_backend scratch_client scratch_copy scratch_exec', 'SCRATCH_EXEC', None),
                ('copy-inherit-scratch-exec-keep', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_keep', 'SCRATCH_EXEC', 1950),
                ('copy-inherit-scratch-exec-stale', 'scratch_backend scratch_client scratch_copy scratch_exec scratch_exec_stale', 'SCRATCH_EXEC', 1950),
                ('copy-inherit-scratch-copy', 'scratch_backend scratch_client scratch_copy', 'SCRATCH_COPY', None),
                ('copy-inherit-scratch-copy-offset', 'scratch_backend scratch_client scratch_copy scratch_owner_drop_offset', 'SCRATCH_COPY', 2507),
                ('copy-inherit-scratch-copy-close', 'scratch_backend scratch_client scratch_copy scratch_owner_early_close', 'SCRATCH_COPY', 1950),
                ('copy-inherit-scratch-copy-table', 'scratch_backend scratch_client scratch_copy scratch_copy_bad_snapshot', 'SCRATCH_COPY', 2506),
                ('copy-inherit-scratch-client', 'scratch_backend scratch_client', 'SCRATCH_CLIENT', None),
                ('copy-inherit-scratch-client-offset', 'scratch_backend scratch_client scratch_owner_drop_offset', 'SCRATCH_CLIENT', 1950),
                ('copy-inherit-scratch-client-cloexec', 'scratch_backend scratch_client', 'SCRATCH_CLIENT_BAD_CLOEXEC', 1950),
                ('copy-inherit-scratch-owner', 'scratch_backend scratch_owner_probe', None, None),
                ('copy-inherit-scratch-owner-offset', 'scratch_backend scratch_owner_probe scratch_owner_drop_offset', None, 2503),
                ('copy-inherit-scratch-owner-close', 'scratch_backend scratch_owner_probe scratch_owner_early_close', None, 2503),
                ('copy-inherit-scratch-drop', 'scratch_backend', None, 2502),
                ('copy-inherit-scratch-epoch', 'scratch_backend', None, 2501),
                ('copy-inherit-offset', 'inherit_private_position', None, 1903),
                ('copy-inherit-close', 'inherit_early_close', None, 1952),
                ('copy-inherit-receipt', 'inherit_bad_receipt', None, None),
                ('copy-inherit-completion', 'inherit_bad_completion', None, None),
                ('copy-inherit-stop', 'inherit_stop', None, None),
                ('copy-inherit-receipt-skip', 'inherit_bad_receipt', 'INHERIT_SKIP_RECEIPT', 1961),
                ('copy-inherit-completion-skip', 'inherit_bad_completion', 'INHERIT_SKIP_CHILD_GATE', 1963),
                ('copy-inherit-parent-skip', 'inherit_bad_receipt', 'INHERIT_SKIP_PARENT_GATE', 1962),
                ('copy-inherit-stop-skip', 'inherit_stop inherit_skip_stop', None, 1964),
                ('copy-inherit-rollback', 'inherit_rollback', 'INHERIT_ROLLBACK', None),
                ('copy-inherit-rollback-leak', 'inherit_rollback inherit_rollback_leak', 'INHERIT_ROLLBACK', 1972),
                ('copy-inherit-rollback-close', 'inherit_rollback inherit_rollback_close', 'INHERIT_ROLLBACK', 1952),
                ('copy-inherit-rollback-cancel', 'inherit_rollback inherit_rollback_cancel', 'INHERIT_ROLLBACK', 1973),
                ('copy-inherit-incomplete-receipt-missing', 'inherit_incomplete inherit_receipt_missing', None, None),
                ('copy-inherit-incomplete-receipt-partial', 'inherit_incomplete inherit_receipt_partial', None, None),
                ('copy-inherit-incomplete-ack-missing', 'inherit_incomplete', 'INHERIT_ACK_MISSING', None),
                ('copy-inherit-incomplete-ack-partial', 'inherit_incomplete inherit_ack_partial', 'INHERIT_ACK_PARTIAL', None),
                ('copy-inherit-incomplete-ack-pad', 'inherit_incomplete inherit_ack_partial inherit_pad_ack', 'INHERIT_ACK_PARTIAL', 1982),
                ('copy-inherit-incomplete-stop-skip', 'inherit_incomplete inherit_incomplete_skip_stop', 'INHERIT_ACK_MISSING', 1981),
                ('copy-inherit-uncertain', 'inherit_uncertain', 'INHERIT_UNCERTAIN', None),
                ('copy-inherit-uncertain-alias', 'inherit_uncertain inherit_uncertain_alias', 'INHERIT_UNCERTAIN', 1992),
                ('copy-inherit-uncertain-stop', 'inherit_uncertain inherit_uncertain_skip_stop', 'INHERIT_UNCERTAIN', 1993),
                ('copy-inherit-uncertain-missing', 'inherit_uncertain inherit_backend_incomplete', 'INHERIT_UNCERTAIN', None),
                ('copy-inherit-uncertain-partial', 'inherit_uncertain inherit_backend_incomplete inherit_backend_partial', 'INHERIT_UNCERTAIN', None),
                ('copy-inherit-uncertain-partial-pad', 'inherit_uncertain inherit_backend_incomplete inherit_backend_partial inherit_backend_pad', 'INHERIT_UNCERTAIN', 1992),
                ('copy-inherit-uncertain-missing-stop', 'inherit_uncertain inherit_backend_incomplete inherit_uncertain_skip_stop', 'INHERIT_UNCERTAIN', 1993),
                ('copy-inherit-uncertain-write', 'inherit_uncertain inherit_write', 'INHERIT_UNCERTAIN_WRITE', None),
                ('copy-inherit-uncertain-write-replay', 'inherit_uncertain inherit_write inherit_write_replay', 'INHERIT_UNCERTAIN_WRITE', 1994),
                ('copy-inherit-uncertain-write-stop', 'inherit_uncertain inherit_write inherit_uncertain_skip_stop', 'INHERIT_UNCERTAIN_WRITE', 1993),
                ('copy-inherit-uncertain-close', 'inherit_uncertain inherit_close', 'INHERIT_UNCERTAIN_CLOSE', None),
                ('copy-inherit-uncertain-close-success', 'inherit_uncertain inherit_close inherit_close_success', 'INHERIT_UNCERTAIN_CLOSE', 1996),
                ('copy-inherit-uncertain-close-replay', 'inherit_uncertain inherit_close inherit_close_replay', 'INHERIT_UNCERTAIN_CLOSE', 1995),
                ('copy-inherit-uncertain-close-stop', 'inherit_uncertain inherit_close inherit_uncertain_skip_stop', 'INHERIT_UNCERTAIN_CLOSE', 1993),
                ('copy-inherit-uncertain-write-missing', 'inherit_uncertain inherit_write inherit_backend_incomplete', 'INHERIT_UNCERTAIN_WRITE', None),
                ('copy-inherit-uncertain-write-partial', 'inherit_uncertain inherit_write inherit_backend_incomplete inherit_backend_partial', 'INHERIT_UNCERTAIN_WRITE', None),
                ('copy-inherit-uncertain-write-partial-pad', 'inherit_uncertain inherit_write inherit_backend_incomplete inherit_backend_partial inherit_backend_pad', 'INHERIT_UNCERTAIN_WRITE', 1992),
                ('copy-inherit-uncertain-write-missing-stop', 'inherit_uncertain inherit_write inherit_backend_incomplete inherit_uncertain_skip_stop', 'INHERIT_UNCERTAIN_WRITE', 1993),
                ('copy-inherit-uncertain-close-missing', 'inherit_uncertain inherit_close inherit_backend_incomplete', 'INHERIT_UNCERTAIN_CLOSE', None),
                ('copy-inherit-uncertain-close-partial', 'inherit_uncertain inherit_close inherit_backend_incomplete inherit_backend_partial', 'INHERIT_UNCERTAIN_CLOSE', None),
                ('copy-inherit-uncertain-close-partial-pad', 'inherit_uncertain inherit_close inherit_backend_incomplete inherit_backend_partial inherit_backend_pad', 'INHERIT_UNCERTAIN_CLOSE', 1996),
                ('copy-inherit-uncertain-close-missing-stop', 'inherit_uncertain inherit_close inherit_backend_incomplete inherit_uncertain_skip_stop', 'INHERIT_UNCERTAIN_CLOSE', 1993),
                ('copy-inherit-final-child-missing', 'inherit_final', None, None),
                ('copy-inherit-final-child-partial', 'inherit_final inherit_final_partial', None, None),
                ('copy-inherit-final-parent-missing', 'inherit_final inherit_final_parent', None, None),
                ('copy-inherit-final-parent-partial', 'inherit_final inherit_final_parent inherit_final_partial', None, None),
                ('copy-inherit-final-child-pad', 'inherit_final inherit_final_partial', 'INHERIT_FINAL_PAD', 2001),
                ('copy-inherit-final-parent-pad', 'inherit_final inherit_final_parent inherit_final_partial', 'INHERIT_FINAL_PAD', 2001),
                ('copy-inherit-final-parent-stop', 'inherit_final inherit_final_skip_parent', None, 2002),
                ('copy-inherit-final-child-stop', 'inherit_final inherit_final_skip_child', None, 2003),
                ('copy-inherit-prepare-present', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=1', None),
                ('copy-inherit-prepare-flags', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=2', None),
                ('copy-inherit-prepare-binding', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=3', None),
                ('copy-inherit-prepare-absent', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=4', None),
                ('copy-inherit-prepare-counts', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=5', None),
                ('copy-inherit-prepare-dead', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=6', None),
                ('copy-inherit-prepare-rights', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=7', None),
                ('copy-inherit-prepare-reference', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=8', None),
                ('copy-inherit-prepare-poison', 'inherit_prepare', 'INHERIT_PREPARE_FAULT=9', None),
                ('copy-inherit-prepare-skip', 'inherit_prepare', 'INHERIT_PREPARE_SKIP', 2010),
                ('copy-inherit-prepare-reserve', 'inherit_prepare inherit_prepare_reserve', 'INHERIT_PREPARE_FAULT=5', 2011),
                ('copy-inherit-mask', None, 'INHERIT_MASK_SEED', None),
                ('copy-inherit-signal', None, 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-incomplete-receipt-missing', 'inherit_incomplete inherit_receipt_missing', 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-incomplete-receipt-partial', 'inherit_incomplete inherit_receipt_partial', 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-incomplete-ack-missing', 'inherit_incomplete', 'INHERIT_SIGNAL_ACK_MISSING', None),
                ('copy-inherit-signal-incomplete-ack-partial', 'inherit_incomplete inherit_ack_partial', 'INHERIT_SIGNAL_ACK_PARTIAL', None),
                ('copy-inherit-signal-incomplete-ack-pad', 'inherit_incomplete inherit_ack_partial inherit_pad_ack', 'INHERIT_SIGNAL_ACK_PARTIAL', 1982),
                ('copy-inherit-signal-incomplete-stop-skip', 'inherit_incomplete inherit_incomplete_skip_stop', 'INHERIT_SIGNAL_ACK_MISSING', 1981),
                ('copy-inherit-signal-final-child-missing', 'inherit_final', 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-final-child-partial', 'inherit_final inherit_final_partial', 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-final-parent-missing', 'inherit_final inherit_final_parent', 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-final-parent-partial', 'inherit_final inherit_final_parent inherit_final_partial', 'INHERIT_SIGNAL', None),
                ('copy-inherit-signal-final-child-pad', 'inherit_final inherit_final_partial', 'INHERIT_SIGNAL_FINAL_PAD', 2001),
                ('copy-inherit-signal-final-parent-pad', 'inherit_final inherit_final_parent inherit_final_partial', 'INHERIT_SIGNAL_FINAL_PAD', 2001),
                ('copy-inherit-signal-final-parent-stop', 'inherit_final inherit_final_skip_parent', 'INHERIT_SIGNAL', 2002),
                ('copy-inherit-signal-final-child-stop', 'inherit_final inherit_final_skip_child', 'INHERIT_SIGNAL', 2003),
                ('copy-inherit-prepare-signal', 'inherit_prepare', 'INHERIT_SIGNAL_REJECT_PREPARE', None),
                ('copy-inherit-signal-receipt', 'inherit_bad_receipt', 'INHERIT_SIGNAL_ABORT', None),
                ('copy-inherit-signal-completion', 'inherit_bad_completion', 'INHERIT_SIGNAL_ABORT', None),
                ('copy-inherit-prepare-signal-skip', 'inherit_prepare', 'INHERIT_SIGNAL_REJECT_PREPARE_SKIP', 2010),
                ('copy-inherit-prepare-signal-fd', 'inherit_prepare', 'INHERIT_SIGNAL_REJECT_PREPARE_FD', 2010),
                ('copy-inherit-signal-receipt-skip', 'inherit_bad_receipt', 'INHERIT_SIGNAL_ABORT_SKIP', 1960),
                ('copy-inherit-signal-completion-skip', 'inherit_bad_completion', 'INHERIT_SIGNAL_ABORT_SKIP', 1960),
                ('copy-inherit-signal-receipt-fd', 'inherit_bad_receipt', 'INHERIT_SIGNAL_ABORT_FD', 1960),
                ('copy-inherit-rollback-signal', 'inherit_rollback', 'INHERIT_SIGNAL_ROLLBACK', None),
                ('copy-inherit-signal-early', None, 'INHERIT_SIGNAL_EARLY', 1950),
                ('copy-inherit-signal-reference', None, 'INHERIT_SIGNAL_REF', 1950),
                ('copy-inherit-signal-no-post', None, 'INHERIT_SIGNAL_NO_POST', 1950),
                ('copy-inherit-signal-outcome', None, 'INHERIT_SIGNAL_OUTCOME', 1950),
                ('copy-inherit-prepare-mask', 'inherit_prepare', 'INHERIT_MASK_PREPARE', None),
                ('copy-inherit-rollback-mask', 'inherit_rollback', 'INHERIT_MASK_ROLLBACK', None),
                ('copy-inherit-mask-receipt', 'inherit_bad_receipt', 'INHERIT_MASK_SEED', None),
                ('copy-inherit-mask-entry-skip', 'inherit_prepare', 'INHERIT_MASK_SKIP_ENTER', 2010),
                ('copy-inherit-mask-reject-skip', 'inherit_prepare', 'INHERIT_MASK_SKIP_REJECT', 2010),
                ('copy-inherit-mask-parent-skip', None, 'INHERIT_MASK_SKIP_PARENT', 1950),
                ('copy-inherit-mask-child-skip', None, 'INHERIT_MASK_SKIP_CHILD', 1950),
            ]
            for label, config, define, failure in inherit_cases:
                client_image = target
                if define:
                    client_obj = out / (label + '.o'); client_image = out / (label + '.elf')
                    command(cc + flags + (['-DAETHER_SUBSTITUTION_SCRIPT=' + json.dumps((substitution_input / 'substitution.sh').read_text())] if 'pipe_consumer' in (config or '').split() else []) + (['-DAETHER_FILE_SCRIPT=' + json.dumps((scratch_input / ('denied-redirection.sh' if 'shell_files_denied' in (config or '').split() else 'redirection.sh' if 'shell_files_redirect' in (config or '').split() else 'fd-leak-control.sh')).read_text())] if 'shell_files' in (config or '').split() else []) + (['-DAETHER_FAILED_SCRIPT=' + json.dumps((ROOT / 'user/native-command/dash-failed-inputs/failed-exec.sh').read_text())] if 'shell_failed_exec' in (config or '').split() else []) + (['-DAETHER_WAIT_SCRIPT=' + json.dumps((ROOT / 'user/native-command/dash-wait-inputs/wait.sh').read_text())] if 'shell_wait' in (config or '').split() else []) + (['-Dmain=__wrap_main'] if 'shell_dash' in (config or '').split() else []) + ['-D' + define, '-c', 'user/native-connections/fork-client.c' if 'public-fork' in label else 'user/native-connections/inherit-client.c', '-o', str(client_obj)], label + '-client')
                    argv = [str(client_obj) if v == str(obj) else v.replace(str(out / 'inherit-client.map'), str(out / (label + '.map'))) for v in inherit_link]
                    argv[argv.index('-o') + 1] = str(client_image)
                    if 'public-fork' in label:
                        argv = [str(fork_rebind) if v == str(out / 'copy-rebind-hook.o') else v for v in argv]
                        at_libc = argv.index(str(lib / 'libc.a'))
                        argv[at_libc:at_libc] = [str(fork_root / 'fork.o'), str(fork_root / ('_Fork-no-repair.o' if label.endswith('-repair') else '_Fork.o'))]
                    if 'public-fork-wait' in label:
                        argv.insert(argv.index(str(lib / 'libc.a')), str(fork_root / 'waitpid.o'))
                    if 'public-fork-wait-exec' in label:
                        argv.insert(argv.index(str(lib / 'libc.a')), str(exec_object))
                    if 'public-fork-wait3' in label or 'public-fork-wait4' in label or 'shell_dash' in (config or '').split():
                        at_libc = argv.index(str(lib / 'libc.a'))
                        argv[at_libc:at_libc] = [str(fork_root / 'wait3.o'), str(fork_root / ('wait4-bad-usage.o' if label.endswith('-usage-bad') else 'wait4.o'))]
                    if 'shell_dash' in (config or '').split():
                        dash = ROOT / 'user/native-command/dash-inputs'
                        objects = json.loads((dash / 'libc-imports.json').read_text())['objects']
                        for name, digest in objects.items():
                            if sha(dash / name) != digest:
                                raise RuntimeError('dash object drift: ' + name)
                        at_libc = argv.index(str(lib / 'libc.a'))
                        argv[at_libc:at_libc] = [str(dash / name) for name in sorted(objects)]
                        replacement = ROOT / 'user/native-command/dash-main-inputs'
                        pin = json.loads((replacement / 'pin.json').read_text())
                        if sha(replacement / 'main.o') != pin['sha256']:
                            raise RuntimeError('native dash main object drift')
                        argv[argv.index(str(dash / 'obj/src/main.o'))] = str(replacement / 'main.o')
                        if '-dash-command' in label and not label.endswith('-legacy'):
                            native_jobs = ROOT / 'user/native-command/dash-fork-inputs'
                            jobs_pin = json.loads((native_jobs / 'pin.json').read_text())
                            if sha(native_jobs / 'jobs.o') != jobs_pin['sha256']:
                                raise RuntimeError('native dash jobs object drift')
                            argv[argv.index(str(dash / 'obj/src/jobs.o'))] = str(native_jobs / 'jobs.o')
                        if 'shell_console' in (config or '').split() and not label.endswith('-tee'):
                            native_input = ROOT / 'user/native-command/dash-input-native'
                            input_pin = json.loads((native_input / 'pin.json').read_text())
                            if sha(native_input / 'input.o') != input_pin['sha256']:
                                raise RuntimeError('native dash input object drift')
                            argv[argv.index(str(dash / 'obj/src/input.o'))] = str(native_input / 'input.o')
                        argv += ['-Wl,--wrap=main', '-Wl,--wrap=_exit']
                    command(argv, label + '-link')
                raw = out / (label + '.raw'); argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                large_owner = any(flag in (config or '').split() for flag in ('shell_prelude', 'pipe_probe', 'scratch_owner_probe', 'scratch_client'))
                if large_owner:
                    argv = [v.replace('user/native-process/program-linker.ld', 'user/native-connections/large-linker.ld') for v in argv]
                command(argv + ['--cfg', 'process_inherit'] + [v for cfg in (config.split() if config else []) for v in ('--cfg', cfg)], label + '-supervisor')
                selected_backend = incomplete_backends['write'] if 'inherit_write' in (config or '').split() else incomplete_backends['close'] if 'inherit_close' in (config or '').split() else incomplete_backends['partial'] if 'inherit_backend_partial' in (config or '').split() else incomplete_backends['missing'] if 'inherit_backend_incomplete' in (config or '').split() else uncertain_backend if label.startswith('copy-inherit-uncertain') else backend_image
                if 'inherit_backend_incomplete' in (config or '').split():
                    operation = 'write-' if 'inherit_write' in config.split() else 'close-' if 'inherit_close' in config.split() else ''
                    selected_backend = incomplete_backends[operation + ('partial' if 'inherit_backend_partial' in config.split() else 'missing')]
                if 'shell_console' in (config or '').split():
                    selected_backend = pending_backends['console-repeat' if 'shell_repeat' in config.split() else 'console']
                if 'stream_pending' in (config or '').split():
                    selected_backend = pending_backends['pending-eof' if label.endswith('-eof') else 'pending']
                if 'scratch_backend' in (config or '').split():
                    selected_backend = scratch_backends['scratch' if any(flag in config.split() for flag in ('scratch_owner_probe', 'scratch_client', 'shell_files')) else label.removeprefix('copy-inherit-')]
                a = client_image.read_bytes(); b = selected_backend.read_bytes(); code = raw.read_bytes()
                if not 0 < len(code) <= (16384 if large_owner else 8192): raise RuntimeError('inherit supervisor bound')
                c = exec_stream_images[31 if 'pipe_consumer_skip' in config.split() else 30] if 'pipe_consumer' in (config or '').split() else exec_stream_images[29 if 'shell_files_skip_helper' in config.split() else 28] if 'shell_files' in (config or '').split() else exec_stream_images[27] if 'shell_null' in (config or '').split() else exec_stream_images[26 if 'shell_closed_leak' in config.split() else 25] if 'shell_closed' in (config or '').split() else exec_stream_images[24 if 'shell_argv_skip' in config.split() else 23] if 'shell_argv' in (config or '').split() else exec_stream_images[22] if 'pipe_exec_serial' in (config or '').split() else exec_stream_images[21] if 'pipe_exec' in (config or '').split() else exec_stream_images[20] if 'shell_repeat' in (config or '').split() else exec_stream_images[19] if 'shell_console' in (config or '').split() else exec_stream_images[18] if 'stream_pending' in (config or '').split() else exec_stream_images[17] if 'shell_dash' in (config or '').split() else exec_stream_images[16] if 'fork_dispatch' in (config or '').split() and 'dispatch_late' not in config.split() else exec_stream_images[15] if 'fork_exec' in (config or '').split() else b
                if 'scratch_exec' in (config or '').split(): c = a
                payload = struct.pack('<8sIIIIII', b'AENMX003' if 'shell_console' in (config or '').split() else b'AENMX002' if large_owner else b'AENMX001', len(a), len(b), len(c), len(code), 0, 0) + entropy + a + b + c + code
                context = (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),) if failure else ()
                if label == 'copy-inherit-scratch-exec-deny-error':
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=251', b'NATIVE supervisor result=1950 reclaimed=0')
                if label in ('copy-inherit-scratch-exec-keep', 'copy-inherit-scratch-exec-stale', 'copy-inherit-scratch-exec-last-wrong'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=254', b'NATIVE supervisor result=1950 reclaimed=0')
                if label == 'copy-inherit-scratch-copy-close':
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=251', b'NATIVE supervisor result=1950 reclaimed=0')
                if label.startswith('copy-inherit-scratch-client-'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=252', b'NATIVE supervisor result=1950 reclaimed=0')
                if label == 'copy-inherit-scratch-epoch':
                    context = (b'NATIVE supervisor result=2501 reclaimed=3',)
                if 'pipe_dash_repeat' in (config or '').split() and failure:
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=0', f'NATIVE supervisor result={failure} reclaimed=1'.encode())
                    if label.endswith('-receipt'):
                        context = (context[0], b'NATIVE terminal slot=2 generation=2 kind=1 detail=80', context[1])
                if 'pipe_exec' in (config or '').split() and 'pipe_exec_serial' not in config.split() and failure:
                    context = ((b'NATIVE terminal slot=2 generation=1 kind=1 detail=227',) if label.endswith('-drop') else ()) + (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),)
                if 'pipe_consumer' in (config or '').split() and failure:
                    context = (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),)
                if 'pipe_exec_serial_grant' in (config or '').split():
                    context = (context[0], b'NATIVE terminal slot=2 generation=2 kind=1 detail=227', context[1])
                if 'shell_argv' in (config or '').split() and failure:
                    context = (f'NATIVE terminal slot=2 generation=1 kind=1 detail={0 if label.endswith("-skip") else 91}'.encode(), f'NATIVE supervisor result={failure} reclaimed=0'.encode())
                if 'shell_closed' in (config or '').split() and failure:
                    context = ((b'NATIVE terminal slot=2 generation=1 kind=1 detail=95',) if label.endswith('-leak') else (b'NATIVE terminal slot=2 generation=1 kind=1 detail=0',)) + (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),)
                if 'shell_null' in (config or '').split() and failure:
                    context = (f'NATIVE terminal slot=2 generation=1 kind=1 detail={2 if label.endswith("-handle") else 231 if label.endswith("-rollback") else 229 if label.endswith("-mask") else 225 if label.endswith("-stale") else 226 if label.endswith("-limit") else 224}'.encode(), f'NATIVE supervisor result={failure} reclaimed=0'.encode())
                if label.endswith('-suspend-frame-valid'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=72', b'NATIVE terminal slot=0 generation=1 kind=1 detail=238', b'NATIVE supervisor result=1950 reclaimed=0')
                if label.endswith('-suspend-stale-post'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=72', b'NATIVE terminal slot=1 generation=1 kind=1 detail=17', b'NATIVE terminal slot=0 generation=2 kind=1 detail=237', b'NATIVE supervisor result=1950 reclaimed=3')
                if label.endswith('-suspend-repeat-post'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=72', b'NATIVE terminal slot=0 generation=1 kind=1 detail=236', b'NATIVE supervisor result=1950 reclaimed=0')
                if label.endswith('-null-wait-disabled'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=233', b'NATIVE supervisor result=1950 reclaimed=0')
                if 'null_fault' in (config or '').split() and failure:
                    context = (b'NATIVE terminal slot=2 generation=1 kind=2 detail=134', f'NATIVE supervisor result={failure} reclaimed=0'.encode())
                if 'dash_signal' in (config or '').split() and failure:
                    context = ((b'NATIVE terminal slot=0 generation=1 kind=4 detail=10' if label.endswith('-scope') else b'NATIVE terminal slot=2 generation=1 kind=1 detail=0'), f'NATIVE supervisor result={failure} reclaimed=0'.encode())
                if label == 'copy-inherit-public-fork-wait-prefork-dash-command-pipe-serial-wrong':
                    context = (b'NATIVE supervisor result=2182 reclaimed=0',)
                if label == 'copy-inherit-public-fork-wait-pipe-reply':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=92', b'NATIVE supervisor result=2167 reclaimed=0')
                if label in ('copy-inherit-public-fork-wait-pipe-signal-no-post', 'copy-inherit-public-fork-wait-pipe-signal-no-poll'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=94', b'NATIVE supervisor result=2172 reclaimed=0')
                if label == 'copy-inherit-public-fork-wait-pipe-stop-frame':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=0', b'NATIVE supervisor result=2166 reclaimed=0')
                if label in ('copy-inherit-public-fork-wait-pipe-fault-frame', 'copy-inherit-public-fork-wait-pipe-fault-status'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=2 detail=134',
                               f'NATIVE terminal slot=0 generation=1 kind=1 detail={90 if label.endswith("-status") else 0}'.encode(),
                               f'NATIVE supervisor result={failure} reclaimed=0'.encode())
                if label == 'copy-inherit-public-fork-wait-pipe-lost-retain':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=92', b'NATIVE supervisor result=2168 reclaimed=0')
                if label == 'copy-inherit-public-fork-wait-pipe-eof':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=90', b'NATIVE supervisor result=2163 reclaimed=0')
                if label == 'copy-inherit-public-fork-wait-pipe-retained':
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=0', b'NATIVE supervisor result=2164 reclaimed=0')
                if '-serial-repeat' in label and failure:
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=72', f'NATIVE supervisor result={failure} reclaimed=1'.encode())
                    if label.endswith('-boot'):
                        context = (context[0], b'NATIVE terminal slot=2 generation=2 kind=1 detail=224', context[1])
                if label.endswith('-redirect-stale'):
                    context = (b'NATIVE supervisor result=2150 reclaimed=0',)
                if label.endswith('-redirect-exec-stale'):
                    context = (b'NATIVE supervisor result=2120 reclaimed=0',)
                if label.endswith('-resume-cleanup'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=0', b'NATIVE supervisor result=2131 reclaimed=0')
                if label.endswith('-resume-exit'):
                    context = (b'NATIVE terminal slot=0 generation=2 kind=1 detail=8', b'NATIVE supervisor result=2130 reclaimed=2')
                if 'stream_pending' in (config or '').split() and failure:
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=85', *context)
                if 'pipe_dash' in (config or '').split() and label.endswith('-status'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=1', *context)
                if 'shell_dash' in (config or '').split() and 'pipe_dash' not in (config or '').split() and 'shell_argv' not in (config or '').split() and failure and not label.endswith(('-tee', '-resume-cleanup', '-resume-exit')):
                    slot, detail = (2, 224) if label.endswith(('-keep', '-serial-wrong')) else (0, 73) if label.endswith('-status') else (0, 2) if label.endswith('-legacy') else (0, 72)
                    context = (f'NATIVE terminal slot={slot} generation=1 kind=1 detail={detail}'.encode(), *context)
                if label in ('copy-inherit-public-fork-wait-exec-dispatch-prefork-wait', 'copy-inherit-public-fork-wait-exec-dispatch-prefork-foreign'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=86', *context)
                if label in ('copy-inherit-public-fork-wait-exec-dispatch-foreign', 'copy-inherit-public-fork-wait-exec-dispatch-early'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=85', *context)
                if label == 'copy-inherit-public-fork-wait-exec-keep':
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=216', *context)
                if label == 'copy-inherit-public-fork-wait-exec-status':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=82', *context)
                if label in ('copy-inherit-public-fork-live-order', 'copy-inherit-public-fork-live-no-post', 'copy-inherit-public-fork-live-repair'):
                    slot = 0 if label.endswith('-order') else 2
                    context = (f'NATIVE terminal slot={slot} generation=1 kind=1 detail=81'.encode(), *context)
                if label in ('copy-inherit-public-fork-wait4-usage-bad', 'copy-inherit-public-fork-wait-broken-ack-false', 'copy-inherit-public-fork-wait-status', 'copy-inherit-public-fork-wait-consume', 'copy-inherit-public-fork-wait-fault-exit', 'copy-inherit-public-fork-wait-signal-exit'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=82', *context)
                if label in ('copy-inherit-public-fork-flag', 'copy-inherit-public-fork-repair'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=80', *context)
                if label == 'copy-inherit-uncertain-alias':
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=254', *context)
                if label in ('copy-inherit-uncertain-partial-pad', 'copy-inherit-uncertain-write-partial-pad'):
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=254', *context)
                if label in ('copy-inherit-uncertain-write-replay', 'copy-inherit-uncertain-close-replay'):
                    context = (b'NATIVE terminal slot=1 generation=1 kind=1 detail=124', *context)
                if label in ('copy-inherit-prepare-signal-skip', 'copy-inherit-prepare-signal-fd', 'copy-inherit-signal-receipt-skip', 'copy-inherit-signal-completion-skip', 'copy-inherit-signal-receipt-fd'):
                    slot = 0 if label.startswith('copy-inherit-prepare') else 2
                    context = (f'NATIVE terminal slot={slot} generation=1 kind=1 detail=79'.encode(), *context)
                if label in ('copy-inherit-signal-early', 'copy-inherit-signal-reference', 'copy-inherit-signal-no-post', 'copy-inherit-signal-outcome'):
                    slot = 0 if label.endswith(('-early', '-outcome')) else 2
                    context = (f'NATIVE terminal slot={slot} generation=1 kind=1 detail=79'.encode(), *context)
                if label in ('copy-inherit-mask-entry-skip', 'copy-inherit-mask-reject-skip', 'copy-inherit-mask-parent-skip', 'copy-inherit-mask-child-skip'):
                    context = (f'NATIVE terminal slot={2 if label == "copy-inherit-mask-child-skip" else 0} generation=1 kind=1 detail=79'.encode(), *context)
                if label == 'copy-inherit-prepare-reserve':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=78', *context)
                if label in ('copy-inherit-uncertain-close-success', 'copy-inherit-uncertain-close-partial-pad'):
                    context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=255', *context)
                if 'shell_failed_exec' in (config or '').split() and failure:
                    terminals = [(1, 126)] if label.endswith('-missing') else [(1, 127), (2, 127 if label.endswith('-denied') else 226)] if label.endswith(('-denied', '-skip')) else [(1, 127), (2, 126)] if label.endswith('-output') else [(1, 127)]
                    reclaimed = 1 if label.endswith(('-denied', '-skip')) else 2 if label.endswith('-output') else 0
                    context = tuple(f'NATIVE terminal slot=2 generation={gen} kind=1 detail={status}'.encode() for gen, status in terminals) + (f'NATIVE supervisor result={failure} reclaimed={reclaimed}'.encode(),)
                if 'shell_files' in (config or '').split() and failure:
                    detail = 80 if label.endswith('-grant') else 224 if label.endswith('-description') else 0
                    context = (f'NATIVE terminal slot=2 generation=1 kind=1 detail={detail}'.encode(),
                               f'NATIVE supervisor result={failure} reclaimed=0'.encode())
                if 'shell_files_redirect' in (config or '').split() and failure:
                    context = (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),)
                    if label.endswith('-stdin'):
                        context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=0',
                                   b'NATIVE terminal slot=0 generation=1 kind=1 detail=0', *context)
                if 'shell_files_denied' in (config or '').split() and failure:
                    context = (f'NATIVE supervisor result={failure} reclaimed=0'.encode(),)
                cases.append((label, payload, b'native C profile rejected' if failure else None, context))
                if label == 'copy-inherit-public-fork-wait-exec-dispatch-prefork':
                    if len(code) <= 8192: raise RuntimeError('large owner witness must cross old bound')
                    cases.append((label + '-legacy-capacity', b'AENMX001' + payload[8:], b'invalid launch envelope', ()))
                    for size in (16383, 16384):
                        padded = bytearray(payload)
                        struct.pack_into('<I', padded, 20, size)
                        padded += bytes(size - len(code))
                        cases.append((label + '-capacity-' + str(size), bytes(padded), None, ()))

                    oversized = bytearray(payload)
                    struct.pack_into('<I', oversized, 20, 16385)
                    oversized += bytes(16385 - len(code))
                    cases.append((label + '-oversize', bytes(oversized), b'invalid launch envelope', ()))

        if shared_files and not file_io:
            cases=[('positive',base,None,())]
            parent_images=list(images)
            for number, original_link in ((1,requester_link),(3,link_command)):
                obj=out/f'parent-first-{number}.o';target=out/f'parent-first-{number}.elf'
                command(cc+flags+['-DPARENT_FIRST',f'-DHELPER={number}','-c',source+('/program.c' if number==3 else '/helper.c'),'-o',str(obj)],f'parent-first-{number}-compile')
                argv=[str(obj) if v==str(out/f'helper{number}.o') else v for v in original_link];argv[argv.index('-o')+1]=str(target);command(argv,f'parent-first-{number}-link');parent_images[number-1]=target.read_bytes()
            argv=list(supervisor_command);target=out/'parent-first.raw';argv[argv.index('-o')+1]=str(target);argv+=['--cfg','parent_first'];command(argv,'parent-first-supervisor');variant=target.read_bytes()
            if not 0<len(variant)<=8192:raise RuntimeError('shared supervisor image bound')
            payload=struct.pack('<8sIIIIII',b'AENMX001',*[len(v) for v in parent_images],len(variant),0,0)+entropy+b''.join(parent_images)+variant
            cases.append(('parent-first',payload,None,()))
            for label,config,detail,worker in [('frozen-offset','frozen_offset',970,239),('early-close','early_close',970,239),('wide-rights','wide_rights',970,237),('leak-close','leak_close',975,None)]:
                argv=list(supervisor_command);target=out/(label+'.raw');argv[argv.index('-o')+1]=str(target);argv+=['--cfg',config];command(argv,label+'-supervisor')
                variant=target.read_bytes()
                if not 0<len(variant)<=8192:raise RuntimeError('shared supervisor image bound')
                payload=struct.pack('<8sIIIIII',b'AENMX001',len(images[0]),len(images[1]),len(images[2]),len(variant),0,0)+entropy+b''.join(images)+variant
                context=(f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)
                if worker:context=(f'NATIVE terminal slot={2 if label == "wide-rights" else 0} generation=1 kind=1 detail={worker}'.encode(),)+context
                cases.append((label,payload,b'native C profile rejected',context))
        if inherited_launch and not file_io:
            cases=[c for c in cases if c[0] in ('positive','parent-first')]
            obj=out/'reject-launch.o';target=out/'reject-launch.elf'
            command(cc+flags+['-DREJECT_LAUNCH','-DHELPER=1','-c',source+'/helper.c','-o',str(obj)],'reject-launch-compile')
            argv=[str(obj) if v==str(out/'helper1.o') else v for v in requester_link];argv[argv.index('-o')+1]=str(target);command(argv,'reject-launch-link');rejected_images=[target.read_bytes(),images[1],images[2]]
            obj=out/'partial-reservation.o';target=out/'partial-reservation.elf'
            command(cc+flags+['-DREJECT_CAPACITY','-DHELPER=1','-c',source+'/helper.c','-o',str(obj)],'partial-reservation-compile')
            argv=[str(obj) if v==str(out/'helper1.o') else v for v in requester_link];argv[argv.index('-o')+1]=str(target);command(argv,'partial-reservation-link');capacity_images=[target.read_bytes(),images[1],images[2]]
            for label,config,detail,worker in [('rejected-launch','reject_launch',None,None),('partial-reservation','partial_reservation',None,None),('leaked-reservation','leak_reservation',970,245),('leaked-admission','leak_admission',970,245),('allow-child-write','allow_widen',970,243),('wrong-status','wrong_status',970,249),('repeat-status','repeat_status',970,250)]:
                argv=list(supervisor_command);target=out/(label+'.raw');argv[argv.index('-o')+1]=str(target);argv+=['--cfg',config];command(argv,label+'-supervisor');variant=target.read_bytes()
                if not 0<len(variant)<=8192:raise RuntimeError('inherited supervisor image bound')
                selected=capacity_images if label in ('partial-reservation','leaked-reservation') else rejected_images if label in ('rejected-launch','leaked-admission') else images
                payload=struct.pack('<8sIIIIII',b'AENMX001',*[len(v) for v in selected],len(variant),0,0)+entropy+b''.join(selected)+variant
                context=() if detail is None else (f'NATIVE terminal slot=0 generation=1 kind=1 detail={worker}'.encode(),f'NATIVE supervisor result={detail} reclaimed=0'.encode())
                cases.append((label,payload,None if detail is None else b'native C profile rejected',context))
        if file_io:
            cases=[('positive',base,None,())]
            for label,config,detail,slot,worker in [('frozen-offset','frozen_offset',970,2,204),('zero-consumes','zero_consumes',970,0,203),('wide-rights','wide_rights',970,2,201),('skip-write','skip_write',985,None,None)]:
                argv=list(supervisor_command);target=out/(label+'.raw');argv[argv.index('-o')+1]=str(target);argv+=['--cfg',config];command(argv,label+'-supervisor');variant=target.read_bytes()
                if not 0<len(variant)<=8192:raise RuntimeError('file I/O supervisor image bound')
                payload=struct.pack('<8sIIIIII',b'AENMX001',*[len(v) for v in images],len(variant),0,0)+entropy+b''.join(images)+variant
                context=(f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)
                if worker:context=(f'NATIVE terminal slot={slot} generation=1 kind=1 detail={worker}'.encode(),)+context
                cases.append((label,payload,b'native C profile rejected',context))
        if command_runner:
            cases=[('positive',base,None,())]
            argv=list(service_command);target=out/'empty-service.a';argv[argv.index('-o')+1]=str(target);argv+=['--cfg','empty_input'];command(argv,'empty-service')
            argv=[str(target) if v==str(out/'service.a') else v for v in service_link];target=out/'empty-backend.elf';argv[argv.index('-o')+1]=str(target);command(argv,'empty-backend')
            cases.append(('empty-input',envelope(images[0],target.read_bytes(),images[2]),None,()))
            parents={}
            for label,define in [('rejected-launch','REJECT_LAUNCH'),('partial-reservation','REJECT_CAPACITY'),('full-output','FULL_OUTPUT')]:
                obj=out/(label+'-parent.o');target=out/(label+'-parent.elf')
                command(cc+flags+['-D'+define,'-DHELPER=1','-c',source+'/helper.c','-o',str(obj)],label+'-parent-compile')
                argv=[str(obj) if v==str(out/'helper1.o') else v for v in requester_link];argv[argv.index('-o')+1]=str(target);command(argv,label+'-parent-link');parents[label]=target.read_bytes()
            for label,config,detail,worker in [('rejected-launch','reject_launch',None,None),('partial-reservation','partial_reservation',None,None),('short-write','short_write',None,None),('full-output','full_output',None,None),('wrong-startup','wrong_startup',970,69),('wrong-status','wrong_status',970,69),('skip-write','skip_write',985,None)]:
                argv=list(supervisor_command);target=out/(label+'.raw');argv[argv.index('-o')+1]=str(target);argv+=['--cfg',config];command(argv,label+'-supervisor');variant=target.read_bytes()
                if not 0<len(variant)<=8192:raise RuntimeError('command supervisor image bound')
                selected=[parents.get(label,images[0]),images[1],images[2]]
                payload=struct.pack('<8sIIIIII',b'AENMX001',*[len(v) for v in selected],len(variant),0,0)+entropy+b''.join(selected)+variant
                context=() if detail is None else (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)
                if worker:context=(f'NATIVE terminal slot=0 generation=1 kind=1 detail={worker}'.encode(),)+context
                if detail is not None:context=(f'NATIVE terminal slot=2 generation=1 kind=1 detail={80 if label == "wrong-startup" else 0}'.encode(),)+context
                cases.append((label,payload,None if detail is None else b'native C profile rejected',context))
            terminal_images={}
            for label,define in [('normal-nonzero','CHILD_NONZERO'),('child-fault','CHILD_FAULT')]:
                selected=list(images)
                for number,original_link in ((1,requester_link),(3,link_command)):
                    obj=out/f'{label}-{number}.o';target=out/f'{label}-{number}.elf'
                    command(cc+flags+['-D'+define,f'-DHELPER={number}','-c',source+('/program.c' if number==3 else '/helper.c'),'-o',str(obj)],f'{label}-{number}-compile')
                    argv=[str(obj) if v==str(out/f'helper{number}.o') else v.replace(str(out/f'helper{number}.map'),str(target.with_suffix('.map'))) for v in original_link];argv[argv.index('-o')+1]=str(target);command(argv,f'{label}-{number}-link');selected[number-1]=target.read_bytes()
                terminal_images[label]=selected
                cases.append((label,envelope(*selected),None,()))
            argv=list(supervisor_command);target=out/'fault-as-exit.raw';argv[argv.index('-o')+1]=str(target);argv+=['--cfg','fault_as_exit'];command(argv,'fault-as-exit-supervisor');variant=target.read_bytes()
            if not 0<len(variant)<=8192:raise RuntimeError('command supervisor image bound')
            selected=terminal_images['child-fault']
            payload=struct.pack('<8sIIIIII',b'AENMX001',*[len(v) for v in selected],len(variant),0,0)+entropy+b''.join(selected)+variant
            cases.append(('fault-as-exit',payload,b'native C profile rejected',(b'NATIVE terminal slot=2 generation=1 kind=2 detail=134',b'NATIVE terminal slot=0 generation=1 kind=1 detail=69',b'NATIVE supervisor result=970 reclaimed=0')))
            for label,define in [('drop-read','DROP_READ'),('corrupt-read','CORRUPT_READ'),('drop-close','DROP_CLOSE'),('allow-poison-traffic','DROP_READ')]:
                obj=out/(label+'-adapter.o');target=out/(label+'.elf')
                command(cc+flags+['-DREPLY_PROBE','-D'+define]+(['-DALLOW_POISON_TRAFFIC'] if label=='allow-poison-traffic' else [])+['-c',source+'/child-adapter.c','-o',str(obj)],label+'-adapter')
                argv=[str(obj) if v==str(out/'child-adapter.o') else v.replace(str(out/'helper3.map'),str(target.with_suffix('.map'))) for v in link_command]
                argv[argv.index('-o')+1]=str(target);command(argv,label+'-link')
                cases.append((label,envelope(images[0],images[1],target.read_bytes()),b'native C profile rejected',(f'NATIVE terminal slot=2 generation=1 kind=1 detail={93 if label == "allow-poison-traffic" else 84}'.encode(),b'NATIVE terminal slot=0 generation=1 kind=1 detail=69',b'NATIVE supervisor result=970 reclaimed=0')))
            for label, field, early in (
                ('bootstrap-reference', 16, False),
                ('bootstrap-descriptor', 20, False),
                ('bootstrap-rights', 24, False),
                ('bootstrap-early-publication', 24, True),
            ):
                obj = out / (label + '-adapter.o')
                target = out / (label + '.elf')
                defines = ['-DBOOTSTRAP_PROBE', f'-DBOOTSTRAP_FIELD={field}']
                if early:
                    defines.append('-DEARLY_PUBLICATION')
                command(cc + flags + defines + ['-c', source + '/child-adapter.c',
                        '-o', str(obj)], label + '-adapter')
                argv = [str(obj) if v == str(out / 'child-adapter.o') else
                        v.replace(str(out / 'helper3.map'), str(target.with_suffix('.map')))
                        for v in link_command]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, label + '-link')
                context = (
                    f'NATIVE terminal slot=2 generation=1 kind=1 detail={97 if early else 95}'.encode(),
                    b'NATIVE terminal slot=0 generation=1 kind=1 detail=69',
                    b'NATIVE supervisor result=970 reclaimed=0',
                )
                cases.append((label, envelope(images[0], images[1], target.read_bytes()),
                              b'native C profile rejected', context))
            for label, skip in (('bootstrap-exit-window', False),
                                ('bootstrap-skip-exit-recheck', True)):
                argv = list(supervisor_command)
                target = out / (label + '.raw')
                argv[argv.index('-o') + 1] = str(target)
                argv += ['--cfg', 'exit_poll_window']
                if skip:
                    argv += ['--cfg', 'skip_exit_recheck']
                command(argv, label + '-supervisor')
                variant = target.read_bytes()
                if not 0 < len(variant) <= 8192:
                    raise RuntimeError('command supervisor image bound')
                selected = [images[0], images[1],
                            (out / 'bootstrap-early-publication.elf').read_bytes()]
                payload = (struct.pack('<8sIIIIII', b'AENMX001',
                           *[len(v) for v in selected], len(variant), 0, 0)
                           + entropy + b''.join(selected) + variant)
                context = (b'NATIVE terminal slot=2 generation=1 kind=1 detail=97',)
                context += ((b'NATIVE supervisor result=990 reclaimed=0',) if skip else (
                    b'NATIVE terminal slot=0 generation=1 kind=1 detail=69',
                    b'NATIVE supervisor result=970 reclaimed=0',
                ))
                cases.append((label, payload, b'native C profile rejected', context))
            obj = out / 'malformed-launch-parent.o'
            target = out / 'malformed-launch-parent.elf'
            command(cc + flags + ['-DMALFORMED_LAUNCH', '-DHELPER=1', '-c',
                    source + '/helper.c', '-o', str(obj)], 'malformed-launch-parent')
            argv = [str(obj) if v == str(out / 'helper1.o') else
                    v.replace(str(out / 'helper1.map'), str(target.with_suffix('.map')))
                    for v in requester_link]
            argv[argv.index('-o') + 1] = str(target)
            command(argv, 'malformed-launch-link')
            selected = [target.read_bytes(), images[1], images[2]]
            cases.append(('malformed-launch', envelope(*selected), None, ()))
            argv = list(supervisor_command)
            target = out / 'allow-launch-version.raw'
            argv[argv.index('-o') + 1] = str(target)
            argv += ['--cfg', 'allow_launch_version']
            command(argv, 'allow-launch-version-supervisor')
            variant = target.read_bytes()
            if not 0 < len(variant) <= 8192:
                raise RuntimeError('command supervisor image bound')
            payload = (struct.pack('<8sIIIIII', b'AENMX001',
                       *[len(v) for v in selected], len(variant), 0, 0)
                       + entropy + b''.join(selected) + variant)
            cases.append(('allow-launch-version', payload, b'native C profile rejected', (
                b'NATIVE terminal slot=0 generation=1 kind=1 detail=103',
                b'NATIVE supervisor result=970 reclaimed=0',
            )))
            for prefix in (0, 1, 4, 16, 31, 32, 383):
                label = f'launch-eof-{prefix}'
                obj = out / (label + '-parent.o')
                target = out / (label + '-parent.elf')
                command(cc + flags + [f'-DLAUNCH_PREFIX={prefix}', '-DHELPER=1',
                        '-c', source + '/helper.c', '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else
                        v.replace(str(out / 'helper1.map'), str(target.with_suffix('.map')))
                        for v in requester_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, label + '-link')
                selected = [target.read_bytes(), images[1], images[2]]
                cases.append((label, envelope(*selected), b'native C profile rejected', (
                    f'NATIVE supervisor result={1100 + prefix} reclaimed=0'.encode(),
                )))
            argv = list(supervisor_command)
            target = out / 'pad-launch-eof.raw'
            argv[argv.index('-o') + 1] = str(target)
            argv += ['--cfg', 'pad_launch_eof']
            command(argv, 'pad-launch-eof-supervisor')
            variant = target.read_bytes()
            if not 0 < len(variant) <= 8192:
                raise RuntimeError('command supervisor image bound')
            payload = (struct.pack('<8sIIIIII', b'AENMX001',
                       *[len(v) for v in selected], len(variant), 0, 0)
                       + entropy + b''.join(selected) + variant)
            cases.append(('pad-launch-eof', payload, b'native C profile rejected', (
                b'NATIVE terminal slot=0 generation=1 kind=1 detail=104',
                b'NATIVE supervisor result=970 reclaimed=0',
            )))
            startup_parents = {}
            for wide in (False, True):
                label = 'runner-startup-wide' if wide else 'runner-startup'
                obj = out / (label + '-parent.o')
                target = out / (label + '-parent.elf')
                defines = ['-DRUNNER_STARTUP'] + (['-DWIDE_STARTUP'] if wide else [])
                command(cc + flags + defines + ['-DHELPER=1', '-c', source + '/helper.c',
                        '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else
                        v.replace(str(out / 'helper1.map'), str(target.with_suffix('.map')))
                        for v in requester_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, label + '-link')
                startup_parents[wide] = target.read_bytes()
            simple = encode_runner_startup(['aether-run', 'bytecount', '--decimal'])
            wide = encode_runner_startup(['aether-run', '--', 'bytecount', '--decimal', '', 'x' * 31])
            startup_cases = [('runner-startup', simple, False, None),
                             ('runner-startup-wide', wide, True, None)]
            for label, offset, size, value in (
                ('startup-version', 7, 1, ord('2')),
                ('startup-zero-count', 8, 1, 0),
                ('startup-over-count', 8, 1, 7),
                ('startup-reserved', 31, 1, 1),
                ('startup-unterminated', 64, 32, ord('X')),
                ('startup-unused', 223, 1, 1),
                ('startup-changed', 64, 1, ord('X')),
            ):
                record = bytearray(simple)
                record[offset:offset + size] = bytes([value]) * size
                startup_cases.append((label, bytes(record), False,
                                      970 if label == 'startup-changed' else 994))
            for label, record, wide, detail in startup_cases:
                artifact = out / (label + '-startup.bin')
                artifact.write_bytes(record)
                report.setdefault('runner_startup_inputs', {})[label] = {
                    'path': str(artifact), 'sha256': sha(artifact), 'size': len(record)}
                argv = list(supervisor_command)
                target = out / (label + '.raw')
                argv[argv.index('-o') + 1] = str(target)
                argv += ['--cfg', 'runner_startup']
                command(argv, label + '-supervisor', {'AETHER_RUNNER_STARTUP': str(artifact)})
                variant = target.read_bytes()
                if not 0 < len(variant) <= 8192:
                    raise RuntimeError('command supervisor image bound')
                selected = [startup_parents[wide], images[1], images[2]]
                payload = (struct.pack('<8sIIIIII', b'AENMX001',
                           *[len(v) for v in selected], len(variant), 0, 0)
                           + entropy + b''.join(selected) + variant)
                context = () if detail is None else (
                    f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)
                if label == 'startup-changed':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=110',) + context
                cases.append((label, payload, None if detail is None else b'native C profile rejected', context))
            argv = list(supervisor_command)
            target = out / 'mapped-results.raw'
            argv[argv.index('-o') + 1] = str(target)
            argv += ['--cfg', 'mapped_results']
            command(argv, 'mapped-results-supervisor')
            mapped_broker = target.read_bytes()
            if not 0 < len(mapped_broker) <= 8192:
                raise RuntimeError('command supervisor image bound')
            result_cases = [(f'public-exit-{value}', value, False, None)
                            for value in (0, 1, 2, 64, 125, 126, 127, 134, 255)]
            result_cases += [('public-fault', 134, True, None),
                             ('public-ignore-kind', 134, True, 'PUBLIC_IGNORE_KIND'),
                             ('public-force-zero', 64, False, 'PUBLIC_FORCE_ZERO')]
            for label, detail, fault, broken in result_cases:
                selected = list(images)
                for number, original_link in ((1, requester_link), (3, link_command)):
                    obj = out / f'{label}-{number}.o'
                    target = out / f'{label}-{number}.elf'
                    defines = ['-DCHILD_FAULT'] if fault else [f'-DCHILD_STATUS={detail}']
                    if number == 1:
                        defines += ['-DPUBLIC_RESULT'] + (['-D' + broken] if broken else [])
                    command(cc + flags + defines + [f'-DHELPER={number}', '-c',
                            source + ('/helper.c' if number == 1 else '/program.c'),
                            '-o', str(obj)], f'{label}-{number}-compile')
                    argv = [str(obj) if v == str(out / f'helper{number}.o') else
                            v.replace(str(out / f'helper{number}.map'), str(target.with_suffix('.map')))
                            for v in original_link]
                    argv[argv.index('-o') + 1] = str(target)
                    command(argv, f'{label}-{number}-link')
                    selected[number - 1] = target.read_bytes()
                payload = (struct.pack('<8sIIIIII', b'AENMX001',
                           *[len(v) for v in selected], len(mapped_broker), 0, 0)
                           + entropy + b''.join(selected) + mapped_broker)
                context = () if not broken else (
                    f'NATIVE terminal slot=2 generation=1 kind={2 if fault else 1} detail={detail}'.encode(),
                    f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail if fault else 0}'.encode(),
                    b'NATIVE supervisor result=970 reclaimed=0',
                )
                cases.append((label, payload, b'native C profile rejected' if broken else None, context))
            for label, wide, fault, broken in (
                ('combined-startup', False, False, False),
                ('combined-wide', True, False, False),
                ('combined-fault', True, True, False),
                ('combined-corrupt', True, False, True),
            ):
                artifact = out / (label + '-startup.bin')
                arguments = (['aether-run', '--', 'bytecount', '--decimal', '', 'x' * 31]
                             if wide else ['aether-run', 'bytecount', '--decimal'])
                artifact.write_bytes(encode_runner_startup(arguments))
                report.setdefault('runner_startup_inputs', {})[label] = {
                    'path': str(artifact), 'sha256': sha(artifact), 'size': artifact.stat().st_size}
                argv = list(supervisor_command)
                target = out / (label + '.raw')
                argv[argv.index('-o') + 1] = str(target)
                argv += ['--cfg', 'runner_startup', '--cfg', 'mapped_results']
                command(argv, label + '-supervisor', {'AETHER_RUNNER_STARTUP': str(artifact)})
                variant = target.read_bytes()
                if not 0 < len(variant) <= 8192:
                    raise RuntimeError('combined supervisor image bound')
                selected = list(images)
                for number, original_link in ((1, requester_link), (3, link_command)):
                    defines = ['-DWIDE_STARTUP'] if wide else []
                    defines += ['-DCHILD_FAULT'] if fault else [f'-DCHILD_STATUS={64 if wide else 0}']
                    if number == 1:
                        defines += ['-DRUNNER_STARTUP', '-DRUNNER_FORWARD', '-DPUBLIC_RESULT',
                                    f'-DFORWARD_FIRST={2 if wide else 1}']
                        if broken:
                            defines.append('-DCORRUPT_FORWARDED')
                    else:
                        defines.append('-DFORWARD_OBSERVER')
                    obj = out / f'{label}-{number}.o'
                    target = out / f'{label}-{number}.elf'
                    command(cc + flags + defines + [f'-DHELPER={number}', '-c',
                            source + ('/helper.c' if number == 1 else '/program.c'),
                            '-o', str(obj)], f'{label}-{number}-compile')
                    argv = [str(obj) if v == str(out / f'helper{number}.o') else
                            v.replace(str(out / f'helper{number}.map'), str(target.with_suffix('.map')))
                            for v in original_link]
                    argv[argv.index('-o') + 1] = str(target)
                    command(argv, f'{label}-{number}-link')
                    selected[number - 1] = target.read_bytes()
                payload = (struct.pack('<8sIIIIII', b'AENMX001',
                           *[len(v) for v in selected], len(variant), 0, 0)
                           + entropy + b''.join(selected) + variant)
                context = () if not broken else (
                    b'NATIVE terminal slot=2 generation=1 kind=1 detail=80',
                    b'NATIVE terminal slot=0 generation=1 kind=1 detail=1',
                    b'NATIVE supervisor result=970 reclaimed=0',
                )
                cases.append((label, payload, b'native C profile rejected' if broken else None, context))
            # Empty-output lifecycle prerequisite, separate from help/version.
            for label, define, premature, detail in (
                ('local-empty', None, False, None),
                ('local-skip-close', 'LOCAL_SKIP_CLOSE', False, 1201),
                ('local-launch', 'LOCAL_LAUNCH', False, 1202),
                ('local-after-close', 'LOCAL_AFTER_CLOSE', False, 1202),
                ('local-stale', 'LOCAL_STALE', False, 1203),
                ('local-status', 'LOCAL_BAD_STATUS', False, 1200),
                ('local-premature', None, True, 100),
                ('local-legacy-gate', None, False, 100),
            ):
                obj = out / (label + '.o')
                target = out / (label + '.elf')
                command(cc + flags + ['-DRUNNER_LOCAL_EMPTY', '-DHELPER=1']
                        + (['-D' + define] if define else [])
                        + ['-c', source + '/helper.c', '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else v
                        for v in requester_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, label + '-link')
                raw = out / (label + '.raw')
                argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                argv += ['--cfg', 'runner_local_empty']
                if premature: argv += ['--cfg', 'local_premature']
                command(argv, label + '-supervisor')
                local_code = raw.read_bytes()
                if not 0 < len(local_code) <= 8192:
                    raise RuntimeError('local supervisor image bound')
                parent = target.read_bytes()
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(parent),
                                      len(images[1]), len(images[2]), len(local_code), 0, 0)
                payload += entropy + parent + images[1] + images[2] + local_code
                reclaims = 2 if premature else 4 if label == 'local-legacy-gate' else 0
                context = () if detail is None else (
                    f'NATIVE supervisor result={detail} reclaimed={reclaims}'.encode(),)
                cases.append((label, payload, None if detail is None else
                              b'native C profile rejected', context))
            stream_service = out / 'stream-service.a'
            argv = list(service_command)
            argv[argv.index('-o') + 1] = str(stream_service)
            command(argv + ['--cfg', 'runner_streams'], 'stream-service')
            stream_backend = out / 'stream-backend.elf'
            argv = [str(stream_service) if v == str(out / 'service.a') else v
                    for v in service_link]
            argv[argv.index('-o') + 1] = str(stream_backend)
            command(argv, 'stream-backend-link')
            denial_service = out / 'denial-service.a'
            argv = list(service_command); argv[argv.index('-o') + 1] = str(denial_service)
            command(argv + ['--cfg', 'runner_streams', '--cfg', 'runner_denial'], 'denial-service')
            denial_backend = out / 'denial-backend.elf'
            argv = [str(denial_service) if v == str(out / 'service.a') else v for v in service_link]
            argv[argv.index('-o') + 1] = str(denial_backend)
            command(argv, 'denial-backend-link')
            cat_backends = {}
            for empty in (False, True):
                name = 'cat-empty-backend' if empty else 'cat-backend'
                archive = out / (name + '.a'); argv = list(service_command)
                argv[argv.index('-o') + 1] = str(archive)
                command(argv + ['--cfg', 'runner_streams', '--cfg', 'cat_roles']
                        + (['--cfg', 'cat_empty'] if empty else []), name + '-service')
                target = out / (name + '.elf')
                argv = [str(archive) if v == str(out / 'service.a') else v for v in service_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, name + '-link'); cat_backends[empty] = target.read_bytes()
            shell_files = {}
            for substitute in (False, True, "open", "read", "close", "open-eof", "read-eof", "close-eof", "open-half", "read-half", "close-half", "open-silent", "read-silent", "close-silent", "open-late"):
                name = 'shell-files-' + substitute if isinstance(substitute, str) else 'shell-files-substitute' if substitute else 'shell-files'
                archive = out / (name + '.a')
                argv = service_command[:service_command.index('--cfg')]
                argv[argv.index('-o') + 1] = str(archive)
                service_flags = ['--cfg', 'command_runner'] if substitute else []
                if isinstance(substitute, str):
                    operation, _, delivery = substitute.partition('-')
                    service_flags = ['--cfg', 'shell_bad_reply']
                    if operation != 'open':
                        service_flags += ['--cfg', 'shell_bad_' + operation]
                    if delivery in ('eof', 'half'):
                        service_flags += ['--cfg', 'shell_reply_eof']
                    if delivery in ('silent', 'late'):
                        service_flags += ['--cfg', 'shell_reply_silent']
                    if delivery == 'late':
                        service_flags += ['--cfg', 'shell_reply_late']
                    if delivery == 'half':
                        service_flags += ['--cfg', 'shell_reply_half']
                command(argv + service_flags, name + '-service')
                target = out / (name + '.elf')
                argv = [str(archive) if v == str(out / 'service.a') else v for v in service_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, name + '-link')
                shell_files[substitute] = target.read_bytes()
            cat_arguments = {'dash': '-', 'unbuffered': '-u', 'format': '-n', 'file': 'example.txt', 'help': '--help', 'version': '--version', 'unknown': '--unknown', 'empty': ''}
            for label, define, config, detail in (
                ('cat-roles-startup', None, None, None),
                ('cat-roles-startup-signal-int', 'STARTUP_SIGNAL_INT', 'cat_signal cat_signal_int', None),
                ('cat-roles-startup-signal-term', 'STARTUP_SIGNAL_TERM', 'cat_signal', None),
                ('cat-roles-startup-signal-exit', 'STARTUP_SIGNAL_EXIT', 'cat_signal cat_signal_int', 1501),
                ('cat-roles-startup-self-retry', 'STARTUP_SELF_RETRY', None, None),
                ('cat-roles-startup-self-retry-discard', 'STARTUP_SELF_DISCARD', None, 1501),
                ('cat-roles-startup-self-auto-retry', 'STARTUP_SELF_AUTO_RETRY', None, None),
                ('cat-roles-startup-self-auto-retry-discard', 'STARTUP_SELF_AUTO_DISCARD', None, 1501),
                ('cat-roles-startup-self-auto', 'STARTUP_SELF_AUTO', None, None),
                ('cat-roles-startup-self-auto-disabled', 'STARTUP_SELF_AUTO', None, 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-syntax', 'STARTUP_SYNTAX', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_syntax', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-syntax-skip', 'STARTUP_DASH_MAIN_SKIP', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_syntax', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-syntax-close', 'STARTUP_DASH_MAIN_SKIP_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_syntax', 1503),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-equal', 'STARTUP_ENV_LOAD', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env cat_env_load', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-uid', 'STARTUP_ENV', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env cat_env_uid', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-gid', 'STARTUP_ENV', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env cat_env_gid', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-noninteractive', 'STARTUP_ENV_NONINTERACTIVE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-absent', 'STARTUP_ENV_ABSENT', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-empty', 'STARTUP_ENV_EMPTY', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-uid-unguarded', 'STARTUP_ENV_LOAD', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env cat_env_uid', 1598),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-gid-unguarded', 'STARTUP_ENV_LOAD', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_env cat_env_gid', 1598),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-privileged', 'STARTUP_PRIVILEGED', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_privileged', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-privileged-skip', 'STARTUP_DASH_MAIN_SKIP', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_privileged', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open-silent', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-read-silent', 'STARTUP_FILES_POISON_READ', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_read', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-close-silent', 'STARTUP_FILES_POISON_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_close', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open-late', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_backend_late', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open-late-stop', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_backend_late cat_files_backend_skip_stop', 1601),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open-eof', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open-half', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-read-eof', 'STARTUP_FILES_POISON_READ', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_read', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-read-half', 'STARTUP_FILES_POISON_READ', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_read', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-close-eof', 'STARTUP_FILES_POISON_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_close', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-close-half', 'STARTUP_FILES_POISON_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_close', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open-half-stop', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_backend_skip_stop', 1601),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-open', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-read', 'STARTUP_FILES_POISON_READ', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_read', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-close', 'STARTUP_FILES_POISON_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_poison_close', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-stop', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_backend cat_files_backend_skip_stop', 1601),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-open', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-open-cut', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_poison_cut', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-read', 'STARTUP_FILES_POISON_READ', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_poison_read', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-read-cut', 'STARTUP_FILES_POISON_READ', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_poison_read cat_files_poison_cut', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-close', 'STARTUP_FILES_POISON_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_poison_close', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-close-cut', 'STARTUP_FILES_POISON_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_poison_close cat_files_poison_cut', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-retire', 'STARTUP_FILES_POISON', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_poison cat_files_poison_skip_cleanup', 1599),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-queued-version', 'STARTUP_QUEUED_BODY', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_queued_body cat_files_version cat_cwd_version', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-queued-legacy', 'STARTUP_QUEUED_BODY', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_queued_body cat_cwd_legacy', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-queued-witness', 'STARTUP_QUEUED_BODY', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_queued_body cat_files_version cat_cwd_version cat_queued_wrong_marker', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-descriptions', 'STARTUP_FILES_BOUNDARIES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_boundaries', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-descriptions-offset', 'STARTUP_FILES_BOUNDARIES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_boundaries cat_files_skip_offset', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-descriptions-reference', 'STARTUP_FILES_BOUNDARIES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_boundaries cat_files_ignore_reference', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-missing', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_missing', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-alias-input', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_alias_input', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-alias-output', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_alias_output', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-alias-diagnostic', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_alias_diagnostic', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-alias-cwd', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_alias_cwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-rights', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_rights', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-kind', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_kind', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-stale', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_stale', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-reserved', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_reserved', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-cut-start', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_cwd_cut cat_files_cut_start', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-cut-middle', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_cwd_cut cat_files_cut_middle', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-cut-tail', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_cwd_cut cat_files_cut_tail', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-version', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_version cat_cwd_version', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-legacy', 'STARTUP_FILES_LEGACY', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_cwd_legacy', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-early', 'STARTUP_FILES_EARLY', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_bad cat_files_reserved', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-skip', 'STARTUP_FILES_SKIP', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-close', 'STARTUP_FILES', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_files cat_files_skip_close', 1599),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files', 'STARTUP_DASH_MAIN', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-substitute', 'STARTUP_DASH_MAIN', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service', 1596),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-close', 'STARTUP_DASH_MAIN', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty cat_file_service cat_file_skip_close', 1597),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main', 'STARTUP_DASH_MAIN', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-skip', 'STARTUP_DASH_MAIN_SKIP', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-close', 'STARTUP_DASH_MAIN_SKIP_CLOSE', 'cat_dash_main cat_dash_init cat_parent_identity cat_identity cat_cwd cat_empty', 1503),
                ('cat-roles-startup-public-dash-init-parent-identity-errno-uid', 'STARTUP_IDENTITY_ERRNO_SKIP=0', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_source', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-errno-euid', 'STARTUP_IDENTITY_ERRNO_SKIP=1', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_source', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-errno-gid', 'STARTUP_IDENTITY_ERRNO_SKIP=2', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_source', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-errno-egid', 'STARTUP_IDENTITY_ERRNO_SKIP=3', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_source', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-descriptor-rights', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_bad_rights', None),
                ('cat-roles-startup-public-dash-init-parent-identity-descriptor-fd', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_bad_fd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-descriptor-stale', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_stale', None),
                ('cat-roles-startup-public-dash-init-parent-identity-descriptor-count', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_missing', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cut-empty', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_cut cat_identity_cut_empty', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cut-header', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_cut cat_identity_cut_header', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cut-role', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_cut cat_identity_cut_role', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cut-metadata', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_cut cat_identity_cut_metadata', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cut-tail', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_cut cat_identity_cut_tail', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-alias-output', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_alias_output', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-alias-diagnostic', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_alias_diagnostic', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-enomem', 'STARTUP_CWD_ENOMEM', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-enomem-skip', 'STARTUP_CWD_ENOMEM_NO_ERRNO', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-v1-sender', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_version cat_identity_version', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-v1-receiver', 'STARTUP_CWD_V1_RECEIVER', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_legacy', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-cut-empty', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_cut cat_cwd_cut_empty', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-cut-header', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_cut cat_cwd_cut_header', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-cut-role', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_cut cat_cwd_cut_role', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-cut-metadata', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_cut cat_cwd_cut_metadata', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-cut-tail', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_cut cat_cwd_cut_tail', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-pwd-match', 'STARTUP_CWD_PWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_pwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-pwd-device', 'STARTUP_CWD_PWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_pwd cat_cwd_pwd_dev', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-pwd-inode', 'STARTUP_CWD_PWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_pwd cat_cwd_pwd_ino', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-pwd-device-collapse', 'STARTUP_CWD_PWD_COLLAPSE_DEV', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_pwd cat_cwd_pwd_dev', 1594),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-pwd-inode-collapse', 'STARTUP_CWD_PWD_COLLAPSE_INO', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_pwd cat_cwd_pwd_ino', 1594),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-poison', 'STARTUP_CWD_POISON', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_poison', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-poison-length', 'STARTUP_CWD_POISON', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_poison cat_cwd_reply_length', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-poison-mode', 'STARTUP_CWD_POISON_STAT', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_poison cat_cwd_reply_mode', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-poison-cut', 'STARTUP_CWD_POISON', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_poison cat_cwd_reply_cut', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-poison-skip', 'STARTUP_CWD_NO_POISON', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_poison', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-alias', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_alias', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-short', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_short', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-version', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_version', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-legacy', 'STARTUP_CWD_LEGACY', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_legacy', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-match', 'STARTUP_CWD_MATCH', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-relative', 'STARTUP_CWD_RELATIVE', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-absent', 'STARTUP_CWD_ABSENT', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-skip', 'STARTUP_CWD_SKIP', 'cat_dash_init cat_parent_identity cat_identity cat_cwd', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-missing', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_missing', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-rights', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_rights', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-kind', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_kind', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-stale', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_stale', None),
                ('cat-roles-startup-public-dash-init-parent-identity-cwd-reserved', 'STARTUP_CWD', 'cat_dash_init cat_parent_identity cat_identity cat_cwd cat_cwd_bad cat_cwd_reserved', None),
                ('cat-roles-startup-public-dash-init-parent-identity', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity', None),
                ('cat-roles-startup-public-dash-init-parent-identity-zero', 'STARTUP_IDENTITY_ZERO', 'cat_dash_init cat_parent_identity cat_identity cat_identity_zero', None),
                ('cat-roles-startup-public-dash-init-parent-identity-skip', 'STARTUP_IDENTITY_SKIP', 'cat_dash_init cat_parent_identity cat_identity', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-source', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_source', None),
                ('cat-roles-startup-public-dash-init-parent-identity-flags', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_flags', None),
                ('cat-roles-startup-public-dash-init-parent-identity-reserved', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_reserved', None),
                ('cat-roles-startup-public-dash-init-parent-identity-uid', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_uid', None),
                ('cat-roles-startup-public-dash-init-parent-identity-euid', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_euid', None),
                ('cat-roles-startup-public-dash-init-parent-identity-gid', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_gid', None),
                ('cat-roles-startup-public-dash-init-parent-identity-egid', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_egid', None),
                ('cat-roles-startup-public-dash-init-parent-identity-stale', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_stale', None),
                ('cat-roles-startup-public-dash-init-parent-identity-short', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_short', None),
                ('cat-roles-startup-public-dash-init-parent-identity-queued-version', 'STARTUP_QUEUED_BODY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_version cat_queued_body', None),
                ('cat-roles-startup-public-dash-init-parent-identity-queued-legacy', 'STARTUP_QUEUED_BODY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_legacy cat_queued_body', None),
                ('cat-roles-startup-public-dash-init-parent-identity-queued-witness', 'STARTUP_QUEUED_BODY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_version cat_queued_body cat_queued_wrong_marker', 1501),
                ('cat-roles-startup-public-dash-init-parent-identity-version', 'STARTUP_IDENTITY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_version', None),
                ('cat-roles-startup-public-dash-init-parent-identity-legacy', 'STARTUP_IDENTITY_LEGACY', 'cat_dash_init cat_parent_identity cat_identity cat_identity_bad cat_identity_legacy', None),
                ('cat-roles-startup-public-dash-init-parent', 'STARTUP_PARENT', 'cat_dash_init cat_parent_identity', None),
                ('cat-roles-startup-public-dash-init-parent-swap', 'STARTUP_PARENT_SWAP', 'cat_dash_init cat_parent_identity cat_parent_swap', None),
                ('cat-roles-startup-public-dash-init-parent-disabled', 'STARTUP_PARENT', 'cat_dash_init', 1501),
                ('cat-roles-startup-public-dash-init-parent-self', 'STARTUP_PARENT_SELF', 'cat_dash_init cat_parent_identity', 1501),
                ('cat-roles-startup-public-dash-init', 'STARTUP_DASH_INIT', 'cat_dash_init', None),
                ('cat-roles-startup-public-dash-init-skip', 'STARTUP_DASH_INIT_SKIP', 'cat_dash_init', 1501),
                ('cat-roles-startup-public-dash', 'STARTUP_DASH_SIGNALS', None, None),
                ('cat-roles-startup-public-dash-skip', 'STARTUP_DASH_SIGNAL_SKIP', None, 1501),
                ('cat-roles-startup-public', 'STARTUP_PUBLIC_ACTION', None, None),
                ('cat-roles-startup-public-ignore-skip', 'STARTUP_PUBLIC_IGNORE_SKIP', None, 1501),
                ('cat-roles-startup-public-disabled', 'STARTUP_PUBLIC_ACTION', None, 1501),
                ('cat-roles-startup-self', 'STARTUP_SELF_TEST', None, None),
                ('cat-roles-startup-self-skip', 'STARTUP_SELF_SKIP', None, 1501),
                ('cat-roles-startup-actions', 'STARTUP_ACTION_TEST', None, None),
                ('cat-roles-startup-actions-peer', 'STARTUP_ACTION_TEST', 'cat_action_peer', None),
                ('cat-roles-startup-actions-peer-shared', 'STARTUP_ACTION_TEST', 'cat_action_peer', 1591),
                ('cat-roles-startup-actions-memory', 'STARTUP_ACTION_MEMORY', None, None),
                ('cat-roles-startup-actions-memory-writable', 'STARTUP_ACTION_MEMORY_WRITABLE', None, 1501),
                ('cat-roles-startup-actions-disabled', 'STARTUP_ACTION_DISABLED', None, None),
                ('cat-roles-startup-guard-live-poison-close', 'STARTUP_GUARD_POISON_CLOSE', 'cat_unknown_close cat_guard_close', None),
                ('cat-roles-startup-guard-live-poison-close-cut', 'STARTUP_GUARD_POISON_CLOSE', 'cat_unknown_close cat_guard_close cat_reply_cut', None),
                ('cat-roles-startup-guard-live-poison-close-jump', 'STARTUP_GUARD_JUMP', 'cat_unknown_close cat_guard_close', None),
                ('cat-roles-startup-guard-live-poison-close-jump-cut', 'STARTUP_GUARD_JUMP', 'cat_unknown_close cat_guard_close cat_reply_cut', None),
                ('cat-roles-startup-guard-live-poison-close-revive', 'STARTUP_GUARD_POISON_REVIVE', 'cat_unknown_close cat_guard_close', 1501),
                ('cat-roles-startup-guard-live-poison-jump', 'STARTUP_GUARD_JUMP', 'cat_unknown_read', None),
                ('cat-roles-startup-guard-live-poison-jump-cut', 'STARTUP_GUARD_JUMP', 'cat_unknown_read cat_reply_cut', None),
                ('cat-roles-startup-guard-live-poison-jump-mask', 'STARTUP_GUARD_JUMP_NO_MASK', 'cat_unknown_read', 1501),
                ('cat-roles-startup-guard-live-poison', 'STARTUP_GUARD_POISON', 'cat_unknown_read', None),
                ('cat-roles-startup-guard-live-poison-cut', 'STARTUP_GUARD_POISON', 'cat_unknown_read cat_reply_cut', None),
                ('cat-roles-startup-guard-live-poison-skip', 'STARTUP_GUARD_POISON_SKIP', 'cat_unknown_read', 1501),
                ('cat-roles-startup-guard-live-error', 'STARTUP_GUARD_ERROR', 'cat_diagnostic', None),
                ('cat-roles-startup-guard-live-error-io', 'STARTUP_GUARD_ERROR_IO', 'cat_diagnostic', None),
                ('cat-roles-startup-guard-live-error-errno', 'STARTUP_GUARD_ERRNO_SKIP', 'cat_diagnostic', 1501),
                ('cat-roles-startup-guard-live-jump', 'STARTUP_GUARD_JUMP', 'cat_diagnostic', None),
                ('cat-roles-startup-guard-live-jump-mask', 'STARTUP_GUARD_JUMP_NO_MASK', 'cat_diagnostic', 1501),
                ('cat-roles-startup-guard-live', 'STARTUP_GUARD_LIVE', 'cat_diagnostic', None),
                ('cat-roles-startup-guard-live-skip', 'STARTUP_GUARD_LIVE_SKIP', 'cat_diagnostic', 1501),
                ('cat-roles-startup-guard', 'STARTUP_GUARD_TEST', None, None),
                ('cat-roles-startup-guard-skip', 'STARTUP_GUARD_SKIP', None, 1501),
                ('cat-roles-startup-guard-restore', 'STARTUP_GUARD_RESTORE_FAIL', None, 1501),
                ('cat-roles-startup-frame', 'STARTUP_FRAME_TEST', None, None),
                ('cat-roles-startup-frame-preempt', 'STARTUP_FRAME_PREEMPT', None, None),
                ('cat-roles-startup-frame-memory-targets', 'STARTUP_FRAME_MEMORY_TARGETS', None, None),
                ('cat-roles-startup-frame-memory-targets-stack-valid', 'STARTUP_FRAME_MEMORY_TARGETS_STACK_VALID', None, 1501),
                ('cat-roles-startup-frame-memory-targets-code-valid', 'STARTUP_FRAME_MEMORY_TARGETS_CODE_VALID', None, 1501),
                ('cat-roles-startup-frame-memory', 'STARTUP_FRAME_MEMORY', None, None),
                ('cat-roles-startup-frame-memory-writable', 'STARTUP_FRAME_MEMORY_WRITABLE', None, 1501),
                ('cat-roles-startup-frame-state', 'STARTUP_FRAME_STATE', None, None),
                ('cat-roles-startup-frame-state-nested', 'STARTUP_FRAME_STATE_NESTED', None, 1501),
                ('cat-roles-startup-frame-state-reg', 'STARTUP_FRAME_STATE_REG', None, 1501),
                ('cat-roles-startup-frame-state-redzone', 'STARTUP_FRAME_STATE_REDZONE', None, 1501),
                ('cat-roles-startup-frame-skip', 'STARTUP_FRAME_SKIP', None, 1501),
                ('cat-roles-startup-frame-adversarial', 'STARTUP_FRAME_ADVERSARIAL', None, None),
                ('cat-roles-startup-frame-uncorrupted', 'STARTUP_FRAME_UNCORRUPTED', None, 1501),
                ('cat-roles-startup-internal-mask', 'STARTUP_MASK_SKIP_INTERNAL', None, 1501),
                ('cat-roles-startup-dup', 'STARTUP_DUP_TEST', None, None),
                ('cat-roles-startup-dup-self', 'STARTUP_DUP_SELF', None, 1501),
                ('cat-roles-startup-dup-flags', 'STARTUP_DUP_FLAGS', None, 1501),
                ('cat-roles-startup-dup-leak', 'STARTUP_DUP_LEAK', None, 1503),
                ('cat-roles-startup-bad-pid', 'STARTUP_BAD_PID', None, 1501),
                ('cat-roles-startup-no-action', 'STARTUP_NO_ACTION', None, 1501),
                ('cat-roles-startup-no-mask', 'STARTUP_NO_MASK', None, 1501),
                ('cat-roles-startup-no-cloexec', 'STARTUP_NO_CLOEXEC', None, 1501),
                ('cat-roles-startup-rights', None, 'cat_bad_rights', None),
                ('cat-roles-startup-fd', None, 'cat_bad_fd', None),
                ('cat-roles-startup-stale', None, 'cat_stale', None),
                ('cat-roles-startup-missing', None, 'cat_missing', None),
                ('cat-roles-signal-live-before', None, 'cat_admission cat_signal cat_fault_before', None),
                ('cat-roles-signal-live-copy', None, 'cat_admission cat_signal cat_fault_copy', None),
                ('cat-roles-signal-live-diagnostic', None, 'cat_admission cat_signal cat_usage cat_fault_diag', None),
                ('cat-roles-signal-live-prefix', 'CAT_CORRUPT', 'cat_admission cat_signal cat_fault_copy', 1505),
                ('cat-roles-signal-live-backend', None, 'cat_admission cat_signal cat_fault_copy cat_skip_backend_close', 1506),
                ('cat-roles-abnormal-before', None, 'cat_admission cat_fault_before', None),
                ('cat-roles-abnormal-copy', None, 'cat_admission cat_fault_copy', None),
                ('cat-roles-abnormal-diagnostic', None, 'cat_admission cat_usage cat_fault_diag', None),
                ('cat-roles-abnormal-stop', None, 'cat_admission cat_force_stop', None),
                ('cat-roles-abnormal-exit-kind', 'CAT_FAULT_EXIT', 'cat_admission cat_fault_copy', 1501),
                ('cat-roles-abnormal-stop-kind', None, 'cat_admission cat_force_stop cat_stop_wrong_kind', 1501),
                ('cat-roles-abnormal-prefix', 'CAT_CORRUPT', 'cat_admission cat_fault_copy', 1505),
                ('cat-roles-abnormal-backend', None, 'cat_admission cat_fault_copy cat_skip_backend_close', 1506),
                ('cat-roles-eintr-read', None, 'cat_admission cat_read_error cat_eintr', None),
                ('cat-roles-eintr-write', None, 'cat_admission cat_write_error cat_eintr', None),
                ('cat-roles-eintr-diagnostic', None, 'cat_admission cat_usage cat_diag_error cat_eintr', None),
                ('cat-roles-eintr-retry', 'CAT_RETRY_ERROR', 'cat_admission cat_write_error cat_eintr', 1530),
                ('cat-roles-eintr-zero', 'CAT_FORCE_ZERO', 'cat_admission cat_read_error cat_eintr', 1501),
                ('cat-roles-finalize-copy', None, 'cat_admission cat_finalize', None),
                ('cat-roles-finalize-usage', None, 'cat_admission cat_usage cat_finalize', None),
                ('cat-roles-finalize-error', None, 'cat_admission cat_close_input cat_finalize', None),
                ('cat-roles-finalize-unknown', None, 'cat_admission cat_unknown_read cat_finalize', None),
                ('cat-roles-finalize-reset', 'CAT_FINAL_RESET', 'cat_admission cat_finalize', 1501),
                *[(f'cat-roles-unknown-{op}-{mode}', None,
                   f'cat_admission cat_unknown_{op}' + (' cat_usage' if op == 'diag' else '') + (' cat_reply_cut' if mode == 'cut' else ''), None)
                  for op in ('read', 'write', 'diag', 'close') for mode in ('malformed', 'cut')],
                ('cat-roles-unknown-force-zero', 'CAT_FORCE_ZERO', 'cat_admission cat_unknown_read', 1501),
                ('cat-roles-unknown-skip-close', 'CAT_SKIP_CLOSE', 'cat_admission cat_unknown_read', 1501),
                ('cat-roles-unknown-clear-poison', 'CAT_CLEAR_POISON', 'cat_admission cat_unknown_read', 1532),
                ('cat-roles-error-read', None, 'cat_admission cat_read_error', None),
                ('cat-roles-error-write', None, 'cat_admission cat_write_error', None),
                ('cat-roles-error-diagnostic', None, 'cat_admission cat_usage cat_diag_error', None),
                ('cat-roles-error-close-input', None, 'cat_admission cat_close_input', None),
                ('cat-roles-error-close-output', None, 'cat_admission cat_close_output', None),
                ('cat-roles-error-close-diagnostic', None, 'cat_admission cat_close_diag', None),
                ('cat-roles-error-usage-close', None, 'cat_admission cat_usage cat_close_diag', None),
                ('cat-roles-error-force-zero', 'CAT_FORCE_ZERO', 'cat_admission cat_read_error', 1501),
                ('cat-roles-error-skip-close', 'CAT_SKIP_CLOSE', 'cat_admission cat_write_error', 1503),
                ('cat-roles-error-retry', 'CAT_RETRY_ERROR', 'cat_admission cat_write_error', 1530),
                *[(f'cat-roles-usage-{name}', None, 'cat_admission cat_usage', None) for name in cat_arguments],
                ('cat-roles-usage-short', None, 'cat_admission cat_usage cat_short', None),
                ('cat-roles-usage-rights', None, 'cat_admission cat_usage cat_bad_rights', None),
                ('cat-roles-usage-skip', 'CAT_USAGE_SKIP', 'cat_admission cat_usage', 1505),
                ('cat-roles-usage-corrupt', 'CAT_USAGE_CORRUPT', 'cat_admission cat_usage', 1505),
                ('cat-roles-usage-read', 'CAT_USAGE_READ', 'cat_admission cat_usage', 1520),
                ('cat-roles-usage-close', 'CAT_SKIP_CLOSE', 'cat_admission cat_usage', 1503),
                ('cat-roles-admit-copy', None, 'cat_admission', None),
                ('cat-roles-admit-empty', None, 'cat_admission cat_empty', None),
                ('cat-roles-admit-short', None, 'cat_admission cat_short', None),
                ('cat-roles-admit-rights', None, 'cat_admission cat_bad_rights', None),
                ('cat-roles-admit-name-bypass', None, 'cat_admission cat_accept_name', 1510),
                ('cat-roles-admit-corrupt', None, 'cat_admission cat_wrong_startup', 1501),
                ('cat-roles-copy', None, None, None),
                ('cat-roles-empty', None, 'cat_empty', None),
                ('cat-roles-short', None, 'cat_short', None),
                ('cat-roles-diagnostic', 'CAT_DIAGNOSTIC', 'cat_diagnostic', None),
                ('cat-roles-rights', None, 'cat_bad_rights', None),
                ('cat-roles-fd', None, 'cat_bad_fd', None),
                ('cat-roles-stale', None, 'cat_stale', None),
                ('cat-roles-missing', None, 'cat_missing', None),
                ('cat-roles-skip', 'CAT_SKIP_COPY', None, 1505),
                ('cat-roles-corrupt', 'CAT_CORRUPT', None, 1505),
                ('cat-roles-close', 'CAT_SKIP_CLOSE', None, 1503),
                ('cat-roles-early', 'CAT_EARLY', 'cat_bad_rights', 1502),
            ):
                cat_env = None
                if config and 'cat_usage' in config:
                    operand = cat_arguments.get(label.removeprefix('cat-roles-usage-'), '--help')
                    artifact = out / (label + '-argument.bin')
                    artifact.write_bytes(operand.encode('ascii').ljust(32, b'\0'))
                    cat_env = {'AETHER_CAT_ARGUMENT': str(artifact)}
                    report.setdefault('cat_startup_inputs', {})[label] = {'argument': operand, 'path': str(artifact), 'sha256': sha(artifact), 'size': 32}
                obj = out / (label + '.o'); target = out / (label + '.elf')
                startup = label.startswith('cat-roles-startup')
                frame_targets = label.startswith('cat-roles-startup-frame-memory-targets')
                frame_memory = label.startswith('cat-roles-startup-frame-memory')
                frame_state = label.startswith('cat-roles-startup-frame-state')
                if frame_state:
                    command(cc + ['-D' + define, '-c', source + '/frame-registers.S', '-o', str(out / (label + '-registers.o'))], label + '-registers')
                if startup:
                    command(cc + flags + ['-Dmain=startup_consumer_main', '-c', source + '/startup-consumer.c', '-o', str(out / 'startup-consumer.o')], label + '-consumer')
                command(cc + flags + (['-DSTARTUP_SYNTAX'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-syntax') else []) + (['-DSTARTUP_ENV'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-') else []) + (['-DSTARTUP_FILES_POISON'] if label.startswith(('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-')) else []) + (['-DSTARTUP_FILES'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root') and not label.endswith(('-admit-legacy', '-admit-queued-legacy')) else []) + (['-DSTARTUP_DASH_MAIN'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main') else []) + (['-DSTARTUP_CWD_ENOMEM'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-enomem') else []) + (['-DSTARTUP_CWD_PWD'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-pwd') else []) + (['-DSTARTUP_CWD_POISON'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-poison') else []) + (['-DSTARTUP_CWD'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd') and label not in ('cat-roles-startup-public-dash-init-parent-identity-cwd-legacy', 'cat-roles-startup-public-dash-init-parent-identity-cwd-v1-receiver') else []) + (['-DSTARTUP_IDENTITY'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity') and label not in ('cat-roles-startup-public-dash-init-parent-identity-queued-legacy', 'cat-roles-startup-public-dash-init-parent-identity-legacy', 'cat-roles-startup-public-dash-init-parent-identity-cwd-v1-receiver') else []) + (['-DSTARTUP_PARENT'] if label.startswith('cat-roles-startup-public-dash-init-parent') else []) + (['-DSTARTUP_DASH_INIT'] if label.startswith('cat-roles-startup-public-dash-init') else []) + (['-DSTARTUP_DASH_SIGNALS', '-Dmain=__wrap_main'] if label.startswith('cat-roles-startup-public-dash') else []) + (['-DSTARTUP_PUBLIC_ACTION'] if label.startswith('cat-roles-startup-public') else []) + (['-DSTARTUP_GUARD_POISON_CLOSE'] if label.startswith('cat-roles-startup-guard-live-poison-close') else []) + (['-DSTARTUP_GUARD_POISON'] if label.startswith('cat-roles-startup-guard-live-poison') else []) + (['-DSTARTUP_GUARD_ERROR'] if label.startswith('cat-roles-startup-guard-live-error') else []) + (['-DSTARTUP_GUARD_JUMP'] if label.startswith(('cat-roles-startup-guard-live-jump', 'cat-roles-startup-guard-live-poison-jump')) else []) + (['-DSTARTUP_GUARD_LIVE'] if label.startswith('cat-roles-startup-guard-live') else []) + (['-DSTARTUP_SELF_AUTO_RETRY', '-DSTARTUP_SELF_AUTO'] if label.startswith('cat-roles-startup-self-auto-retry') else []) + (['-DCAT_SIGNAL_LIVE'] if label.startswith('cat-roles-signal-live') else []) + (['-DSTARTUP_SIGNAL_TERM'] if label.startswith('cat-roles-startup-signal') else []) + (['-DSTARTUP_SIGNAL_INT'] if label == 'cat-roles-startup-signal-exit' else []) + (['-DSTARTUP_SELF_RETRY'] if label.startswith('cat-roles-startup-self-retry') else []) + (['-DSTARTUP_SELF_TEST'] if label.startswith('cat-roles-startup-self') else []) + (['-DSTARTUP_ACTION_MEMORY'] if label.startswith('cat-roles-startup-actions-memory') else []) + (['-DSTARTUP_ACTION_TEST'] if label.startswith('cat-roles-startup-actions') else []) + (['-DSTARTUP_GUARD_TEST'] if label.startswith('cat-roles-startup-guard') and not label.startswith('cat-roles-startup-guard-live') else []) + (['-DSTARTUP_FRAME_MEMORY_TARGETS'] if frame_targets else []) + (['-DSTARTUP_FRAME_TEST', '-DSTARTUP_FRAME_MEMORY'] if frame_memory else []) + (['-DSTARTUP_FRAME_TEST', '-DSTARTUP_FRAME_STATE'] if frame_state else []) + (['-DSHELL_STARTUP'] if startup else []) + (['-DSTARTUP_FRAME_TEST'] if define in ('STARTUP_FRAME_SKIP', 'STARTUP_FRAME_ADVERSARIAL', 'STARTUP_FRAME_UNCORRUPTED', 'STARTUP_FRAME_PREEMPT') else []) + (['-DSTARTUP_FRAME_ADVERSARIAL'] if define == 'STARTUP_FRAME_UNCORRUPTED' else []) + ['-DCAT_ROLES'] + ['-D' + cfg.upper() for cfg in (config.split() if config else []) if cfg in ('cat_fault_before', 'cat_fault_copy', 'cat_fault_diag')] + (['-DCAT_EINTR'] if config and 'cat_eintr' in config else []) + (['-DCAT_FINAL_TEST'] if config and 'cat_finalize' in config else []) + (['-DCAT_UNKNOWN'] if config and 'cat_unknown_' in config else []) + (['-DCAT_ADMISSION'] if config and 'cat_admission' in config else []) + (['-D' + define] if define else [])
                        + ['-c', source + ('/startup-client.c' if startup else '/cat-client.c'), '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else v for v in requester_link]
                if startup:
                    argv.insert(argv.index(str(lib / 'libc.a')), str(out / 'startup-consumer.o'))
                if label.startswith('cat-roles-startup-public-dash'):
                    dash = ROOT / 'user/native-command/dash-inputs'
                    objects = json.loads((dash / 'libc-imports.json').read_text())['objects']
                    for name, digest in objects.items():
                        if sha(dash / name) != digest:
                            raise RuntimeError('dash object drift: ' + name)
                    argv[argv.index(str(lib / 'libc.a')):argv.index(str(lib / 'libc.a'))] = [str(dash / name) for name in sorted(objects)]
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main'):
                        replacement = ROOT / 'user/native-command/dash-main-inputs'
                        pin = json.loads((replacement / 'pin.json').read_text())
                        if sha(replacement / 'main.o') != pin['sha256']:
                            raise RuntimeError('native dash main object drift')
                        if not label.endswith('-unguarded'):
                            argv[argv.index(str(dash / 'obj/src/main.o'))] = str(replacement / 'main.o')
                        argv.append('-Wl,--wrap=_exit')
                    argv.append('-Wl,--wrap=main')
                if frame_state:
                    argv.insert(argv.index(str(lib / 'libc.a')), str(out / (label + '-registers.o')))
                argv[argv.index('-o') + 1] = str(target); command(argv, label + '-link')
                raw = out / (label + '.raw'); argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                command(argv + ['--cfg', 'cat_roles'] + [arg for cfg in (config.split() if config else []) for arg in ('--cfg', cfg)], label + '-supervisor', cat_env)
                variant = raw.read_bytes(); parent = target.read_bytes(); back = cat_backends['cat_empty' in (config or '')]
                if not 0 < len(variant) <= 8192: raise RuntimeError('cat role owner bound')
                file_variant = label.endswith('-substitute')
                if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-'):
                    file_variant = label.removeprefix('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-')
                    file_variant = 'open' if file_variant == 'stop' else file_variant.removesuffix('-stop')
                child_image = shell_files[file_variant] if config and 'cat_file_service' in config else images[2]
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(parent), len(back), len(child_image), len(variant), 0, 0)
                payload += entropy + parent + back + child_image + variant
                context = () if detail is None else (f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)
                if label.startswith('cat-roles-signal-live') and detail:
                    context = (b'NATIVE terminal slot=0 generation=1 kind=4 detail=15', *context)
                if detail == 1601 or label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-retire':
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=1', *context)
                if detail == 1594:
                    context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=0', *context)
                if startup and detail and detail not in (1594, 1596, 1597, 1599, 1601) and label != 'cat-roles-startup-actions-peer-shared':
                    stage = 2 if label.endswith('-syntax-close') else 0 if label.endswith('-syntax-skip') else 7 if label.endswith('-unguarded') else 0 if label.endswith('-privileged-skip') else 108 if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-queued-witness' else 114 if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-descriptions-') else 113 if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-early' else 2 if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-skip' else 0 if label.endswith('cwd-main-skip') else 7 if label.endswith('cwd-main-close') else 108 if label == 'cat-roles-startup-public-dash-init-parent-identity-queued-witness' else 105 if label.startswith('cat-roles-startup-public-dash-init-parent-identity-errno-') else 106 if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-enomem-skip' else 107 if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-poison-skip' else 106 if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-skip' else 105 if label == 'cat-roles-startup-public-dash-init-parent-identity-skip' else 104 if label in ('cat-roles-startup-public-dash-init-parent-disabled', 'cat-roles-startup-public-dash-init-parent-self') else 103 if label == 'cat-roles-startup-public-dash-init-skip' else 102 if label == 'cat-roles-startup-public-dash-skip' else 101 if label in ('cat-roles-startup-public-disabled', 'cat-roles-startup-public-ignore-skip') else 100 if label == 'cat-roles-startup-guard-live-poison-close-revive' else 99 if label == 'cat-roles-startup-guard-live-poison-jump-mask' else 98 if label == 'cat-roles-startup-guard-live-poison-skip' else 97 if label == 'cat-roles-startup-guard-live-error-errno' else 96 if label == 'cat-roles-startup-guard-live-jump-mask' else 95 if label == 'cat-roles-startup-guard-live-skip' else 94 if label == 'cat-roles-startup-self-auto-retry-discard' else 91 if label == 'cat-roles-startup-self-auto-disabled' else 130 if label == 'cat-roles-startup-signal-exit' else 92 if label == 'cat-roles-startup-self-retry-discard' else 91 if label == 'cat-roles-startup-self-skip' else 90 if define == 'STARTUP_ACTION_MEMORY_WRITABLE' else 125 if define == 'STARTUP_GUARD_RESTORE_FAIL' else 88 if define == 'STARTUP_GUARD_SKIP' else 87 if frame_targets else 81 if frame_memory else 79 if define == 'STARTUP_FRAME_STATE_NESTED' else 80 if frame_state else 78 if define == 'STARTUP_FRAME_UNCORRUPTED' else 75 if define == 'STARTUP_FRAME_SKIP' else 73 if define == 'STARTUP_MASK_SKIP_INTERNAL' else 70 if define == 'STARTUP_DUP_SELF' else 71 if define == 'STARTUP_DUP_FLAGS' else 0 if define == 'STARTUP_DUP_LEAK' else 10 if define == 'STARTUP_BAD_PID' else 20 if define == 'STARTUP_NO_ACTION' else 21 if define == 'STARTUP_NO_MASK' else 30
                    context = (f'NATIVE terminal slot=0 generation=1 kind=1 detail={stage}'.encode(), *context)
                cases.append((label, payload, None if detail is None else b'native C profile rejected', context))
            for label, define, config, detail in (
                ('success-helper-argv', None, 'success_helper_argv', None),
                ('success-helper-argv-arg', None, 'success_helper_argv success_helper_bad_arg', 1407),
                ('success-helper-argv-env', None, 'success_helper_argv success_helper_bad_env', 1407),
                ('success-helper-argv-skip', None, 'success_helper_argv', 1405),
                ('success-helper-argv-close', None, 'success_helper_argv', 1403),
                ('success-exit134', None, 'success_nonzero', None),
                ('success-fault', None, 'success_fault', None),
                ('success-forward', None, None, None),
                ('success-forward-wide', None, 'success_wide', None),
                ('success-forward-fault', None, 'success_fault success_wide', None),
                ('success-force-zero', 'SUCCESS_FORCE_ZERO', 'success_nonzero', 1401),
                ('success-ignore-kind', 'SUCCESS_IGNORE_KIND', 'success_fault', 1401),
                ('success-corrupt-argv', 'CORRUPT_FORWARDED', 'success_wide', 1407),
                ('success-skip-retire', None, 'success_fault success_skip_retire', 1403),
                ('success-stale-collect', 'SUCCESS_STALE_COLLECT', None, 1404),
                ('success-child', None, None, None),
                ('success-short', None, 'success_short', None),
                ('success-skip-collect', 'SUCCESS_SKIP_COLLECT', None, 1401),
                ('success-skip-close', 'SUCCESS_SKIP_CLOSE', None, 1403),
                ('success-skip-write', None, 'success_skip_write', 1405),
                ('success-wrong-sink', None, 'success_wrong_sink', 1405),
            ):
                forward = label.startswith('success-forward') or label == 'success-corrupt-argv'
                wide = bool(config and 'success_wide' in config)
                fault = bool(config and 'success_fault' in config)
                nonzero = bool(config and 'success_nonzero' in config)
                startup_env = None
                if forward:
                    artifact = out / (label + '-startup.bin')
                    artifact.write_bytes(encode_runner_startup(
                        ['aether-run', '--', 'bytecount', '--decimal', '', 'x' * 31] if wide
                        else ['aether-run', 'bytecount', '--decimal']))
                    report.setdefault('runner_startup_inputs', {})[label] = {
                        'path': str(artifact), 'sha256': sha(artifact), 'size': artifact.stat().st_size}
                    startup_env = {'AETHER_RUNNER_STARTUP': str(artifact)}
                child = images[2]
                helper_argv = label.startswith('success-helper-argv')
                if helper_argv:
                    helper = ROOT / 'user/native-command/dash-helper-inputs'
                    helper_pin = json.loads((helper / 'pin.json').read_text())
                    if sha(helper / 'helper.c') != helper_pin['sha256']:
                        raise RuntimeError('consumer helper source drift')
                    helper_obj = out / (label + '-consumer.o')
                    command(cc + flags + ['-Dmain=consumer_helper_main', '-c', str(helper / 'helper.c'), '-o', str(helper_obj)], label + '-consumer')
                    obj = out / (label + '-3.o'); target = out / (label + '-3.elf')
                    defines = ['-DCONSUMER_HELPER']
                    if label.endswith('-skip'): defines += ['-DCONSUMER_HELPER_SKIP']
                    if label.endswith('-close'): defines += ['-DCONSUMER_HELPER_SKIP_CLOSE']
                    command(cc + flags + defines + ['-c', source + '/program.c', '-o', str(obj)], label + '-child-compile')
                    argv = [str(obj) if v == str(out / 'helper3.o') else v.replace(str(out / 'helper3.map'), str(target.with_suffix('.map'))) for v in link_command]
                    argv.insert(argv.index(str(lib / 'libc.a')), str(helper_obj))
                    argv[argv.index('-o') + 1] = str(target)
                    command(argv, label + '-child-link')
                    child = target.read_bytes()
                if forward or fault or nonzero:
                    obj = out / (label + '-3.o'); target = out / (label + '-3.elf')
                    defines = (['-DWIDE_STARTUP'] if wide else []) + (['-DFORWARD_OBSERVER'] if forward else [])
                    defines += ['-DCHILD_FAULT'] if fault else [f'-DCHILD_STATUS={134 if nonzero else 64}'] if nonzero or wide else []
                    command(cc + flags + defines + ['-DHELPER=3', '-c', source + '/program.c', '-o', str(obj)], label + '-child-compile')
                    argv = [str(obj) if v == str(out / 'helper3.o') else v.replace(str(out / 'helper3.map'), str(target.with_suffix('.map'))) for v in link_command]
                    argv[argv.index('-o') + 1] = str(target)
                    command(argv, label + '-child-link')
                    child = target.read_bytes()
                obj = out / (label + '.o'); target = out / (label + '.elf')
                command(cc + flags + ['-DRUNNER_STREAMS', '-DRUNNER_SUCCESS'] + (['-DSUCCESS_HELPER_ARGV'] if helper_argv else [])
                        + (['-DRUNNER_STARTUP', '-DRUNNER_FORWARD', f'-DFORWARD_FIRST={2 if wide else 1}'] if forward else [])
                        + (['-DWIDE_STARTUP'] if forward and wide else [])
                        + (['-D' + define] if define else [])
                        + ['-c', source + '/success-client.c', '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else v for v in requester_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, label + '-link')
                raw = out / (label + '.raw'); argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                argv += ['--cfg', 'runner_success'] + [arg for cfg in (config.split() if config else []) for arg in ('--cfg', cfg)] + (['--cfg', 'runner_startup'] if forward else [])
                command(argv, label + '-supervisor', startup_env)
                variant = raw.read_bytes(); parent = target.read_bytes(); back = denial_backend.read_bytes()
                if not 0 < len(variant) <= 8192: raise RuntimeError('success supervisor bound')
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(parent), len(back),
                                      len(child), len(variant), 0, 0)
                payload += entropy + parent + back + child + variant
                context = () if detail is None else (f'NATIVE supervisor result={detail} reclaimed={3 if label == "success-stale-collect" else 0}'.encode(),)
                if helper_argv and detail is not None:
                    context = (f'NATIVE terminal slot=2 generation=1 kind=1 detail={91 if detail == 1407 else 0}'.encode(), *context)
                cases.append((label, payload, None if detail is None else b'native C profile rejected', context))
            for label, text_name, define, config, detail in (
                ('streams-denial-fail-name-zero', 'unavailable', None, 'denial_missing stream_zero', None),
                ('streams-denial-fail-rights-fatal', 'denied', None, 'denial_rights stream_fatal', None),
                ('streams-denial-fail-busy-zero', 'capacity', None, 'denial_busy stream_zero', None),
                ('streams-denial-fail-name-close', 'unavailable', None, 'denial_missing stream_close_error', None),
                ('streams-denial-fail-name-cut', 'unavailable', None, 'denial_missing stream_cut_write', None),
                ('streams-denial-fail-rights-partial', 'denied', None, 'denial_rights stream_cut_partial', None),
                ('streams-denial-fail-busy-cut-close', 'capacity', None, 'denial_busy stream_cut_close', None),
                ('streams-denial-fail-hide', 'unavailable', 'DENIAL_HIDE_FAILURE', 'denial_missing stream_zero', 1301),
                ('streams-denial-fail-skip-last', 'unavailable', 'DENIAL_SKIP_LAST_CLOSE', 'denial_missing stream_zero', 1303),
                ('streams-denial-fail-resume', 'unavailable', 'STREAM_RESUME', 'denial_missing stream_cut_write', 1320),
                ('streams-denial-short', 'unavailable', None, 'denial_missing stream_short', None),
                ('streams-usage-short', 'usage', None, 'stream_usage stream_short', None),
                ('streams-help-launch', 'help', 'STREAM_LAUNCH_HELP', None, 1302),
                ('streams-denial-name', 'unavailable', None, 'denial_missing', None),
                ('streams-denial-rights', 'denied', None, 'denial_rights', None),
                ('streams-denial-busy', 'capacity', None, 'denial_busy', None),
                ('streams-denial-skip', 'unavailable', 'DENIAL_SKIP', 'denial_missing', 1340),
                ('streams-denial-repeat', 'unavailable', 'DENIAL_REPEAT', 'denial_missing', 1340),
                ('streams-denial-text', 'unavailable', 'STREAM_WRONG_BYTE', 'denial_missing', 1305),
                ('streams-denial-errno', 'unavailable', None, 'denial_wrong_error', 1301),
                ('streams-denial-leak', 'capacity', None, 'denial_leak', 1342),
                ('streams-denial-child-role', 'unavailable', None, 'denial_bad_child', None),
                ('streams-start-magic', 'help', None, 'stream_bad_magic', None),
                ('streams-start-missing', 'help', None, 'stream_missing_role', None),
                ('streams-start-excess', 'help', None, 'stream_excess_role', None),
                ('streams-start-generation', 'help', None, 'stream_bad_header_generation', None),
                ('streams-start-header-pad', 'help', None, 'stream_bad_header_padding', None),
                ('streams-start-fd', 'help', None, 'stream_bad_fd', None),
                ('streams-start-capacity', 'help', None, 'stream_bad_capacity', None),
                ('streams-start-record-pad', 'help', None, 'stream_bad_record_padding', None),
                ('streams-start-ignore-capacity', 'help', 'STREAM_IGNORE_CAPACITY', 'stream_bad_capacity', 1302),
                ('streams-amb-write', 'help', None, 'stream_cut_write', None),
                ('streams-amb-partial', 'help', None, 'stream_cut_partial', None),
                ('streams-amb-usage', 'usage', None, 'stream_usage_cut', None),
                ('streams-amb-close', 'help', None, 'stream_cut_close', None),
                ('streams-amb-close-partial', 'help', None, 'stream_cut_close_partial', None),
                ('streams-amb-resume', 'help', 'STREAM_RESUME', 'stream_cut_write', 1320),
                ('streams-amb-hide', 'help', 'STREAM_FORCE_ZERO', 'stream_cut_write', 1301),
                ('streams-amb-retire', 'help', None, 'stream_cut_skip_retire', 1321),
                ('streams-zero', 'help', None, 'stream_zero', None),
                ('streams-fatal', 'help', None, 'stream_fatal', None),
                ('streams-usage-zero', 'usage', None, 'stream_usage_zero', None),
                ('streams-exhaust', 'exhaust', None, 'stream_exhaust', None),
                ('streams-close-error', 'help', None, 'stream_close_error', None),
                ('streams-retry', 'help', 'STREAM_RETRY', 'stream_zero', 1310),
                ('streams-hide-failure', 'help', 'STREAM_FORCE_ZERO', 'stream_fatal', 1301),
                ('streams-ignore-close', 'help', 'STREAM_IGNORE_CLOSE', 'stream_close_error', 1301),
                ('streams-fake-failure', 'help', 'STREAM_FAKE_FAILURE', 'stream_zero', 1311),
                ('streams-help', 'help', None, None, None),
                ('streams-version', 'version', None, 'stream_version', None),
                ('streams-usage', 'usage', None, 'stream_usage', None),
                ('streams-short', 'help', None, 'stream_short', None),
                ('streams-skip', 'help', 'STREAM_SKIP', None, 1305),
                ('streams-byte', 'help', 'STREAM_WRONG_BYTE', None, 1305),
                ('streams-sink', 'usage', 'STREAM_WRONG_SINK', 'stream_usage', 1305),
                ('streams-close', 'help', 'STREAM_SKIP_CLOSE', None, 1303),
                ('streams-after-close', 'help', 'STREAM_AFTER_CLOSE', None, 1302),
                ('streams-early', 'help', 'STREAM_EARLY', 'stream_bad_rights', 1302),
                ('streams-rights', 'help', None, 'stream_bad_rights', None),
                ('streams-role', 'help', None, 'stream_bad_role', None),
                ('streams-generation', 'help', None, 'stream_bad_generation', None),
            ):
                denial = label.startswith('streams-denial-')
                text_bytes = b'X' * 528 if text_name == 'exhaust' else (ROOT / source / 'text' / (text_name + '.txt')).read_bytes()
                include = out / (label + '-include'); include.mkdir()
                (include / 'stream-text.h').write_text('static const unsigned char stream_text[] = {'
                    + ','.join(str(v) for v in text_bytes) + '};\n')
                obj = out / (label + '.o'); target = out / (label + '.elf')
                command(cc + flags + ['-DRUNNER_STREAMS', '-I', str(include),
                        '-DSTREAM_FD=' + ('2' if denial or text_name == 'usage' else '1'),
                        '-DSTREAM_STATUS=' + ('2' if denial else '64' if text_name == 'usage' else '0')]
                        + (['-D' + define] if define else [])
                        + (['-DRUNNER_DENIAL', '-DDENIAL_ERRNO=' + str({'unavailable': 2, 'denied': 13, 'capacity': 16}[text_name])] if denial else [])
                        + (['-DSTREAM_SKIP'] if define == 'STREAM_FAKE_FAILURE' else [])
                        + (['-DSTREAM_AMBIGUOUS'] if label.startswith('streams-amb-') or (denial and config and 'stream_cut_' in config) else [])
                        + ['-c', source + '/stream-client.c', '-o', str(obj)], label + '-compile')
                argv = [str(obj) if v == str(out / 'helper1.o') else v for v in requester_link]
                argv[argv.index('-o') + 1] = str(target)
                command(argv, label + '-link')
                raw = out / (label + '.raw'); argv = list(supervisor_command)
                argv[argv.index('-o') + 1] = str(raw)
                argv += ['--cfg', 'runner_streams'] + (['--cfg', 'runner_denial'] if denial else []) + [arg for cfg in (config.split() if config else []) for arg in ('--cfg', cfg)]
                command(argv, label + '-supervisor')
                variant = raw.read_bytes(); parent = target.read_bytes(); back = (denial_backend if denial else stream_backend).read_bytes()
                if not 0 < len(variant) <= 8192: raise RuntimeError('stream supervisor bound')
                payload = struct.pack('<8sIIIIII', b'AENMX001', len(parent), len(back),
                                      len(images[2]), len(variant), 0, 0)
                payload += entropy + parent + back + images[2] + variant
                context = () if detail is None else (
                    f'NATIVE supervisor result={detail} reclaimed=0'.encode(),)
                cases.append((label, payload, None if detail is None else b'native C profile rejected', context))
            for target in sorted(out.glob('*.elf')):
                for tool in ('nm','objdump','readelf'):
                    opts=['--undefined-only','--extern-only'] if tool=='nm' else ['-d'] if tool=='objdump' else ['-h','-l']
                    label=target.stem+'-'+tool;command([tools[tool]['path'],*opts,str(target)],label)
                    output=(out/(label+'.log')).read_bytes()
                    if tool=='nm' and output.strip():raise RuntimeError('undefined command ELF symbol')
                    if tool=='objdump' and re.search(rb'\bsyscall\b',output):raise RuntimeError('Linux syscall in command ELF')
            mapping=(out/'helper3.map').read_text()
            if not all('libc.a('+name+'.lo)' in mapping for name in ('read','write','close')):raise RuntimeError('command bypassed public musl I/O')
        if command_runner:
            cases.sort(key=lambda case: 0 if case[0].startswith(('streams-', 'success-', 'cat-roles-')) or case[0] == 'local-after-close' else 1)
        if command_runner:
            cases.sort(key=lambda case: not case[0].startswith('success-helper-argv'))
        if connections:
            cases.sort(key=lambda case: (not case[0].startswith('copy-inherit-public-fork-wait-pipe'), not case[0].startswith('copy-inherit-public-fork-wait-exec-dispatch-prefork')))
        for label, raw, panic, context in cases:
            destination = out / label; destination.mkdir()
            payload = destination / 'native-c.bin'; payload.write_bytes(raw)
            case = {'name': label, 'status': 'incomplete', 'envelope_sha256': sha(payload)}
            report['cases'].append(case)
            print('[RUNNING]', label, file=sys.stderr, flush=True)
            command(['zig', 'build', *(['-Dnative-exec-denial=true'] if '-dash-command-failed-exec' in label else []), *(['-Dnative-signal-suspend=true'] if label.endswith('-null-wait') or '-wait-suspend-' in label else []), *(['-Dnative-signal-actions=true', '-Dnative-signal-public=true', '-Dnative-copy-signals=true'] if '-wait-suspend-' in label else []), *(['-Dnative-signal-actions=true', '-Dnative-signal-public=true', '-Dnative-signal-mask-delivery=true', '-Dnative-signal-termination=true'] if label.startswith('copy-inherit-public-fork-wait-pipe-signal') else []), *(['-Dnative-signal-mask-delivery=true', '-Dnative-signal-termination=true'] if label.startswith('copy-inherit-public-fork-wait-prefork-dash-command-pipe') else []), *(['-Dnative-signal-actions=true', '-Dnative-signal-public=true', '-Dnative-copy-signals=true'] if '-prefork-dash' in label else []), *(['-Dnative-process-exec=true', '-Dnative-process-freeze=true', '-Dnative-memory=true', '-Dnative-process-copy=true'] if label.startswith('exec-') else []), *(['-Dnative-process-exec=true'] if 'public-fork-wait-exec' in label or '-dash-command-pipe-exec' in label or label.startswith('copy-inherit-scratch-exec') else []), *(['-Dnative-' + label + '=true'] if label in ('exec-early', 'exec-token', 'exec-copy') else []), *(['-Dnative-signal-actions=true', '-Dnative-signal-mask-delivery=true'] if label.startswith(('copy-signals', 'copy-inherit-signal', 'copy-inherit-prepare-signal')) or label == 'copy-inherit-rollback-signal' or 'public-fork-live' in label or 'public-fork-wait-signal' in label else []), *(['-Dnative-copy-signals=true'] if (label.startswith(('copy-signals', 'copy-inherit-signal', 'copy-inherit-prepare-signal')) or label == 'copy-inherit-rollback-signal' or 'public-fork-live' in label or 'public-fork-wait-signal' in label) and label != 'copy-signals-disabled' else []), *(['-Dnative-copy-signals-' + label.removeprefix('copy-signals-') + '=true'] if label in ('copy-signals-drop', 'copy-signals-pending', 'copy-signals-parent') else []), *(['-Dnative-process-copy=true', '-Dnative-process-freeze=true', '-Dnative-memory=true'] if label.startswith('copy-') else []), *(['-Dnative-copy-slot-tid=true'] if label == 'copy-slot-tid' else []), *(['-Dnative-copy-fail-stage=true'] if label in ('copy-rollback', 'copy-signals-rollback', 'copy-zero') or label.startswith('copy-inherit-rollback') else []), *(['-Dnative-copy-skip-zero=true'] if label == 'copy-zero' else []), *(['-Dnative-copy-share=true'] if label == 'copy-share' else []), *(['-Dnative-copy-lose-anonymous=true'] if label == 'copy-anonymous' else []), *(['-Dnative-process-freeze=true'] if label.startswith('freeze-') and label != 'freeze-disabled' else []), *(['-Dnative-freeze-skip-park=true'] if label == 'freeze-skip' else []), *(['-Dnative-freeze-ignore-token=true'] if label == 'freeze-token' else []), *(['-Dnative-signal-actions=true', '-Dnative-runner-local=true'] if label == 'freeze-unsupported' else []), *(['-Dnative-parent-identity=true'] if label.startswith('cat-roles-startup-public-dash-init-parent') and label != 'cat-roles-startup-public-dash-init-parent-disabled' else []), *(['-Dnative-signal-public=true'] if label.startswith('cat-roles-startup-public') and label != 'cat-roles-startup-public-disabled' else []), *(['-Dnative-signal-mask-delivery=true'] if (label.startswith('cat-roles-startup-self-auto') and label != 'cat-roles-startup-self-auto-disabled') or label.startswith('cat-roles-startup-guard-live') else []), *(['-Dnative-signal-termination=true'] if label.startswith(('cat-roles-startup-signal', 'cat-roles-signal-live')) or 'public-fork-wait-signal' in label else []), *(['-Dnative-signal-actions-shared=true'] if label == 'cat-roles-startup-actions-peer-shared' else []), *(['-Dnative-signal-actions=true'] if label.startswith(('cat-roles-startup-public', 'cat-roles-startup-actions', 'cat-roles-startup-self', 'cat-roles-startup-signal', 'cat-roles-signal-live', 'cat-roles-startup-guard-live')) and label != 'cat-roles-startup-actions-disabled' else []), *(['-Dnative-memory=true'] if label.startswith(('cat-roles-startup-public-dash-init', 'cat-roles-startup-frame-memory', 'cat-roles-startup-actions-memory')) else []), *(['-Dnative-init-large-dirty-tail=true'] if label == 'dirty-tail' else []), *(['-Dnative-runner-local=true'] if (label.startswith('local-') and label != 'local-legacy-gate') or label.startswith(('streams-', 'cat-roles-', 'copy-inherit', 'copy-signals', 'exec-streams')) else []), *(['-Dnative-runner-files=true'] if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files') else []), '-Dsmp=false', '-Dnative-c-image=' + str(payload), '-p', str(destination),
                     *(['-Dnative-skip-zero=true'] if label == 'cleanup-no-zero' else ['-Dnative-init-skip-deadline=true'] if label == 'skip-deadline' else ['-Dnative-coexist-small-pool=true'] if label == 'small-pool' else []),
                     '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global')], label + '-build')
            if '-dash-command-pipe-exec-serial' in label:
                run_pipe_console(destination / 'aether.iso', external=True, exec_rejection='stale' if label.endswith('-stale') else 'grant' if label.endswith('-grant') else None)
            elif '-dash-command-pipe-serial' in label:
                run_pipe_console(destination / 'aether.iso', wrong=label.endswith('-wrong'), stale_token=label.endswith('-token'))
            elif '-dash-command-serial' in label:
                run_dash_console(destination / 'aether.iso', wrong=label.endswith('-wrong'), legacy=label.endswith('-tee'), resume='-serial-resume' in label, old_cleanup=label.endswith('-resume-cleanup'), wrong_exit=label.endswith('-resume-exit'), repeat='-serial-repeat' in label, redirect='-repeat-redirect' in label, repeat_failure='closed-exec' if label.endswith('-redirect-exec-stale') else 'closed' if label.endswith('-redirect-stale') else 'token' if label.endswith('-repeat-token') else 'boot' if label.endswith('-repeat-boot') else None)
            else:
                run(destination / 'aether.iso', expected_panic=panic, panic_context=context, marker=b'AETHER NATIVE CONNECTIONS PASS' if connections else b'AETHER NATIVE PROGRAM PASS' if program else b'AETHER NATIVE COEXIST PASS' if coexist else ((b'AETHER NATIVE INIT COMPOSED CLOSED' if init_composed else b'AETHER NATIVE INIT LARGE CLOSED' if init_large else b'AETHER NATIVE INIT CLOSED') if label in ('owner-exit','owner-fault','code-write','code-write-page2','code-write-page3','stack-execute','stack-guard') else (b'AETHER NATIVE INIT COMPOSED PASS' if init_composed else b'AETHER NATIVE INIT LARGE PASS' if init_large else b'AETHER NATIVE INIT PASS')) if init else b'AETHER NATIVE FILE SERVICE PASS' if (files or process) else b'AETHER NATIVE CHANNEL PASS' if channel else b'AETHER NATIVE LAUNCH PASS')
            serial = (destination / 'native-serial.log').read_text()
            if label.startswith('cat-roles-'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                if any('slot=2 ' in line for line in actual) and not label.startswith(('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-')) and label != 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-descriptions' and not label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-') and label not in ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-close'): raise RuntimeError('cat role prerequisite admitted child')
                if label in ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-substitute', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-close') and actual:
                    raise RuntimeError('file composition precondition reached child terminal')
                if panic is None:
                    status = 110 if label in ('cat-roles-startup-rights', 'cat-roles-startup-fd', 'cat-roles-startup-stale', 'cat-roles-startup-missing', 'cat-roles-rights', 'cat-roles-fd', 'cat-roles-stale', 'cat-roles-missing', 'cat-roles-admit-rights', 'cat-roles-usage-rights') else 64 if label.startswith('cat-roles-usage-') or label in ('cat-roles-error-diagnostic', 'cat-roles-error-usage-close') else 64 if label.startswith('cat-roles-unknown-diag-') or label in ('cat-roles-eintr-diagnostic', 'cat-roles-finalize-usage') else 1 if label.startswith(('cat-roles-error-', 'cat-roles-unknown-', 'cat-roles-eintr-')) or label in ('cat-roles-finalize-error', 'cat-roles-finalize-unknown') else 0
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-') and label.rsplit('-', 1)[-1] in ('source', 'flags', 'reserved', 'uid', 'euid', 'gid', 'egid', 'stale', 'short', 'version', 'legacy'):
                        status = 110
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-') and label.rsplit('-', 1)[-1] in ('missing', 'rights', 'kind', 'stale', 'reserved', 'alias', 'short', 'version', 'legacy'):
                        status = 110
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-poison'):
                        status = 1
                    if label.startswith(('cat-roles-startup-public-dash-init-parent-identity-cwd-v1-', 'cat-roles-startup-public-dash-init-parent-identity-cwd-cut-')):
                        status = 110
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-alias-'):
                        status = 110
                    if label.startswith(('cat-roles-startup-public-dash-init-parent-identity-descriptor-', 'cat-roles-startup-public-dash-init-parent-identity-cut-')):
                        status = 110
                    if label in ('cat-roles-startup-public-dash-init-parent-identity-cwd-main', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files'):
                        status = 7
                    if label in ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-privileged', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-syntax'):
                        status = 2
                    kind = 1
                    if label.startswith('cat-roles-startup-guard-live-poison'):
                        status = 1
                    if label.startswith('cat-roles-startup-signal'):
                        status, kind = (2 if label.endswith('-int') else 15), 4
                    if label.startswith('cat-roles-signal-live'):
                        status, kind = 15, 4
                    if label.startswith('cat-roles-abnormal-'):
                        status, kind = (143, 3) if label == 'cat-roles-abnormal-stop' else (134, 2)
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind={kind if slot == 0 else 1} detail={status if slot == 0 else 17}'
                                for gen in (1, 2) for slot in ((1,) if label == 'cat-roles-abnormal-stop' else (0, 1))]
                    if label == 'cat-roles-startup-public-dash-init-parent-swap':
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={0 if slot == 1 else 17}'
                                    for gen in (1, 2) for slot in (1, 0)]
                    reclaims = 4
                    if label in ('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root'):
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={(0 if label.endswith('-root') else 7) if slot == 0 else 17}' for gen in (1, 2) for slot in (0, 1, 2)]
                        reclaims = 6
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-env-'):
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={7 if slot == 0 else 17}' for gen in (1, 2) for slot in (0, 1, 2)]
                        reclaims = 6
                    if label.startswith(('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-reply-', 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-')):
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={1 if slot == 0 else 17}' for gen in (1, 2) for slot in (0, 1, 2)]
                        reclaims = 6
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-backend-'):
                        # Forced stop has a retained state but emits no normal-exit line.
                        # The owner checks kind3/detail143; the omitted-stop mutant must fail.
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={1 if slot == 0 else 17}' for gen in (1, 2) for slot in (0, 1)]
                        reclaims = 6
                    if label == 'cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-descriptions':
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={0 if slot == 0 else 17}' for gen in (1, 2) for slot in (0, 1, 2)]
                        reclaims = 6
                    if label.startswith('cat-roles-startup-public-dash-init-parent-identity-cwd-main-files-root-admit-'):
                        expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={110 if slot == 0 else 17}' for gen in (1, 2) for slot in (0, 1, 2)]
                        reclaims = 6
                    if actual != expected or f'NATIVE supervisor result=100 reclaimed={reclaims}' not in serial.splitlines():
                        raise RuntimeError('cat role lifecycle mismatch')
            if label.startswith('success-') and panic is None:
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                fault = label in ('success-fault', 'success-forward-fault')
                child_detail = 134 if fault or label == 'success-exit134' else 64 if label == 'success-forward-wide' else 0
                expected = [f'NATIVE terminal slot={slot} generation={gen} kind={2 if fault and slot == 2 else 1} detail={17 if slot == 1 else child_detail if slot == 2 else 1 if fault else child_detail}'
                            for gen in (1, 2) for slot in (2, 0, 1)]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('four-role child lifecycle mismatch')
            if label.startswith('streams-'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                if any('slot=2 ' in line for line in actual):
                    raise RuntimeError('stream-only action admitted child')
                if panic is None:
                    status = 110 if label == 'streams-denial-child-role' else 1 if label.startswith('streams-denial-fail-') else 2 if label.startswith('streams-denial-') else 1 if label.startswith('streams-amb-') or label in ('streams-zero', 'streams-fatal', 'streams-usage-zero', 'streams-exhaust', 'streams-close-error') else 110 if label.startswith('streams-start-') or label in ('streams-rights', 'streams-role', 'streams-generation') else 64 if label in ('streams-usage', 'streams-usage-short') else 0
                    kind = 1
                    if label.startswith('cat-roles-abnormal-'):
                        status, kind = (143, 3) if label == 'cat-roles-abnormal-stop' else (134, 2)
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind={kind if slot == 0 else 1} detail={status if slot == 0 else 17}'
                                for gen in (1, 2) for slot in ((1,) if label == 'cat-roles-abnormal-stop' else (0, 1))]
                    if actual != expected or 'NATIVE supervisor result=100 reclaimed=4' not in serial.splitlines():
                        raise RuntimeError('stream lifecycle mismatch')
            if label.startswith('local-'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                if any('slot=2 ' in line for line in actual):
                    raise RuntimeError('local action admitted a child')
                if label in ('local-empty', 'local-legacy-gate', 'local-premature'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={0 if slot == 0 else 17}'
                                for gen in ((1,) if label == 'local-premature' else (1, 2))
                                for slot in (0, 1)]
                    if actual != expected:
                        raise RuntimeError('local lifecycle inventory mismatch')
            if label.endswith('-dash-command-failed-exec') and panic is None:
                expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={status}' for slot, gen, status in [(2,1,127),(2,2,126),(0,1,0),(1,1,17)]]
                if [line for line in serial.splitlines() if line.startswith('NATIVE terminal')] != expected or 'NATIVE supervisor result=100 reclaimed=4' not in serial.splitlines():
                    raise RuntimeError('failed-exec lifecycle mismatch')
            if label.startswith('copy-inherit') and not label.endswith('-dash-command-failed-exec') and panic is None:
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={71 if slot == 0 else 72 if slot == 2 else 17}' for generation in (1, 2) for slot in (0, 2, 1)]
                if label in ('copy-inherit-receipt', 'copy-inherit-completion', 'copy-inherit-stop', 'copy-inherit-mask-receipt', 'copy-inherit-signal-receipt', 'copy-inherit-signal-completion'):
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={251 if slot == 2 else 73 if slot == 0 else 17}' for generation in (1, 2) for slot in ((0, 1) if label == 'copy-inherit-stop' else (2, 0, 1))]
                if 'public-fork-wait' in label:
                    kind, detail = (2, 134) if label.endswith('-fault') else (4, 15) if label.endswith('-signal') else (1, 134) if label.endswith('-high') else (1, 72)
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind={kind if slot == 2 else 1} detail={detail if slot == 2 else (72 if '-prefork-dash' in label else 71) if slot == 0 else 17}' for generation in (1, 2) for slot in (2, 0, 1)]
                if label == 'copy-inherit-public-fork-wait-suspend-stale':
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={72 if slot == 2 else 71 if slot == 0 else 17}' for gen in (1, 2) for slot in ((2, 1) if gen == 1 else (2, 0, 1))]
                if label in ('copy-inherit-public-fork-wait-suspend-stop', 'copy-inherit-public-fork-wait-suspend-ignore', 'copy-inherit-public-fork-wait-suspend-block'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={72 if slot == 2 else 17}' for gen in (1, 2) for slot in (2, 1)]
                if label in ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-signal-table', 'copy-inherit-public-fork-wait-pipe', 'copy-inherit-public-fork-wait-prefork-dash-command-pipe', 'copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec', 'copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-consumer'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 0}' for gen in (1, 2) for slot in (2, 0, 1)]
                if label in ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv', 'copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-closure'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 0}' for gen in (1, 2) for slot in (2, 0, 1)]
                if label in ('copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null', 'copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-wait'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 7 if slot == 2 else 0}' for gen in (1, 2) for slot in (2, 0, 1)]
                if label == 'copy-inherit-public-fork-wait-prefork-dash-command-pipe-repeat':
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot==1 else 0}' for slot,gen in [(2,1),(2,2),(0,1),(1,1),(0,2),(1,2)]]
                if label in ('copy-inherit-public-fork-wait-prefork-dash-command-pipe-serial', 'copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-serial'):
                    actual = re.findall(r'NATIVE terminal slot=\d+ generation=\d+ kind=\d+ detail=\d+', serial)
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot==1 else 0}' for slot,gen in [(2,1),(2,2),(0,1),(0,2),(1,1),(1,2)]]
                if label in ('copy-inherit-public-fork-wait-pipe-signal', 'copy-inherit-public-fork-wait-pipe-signal-block'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind={4 if slot == 0 else 1} detail={13 if slot == 0 else 17}' for gen in (1, 2, 3) for slot in (0, 1)]
                if label == 'copy-inherit-public-fork-wait-pipe-stop':
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 0}' for gen in (1, 2) for slot in (0, 1)]
                if label in ('copy-inherit-public-fork-wait-pipe-fault', 'copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-fault'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind={2 if slot == 2 else 1} detail={134 if slot == 2 else 17 if slot == 1 else 0}' for gen in (1, 2) for slot in (2, 0, 1)]
                if '-dash-command-serial' in label:
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={status}' for slot, gen, status in [(2,1,72),(0,1,72),(2,2,72),(0,2,72),(1,1,17),(1,2,17)]]
                if '-serial-resume' in label:
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={status}' for slot, gen, status in [(2,1,72),(0,1,0),(2,2,72),(0,2,7),(1,1,17),(1,2,17)]]
                if '-serial-repeat' in label:
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={status}' for slot, gen, status in [(2,1,72),(2,2,72),(2,3,72),(0,1,0),(1,1,17),(1,2,17)]]
                if label.startswith(('copy-inherit-incomplete-', 'copy-inherit-signal-incomplete-')):
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={73 if slot == 0 else 17}' for generation in (1, 2) for slot in (0, 1)]
                if label.startswith('copy-inherit-uncertain'):
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={74 if slot == 0 else 75}' for generation in (1, 2) for slot in (0, 2)]
                if label.startswith('copy-inherit-uncertain-close'):
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={76 if slot == 0 else 77}' for generation in (1, 2) for slot in (0, 2)]
                if label.startswith(('copy-inherit-final-', 'copy-inherit-signal-final-')):
                    expected = [f'NATIVE terminal slot=1 generation={generation} kind=1 detail=17' for generation in (1, 2)]
                if label.startswith('copy-inherit-rollback'):
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={73 if slot == 0 else 17}' for generation in (1, 2) for slot in (0, 1, 2)]
                reclaims = 6
                if label in ('copy-inherit-public-fork-wait-pipe-lost', 'copy-inherit-public-fork-wait-pipe-one', 'copy-inherit-public-fork-wait-pipe-short'):
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={92 if slot == 0 else 17}' for gen in (1, 2, 3) for slot in (0, 1)]
                if label.startswith('copy-inherit-prepare-'):
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={78 if slot == 0 else 17}' for generation in (1, 2, 3) for slot in (0, 1)]
                if label == 'copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files':
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 95 if slot == 2 else 22}' for gen in (1, 2) for slot in (2, 0, 1)]
                if label == 'copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-redirection':
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 0}' for gen in (1, 2) for slot in (2, 0, 1)]
                if label == 'copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-files-denied':
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 2 if slot == 2 else 0}' for gen in (1, 2) for slot in (2, 0, 1)]
                if actual != expected or f'NATIVE supervisor result=100 reclaimed={reclaims}' not in serial.splitlines():
                    raise RuntimeError('inherit lifecycle mismatch')
            if label.startswith('copy-') and not label.startswith('copy-inherit') and panic is None:
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={29 if slot == 1 or (label in ("copy-rollback", "copy-signals-rollback") and slot == 2) else 72 if slot == 2 else 71}'
                            for generation in (1, 2) for slot in ((1, 0, 2) if label in ('copy-rollback', 'copy-signals-rollback') else (1, 2, 0))]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('copy lifecycle mismatch')
            if label in ('exec-streams-close-missing', 'exec-streams-close-partial', 'exec-streams-boot-missing', 'exec-streams-boot-partial', 'exec-streams-table-missing', 'exec-streams-table-partial'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                # Forced-stop terminal records are checked by the owner, not logged.
                expected = []
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec close containment lifecycle mismatch')
            if label in ('exec-streams-eof-boot', 'exec-streams-eof-boot-partial', 'exec-streams-eof-table', 'exec-streams-eof-table-partial', 'exec-streams-malformed-boot', 'exec-streams-malformed-table'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot=0 generation={generation} kind=1 detail={216 if label == "exec-streams-malformed-table" else 215}' for generation in (1, 2)]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec rejected bootstrap lifecycle mismatch')
            if label in ('exec-streams-peer-close-missing', 'exec-streams-peer-close-partial', 'exec-streams-fault-close-missing', 'exec-streams-fault-close-partial'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot=2 generation={generation} kind=2 detail=134' for generation in (1, 2)] if label.startswith('exec-streams-fault') else []
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec shared-close containment mismatch')
            if label in ('exec-streams-peer-first', 'exec-streams-peer-fault'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                fault = label == 'exec-streams-peer-fault'
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind={2 if slot == 2 and fault else 1} detail={(134 if fault else 64) if slot == 2 else 62 if slot == 0 else 17}' for generation in (1, 2) for slot in (2, 0, 1)]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec peer-first lifecycle mismatch')
            if label == 'exec-streams-shared':
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={62 if slot == 0 else 63 if slot == 2 else 17}' for generation in (1, 2) for slot in (0, 2, 1)]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec shared-holder lifecycle mismatch')
            if label in ('exec-streams', 'exec-streams-public', 'exec-streams-mask', 'exec-streams-mask-zero'):
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={62 if slot == 0 else 17}' for generation in (1, 2) for slot in (0, 1, 2)]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec stream lifecycle mismatch')
            if label == 'exec-positive':
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail={61 if slot == 0 else 29}' for generation in (1, 2) for slot in (0, 1, 2)]
                if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                    raise RuntimeError('exec lifecycle mismatch')
            if label.startswith('freeze-') and panic is None:
                actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                expected = [f'NATIVE terminal slot={slot} generation={generation} kind=1 detail=29'
                            for generation in (1, 2) for slot in ((1, 2) if label == 'freeze-stop' else (0, 1) if label == 'freeze-unsupported' else (0, 1, 2))]
                if actual != expected or f'NATIVE supervisor result=100 reclaimed={4 if label == "freeze-unsupported" else 6}' not in serial.splitlines():
                    raise RuntimeError('freeze lifecycle mismatch')
            if connections:
                if label in ('combined-startup', 'combined-wide', 'combined-fault'):
                    fault = label == 'combined-fault'
                    detail = 134 if fault else 64 if label == 'combined-wide' else 0
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind={2 if fault and slot == 2 else 1} detail={detail if slot == 2 else (1 if fault else detail) if slot == 0 else 17}'
                                for generation in (1, 2) for slot in (2, 0, 1)]
                    actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                    if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                        raise RuntimeError('combined startup/result lifecycle mismatch')
                if label.startswith('public-exit-') or label == 'public-fault':
                    fault = label == 'public-fault'
                    detail = 134 if fault else int(label.removeprefix('public-exit-'))
                    expected = [f'NATIVE terminal slot={slot} generation={generation} kind={2 if fault and slot == 2 else 1} detail={detail if slot == 2 else (1 if fault else detail) if slot == 0 else 17}'
                                for generation in (1, 2) for slot in (2, 0, 1)]
                    actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                    if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():
                        raise RuntimeError('mapped result lifecycle mismatch')
                if label in ('startup-version', 'startup-zero-count', 'startup-over-count',
                             'startup-reserved', 'startup-unterminated', 'startup-unused') and 'NATIVE terminal' in serial:
                    raise RuntimeError('invalid startup carrier reached worker termination')
                if label.startswith('launch-eof-') and 'NATIVE terminal' in serial:
                    raise RuntimeError('launch EOF reached worker termination')
                if label in ('positive','empty-input','short-write','full-output','normal-nonzero','child-fault','parent-first','rejected-launch','partial-reservation','malformed-launch','runner-startup','runner-startup-wide'):
                    expected=[f'NATIVE terminal slot={slot} generation={gen} kind={2 if label == "child-fault" and slot == 2 else 1} detail={17 if slot == 1 else (134 if label in ("normal-nonzero","child-fault") else 82 if label == "full-output" else 0) if command_runner and slot == 2 else 29}' for gen in (1,2) for slot in ((0,2,1) if label == "parent-first" else (2,0,1))]
                    actual=[line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                    if actual != expected or 'NATIVE supervisor result=100 reclaimed=6' not in serial.splitlines():raise RuntimeError('connections lifecycle mismatch')
                if label in ('reserved','bad-third-machine') and 'NATIVE terminal' in serial:raise RuntimeError('malformed connections admitted worker')
            elif process:
                if label == 'positive':
                    for line in ('NATIVE terminal slot=1 generation=1 kind=1 detail=17', 'NATIVE terminal slot=1 generation=2 kind=1 detail=' + ('17' if coexist else '33'), 'NATIVE terminal slot=0 generation=1 kind=1 detail=29', 'NATIVE supervisor result=100 reclaimed=' + ('5' if program else '3')):
                        if line not in serial.splitlines(): raise RuntimeError('missing process outcome: ' + line)
                if program and label in ('bad-third-machine','program-reserved','program-truncated') and 'NATIVE terminal' in serial: raise RuntimeError('malformed program bootstrap admitted a worker')
            elif init:
                if init_large and panic is None and 'mappings=verified' not in serial:
                    raise RuntimeError('missing v2 mapping verification')
                if label in ('code-write','code-write-page2','code-write-page3','stack-execute','stack-guard'):
                    expected_error = 6 if label == 'stack-guard' else 7 if label.startswith('code-write') else 21
                    if not re.search(r'NATIVE fault vector=14 rip=[0-9a-f]+ error=' + format(expected_error, 'x') + r'\n', serial):
                        raise RuntimeError('wrong protection fault')
                if (label.startswith('capacity-') or label in ('old-over','old-v2-over')) and panic and ('NATIVE terminal' in serial or 'mappings=verified' in serial):
                    raise RuntimeError('malformed capacity admitted supervisor')
                if label in ('owner-exit','owner-fault'):
                    if 'NATIVE init closing live=1 terminal=1 queued=2 wait=1' not in serial.splitlines():
                        raise RuntimeError('missing supervisor death precondition')
                elif label in ('positive','sequential','sequential-reverse'):
                    if 'NATIVE supervisor result=100 reclaimed=3' not in serial.splitlines():
                        raise RuntimeError('missing init completion')
                    if label != 'positive':
                        order = (1, 0, 1) if label == 'sequential-reverse' else (0, 1, 0)
                        expected = [f'NATIVE terminal slot={slot} generation={2 if i == 2 else 1} kind=1 detail=17' for i, slot in enumerate(order)]
                        actual = [line for line in serial.splitlines() if line.startswith('NATIVE terminal')]
                        if actual != expected: raise RuntimeError('incorrect sequential reuse order')
            elif (channel or files) and panic is None:
                for line in ('NATIVE terminal slot=1 generation=1 kind=1 detail=29', 'NATIVE terminal slot=0 generation=2 kind=1 detail=33', 'NATIVE supervisor result=100 reclaimed=3'):
                    if line not in serial.splitlines(): raise RuntimeError('missing channel outcome: ' + line)
            elif label == 'positive':
                for line in ('NATIVE terminal slot=0 generation=1 kind=1 detail=17',
                             'NATIVE terminal slot=1 generation=1 kind=1 detail=29',
                             'NATIVE terminal slot=0 generation=2 kind=2 detail=134',
                             'NATIVE supervisor result=100 reclaimed=3'):
                    if line not in serial.splitlines(): raise RuntimeError('missing launch outcome: ' + line)
            elif label in ('bad-machine', 'reserved', 'bad-layout') and 'NATIVE terminal' in serial:
                raise RuntimeError('malformed bootstrap reached child')
            case.update(status='pass', iso_sha256=sha(destination / 'aether.iso'), serial_sha256=sha(destination / 'native-serial.log'))
        for name, pin in report['sources'].items():
            if sha(ROOT / name) != pin: raise RuntimeError('source changed: ' + name)
        if connections and not shared_files and not command_runner:
            if {str(p.relative_to(headers)): sha(p) for p in headers.rglob('*') if p.is_file()} != header_hashes:
                raise RuntimeError('rebind private headers changed during run')
        report['status'] = 'pass'
    finally:
        (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
        compact_run(out, report)
    print(f'[PASS] {len(cases)} {"command-runner" if command_runner else "file-io" if file_io else "inherited-launch" if inherited_launch else "shared-files" if shared_files else "connections" if connections else "program" if program else "coexist" if coexist else "process" if process else "lookup" if lookup else "init" if init else "file-service" if files else "channel" if channel else "launch"} cases:', out)


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    profiles = parser.add_mutually_exclusive_group()
    profiles.add_argument('--command-runner', action='store_true', help='run the libc bytecount command with explicit stdin/stdout')
    profiles.add_argument('--file-io', action='store_true', help='test bounded general reads, EOF and shared-position writes')
    profiles.add_argument('--inherited-launch', action='store_true', help='test parent-requested restricted child admission and rollback')
    profiles.add_argument('--shared-files', action='store_true', help='test fixed bootstrap aliases with shared file position and lifetime')
    profiles.add_argument('--connections', action='store_true', help='test two private clients and a backend with incremental framing')
    profiles.add_argument('--program', action='store_true', help='test a third executable beside the requester and file service')
    profiles.add_argument('--coexist', action='store_true', help='test process and file connections in a four-channel profile')
    profiles.add_argument('--process', action='store_true', help='test connection-bound launch requests and empty inheritance')
    profiles.add_argument('--lookup', action='store_true', help='test scoped immutable executable names over existing launch grants')
    profiles.add_argument('--init-composed', action='store_true', help='test opt-in ABI 16 four-page init supervisor capacity')
    profiles.add_argument('--init-large', action='store_true', help='test opt-in ABI 15 two-page init supervisor capacity')
    profiles.add_argument('--init', action='store_true', help='test native init wait, delegation and fail-closed cleanup')
    profiles.add_argument('--writable-files', action='store_true', help='test bounded Rust scratch creation, writes and truncation')
    profiles.add_argument('--files', action='store_true', help='run the Rust read-only file service and C consumer')
    profiles.add_argument('--channel', action='store_true', help='test explicit byte-channel transfer and lifecycle instead of basic launch')
    parser.add_argument('--version', action='version', version='aether-launch-smoke 1')
    args = parser.parse_args()
    try: suite(args.libc_build, args.tools_lock, args.channel, args.files, args.writable_files, args.init, args.lookup, args.process, args.coexist, args.program, args.connections, args.shared_files, args.inherited_launch, args.file_io, args.command_runner, args.init_large, args.init_composed)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
