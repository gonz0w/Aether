# Scoped native block grant evidence — 2026-09-06

[Native block v1](../../NATIVE-BLOCK.md) passes on the frozen final sources.
AENBD001 / ABI 13 gives one sector of authority to a specific caller, permits
one-hop rights reduction, and binds the recipient to its task generation.
Full user-buffer validation precedes synchronous I/O through kernel-owned copies;
no user address becomes a DMA descriptor. This is not a filesystem service.

## Final checks

native-block-final-2026-09-06/results.json records commands, UTC intervals and
zero exits for every selected command:

- Five native cases: write/flush, verification in a fresh VM, read-only attenuation,
  actual recipient fault, and corrupt seed rejection. Successful cases reclaim
  three generations; rejected input has supervisor 841/reclaimed 1 and the exact
  native-profile panic. Whole-disk comparison confirms out-of-scope bytes unchanged.
- Seven original hardware cases, two composed console cases, seven M4 regressions,
  and one-core boot/framebuffer smoke.
- Host checks (85 Python cases plus kernel and offline standards/workflow checks),
  scoped Zig/Rust/C formatting and Experience verification.

Client assertions cover forged selectors, non-owner access, read/write/flush
rights, stale/terminal transfer targets, rejected rights, relative sector bounds,
exact transfer length, invalid/overflowing/read-only buffers, onward-transfer
rejection and permanent close. The mapped byte before an invalid destination
boundary retains its sentinel, proving preflight rejection does not partially
change that user buffer. The fault case requires generation 2, kind 2/detail 134
before the replacement denial; it does not close the grant before faulting.

## Attempts

block-7zppbnwp is the initial passing native suite before the explicit buffer
sentinel assertion. The final wrapper repeats the full suite after that addition.
Every attempt's source archive is checked against every original receipt digest.

block-8xy5zwm7 is the deliberate broken-generation control. Its kernel omits only
the block recipient generation comparison; its harness selects only the existing
fault case without changing its oracle. After the recipient faults, a replacement
can incorrectly read the sector. The client catches that access and rejects at
supervisor 844/reclaimed 2. The wrapper classifies the suite's incomplete status
as the expected generation rejection. Both kernel and case-selection source bytes
were restored in a finally block before final qualification. No unplanned failure.

Final attempt paths are in the wrapper logs. All native artifacts, source archives,
SDK receipt/archive/tool-lock hashes, raw serial and build logs are retained.
Hardware/console/M4 archives and the one-core ISO preserve selected regressions.
The two wrapper scripts are included; the mutation wrapper temporarily changes
source and requires exclusive working-tree access. Local installed toolchain
selection is not independent committed-build or complete transitive provenance
attestation. No sibling checkout, service ownership or consumer pin changed.

## Limits

Only one fixed sector is exposed. A filesystem-sized range contract and production
Rust service are still missing. Device failure/timeout is fail-stop with static DMA
backing retained, not recoverable I/O or asynchronous progress. Reopening/recovery,
physical hardware, IOMMU isolation, timeout injection and independent consumer
adoption remain pending. Fresh-VM persistence does not establish power-loss
safety; QEMU shutdown may flush its backend. Existing hardware durability limits
remain applicable. Retain all attempts under DEVELOPMENT policy.
