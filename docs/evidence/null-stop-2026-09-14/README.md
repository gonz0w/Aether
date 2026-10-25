# Native null fault cleanup

Prospective review, 2026-09-14. Require owner-local null and inherited-holder
cleanup after an authenticated child #UD terminal record, without libc exit
finalization. Select the existing private foreground shell/null profile: after
real denied exec returns and null EOF is checked, the child deliberately faults
before replacement. The parent must observe SIGILL (shell status132), preserve
its original input and output, finish normally, and repeat with a fresh generation.

Forbidden: release before terminal observation, retain the stopped child's null
object or stream aliases, close the parent's streams, treat a fault as normal
exit, or reclaim with incomplete frames/cleanup. Keep the current exact-frame
restriction; queued/partial in-flight interruption is outside this slice. Negative
controls skip null cleanup and inherited-holder cleanup with distinct owner errors.

Aether owns this private runtime fixture. Userland's unchanged background wait,
independent acceptance and installed SDK remain separate. No sibling, kernel ABI,
released pin, service policy, new dependency or allocation is changed. The native
terminal capability authenticates the child; no caller-supplied terminal message
is introduced. The local null release method confers no lifecycle authority; its
caller must have confirmed stop and must never serve that connection again.

SE-01–05: reuse the existing terminal observation, wait-status conversion and
owner-local holder table rather than introduce another lifecycle service. Normal
client close is insufficient because a fault skips it. A single private release
operation removes dependence on client finalization; no general cleanup framework
or obsolete path removal is needed. State remains bounded and single-owner.
The new C UD2 injection has no memory operands; it terminates only the current
native user context. Rust adds no unsafe boundary. Preserve existing formatter
style (Rust2024; C clang-format21.1.8 reviewed style) without broad reformatting.

Selected checks: null core tests plus x86_64 no_std compilation, all11 focused
null profiles, complete301 connections regression, host tests and offline pins.
Require exact fault/parent/backend records, two generations and six reclaims for
the new positive, distinct zero-reclaim negative outcomes, unchanged prior images
where possible, frozen sources and retained failed attempts. Update the native
reference, workflow, STATE/ROADMAP and companion summary with measured results.

First attempt: the ordinary null positive passed; the new fault profile reached
actual child #UD then owner2310 with zero reclaims. The reused normal-exit oracle
required empty stderr, while real dash reports the signal. The corrected profile
requires exactly `Illegal instruction\n` (20 bytes) from the backend, preserving
its existing stdout check. This is a fixture output-oracle gap, not a timeout or
cleanup pass. All later cases were not run in that attempt. Its sources and logs
are retained. Also require actual request-channel EOF after terminal observation
before releasing the null object; observed empty framing alone is insufficient.

Second attempt: the guest completed both #UD/parent0/backend17 generations and
six reclaims, with exact stdout/stderr checks. The harness still selected a generic
normal-exit lifecycle list for the new profile and rejected it. Add the new exact
profile to the existing #UD lifecycle oracle (kind2/detail134, parent0/backend17),
not a relaxed success-marker check. Later controls were not run. Retain this
harness integration failure and its source set as well.

## Qualification

PASS: all301 connections cases in 934.16s, all11 focused null
profiles, 101 host Python tests plus Zig/pins, three null core tests and x86_64
no_std compilation. C21.1.8/Rust2024 format checks pass. The final264 source bytes
match the target's 249 inputs; source inventories and every
attempt's artifacts are retained and verified. Both failed attempts are fixture
oracle integration errors described above; no timeout was accepted as a result.

The positive requires actual kind2/detail134 child terminal, parent0/backend17,
both generations and six reclaims. Skipping null release rejects2322; skipping
holder release rejects2323, after the real child fault and with zero reclaims.
The owner checks request-channel EOF, stale null operations and exact parent
stream contents, including the real20-byte dash fault diagnostic. Normal close,
denied-exec retry, stale-instance and quota controls remain passing.

572 of 572 prior ELF/raw artifacts are byte-identical.
Changed names are listed in compatibility.json. New null owner sizes are
[11512, 12352, 12272, 12336, 11544, 11608, 11560, 11512, 11736, 11496, 11512]; maximum inherited owner is 15408 bytes,
within16384. No kernel, SDK, protocol layout, quota, dependency or released pin
changed. No peak-memory/performance or independent-reader claim is made.

This is a private foreground producer fixture. It does not qualify partial/queued
in-flight interruption, post-exec null fault cleanup, arbitrary supervision stop,
general libc reopening, consumer failed-exec acceptance or background wait.
Next is lifecycle-owned SIGCHLD with atomic mask/suspend. No sibling was modified.
