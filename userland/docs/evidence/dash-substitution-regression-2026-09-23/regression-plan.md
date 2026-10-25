# UL-007 substitution full connections regression

Run all358 native connections cases from the same frozen268-source fixture as
our prior three focused substitution cases. Preserve the sealed prior packet.
This new packet reuses its verified source/SDK/tool inputs, existing owned work
root and byte-identical driver. Old suites were already verified/compacted;
only new completed output is selected for this packet's compaction.

Foundations E-01–08, Testing TE-01–05 and the original review.md apply. No runtime,
sibling, tool, SDK, compiler flags, released pin or command-runner behavior changes.
The original preparation/host receipt is reused, not newly executed: all633
restored sources/support,4311 SDK files and recorded tools are rehashed before
use. No source change invalidates the104-test host result. Source changes require
fresh qualification rather than refreshed pins. Preserve all failures.

Use timed.py connections with existing owned run():3600-second deadline,512MiB
stream bounds, guest watchdogs unchanged,1800-second review ceiling. One native
suite at a time. Exact inventory, pass results and268 harness source hashes must
match producer receipt. Compare all14 scratch/substitution lifecycle and PASS
oracles from sealed prior packets after completion, retaining all358 serial logs.
Complete owned process cleanup and post-run source/SDK/tool integrity required.

Retain receipt, output hashes, raw logs and source identities; archive/readback
verify every generated file and unchanged original inventory before removing
only this new suite and its compiler cache. Sources/SDK and historical archives
remain. Sources and prior host receipt are linked through prior-evidence.json.
No new framework, dependency, installation or authority. This is bounded private
regression, not matching command-runner, supported SDK or assembled M3 acceptance.

Codex performs scoped technical review; independent owner/reader review pending.
Record actual elapsed and cleanup. Update acceptance references and STATE only
after success, then run local quality gate. Pipeline/early-reader, matching
command-runner producer/consumer, SDK/reviews, persistence and R1 remain open.
