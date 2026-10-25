# UL-059 / UL-063 / UL-081 decoder proposal experiment

Scope: host-only executable review of the proposed AERIO002 role decoder and
0x7b receipt decoder/terminal policy. No maintained runtime file, adapter,
bootstrap, runner, child payload or owner contract is changed or adopted.
Owner reconciliation required by SUSTAINED.md is still pending. This experiment
makes that proposal reviewable; it is not approval for UL-058 runtime changes.

Preimplementation source review by this Codex task: four-role.c validates size
and context before reads, exact roles/rights/capacities and all padding before
publishing a stack candidate. runner-result.c validates size/context first,
uses bounded unsigned wire-error decoding, validates reserved bytes and terminal
kind before publication. ar_terminal_exit additionally validates receipt, error,
kind, representable status and exact cleanup flag. No allocation, retained
pointer, transport, concurrency or authority effect exists in these pure functions.
Disjoint live input/output storage remains a caller precondition. Reference and
receipt values are connection-local selectors; these tests cannot prove ownership,
consumption, endpoint isolation, native generation or retirement. Review covers
these four source/header files only, not full UL-063 or native adapters.

Foundations O/I/E, Coding CE/CC/CP, Testing TD/TC/TE and Distribution PX/EV apply.
Sources and patch are hashed before use. Apply a small exact-context patch to a
private build copy and version all four decoder function symbols. Default sources
stay byte-identical. Use pinned Clang 21.1.8, C17 warnings-as-errors and UBSan;
owned process helper, clean environment, 30-second commands, 16 MiB per stream.
Preserve every command receipt, failure and build directory. No new dependency.
Original additions use BSD-2-Clause; copied sources keep notices.

Oracles: legacy controls unchanged; proposed controls cover eight boundary epochs,
all field-byte mutations/truncations, full error range and terminal statuses;
independent peer controls check all 65535 epochs and old/new rejection in both
directions. Wrong role bits, zero/overflow epochs, stale receipts and bad cleanup
must reject. A mixed-link control must fail specifically on versioned symbols.
Host behavior is the only execution claim. New test C requires formatter check;
Python syntax and local quality gate are required. Broader extended checks,
actual bootstrap tests, full-width native query checks, native linking/execution,
owner and independent reader review remain incomplete.

Simpler alternative: directly widen legacy comparisons. It cannot distinguish
wire versions and breaks frozen consumers. Choose a small patch to copied pure
decoders with explicit symbols, not a second maintained runtime. None of the
legacy path can be removed until matching owner delivery and acceptance.

Completion means an executable decoder proposal and retained local checks only.
UL-059/081 and the broader UL-063 audit remain open. Documentation impact:
SUSTAINED, STATE, BACKLOG and four-role coverage link this limited evidence.
