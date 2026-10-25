# Checked libzpool random boundary — 2026-10-04

The [before-code contract](contract.md) ports the actual four random helper entry
points from OpenZFS2.4.4 commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1 to the
[explicit native grant](../../NATIVE-ENTROPY.md). Original full kernel.c and CDDL
header/notice, private whole-source port and exact diff are preserved. Only the
selected helper block is compiled/executed; the whole engine is not rebuilt or run.
A header review adds explicit standard/auxv prototypes to whole-source preparation;
the byte-identical component block is unchanged. Both preparation versions remain.

First12 and second13 cases pass; fresh final15 cases pass. Actual random_get_bytes
and pseudo_bytes receive real bounded/chunked draws. Missing/duplicate init, absent
or disabled authority, quota exhaustion, null/overflow/oversized buffers, after-fini,
reinit and duplicate fini terminate125. An invalid second-chunk mapping after real
partial progress terminates125 and never returns success. A deliberately ignored
fatality control reaches exact255 and is rejected. Old TLS/memory/output/64-yield
checks remain. Three supervised admissions reset state/authority/quota; real8192-byte
backend exhaustion reaches generation2 then the exact kernel DMA-retained timeout.
All owned VMs terminate within the teardown bound; no discarded failed attempts.

Empty requests require initialized state. Calls larger than256 bytes use bounded
chunks within the4096-byte fixture budget. Per-chunk kernel validation protects
mappings; a later failure may follow earlier completed bytes and is fatal, not a
returned-success or unchanged-buffer promise. Init proves one real granted byte;
fini permanently closes this domain lifetime. Service restart requires a fresh
explicit native admission. No ambient host path/FD, fallback bytes, wall clock or
entropy quality/reseed policy is supplied. Concurrent init/fini/retirement remains
owner work; these tests do not certify production cryptography or scheduling latency.

Full137 Python host cases plus Zig/Rust/offline pins/workflow and scoped C syntax/
format/source identity/simplicity/link checks pass. Existing required hardware/M4/
older native block regressions remain bound by the preceding unchanged-runtime
[native entropy packet](../native-entropy-2026-10-04/README.md); no kernel change in
this component step. Setup reads back all1979+5037 members from sealed provider and
source archives, staging only241 regular SDK files and the original kernel.c.
No mutable sibling, release pin, SDK or kernel-limit change is made.

Reproduce with pinned offline setup: `python3 docs/evidence/openzfs-native-random-2026-10-04/setup.py`
then `python3 docs/evidence/openzfs-native-random-2026-10-04/native.py` and the scoped
checks. Each build180seconds, VM30seconds, owned teardown3seconds; forced kill fails.
Clang/LLD21.1.8, Rust1.98.0, Zig0.16.0, QEMU11.1.1/qemu64/q35/TCG and pinned firmware
are bound with actual commands, UTC times, artifact/tool/source digests and raw logs.
Every archive member is read back before only owned verified duplicate cleanup.
Derived port source remains CDDL-1.0; new original probes/tooling are BSD-2-Clause,
with original musl/OpenZFS notices retained. No full-engine or release readiness claim.

Next measure actual task-queue/memory service policy before owner-local admission;
current default engine still exceeds8-MiB/two-child/four-admission limits. Identity,
configuration, remaining feature closure and actual whole-engine startup/fini/
restart still precede granted volume/filesystem/package composition.
