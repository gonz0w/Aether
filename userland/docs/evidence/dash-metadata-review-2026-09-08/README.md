# UL-007 metadata intake review — 2026-09-08

PASS for input verification and host static inspection only. **Metadata native
execution: NOT RUN.** The producer delivery selected here is a documentation-only
AECAT002 proposal; no completed runtime packet was available at intake.

[Consumer acceptance](../../../experiments/dash-native/METADATA.md) records twelve
local case families for the existing suite: tuple identity/reuse, staged admission,
malformed/truncated/versioned input, publication mutation, zero-ID denial, actual
initvar, public/raw distinction and failure readiness. Numeric producer failure
oracles and concrete fixtures remain to be bound at implementation delivery.
No startup probe or runtime implementation was added.

## Concrete configuration finding

The unchanged upstream var.c selects PS1 from effective UID before environment
import. main.c places its UID/GID equality guard for interactive ENV behind
`#ifndef linux`. [Recorded compiler macros](target-macros.stdout) define linux;
[the retained main object imports](main-imports.stdout) contain none of the four
UID/GID getters. Main object SHA256:
`27df57d1245db1297b348c6247f644893ff98849a7df23961464f46e83199b1b`.
The native startup fixtures wrap main, so their passing receipts do not qualify
this path. Native configuration and any alternative startup/environment protection
need an explicit decision and actual-main tests before full-shell acceptance.
This is not a demonstrated exploit or proof of absent protection in every layer.

The captured old bootstrap-failure oracle also expects signal queries to return
EAGAIN. The producer proposal correctly separates public raw signal state from
metadata/descriptor admission. The implementation must revise that selected
oracle without weakening descriptor/getter non-publication or legacy checks.

## Evidence and limits

[Results](results.json) bind all twelve producer input hashes, reference archive,
object, compiler/nm, exact command arguments, runtime environment and cleanup.
Both owned host commands exit 0 and clean up under a 30-second per-command deadline.
The macro query uses the recorded target/optimization mode without headers or
linking; it is not a complete native configuration rebuild. The source files match
the pinned dash 0.5.13.5 archive; cc.py/config.h and main.o match existing receipts.
No failed inspection attempt, changed source object or native test run.

Producer manifest SHA256:
`0985952be1fb7a9ee589076be3b3eff2d92e4d6b74129edb54198bd157bb87af`.
All four packet files and twelve regular archive members verify before review.
The full packet and extracted review inputs are retained with original terms;
main.c/var.c/COPYING are unchanged upstream extracts. run.py is the exact one-off
inspection script. Its actual interpreter is Python 3.14.7; minimum-version
execution and full source/reader review are not inferred. Outputs remain under
`build/dash-metadata-review-tk5iz3ok` and are retained here. Quality gate passes.

Next: capture a completed metadata runtime delivery and run the matching existing
suite; scoped directory/CWD follows. Resolve the separate full-main configuration
question before consuming actual-main/ENV behavior. UL-007/M3, UL-016, UL-063/081
and independent technical/reader review remain open. No sibling edit, message,
consumer-default change or release pin update occurred.
