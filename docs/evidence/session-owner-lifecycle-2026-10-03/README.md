# SESSION owner lifecycle — 2026-10-03

Before-code requirement: opt-in `session_lifecycle` Rust owner for AENMX009/ABI24.
Run one persistent shell until observed terminal, drain progress before atomic
compare-park, settle children/pipes/channels/backing, close UART then request
quiescent halt. Remove fixture idle/transfer/three-parent/observation-finish cutoffs
on this selected path only. Old ABI21/23 fixture behavior remains available.

Forbidden outcomes: missed cooperative freeze/ready wake, idle busy polling,
reclaim before confirmed terminal, admitting a replacement after unknown effects,
raising quotas, silently changing old profiles, or calling this owner actual
sys-init. Kernel only adds the missing009 freeze-state event publication. Existing
owner authority, contextual grants, scalar trap serialization and resource limits
remain unchanged. No new unsafe boundary, dependency or sibling change.

Simpler alternative: retaining the bounded fixture or increasing counters cannot
provide a healthy manual prompt. Reuse its dispatch and confirmed cleanup in one
shared pump; add selected snapshot/park helpers and one-parent lifecycle path.
No new service, generic retry/restart framework or policy abstraction is needed.
The private owner remains part of the supervisor TCB; sys-init policy consumption
and matching SDK qualification are distinct later gates.

Tests: fresh Rust raw/ELF and code/stack inspection, native real dash with long
idle at prompt and between commands, external execution/pipelines/persistent shell
state/stderr/exit and ten confirmed reclaims before halt; exact mismatch controls,
old serial SESSION regressions, host/pins/workflow and M4 scheduler tests. Retain
all failures; freeze sources during target runs. Private diagnostics stay ASCII;
existing machine markers and presentation/pins remain unchanged.

First native attempt exposed an affected-path correctness defect: an event could
make parked() false before its pending completion was delivered. A cooperative
yield could then resume the owner, and a later timer would overwrite another
syscall result (observed false stdin EOF/early shell exit). Before the repair,
recorded requirement: consume pending completion in select() before returning any
user frame. refreshSustained has no scheduler recursion and takes a completion
once; ordinary calls must never be overwritten later. This fix also applies to
ABI22 and therefore requires its native regression, plus an intentionally omitted
completion-delivery control failing for the observed early-EOF reason. Retain the
first failed source export/trace; do not qualify it as a healthy shell result.

Correction after investigation: the first pending-completion hypothesis was not
established; rotate() already refreshes lifecycle completion before selecting the
owner. The trial select() refresh did not fix early exit and was removed. Both
failed source exports and diagnostic-only traces remain retained. The traced
stdin request stays nonzero and Pending; no fabricated zero read was observed.
The short-input run completes correctly. Frozen client transport move() instead
has a100000-attempt limit, marks poisoned on exhaustion and returns failure to the
shell. The parked owner allows the client to exhaust that polling budget before
human input arrives. Thus long prompt idle is not qualified. Next design a
capability-scoped native channel wait with a matched userland runtime adaptation;
removing a counter while leaving the client busy-polling is not sufficient.

The009 owner also removes fixed128-byte stdout/32-byte stderr observation buffers
as admission gates: bytes flow through existing bounded chunks/UART authority.
Old fixture output observations keep their caps. A larger-output native case tests
that change. Copies/exec counters retain existing finite resource checks.

## Qualified results and remaining gate

Short-input actual dash:588 ticks, ten terminal/reclaim records, exact prompt/UART
stream, external helpers, pipelines, substitution, persistent variables/PID and
normal exit before authorized halt. A second run adds161 stdout and65 stderr bytes
beyond old observation capacities and completes at891 ticks/ten reclaims. Both
use the same native-tested owner15184 bytes with estimated stack3864/4088. Raw/ELF
bytes and immutable GOT targets/register provenance were inspected. The final
current-source raw rebuild is identical after adding the opt-in wrong-ABI control.
The driver uses a stricter16KiB linker assertion while009 kernel permits24KiB;
these tested images satisfy both. No general all-path or kernel stack proof.

The final mismatched owner ABI control rejects before worker admission with the
labelled failure and supervisor termination. All11 old serial cases rebuild fresh
owners using recorded producer recipes with exact sealed worker payloads and pass.
ABI22 native mechanism, seven M4 targets and full host/pin/workflow checks pass.
The initial old-owner mismatch attempt timed out because its legacy fixture finish
returns -38 under009; it is retained as a failed expectation, not a successful
negative. Partial diagnostic bytes initially confused the mismatch oracle; corrected
oracle waits for its complete named failure. The legacy recipe initially omitted
that stale-wait/reference cases reuse the composed owner; corrected and all rerun.
An initial indirect-call register inventory omitted r13; inspected linked memcpy
provenance before admitting it. Diagnostic traces are not qualified normal images.

The final withheld-input control demonstrates the bounded client limitation: no
input is sent, only the first prompt appears, parent exits0 early, exactly one
terminal/reclaim precedes actual halt. Frozen source move() has100000 attempts and
sets poisoned on exhaustion; linked parent disassembly retains that counter.
Traced owner reads remained nonzero/Pending, and no zero-byte UART completion was
observed. This supports attributing early shell exit to client transport exhaustion;
it is not exhaustive instruction tracing or proof of every client error path.
No healthy long-idle/manual shell acceptance is claimed. Original failed long-idle
source exports, the removed select-refresh trial and short diagnostic attempt
remain available. Remaining runtime/input wait coverage is an explicit gate.

Next is kernel-scoped channel waiting plus matching userland adaptation, retaining
endpoint authority/generation, partial frames and rescan/error/cleanup semantics.
Actual sys-init still owns boot policy; this Rust owner is an Aether fixture. Keep
SDK/reader/full matrix and persistence/packages/R1 separate. Reproduce through the
copy-to-fresh command in NATIVE-CONNECTIONS; sealed records are not overwritten.
All original files remain BSD-2-Clause, frozen worker/upstream terms remain in the
referenced serial packet, and no siblings or standards release pins changed.

Two strict positive trace replays and18 named corruptions reject missing/duplicate/
wrong terminal identity/status, changed streams/prompts, extra UART, missing halt
and incorrect reclaim totals. Every unpacked attempt/regression root is sealed
and every archived file read back before removing its duplicate; source/evidence
exports, failures, commands and logs remain. See artifacts.json and cleanup.json.
