# Readiness diagnostics and Linux acceptance — 2026-09-05

[Decision 0015](../../decisions/0015-host-readiness-diagnostics.md) adds a separate
128-record bounded diagnostic deque: SYSINIT-READY-CLOSED, INCOMPLETE and MALFORMED
with service/generation and a 0–6 received-byte count. Raw payload and descriptor
values are absent. Existing invalid-ready tuples, first-frame acceptance,
termination requests and lifecycle policy remain unchanged. Three new test methods
verify all codes, one-record behavior, per-generation association and no false
error for valid frames with trailing bytes. A failure record does not prove death.

[macOS report](macos/results.json) and [Linux report](linux/results.json) both pass:
48 host tests, 34 model tests/three mutation controls, 23 harness tests, the
22-recorded-case native evidence audit and three offline standards checks.
Recorded source SHA-256 maps match exactly and remain unchanged during both runs.
There was no new native Aether execution. Historical native bundles remain intact.

[Decision 0016](../../decisions/0016-linux-host-validation.md) consumes an existing
running Podman applehv VM and cached local Aether-userland reference image, pinned
by image ID and digest in [container command/identity](container.json). No image
was downloaded/built and no new VM or CI provider was configured. The test
container was ephemeral, with no network, read-only root/source, a private report
mount/tmpfs, dropped capabilities, no privilege escalation, and bounded CPU,
memory and process count. Only the private report location was writable on the
host mount. The Linux source snapshot remains at the recorded local path.

Linux reports kernel 6.18.10-200.fc43.aarch64, glibc 2.41 and Python 3.13.12.
This is Linux container behavior in that VM, not bare-metal Linux, every Linux
distribution, BSD, illumos or native Aether. Image digests identify trusted local
bytes; no publisher authenticity/full upstream provenance claim is added. Parent-
death/helper tests retain their explicit unobserved external reaping limitation.

Docker's default socket was absent. Podman inventory initially needed host access
for its VM lockfile; the permitted inventory then confirmed the running VM. This
was an available alternative, so the previous Linux-unavailable gate was lifted.
No companion source or user services were modified; the VM was left in its prior
running state and the --rm test container exited successfully.

Reproduce with the exact cached image and command structure in container.json,
a fresh frozen source snapshot and private writable result mount. The ordinary
entry point remains `python3 scripts/check-all.py`. Exact per-check commands,
counts, logs, host identity and source hashes are retained in each report tree.
SHA256SUMS.json fingerprints this bundle. [Remaining inputs](../../INTEGRATION-GATES.md)
now bound this workstream: BSD/illumos environments, CI provider/remote selection,
and accepted native clock/wait, delegation and supervisor-recovery contracts.
