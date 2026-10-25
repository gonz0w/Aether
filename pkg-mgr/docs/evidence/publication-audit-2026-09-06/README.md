# Publication and cleanup audit — 2026-09-06

Scope: bounded release review of state initialization/registration, binary
export/import/recovery, replacement preparation/finish, and their owned cleanup.
The implementation under test is the previously qualified 187-file candidate
`9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043`.
No runtime implementation or candidate bytes are edited by this audit.

## Requirements and review

Accepted state must survive failures before publication. A nonzero result after
a rename can mean the effect already occurred: inspect actual bytes, do not infer
absence or blindly replay. Recovery must validate retained bytes and the original
pin. Cleanup may remove only scratch or a newly published unregistered stage owned
by this invocation; it must preserve committed records and their payloads.

The reviewed code has explicit same-filesystem publication paths. State init and
registration own their pending temporaries. Binary import tracks its new stage and
checks record existence before cleanup; a failed stage rename after the effect can
leave a stage for explicit pinned recovery. Recovery does not own the existing
stage. Replacement prepares adjacent non-authoritative workspace, guards readers
while pending, and retains prior payload/records through completion. Historical
partial-record-copy evidence remains blocked and preserved rather than repaired.
These rules assume a caller-controlled filesystem and one writer.

## Executable plan

The one-off audit.py and fault-tool.sh operate on private clones of the qualified
bytecount fixture. A record-only synthetic version 0.2 keeps the original executable
and changes version/build-record binding solely to exercise replacement; it is not
an upstream bytecount release or a new base-package recommendation. The synthetic
record and bundle pass the candidate's normal validators before fault testing.

The matrix covers 27 cases:

- State init rename: failure before/after (2).
- State registration pending copy and record rename: before/after (4).
- Binary export rename: before/after (2).
- Binary import stage and record renames: before/after (4).
- Binary import record rename failure plus failed owned-stage cleanup (1).
- Explicit recovery record rename: before/after (2).
- Replacement prepare adjacent copy and pending rename: before/after (4).
- Replacement finish old-stage, new-stage, record and history renames: before/after (8).

The wrapper emits a required marker and fails before the selected command or after
executing that command successfully. Unselected commands delegate to identified
host tools. Every injected operation must return nonzero without a success receipt.
Exact file/hash/mode snapshots distinguish uncommitted, committed and pending states;
retry or explicit pinned recovery must pass at the declared recoverable boundaries.
Failed cleanup must retain the stage, leave the record absent and allow explicit
recovery. Recovery is never taken as permission to delete a preexisting payload.

Each child invocation has a 60-second limit; the outer process-group watchdog has
600 seconds, with a 540-second driver budget. Raw commands/statuses/stdout/stderr,
before/after snapshots, input hashes and every failed attempt are retained. The
same selected candidate files and archive digest must remain unchanged afterward.
The driver is an evidence artifact, not a new product command or supported test
framework; the existing development inventory already owns these runtime surfaces.

## Harness corrections and limitations

Initial ShellCheck flagged a dynamic glob pattern. The wrapper now quotes the
controlled prefix/suffix and uses an explicit wildcard; no suppression was added.
initial-lint.log retains the finding. The first runtime audit attempt copied the
package record with copyfile, changing its mode from 0600 to 0644. The export bytes
matched but the mode oracle correctly failed. attempt-1 retains the script, exact
hashes, raw commands and failed assertion. copy2 preserves the original mode in
the corrected fixture. This was a harness error, not a demonstrated runtime defect.

This audit does not simulate physical full storage, flush ordering, power loss,
hostile filesystem races, concurrent writers, arbitrary cp implementations or
external side effects. Existing corruption and partial-write controls remain
separate evidence. Passing these cases does not establish complete security or
production durability. Independent review, captured clean-builder setup, broader
qualification and a monitored security contact remain release gates.


## Outcome and freeze checkpoint

All 27 cases pass, including failure after successful renames and explicit recovery
from failed stage cleanup. No additional runtime defect was demonstrated in this
bounded audit, and no runtime/candidate changes were required. result.json records
the elapsed run, calls.json and numbered streams retain every invocation, and
results.json records before/after snapshots. The candidate's 187 selected files
retain exact bytes/modes and its archive digest remains unchanged.

The prior full-suite/manual qualification still applies to these unchanged bytes;
this additional audit does not require repeating unrelated runtime tests. Final
checks cover the evidence wrapper lint, Python syntax, development documentation,
standards and whitespace. Runtime changes are frozen except demonstrated release
blockers; repeated candidate transaction qualification and independent reviews are
next. This freeze is a scope checkpoint, not release approval or a write lock.
