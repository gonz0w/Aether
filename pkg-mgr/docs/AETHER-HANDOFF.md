# Aether boot-artifact handoff

> Update 2026-09-05: the [five-artifact v2 handoff](BOOT-HANDOFF-V2.md) now passes current target smoke and pixel validation. Earlier pair/mismatch descriptions below are historical evidence; the legacy adapter remains unchanged.

Validated: 2026-09-05. `mk/aether-boot.sh` stages a pinned kernel/boot-fixture pair for Aether's existing `scripts/image.py` file-input interface. The resulting image passed Aether's existing two-CPU smoke test. This is a boot-image handoff, not native package installation, a selected package ABI, or service activation.

## Implemented interface

```sh
sh mk/aether-boot.sh stage "$fixture_root" "$kernel" "$user_fixture" "$kernel_sha256" "$user_sha256"
sh mk/aether-boot.sh verify "$fixture_root"
```

ROOT must be an initialized private build root. Inputs are explicitly named readable regular files with expected lowercase SHA-256 digests. The adapter checks the kernel's ELF64/little-endian/x86_64 executable header and the fixture's 1–4096-byte bound. This is not a complete ELF validator or proof that the two files are compatible. The consuming boot test supplies the runtime evidence.

The adapter verifies source hashes, copies into a private adjacent temporary directory, verifies the copied bytes, and publishes a new `ROOT/aether-boot` directory. Existing bundles cannot be replaced. A failed publication leaves the destination absent and removes pending output. Single-writer and trusted-host assumptions from the build fixture still apply.

```text
ROOT/aether-boot/
  boot/aether
  boot/protection.bin
  manifest.tsv
  receipt.kv
```

The manifest contains sorted regular-file hash/size/path rows. The receipt has an exact fixed schema, records the two hashes, labels the target `x86_64` with `unversioned-aether-fixture` ABI, and explicitly marks source authenticity unproven and service activation unsupported. Verification rejects unknown entries, unsupported filesystem types/links, receipt changes, and byte/manifest mismatches. Header-shaped synthetic unit fixtures are never described as bootable kernels.

Host OS/architecture and observed interpreter/emulator versions belong in the separate run evidence, not the target ABI. The adapter does not infer compiled provenance from a nearby source checkout or a toolchain pin. This transport bundle is separate from staged-package records: the existing package build-record schema describes a local source fixture and must not be fabricated to attest an imported kernel binary.

## Existing consumer commands

After verifying a bundle, these are the actual Aether interfaces exercised:

```sh
mkdir "$fixture_root/run"
PYTHONDONTWRITEBYTECODE=1 python3 "$aether_source/scripts/image.py" \
    "$fixture_root/aether-boot/boot/aether" "$fixture_root/run/aether.iso" \
    "$fixture_root/aether-boot/boot/protection.bin"
PYTHONDONTWRITEBYTECODE=1 python3 "$aether_source/scripts/emulator.py" \
    smoke "$fixture_root/run/aether.iso" --cpus 2
```

They require Aether's already provisioned boot dependencies and pinned image/emulator tools. Python, xorriso, and QEMU are optional live integration dependencies owned by that project; they are not added to pkg-mgr's ordinary shell fixture suite. The image builder reads its own Limine configuration and dependencies, so the bundle alone is not a standalone/reproducible ISO specification.

No companion implementation was changed. `PYTHONDONTWRITEBYTECODE` prevented Python cache writes there, and image, firmware-temporary, and smoke outputs stayed in disposable paths. The emulator ran headless with networking disabled and no physical-disk installation. Its local QMP socket required sandbox escalation; the initial restricted attempt failed before boot, then the permitted run passed.

## Recorded live result

To avoid choosing among potentially incompatible build-cache entries, this review copied the existing `~/DEV/Aether/zig-out/aether.iso` and extracted both `/boot/aether` and `/boot/protection.bin` from that same snapshot. Those hashes were supplied to the staging adapter. Aether's image builder consumed the staged copies, and its smoke harness accepted `AETHER SMP IPC PASS` plus the framebuffer checks on two CPUs.

- [Run identity and ISO hashes](evidence/aether-boot-2026-09-05/run.kv).
- [Target receipt](evidence/aether-boot-2026-09-05/receipt.kv) and [payload manifest](evidence/aether-boot-2026-09-05/manifest.tsv).
- [Guest serial evidence](evidence/aether-boot-2026-09-05/serial.log) and [framebuffer](evidence/aether-boot-2026-09-05/framebuffer.png).
- [Hashes of reviewed companion files](evidence/aether-boot-2026-09-05/reviewed-sources.sha256), captured at review closeout; these are not a compiled-source attestation.

Large input/output images remain at the temporary root recorded in run.kv and may be removed by host cleanup. The small evidence above is retained in the repository. No bit-for-bit rebuild claim, arbitrary executable loader, target shell, package installation, or sys-init integration follows from this successful boot transport.

## Next boundary

Sys-init currently tracks its package/service contract as BG-027, pending. See [the package-side service proposal](SERVICE-HANDOFF.md). A boot module consumed by Limine is not a sys-init service descriptor. General target ABI/versioning, userland artifact loading, and service enablement require their respective owners' contracts before widening this interface.
