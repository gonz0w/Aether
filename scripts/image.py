"""Create a UEFI-only optical image from the kernel and pinned boot inputs."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from deps import DEPS, ROOT, LOCK, verify


def build(kernel, output, user, display, lifecycle, smp_supervisor, native_c=None):
    verify()
    version = subprocess.run(["xorriso", "-version"], capture_output=True, text=True, check=True)
    if f"xorriso version   :  {LOCK['xorriso']}" not in version.stdout:
        raise RuntimeError("xorriso version differs from boot/dependencies.json")
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="image-", dir=output.parent) as directory:
        tree = Path(directory)
        (tree / "boot").mkdir()
        (tree / "EFI/BOOT").mkdir(parents=True)
        shutil.copyfile(kernel, tree / "boot/aether")
        shutil.copyfile(user, tree / "boot/protection.bin")
        shutil.copyfile(display, tree / "boot/display.bin")
        shutil.copyfile(lifecycle, tree / "boot/lifecycle.bin")
        shutil.copyfile(smp_supervisor, tree / "boot/smp-supervisor.bin")
        shutil.copyfile(ROOT / "boot/limine.conf", tree / "limine.conf")
        shutil.copyfile(ROOT / "LICENSE", tree / "boot/LICENSE-Aether.txt")
        if native_c is not None:
            shutil.copyfile(native_c, tree / "boot/native-c.bin")
            with (tree / "limine.conf").open("a") as config:
                config.write("    module_path: boot():/boot/native-c.bin\n")
        shutil.copyfile(DEPS / "limine/BOOTX64.EFI", tree / "EFI/BOOT/BOOTX64.EFI")
        shutil.copyfile(DEPS / "limine/LICENSE", tree / "boot/LICENSE-Limine.txt")
        shutil.copyfile(DEPS / "limine/limine-uefi-cd.bin", tree / "boot/limine-uefi-cd.bin")
        # No host disk/device access and no BIOS installation step.
        subprocess.run(["xorriso", "-as", "mkisofs", "-R", "-J", "-V", "AETHER",
                        "-eltorito-alt-boot", "-e", "boot/limine-uefi-cd.bin", "-no-emul-boot",
                        "-efi-boot-part", "--efi-boot-image", "--protective-msdos-label",
                        "-o", str(output), str(tree)], check=True, stdout=subprocess.DEVNULL)
    print("Image:", output)


if __name__ == "__main__":
    build(*sys.argv[1:])
