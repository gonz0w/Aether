# UL-007 composed session proposal

2026-09-24. Consumer-owned next workload, pending Aether owner review and native
delivery. The existing twelve-script acceptance remains unchanged. This new
[script](session/composed.sh) combines already exercised operations in one dash
parent: external argv, pipeline, substitution, another pipeline, descriptor leak
check and stderr/stdout restoration. It is a finite command session, not an
interactive TTY or full M3 acceptance. Native execution is NOT RUN.

Use the existing pinned helper source without modification. Environment remains
WITNESS=value, LC_ALL=C, PATH=/nonexistent. Only /inputs/helper needs executable
namespace authority. No scratch, general filesystem or package installation is
required. Consume the entire script through actual dash main using one -c input;
do not split it into separately booted scripts or synthesize its output. A later
serial-input delivery must execute the same command sequence and separately bind
input framing, prompts and disconnect behavior.

The manifest pins script, helper and independently specified stdout/stderr bytes.
Status must be zero; both streams must match exactly. This fixture introduces no
public diagnostic format or changes to existing boot markers. The shell-level
$$ check is a consistency check only: authenticated owner observations must prove
one unchanged parent identity/generation across all stages.

## Acceptance and owner handoff

| ID | Required observation | Current status |
| --- | --- | --- |
| SESSION-01 | Exact positive streams/status; real helper argv/environment; one parent through every stage | NOT RUN |
| SESSION-02 | Both three-stage pipelines transfer ten bytes through two real helpers, EOF and all child statuses collected before resource reuse | NOT RUN |
| SESSION-03 | Real substitution captures eight helper bytes, removes newline, restores parent descriptors and retains x across the following pipeline | NOT RUN |
| SESSION-04 | Final exec sees fd3–63 closed; stderr contains only its declared line and stdout resumes correctly | NOT RUN |
| SESSION-05 | Denied/malformed controls below reject at their specific boundary; no success from timeout, crash or skipped work | NOT RUN |
| SESSION-06 | Repeat the complete session in three owner generations with no stale handles, endpoints, children or grants; exact cleanup accounting | NOT RUN |

Before running, the producer must supply a sealed final source/support set including
the current tests/test_build_policy.py, tool/SDK inventories, exact flags and target
ABI, launch/namespace authority, quotas, stacks and a linked stack audit. Specify
phase identities, wait results, image admissions, copied children and terminal/
reclaim expectations separately. Do not infer counts from the earlier fixture's
12 admissions or 15 reclaims. Those belong to a different lifecycle. Pipeline
status here observes the last command; owner oracles must also require successful
upstream stages and real EOF. A success string cannot replace those observations.

Required semantic controls: wrong WITNESS (first helper91, shell31); changed first
pipeline output (exact-stream rejection even if children exit0); corrupted
substitution bytes (shell33); leaked unflagged fd3 into the final helper (helper95,
shell35); stale wait identity and retained writer alias (exact owner rejection or
bounded failure, never a passing positive). Native owner error numbers, side
effects and cleanup predicates must be agreed and frozen before execution.
Record each mutation separately; never modify the positive script to accommodate
missing support. General PID/signal/TTY semantics are outside this case.

Consumer replay uses the existing owned runner, unchanged guest watchdogs and
sequential suites: at most3600 seconds per native suite,1800-second review ceiling,
512 MiB per output stream. Measure elapsed monotonic time. Require complete process
cleanup, matching source/tool/SDK hashes, raw streams, exact case discovery and
fresh matching producer regressions. Preserve all attempts, then verify archives
before removing only completed generated suites/caches.

## Next increments and limits

First deliver SESSION-01–06 without changing native resource bounds implicitly.
Then compose early-reader EPIPE/pipefail recovery followed by another command,
failed exec recovery, scratch redirection and real serial input. Each needs an
explicit new workload and owner oracles. Existing twelve-script results remain
useful component evidence, not proof of this composition. UL-007/M3, UL-081 SDK
boundary, independent reviews, UL-008/009 TTY and packaged sys-init assembly stay
open. No sibling implementation or shared standard is changed by this proposal.
