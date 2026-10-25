# Shell continuation and normal exit cleanup — 2026-09-11

Actual dash returns to its `$ ` prompt after /next reads host a and exits72. Only
then does the host send `echo $?;exit N`. Dash prints72 and exits0 in session1,
then7 in session2. Four real prompts, six ordered host exchanges, per-session
22/27/4 stdin/stdout/stderr byte totals, final shared closes and six exact terminal/
reclaim outcomes pass. Both sessions still share one UART backend; slot reuse is
denied its still-open grant.

The private console driver no longer selects healthy parent cleanup by exit72/73.
It captures the initialized parent's PID and uses startup_ready plus unpoisoned
transport for that parent's normal exit. Copied-child error paths and other driver
modes retain the prior gate. This local PID comparison grants no authority and is
not a general process/descriptor API or an installed libc change.

| Check | Result |
| --- | --- |
| Complete connections suite | 241 cases pass, including three resumed-session cases |
| Launch suite | Five cases pass |
| Console ABI18 regression | Two cases pass |
| Host/harness/workflow and offline pins | `zig build test` passes |
| Rust/C formatting, workflow, standards, experience and whitespace | Pass; final-checks.json records commands |
| Simplicity snapshot | Pinned manifest and all four files verified |

The `-resume-cleanup` control retains the old exit-code gate: parent exits0 without
final descriptor cleanup and owner2131 rejects with zero reclaims. `-resume-exit`
chooses8 instead of7 in the second session: parent8/owner2130 must reject with two
reclaims from the completed first session. Expected contexts are required; generic
panic or timeout is insufficient. Existing serial one-line, native dash, wait,
shared-offset, poisoned-transport and cleanup controls remain regressions. No
unexpected build or target attempt failed in this qualification.

[Plan](plan.md) records the pre-code requirement, forbidden outcomes, test selection,
ownership/resource implications and SE01–05 review. The existing post-fork request
loop already supports another stdin command; the actual lifecycle fix removes
exit-code policy from healthy parent descriptor cleanup. No new kernel mechanism,
protocol, dependency, queue, SDK object, released pin or sibling modification.
The private normal parent path is tested for0,7 and72. Readiness/poison guards are
retained; this does not qualify arbitrary asynchronous exit, cancellation, fault
cleanup or indefinite input waiting. All upstream object and released standards pins remain unchanged.

The test still allows one external child per shell. Collected children remain
retained until shell exit, and the private admission fixture assumes matching
parent/child generations and its first freeze token. Next decouple those lifetimes,
reclaim after confirmed terminal plus wait acknowledgment, and qualify another
external command within the same shell while rejecting stale references. Editing,
job control, general pipelines/redirection, independent consumer adoption and
sys-init/filesystem/package release assembly remain separate acceptance work.

`*-timing.json` binds commands, timestamps, durations and return codes.
`*-results.json` binds case lists and tool/source hashes. Copied serial logs and
`dash-exchange.json` show the prompts, status output, chosen exit codes and exact
negative contexts. `run-sources.*` preserves the frozen inputs; `sources.*` adds
post-run reference/progress updates. `change.patch` compares the preceding serial
dash packet. `artifacts.json` indexes the read-back-verified artifact archive;
`qualification.json` records counts and maximum owner size. `manifest.json` seals
this packet. `cleanup.json` records removal of verified superseded unpacked
outputs, preserving the preceding archive and the current target directories.
Recorded helper scripts are audit artifacts; do not rerun them in this sealed
packet. Use the live documented commands with a fresh evidence destination.

The snapshots cover255 source files and4,368 target artifacts; maximum compiled
owner size remains9,528 bytes within16 KiB. Input accounting is6 command bytes,
one child byte and15 continuation bytes, computed as22 before the first run.
Verified cleanup removed 2.53 GiB of superseded unpacked outputs.
