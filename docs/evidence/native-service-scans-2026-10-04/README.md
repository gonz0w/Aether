# Larger-owner bounded scans

Status: private producer qualification passes, 2026-10-04.
[Before-code scope](contract.md) preserves the private memory/authority profile
while replacing repeated metadata scans. [Reference](../../NATIVE-SERVICE-SCANS.md)
records the algorithmic bound and remaining limits.

44 fresh targets pass: 25 maintained default/large memory, seven M4, ten larger
owner and two storage cases. Full 137 Python/Zig/Rust/pins/workflow and 15 memory
tests pass, including deterministic comparisons against legacy small-owner plans
and whole-owner permuted cursor clearing. The actual removed coverage guard fails
the anonymous-hole witness. Three selected release omission guards reject.
The three-generation big-image fixture restores full-budget allocation in every
generation under the unchanged 30-second watchdog. Its roughly 11-second recorded
build/guest interval is not measured syscall latency or WCET.

`sdk-setup.py` verifies every member of the sealed upstream/SDK inputs, stages a
private original SDK plus a receipt-name adaptation for maintained regressions.
`native.py` and `threads.py` record actual commands/source/tool/SDK/header receipts.
`regressions.py` runs unchanged maintained memory oracles; `python3 scripts/regression.py`
runs seven M4. `model.py` qualifies pure plans and a real removed coverage guard.
`checks.py` binds results and historical unchanged bodies; `archive.py` reads all
owned members before removing verified duplicates. `manifest.json` binds packet
files. A setup-edit script used the wrong workflow key before qualification; no
workflow bytes or targets changed in that failed invocation.

Prior memory packet attempts remain sealed, including the timeout. Prior full
pair/origin/reuse/entropy coverage is historical, not additional fresh cases.
Temporary bitmap stack cost is 1 KiB on the existing 64 KiB exception stack; no
measured stack peak, production latency, larger workers, independent reader/SDK,
full engine, persistent filesystem or assembled R1 claim. No sibling/pin changes.
