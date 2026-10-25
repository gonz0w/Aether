# UL-007 scratch workload consumer intake

Current checkpoint,2026-09-23: [local scratch qualification](../../docs/evidence/dash-scratch-consumer-2026-09-23/README.md)
passes11 focused and355 full connections cases with22 exact trace checks. All three
scripts below now have local native evidence. Matching command-runner remains open.
The earlier intake and requirements below are preserved as dated context.

As of 2026-09-15, Aether delivers fork-adapter, owner-grant and replacement-helper
boundaries. [Verified intake](../../docs/evidence/dash-scratch-intake-2026-09-15/README.md)
checks their 41 sealed members and all twelve local workload pins. No native
profile selects the new helper yet. These scoped archives are not a full replay
kit; host tests and object compilation do not qualify an unchanged dash script.

## Exact next oracles

| Unchanged script | Required observations |
| --- | --- |
| fd-leak-control | Real writable `/scratch/leak` opened as FD9, inherited through actual fork/exec; unchanged helper `closed` returns95, dash collects it and exits22; stdout empty |
| redirection | FD4 duplicates FD3's open description; writes A then B use one offset; both aliases close; a real helper `copy` reads reopened file through stdin to EOF; stdout exactly `AB`, helper and dash exit0 |
| denied-redirection | Actual subshell write to `/inputs/denied` fails with no unauthorized mutation; dash observes nonzero subshell status, stdout exactly `denied ok\n`, parent exit0 |

A helper95 result alone is insufficient: its scan accepts any unexpected FD3–63
or erroneous F_GETFD response as a leak. The owner must independently prove live
FD9 and valid scratch binding, and rule out an unrelated descriptor/error as the
cause. Observe child status, collected parent status, file-holder release and
all admitted-domain/channel cleanup. Define exact native terminal/reclaim markers
from the final owner fixture before running; do not invent counts from older VMs.

The redirection script tests shared offsets and reopen/readback, not append mode.
Append and general descriptor restoration need separate evidence; they must not
silently expand this script's claim. The denied case similarly needs independent
proof of write denial: a generic child crash can satisfy its shell-level nonzero
check and is not sufficient acceptance.

## Handoff and controls

Require a sealed final source/support kit, SDK/tool pins, actual launch selection,
exact positive and negative transcripts, complete full connections and matching
command-runner receipts. Current helper receive order is stream/table/saved mask,
AESFD001 grant, then two sixteen-byte description records. Keep this private
producer contract owner-defined; do not promote it to a supported SDK interface.

Proposed controls, subject to exact owner fixture agreement: remove FD9 or force
CLOEXEC (helper0/parent0 must fail the leak oracle); corrupt collected child status;
lose a shared offset; close a description prematurely; permit the denied write;
and retain a child/file holder after exit. Each must reject for the named semantic
reason, with exact statuses and cleanup outcomes retained, rather than timeout.

Reuse the owned consumer runner and retention procedure from failed-exec. Pin
final inputs before execution; run focused cases then sequential matched suites,
3600-second outer limits and 1800-second review ceilings, preserving guest
watchdogs and every failed attempt. Retain complete serial receipts before oracle
analysis. Archive/readback-verify completed outputs before deleting unpacked suites
and caches. No sibling edits, real-prefix installation or quota changes are implied.

At the original intake, acceptance stayed six of twelve. Persistence, pipelines, general signals,
TTY, public SDK/reviews and full M3/assembly remain separate open gates.
