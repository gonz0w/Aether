#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host controls and pinned static SI-07 clients; no Aether execution claim.

Python 3.10+, provisioned strict SDK and Clang/LLD21.1.8; run from any cwd.
Every command has an owned cleanup receipt. Outputs remain under build/.
"""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import sys
import tempfile
from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    work = Path(tempfile.mkdtemp(prefix='sustained-runtime-', dir=ROOT / 'build'))
    report = {'status': 'incomplete', 'work': str(work), 'commands': [],
              'platform': platform.platform(), 'python': sys.version,
              'python_path': sys.executable,
              'python_sha256': sha(Path(sys.executable).resolve()),
              'native_execution': 'NOT RUN'}
    print(work, flush=True)

    def save():
        (work / 'results.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    try:
        pin = ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
        receipt = json.loads(pin.read_text())
        sdk = ROOT / 'build/native-c-xhkdw6jv'
        actual = {str(p.relative_to(sdk)): sha(p)
                  for p in (sdk / 'stage').rglob('*') if p.is_file()}
        need(not any(p.is_symlink() for p in (sdk / 'stage').rglob('*')), 'SDK symlink')
        need(actual == receipt['sdk_inputs'], 'SDK drift')
        need(sha(sdk / 'evidence.json') == receipt['libc_receipt_sha256'], 'SDK receipt drift')
        tools = receipt['tools']
        for tool in tools.values():
            need(sha(Path(tool['path'])) == tool['sha256'], 'tool drift')
        src = work / 'source'
        src.mkdir()
        names = ['four-role.c', 'four-role.h', 'four-role-io.c',
                 'four-role-runner.c', 'native-io.c', 'native-io.h',
                 'native-entry.c', 'bytecount.c', 'runner-parse.c',
                 'runner-parse.h', 'runner-result.c', 'runner-result.h',
                 'sustained-transport-controls.c', 'process.py',
                 'four-role-controls.c', 'result-controls.c',
                 'check-sustained.py', 'SUSTAINED.md']
        inputs = {str(HERE / n): sha(HERE / n) for n in names}
        for n in names:
            shutil.copy2(HERE / n, src / n)
        channel = HERE.parent / 'native-channel'
        # Keep original relative include resolution in the frozen snapshot.
        copied_channel = work / 'native-channel'
        copied_channel.mkdir()
        for n in ['channel.c', 'channel.h']:
            inputs[str(channel / n)] = sha(channel / n)
            shutil.copy2(channel / n, copied_channel / n)
        controls = HERE / 'sustained-decoder'
        for n in ['four-role-controls.c', 'result-controls.c', 'peer-controls.c']:
            inputs[str(controls / n)] = sha(controls / n)
        report.update(inputs=inputs, sdk_inputs=actual, tools=tools,
                      sdk_receipt_sha256=sha(pin))
        env = clean_env(work)
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'

        def command(label, argv, expected=0):
            executable = Path(argv[0]).resolve()
            report.setdefault('executables', {})[str(executable)] = sha(executable)
            save()
            result = run(argv, cwd=work, env=env, work=work, label=label,
                         timeout=30 if label.endswith('-run') else 180,
                         file_limit=16 * 1024**2)
            report['commands'].append(result.record)
            save()
            need(result.record['complete'] and result.record['cleanup'] == 'complete',
                 label + ' incomplete')
            need(result.returncode == expected if expected == 0 else result.returncode != 0,
                 label + ' exit')
            return result

        clang = tools['clang']['path']
        host_sdk = command('host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
        report['host_sdk'] = {'path': host_sdk,
                              'settings_sha256': sha(Path(host_sdk) / 'SDKSettings.json')}
        resource = command('clang-resource', [clang, '--no-default-config',
                                               '-print-resource-dir']).stdout.decode().strip()
        runtime = Path(resource) / 'lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib'
        report['ubsan'] = {'path': str(runtime), 'sha256': sha(runtime)}
        host = [clang, '--no-default-config', '-isysroot', host_sdk, '-std=c17',
                '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined',
                '-fno-sanitize-recover=all', '-I', str(src)]
        objects = []
        for profile, defines in [('legacy', []), ('v2', ['-DNATIVE_SUSTAINED_V2'])]:
            for label, source, control in [('roles', 'four-role.c', 'four-role-controls.c'),
                                           ('results', 'runner-result.c', 'result-controls.c')]:
                path = src if profile == 'legacy' else controls
                target = work / (profile + '-' + label)
                command(target.name + '-build', host + defines +
                        [str(src / source), str(path / control), '-o', str(target)])
                command(target.name + '-run', [str(target)])
                obj = work / (profile + '-' + source + '.o')
                command(obj.stem, host + defines + ['-c', str(src / source), '-o', str(obj)])
                objects.append(str(obj))
        peer = work / 'peer'
        command('peer-build', host + ['-DNATIVE_SUSTAINED_V2', str(controls / 'peer-controls.c')]
                + objects + ['-o', str(peer)])
        command('peer-run', [str(peer)])
        negative = command('mixed-decoder-link', host + ['-DNATIVE_SUSTAINED_V2',
                           str(controls / 'four-role-controls.c'),
                           str(work / 'legacy-four-role.c.o'), '-o', str(work / 'bad')], 1)
        need(b'ar_roles_decode_sustained_v2' in negative.stderr, 'mixed-link oracle')
        shim = work / 'host-include/sys'
        shim.mkdir(parents=True)
        (shim / 'auxv.h').write_text('unsigned long getauxval(unsigned long);\n')
        report['host_auxv_shim_sha256'] = sha(shim / 'auxv.h')
        for role, source, defines in [('parent', 'four-role-io.c', ['-DNATIVE_RUNNER_STARTUP']),
                                      ('child', 'native-io.c', [])]:
            target = work / (role + '-controls')
            command(role + '-controls-build', host + ['-I', str(shim.parent)] + defines + ['-DNATIVE_SUSTAINED_V2',
                    str(src / source), str(src / 'four-role.c'), str(src / 'runner-parse.c'),
                    str(src / 'sustained-transport-controls.c'), '-o', str(target)])
            command(role + '-controls-run', [str(target)])
        for label, source, defines, before_text, after_text in [
                ('parent-narrowing', 'four-role-io.c', ['-DNATIVE_RUNNER_STARTUP'],
                 'if (native_epoch < 1 || native_epoch > 65535)',
                 'if ((unsigned)native_epoch < 1 || (unsigned)native_epoch > 65535)'),
                ('child-narrowing', 'native-io.c', [],
                 'if (native_epoch < 1 || native_epoch > 65535)',
                 'if ((unsigned)native_epoch < 1 || (unsigned)native_epoch > 65535)'),
                ('child-fallback', 'native-io.c', [],
                 'native_word(r + 28) != 0x324f494eu',
                 '(native_word(r + 28) && native_word(r + 28) != 0x324f494eu)')]:
            text = (src / source).read_text()
            need(text.count(before_text) == 1, label + ' anchor')
            mutant = src / (label + '.c')
            mutant.write_text(text.replace(before_text, after_text))
            binary = work / label
            command(label + '-build', host + ['-I', str(shim.parent)] + defines
                    + ['-DNATIVE_SUSTAINED_V2', str(mutant), str(src / 'four-role.c'),
                       str(src / 'runner-parse.c'), str(src / 'sustained-transport-controls.c'),
                       '-o', str(binary)])
            result = command(label + '-run', [str(binary)], 1)
            need(b'Assertion failed' in result.stderr and b'ok == expected' in result.stderr,
                 label + ' semantic oracle')
        native = [clang, '--no-default-config', '--target=x86_64-linux-musl',
                  '--sysroot=' + str(sdk / 'empty-root')]
        flags = ['-D_POSIX_C_SOURCE=200809L', '-std=c17', '-O2', '-Wall', '-Wextra',
                 '-Werror', '-ffreestanding', '-fno-builtin', '-fstack-protector-strong',
                 '-nostdinc', '-isystem', str(sdk / 'stage/usr/include')]
        lib = sdk / 'stage/usr/lib'
        artifacts = {}
        for profile, defines in [('legacy', []), ('v2', ['-DNATIVE_SUSTAINED_V2'])]:
            for role, sources in [('parent', ['four-role', 'four-role-io', 'four-role-runner',
                                              'runner-parse', 'runner-result', 'channel']),
                                   ('child', ['bytecount', 'native-entry', 'native-io', 'channel'])]:
                objs = []
                for name in sources:
                    obj = work / (profile + '-' + role + '-' + name + '.o')
                    selected = list(defines)
                    if role == 'parent':
                        selected += ['-DNATIVE_RUNNER_STARTUP']
                    if name == 'bytecount':
                        selected += ['-Dmain=bytecount_main']
                    if name == 'channel':
                        selected += ['-D__aether_io=__aether_channel_io']
                    source = copied_channel / 'channel.c' if name == 'channel' else src / (name + '.c')
                    command(obj.stem, native + flags + selected + ['-c', str(source), '-o', str(obj)])
                    objs.append(str(obj))
                elf = work / (profile + '-' + role + '.elf')
                command(elf.stem + '-link', native + ['--ld-path=' + tools['lld']['path'],
                        '-nostdlib', '-static', '-Wl,-z,noexecstack', '-Wl,--no-undefined',
                        str(lib / 'crt1.o'), str(lib / 'crti.o')] + objs +
                        [str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(elf)])
                headers = command(elf.stem + '-headers', [tools['readelf']['path'], '-h', '-l', str(elf)])
                need(b'INTERP' not in headers.stdout and b'DYNAMIC' not in headers.stdout, 'dynamic ELF')
                undefined = command(elf.stem + '-undefined', [tools['nm']['path'],
                                    '--extern-only', '--undefined-only', str(elf)])
                need(not undefined.stdout.strip(), 'undefined externals')
                artifacts[elf.name] = {'path': str(elf), 'sha256': sha(elf), 'bytes': elf.stat().st_size}
        # Independent previously native-tested parent, rather than a same-source oracle.
        old = ROOT / 'build/four-role-_eezngko'
        old_report = json.loads((old / 'summary.json').read_text())
        need(sha(old / 'parent.elf') == old_report['elf']['sha256'], 'old parent pin')
        need(sha(work / 'legacy-parent.elf') == old_report['elf']['sha256'], 'legacy parent changed')
        report['legacy_parent_identity'] = old_report['elf']
        # Freeze exact pre-change native child sources, selected by before hashes.
        before = json.loads((ROOT / 'docs/evidence/sustained-runtime-2026-10-03/before.json').read_text())
        baseline = work / 'baseline'
        baseline.mkdir()
        candidate = ROOT / 'build/serial-session-consumer-_tfiol9l/producer/docs/evidence/init-command-handoff-2026-09-08/inputs/command-runner'
        for name in ['native-io.c', 'native-io.h', 'native-entry.c', 'bytecount.c']:
            need(sha(candidate / name) == before[name], 'before child pin: ' + name)
            shutil.copy2(candidate / name, baseline / name)
        baseline_objs = []
        for name in ['bytecount', 'native-entry', 'native-io']:
            obj = work / ('before-' + name + '.o')
            command(obj.stem, native + flags + (['-Dmain=bytecount_main'] if name == 'bytecount' else [])
                    + ['-c', str(baseline / (name + '.c')), '-o', str(obj)])
            baseline_objs.append(str(obj))
        old_child = work / 'before-child.elf'
        command('before-child-link', native + ['--ld-path=' + tools['lld']['path'], '-nostdlib',
                '-static', '-Wl,-z,noexecstack', '-Wl,--no-undefined', str(lib / 'crt1.o'),
                str(lib / 'crti.o')] + baseline_objs + [str(work / 'legacy-child-channel.o'),
                str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(old_child)])
        need(sha(old_child) == artifacts['legacy-child.elf']['sha256'], 'legacy child changed')
        report['legacy_child_identity'] = sha(old_child)
        negative = command('mixed-transport-link', native + ['--ld-path=' + tools['lld']['path'],
                           '-nostdlib', '-static', str(lib / 'crt1.o'), str(lib / 'crti.o'),
                           str(work / 'v2-child-native-entry.o'), str(work / 'legacy-child-native-io.o'),
                           str(work / 'legacy-child-bytecount.o'), str(work / 'legacy-child-channel.o'),
                           str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(work / 'bad-native')], 1)
        need(b'native_bootstrap_sustained_v2' in negative.stderr, 'mixed transport oracle')
        formatter = str(Path(clang).parent / 'clang-format')
        command('format', [formatter, '--dry-run', '--Werror',
                '--style=file:' + str(ROOT / 'docs/quality/clang-format.yaml')]
                + [str(src / n) for n in names if n.endswith(('.c', '.h'))])
        for path, digest in inputs.items():
            need(sha(Path(path)) == digest, 'source drift')
        need(actual == {str(p.relative_to(sdk)): sha(p)
                        for p in (sdk / 'stage').rglob('*') if p.is_file()}, 'SDK changed')
        for tool in tools.values():
            need(sha(Path(tool['path'])) == tool['sha256'], 'tool changed')
        report.update(status='pass', artifacts=artifacts,
                      profile={'name': 'NATIVE_SUSTAINED_V2', 'parent': 'AERIO002',
                               'child_discriminator': 'NIO2', 'receipt_prefix': '0x7b000000',
                               'epoch_domain': [1, 65535], 'native_cohort': 'full-width equality',
                               'owner_envelope': 'AENSI001/ABI22 proposed, NOT RUN',
                               'fallback': False})
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        report['error'] = str(error)
        print(str(error), flush=True)
    save()
    print(report['status'], flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
