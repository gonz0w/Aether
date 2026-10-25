# SI-07 authority and wake controls — 2026-09-29

Status: scoped mechanism checks pass; real-command composition remains blocked.
The completed packet is sealed by SHA256SUMS. Prior evidence stays immutable.

Results: positive-3 and positive-repeat each observe3015 total/3007 idle ticks,
six exact worker lifetimes/reclaims and authorized halt. Wrong-expectation exits77,
is reclaimed/stale-denied, then causes the explicit owner rejection. All119 Python
plus configured Zig/Rust/pin tests and six optimized core tests pass. Kernel bytes
match the prior recovery packet (`scope.json`); broad kernel regressions are not
rerun or newly claimed for a test-fixture-only change.

The blocked userland decoders are rechecked in consumer-dependency.json. There is
no new sustained contract or independent recovery replay. No sibling is modified.
These fixtures do not implement sys-init policy, the real command protocol, a
shared SDK or full R1 shell. Exhaustive native race and finite-sequence exhaustion
remain distinct from the bounded guest and host-model evidence here.

Before-code scope: extend the existing experimental mechanism witness, without
changing kernel mechanisms, ABI22, grants or quotas. An ordinary Rust worker must
receive EACCES for owner-only event snapshot/park/halt, UART and factory operations,
even when it supplies the correct numeric grant. Launch/observe/reclaim it six times
with disjoint instance identities and stale-handle rejection. The owner checks
publication before compare/park, terminal-event wake, invalid reserved fields with
unchanged sequence, UART level readiness across two waits without consuming the
byte, and deadline completion after consumption. Retain >3000 actual idle ticks.

The worker has no libc or consumer protocol, and cannot substitute for the blocked
real runner/bytecount. Its ELF entry aligns the native initial stack before calling
Rust; borrowed trap buffers stay live for synchronous operations, and no heap,
writable static or new production unsafe boundary is introduced. Reuse existing
link scripts and the existing three-image envelope. No new service or kernel flag.
The simpler alternative of only host state tests misses actual caller enforcement
and scheduler wiring; this small guest fixture supplies those checks. Owner policy
and versioned userland decoders remain with their existing owners.

Freeze each attempt and retain outputs. Required checks: existing host suite,
optimized core checks, native positive, explicit wrong-expectation worker control,
exact six terminal identities/reclaims, real serial input and authorized halt.
Timeout or generic crash cannot satisfy the negative. Update the canonical SI-07
reference/workflow/STATE with measured results. Independent sys-init consumption,
full SI-07 qualification and real-command generations beyond2 remain blocked.


Attempt positive-1 failed before launch: the generic raw-owner link script did
not satisfy the native ELF requirement for mapped PHDR/TLS/NX-stack headers.
Its complete artifacts and sources are retained. A dedicated tiny worker ELF
script now supplies those existing headers and an unused one-byte read-only TLS
template; the kernel parser is unchanged. The first host driver stopped on a
partial panic prefix; subsequent attempts retain the complete panic line before
classifying it. This first failure has no complete reason line and is not a
passed negative control. Original driver bytes are retained separately.


Positive-2 also failed loader preflight. Readelf identified a zero-sized PT_PHDR:
the custom script needed the PHDRS keyword on that segment. Corrected the script,
not the loader. The complete invalid-launch panic and failed ELF are retained.


## Resource and evidence review

The raw owner is2880 bytes. Inspection aid stack.py bounds its stack at352/4088
bytes; its only indirect call resolves through400b38 to immutable memset400a80.
No register-indirect calls exist. The scalar worker's linked assembly uses168
stack bytes including the aligned entry call and deepest exit-call chain; this
is a bounded contributor inspection, not independent/formal stack verification.
The identical owner bytes run in both positives and the negative control.

Per-attempt source snapshots, build commands, ISO/ELF/raw images, firmware-variable
copies, serial logs and errors are retained. The first two loader failures never
count as passing controls. The original short-panic driver is retained separately.
Completed output roots are archived, every archived member is read back and
compared with the live source, then redundant owned roots are removed.

Run the self-building driver from the repository root with a new attempt label;
use --wrong-expectation for the exact negative. The source/support replay export
includes the complete previously established build support plus current fixture
sources and this driver. It is hash-verified; no separate exported-tree native run
is claimed. Firmware and tool provenance are pinned/recorded. Existing generation
limits, grant checks, input protocols and machine markers are preserved.
