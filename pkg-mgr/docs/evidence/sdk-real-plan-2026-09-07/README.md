# Real-input SDK planner evidence

2026-09-07. One-shot execution of the existing read-only helper; no runtime/helper
implementation changes. [Observation recipe](run.py), [source pins](inputs.json),
[commands](commands.json) and [workspace](workspace.txt) retain the actual inputs
and actions. The recipe refuses to overwrite an existing command log. Each command
has a 120-second deadline; nonzero unexpected results stop the observation.

The installed SDK is freshly imported using the accepted real descriptor/profile
pins. SDK-only roots copy the exact retained baseline and changed-observation
records and their stages; state verification checks the copies. The changed SDK
is an observation, not a newly exported or admitted SDK. Historical profile
receipts do not requalify changed bytes merely by remaining manifest-bound.

Fresh consumer packages contain the retained userland ELF as non-executed 0644
data, the exact opaque input receipt, and a new sdk-static-binding-v1 KV file.
This is explicit local package metadata; the old JSON binding is not silently
adopted as the new format. probe-workload and unrelated-data are synthetic scope
markers around that real consumer, not actual userland package candidates.

Registration uses advisory observation metadata. Its minimal sbom_ref document is
an unvalidated metadata reference, not an SPDX-conformant or complete SBOM. It is
not a release artifact. No compiler, native executable, build/apply command or
service operation is run by this observation. No source authenticity is inferred.

The oracle compares the complete TSV with an independently constructed expected
report, not just a helper-derived selection. Before/after snapshots cover root
entry types, modes and hashes on every planner invocation, plus all three retained
source roots and every source input hash at the end. These are quiesced private
roots, not hostile-concurrency or storage-durability evidence.

[Owner checkpoint](owner-checkpoint.json) separately retains userland's current
native/record-review document identities. Its native result reports a matched
positive/denial/positive-reclaim slice for the same ELF; it explicitly lacks denial
native reclaim and independent approval. We compared the ELF identity and the
review's binding to our prior result. We did not rerun its native workload or
supply independent release acceptance. Historical failed/NOT RUN checkpoints
remain intact, but no longer describe the latest bounded native result.

[Final result](result.json): all seven outcomes passed in the first attempt, across
46 successful or expected-rejection commands. The [handoff](../../SDK-REAL-PLAN.md)
links the exact reports and describes remaining producer/reviewer work.

[Checks](checks.json) retain passing documentation/standards/whitespace commands,
exact dirty documentation hashes and post-run tool identities. Runtime inputs match
the prior passing full suite; no runtime change justified rerunning that suite.
This is not a new full-suite, target-support or original-build-host qualification.
