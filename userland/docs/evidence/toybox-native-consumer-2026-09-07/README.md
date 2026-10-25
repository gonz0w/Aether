# UL-067 native Toybox normal-copy checkpoint

The local consumer rebuild now runs actual Toybox 0.8.14 cat_main on Aether.
Binary32, empty and forced-short input copy exactly; each positive case verifies
client0/backend17 in two generations and supervisor100/reclaimed4. The captured
owner independently checks input preservation, exact output and positions, three
alias closes, backend closure and stale-handle rejection. This is a bounded
stdin-only native utility, not a shell or general installed cat command.

| Case | Expected and observed |
| --- | --- |
| copy / empty / short | Exact owner-verified bytes; four native reclaims each |
| skip-copy | Client0 followed by supervisor1505 rejection |
| skip-callback / skip-flush | Client120 followed by supervisor1501 rejection |
| skip-close | Client0 followed by supervisor1503 rejection |

All seven cases pass their distinct oracles. Negative cases intentionally reject
with zero reclaims; no recovery claim is made for those controls. See
[final results](final/results.json) and each case's raw serial/QEMU logs.

## Inputs and execution

[Intake](intake.json) captures the latest usage delivery's 155 runtime source files
from archive1783abb5d57978c9e2f28fd319ea9cb60d06fde5ac82425e1e011068d1d01355.
Retained runner source scaffolding supplies the remaining boot/build files; the
complete resulting private inventory is recorded. No live sibling source is used
during compilation. All231 SDK files and15 original baseline inputs match their
producer receipt. The earlier normal-copy recipe is retained and adapted locally
to use this captured source, owned processes and private paths.

All baseline Toybox translation units and the native adapter are rebuilt from
retained source. Archived objects are checked as inputs but replaced before the
link. Each case recompiles the probe, real musl __stdio_write callback and Toybox
xwrap variant. SDK libc/CRT remain the pinned dependency; owner/backend images
are reused from hash-checked cat-abnormal envelopes. **The owner/backend are not
source-rebuilt by this run.** A fresh producer rebuild/regression remains a gate.

[Execution identity](execution.json) binds the original and adapted recipe,
driver, process helper, host tools and environment. Commands retain argv, output,
180-second deadlines and complete process-group cleanup. The pinned smoke helper
retains its30-second guest watchdog and terminate/wait cleanup. Build directories
retain payloads, ISOs and objects; receipts retain their identities. Existing
SDK, shared standards and UL-059 pins are unchanged. No installation or network
fetch is performed. Reproduce from the repository root:

```
python3 -B experiments/toybox-native/run.py --snapshot build/toybox-consumer-x__smsdx
```

[Attempt1](attempt-1/results.json) failed before compilation/boot: sequential
path substitution accidentally rewrote the Aether prefix inside Aether-userland.
Its driver, generated recipe and raw diagnostics are retained. Corrected ordered
substitution produced the successful rerun; native source and oracles unchanged.

## Review and remaining acceptance

Scope is the [normal-copy plan](PLAN.md), under Foundations O/I/E and quality
C/CP/TD/TE. Codex reviewed complete AECAT001 validation before binding publication,
rights/generation/liveness checks and shared transport poison; process-local mask
does not grant authority. The probe retains upstream toy_singleinit, real TLS,
locale and allocator/buffer checks. cat_main/loopfiles/xwrite are unmodified.
Toybox's xexit owns and frees callback nodes before real fflush/ferror; the private
normal _xexit argument patch then consumes aliases. Rebound/vfork code is retained
but untested. Callback functions stay live; no concurrent mutation is supported.

The private musl callback substitutes only the writev transport call. Caller-owned
buffer lifetimes and the two-vector/16-byte bridge bound remain explicit. Original
code keeps BSD-2-Clause; copied upstream Toybox/musl retain their notices. Existing
ASCII diagnostics and machine markers are preserved. This is an imported probe
adoption and local execution review, not an independently authored second adapter.

CAT-02 normal-copy evidence is now local. CAT-01/04/06/07 have partial witnesses;
CAT-03 usage and CAT-05 errors have producer evidence but are not locally rerun.
CAT-06 still requires failed/unknown close, final diagnostic and re-entry treatment;
the current normal-exit hook does not implement the proposed final close-error
diagnostic. CAT-08 needs the selected producer rebuild and broader regressions.
Independent reader/maintainer review is pending. UL-067 and M3 remain active.

Next: qualify the delivered error/usage profiles locally and resolve the exact
finalization gaps required by CAT-06, then integrate native dash external-command
and pipeline/wait/cleanup. Optional tuning remains deferred. Source, SDK, tool,
plan or owner changes invalidate affected evidence reuse.
