"""Run QEMU with disposable firmware state; bounded smoke tests never open a UI."""
import argparse
import binascii
import json
from pathlib import Path
import shutil
import socket
import subprocess
import struct
import tempfile
import time
import zlib
from deps import ROOT, DEPS, LOCK, verify

PASS = b"AETHER FAULT RECOVERY PASS"


def wait_for_boot(process, log, timeout, marker=PASS, expected_panic=None, panic_context=(), poll=None):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = log.read_bytes() if log.exists() else b""
        if expected_panic is not None:
            # Ignore an incomplete UART line; matching a prefix could accept a
            # different panic. A successful guest cannot satisfy a negative.
            lines = data.split(b"\n")[:-1]
            if marker in [line.rstrip(b"\r") for line in lines]:
                raise RuntimeError("unexpected boot success in negative test")
            panics = [line.rstrip(b"\r") for line in lines if b"AETHER PANIC:" in line]
            if panics:
                if panics != [b"AETHER PANIC: " + expected_panic]:
                    raise RuntimeError("unexpected kernel panic (see serial log)")
                complete = [line.rstrip(b"\r") for line in lines]
                before = complete[:complete.index(panics[0])]
                for required in panic_context:
                    if required not in before:
                        raise RuntimeError("expected panic lacks ordered execution context")
                    before = before[before.index(required) + 1:]
                if process.poll() is not None:
                    raise RuntimeError("QEMU exited during negative test")
                return
            if process.poll() is not None:
                raise RuntimeError("QEMU exited before expected panic")
            time.sleep(0.05)
            continue
        if b"AETHER PANIC:" in data:
            raise RuntimeError("kernel panic (see serial log)")
        if process.poll() is not None:
            raise RuntimeError(f"QEMU exited before boot completed: {process.returncode}")
        if marker in data.splitlines():
            return
        if poll is not None:
            poll()
        time.sleep(0.05)
    raise TimeoutError(f"no boot success marker within {timeout}s")


def screenshot(path, output):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(5)
        client.connect(str(path))
        with client.makefile("rwb") as stream:
            json.loads(stream.readline())  # Greeting.
            for command in [{"execute": "qmp_capabilities"},
                            {"execute": "screendump", "arguments": {"filename": str(output)}}]:
                stream.write(json.dumps(command).encode() + b"\n")
                stream.flush()
                while True:
                    response = json.loads(stream.readline())
                    if "error" in response:
                        raise RuntimeError(response["error"])
                    if "return" in response:
                        break


class FramebufferMismatch(RuntimeError):
    """A complete, correctly formatted capture contains incorrect guest pixels."""


def check_framebuffer(path, display=False):
    # QMP emits this simple P6 header. Check the actual guest's pixels, not
    # merely whether screendump created a file, then encode a lossless PNG.
    magic, dimensions, depth, pixels = path.read_bytes().split(b"\n", 3)
    if magic != b"P6" or depth != b"255" or dimensions != b"800 600":
        raise RuntimeError("unexpected framebuffer dimensions or screenshot format")
    width, height = 800, 600
    if len(pixels) != width * height * 3:
        raise RuntimeError("truncated framebuffer capture")
    samples = {(0, 0): (255, 255, 255), (400, 100): (24, 32, 48),
               (100, 300): (255, 0, 0), (400, 300): (0, 255, 0),
               (700, 300): (0, 0, 255), (10, 415): (40, 180, 180),
               (40, 415): (16, 70, 90), (10, 432): (16, 70, 90)}
    if display:
        samples[(400, 164)] = (80, 220, 180)
        samples[(400, 480)] = (80, 220, 180)
        samples[(400, 540)] = (80, 140, 240)
    for (x, y), expected in samples.items():
        offset = (y * width + x) * 3
        if tuple(pixels[offset:offset + 3]) != expected:
            raise FramebufferMismatch(f"framebuffer pixel mismatch at {x},{y}")

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", binascii.crc32(kind + data) & 0xffffffff))

    rows = b"".join(b"\0" + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
           chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))
    path.with_suffix(".png").write_bytes(png)


def verify_framebuffer(path, display=False, expected_failure=False):
    try:
        check_framebuffer(path, display)
    except FramebufferMismatch:
        if not expected_failure:
            raise
        return
    if expected_failure:
        raise RuntimeError("unexpected correct framebuffer in negative test")


def run(mode, image, timeout=30, cpus=2, expected_panic=None, panic_context=(), expected_pixel_failure=False):
    if expected_pixel_failure and (mode != "smoke" or expected_panic is not None):
        raise ValueError("pixel negative requires successful smoke boot")
    if expected_panic is not None and mode != "smoke":
        raise ValueError("expected panic requires smoke mode")
    verify()
    version = subprocess.check_output(["qemu-system-x86_64", "--version"], text=True)
    if version.splitlines()[0] != "QEMU emulator version " + LOCK["qemu"]:
        raise RuntimeError("QEMU version differs from boot/dependencies.json")
    image = Path(image).resolve()
    evidence = image.parent
    if mode == "smoke":
        for name in ("framebuffer.ppm", "framebuffer.png"):
            (evidence / name).unlink(missing_ok=True)
    serial = evidence / "serial.log"
    serial.write_bytes(b"")
    # /tmp keeps the UNIX socket path within macOS's length limit.
    with tempfile.TemporaryDirectory(prefix="aether-", dir="/tmp") as directory:
        temp = Path(directory)
        variables = temp / "vars.fd"
        shutil.copyfile(DEPS / "firmware/vars.fd", variables)
        qmp = temp / "qmp.sock"
        command = ["qemu-system-x86_64", "-machine", "pc-q35-11.1", "-accel", "tcg",
                   "-cpu", "qemu64", "-smp", str(cpus), "-m", "256M",
                   "-drive", f"if=pflash,format=raw,readonly=on,file={DEPS / 'firmware/code.fd'}",
                   "-drive", f"if=pflash,format=raw,file={variables}",
                   "-cdrom", str(image), "-boot", "d", "-nic", "none",
                   "-vga", "std", "-serial", f"file:{serial}", "-monitor", "none",
                   "-no-reboot", "-no-shutdown"]
        if mode == "smoke":
            command += ["-display", "none", "-qmp", f"unix:{qmp},server=on,wait=off"]
        with (evidence / "qemu.log").open("wb") as diagnostics:
            process = subprocess.Popen(command, stdout=diagnostics, stderr=subprocess.STDOUT)
            try:
                if mode == "run":
                    print("QEMU running; close its window or press Ctrl-C here. Serial:", serial, flush=True)
                    return process.wait()
                wait_for_boot(process, serial, timeout, PASS if cpus == 2 else b"AETHER LIFECYCLE V1 PASS", expected_panic, panic_context)
                if expected_panic is not None:
                    print("PASS: expected panic:", expected_panic.decode("ascii"), flush=True)
                    return 0
                screenshot(qmp, evidence / "framebuffer.ppm")
                verify_framebuffer(evidence / "framebuffer.ppm", display=cpus == 2,
                                   expected_failure=expected_pixel_failure)
                if expected_pixel_failure:
                    print("PASS: guest completed; expected framebuffer pixel mismatch", flush=True)
                    return 0
                print(f"PASS: {cpus}-CPU acceptance complete; framebuffer captured in", evidence)
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["run", "smoke"])
    parser.add_argument("image")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--cpus", type=int, choices=[1, 2], default=2)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    try:
        raise SystemExit(run(args.mode, args.image, args.timeout, args.cpus))
    except KeyboardInterrupt:
        parser.exit(130, "Stopped QEMU.\n")
    except (OSError, RuntimeError, TimeoutError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"FAIL: {error}\n")
