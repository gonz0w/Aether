"""Opt-in native C witness; never substitutes for ordinary kernel smoke."""
from pathlib import Path
from datetime import datetime
import json
import shutil
import subprocess
import sys
import tempfile
from deps import ROOT, DEPS, LOCK, verify
from emulator import wait_for_boot


class NativeStopError(RuntimeError):
    """Process stop is unconfirmed; callers must retain owned media/resources."""


def run(image, expected_panic=None, panic_context=(), marker=b'AETHER NATIVE C PASS', entropy=False, rtc_base=None, block_disk=None, block_large=False, block_namespace=False, zpl_writer=None, _pair_stop=False, _zpl_writer_60s=False, _zpl_mutation_seed=False, _monitor_diagnostic=False, _storage_lifetime=False, _fs_session_writer=None, _fs_init_writer=None):
    if _fs_init_writer is not None and not (
            _pair_stop and block_namespace and block_large and block_disk is not None and
            _fs_session_writer is None and zpl_writer is None and
            not any((_zpl_writer_60s, _zpl_mutation_seed, _monitor_diagnostic, _storage_lifetime)) and
            expected_panic is None and not panic_context and marker == b'AETHER NATIVE BLOCK PASS' and
            Path(image).name == 'aether.iso' and Path(image).parent.name == 'reader' and
            Path(image).parent.parent.name.startswith('thread-suite-service-runtime-zpl-pair-fs-session-')):
        raise ValueError('init recovery requires its isolated owned reader')
    if _fs_session_writer is not None and not (
            _pair_stop and block_namespace and block_large and block_disk is not None and
            zpl_writer is None and not any((_zpl_writer_60s, _zpl_mutation_seed, _monitor_diagnostic, _storage_lifetime)) and
            expected_panic is None and not panic_context and marker == b'AETHER NATIVE BLOCK PASS' and
            Path(image).name == 'aether.iso' and Path(image).parent.name == 'reader' and
            Path(image).parent.parent.name.startswith('thread-suite-service-runtime-zpl-pair-fs-session-')):
        raise ValueError('combined recovery requires its isolated owned reader')
    if not isinstance(_storage_lifetime,bool) or (_storage_lifetime and (not _zpl_writer_60s or _monitor_diagnostic or _zpl_mutation_seed)):
        raise ValueError('storage lifetime requires the separate isolated non-monitor writer')
    if not isinstance(_monitor_diagnostic, bool) or (_monitor_diagnostic and not (
            _pair_stop and _zpl_writer_60s and not _zpl_mutation_seed)):
        raise ValueError('monitor diagnostic requires the fixed-budget pristine writer')
    if not isinstance(_zpl_mutation_seed, bool) or (_zpl_mutation_seed and not (
            _zpl_writer_60s and zpl_writer is not None)):
        raise ValueError('namespace mutation seed requires fixed-budget writer and qualified media')
    if not isinstance(_zpl_writer_60s, bool):
        raise ValueError('writer60 selector must be boolean')
    if _zpl_writer_60s and not (
            _pair_stop and block_namespace and block_large and block_disk is not None and
            (zpl_writer is not None if _zpl_mutation_seed else zpl_writer is None) and expected_panic is None and not panic_context and
            marker == b'AETHER NATIVE BLOCK PASS' and Path(image).name == 'aether.iso' and
            Path(image).parent.name == 'writer' and
            Path(image).parent.parent.name.startswith('thread-suite-service-runtime-zpl-pair-')):
        raise ValueError('writer60 requires the isolated owned ZPL writer')
    if zpl_writer is not None and not (block_namespace and block_large and block_disk is not None):
        raise ValueError('ZPL recovery requires the owned namespace fixture')
    if rtc_base is not None:
        if not isinstance(rtc_base, str) or len(rtc_base) != 19:
            raise ValueError('RTC base must be YYYY-MM-DDTHH:MM:SS')
        parsed = datetime.strptime(rtc_base, '%Y-%m-%dT%H:%M:%S')
        if parsed.strftime('%Y-%m-%dT%H:%M:%S') != rtc_base:
            raise ValueError('RTC base must be canonical')
    if block_namespace and (not block_large or block_disk is None):
        raise ValueError('namespace block requires explicit large fixture selection')
    if block_large and block_disk is None:
        raise ValueError('large block selection requires an owned disposable disk')
    if block_disk is not None:
        image = Path(image).absolute()
        owner = image.parent.parent
        block_disk = Path(block_disk).absolute()
        if (owner.parent != ROOT / 'zig-out' or not owner.name.startswith('thread-suite-service-runtime-')
                or owner.is_symlink() or owner.resolve() != owner or image.parent.is_symlink()
                or block_disk.parent not in (owner, image.parent)
                or block_disk.name != ('native-namespace.raw' if block_namespace else 'disposable.raw') or block_disk.is_symlink()
                or not block_disk.is_file() or block_disk.stat().st_size != (1024 * 1024 * 1024 + 8192 if block_namespace else 64 * 1024 * 1024 + 8192 if block_large else 16 * 1024 * 1024)):
            raise ValueError('block source requires an owned disposable disk of the selected exact size')
        if block_namespace:
            if _fs_init_writer is not None:
                from fs_init_checks import recovery_media
                recovery_media(_fs_init_writer, block_disk)
            elif _fs_session_writer is not None:
                from fs_session import recovery_media
                recovery_media(_fs_session_writer, block_disk)
            elif zpl_writer is None:
                from openzfs_namespace import native_media_snapshot
                native_media_snapshot(block_disk)
            else:
                from service_runtime_smoke import check_zpl_recovery_media
                check_zpl_recovery_media(zpl_writer, block_disk)
    verify()
    if subprocess.check_output(['qemu-system-x86_64','--version'],text=True).splitlines()[0] != 'QEMU emulator version '+LOCK['qemu']:
        raise RuntimeError('QEMU version mismatch')
    image=Path(image).resolve();serial=image.parent/'native-serial.log'
    serial.write_text('')
    with tempfile.TemporaryDirectory(prefix='native-qemu-') as d:
        variables=Path(d)/'vars.fd';shutil.copyfile(DEPS/'firmware/vars.fd',variables)
        args=['qemu-system-x86_64','-machine','pc-q35-11.1','-accel','tcg','-cpu','qemu64','-smp','1','-m','256M',
              '-drive',f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
              '-drive',f'if=pflash,format=raw,file={variables}','-cdrom',str(image),'-boot','d',
              '-nic','none','-vga','std','-display','none','-serial',f'file:{serial}','-monitor','none','-no-reboot','-no-shutdown']
        if entropy:
            args += ['-object', 'rng-random,id=random,filename=/dev/urandom',
                     '-device', 'virtio-rng-pci,rng=random,disable-modern=on,max-bytes=1048576,period=1000']
        if rtc_base is not None:
            args += ['-rtc', 'base=' + rtc_base + ',clock=vm']
        if block_disk is not None:
            args += ['-drive', 'if=none,id=work,format=raw,cache=writeback,file=' + str(block_disk),
                     '-device', 'virtio-blk-pci,drive=work,disable-modern=on']
        snapshots = None
        if _monitor_diagnostic:
            from native_monitor import Snapshots
            args += ['-qmp', 'unix:' + str(Path(d) / 'monitor.sock') + ',server=on,wait=off']
            snapshots = Snapshots(Path(d) / 'monitor.sock', image.parent / 'native-monitor.json')
        (image.parent / 'native-qemu-command.json').write_text(json.dumps({'argv': args, 'entropy': entropy, **({'writer_watchdog_seconds': 120 if _storage_lifetime else 60} if _zpl_writer_60s else {})}, indent=2) + '\n')
        with (image.parent/'native-qemu.log').open('wb') as log:
            process=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
            try:
                wait_for_boot(process,serial,120 if _storage_lifetime else 60 if _zpl_writer_60s else 30,marker,expected_panic,panic_context,
                              **({'poll': snapshots.poll} if snapshots is not None else {}))
            finally:
                try:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            if _pair_stop:
                                process.wait(timeout=3)
                            else:
                                process.wait()
                except (OSError, subprocess.SubprocessError) as error:
                    if _pair_stop:
                        raise NativeStopError(f'native VM stop unconfirmed (pid={process.pid}); retain owned resources') from error
                    raise
    if expected_panic is not None:
        print('PASS: expected native panic:', expected_panic.decode())
        return
    if marker == b'AETHER NATIVE C PASS':
        print('PASS: native C startup, two contexts and terminal cleanup; no general POSIX runtime claim')
    else:
        print('PASS: expected native profile marker:', marker.decode())

if __name__=='__main__':
    try:run(sys.argv[1])
    except (OSError,RuntimeError,TimeoutError,subprocess.CalledProcessError) as e:sys.exit(str(e))
