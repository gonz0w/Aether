# Runner-only empty-output lifecycle — 2026-09-07

The first UL-059 prerequisite passes: two generations each admit only parent and
backend, accept explicit generation-bound closes, verify unchanged input/empty
output through backend readback, consume backend handles and reclaim both native
instances. The final count is four, with ordered parent-zero/backend-17 normal
terminal records. The owner never calls child admission or collection in this
profile. The unused third envelope image is not admitted.

The [preimplementation contract](contract.md) records scope and forbidden outcomes.
This is a bounded conformance witness, not native help/version, RL01–12 completion,
independent consumer acceptance or a publishable handoff. Separate stdout/stderr
roles, exact delivery and failure evidence remain the next UL-059 work. UL-067
retains a separate child role/admission contract. OpenZFS profiling is paused.

## Qualification

All runs pass on their first attempt, with implementation inputs frozen and
verified against each suite receipt:

- 62 command-runner cases: previous 55 plus seven local cases. Positive requires
  two generations/four reclaims. Skipped close, unexpected launch, stale reference
  and wrong parent status reject at 1201/1202/1203/1200 with zero reclaims.
  Premature completion rejects 100/two reclaims; the unchanged default oracle
  rejects the local witness at 100/four reclaims. No watchdog substitutes for an
  expected rejection. Local terminal inventories contain no child slot 2.
- Nine inherited-launch and six connections cases pass unchanged.
- `zig build test` passes all 98 Python tests, Zig tests and offline pin/workflow
  checks. Rustfmt 1.98.0 edition 2024, Zig 0.16.0 formatting, Python compilation,
  workflow and diff checks pass.
- Build guards reject the local oracle without a native image or with SMP enabled.

`-Dnative-runner-local=true` selects an exact fixture completion oracle; it adds
no syscall, rights or capacity. Default completion still requires six native
reclaims. The local supervisor is 3,408 bytes within the existing 8,192-byte bound.
The owner/frame transfer uses existing synchronous traps and fixed stack buffers;
no new unsafe block, allocator, dependency or concurrency mechanism is introduced.
Kernel cleanup still verifies all admitted workers retired and channel state zero.

`*-results.json` retain commands, tool/SDK pins, all cases, source and artifact
hashes. `artifacts.tar.gz` retains source snapshots, native envelopes, binaries and
logs; duplicate ISO/installed boot copies and kernel.elf are omitted, with their
recorded ISO hashes preserved. `qualification.json` records receipt modification
times explicitly as filesystem observations; the existing harness does not record
per-case timestamps. This remains a traceability limitation, not full draft testing
conformance. Review-input snapshots are inert userland owner documents, not local
normative replacements. No sibling, standards release byte or pin was changed.

Reproduce with the full command in NATIVE-COMMAND-IO, using SDK
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and tools lock
`/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use the same arguments with `--inherited-launch` and `--connections` for regressions.
Independent owner review and matching consumer build/adoption remain open.
