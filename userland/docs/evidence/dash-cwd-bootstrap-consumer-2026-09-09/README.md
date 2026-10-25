# UL-007 directory bootstrap rejection consumer — 2026-09-09

PASS: all 323 original native command cases reproduced locally. The
[native receipt](native-results.json) records build flags, tools, artifacts and
results; the [outer receipt](results.json) records exit0 and complete process
cleanup. All 545 source and 4311 SDK hashes remained unchanged. There was one
local native attempt, with no failure or interruption.

[Four independent final serial checks](bootstrap-cases.json) pass against completed
receipt digests: client110/backend17 in both generations, owner100/four reclaims
and no panic. All 323 serial/QEMU logs are retained under cases/. These are scoped
rejection and cleanup results; the complete directory matrix remains open.

## Selected scope

The frozen producer adds four cases to the preceding 319-case directory suite:

| Case suffix | Input | Required native result |
| --- | --- | --- |
| cwd-alias | Directory reference equals stdin reference | Client110/backend17 in both generations; owner100/four reclaims |
| cwd-short | EOF after 16 bytes of final 32-byte directory record | Same rejection and cleanup |
| cwd-version | V2 header received by selected V3 client | Same rejection and cleanup |
| cwd-legacy | V3 header received by selected V2 client | Same rejection and cleanup |

The version senders supply only the header and close their writer. The short
sender closes after the half record. All four must leave the selected startup
state unpublished and emit no client I/O under the original guest/owner assertions.
The V2 client has no V3 directory facade check; this reverse mismatch does not
establish V3 directory-state coverage. The independent secondary check compares
completed serial digests and exact lifecycle records, not a new shell oracle.

## Remaining gates

Only stdin aliasing and one truncation boundary are selected. Stdout/stderr aliasing,
V1/V3 mismatches, queued incompatible bodies, other header/body truncation points,
directory reply corruption/truncation, poison persistence/no further traffic and
teardown, identity/PWD mismatch, and forced getcwd ENOMEM remain unqualified.
The five partial [metadata rows](../../../experiments/dash-native/METADATA.md)
remain open. Private immutable /work and three stat fields remain the directory
scope; no general filesystem, authentication, POSIX conformance or native SDK
default is established. Native-main ENV configuration and actual main/exec/wait/
pipes still gate UL-007/M3; UL-016/063/081 and independent reviews remain open.

## Provenance and reproduction

Producer shell-cwd-bootstrap-2026-09-09 manifest SHA256:
`dd88f0e0d5dbe42bb444ffd555c613b064377da4f296ab1e8f3339e5d3763b19`.
All 12 sealed files were checked before consumption and retention. The retained
producer-packet/ includes sources and receipts; packet-retention.json identifies
the verified target archive omitted from this copy. This producer step reports no
failed/interrupted attempt; predecessor history remains in the preceding local
packet. [Intake](intake.json) confirms unchanged kernel/build and 32 dash objects. The source comparison selects
five changed files: sender, harness and three planning/evidence documents. C decoder,
adapters, kernel/build and imported dash objects are unchanged. The existing bounded
half-record sender is shared with metadata truncation, motivating the full original
323-case regression suite. No local producer/oracle edits or sibling changes.

Run `python3 -B docs/evidence/dash-cwd-bootstrap-consumer-2026-09-09/run.py` on the
recorded Python 3.14.7 host with the pinned dependencies. Build outputs are under
`build/dash-cwd-bootstrap-consumer-epf1wqfq`. The original native receipt captures
compiler flags, target ABI, tool hashes and case artifacts. The existing process
helper uses controlled PATH/LC_ALL/private TMPDIR, an 1800-second outer deadline,
512 MiB stream bound and original guest watchdogs. This reuses the pinned SDK and
32 dash objects; no fresh libc/dash source build, M4 or host kernel-suite claim.
Minimum-interpreter execution and full source review are not inferred.

[Pre-execution review](review.md) records source assessment, bounds, oracles,
cleanup, documentation impact and pending independent technical/reader approval.

Final local quality gate, driver syntax/receipt identity and tracked-document
whitespace checks pass. The quality gate validates pins/inventory structure;
it does not supply the pending independent reviews.
