# Ownership consolidation and native integration review

Reviewed 2026-09-05. This consolidates BG-028/BG-032/BG-033/BG-040/BG-054 evidence;
it does not select a production language, process topology or new kernel ABI.
Shared rules remain in Aether-standards; exact lifecycle policy stays here.

## What the evidence supports

| Concern | Host evidence | Native evidence and remaining distinction |
| --- | --- | --- |
| Ownership identity | Tracked direct children, generation identity, exclusive wait; observed wait loss becomes unknown/incomplete | Holder-scoped instance handles with retained terminal observation; host PID/wait APIs are not the native interface |
| Readiness | Six-byte first frame on a generation-specific pipe; explicitly delegated helper writer can signal | Caller-local notification retained historically in instance status; terminal-plus-ready does not mean currently ready |
| Terminal accounting | Eight accumulated children, exact exit versus signal outcomes across bounded cuts | Supervision fixture distinguishes normal exit, actual fault and explicit stop; detail and kind must both be interpreted |
| Cleanup | Wait plus descriptor closure; no successful replacement with unresolved ownership | Terminal-only reclaim detaches mappings, flushes translations, zero-checks backing and invalidates handles |
| Lost owner | Exception/finally cleanup tested; SIGKILL can leave child alive; stolen wait cannot mean success | Supervisor failure terminates the experiment with a panic; recovery authority and surviving-instance ownership are not implemented |
| Stop | Trusted host cooperative signal, force, terminal observation and cleanup are separate | Native 0x20007 directly stops the worker; detail 143/kind 3 is an ABI outcome, not evidence of POSIX SIGTERM delivery or a graceful handler |
| I/O | Readiness pipe only; no general service stdin/stdout transport in this host adapter | AENFD001 supports bounded producer input, separate retained outputs, backpressure, EOF and fresh generations; userland owns descriptor bookkeeping |
| Timing/resources | Repeated instrumented host baselines with explicit tracing and process inventory | Yield loops/PIT experiment watchdogs are not an accepted per-service clock API; host milliseconds cannot set native budgets |

Host claims are supported by decisions [0003](decisions/0003-host-readiness-fixture.md),
[0004](decisions/0004-host-request-clock.md), [0005](decisions/0005-host-emergency-close.md),
[0006](decisions/0006-host-parent-death-witness.md), [0007](decisions/0007-host-exclusive-wait.md),
[accounting evidence](evidence/host-accounting-2026-09-05/README.md) and
[measurements](HOST-MEASUREMENTS.md). Current functional coverage is 38 host cases,
34 model cases/three mutation controls and 13 harness cases. Host coverage remains
macOS-only; total RSS and child-memory measurements remain absent.

The accepted bounded native profiles are documented in
[sys-init supervision](NATIVE-SUPERVISION.md), [sys-init I/O](NATIVE-IO.md),
[kernel supervision](../../docs/NATIVE-SUPERVISION.md),
[kernel streams](../../docs/NATIVE-IO.md) and
[userland descriptors](../../userland/docs/NATIVE-DESCRIPTORS.md).
Two slots and bounded generations are fixture capabilities, not general service
configuration. Fork/exec/wait compatibility, arbitrary inherited descriptors,
terminal/job control, persistent enablement and SMP supervision remain open.

## Source and evidence review

The [audit](evidence/ownership-review-2026-09-05/audit.json) checks all five retained
supervision and four retained I/O serial outcomes against explicit markers and
recorded exit codes. Negative cases must contain the expected panic and no success
marker. This review did not rebuild images, verify retained ISO bytes or run QEMU.

Selected source comparison excludes VCS metadata and compares recorded code/build
inputs with current owner checkouts. Absolute paths from disposable runs are
mapped to the corresponding current repository, not mistaken for current sources.
Supervision has nine changed inputs among 51 compared; I/O has six among 57.
The I/O sys-init client/builder and userland adapter/probe/runner still match their
tested hashes. Kernel native_c.zig and build paths have changed; inspection shows
native-memory work as well as later build changes. Historical results remain valid
for their snapshots, not proof of current-tree compatibility. These counts describe
the recorded review instant, not every current file or later edits.

The [central catalog](../../../Aether-standards/docs/CATALOG.md) now routes an
unreleased native-memory proposal and Distribution v0.2.0 draft. They are awareness
inputs, not adopted consumer pins or permission to assume new native contracts.
The three existing offline release pins stay unchanged.

The [package transport](../../pkg-mgr/docs/SUPERVISED-HANDOFF.md) accepts AENSUP01.
Do not send it AENFD001 as if format compatibility were already established.
Byte transport, descriptor facade, package staging and supervision remain distinct
owner responsibilities; none alone establishes installed service activation.

## Next integration step

BG-055 captures a fresh witness for the existing profiles before extending them:

1. Freeze current Aether, sys-init and Aether-userland inputs in a private snapshot.
   Verify SDK/source/envelope correspondence and pinned build dependencies before
   consuming them. Record the optional native-memory build setting explicitly.
2. Rebuild the supervised and I/O envelopes, then run the existing five-case
   sys-init supervision suite and four-case userland I/O suite against that same
   kernel snapshot. Retain exact semantic controls, hashes and serial logs. A
   compiler failure, emulator failure or timeout cannot substitute for rejection.
3. Verify unchanged source inputs at the end; leave mutable working trees and
   historical receipts untouched. A second host is unnecessary for this native
   snapshot refresh; it remains a separate portability gate.
4. After that baseline passes, specify and implement explicit-stop/fault I/O
   closure cases under BG-032/BG-040: retained output, sealed input, terminal kind,
   reclaim, stale handle denial and a clean next generation. The documented
   stream/stop contract supplies the initial seam; do not invent new syscalls.

This is unblocked integration work using existing bounded interfaces, not a claim
that the host model can now be ported wholesale. Native service deadlines, owner
recovery, concurrent wait enforcement, production authority and broader resource
policy still need accepted contracts. BG-028 remains partial; BG-032/BG-033 retain
those native questions. Prioritizing a snapshot refresh avoids repeating finished
host tests as a substitute for consuming current kernel work.

Current integration checkpoint: [BG-055 refresh](evidence/native-refresh-2026-09-05/README.md) rebuilds both SDK variants and passes all five supervision plus four I/O cases against one frozen source snapshot. It supersedes the earlier current-source compatibility gap for those exact inputs. Native memory remains disabled; broader ABI, recovery and production claims remain open.
