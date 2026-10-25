# Host readiness writers — 2026-09-05

[Decision 0014](../../decisions/0014-host-readiness-writers.md) retains the fixed
first frame. Three new methods use real pipes/children to test repeated writes,
bounded junk pressure and a forked helper's late notification after main exit.
No runtime/model or wire-format change was required.

The second valid write gets EPIPE without another consumer launch. A nonblocking
writer has a 1 MiB successful-byte ceiling and five-second watchdog; the adapter
rejects its invalid prefix after exactly one six-byte read. The writer ignores
SIGTERM, remains alive and observes EPIPE, distinguishing reader closure from
process death. This is bounded pressure, not unbounded throughput measurement.

The helper inherits the actual main readiness writer through fork. It registers
before main exit, then writes six bytes only after the test has reaped the main
but before the adapter's observation cut. The adapter discards that buffered
frame, never admits the consumer and closes the reader; the helper's retry gets
EPIPE. A cooperative release closes the helper writer and records exit-path
progress. The helper also has a ten-second self-watchdog. External helper reaping
is unobserved. No numeric orphan PID is signalled and no crash containment is
claimed. The successful host log retains a LATE-HELPER-WITNESS record.

[Full validation](validation/results.json) passes 45 host tests, 34 model tests/
three mutation controls, 23 harness tests, the historical native evidence audit
and three offline standards checks. No Aether execution or companion edits ran.

[Mutation](mutation.json) suppresses known terminal handling and permits reading
readiness for an exited process only in a private source copy. Only the helper
test fails, with readiness incorrectly true; there are no other failures/errors.
The current runtime digest matches the retained pre-mutation digest. The mutant
is inert evidence, not a runtime replacement. Cleanup requests helper release
also when the negative assertion fails.

Run `python3 scripts/check-all.py` or
`python3 -m unittest discover -s tests -p test_host_readiness_writers.py -v`.
Mutation substitutions/command, source snapshots and validation logs are retained.
SHA256SUMS.json fingerprints this bundle. [Acceptance review](../../HOST-READINESS-ACCEPTANCE.md)
keeps diagnostic, cross-host and production limitations explicit; BG-040 stays
active/partial. Shared standards and historical evidence remain unchanged.
