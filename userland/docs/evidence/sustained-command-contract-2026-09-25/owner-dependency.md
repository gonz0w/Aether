### Current SI-07 integration dependency — 2026-09-25

[Exploratory results](evidence/sustained-core-2026-09-25/README.md) demonstrate the
serial-selected kernel mechanism: 3004 idle ticks, wake on real UART input,
contextual grant denials, channel reuse beyond three lifetimes and checked halt.
The legacy five-case real-command suite still passes. These are selected checks,
not complete new-profile qualification or independent sys-init acceptance.

The real runner/bytecount/backend composition completes generations 1 and 2.
Generation 3 is admitted by the kernel, then runner startup exits 110: the frozen
userland `experiments/command-runner/four-role.c` rejects all generations except
1 and 2. `runner-result.c:ar_admission` and `native-io.c` contain the same restriction.
The current sibling copies are byte-identical to those pinned inputs. The first
exploratory run timed out after this rejection because the old fixture error path
called unsupported finish; the new profile's error path now emits a failure and
faults, and the second attempt reproduces the same generation-3 exit immediately.
Neither run is accepted as sustained success. The consumer checks remain unchanged.

Userland must provide a versioned sustained role-carrier, admission-reply and
native-I/O contract plus matched rebuilt runner/bytecount inputs and rejection
oracles. It must specify finite private reference/receipt generations and retirement:
current file references combine generation with fields at bit 16, so expanding a
comparison to the kernel's 28-bit lifetime would alias fields. Preserve existing
bounded decoders/fixtures and do not conflate private protocol epochs with native
instance identities. Sys-init then supplies its owner and accepts the composition.

After matching input delivery, finish five useful cycles and real shutdown,
worker/foreign authority and race controls, fresh source-built inputs, and matching
legacy regression/evidence before presenting SI-07 as a producer handoff. The current
experimental profile is not merge/release qualification. No sibling edits or
relaxed consumer assertions were used to bypass this dependency.

Exploratory commands (prepared images and original prerequisites are recorded in
that packet): `python3 docs/evidence/sustained-core-2026-09-25/run-probe.py`,
`python3 docs/evidence/sustained-core-2026-09-25/run-final-probe.py`, and
`python3 docs/evidence/sustained-core-2026-09-25/run-command.py`. Use a new
`PROBE_ATTEMPT` value for each execution; do not overwrite existing run receipts.
The command probe is expected to expose the recorded consumer rejection until
new inputs arrive. It is not a passing smoke command.

