# Format coverage and repeated host qualification

2026-09-07 UTC. Documentation/inventory-only continuation of ADP04-02/03.
Twenty-seven critical groups are mapped, adding state idempotence/read-only views,
world validation, ownership, modes, schema rejection, cycles, publication failure
and canonical build-record digests. This is not complete format conformance.

The retained driver runs five sequential rounds of package-state.sh and
trust-metadata-records.sh. Each starts from a fresh verified private copy, with the
existing watchdog enforcing 60 seconds and cleaning only its owned process group.
Every round must exit zero and emit all three exact completion markers once.
Fixtures supply their own semantic assertions; missing completion or failed cleanup
cannot become success. The campaign stops on its first failure and retains every
attempt. No production source, scheduler, service or dependency is added.

inputs.json binds HEAD, dirty status and exact copied source/fixture bytes. The
driver checks each copy before execution and checks original inputs again afterward.
results.json retains command, time, deadline, raw exit, semantic completion, log
hash and private root for every round. Each root remains available for inspection;
no real prefix or shared checkout is mutated by the fixtures. driver.py.txt preserves
the executed development procedure, not a new installed test entry point.

This qualifies only the two repeated host fixture suites. It does not satisfy the
planned five-full-suite weekly campaign, deploy daily/weekly runs, discover new
fuzz seeds, exercise concurrent writers or prove native persistence/power-loss.
Elapsed times are operational observations, not comparative performance measurements.
The broader extended-test, native and human review gaps remain open.
