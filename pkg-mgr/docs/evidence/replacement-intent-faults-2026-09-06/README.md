# Replacement intent hash failure review — 2026-09-06

HR-02/HR-04 found that intent construction embedded hash commands in printf
arguments. A successful printf hid a failed hash helper, so preparation could
publish an intent with an empty digest field and return a prepared receipt.
The pre-fix regression failed with `FAIL: accepted invalid binary operation` when
the old-record hash request failed. before-test.log and before-result.json retain
the failed attempt; before-replacement.sh and before-inputs.json identify its
implementation and exact dirty-tree fixture inputs. This is false-success
preparation, not evidence that finish accepted an invalid intent or lost payloads.

Each intent digest is now assigned and checked before its field is emitted.
Failure propagates from intent generation to the prepare/finish command before
publication or further validation. Successful format and receipt bytes are
unchanged. There is no new diagnostic, format, dependency, native ABI or standards
pin. The existing helper error remains on stderr.

Ten controls fail the old-record, new-record, world, others.tsv and bundle/artifact.kv
hash requests during prepare and finish. The wrapper selects only the exact
hash-file helper and transaction-relative path, emits a required reachability
marker, and returns 73. Each case must fail without stdout and preserve the target's
file/hash/mode snapshot. Prepare must leave no pending transaction. Existing normal
prepare, finish, repeated finish and interrupted publication cases remain the
positive/recovery controls. PLAN.md records the oracle and forbidden outcomes.

The selected checks are scoped ShellCheck, the normal sixteen-fixture suite with
its 600-second watchdog and three standards gates, and final development/whitespace
validation. input-sha256.json binds the runtime/test inputs; tools.json identifies
the local host and executables. Raw suite output and exit status are retained.
The before-test run had a separate 300-second process-group watchdog. The recorded
Xcode host warnings are retained, not converted into a platform-support claim.

These command-failure injections do not establish physical full-storage behavior,
concurrency safety or power-loss durability. The previously qualified public
archive predates this correction and requires refreshed assembly and qualification.
Independent review, captured clean-builder setup, a monitored security contact
and publication approval remain separate release gates.

All sixteen fixtures, all three standards gates and whole-shell lint passed.
The ten new intent-hash controls and existing positive/recovery markers are
present in suite.log. Runtime/test input hashes remained unchanged after the run.
