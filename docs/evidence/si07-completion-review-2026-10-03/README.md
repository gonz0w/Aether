# SI-07 bounded kernel-contract completion review — 2026-10-03

Before-work scope: assess the original SI-07 backlog acceptance against sealed
producer and actual sys-init consuming evidence. Verify every referenced local
packet member and current enforcing source bindings before changing backlog state.
No new runtime, ABI, grant, quota, dependency, unsafe boundary or sibling change.
No new native run or consumer approval is inferred. Preserve released pins and
all failed attempts. Run retained trace checks, host/pin/workflow checks and links.

Simplicity/security: use the existing backlog's explicit acceptance boundary;
do not add a shell, filesystem, recovery service or exhaustive wire matrix to a
kernel-mechanism dependency that explicitly excludes those product steps. The
simpler alternative of leaving every milestone open until R1 obscures dependency
ownership. Closing this scoped gate removes that ambiguity, not a safety check.
Authority bypass, unsafe reuse, unknown cleanup and generic failure never qualify
successful halt. Foundations O-01–05/I-01/03–06/E-01–08 and SE-01–05 apply.

## Disposition

**Complete for the original bounded SI-07 kernel backlog contract:** sustained
AENSI001/ABI22 lifetime, reuse, scoped input/final action and matching sys-init-owned
consuming witness. This is a kernel backlog disposition, not acceptance on behalf
of another owner. It does not close the broader SUSTAIN-01–06 protocol matrix,
production sys-init, shared SDK or bootable serial-shell/R1 assembly. Earlier status
entries conflated these boundaries; this dated review supersedes that current
kernel-backlog interpretation while retaining their historical evidence.

| Original SI-07 requirement | Executable evidence | Scope/remaining limit |
| --- | --- | --- |
| Healthy guest lifetime separate from harness timeout, actual idle/wakeup beyond3000 | [Matched producer](../si07-native-2026-10-03/README.md): five useful cycles,3044 total/3004 idle; [sys-init intake](../si07-handoff-review-2026-10-03/README.md): actual owner five cycles and quiescent six-cycle loop | External watchdog remains; finite observations are not indefinite uptime |
| Readiness before/during registration, retained event and no fabricated work | [Mechanism controls](../sustained-controls-2026-09-29/README.md): native serial level checks, publication-before-park and terminal wake; [composed waits](../si07-wait-composition-2026-10-03/README.md): delayed wake, repeated unconsumed readiness, deadline/future-sequence rejection and retained lifecycle recheck with useful command | Bounded schedules; lifecycle source includes channel/terminal/cleanup. Exhaustive races/cancellation are not native-composition claims |
| More than three clean useful cycles, bounded live quotas, stale authority, finite exhaustion | Producer five cycles/15reclaims; sys-init six cycles/18reclaims; native seeded255/256/65534/65535 and65536pre-admission rejection; stale task/channel/private-reference denials | No65535-cycle endurance claim. Private epoch ends65535; native identity limit remains separate |
| Authorized shutdown after settlement; denied/foreign/unsupported/busy actions ineffective | Mechanism worker supplies owner grant numbers but is denied; matched owner checks denied grants/unsupported action/busy halt; sys-init loop halts before work or after complete cycles, buffers halt intent and denies omitted-console-close halt | Selected action is halt only. Developer serial grant is not public login authentication; shutdown is quiescent, not arbitrary effect cancellation |
| Frozen producer, semantic controls, matching legacy behavior and actual sys-init consumer | Producer packet/legacy five-case runs; intake verifies six companion snapshots, normal sys-init raw/ELF rebuild and matching35kernel members; independent userland nine producer/seven sys-init loop replays | Newly added child-profile/request-denial/wait controls are producer evidence; no independent replay of those additions is claimed |

Sys-init's captured disposition accepts SUSTAIN-05 only for its private useful-cycle
core, and leaves full protocol/product work partial. Userland likewise distinguishes
its bounded ABI22 assessment from ABI23 dash. Those owner dispositions are preserved
under inputs/ and remain authoritative for their projects. No sibling backlog is
closed here. Kernel minimum acceptance does not require OpenZFS or full dash.

## Work that remains outside this closure

Keep the following in the existing R1/interface work, rather than claiming it done:

- Full SUSTAIN-01–06 native bootstrap/admission/result-path malformed matrices;
  consumed receipts, actually foreign native endpoint schedules, truncated framing,
  wider interruption/wait schedules and final-epoch consumer composition. The latest
  request controls inject complete received frames; they do not establish endpoint
  spoofing protection through that technique.
- Cancellation/retention in the pure event core is host evidence. ABI22 exposes
  snapshot/park/halt and no public cancel operation; an event wake requires rescan.
  Quiescent shutdown and fail-closed Unknown/no replay do not imply production recovery.
- Independent technical/reader and SDK disposition, explicit sys-init/serial-shell
  profile composition (ABI22 and ABI23 payloads are not interchangeable), persistent
  filesystem, package management and assembled release acceptance.

Next is matching sys-init-to-serial-shell contract reconciliation and the smallest
assembled useful-session experiment. Do not hold that design work on a fictitious
missing sustained kernel API, or silently waive a concrete authority/lifetime defect.

## Verification

From repository root:

```sh
python3 docs/evidence/si07-completion-review-2026-10-03/verify.py
python3 docs/evidence/si07-completion-review-2026-10-03/test_verify.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The verifier reads only captured dispositions, immutable local packet manifests
and current kernel/user source bindings. It never follows a sibling during checks.
Native executions retain their original dates/tools/artifacts/failures; this review
adds no QEMU runs. checks.json, inputs.json and SHA256SUMS bind the review.

Verified result: six sealed packets pass complete member/inventory comparison;
276 current kernel/user/build source members match their native-tested bindings.
Thirty retained companion/child/request/wait traces pass with141 deliberate
corruptions rejected. Oracle outputs are redirected only to this review, and all
six manifests are rechecked afterwards; no immutable evidence is rewritten.
Local host/pin/process checks are recorded in checks.json. No new native run,
independent build, human sign-off or blanket protocol conformance is claimed.

Initial verifier-test attempt rejected a valid disposable packet because the
macOS temporary path has an OS-owned ancestor symlink. The corrected verifier
rejects symlinks within the packet and at its root, without treating host ancestors
as packet members. Initial code/test log and classification remain retained. No
runtime/evidence bytes changed; final controls qualify the corrected checker.
