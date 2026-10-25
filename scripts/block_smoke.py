# SPDX-License-Identifier: BSD-2-Clause
"""Exercise persistent block transport using only a newly created disposable disk."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from evidence import compact_run
from deps import ROOT, DEPS, LOCK, verify
from emulator import wait_for_boot
from regression import Parser, inputs


def suite(native=False, libc_build=None, tools_lock=None, regions=False, rust_worker=False, service_memory=False):
    if service_memory and not (native and regions):
        raise RuntimeError('service backing requires native region-v2')
    verify()
    if subprocess.check_output(['qemu-system-x86_64', '--version'], text=True).splitlines()[0] != 'QEMU emulator version ' + LOCK['qemu']:
        raise RuntimeError('QEMU version mismatch')
    out = Path(tempfile.mkdtemp(prefix='block-', dir=ROOT / 'zig-out'))
    report = {'status': 'incomplete', 'native': native, 'regions': regions, 'rust_worker': rust_worker,
              'service_memory': service_memory, 'sources': inputs(), 'commands': [], 'cases': [],
              'start_utc': datetime.now(timezone.utc).isoformat()}
    print('[RUNNING] Evidence:', out, flush=True)
    seed = bytearray([165] * ((32768 if regions else 64) * 512))
    sectors = [8, 785, 16391] if regions else [7]
    for j, sector in enumerate(sectors):
        seed[sector * 512:(sector + 1) * 512] = bytes((i * 17 + 3 + j) & 255 for i in range(512))
    expected = bytearray(seed)
    for j, sector in enumerate(sectors):
        expected[sector * 512:(sector + 1) * 512] = bytes((i * 17 + 91 + j) & 255 for i in range(512))
    disk = out / 'disposable.raw'
    disk.write_bytes(seed)
    try:
        def command(args, label):
            entry = {'argv': args, 'start_utc': datetime.now(timezone.utc).isoformat()}
            report['commands'].append(entry)
            with (out / (label + '.log')).open('wb') as log:
                entry['exit_code'] = subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180).returncode
            entry['end_utc'] = datetime.now(timezone.utc).isoformat()
            if entry['exit_code']:
                raise RuntimeError('block build failed: ' + label)
        for mode in (['write', 'verify', 'readonly', 'fault'] if native else ['write', 'verify']):
            selection = ['-Dblock-test=' + mode]
            if native:
                from native_block_probe import build
                envelope = build(libc_build, tools_lock, out / (mode + '-client'), mode, command, regions, rust_worker)
                selection = ['-Dnative-c-image=' + str(envelope)]
            if service_memory:
                selection += ['-Dnative-memory=true', '-Dnative-memory-large=true',
                              '-Dnative-image-large=true', '-Dnative-backing=true',
                              '-Dnative-service-memory=true', '-Dnative-service-block=true']
                if mode == 'write':
                    rejected_selection = [s for s in selection if s != '-Dnative-service-block=true']
            command(['zig', 'build', '-Dsmp=false'] + selection + [
                    '--cache-dir', '.zig-cache', '--global-cache-dir', '.zig-cache/global', '--prefix', str(out / mode)], mode + '-build')
        if service_memory:
            command(['zig', 'build', '-Dsmp=false', *rejected_selection,
                     '--cache-dir', '.zig-cache', '--global-cache-dir', '.zig-cache/global',
                     '--prefix', str(out / 'wrong-profile')], 'wrong-profile-build')
        cases = [('write', 'write', None), ('reboot-verify', 'verify', None),
                 ('absent', 'write', b'block device absent'),
                 ('duplicate', 'write', b'block duplicate device'),
                 ('readonly', 'write', b'block read-only device'),
                 ('large-queue', 'write', b'block unsupported queue'),
                 ('corrupt', 'verify', b'block seed mismatch')]
        if native:
            cases = [('write', 'write', None), ('reboot-verify', 'verify', None),
                     ('readonly', 'readonly', None), ('fault', 'fault', None),
                     ('corrupt', 'verify', b'native C profile rejected')]
        if service_memory:
            cases += [('wrong-profile', 'wrong-profile', b'native C profile rejected')]
        for label, mode, panic in cases:
            case_disk = disk
            before = bytes(expected)
            if label in ('readonly', 'corrupt', 'fault', 'wrong-profile'):
                case_disk = out / (label + '.raw')
                before = bytes(seed)
                case_disk.write_bytes(before)
            variables = out / (label + '-vars.fd')
            shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
            args = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64', '-smp', '1', '-m', '256M',
                    '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
                    '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(out / mode / 'aether.iso'),
                    '-boot', 'd', '-nic', 'none', '-display', 'none', '-vga', 'std',
                    '-serial', 'file:' + str(out / (label + '-serial.log')), '-monitor', 'none', '-no-reboot', '-no-shutdown']
            if label != 'absent':
                args += ['-drive', f'if=none,id=work,format=raw,cache=writeback,file={case_disk}' + (',readonly=on' if label == 'readonly' and not native else ''),
                         '-device', 'virtio-blk-pci,drive=work,disable-modern=on' + (',queue-size=512' if label == 'large-queue' else '')]
            extra_disk = None
            if label == 'duplicate':
                extra_disk = out / 'second.raw'
                extra_disk.write_bytes(seed)
                args += ['-drive', f'if=none,id=second,format=raw,file={extra_disk}',
                         '-device', 'virtio-blk-pci,drive=second,disable-modern=on']
            entry = {'name': label, 'argv': args, 'start_utc': datetime.now(timezone.utc).isoformat(), 'status': 'incomplete'}
            report['cases'].append(entry)
            with (out / (label + '-qemu.log')).open('wb') as log:
                process = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT)
                try:
                    marker = b'AETHER NATIVE BLOCK PASS' if native else b'AETHER BLOCK WRITE PASS' if mode == 'write' else b'AETHER BLOCK VERIFY PASS'
                    wait_for_boot(process, out / (label + '-serial.log'), 30, marker, expected_panic=panic,
                                  panic_context=(b'NATIVE supervisor result=841 reclaimed=1',) if native and panic and label != 'wrong-profile' else ())
                finally:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=3)
                            raise RuntimeError('block QEMU forced teardown')
                    entry['end_utc'] = datetime.now(timezone.utc).isoformat()
            if case_disk.read_bytes() != (bytes(expected) if label in ('write', 'fault') else before):
                raise RuntimeError('whole-disk data mismatch: ' + label)
            if extra_disk is not None and extra_disk.read_bytes() != bytes(seed):
                raise RuntimeError('duplicate disk changed')
            if native and label == 'fault' and b'NATIVE terminal slot=0 generation=2 kind=2 detail=134\n' not in (out / (label + '-serial.log')).read_bytes():
                raise RuntimeError('block recipient fault evidence missing')
            entry['status'] = 'pass'
        if inputs() != report['sources']:
            raise RuntimeError('block source drift')
        report['status'] = 'pass'
    except BaseException as error:
        report['error'] = str(error)
        raise
    finally:
        report['end_utc'] = datetime.now(timezone.utc).isoformat()
        report['artifacts'] = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in out.rglob('*') if p.is_file()}
        (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
        compact_run(out, report)
    print('[PASS] Persistent block read/write/flush and rejection:', out)


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--rust-worker', action='store_true')
    parser.add_argument('--regions', action='store_true')
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--service-memory', action='store_true',
                        help='compose unchanged region-v2 grants with large service backing')
    parser.add_argument('--libc-build')
    parser.add_argument('--tools-lock')
    parser.add_argument('--version', action='version', version='aether-block-smoke 1')
    args = parser.parse_args()
    if args.rust_worker and not args.regions:
        parser.error("--rust-worker requires --native --regions")
    if args.regions and not args.native:
        parser.error("--regions requires --native")
    if args.service_memory and not (args.native and args.regions):
        parser.error('--service-memory requires --native --regions')
    if args.native != bool(args.libc_build and args.tools_lock) or (not args.native and (args.libc_build or args.tools_lock)):
        parser.error("--native requires both --libc-build and --tools-lock; hardware mode takes neither")
    try:
        suite(args.native, args.libc_build, args.tools_lock, args.regions, args.rust_worker, args.service_memory)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
