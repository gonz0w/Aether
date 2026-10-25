# Unchanged DASH-signal-table review — 2026-09-13

Requirement: execute the unchanged userland signal-table.sh through actual dash.
Its real child runs kill -l 10, writes USR1 plus newline to its pipe, and is
waited/acknowledged. The parent installs a USR1 trap and signals itself; the trap
must produce signal ok plus newline. Preserve exact input bytes, real statuses,
backend readback, EOF and six reclaims across two complete lifetimes.

Aether owns this private producer adapter and scope enforcement; userland owns
independent acceptance and SDK integration. No sibling edits or release-pin
updates. Existing one-child pipe, signal actions, mask restoration and explicit
self-delivery operation are reused. No kernel, quota, dependency or service change.

The new opt-in kill facade supports only positive current PID with signal0 (probe)
or SIGUSR1 (existing synchronous native post/delivery). Foreign positive PID is
EPERM; groups/nonpositive PID and other valid signals are ENOTSUP, invalid signal
numbers EINVAL. A PID is advisory identity, never authority to address another
process. No process table lookup or general kill API is introduced. Before script
entry verify invalid/group/foreign/probe behavior without modifying signal state.

Forbidden: forged signal-name pipe bytes, false EOF/wait, dropped signal reported
as successful completion, cross-process signal authority, fake trap output or
uncleared/reused descriptors. Test omitted native post and bypassed PID guard as
separate negative profiles; preserve the consumer script bytes in both.

Simplicity: adapt the existing pipe owner and native self-delivery boundary;
a separate signal service or new PID authority mechanism is unnecessary. Restrict
the private facade to the present workload rather than inventing general kill
semantics. No consumed path is obsolete yet. Existing single-context transport
masking, valid native interrupt frame, handler/restorer validation and kernel-owned
pending state continue to govern reentrancy and cleanup. The revised FFI call has
no borrowed pointers; handler entry can occur before the call returns.

Selection: focused positive and both semantic controls, complete connections suite,
host/harness/pin checks, scoped C/Rust formatting and separate simplicity hashes.
Freeze sources per run and retain all attempts. Update native shell/connections,
STATE and companion handoff scope. This is not full-dash or SDK acceptance.

Status: final bounded producer qualification passes. All287 connections cases
pass in 881.73s. The final focused run passes all seven argument/signal cases.
Host tests (100 Python tests plus Zig checks), C/Rust formatting, workflow and
immutable standards pins pass; the simplicity manifest and four files match.

Final retention: 256 frozen runtime/test files, 242 harness source hashes,
5117 final target artifacts, all four preflight directories and the deliberately
interrupted early full build. Archives are verified member by member; command
receipts preserve timing and outcomes. Runtime/test sources stayed frozen during
the final preflight, host tests and full native run.

Attempts: preflight1 rejects a formatting-sensitive script extractor before QEMU;
preflight2 passes three cases with the earlier fixture environment. The first full
build is stopped before QEMU to correct the consumer environment. Preflight3 then
finds the argv extractor matching the newly added environment literal; its pattern
is scoped to the command and a reused local variable name is corrected.
Preflight4 passes all seven cases with the captured manifest environment. The
earlier passing preflight is not a substitute for final qualification.

Compatibility inventory: 95 previous clients and25 replacement images are unchanged;
four argv clients change for the environment.262 owners are unchanged;15 pipe
variants change with pipe-byte selection and pass full regression. An initial
comparison's assumption of no owner changes is explicitly corrected in
compatibility.json. New owner10,768bytes; maximum final owner15408 within16,384.
No kernel, ABI, SDK, sibling, quota or released standard pin change.

The [contract](../../NATIVE-SHELL-STARTUP.md#unchanged-consumer-dash-signal-table--2026-09-13)
and connections.json supply replay details using the existing connections command,
pinned SDK and tool lock. native-traces.json and argv-native-traces.json require
exact terminal/reclaim outcomes. The implementation diff is relative to the
prior argv packet; earlier sealed evidence remains untouched.

Next consolidate the phase-one producer handoff with matched inputs, artifacts,
replay and explicit gaps. This does not grant independent acceptance, install a
public SDK, finish the twelve-workload gate or assemble the R1 filesystem shell.

## Consumer environment correction before final qualification

The consumer WORKLOADS.md and workloads.json require WITNESS=value, LC_ALL=C and
PATH=/nonexistent. Initial probes used the older private-shell environment. Stop
the first full build, preserve its original receipts/sources/artifacts, and align
both opt-in argument and signal profiles with the manifest before final runs.
Retain PWD=/work for the existing explicitly granted cwd. Capture and hash the
consumer manifest offline, check its script/exit/stdout and environment contracts,
and compare both C environment literals at build time. This affects the four
older DASH-argv client ELFs; it does not alter the prior sealed packet or any
sibling. Include all seven argument/signal positives and controls in the new
focused run, then repeat full connections and host qualification on frozen sources.
The first restricted process-stop request was denied by the sandbox; an approved
retry stopped only the owned test group. No source changed while it was running.
