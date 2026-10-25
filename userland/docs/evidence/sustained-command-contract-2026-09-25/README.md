# Sustained command dependency: contract and host checks

Aether SI-07's real-command prototype reaches generation3 and is rejected by the
unchanged userland two-generation profile. This packet supplies a
[versioned proposal](../../../experiments/command-runner/SUSTAINED.md) and scoped
source assessment. It does **not** supply rebuilt sustained binaries or unblock
native qualification yet.

The proposed opt-in profile uses AERIO002, a tagged child bootstrap, a disjoint
receipt tag, private nonzero16-bit epochs and explicit cohort retirement at65535.
Native generations and private epochs remain distinct concepts; the initial profile
requires exact cohort equality and rejects divergent identities. Owner review is
pending. Legacy defaults, wire bytes, source and accepted evidence are unchanged.

Executed checks on macOS27 arm64:

- All458,745 identities across seven private namespaces and65,535 epochs are
  distinct; stale predecessor and cross-role comparisons reject.49 invalid-epoch
  checks pass, including zero, overflow, native28-bit maximum and bool input.
- A concrete widened-field collision is reproduced. This is arithmetic evidence,
  not a native exploit claim or runtime retirement/authority witness.
- Existing four-role controls pass648 cases. Existing result controls pass28,159
  assertions. Both compile/run with Clang21.1.8, C17 warnings-as-errors and UBSan;
  no sanitizer failure, retries or incomplete cleanup occurred.

`inputs.json` pins sources, tools, script/review and host identity before checks.
`results.json` and process logs bind exact commands, SDK metadata, sanitizer runtime,
limits and cleanup. All commands use the unchanged owned runner,30-second limits
and16 MiB streams. Build output stays in the recorded private build directory.

Source review identifies an additional terminal-exit receipt restriction beyond
Aether's first reported startup failure. The complete change must cover role carrier,
runner and child bootstrap, admission, collection, terminal policy and both rebuilt
payloads. Updating one comparison is insufficient.

Next: reconcile the private contract with Aether/sys-init, complete affected UL-063
review, implement the opt-in decoder/build paths and fresh malformed/stale/exhaustion
controls, then deliver linked inputs for matching native producer and consumer runs.
Host checks do not establish SUSTAIN-01–06 native acceptance. The independently
pinned dash recovery workload remains ready in parallel. Full M3/R1, shared SDK,
independent reader review and sys-init acceptance remain open.
