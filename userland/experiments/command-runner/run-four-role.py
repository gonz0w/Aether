#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Boot the independent four-role consumer against the captured M3 producer."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='four-role-native-', dir=ROOT / 'build'))
    kernel = ROOT / 'build/m3-producer-_7hbg9fd/producer'
    sdk = ROOT / 'build/native-c-5olokhku'
    prepared = ROOT / 'build/four-role-_eezngko'
    report = dict(status='incomplete', work=str(work), commands=[], cases=[])
    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    def need(ok, message):
        if not ok:
            raise RuntimeError(message)
    print(work, flush=True)
    save()
    try:
        manifest = ROOT / 'docs/evidence/m3-refocus-2026-09-07/source-manifest.json'
        need(sha(manifest) == 'e3628b849d36c33c6f6c44f7eb5e60a4ccac3f47e381ff37e1009cf6bb8561b8', 'manifest pin')
        sources = json.loads(manifest.read_text())
        # Every captured member is checked; caches and boot inputs are separate.
        for name, pin in sources.items():
            need(sha(kernel / name) == pin['sha256'], 'producer drift: ' + name)
        receipt = json.loads((prepared / 'summary.json').read_text())
        need(receipt['status'] == 'pass', 'parent preparation')
        parent = Path(receipt['elf']['path'])
        need(sha(parent) == receipt['elf']['sha256'], 'parent ELF drift')
        actual = {str(p.relative_to(sdk)): sha(p) for p in (sdk / 'stage').rglob('*') if p.is_file()}
        need(actual == receipt['sdk_inputs'], 'SDK drift')
        tools = receipt['tools']
        host = json.loads((HERE / 'host-tools.lock.json').read_text())
        for tool in [*tools.values(), *host.values()]:
            need(sha(Path(tool['path'])) == tool['sha256'], 'tool drift')
        local = {str(p): sha(p) for p in HERE.iterdir() if p.is_file()}
        report.update(producer_manifest_sha256=sha(manifest), producer_sources=sources,
                      parent=receipt['elf'], preparation_sha256=sha(prepared / 'summary.json'),
                      sdk_inputs=actual, tools=tools, host_tools=host, local_sources=local)
        if not (kernel / '.deps').exists():
            shutil.copytree(ROOT.parent / '.deps', kernel / '.deps')
        sys.path.insert(0, str(kernel / 'scripts'))
        from deps import verify
        from runner_startup import encode
        verify()
        report['boot_dependencies'] = json.loads((kernel / '.deps/manifest.json').read_text())
        tool_bin = work / 'tools'
        tool_bin.mkdir()
        for name in ('zig', 'qemu-system-x86_64', 'xorriso'):
            (tool_bin / name).symlink_to(host[name]['path'])
        (tool_bin / 'python3').symlink_to(sys.executable)
        wrapper = tool_bin / 'rustc'
        wrapper.write_text('#!' + sys.executable + '\nimport os,sys\n'
            + 'os.environ["DYLD_LIBRARY_PATH"]=' + repr(str(Path(host['rustc']['path']).parents[1] / 'lib')) + '\n'
            + 'compiler=' + repr(host['rustc']['path']) + '\n'
            + 'os.execv(compiler,[compiler]+[x for x in sys.argv[1:] if x!="+1.98.0"])\n')
        wrapper.chmod(0o755)
        report['rust_wrapper_sha256'] = sha(wrapper)
        env = clean_env(work)
        env['PATH'] = str(tool_bin) + ':/usr/bin:/bin'
        def command(label, argv, extra=None):
            selected = dict(env, **(extra or {}))
            result = run(argv, cwd=kernel, env=selected, work=work, label=label,
                         timeout=180, file_limit=512 * 1024**2)
            report['commands'].append(result.record)
            save()
            need(result.record['complete'] and result.returncode == 0, label + ' failed')
            return result
        cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
              '--sysroot=' + str(sdk / 'empty-root')]
        flags = ['-D_GNU_SOURCE', '-std=c17', '-O2', '-Wall', '-Wextra', '-Werror',
                 '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc',
                 '-isystem', str(sdk / 'stage/usr/include')]
        lib = sdk / 'stage/usr/lib'
        def compile_obj(label, source, defines=()):
            obj = work / (label + '.o')
            command(label, cc + flags + list(defines) + ['-I', str(HERE), '-c', str(source), '-o', str(obj)])
            return obj
        def link(label, objects):
            elf = work / (label + '.elf')
            command(label, cc + ['--ld-path=' + tools['lld']['path'], '-nostdlib', '-static',
                    '-Wl,-z,noexecstack', '-Wl,--no-undefined', str(lib / 'crt1.o'), str(lib / 'crti.o')]
                    + list(map(str, objects)) + [str(lib / 'libc.a'), str(lib / 'crtn.o'), '-o', str(elf)])
            return elf
        backend_obj = compile_obj('backend', 'user/native-command/helper.c', ['-DHELPER=2', '-DCOEXIST', '-DPROGRAM'])
        adapter = compile_obj('backend-adapter', 'user/native-memory/adapter.c')
        rust = [host['rustc']['path'], '--edition=2024', '--target=x86_64-unknown-none',
                '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static']
        rust_env = {'DYLD_LIBRARY_PATH': str(Path(host['rustc']['path']).parents[1] / 'lib')}
        service = work / 'service.a'
        command('service', rust + ['--crate-type=staticlib', 'user/native-files/service.rs',
                '--cfg', 'command_runner', '--cfg', 'writable', '--cfg', 'runner_streams',
                '--cfg', 'runner_denial', '-o', str(service)], rust_env)
        backend = link('backend-link', [backend_obj, adapter, service])
        child_objs = [compile_obj('child-' + n, HERE / (n + '.c'),
                     ['-Dmain=bytecount_main'] if n == 'bytecount' else [])
                     for n in ('bytecount', 'native-entry', 'native-io')]
        channel = compile_obj('channel', HERE.parent / 'native-channel/channel.c', ['-D__aether_io=__aether_channel_io'])
        child = link('child-link', child_objs + [channel])
        startup = work / 'startup.bin'
        startup.write_bytes(encode(['aether-run', 'bytecount', '--decimal']))
        supervisor = work / 'supervisor.raw'
        command('supervisor', ['opt-level=s' if arg == 'opt-level=2' else arg for arg in rust] + [
                '-C', 'lto=fat', '-C', 'codegen-units=1', '-C', 'link-arg=-Tuser/native-process/program-linker.ld',
                '-C', 'link-arg=--oformat=binary', 'user/native-connections/supervisor.rs',
                '--cfg', 'coexist', '--cfg', 'program', '--cfg', 'command_runner',
                '--cfg', 'runner_success', '--cfg', 'runner_startup', '-o', str(supervisor)],
                dict(rust_env, AETHER_RUNNER_STARTUP=str(startup)))
        need(0 < supervisor.stat().st_size <= 8192, 'supervisor bound')
        # Controls are private derived sources; the normal consumer stays unchanged.
        parents = {'positive': parent}
        for label, filename, before, after in (
            ('wrong-role', 'four-role-io.c', '    if (!ar_roles_decode(r, sizeof r, generation, &roles))',
             '    r[32] ^= 1; /* Inject invalid role before validation. */\n    if (!ar_roles_decode(r, sizeof r, generation, &roles))'),
            ('skip-close', 'four-role-runner.c', 'if (fd != 3 && close(fd))', 'if (fd != 3 && fd != 1 && close(fd))'),
        ):
            text = (HERE / filename).read_text()
            need(text.count(before) == 1, 'control anchor')
            derived = work / (label + '.c')
            derived.write_text(text.replace(before, after))
            obj = compile_obj(label, derived, ['-DNATIVE_RUNNER_STARTUP'])
            names = ['four-role', 'four-role-io', 'four-role-runner', 'runner-parse', 'runner-result', 'channel']
            parents[label] = link(label + '-link', [obj if n + '.c' == filename else prepared / (n + '.o') for n in names])
        report['artifacts'] = {str(p): sha(p) for p in [*parents.values(), backend, child, supervisor, startup]}
        entropy = os.urandom(48)
        for label, parent_elf in parents.items():
            dest = work / label
            dest.mkdir()
            images = [p.read_bytes() for p in (parent_elf, backend, child, supervisor)]
            payload = dest / 'native-c.bin'
            payload.write_bytes(struct.pack('<8sIIIIII', b'AENMX001', *map(len, images), 0, 0) + entropy + b''.join(images))
            command(label + '-kernel', [host['zig']['path'], 'build', '-Dsmp=false',
                    '-Dnative-c-image=' + str(payload), '-p', str(dest), '--cache-dir', str(kernel / '.zig-cache'),
                    '--global-cache-dir', str(kernel / '.zig-cache/global')])
            detail = {'wrong-role': 1401, 'skip-close': 1403}.get(label)
            launch = ('import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); '
                      'from native_smoke import run; detail=int(sys.argv[3]); '
                      'run(Path(sys.argv[2]), marker=b"AETHER NATIVE CONNECTIONS PASS", '
                      'expected_panic=b"native C profile rejected" if detail else None, '
                      'panic_context=(f"NATIVE supervisor result={detail} reclaimed=0".encode(),) if detail else ())')
            command(label + '-boot', [sys.executable, '-B', '-c', launch, str(kernel / 'scripts'), str(dest / 'aether.iso'), str(detail or 0)])
            lines = (dest / 'native-serial.log').read_text().splitlines()
            actual = [line for line in lines if line.startswith('NATIVE terminal')]
            expected = ([f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 0}'
                         for gen in (1, 2) for slot in (2, 0, 1)] if detail is None else
                        ['NATIVE terminal slot=0 generation=1 kind=1 detail=110'] if label == 'wrong-role' else
                        ['NATIVE terminal slot=2 generation=1 kind=1 detail=0', 'NATIVE terminal slot=0 generation=1 kind=1 detail=0'])
            need(actual == expected, label + ' terminal mismatch')
            need(detail is not None or 'NATIVE supervisor result=100 reclaimed=6' in lines, 'six reclaims')
            report['cases'].append(dict(name=label, status='pass', expected_terminal=expected,
                    observed_terminal=actual, expected_rejection=detail, payload_sha256=sha(payload),
                    iso_sha256=sha(dest / 'aether.iso'), serial_sha256=sha(dest / 'native-serial.log')))
            save()
            print(label + ': pass', flush=True)
        for name, pin in sources.items():
            need(sha(kernel / name) == pin['sha256'], 'producer changed during run')
        for path, digest in local.items():
            need(sha(Path(path)) == digest, 'local source changed during run')
        report['status'] = 'pass'
    except (OSError, RuntimeError, ValueError, KeyError) as error:
        report['error'] = str(error)
        print(str(error), flush=True)
    save()
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
