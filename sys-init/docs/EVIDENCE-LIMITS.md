# Evidence coverage and remaining work

## Current delivery priority — decision 0153

Maintainer decision, 2026-10-22: sys-init targets Aether only. Other-OS product
support and Linux/BSD/illumos qualification campaigns are withdrawn, superseding
decision 0153's deferral. Keep useful host tooling, POSIX authoring conventions and
focused checks for changed code. Require fresh native Aether witnesses and actual
independent review for corresponding runtime/release claims. Historical platform
results retain their original scope; retiring requirements does not mark tests run.
Hosted CI remains a development delivery decision, not another runtime target.



Current checkpoint: decision 0142, following the decision 0141 host audit. This
page consolidates current limits; individual decisions and sealed evidence retain
exact implementation/test identities. The native catalog records 3,019 case
outcomes across 50 historical bundles. An offline pass checks those records; it
does not execute 3,019 new target cases or certify a production init.

## What the native audit verifies

| Boundary | Current coverage | Reference |
| --- | --- | --- |
| Catalog and manifests | Strict bounded JSON/fields, pinned bytes, ordinary files, exact bundle membership and sequential end checks | [record reference](NATIVE-EVIDENCE-RECORDS.md), decisions 0126–0132 |
| Consumer and linked receipts | Exact supported fields/types, collection/text bounds, fixed SDK read locations, no recorded command execution | Decisions 0133–0134 and 0137 |
| Retained artifact links | I/O supervisor/native correspondence; worker SDK/libc/tool-lock links; 904 derived input links and worker/envelope correspondence | Decisions 0135–0138 |
| Producer consistency | 40 suite counts and 54 producer/worker dependency links | Decision 0139 |
| Source archives | All 45 archive maps match 8,307 summary inputs, bounded in-memory parsing without extraction | Decision 0140 |
| Producer source maps | 3,420 available source references checked; ten historical metadata omissions allowed only at exact pins/schema/names/digests | [scoped limitation](STANDARDS.md), decision 0141 |

Source-map counts are occurrences across retained snapshots, not unique source
files. Hash correspondence establishes identity within the retained records, not
signer authority, freshness, source authenticity, correct compilation or permission
to execute. Native policy changes still require a fresh consuming target witness.

## Limits that remain

| Limit | Consequence and disposition | Owner/work |
| --- | --- | --- |
| Missing consumer ISO files | The 2,997 init ISO hashes remain recorded structural claims | Maintainer, BG-056; replace evidence only through a new witnessed bundle |
| Missing producer artifacts | At expected paths, 350 of 395 producer envelopes and all producer case serials/ISOs are absent; 45 positive envelopes remain audited | Maintainer, BG-056; no full producer-suite claim |
| Missing direct SDK artifacts | The first I/O receipt's sdk/startup/bad-dup artifacts are unavailable; structural receipt validation cannot repeat inspection | Maintainer, BG-056 |
| Ten source metadata omissions | Two .DS_Store paths in five normalized snapshots remain unverified; no new/repinned bundle inherits the exception | Maintainer, BG-056; revisit on replacement/acceptance |
| Sequential filesystem checks | Not atomic snapshots; restored or sufficiently late changes may evade comparisons; blocking filesystem I/O has no standalone deadline | Maintainer, BG-056; do not widen concurrency guarantees |
| Runtime and provenance claims | Receipt patch/ELF/tool assertions are not repeated execution, provenance or production conformance | Maintainer, relevant native/release work |
| Platform and extended tests | Full checks witnessed on macOS arm64 and pinned Linux arm64; offline Linux reload also witnessed. Physical/SMP Aether and hosted CI remain open; BSD/illumos product requirements are retired | Maintainer, BG-054 |
| Independent and release review | Technical/reader review, manual visual review, assembled-image acceptance and operational support readiness remain pending | Actual reviewers/release owners required |

The maintainer provided security@aethersys.org. Publishing that address does not
prove delivery, response times or a support period. No reviewer sign-off is implied
by automated checks. Current standards releases remain pinned; RC1 is unpublished.

## Prioritized local work

1. **Aggregate source snapshots (BG-056), bounded slice complete:** decision 0143
   adds per-file/total/traversal limits, ordinary-file/component checks, stable read
   identity and membership rechecks. Current-map compatibility and temporary
   malformed/change controls pass; see DEVELOPMENT-CHECKS.md. These checks do not
   provide atomic snapshots or blocking filesystem deadlines.
2. **Aggregate report/error paths (BG-056), scoped slice complete:** decision 0144
   adds atomic replacement and snapshot/report failure records. Decision 0145
   handles output-directory startup and broken pipes. Repeated/fatal signals,
   blocked I/O and crash durability remain explicit limits.
3. **Extended tests (BG-054), local campaign passed:** decisions 0146–0147 pin
   54 cases and eight seeded orders with budgets, cleanup, triage and freshness.
   The local runner completed 432 executions with no skips on macOS arm64.
   No scheduler or hosted provider is configured by this document.
4. **Review and Aether qualification:** secure actual review and required target
   environments before claiming their gates. Keep post-R1 runtime features queued.

These priorities do not reopen completed receipt validation or permit repairs to
immutable historical artifacts. If an absent artifact or reviewer blocks its
claim, record that block and proceed with independent local work.

## Composed-profile addition — decision 0175

[Decision 0175](decisions/0175-init-composed-terminal-consumer.md) supplies 214
fresh ABI-16 sys-init cases and 32 independently replayed profile-boundary cases,
with complete 499-file producer membership. They are separately sealed evidence;
the older catalog's 3019 outcomes do not include them. BG-056 tracks explicit
new-profile/intake-schema audit support. All 359 legacy images are unchanged.
Generated-dependent Terminal is qualified; issued reclaim/Cleaned, sustained
retention, recovery and independent review remain outside this result.


2026-10-20 / decision0191: the first exact ABI29 filesystem owner has producer-
executed native activation/readback/fixed-peer coverage. The new local review
independently checks identities and five complete retained normalized kernel
failure spans. Positive tails omit early admissions/cleanup; raw logs/images were
disposed, so full positive-trace replay is unavailable here. Do not reconstruct
missing raw bytes or call receipt summaries an independent execution. This is a
scoped evidence limit, not a blanket implementation pause or released conformance.

## AF07 consumer checkpoint — 2026-10-21

Decision0193 has complete bounded v2 selected AF07 oracle records for all eight
cases, closing the earlier positive-tail gap for this run only. Four exact wait
substitutions decode losslessly; omitted clock park/timeout events retain only
count/hash summaries. No raw UART, full timer schedule or local media/VM replay
follows. Linked AF07 v3/v5 engine ELF matches despite distinct harness seals/ISOs.
Boot-parent mismatch controls execute the sealed C decoder on this host; native
PPID7 derives from pinned source arithmetic and is not newly measured in a VM.
