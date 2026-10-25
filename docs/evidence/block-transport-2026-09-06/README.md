# First persistent block transport — 2026-09-06

The opt-in BSP driver reads/writes 512-byte sectors through QEMU transitional
virtio-blk, negotiates FLUSH and checks its completion. A fresh QEMU process reads
the sector changed by the first process. Whole-disk comparison confirms all other
bytes remain unchanged. This is controlled VM-restart persistence, not a mounted
filesystem, power-loss durability, native service grant or installed package.

[Contract and limits](../../BLOCK-DEVICE.md) records the pre-implementation scope,
static DMA ownership, protocol reference, bounds and incomplete coverage. No user
pointer or untrusted descriptor is supplied to the device. All disk files are
created privately by the harness; it accepts no existing disk path.

## Attempts

- block-v_jjqoo2: build failure only. The block-only noreturn path excluded the
  protection exception handler, but still linked unused interrupt assembly. The
  corrected block-only build omits that assembly. Normal/native builds retain it.
- block-rzh3hf44: initial six-case pass, before duplicate-device coverage was added.
- block-8qk5y9v2: deliberately writes the wrong pattern while reporting guest
  success. The host rejects at `whole-disk data mismatch: write`. The separate
  control receipt classifies this expected failure; original bytes were restored
  before final qualification. Its incomplete suite report is not a product pass.
- block-kol5l3p0: final seven cases pass: write, fresh-process verification, absent
  device, duplicate devices, read-only device, unsupported queue size and corrupt
  input. Positive reads wrap the queue position repeatedly (300 requests); an
  out-of-range request rejects before submission. All negative-case disk bytes
  remain unchanged, including the second disk in the duplicate-device test.

Final block-final-2026-09-06/results.json records exact commands, UTC intervals and
exit statuses. Additional passes: two composed console cases, seven M4 regressions,
one-core boot/framebuffer smoke, host checks (85 Python cases plus kernel and all
standards/workflow checks), scoped Zig formatting and Experience validation.

Console/M4 artifacts, all block attempt images/logs/envelopes as applicable and
hash-verified source archives are retained. Final runtime sources match the final
block receipt. Wrapper scripts are included; the corruption-control script edits
a source file temporarily and must have exclusive working-tree access. The one-
core ISO is retained separately. Installed local toolchain/dependency selection
is not an independent committed build or full transitive provenance attestation.

## Claim boundaries

FLUSH support is required and the submitted command must complete successfully.
However, QEMU shutdown can flush its backend, so the restart test is not an
independent proof of FLUSH efficacy. Power-loss, missing-FLUSH injection, timeout/
malformed-completion injection, physical devices and IOMMU isolation remain open.
No backing is reclaimed after an uncertain request; the experiment halts with
static DMA buffers retained until VM teardown. This is not general device recovery.

Normal boot does not run this driver. The next step is a caller-bound, sector-
scoped block grant with copied buffers, followed by the Rust filesystem service
and mature engine. Filesystem selection, snapshot/rollback scope and end-to-end
shell/package/sys-init assembly remain open. No sibling repository or consumer
pin changed. Retain all attempts under DEVELOPMENT policy.
