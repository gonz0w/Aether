# Exec peer-first termination — 2026-09-11

Both normal peer close/exit and #UD fault cleanup preserve the replacement's live
input/stderr records. The replacement remains committed and parked while the owner
observes the peer outcome. Fault cleanup requires terminal134/kind2 and output EOF;
normal cleanup requires descriptor close requests and terminal64/kind1. Only stdout
is unshared and closes at this point. The owner checks retained commit/freeze
identity, publishes the replacement, verifies input c and confirms its final closes.
Both holder rows must be empty, position3 and exactly three backend close receipts
per generation. Two generations produce six domain reclaims.

All196 connections cases, five launch cases and host tests (99 Python and five Rust
descriptor tests) pass. The premature-close mutant rejects1952 on failed surviving
input I/O. The leaked-holder mutant rejects2091 on incomplete ownership accounting.
Both fail with zero reclaims. Ordered positive terminal records are peer64/kind1 or
134/kind2, source62/kind1, backend17/kind1, in each generation.

## Scope and review

Use the existing holder matrix, descriptor plan, connection-local references,
private channels and backend. A 32-byte peer barrier selects the precise post-commit,
pre-publication ordering. No new service, allocator, authority, kernel interface,
SDK API, dependency or release pin. The peer remains independently admitted; this
is not public fork/execve, full dash acceptance or release readiness. Exact cleanup
of these fixed RAM records does not establish persistent recovery, owner-failure
recovery or faults during partial I/O. Incomplete shared-close receipts and consumer
staging acceptance remain open. Pre-code selection and simplicity assessment are in
NATIVE-SHELL-STARTUP.md; no reader or affected-owner approval is inferred.

## Attempts and evidence

Attempt1 failed to compile the new Rust owner because its commit-state query omitted
the final zero scalar argument (E0061). Connections target execution did not begin;
host and launch passed. Full artifacts, logs and frozen sources are retained in
attempt1. The final query has the required argument count and all selected suites
were rerun on frozen runtime sources. No retained evidence was deleted.

Commands, timings, exact tools and cases are in timing/results files. Reproduce with
the connections/launch commands in NATIVE-CONNECTIONS.md and the recorded SDK/tools
lock. run-sources captures execution inputs; sources additionally captures final
documentation. Both source and target archives are read back against hashes.
change.patch compares the preceding shared-holder packet. compatibility.json checks
all192 prior cases: kernel load segments and entry remain identical, with only
nonloaded .debug_line differences permitted. Changed older exec owner payloads are
identified; other payloads match outside developer entropy bytes. qualification.json
records source/artifact counts and owner size bounds. final-checks.json retains host,
format, workflow, standards and diff checks. collect.py also verifies the preceding
sealed manifest and the four-file simplicity snapshot. manifest.json seals this
packet including the failed attempt. No independent consumer acceptance is claimed.
