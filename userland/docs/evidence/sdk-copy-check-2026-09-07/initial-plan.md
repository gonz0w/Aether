# SDK startup copy verification — UL-005 / UL-063

Before compiling, verify each staged adapter/probe against its receipt hash, as
already done for SDK files. Source validation alone precedes copying and cannot
establish the bytes actually consumed. Preserve original receipt, SDK/tool pins,
link flags, 30-second command deadlines, cleanup and error/exit contracts.

Change review: userland-only Python evidence harness; Foundations E-01/E-05/E-06,
quality CP/TD/TE, existing SDK-05 startup plan. No sibling or native code changes,
new dependencies or authority. Independent technical review remains pending.

Controls: normal copy matches; altered destination after copy and live source
change during copy reject. Integration control injects changed copy bytes with the
source restored, requires incomplete report and zero process commands. This must
fail against the prior harness. Do not mutate real source or imported SDK inputs.

Run python3 -B experiments/sdk-consumer/test-startup-copy.py (60-second budget),
then python3 -B experiments/sdk-consumer/check-startup.py (5-minute suite budget,
existing per-command limits), then python3 -B docs/quality/check.py. Test temporary
files and outputs stay under build/. Retain commands, interpreter, hashes, results
and failed attempts in docs/evidence/sdk-copy-check-2026-09-07. Compare startup ELF
to the earlier receipt-pinned result. No native execution needed for this change.

Documentation impact: README, draft coverage and UL state. This fixes a gap within
trusted private staging; it does not claim protection from a hostile writer able
to modify the private directory after validation or the toolchain during execution.
Prior evidence remains unchanged. No whole SDK/native acceptance follows.
