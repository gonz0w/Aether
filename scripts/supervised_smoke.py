"""Opt-in native C witness; never substitutes for ordinary kernel smoke."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from deps import DEPS, LOCK, verify
from emulator import wait_for_boot

def run(image):
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
        with (image.parent/'native-qemu.log').open('wb') as log:
            process=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
            try:
                wait_for_boot(process,serial,30,b'AETHER NATIVE SUPERVISION PASS')
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:process.wait(timeout=3)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
    print('PASS: sys-init native launch, readiness, output, fault/replacement, peer progress and cleanup')

if __name__=='__main__':
    try:run(sys.argv[1])
    except (OSError,RuntimeError,TimeoutError,subprocess.CalledProcessError) as e:sys.exit(str(e))
