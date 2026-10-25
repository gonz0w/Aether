# UL-007 real serial SESSION handoff

2026-09-29. Consumer-owned input after scratch acceptance. Native **NOT RUN**.
Execute the same command sequence as accepted SESSION-01–06 in one interactive
dash parent, grouped into three LF-terminated [inputs](serial-session/README.md).
This is the missing serial form promised in SESSION.md, not an accumulation of
scratch, recovery and failed-exec scripts that would exceed current lifetime limits.
Those compositions retain their separate accepted scopes.

## Input and output contract

Launch actual dash main in the owner's existing interactive serial mode. Use the
unchanged helper at /inputs/helper, WITNESS=value, LC_ALL=C, PATH=/nonexistent,
PS1=`$ ` and PS2=`> `; declare the exact native bootstrap/PWD and environment allowlist
in the producer delivery. Shell parent and copied children must not acquire direct
UART authority. An authenticated serial owner alone forwards stdin/stdout/stderr
under the current native grant and holder rules. Path names and FD numbers are not
grants. No scratch authority, real-prefix installation or package setup is needed.

The harness sends command1 only after this parent's real first prompt; command2
only after the returned prompt following phase1; command3 only after the prompt
following phase2. Never preload later phases or invoke a separate shell per line.
Track byte offsets, exact sent bytes, generation and observed prompt for each input.
Split at least one input into positive short writes; advance by actual accepted
count without dropping/repeating bytes. Do not use a sleep as the handshake.

Phase1 establishes session_parent, checks external argv/environment and a pipeline.
Phase2 captures substitution, checks its bytes and runs another pipeline. Phase3
rechecks x across the returned prompt, then checks FD closure, the original parent
PID and separate stderr/stdout,
then exits0. The shell must retain state across prompts. All pipeline stages0,
real EOF, completed waits and cleanup before next prompt are owner requirements;
the last pipeline status alone is insufficient. Prompts are output, not proof of
cleanup without matching native lifecycle observations.

The manifest pins commands, helper, original source, exact65-byte stdout and19-byte
program stderr, two-byte prompt, phase exchange and exact90-byte combined UART
stream per parent. There are three prompts/sent commands per parent and no fourth
prompt after exit. Raw serial logs may interleave kernel markers: retain them,
record command/prompt offsets and separately identify forwarded UART bytes using
owner-defined observation framing. Do not regex-away arbitrary unmatched bytes.
The combined UART oracle does not independently prove fd1/fd2 routing: also require
source-bound owner channel/rights checks and a stderr-misroute negative. Preserve
existing native boot markers and upstream prompt bytes; no styling change.

## Native acceptance and controls

| ID | Required observation | Status |
| --- | --- | --- |
| SERIAL-SESSION-01 | Three actual prompt-driven inputs, exact byte framing/short-write progress, no future-input preload or parser execution shortcut | NOT RUN |
| SERIAL-SESSION-02 | Same authenticated parent/$$ and retained x; real argv, substitution and both pipelines with all healthy child statuses/EOF | NOT RUN |
| SERIAL-SESSION-03 | Returned prompts follow all preceding phase child terminals/collection; exact UART and checked stdout/stderr routing, no command echo | NOT RUN |
| SERIAL-SESSION-04 | Native UART grant enforcement, copied/parent direct-access denial, empty-read EAGAIN and stale/closed endpoint rejection | NOT RUN |
| SERIAL-SESSION-05 | Precise semantic negatives plus owner-requested idle-parent cancellation with confirmed stop/closure/reclaim | NOT RUN |
| SERIAL-SESSION-06 | Three fresh parents, exact phase/admission/terminal accounting and serial/pipe holder retirement before reuse | NOT RUN |

Positive per parent: nine copies, seven successful helper replacements, eight
image admissions including parent and ten terminals/reclaims. Across three:
27 copies,21 replacements,24 admissions,30 terminals/reclaims. Under the existing
slot policy slot2 has five lifetimes per parent (argv, first writer, substitution,
second writer, closure); slots3/4 have two each. Reconcile the actual map first;
these expected totals do not authorize identity truncation or quota growth.

Require wrong WITNESS helper91/parent31; corrupt first pipeline UART bytes with
normal lifecycle but exact-output rejection; corrupt substitution result with
parent33; fd3 leak helper95/parent35; altered/misrouted stderr; stale wait/serial
reference and wrong UART selector. Preserve exact expected prefixes and freeze
native result codes, image admissions and terminal/reclaim identities before
replay. Native stderr failure may end in wrapper141; do not invent a script code.
Known prior serial corruption changes both p bytes: specify the actual mutation,
not a guessed single-byte outcome. No timeout/crash may satisfy a semantic control.

Require a harness counterexample that sends a later command without its fresh
prompt, a duplicate/missing prompt, wrong generation, dropped/duplicated input
byte and a fabricated prompt before child completion. Reject before falsely
recording success. Distinguish harness/parser controls from actual native mutations.

For cancellation, stop supplying bytes after phase1 has fully returned its prompt;
observe an owner-confirmed empty read/EAGAIN with no synthetic EOF or advancement.
Then issue an explicit authenticated supervisor stop for that exact idle parent.
Expected parent terminal is kind3/detail143 (subject to owner confirmation), with
phase1's four successful children plus parent: five terminal/reclaims, three helper
replacements and four image admissions. All UART/pipe holders retire; no later
phase executes. Freeze owner result and closed/stale access results. This qualifies
explicit cancellation after input withdrawal, not physical UART unplug detection.
An empty UART is not EOF; serial has no assumed EOF-on-disconnect contract. General
hangup, job control, terminal editing and signal recovery remain separate gates.

## Producer delivery and bounds

Aether owns adapter/owner implementation and exact native authority protocol;
userland owns these frozen inputs and independent acceptance. No sibling edits
are authorized by this handoff. Supply complete sealed source/support and invoked
drivers, tool/SDK/ABI inputs, linked raw/ELF code and stack review, raw UART plus
phase/lifecycle records, selected host/native regressions and every failed attempt.

Preserve15 lifetimes, three children/two pipes,24KiB code and4088 usable stack.
Prior serial and session stack estimates apply to different images; inspect the
actual combined owner, including indirect calls. Do not silently import legacy
AENMX006/ABI20 assumptions into AENMX007/ABI21. No public SDK acceptance follows.
Consumer replay uses sequential3600-second native deadlines,1800-second review
ceilings,512MiB streams and unchanged guest watchdogs, with checked owned cleanup.
Archive/readback-verify completed artifacts before scoped duplicate removal.

Host preparation uses noninteractive stdin and explicitly relocated helper paths
under build/. It checks semantics only, never real prompt timing, native UART,
authority or cancellation. Real serial delivery/replay, SI-07 full transport and
rebuilt payloads, UL-081 SDK/review and full M3/R1 remain open.
