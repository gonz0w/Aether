# Serial-session denial controls

2026-10-04, decision0186/BG-067. Eight fresh Aether VM controls pass expected
rejection: five expected boot-handle mismatches, actual console read/write with
halt grant (-13), and actual halt after the real shell workload while console
remains live (-16). Maintained runtime raw/ELF/source and release pins are unchanged.
The [acceptance matrix](../../SERIAL-SESSION-ACCEPTANCE.md) names exact scope.

All early cases have the supervision boundary, exact owner failure/UD2-vector6
context, no admission, input event, terminal or successful halt. Wrong-grant cases
require a marker emitted only after actual -13. The late case requires original
90-byte UART/eight-admission/ten-terminal identities and prompt-driven fragmented
commands, confirmed -16, owner fault and no halt/replay. It intentionally retains
console authority; host emulator teardown is not guest cleanup. No direct native
reclaim-count claim is made from terminal records alone.

Linked inspection before boot verifies raw/ELF .text parity, immutable builtin
indirect calls and scoped stack. Handle controls:15120/3816, actual grant controls:
288/64, late halt control:15216/3864 bytes. Limits stay16384 code/4088 usable stack.
Client, spare, entropy and all other boot modules read back exactly for each ISO.
Original kit notices are retained in the artifact archive. Tools are already local;
no kernel/SDK/client rebuild, sibling mutation or platform expansion occurred.

Rejected private variants in rejected/ retain source, assembly, stack records and
raw/ELF artifacts (archived): omitted-close4232, out-of-line lifecycle4504 and
zero-length-query4232-byte stacks. None was booted. The final late source keeps
constructor/lifecycle/settlement out of line, with zero-length console queries
instead of closure. Initial prepare.py is historical setup; the final qualified
sources/variant.json maps in each case are authoritative, not a replay of that
initial preparer. build.py consumes those explicit source trees and variant maps.

The first early-read run used the positive smoke driver and stopped at unexpected
prompt bytes before full panic. rejected/read-driver-preempted/ retains it; it
is not accepted denial evidence. Final native.py uses a no-input bounded drain
for early controls and the maintained prompt-driven smoke for the late workload.
Final check.py independently rejects unrelated faults, absent/wrong markers,
wrong linked RIP, missing cleanup, false halt, timeout identity and stream/identity/
fragment mutations. Four host tests execute eight retained traces plus mutations.
Tool/native bounds and owned live-group cleanup remain180s/4MiB and90s/1MiB UART/
4MiB stderr. Filesystem deadlines/races, detached tools and fatal/repeated signals
remain limitations.

Validation contains full local check output and focused tests. artifacts.json
pins the two bounded archives and every member; sha256.json seals the packet.
readback.py verifies membership, retained oracles and checked-source identities.
New controls establish only their recorded VM boundary. Remaining component-loader
matrix, admission exhaustion, further cleanup uncertainty and independent assembled
review remain open. No sign-off, release authorization or full conformance inferred.

All ten local gates pass in validation/results.json (out/checks/run-9o0mt5xj),
with checked sources unchanged. Four focused host tests pass. identity-timing.json
records when inputs and harness identities were captured; no retrospective
pre-frozen harness claim is made.
