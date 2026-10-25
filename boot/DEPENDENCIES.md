# Dependencies and boot contract

The machine-readable pins and download hashes are in [dependencies.json](dependencies.json). `python3 scripts/deps.py` downloads and verifies the boot inputs. Builds and runs subsequently use only local files; they do not fetch dependencies. `.deps/` is disposable and excluded from version control.

## Validated environment

| Component | Version / source |
| --- | --- |
| Zig | 0.16.0; LLVM and LLD explicitly selected for the kernel |
| Rust | 1.98.0, `x86_64-unknown-none`; pinned in `rust-toolchain.toml` |
| QEMU | 11.1.1; `pc-q35-11.1`, TCG, `qemu64`, two CPUs by default / one for M2 regression, 256 MiB |
| xorriso | 1.5.8.pl02 |
| Python | 3.14.7 tested; scripts use the standard library |
| Limine | 12.7.0 official binary release, SHA-256 pinned |
| Limine protocol | Commit `617369cb577108e483c096e373c4f2ecc9d2081d`; base revision 6 |
| OVMF | QEMU v11.1.1's `edk2-x86_64-code.fd.bz2` and `edk2-i386-vars.fd.bz2`; compressed and decompressed hashes pinned |

Tested on arm64 macOS using Homebrew tools. Other hosts are not yet validated. Build, image, and emulator entry points reject a mismatched Zig, xorriso, or QEMU version respectively. The Rust fixture builder rejects a mismatched Rust version. Install its target during setup; subsequent builds require no registry packages or downloads.

Use the versions above, not moving `latest` references. Homebrew installation is a convenience for the current host, not a permanent lock mechanism; if it supplies a different release, install the pinned official version or deliberately update the pins and rerun all checks. Firmware is fetched independently so a different system OVMF installation cannot silently change the boot path.

## Sources and notices

- [Limine release](https://github.com/Limine-Bootloader/Limine/releases/tag/v12.7.0). Its BSD-2-Clause license is retained in `.deps/limine/LICENSE` and copied into the generated image as `/boot/LICENSE-Limine.txt`.
- [Limine protocol header](https://github.com/Limine-Bootloader/limine-protocol/blob/617369cb577108e483c096e373c4f2ecc9d2081d/include/limine.h). The minimal Zig ABI declarations follow its 0BSD definitions; attribution is in [LICENSE-Limine-Protocol.txt](LICENSE-Limine-Protocol.txt).
- [QEMU firmware inputs](https://github.com/qemu/qemu/tree/v11.1.1/pc-bios) and [firmware provenance](https://github.com/qemu/qemu/blob/v11.1.1/pc-bios/README). Firmware remains a local development dependency and is not embedded in the ISO. Preserve upstream firmware notices when separately redistributing it.

Original Aether work is licensed under [BSD-2-Clause](../LICENSE); the image builder
includes that text at `/boot/LICENSE-Aether.txt`. Third-party
redistribution review remains required; this does not relicense boot inputs.

## Boot contract and limitations

Limine loads a higher-half ELF with separate writable request/data segments, executable text, and read-only data. Zig uses the System V entry ABI with FP/SIMD disabled, no red zone, and Debug safety checks. The kernel requests the memory map, framebuffer, HHDM, executable load address, four ordered boot modules, and (for M3) MP bootstrap information, and verifies base revision support before reading responses. The protection module is a Rust fixture compiled using the target’s soft-float/no-red-zone defaults and a checked one-page flat-image linker script.

Boot response pointers and the bootloader are trusted inputs. Counts, ranges, and framebuffer arithmetic are checked; the renderer accepts RGB 32-bpp with non-overlapping 8-bit masks, dimensions 1–8192, aligned row pitch, and a span no larger than 256 MiB. Other formats stop with a serial panic. The emulator fixture requests 800×600; smoke checks that exact output.

The M2 [protection contract](../.planning/M2-PROTECTION.md) describes private lower-half page tables, supervisor upper-half mappings, user RX code and RW/NX stacks, GDT/TSS/IDT setup, and ring-3 fault/preemption fixtures. The software interrupt supports fixture exit and the bounded [endpoint capability ABI](../.planning/M2-CAPABILITIES.md). A kernel exception panics; expected user faults advance the test harness to a fresh domain. The subsequent factory experiment performs explicit bounded task teardown. Boot mappings, firmware, response data, and initial fixture pages remain reserved. Only the factory worker’s two backing pages are reused under the [lifetime contract](../.planning/M2-LIFETIME.md). A fixed round-robin scheduler saves general registers and uses the legacy PIC/PIT on the one-CPU q35 baseline; it disables the local APIC because Limine masks LINT0. IRQ0 is the only unmasked device interrupt, and interrupt gates keep the kernel non-preemptible. The boot CPU also owns fixed endpoint capability tables, derivation nodes, and a four-message FIFO. The typed factory/task/memory extension authorizes one worker and its backing bundle, with checked mapping removal and zeroing before reuse. There is no general allocator, boot-memory reclamation, arbitrary program loader, or GPU command submission. FP/SIMD use traps in the default Rust fixture profile. The opt-in [native C experiment](../docs/NATIVE-C.md) has separately bounded x87/SSE context support.

The emulator uses read-only firmware code, a per-run copy of variables, no guest networking, and the generated ISO. It never writes a host boot device. A graphical run owns its QEMU process until the window closes or Ctrl-C is pressed; smoke runs terminate their process on success, panic, launch failure, or timeout.

The default image completes M2 with the AP parked, then runs the
[M3 kernel bring-up probe](../.planning/M3-BRINGUP.md). Limine MP structures are
ABI-checked; AP entry is release-published after initialization. Each CPU owns a
probe stack/GDT/IDT and counter. Two bounded queues use acquire/release atomics.
The kernel is built without Zig's single-threaded assumption. The subsequent [per-core user phase](../.planning/M3-USER-CORES.md) runs Rust
on both CPUs using private page tables/TSS/contexts and local APIC timers. The
AP does not participate in M2 backing reuse. PIC delivery is masked before
the user phase; the APIC page is mapped supervisor-only, UC, and NX. Timer
initial count/divisor is fixed for QEMU and is not a calibrated timing API.

## Display boot module

The default image contains four ordered modules: the protection fixture, the display
service, the lifecycle supervisor, and the separate SMP supervisor. The opt-in
[native C experiment](../docs/NATIVE-C.md) adds a fifth module. Protection/display are immutable flat
images capped at one code page and use the same fixed entry/linker layout. The
lifecycle module adds a validated v1 header and can be explicitly supplied from
another project; see [the lifecycle profile](../.planning/M4-LIFECYCLE-V1.md). `scripts/display.py` builds the second
image with pinned Rust and no packages. The kernel copies it before dropping boot
mappings. Default SMP rendering is performed by this service; one-core regression
mode retains the original kernel pattern. See [display contract](../.planning/M4-DISPLAY.md).
