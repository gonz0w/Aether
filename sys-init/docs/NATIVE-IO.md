# Native I/O lifecycle fixture

Current consolidated index: [native coverage and contract gaps](NATIVE-COVERAGE.md).
The sections below preserve the sequence of bounded extensions.

2026-09-05: the independently owned Rust io.rs client launches two successive
musl descriptor probes through Aether's AENFD001 profile (ABI 2). It waits for
readiness, fills the bounded input queue, verifies backpressure, seals the producer,
checks separate exact stdout/stderr bytes and EOF, observes normal terminal status,
reclaims backing and checks that the old handle cannot read output. The second
fresh generation repeats those checks. Sys-init owns only fixture policy here;
libc descriptor mapping belongs to Aether-userland, and byte enforcement to Aether.

Build with `python3 scripts/build-native-supervisor.py NATIVE_C_BIN OUTPUT --variant io`.
The supplied C envelope must be produced by Aether-userland's `build.py --io`.
Use its `experiments/native-c/test_io.py` for an isolated target run and semantic
controls. Existing native-supervision variants retain their protocol and pass.

[Exact kernel interface](../../docs/NATIVE-IO.md),
[consumer and compatibility inventory](../../userland/docs/NATIVE-DESCRIPTORS.md).
Evidence is under docs/evidence/native-io-2026-09-05/. Normal, bad-reference-count,
withheld-output and skipped-zeroing outcomes are verified separately; merely
exiting nonzero cannot pass a negative case.

No service configuration, durable selection, console policy, production init,
terminal modes, signal/job control or recovery after supervisor failure is claimed.
BG-028/BG-040 and broader native questions remain open. Shared pins are unchanged.

Current integration checkpoint: [BG-055 refresh](evidence/native-refresh-2026-09-05/README.md) rebuilds both SDK variants and passes all five supervision plus four I/O cases against one frozen source snapshot. It supersedes the earlier current-source compatibility gap for those exact inputs. Native memory remains disabled; broader ABI, recovery and production claims remain open.

## Explicit-stop closure extension

[Decision 0008](decisions/0008-native-io-stop.md) adds sys-init-owned `io_stop.rs` and builder variants `io-stop` / `io-stop-wrong-detail`. With the unchanged BG-055 kernel and I/O SDK, four target cases pass: stop closure, wrong detail, skipped zeroing, and original-I/O compatibility. Both stopped empty streams reach EOF, input/seal reject, stale operations reject after reclaim, and the next generation completes normal I/O. [Evidence and commands](evidence/native-io-stop-2026-09-05/README.md) retain exact outcomes. Nonempty output at stop, actual worker-fault closure and recovery remain untested by this extension.

## Retained output across stop and fault

[Decision 0009](decisions/0009-native-retained-output.md) adds a sys-init-owned C
worker and `io-retained-stop` / `io-retained-fault` / `io-retained-wrong-kind`
supervisor variants. The worker uses the unchanged verified musl I/O SDK. Four
new target cases pass, including real UD2 and semantic rejection controls;
the original four-case stop suite still passes. Exact nonempty stdout/stderr
survive terminal closure through EOF, stale handles reject after reclaim, and
replacement output carries the new generation. [Evidence and reproduction](evidence/native-io-retained-2026-09-05/README.md)
retain source, link inputs, ELF inspection and serial logs. This extends the
previous empty-stream result; readiness-before-terminal ordering and recovery
remain open.

## Readiness and terminal ordering

[Decision 0010](decisions/0010-native-readiness-ordering.md) adds an opt-in worker
profile and seven native cases. Exit, UD2 and explicit stop before notification
retain false readiness; notify-then-exit and notify-then-UD2 retain true history.
The client polls terminal state without requiring an observed live-ready state,
checks repeated terminal observations and starts an initially unready replacement.
Invented readiness and omitted-zeroing controls reject. [Evidence and commands](evidence/native-readiness-2026-09-05/README.md)
retain eleven new/compatibility target outcomes, source/link inputs and full checks.
This is controlled ordering coverage; external/delegated authority, general
readiness deadlines and recovery remain open.

## Worker-local readiness authority

[Decision 0011](decisions/0011-native-readiness-authority.md) tests supervisor
rejection from worker-local notification/generation operations throughout the
lifecycle, and worker rejection from eight supervisor control operations. Two
fresh generations retain only their own readiness; duplicate local notifications
with ignored nonzero arguments preserve history. The positive, wrong-authority
expectation and omitted-zeroing cases pass, as does the earlier readiness suite.
[Evidence and reproduction](evidence/native-authority-2026-09-05/README.md) retain
source/link pins, exact outcomes and compatibility. These guessed-value tests do
not establish delegated authority or exhaustive live-peer noninterference.

## Known live-peer readiness

[Decision 0012](decisions/0012-native-peer-readiness.md) adds a separate peer
worker and tests both live-slot orders. Knowing the peer's exact numeric handle
still gives neither control authority nor the ability to notify readiness for it.
Only the caller becomes ready; stopping/reclaiming one worker leaves the other
live-ready and able to exit normally. The incorrect peer-readiness and zeroing
controls reject. [Evidence and commands](evidence/native-peer-2026-09-05/README.md)
retain four new target cases, three authority compatibility cases and full checks.
This is bounded single-core coverage, not exhaustive concurrency or delegation.

The canonical [builder manual](man/sys-init-build-native-io-worker.1) covers current
inputs, options, output lifetime, receipts and build-only limitations. See
[documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.

The canonical [native-runner manual](man/sys-init-test-native-io-stop.1) covers
current inputs, profile selection, workspace and error behavior. Target
acceptance still requires the matching retained producer/consumer evidence.
