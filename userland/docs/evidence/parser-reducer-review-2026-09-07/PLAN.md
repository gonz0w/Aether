# UL-062 reduction outcome review

Scope before changes: repair outcome classification in check-parser-extended.py.
Fixture exit 91, unexpected diagnostics/output, and retained byte/metadata mismatch
must stop reduction as incomplete, not count as a non-reproducing candidate.
Only exit 0 with exact PASS marker and no failure files is a negative outcome;
only exit 90 with exact named ORACLE line and matching retained evidence is positive.
This is host harness work; preserve production parser, C fixtures, process helper,
existing uncommitted host-stress work, native contracts and release pins.

Requirements: Testing TE-01–03, TD-01–05 and TC-02; Coding CE-03–05, CP-01–03;
Foundations E-01–08. Existing compiler/runtime pins and Python standard library;
BSD-2-Clause. Record source/plan hashes, all attempts and process receipts.
New unittest controls use private build roots and no subprocesses of their own.
Test normal positive/negative, fixture error, crash, cleanup failure, diagnostic
noise, missing success marker, mismatched bytes/metadata, invalid JSON and boolean
numeric fields. Retain every candidate outcome including classification failure.

Run controls on actual Python 3.14.7 and 3.10.21 and demonstrate the old outcome
logic's false-negative behavior. Run full affected --ubsan-only sweep/reduction
on both interpreters with the existing 30-second child timeout/1024-call bounds.
ASan remains NOT RUN; no silent fallback or native qualification. Quality gate
and git diff --check complete the selection. Preserve other work's evidence.

Self-review is scoped technical evidence, not independent maintainer/reader approval.
UL-062 stays active. The existing between-call time-gap check is not a total
reduction deadline; changing timing budgets or broader stress work is separate.
