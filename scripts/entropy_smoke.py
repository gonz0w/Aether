# SPDX-License-Identifier: BSD-2-Clause
"""Qualify isolated BSP entropy transport using an explicit host random backend."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

from evidence import compact_run
from deps import ROOT, DEPS, LOCK, verify
from emulator import wait_for_boot
from regression import Parser, inputs

MARKER = b'AETHER ENTROPY PASS'
READY = b'ENTROPY queue ready'
CASES = (
    ('draw', 'draw', None),
    ('partial', 'partial', None),
    ('absent', 'draw', b'entropy device absent'),
    ('duplicate', 'draw', b'entropy duplicate device'),
    ('modern', 'draw', b'entropy modern device unsupported'),
    ('head', 'head', b'entropy invalid head; DMA retained'),
    ('length', 'length', b'entropy invalid length; DMA retained'),
    ('index', 'index', b'entropy invalid index; DMA retained'),
    ('timeout', 'timeout', b'entropy timeout; DMA retained'),
    ('stalled', 'draw', b'entropy timeout; DMA retained'),
    ('accept-length-mutant', 'accept_length', b'entropy invalid length; DMA retained'),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def observe(process, path, label, panic):
    context = (READY,) if label not in ('absent', 'duplicate', 'modern') and panic else ()
    try:
        wait_for_boot(process, path, 30, MARKER, panic, context)
    except RuntimeError as error:
        if label == 'accept-length-mutant' and str(error) == 'unexpected boot success in negative test':
            return 'broken validator rejected by exact length oracle'
        raise
    if label == 'accept-length-mutant':
        raise RuntimeError('length oracle accepted the broken validator')
    data = path.read_bytes().splitlines()
    if panic is None:
        if data.count(MARKER) != 1 or data.count(READY) != 1:
            raise RuntimeError('duplicate or missing entropy proof marker')
        if label == 'partial' and data.count(b'ENTROPY partial completion checked') != 1:
            raise RuntimeError('partial completion evidence missing')
    return 'expected outcome'


def suite():
    verify()
    if subprocess.check_output(['qemu-system-x86_64', '--version'], text=True).splitlines()[0] != 'QEMU emulator version ' + LOCK['qemu']:
        raise RuntimeError('QEMU version mismatch')
    out = Path(tempfile.mkdtemp(prefix='entropy-', dir=ROOT / 'zig-out'))
    report = {'format': 'aether-entropy-device-v1', 'status': 'incomplete',
              'scope': 'BSP QEMU hardware transport only; no userland capability or entropy quality qualification',
              'sources': inputs(), 'tools': {}, 'firmware': {}, 'commands': [], 'cases': [], 'start_utc': utc()}
    for name in ('zig', 'python3', 'qemu-system-x86_64', 'rustc'):
        path = Path(shutil.which(name)).resolve()
        report['tools'][name] = {'path': str(path), 'sha256': sha(path)}
    sysroot = Path(subprocess.check_output(['rustc', '--print', 'sysroot'], text=True).strip())
    compiler = sysroot / 'bin/rustc'
    report['tools']['rustc-compiler'] = {'path': str(compiler), 'sha256': sha(compiler)}
    for name in ('code.fd', 'vars.fd'):
        report['firmware'][name] = sha(DEPS / 'firmware' / name)
    print('[RUNNING] Entropy evidence:', out, file=sys.stderr, flush=True)
    try:
        def command(args, label, expected=None):
            entry = {'argv': args, 'start_utc': utc(), 'status': 'incomplete'}
            report['commands'].append(entry)
            log = out / (label + '.log')
            with log.open('wb') as stream:
                result = subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
            entry.update(end_utc=utc(), returncode=result.returncode)
            if expected is None and result.returncode != 0:
                raise RuntimeError(label + ' failed')
            if expected is not None and (result.returncode == 0 or expected not in log.read_bytes()):
                raise RuntimeError(label + ' lacks exact build rejection')
            entry['status'] = 'pass'
        base = ['zig', 'build', '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global')]
        guards = (
            ('invalid-mode', ['-Dsmp=false', '-Dentropy-test=unknown'], b'invalid entropy test mode'),
            ('smp-mix', ['-Dentropy-test=draw'], b'entropy test requires -Dsmp=false'),
            ('block-mix', ['-Dsmp=false', '-Dentropy-test=draw', '-Dblock-test=write'], b'entropy test requires -Dsmp=false'),
            ('native-mix', ['-Dsmp=false', '-Dentropy-test=draw', '-Dnative-c-image=missing'], b'entropy test requires -Dsmp=false'),
        )
        for label, flags, expected in guards:
            command(base + flags, label, expected)
        modes = sorted({mode for _, mode, _ in CASES})
        for mode in modes:
            command(base + ['-Dsmp=false', '-Dentropy-test=' + mode, '-Drelease-artifact=true'], 'release-denied-' + mode,
                    b'release artifact contains an entropy lab control')
            command(base + ['-Dsmp=false', '-Dentropy-test=' + mode, '-p', str(out / mode)], mode + '-build')
        for label, mode, panic in CASES:
            variables = out / (label + '-vars.fd')
            shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
            args = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64', '-smp', '1', '-m', '256M',
                    '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
                    '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(out / mode / 'aether.iso'),
                    '-boot', 'd', '-nic', 'none', '-display', 'none', '-vga', 'std',
                    '-serial', 'file:' + str(out / (label + '-serial.log')), '-monitor', 'none', '-no-reboot', '-no-shutdown']
            if label != 'absent':
                quota = 'max-bytes=63,period=1' if label == 'partial' else 'max-bytes=65536,period=60000' if label == 'stalled' else 'max-bytes=1048576,period=1000'
                interface = 'disable-legacy=on' if label == 'modern' else 'disable-modern=on'
                args += ['-object', 'rng-random,id=random,filename=/dev/urandom',
                         '-device', f'virtio-rng-pci,rng=random,{interface},{quota}']
                if label == 'duplicate':
                    args += ['-object', 'rng-random,id=second,filename=/dev/urandom', '-device', 'virtio-rng-pci,rng=second,disable-modern=on']
            entry = {'name': label, 'argv': args, 'expected_panic': panic.decode() if panic else None,
                     'start_utc': utc(), 'status': 'incomplete'}
            report['cases'].append(entry)
            with (out / (label + '-qemu.log')).open('wb') as stream:
                process = subprocess.Popen(args, stdout=stream, stderr=subprocess.STDOUT)
                try:
                    entry['outcome'] = observe(process, out / (label + '-serial.log'), label, panic)
                finally:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=3)
                            raise RuntimeError('entropy QEMU forced teardown')
                    entry['end_utc'] = utc()
                    entry['teardown_returncode'] = process.returncode
            entry['status'] = 'pass'
        if inputs() != report['sources']:
            raise RuntimeError('entropy source drift')
        for row in report['tools'].values():
            if sha(Path(row['path'])) != row['sha256']:
                raise RuntimeError('entropy tool drift')
        for name, digest in report['firmware'].items():
            if sha(DEPS / 'firmware' / name) != digest:
                raise RuntimeError('entropy firmware drift')
        report['status'] = 'pass'
    except BaseException as error:
        report['error'] = str(error)
        raise
    finally:
        report['end_utc'] = utc()
        report['artifacts'] = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
        compact_run(out, report)
    print('[PASS] Entropy transport and semantic rejection:', out)


if __name__ == '__main__':
    parser = Parser(description=__doc__, epilog='Usage: python3 scripts/entropy_smoke.py. Requires pinned tools and dependency setup. Owns only zig-out/entropy-* and its VMs; never prints entropy bytes. Exit0/pass,1/fail,64/usage,130/interrupted.')
    parser.add_argument('--version', action='version', version='aether-entropy-smoke 1')
    parser.parse_args()
    try:
        suite()
    except KeyboardInterrupt:
        sys.exit(130)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        print(f'[FAIL] {error}', file=sys.stderr)
        sys.exit(1)
