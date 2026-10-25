# UL-007 actual dash workload handoff

These twelve candidate native scripts reuse the existing Linux-reference tests.
The sole transformation removes `/usr/bin/qemu-x86_64` before `/inputs/helper`.
[Manifest](workloads.json) pins each original/transformed script, existing expected
stdout, exact exit and current helper source. All twelve unchanged scripts now have bounded local native evidence; see the
[current acceptance matrix](ACCEPTANCE.md) for exact scope and remaining gates.
The manifest is preserved as a historical producer input; its original NOT RUN
fields are not the current acceptance record.
No shell behavior or expected error is relaxed to fit current producer support.

Next integration: [composed-session proposal](SESSION.md), a separate pinned
workload for pipeline/substitution/resource reuse in one parent. Its native cases
are NOT RUN and do not change this twelve-script matrix.

## Admission and fixture contract requiring owner agreement

Before execution, select matching dash source/config/generated files, SDK/adapter,
helper ELF, kernel, startup envelope and explicit resource limits. Record hashes,
compiler flags, target ABI, runtime, timeout and independent terminal/reclaim oracle.
The helpers must execute as native child images with argv/environment, not through
an emulator. Give the shell WITNESS=value, LC_ALL=C and PATH=/nonexistent.

The logical `/inputs` fixture needs executable helper, a missing `missing` entry,
a present but non-executable `not-executable` entry and denied write to `denied`.
`/scratch` needs a fresh empty writable namespace per test. Names alone confer no
native authority. The owner must explicitly provide/review these mappings before
claiming the existing cases run natively; path strings do not authorize installation.
Do not mount/write real system prefixes or mutate an unrelated service namespace.

## Ordered acceptance

1. Run actual dash initialization with checked custom handler/mask semantics.
   Then argv, signal-table and syntax-error cases. The earlier startup probe is
   prerequisite evidence only; dash trap setters can hide unsupported operations.
2. Run wait, failed-exec, fd-closure and deliberate fd-leak-control. Require exact
   exit22 for the leaked-descriptor control, status7 collected by the wait script,
   and127/126 for missing/non-executable images as checked by the script. Parent
   status must survive child failures and all owned children must be reclaimed.
3. Run redirection, denied-redirection, pipeline, substitution and early-reader.
   Preserve shared offsets/FD restoration, last-endpoint EOF and checked EPIPE.
   The early-reader helper attempts up to16 MiB through a pipe until EPIPE; this is
   a bounded progress test, not a requirement to allocate a16 MiB pipe. Its4096-byte
   local buffer plus native stack usage needs an explicitly reviewed stack budget.

Use exact stdout and exit from workloads.json; do not demand Linux-specific stderr
wording. Capture stderr for diagnosis and agree native diagnostics before publication.
A matching success text alone cannot establish child status, signal delivery, denied
authority or cleanup. The owner-observed status/reclaim context must accompany it.
Syntax-error exit2 and fd-leak exit22 are expected negatives, not infrastructure
failures. A crash, timeout, unsupported operation or uncertain cleanup never passes.

This is the first existing-workload subset, not complete M3 acceptance. ENOEXEC
fallback, large here-documents, interruption/wait races, nested state and broader
failure cleanup still need exact owner-reviewed cases. Track these within UL-007;
TTY/jobs/Zsh remain UL-008/009. Source/license trust remains UL-016. Do not expand
optional utility/benchmark work while these dependencies are unresolved.

## Native syntax and helper checkpoint — 2026-09-10

[Independent qualification](../../docs/evidence/dash-helper-consumer-2026-09-10/README.md)
reproduces the exact syntax-error script bytes via actual dash `-c`, with empty
stdout, native syntax diagnostic, status 2 and four reclaims. Skip/close mutations
are detected. The original twelve-workload manifest and expected outputs remain
unchanged. This is a bounded syntax workload, not the full fixture contract.

The unchanged helper also executes through an explicit owner image launcher with
correct spaced argument, literal star, WITNESS, eight-byte output and child/parent
status 0, plus corruption/skip/close controls. This is a helper boundary witness;
DASH-argv still needs the actual shell fork/exec/wait path. All other eleven shell
workloads, general namespace/resource mappings and full M3 remain open.


## Serial process path checkpoint — 2026-09-11

[Local 303-case qualification](../../docs/evidence/dash-serial-consumer-2026-09-11/README.md)
now executes actual dash fork/exec/wait3/wait4 via a configured jobs object and
private libc staging. Serial input uses the native one-byte fallback; /next exits72,
dash returns to its prompt and prints the status before normal cleanup. This uses
a fixed delegated replacement image and one external child per shell. It does not
execute the original twelve-script matrix or its helper/namespace requirements;
only the previously qualified syntax-error row is accepted from that matrix.
Repeated children, arbitrary command paths, pipelines, redirection and failure
workloads still need exact producer/consumer execution. Preserve manifest bytes.


## Repeated commands and descriptor redirection — 2026-09-11

[Independent qualification](../../docs/evidence/dash-redirect-consumer-2026-09-11/README.md)
now runs three /next children sequentially in one dash process, with builtin >&2,
stdout restoration and final cleanup. This does not execute the original filesystem
redirection script or pipeline/substitution scripts. Their expected outputs and
manifest remain unchanged. [Next pipe intake](../../docs/evidence/dash-redirect-consumer-2026-09-11/pipe-next.md)
requires native endpoint EOF before wait, backpressure, failure/alias/signal controls
and the unchanged helper for DASH-substitution. Producer host pipe tests alone do
not supply that acceptance; concurrent pipelines need a participant-budget review.


## 2026-09-13 — UL-007 unchanged argv/signal native consumer checkpoint

DASH-argv and DASH-signal-table now pass locally through the private native
producer adapter. Seven focused cases and seven independent serial checks pass;
consumer scripts/helper/manifest match byte for byte. Positives require two
child0/parent0/backend17 lifetimes and six reclaims. Argument/environment, skipped
helper, dropped post and bypassed PID scope reject exactly as selected.
Evidence: docs/evidence/dash-argv-signal-consumer-2026-09-13/README.md.
Native run passed first attempt; a retained filename error affected retention
only and was corrected without rerun. Full local 287-case regression is NOT RUN.
Next: remaining changed pipe/exec controls and consolidated producer handoff.
Original substitution/pipeline/file/TTY/assembly gates and independent review stay
open; UL-007/M3 and public SDK/release acceptance are not complete.


## 2026-09-14 — UL-007 background wait consumer checkpoint

Unchanged DASH-wait passes locally: helper7/parent0/backend17 twice, exact owner
readback and six reclaims. All 13 focused native cases and 13 separate transcript
comparisons pass, including before/after parking, stop, ignore/block, duplicate
notification and stale-parent replacement controls. Consumer script/helper/manifest
match local bytes. Source/SDK integrity and owned cleanup pass on the first run.
Evidence: docs/evidence/dash-wait-consumer-2026-09-14/README.md.
This is bounded private-adapter acceptance; no full314, matched command-runner or
scheduler replay was performed here. Next matched phase-one replay and descriptor
closure qualification, then remaining workloads and changed-path regression.
General signals, eventual unblock, writable files/TTY/persistence/assembly and
independent reviews remain open. UL-007/M3 is not complete.


## 2026-09-14 — UL-007 descriptor closure consumer checkpoint

Unchanged DASH-fd-closure passes locally: descriptors3–63 closed after real exec,
owner readback, child0/parent0/backend17 twice and six reclaims. All three native
cases and transcript comparisons pass; injected FD3 and corrupt wait status reject
exactly. Consumer byte identity, source/SDK integrity and owned cleanup pass on the
first attempt. Evidence: docs/evidence/dash-closure-consumer-2026-09-14/README.md.
Corrected phase-one dependencies and256 source/346 support members verify read-only;
this is intake, not execution. Next matched431 command-runner/287 connections replay
with the corrected source set. Full290 closure regression, writable fd-leak-control,
other unchanged workloads, public SDK/reviews and M3/assembly remain open.


## 2026-09-14 — UL-007 matched phase-one consumer qualification

Corrected matched phase-one replay passes locally:431 command-runner plus287
connections,718 native cases on identical242 harness source hashes. All208 startup
cases indexed; ten exact syntax/argv/signal trace checks pass. Host checks including
100 Python tests pass. All602 restored source/support files and4311 SDK files stay
unchanged; all started commands have complete cleanup. Both native suites passed
first attempt. A retained collector PASS-marker mismatch was corrected separately
without native rerun. Evidence: docs/evidence/dash-phase-one-consumer-2026-09-14/README.md.
This closes the fresh matched private phase-one runtime replay gap. It does not
close independent reviews or UL-081 public SDK boundary acceptance. Next integrate
newer wait/closure sets with matching broader regression and remaining unchanged
workloads. General signal/TTY, writable files, persistence/assembly and full
UL-007/M3 remain open. No new release or installed SDK claim.


## 2026-09-14 — UL-007 matched recovery consumer qualification

Matched316 connections and431 command-runner cases pass locally, sequentially,
on identical250 harness source hashes. All208 startup and25 selected transcript
checks pass; host includes101 Python tests. All611 source/support and4311 SDK
files remain unchanged. Timings1072.68/1463.65seconds are within1800 review ceiling;
owned cleanup complete. Evidence: docs/evidence/dash-recovery-consumer-2026-09-14/README.md.
This closes newer recovery full-set replay; previous timeout remains historical.
Full artifacts are compacted with verified readback and relocation mappings to
preserve the user's cleanup preference. No sibling/SDK installation change.
Five unchanged scripts remain qualified; failed-exec is an owner contract awaiting
implementation (two fresh VMs, two sequential children/four reclaims each proposed
by Aether; actual native admissions still require measurement). Next consume that
native delivery and controls. General signals/TTY, writable filesystem, persistence,
SDK/reviews and full UL-007/M3/assembly remain open.
