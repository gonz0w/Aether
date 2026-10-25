# Roadmap

## Session runtime package intake — 2026-10-07

[Verified intake](../docs/evidence/session-sdk-intake-2026-10-07/README.md) closes
byte identity inspection of the selected private ABI24 bundle, not package admission.
Before implementation, userland and pkg-mgr must settle runtime package identity,
layout, source/prebuilt closure, receipt selection and external dependency boundary.
The current standalone aether-musl-sdk transport is not authority to relabel the
whole runtime bundle. Keep its unchanged 231-file musl payload and existing pins.
Full native tools, filesystem-backed loading, native target admission and durable
same-disk reboot remain acceptance gates under the existing ISO test card.


## Simplicity follow-up — prospective, 2026-09-07

[Local adoption](../docs/STANDARDS.md) adds no runtime/refactoring milestone. Apply
SE-01–SE-05 within the next real change; do not add machinery for these entries
before their delivery trigger. pkg-mgr maintainer owns triage and review.

| Finding | Delivery impact / risk / next scoped action |
| --- | --- |
| SIMP-01: mk/binary.sh selects host versus SDK role at dispatch, descriptor construction, target validation, bound metadata and result delivery | Before adding any legitimate native-program admission, review these existing branch points together: another role risks inconsistent identity or success semantics. Keep the tested host/SDK separation; compare a direct explicit branch with shared helpers using actual repeated policy. No defect is diagnosed and no general profile/plugin framework or split by file length is authorized. |
| SIMP-02: mk/sdk-rebuild-plan.sh bounded() exports bytes through shell scope; snapshot() also reuses selected, output, count and digest | Lower priority, next substantive planner edit: make variable ownership and call-order assumptions explicit and assess whether narrowly named variables clarify the coherent operation. Preserve bounds, checked tool statuses, exact TSV, failure cleanup and existing controls. No current failure, language migration or speculative extraction is claimed. |

Native ISO/package prerequisites remain the delivery priority. Neither item opens
SDK apply, installed-payload deletion, service authority or post-R1 features.


## Standards candidate handoff — ADP-04, 2026-09-06

See [the clause/compatibility review](../docs/STANDARDS-RC1-REVIEW.md) and retained evidence.
These are local work IDs, not additional shared requirements or post-R1 feature work.

| Work ID | Owner / status | Acceptance |
| --- | --- | --- |
| ADP04-01 | pkg-mgr / complete | Reconcile historical lint counts with current 38-file check and three scoped suppressions; retain candidate identities and checks without changing pins. |
| ADP04-02 | pkg-mgr / partial: 68 enforced critical-case groups and C17 host syntax audit | Complete case-level parser/trust/transaction and public-surface mappings; review resource/path/cancellation bounds, Python minimum-version execution, first-party zpipe C diagnostics/style and declared shell/make support. Preserve upstream exclusions. |
| ADP04-03 | pkg-mgr maintainer / partial: five-full-suite campaign and relocated source pass; runner handoff prepared, deployment open | Define extended workloads, seeds, budgets, cleanup, triage, metrics and maximum evidence age; distinguish planned schedules from actual deployed runs. |
| ADP04-04 | pkg-mgr consuming owning-project contracts / open | Reconcile exact native shell/tool/storage and PD/CT/MR profiles with the AETHER-RELEASE workload; obtain target package/persistence evidence and separately scoped removal/trust decisions. Do not implement missing sibling mechanisms here. |
| ADP04-05 | pkg-mgr, Cam and representative reader / partial: public CLI map and reader procedure defined | Complete version-bound documentation inventory, semantics/anchors and independent onboarding/recovery walkthroughs; verify packaged Aether manual lookup and any included diagrams. |
| ADP04-06 | Cam; coordinate Aether-dist / partial: security@aethersys.org supplied | Record actual review, security channel/triage owner, release provenance/license closure and scoped exceptions. Adopt only a published immutable standard through explicit pins; publication remains separate. |

## OC-H3 declared closure — 2026-09-06

The [host-review profile](../docs/ORIGINS-CLOSURE.md) defines local release-map,
selection/name mapping, synthetic SDK/target and evidence records. The read-only
consumer verifies a complete declared two-package set and every referenced object.
44 focused cases pass, including mapping/reference/profile conflicts, missing
object classes, graph/resource limits, multiple roots and unchanged state.
[Evidence](../docs/evidence/origins-closure-2026-09-06/README.md) preserves original
attempts. The final full host gate passes, including all sixteen shell fixtures
and all three origins suites. No source execution or fresh trust.

These are concrete review schemas, not origins/userland/shared acceptance or real
SDK completeness. Next: obtain owner disposition of these exact fields and a real
base candidate's SDK/profile/license/admission closure, then qualify that handoff.
Trust/time/recovery and native shell/filesystem remain separate gates. No sibling
implementation or shared immutable pin changed.

## OC-H2 inert source inspection — 2026-09-06

The [host inspector](../docs/ORIGINS-SOURCE-INSPECTION.md) passes 96 focused cases
plus help/version/usage checks. It validates pinned canonical source-record bytes,
bounds and field relationships as inert data. Every report says inspection-only,
unresolved closure/profiles and eligibility not-evaluated. The existing shell/make
runtime and source verifier remain unchanged; Python is development tooling only.

OC-01–06 are resolved for inspection scope through preserved identities/paths,
declared-role checks, explicit size reporting and no materialization/opaque closure
claims. General producer/source-profile adoption and OC-07–08 remain pending.
[Evidence](../docs/evidence/origins-source-inspection-2026-09-06/README.md) retains
all attempts. The full sh tests/check.sh gate passes, including all sixteen shell
fixtures, both origins suites and required standards/lint checks.

Next: agree the release-map/SDK/target and local package-mapping formats with origins
and userland, then test a complete selected closure. No actual base package, fresh
trust, native filesystem or source execution is accepted by this checkpoint.

## OC-H1 source-byte handoff — 2026-09-06

The [pinned offline consumer fixture](../docs/ORIGINS-CONSUMER.md) passes 13 host
cases: real exporter/verifier round trip and retry, exact corruption/size failures,
failed partial/complete export gating, missing tools, symlink/FIFO/path denial and
identical put. Private package sentinel and stored object identities remain unchanged.
[Evidence](../docs/evidence/origins-byte-handoff-2026-09-06/README.md) retains the
initial setup failure and successful focused/integrated runs. The full host suite
passes, including all sixteen shell fixture scripts and required lint/standards checks.
The test is part of sh tests/check.sh. No runtime package behavior, sibling,
shared pin, base admission or native authority changed.

This closes OC-H1 byte-only consumption, not OR-04 or fresh source eligibility.
Next source work: resolve OC-01–06 identity/path/role/closure contracts and implement
bounded inert source-record inspection; OC-07–08 trusted-time/durable-recovery and
profile decisions remain separate. Native shell/filesystem blockers are unchanged.

## Origins source-consumer review — 2026-09-06

[Consumer review](../docs/ORIGINS-CONSUMER.md) records eight contract findings and
the proposed trust/time/recovery and private-cache boundaries. No source adapter,
base admission, shared acceptance or sibling modification is claimed. Existing
formats and native blockers remain unchanged.

Next local work: OC-H1, a pinned offline byte-transfer fixture feeding the existing
source verifier without recipe execution or fresh eligibility. OR-04 package
admission separately needs source-map/SDK/target/identity agreement, userland
selection/license/closure evidence and durable consumer trust authority.
Validation is retained in docs/evidence/origins-consumer-review-2026-09-06.

## R1 dependency checkpoint — 2026-09-06

The accepted 53-case package transport remains the baseline. Current userland
tracking reports 66 native cases, but native local outcomes still await the
[Aether owner packet](../../userland/docs/RUNNER-OWNER-HANDOFF.md): output
roles, separate bounded stdout/stderr, no-child lifecycle, independent admission
observations and unknown-delivery ownership. This packet is prepared, not owner
acceptance or an instruction to edit/send to the sibling. No pin was advanced.

Aether's latest 8-MiB native backing qualification is runtime capacity, not a
filesystem service, namespace or durable package-publication API. Its next work
is larger static executable admission; native threading/engine/service composition
and shell/package assembly remain open. The package implementation is therefore
blocked on concrete native shell/tools, filesystem and artifact-identity contracts.

Next owner work: Aether R1-02/03/04 and its UP-02 review of userland's packet;
userland independently qualifies the returned output/lifecycle bundle and actual
shell/tools. Package work resumes on those concrete inputs with native admission
and publication changes. Do not substitute another isolated transport replay for
R1 install/reboot/verify acceptance. No runtime, selector, shared pin or sibling
source changed in this read-only checkpoint.

## Native command transport accepted — 2026-09-06

The dedicated consumer reconstructed and booted all 53 pinned command cases from
verified package staging: 22 successes and 31 exact expected rejections. Envelope/
base bytes, startup, terminal kind/status, cleanup and uncertainty outcomes pass.
[Evidence](../docs/evidence/native-command-consumer-2026-09-06/README.md) retains all
case receipts/logs and the pre-output tool-path correction. All sixteen host
fixtures and scoped oracle/preflight checks pass. Existing selectors/pins and
frozen archive are unchanged; no sibling implementation was edited.

This closes the selected command transport consumption step, superseding the
preflight-only and reconstruction-pending notes below. It does not run bin/pkg-mgr
on Aether or provide durable installation. Next: delivered native shell/tool and
filesystem/identity contracts for R1 package admission/publication; separately
consume owner extensions for local help/error outcomes when qualified. No new
blanket kernel API request follows from the accepted runner transport.

## Command consumer preflight implemented — 2026-09-06

The dedicated read-only command handoff preflight validates exact schema/modes,
53-case identity/polarity, artifact inventory and image/envelope/log/client hashes.
[Evidence](../docs/evidence/command-preflight-2026-09-06/README.md) records the retained
owner invocation. Negative fixtures cover malformed handoffs and path/hash errors.
No receipt command runs; no staging or native boot is claimed.

Next: freeze producer tool/dependency closure, reconstruct package-staged images
and add exact boot oracles. Native admission/storage remain separate R1 gates.
Existing transport selectors, package runtime, pins and frozen archive are unchanged.

## Mapped runner handoff verified — 2026-09-06

[Read-only review](../docs/evidence/runner-mapped-handoff-review-2026-09-06/README.md)
verifies NB-03/04, startup, result and uncertainty evidence manifests, all 62 latest
combined/legacy ISO-log pairs and client/artifact identities. Ten mapped positives
and six uncertainty rejects have exact terminal-marker checks. Older statements
that NB-03/04 or all parser/startup implementation are pending are superseded.

Next bounded work: a separately named package command-runner transport profile,
exact case-set/identity rejection tests and package-stage consuming boots. The
current receipt still excludes complete public CLI acceptance; local outcomes and
remaining controls stay open. Native shell, filesystem, admission and durability
remain separate R1 gates. No runtime, selector, pin, archive or sibling changes.

## R1 prerequisite source audit — 2026-09-06

The [source-derived workload requirements](../docs/AETHER-RELEASE.md#source-derived-r1-prerequisites--2026-09-06)
now enumerate the existing import/inspection tool behaviors, root ownership/mode
checks, temporary storage, shell semantics and permission/hash-provider alternatives.
Two implementation seams are explicit: host-only admission is enforced on export
and import, and current publication has no durability barriers. Neither can be
closed by merely running the shell on Aether or relabeling a binary.

Next: selected native artifact identities and storage ordering/error contracts,
then narrow package adaptations with wrong-runtime rejection and data-preservation
oracles. Userland NB-03/04 and UL-059 remain pending at inspection. No runtime,
shared policy, pins, frozen archive or sibling source changed; no new native test.

## R1 native package workload — 2026-09-06

Aether now targets a persistent boot-to-shell system under R1. The package-side
[workload brief](../docs/AETHER-RELEASE.md#r1-boot-to-shell-workload-reconciliation--2026-09-06)
selects the existing bytecount source for local-bundle import/list/verify/execution
and same-disk reboot verification. It identifies native target metadata, shell/
tools, filesystem-backed execution, storage semantics and sys-init composition
as dependencies. No host target relabeling or substitute package core is proposed.

Userland has no newer completed NB-03/04 or UL-059 evidence at inspection. These
remain runner gates; the composed R1 path adds concrete shell/storage work beyond
them. R1 requests removal, but pkg-mgr's explicit no-deletion scope is unchanged:
removal requires a separately opened contract, and R1 cannot close without it.
Next: reconcile delivered native owner contracts against the documented workload.
Documentation only; no runtime, native test, pin, frozen artifact or sibling edits.

## Native reply evidence refresh — 2026-09-06

Userland NB-02 now has verified native uncertainty controls: lost/malformed read,
lost close and a disabled-poison mutation. Read-only package review verifies
1,284 owner files, 26 ISO/serial pairs, four exact negative marker sets and the
unchanged adapter. [Evidence](../docs/evidence/runner-native-replies-review-2026-09-06/README.md).
The scoped local no-replay/consuming-close boundary is evidenced; remote recovery
is not. This supersedes the earlier NB-02 preparation-only checkpoint.

Next: NB-03 launch framing, NB-04 abnormal child and UL-059 public consumer.
No package runtime, selector, pin, frozen archive or sibling code changed. Native
shell/make/storage and Cam review remain separate Aether release gates.

## Native bootstrap evidence refresh — 2026-09-06

Userland NB-01 now has verified native rejection evidence: malformed reference,
descriptor and rights controls plus an early-publication mutant. Package read-only
review verified 1,117 owner files, 22 ISO/serial pairs and the four exact negative
marker sets. [Evidence](../docs/evidence/runner-native-bootstrap-review-2026-09-06/README.md).
This closes the scoped NB-01 evidence hold; it does not establish remote cleanup.

Next: completed NB-02–04 and UL-059 public consumer handoff. NB-02 preparation has
no completed receipt yet. No package runtime, selector, pin, frozen archive or
sibling implementation changed. Native shell/make/storage and Cam review remain
separate release gates; Aether is the only release target.

## Runner transfer/reply evidence refresh — 2026-09-06

New owner UL-058 evidence closes the scoped CB-08–13 host hold: 53 UBSan scenarios
and two semantic mutation rejections pass. Package read-only review verifies all
810 retained files and 55 outcome entries; the adapter matches the earlier
bootstrap-corrected native input. [Evidence](../docs/evidence/runner-transfer-review-2026-09-06/README.md)
records exact identities and keeps the initial mutation compile failure separate.

Native NB-01–04 and UL-059 public carrier/parser/consumer remain open. This is not
a new native run or a package consumer handoff. No pkg-mgr runtime/harness selector,
shared pin, immutable artifact or sibling implementation changed. Next: consume
the completed owner native/public handoff when delivered; Aether's combined
mechanism is ready and does not need a new blanket kernel API request. Cam's
reviews and eventual native shell/make/storage acceptance remain separate.

## Runner handoff evidence review — 2026-09-06

The current userland UL-058 bootstrap fix has 22 UBSan host scenarios, two mutation
rejections and nine legacy native regression passes. Package read-only review
verified 858 owner evidence files, 293 pinned combined-producer source members,
ten native artifacts, nine images and five changed client ELFs. [Review](../docs/evidence/runner-handoff-review-2026-09-06/README.md)
records exact inputs; no native boots or producer commands were rerun.

The old UL-057-pending note is superseded for the finite legacy runner. Public
UL-059 carrier/parser/combined consumer and remaining UL-058 CB-08–13/NB-01–04
controls are still open. The owner receipt is not a supported pkg-mgr harness
selector and must not be passed as the older file-I/O profile. [Acceptance conditions](../docs/NATIVE-COMMAND-CONSUMPTION.md)
now name the required next handoff. Aether's combined mechanism is ready; no blanket
kernel blocker is identified. Next: completed userland public-consumer evidence,
then package-owned validation/staging/boot consumption. Cam's review and native
shell/make/storage acceptance remain separate. No runtime, pin, immutable archive
or sibling implementation changed; Aether remains the only release target.

## Aether-only release scope — 2026-09-06

Maintainer instruction: skip macOS as a release target; work only toward Aether.
Cam will perform reviews. [Active release acceptance](../docs/AETHER-RELEASE.md)
supersedes the old host-preview gates. No retained Apple installer or independent
macOS builder is required. The frozen host-tested archive and its audits remain
valid development evidence, not a native package-manager release. No native
runtime or storage acceptance is inferred, and no review is marked complete.

Current owner tracking keeps userland UL-058/UL-059 boundary/public-runner work
active; Aether's combined runner mechanism is ready for a concrete consumer.
Next: Cam's review and a focused comparison of that owner handoff with pkg-mgr's
command-consumption contract. Native shell/make and package storage/publication
still need executable acceptance. Security contact/triage owner remains unspecified.
No runtime, immutable archive, standard pin or sibling repository was changed.
The just-assembled macOS-oriented private review kit is superseded for release
instructions; use the Aether review scope instead. Nothing was published.

## Frozen candidate repetition checkpoint — 2026-09-06

Two additional transaction-fixture runs pass on fresh extractions of archive
9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043,
each under a 300-second process-group watchdog with all eleven required markers.
Selected file bytes/modes, source manifest and archive digest remain unchanged.
This gives three transaction-fixture witnesses on this exact candidate including
its original full suite; older-archive repetitions are not counted. [Evidence](../docs/evidence/frozen-candidate-repeats-2026-09-06/README.md)
retains individual runs and a concrete independent-review handoff. No runtime or
candidate changes were needed; freeze remains except demonstrated release blockers.
Next: actual independent technical/content, reader and captured clean-builder
reviews. No reviewers are assigned or approvals claimed. A monitored security
contact and publication decision also remain open. Repetition is not soak,
physical full-storage, power-loss, concurrency or broad target qualification.

## Publication/cleanup audit and freeze — 2026-09-06

The frozen candidate 9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043
passes 27 additional before/after publication and cleanup failure cases across
state init/register, binary export/import/recovery and replacement prepare/finish.
Actual records/payloads distinguish committed, pending and uncommitted outcomes;
explicit recovery and repeated finish pass. No additional runtime defect was
demonstrated and no runtime/candidate bytes changed. [Evidence](../docs/evidence/publication-audit-2026-09-06/README.md)
retains a corrected fixture-mode mistake, all calls and exact before/after states.
The 187 selected bytes/modes and retained archive digest remain unchanged.
Freeze runtime changes except demonstrated release blockers. Next: bounded repeated
transaction qualification of this candidate, then independent content/build/reader
reviews. Captured clean-builder setup and a monitored security contact remain open.
This is not full-storage, power-loss, concurrency or complete security approval.

## Binary reader review and candidate qualification — 2026-09-06

HR-02/HR-04 fixes failed metadata/identity readers being accepted when they print
plausible values. Checked field, uname and record-version assignments reject before
export/import publication. Thirteen controls pass, with prior descriptor/preflight
hash fixes included in refreshed archive
9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043.
All sixteen fixtures, three standards gates, lint, host preflight and required
manual/bytecount checks pass from the extracted 187-file archive. Repeated assembly
matches; selected bytes/modes, manifest and archive remain unchanged after tests.
[Evidence/artifact](../docs/evidence/binary-reader-faults-2026-09-06/README.md)
retains the false-success regression, initial lint findings and six changed inputs
with no added/removed files. Next: broader failure qualification and independent
content/build/reader review. Captured builder setup and a monitored security contact
remain open. No signing, tagging, upload, durability or independent approval claim.

## Preflight report hash checkpoint — 2026-09-06

HR-02/HR-04 fixes preflight returning success after a final record hash fails.
Old/new report digests are now checked before the header is emitted. Four controls
cover empty and valid-digest output with failed helper status; all reject without
report bytes or target file/hash/mode changes. The exact successful report header,
all sixteen fixtures, three standards gates and scoped/whole-shell lint pass.
[Evidence](../docs/evidence/preflight-receipt-faults-2026-09-06/README.md) retains
the false-success regression and exact source/test identities. No successful
format, pin or dependency change. Continue the remaining reader/boundary review
before refreshing the candidate with accumulated fixes. Captured builder setup,
independent reviews and a monitored security contact remain open.

## Binary descriptor hash checkpoint — 2026-09-06

HR-02/HR-04 fixes binary export reporting success after a descriptor hash helper
fails. All four descriptor table hashes are now checked explicitly; the exported
receipt digest is computed before publication. Nine export/import fault controls
reject without receipts or publication and preserve target bytes/modes. Exact
successful export receipts and all sixteen fixtures, three standards gates and
scoped/whole-shell lint pass. [Evidence](../docs/evidence/binary-descriptor-faults-2026-09-06/README.md)
retains the pre-fix false-success regression and exact source/test identities.
No successful format, pin or dependency change. The prior candidate predates this
correction. Continue the remaining boundary review before the next candidate
refresh; captured builder setup, independent reviews and a monitored security
contact remain open. No publication or durability claim.

## Candidate intent-fix qualification — 2026-09-06

The refreshed 187-file archive includes the replacement intent hash correction.
Archive 28d7b300bf8e9f68b101ae2805cdca5fb3cde098e1211c2e50f0765da0124428
passes repeated assembly/extraction, all sixteen fixtures, all three standards
gates, whole-shell lint, host preflight and required manual/bytecount checks from
the extracted tree. Ten intent-hash failure controls pass. Selected bytes/modes,
manifest and retained archive are unchanged after testing. [Evidence/artifact](../docs/evidence/candidate-intent-refresh-2026-09-06/README.md)
records six changed inputs with no added/removed files. This candidate has one
transaction-fixture run; previous-archive repetitions are not transferred. Next:
broader boundary/failure qualification and independent content/build/reader review.
Captured builder setup and the monitored security contact remain open. Nothing
has been tagged, signed or uploaded.

## Replacement intent hash checkpoint — 2026-09-06

HR-02/HR-04 fixes failed hash helpers being hidden by successful printf during
replacement intent construction. Preparation could previously return a prepared
receipt containing an incomplete intent. Checked digest assignments now stop
before publication; ten prepare/finish hash-failure controls preserve target
files/modes and emit no receipt. All sixteen fixtures, three standards gates and
scoped/whole-shell lint pass. [Evidence](../docs/evidence/replacement-intent-faults-2026-09-06/README.md)
retains the reproduced false-success regression and exact inputs. No successful
format or standards pin change. Next: refresh and qualify the public candidate;
its previous archive predates this correction. Captured builder setup, broader
failure review, independent reviews and the security contact remain open.

## Host acquisition checkpoint — 2026-09-06

The [local acquisition audit](../docs/evidence/host-acquisition-2026-09-06/README.md)
records 15 package/version identities, 13 available receipts and two missing old
dependency receipt versions. One cached minisign bottle was retained and matched
against local manifest metadata; this is not publisher authentication. The
maintainer confirmed that the original Apple installers/VM image were not retained.
HR-06 now requires a newly captured builder and fresh independent qualification;
the existing candidate results remain valid for their observed host. See the
[setup acceptance plan](../docs/HOST-SETUP.md). Broader boundary/failure review can
continue locally. Independent content/reader review and a monitored security
contact also remain outstanding. No runtime or candidate archive change.

## Refreshed candidate qualification — 2026-09-06

The 187-file public candidate now includes all three boundary fixes. Archive
4530c8176b496003530a7ec8a306a5da6a0197550f7f7e0a32555d0163ba4843 passes
repeat assembly/extraction, the full sixteen-fixture suite, all three standards
gates, host preflight and required manual/bytecount checks from its extracted tree.
Two extra watchdog-controlled transaction runs also pass (three total including
the suite), with complete markers and unchanged selected bytes/modes afterward.
[Evidence and retained artifact](../docs/evidence/candidate-refresh-2026-09-06/README.md)
identify the 13 changed files, tool identities, raw logs and individual run results.
No publication/signing/tagging. Next: pinned tool acquisition/setup, broader
boundary/failure qualification and independent content/build/reader review. The
actual monitored security contact remains pending. Three fresh-root transaction
runs are bounded repetition, not soak, physical full-storage or durability proof.

## Record comparison error checkpoint — 2026-09-06

HR-02 fixes preflight/prepare/finish treating cmp errors as ordinary differences.
Branching comparisons now distinguish equal (0), different (1) and errors (>1),
rejecting errors before success reports or target mutation. Six injected errors
(statuses 2 and 73) pass with unchanged file/hash/mode snapshots; all sixteen
fixtures, three standards gates and scoped/whole-shell lint pass.
[Evidence](../docs/evidence/record-compare-faults-2026-09-06/README.md) preserves the
pre-fix false-success assertion, prior implementations and exact runtime inputs.
No format, pin or successful-output change. Next: refresh and qualify the public
candidate with the accumulated boundary fixes. Pinned setup, broader failure review,
independent reviews and the monitored security contact remain outstanding.

## Preflight pipeline failure checkpoint — 2026-09-06

HR-02 fixes comparison/observation pipelines that hid failed producers behind a
successful sort or reader. Steps now complete separately before report emission.
Twelve empty/partial-output producer/sort faults reject without reports or target
file/hash/mode changes. Existing successful and conflicting comparisons, all sixteen
fixtures, three pinned standards gates and scoped lint pass.
[Evidence](../docs/evidence/preflight-pipeline-faults-2026-09-06/README.md) retains the
pre-fix false-success regression and exact inputs. No format, pin, successful report
or runtime dependency change. Next: remaining boundary review and refreshed public
candidate qualification. Full-storage/durability, pinned setup, independent reviews
and the monitored security contact remain separate outstanding gates.

## Snapshot hash-tool failure checkpoint — 2026-09-06

HR-02 fixes snapshot_digest losing the failed hash-tool exit status after an if
compound. The existing hash-unavailable result now distinguishes infrastructure
failure from mismatched content. Eight injected self/index hash-tool faults reject
before signing, preserve inputs and clean temporary files; a signer-reachability
control passes. All sixteen fixtures, three standards gates and scoped lint pass.
[Evidence](../docs/evidence/snapshot-hash-faults-2026-09-06/README.md) preserves the
reproduced failure and initial lint-gate failure before correction. No trust policy,
format or successful output change. Next: remaining boundary/failure qualification
and refreshed public-candidate assembly/tests; the prior archive predates this fix.
Independent review, pinned setup and monitored security contact remain outstanding.

## Public source candidate checkpoint — 2026-09-06

An explicit 187-file [allowlist/assembler](../docs/PUBLIC-SOURCE.md) replaces the
broad development snapshot for public-candidate preparation. The README overlay
and 81 marked omitted development references form a recorded documentation edition;
159 non-Markdown/vendor files remain byte-identical. Repeated archive/extraction
checks, all sixteen fixtures, three standards gates, host setup and required
manual/bytecount checks pass from the extracted candidate. Six rejection controls
pass; selected source bytes/modes remain unchanged after testing.
[Evidence](../docs/evidence/public-source-2026-09-06/README.md) binds the exact archive
and records the initial control-fixture path-alias correction. Nothing published.
Next: remaining boundary/failure qualification, pinned acquisition/setup and real
independent content/build/reader review. The monitored security contact remains
pending. Later checkpoint documentation is separate from the tested candidate hash.

## Preview content and setup review — 2026-09-06

[Content/notice scope](../docs/RELEASE-CONTENTS.md) separates host-preview inputs,
unchanged licensed bytecount, immutable standards and optional development recipes
from excluded history/research. Bytecount source/license match recorded origin pins.
The [host preflight](../docs/HOST-SETUP.md) records actual Apple-selected compiler,
make and SDK metadata in addition to the shared command shims. Missing tools and
wrong ShellCheck controls block correctly; no runtime package behavior changed.
[Evidence](../docs/evidence/release-inputs-2026-09-06/README.md) retains identities
and controls. Next: exact public allowlist and documentation closure, then extracted
candidate checks, pinned acquisition/setup and independent review. The actual
monitored security contact is requested and still pending; no publication approval.

## Development source closure checkpoint — 2026-09-06

HR-06 now has a [development snapshot tool](../docs/SOURCE-SNAPSHOT.md): 3,207 files,
identical repeated archive bytes, and host-tar extraction matching exact contents
and modes. All sixteen fixtures, three pinned standards checks, required manual
renders/lookup and the bytecount lifecycle pass from the relocated extracted tree.
Eight corruption/omission controls reject; selected source inputs remain unchanged.
[Evidence](../docs/evidence/source-snapshot-2026-09-06/README.md) binds these results
to the tested archive, including the initial legacy-tar path-length failure.
Next: select the public source/license inventory, qualify setup and remaining
release gates, then obtain independent build/reader review. The development snapshot
includes historical evidence and optional development recipes; it is not a public
release candidate or redistribution approval. No native package readiness claim.

## Binary-format manual checkpoint — 2026-09-06

HR-05 adds pkg-binary(5), documenting exact bundle layout, descriptor/target keys,
permissions, dependencies and recovery limits. All three manuals pass strict lint,
HTML and 60/80-column rendering and staged host lookup. A real bytecount lifecycle
passes; its exported bundle matches the documented inventory, ordered keys and four
digest bindings. A changed descriptor key is rejected by the coverage check.
[Evidence](../docs/evidence/binary-manual-2026-09-06/README.md) retains successful and
failed checker attempts. Next: assemble and qualify a clean host candidate, complete
remaining release gates and obtain independent build/reader review. No release or
native package-manager readiness is claimed.

## Package-state manual checkpoint — 2026-09-06

HR-05 adds pkg-state(5), including v1/v2 rows, all 19 build evidence keys, identifiers,
paths, permissions, world and recovery limits. Both manuals pass lint and 60/80-column
and HTML rendering; world examples and duplicate-root rejection pass. Host man lookup
finds/displays both pages from a private staged layout. Schema drift, an unchecked
manual and missing required lookup tool reject.
[Evidence](../docs/evidence/state-manual-2026-09-06/README.md) records the checks.
Binary-format manual, real release
packaging and independent reader qualification remain open.


## CLI manual checkpoint — 2026-09-06

HR-05 adds pkg-mgr(1), covering all 13 commands and seven options, with required
sections and existing exit/recovery limits. Curated examples caught and corrected
an external-temp-root registration example in docs/CLI.md. Mandoc lint, HTML and
60/80-column rendering and executable examples pass; missing coverage/required-tool
controls reject. [Evidence](../docs/evidence/cli-manual-2026-09-06/README.md).
Format manuals, actual packaged lookup and independent reader/technical review
remain pending, along with broader failure/resource and clean candidate qualification.


## Whole-shell lint gate — 2026-09-06

HR-02 resolves the remaining CLI/state/build/test lint findings. All 38 active shell
files pass configured ShellCheck 0.11.0; three narrow false-positive exceptions are
recorded in [development](../docs/DEVELOPMENT.md). No broad suppression baseline.
Normal checks now require whole-shell lint and fail on missing/wrong-version tooling.
All sixteen fixtures and three standards checks pass, plus the real bytecount
build/register/export/import workflow. Three lint-tool rejection controls pass.
[Evidence](../docs/evidence/shell-review-2026-09-06/README.md) retains frozen inputs,
logs and scoped exceptions. Next: broader bounded failure/resource
coverage and manuals, followed by independent clean candidate/reader qualification.
Lint success is not a completed security, portability or release review.


## Trust metadata lint review — 2026-09-06

HR-02 makes the metadata helper lint-clean without suppressions. Unused diagnostic
path arguments and unused descriptive-field storage are removed; required/nonempty/
duplicate checks and trust scope stay unchanged. All 71 source-corpus cases have
identical status/stdout/stderr before and after the refactor. Whole-repository lint
findings now number 62. All sixteen fixtures and three standards checks pass; 43
additional snapshot controls preserve exact before/after results and required-field
validation. [Evidence](../docs/evidence/trust-parser-review-2026-09-06/README.md)
retains the previous helper, differential controls and full-suite log.
Next: remaining CLI/state/build lint review, then broader bounded failure testing,
manuals and clean host-release qualification. Freshness/key policy is still unopened.


## Source metadata corpus — 2026-09-06

HR-04 adds 71 deterministic source-record cases (seed 20260906) through the normal
source fixture. Exact diagnostics/status, key constraints, permutation acceptance,
inert URI text and target-byte preservation are checked with five-second child
deadlines. All sixteen fixtures and three standards checks pass with this corpus.
[Evidence](../docs/evidence/source-corpus-2026-09-06/README.md) retains both attempts
and the full-suite witness. An initial
incorrect test-label expectation is retained, then corrected to the existing contract.
No parser runtime changes or new input-size limit. Remaining work: parser/trust lint,
broader malformed-input/resource coverage, manuals and clean host-release qualification.


## Replacement failure review — 2026-09-06

HR-02 reviews replacement validation guards without changing their predicates,
error text or authority. The replacement helper and binary fixture pass ShellCheck
0.11.0 without suppressions. HR-04 adds deterministic partial-record-copy and
record-rename failure controls, with preserved old records/payloads and distinct
blocked-versus-retry behavior. See [the contract](../docs/REPLACEMENT-POLICY.md).
All sixteen fixtures, three standards checks and both injected failure cases pass.
[Evidence](../docs/evidence/host-replacement-faults-2026-09-06/README.md) binds the
frozen inputs and full log. Remaining shell diagnostics: 98; no suppressions added.
Further parser/trust lint review, bounded fuzz/repetition, manuals and clean release
qualification remain on the host release plan. No real full-disk or durability claim.


## Experimental host release preparation

Active priority is [the host release plan](../docs/HOST-RELEASE.md), HR-01–HR-08.
The initial scope is macOS arm64 private-root workflows; broader hosts and native
installation are not promised. HR-02 found and corrected a source-rejection test's
ineffective negated grep; touched shell files must pass the scoped lint gate.
HR-03 adds an owned-process-group 600-second suite watchdog and executable controls.
Next: complete parser/transaction lint triage and bounded failure exploration, then
manuals and a clean candidate/independent witness. Native harness extensions are
secondary to this release scope. Publication/contact/reader review remain pending.


## Standards process review — 2026-09-05

Updated Aether-standards drafts reviewed; three released pins unchanged. Contributor
instructions, subsystem coverage inventory, source syntax/local-link gate and explicit
changed-shell lint/drift commands are in place. See [development](../docs/DEVELOPMENT.md)
and [review evidence](../docs/evidence/standards-process-2026-09-05/README.md).
Existing lint findings, manuals/reader review, extended runners and release/target
coverage remain explicit migration gates. No full draft conformance or CI deployment
is claimed. Apply this process before returning to the native command harness;
UL-057/matching producer acceptance remains the next runtime input.


## Bytecount host package checkpoint — 2026-09-05

UL-056 prepared the real command, host controls and native object, but no accepted
native command-runner bundle was present. Package work proceeded on the host:
a pinned bytecount 0.1 shell/make recipe builds, stages its BSD license, registers,
exports/imports and runs successfully in retained private roots. Eleven exact
output/status cases pass at build/stage/import boundaries; same-size source
corruption rejects before extraction. Source/license come from the verified
75-file userland preparation bundle. All three pinned standards checks and sixteen
active fixtures pass on macOS. [Recipe](../docs/BYTECOUNT-PACKAGE.md) and
[evidence](../docs/evidence/bytecount-package-2026-09-05/README.md).

This is host-targeted package lifecycle, not native command or base-set acceptance.
No sibling implementation or shared pin changed. Next native input is UL-057's
independent runner/two-binding adapter after a completed matching Aether producer
archive/report. Preserve broker-side exact output verification versus runner EOF;
old one-reference receipts cannot substitute for the two-record command contract.
No new kernel capacity is required by the proposal, but implementation and consuming
acceptance are still missing. Native shell, policy composition and release trust
remain separate. Other historical fixture/native counts below retain their scope.

## General-size shared libc I/O checkpoint — 2026-09-05

UL-054's extension review and UL-055's final independent consumer are delivered.
The explicit userland-fileio-libc selector consumes ten cases over unchanged
ABI-9 connections transport. All ten package-staged/rebuilt QEMU outcomes pass,
including short I/O/EOF, capacity, independent complete storage readback and exact
fault controls. Six malformed input controls reject before output creation. All
three standards checks and sixteen package fixtures pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-fileio-libc-transport-2026-09-05/README.md).

Each libc call makes one bounded transfer with broker-owned position. The owner
supplies complete backend readback and final-close probes; uncertain replies retain
poison/no replay rather than recovery claims. Only the final corrected dropped-close
run is accepted. No receipt, runtime transport, sibling source, ABI or shared pin
changed. Next: UL-056's CR-01 review and concrete bytecount/stdin/stdout/startup
handoff. The two-byte limitation is closed for this separate profile, but a single
volatile file reference does not establish a real command runner or native shell.
Two-record admission, process/pipe/TTY, policy composition and release trust remain
separate. Earlier checkpoints retain their historical scope.

## Inherited musl consumer checkpoint — 2026-09-05

UL-053 is package-consumed from its final source run, including connection-wide
poison and outgoing-frame checks. The explicit userland-inherited-libc selector
uses unchanged ABI-9 connections transport. All fourteen QEMU outcomes pass:
four successful admission/lifecycle scenarios and ten exact workload rejections.
Six malformed input controls reject before publication. All three standards
checks and sixteen package fixtures pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-inherited-libc-transport-2026-09-05/README.md).

The new inherited binding owns no local position; actual musl read/close reaches
broker-owned shared state. Lost/corrupt replies poison all connection helpers;
failed workloads do not claim remote cleanup or replay safety. No runtime transport,
receipt, sibling implementation, native ABI or standards pin changed.
Next: UL-054's concrete general-size shared-read/EOF owner handoff and independent
workload. Exactly-two-byte reads do not serve general applications, FILE buffering
or the proposed useful bytecount command. Native shell, process/pipe/TTY, lifecycle
composition and release trust remain separate. UL-052's review-only hold is closed.

## UL-052 review and next useful workload — 2026-09-05

UL-052 is complete as a design review, not a new runtime consumer. All 19 retained
review-file hashes verify. Its new binding must use broker-owned positions; the
older local-offset FD facade cannot be reused. Package acceptance preparation is
recorded in [native command consumption](../docs/NATIVE-COMMAND-CONSUMPTION.md),
with [exact review pins](../docs/evidence/inherited-libc-readiness-2026-09-05/review.json).

Next runtime input is UL-053's bounded musl read/close witness over the pinned
UL-051 broker. Userland can proceed without a new kernel operation. Do not invent
its evidence schema/statuses or promote compatibility from the review. No new
package transport, native run or executable was added here; all three pinned
standards checks pass. Earlier sixteen-fixture/nine-boot results remain historical.

Aether's CR-01 proposal supplies the useful next command target: aether-run plus
bytecount, explicit input/output references, copied startup and exact output.
It still requires owner agreement, two-entry broker/startup implementation and
independent libc acceptance before package reconstruction. This local preparation
is not approval on another owner's behalf or a completed shared PD review.

## Inherited admission/collection checkpoint — 2026-09-05

UL-051 is package-consumed. The distinct userland-inherited evidence selector
runs over existing ABI-9 connections transport. The package parser's supervisor
ceiling is corrected from 4096 to the owner-defined 8192 bytes; tests accept
4097/8192 and reject 8193 without changing older profile limits or receipt fields.
All nine QEMU outcomes pass, including both orders, admission rollback/retry and
five precise semantic rejections. Six malformed input controls reject before
output creation. All three standards checks and sixteen package fixtures pass
on macOS. [Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-inherited-transport-2026-09-05/README.md).

The independent clients check narrowed one-entry admission, generation receipts,
shared reads and one-time observed child results; owner code supplies the native
rollback mechanisms and final-close probe. No sibling runtime, ABI or shared pin
changed. Lost successful admission/collection replies remain unknown, not replayable.
Next: UL-052's review of local libc/FD integration with broker-owned references
and positions, then its bounded consumer workload. General inheritance lists,
fork/exec/pipe/shell, POSIX parenting, policy composition and release trust remain
separate. Historical checkpoint claims below retain their original scope.

## Fixed-alias shared-file checkpoint — 2026-09-05

UL-050 is package-consumed through the unchanged ABI-9 connections transport.
The explicit userland-shared witness selector accepts only its separate schema
and six-case set. All six rebuilt-image QEMU boots pass: both exit orders,
frozen position, premature close, missing rights denial and omitted final close.
Six malformed input controls reject before output creation. All three standards
checks and sixteen package fixtures pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-shared-transport-2026-09-05/README.md).

Independent clients establish bootstrap/reply/reference checks, shared bytes and
surviving access. The final backend-close probe is owner code; the rights control
checks EACCES versus ENOTSUP, not successful unauthorized storage mutation.
No transport/receipt, sibling implementation, ABI or standards pin changed.
Next userland boundary: UL-051's parent-requested inherited-launch acceptance.
Fixed bootstrap aliases do not establish that admission/rollback contract,
general descriptor lists, POSIX parenting, exec/fork, native shell or persistence.

## Independent ABI-9 connections checkpoint — 2026-09-05

UL-049 is package-consumed with explicit AENMX001 three-image transport and a
separate reduced-pool control profile. All six outcomes pass: four rebuilt-image
QEMU checks and two prepublication structural rejections. Positive execution
preserves two client/backend terminal rounds and six reclaims; reduced capacity,
partial-frame policy and corrupt bytes reach exact rejection contexts. Five
malformed input controls reject before output creation. All three standards
checks and sixteen package fixtures pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-connections-transport-2026-09-05/README.md).

ABI 8's separate program-stop workload was reviewed, not independently executed
or package-adopted. No sibling source, prior receipt or shared pin changed.
Next userland boundary: UL-050's distinct shared-files bootstrap on ABI 9.
Connection acceptance does not establish shared open-file positions/inheritance,
FD/stdio through the broker, general admission rollback, POSIX parenting, shell,
persistence or sys-init composition. Those remain owner-coordinated work.

## ABI-7 coexistence consumer checkpoint — 2026-09-05

UL-047 is package-consumed. Explicit AENCO001 coexistence and reduced-pool control
transports preserve exact kernel-option metadata and separate destinations.
Twelve staging/rebuilt-image QEMU outcomes pass: six coexistence and six fresh
ABI-5 regressions. Exact backend generations, request failures, stale collection,
pool exhaustion and corruption outcomes are retained. Five malformed input
controls reject before publication. All three standards checks and sixteen package
fixtures pass on macOS. [Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md)
and [evidence](../docs/evidence/native-coexist-transport-2026-09-05/README.md).

No sibling runtime, shared ABI or standards pin changed. Both broker/file channel
pairs are live in the accepted raw-RPC workload; local FD/stdio through that broker
and inherited-file state remain unproven. Next userland boundary: UL-049 independent
ABI-8/9 program/multi-client capacity acceptance. UP-01 inherited-file ownership,
UP-02 process/exec/shell, ABI-6 init composition and release trust remain separate.
Do not infer acceptance of these from producer code presence or this ABI-7 run.

## Independent launch broker checkpoint — 2026-09-05

UL-045's gap review and UL-046's independent broker are delivered. The package
transport now has an explicit `process` profile over unchanged AENFS001 and a
`userland-broker` witness selector. Six staging/rebuilt-image QEMU outcomes pass,
including exact worker generations, requester statuses and cleanup counts. Five
schema/profile/case/input-boundary controls reject before output creation. All
three standards checks and sixteen package fixtures pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-broker-transport-2026-09-05/README.md).

The run consumes receipt-matched captured producer sources rather than Aether's
newer changing checkout. Inheritance remains empty, the namespace is connection
bound, and collection consumes each terminal ticket once. No native POSIX process,
file-service coexistence or inherited-file state is established. No sibling source,
shared ABI or standard pin changed.

Next userland boundary: UL-047 independent coexistence acceptance. Sys-init has a
separate recorded sequential cross-slot reuse kernel fault under SI-04; this
broker run does not test or fix it. Preserve accepted orderings while its owner
correction and consuming evidence remain pending. Native exec/fork/TTY, persistent
installation, general lifecycle/recovery and release trust stay separate.

## Buffered FILE consumer checkpoint — 2026-09-05

UL-044 is now package-consumed. The explicit `files-writable-memory` transport
preserves AENFS001 with native-memory=true, smp=false and volatile-scratch service
mode; older transport receipts remain unchanged. `userland-stdio` selects the
bounded consumer and its exact mode/build checks. All 27 rebuilt-image QEMU
outcomes pass: four stdio cases and 23 fresh regressions. Baseline input fflush,
corrupt vectors and leaked polling errno reject at exact client 189/186/196.
Seven malformed mode/build/profile/case-set controls reject before output creation.
All three standards checks and sixteen package fixtures pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-stdio-transport-2026-09-05/README.md).

No sibling implementation, musl archive, shared ABI or standards pin changed.
Memory-option metadata alone does not prove configuration; pinned accepted images
and the native consumer witness establish this bounded combination. Dynamic FILE
allocation, buffered I/O, failure preservation and cleanup do not establish all
stdio modes, automatic exit flushing, threads, native shell or persistent install.
Next userland work is UL-045's native dash gap review and concrete owner-mechanism
handoff. Process/exec/TTY, lifecycle adoption and release trust remain separate.
Historical checkpoints below retain their original scope.

## Failure-handling and libc consumer checkpoint — 2026-09-05

UL-042 and UL-043 are now package-consumed. The witness harness explicitly selects
`userland-failures` and `userland-libc` over the existing writable transport,
validates exact mode/build declarations and retains separate semantic oracles.
All 23 cases from the latest UL-043 bundle pass staging, image reconstruction and
QEMU: seven failure, four libc and twelve descriptor/file regressions. Eight
malformed input controls reject before creating output roots. All three pinned
standards checks and sixteen package fixture scripts pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-libc-transport-2026-09-05/README.md).

No package runtime/receipt format, native ABI, sibling implementation or shared
standard pin changed. Failures are injected after complete real replies; raw test
inspection is not production recovery. Libc acceptance is bounded public calls,
not internal stdio, threads, inherited descriptors or native shell execution.
Next userland boundary is UL-044 buffered-file paths; process/exec/TTY, persistent
installation, service ownership/adoption and release trust remain separate.
Older readiness-only checkpoints below are historical and superseded by this run.

## Readiness review — 2026-09-05

The UL-042 producer wait is lifted. Read-only inspection verified all 230 retained
record hashes and 19 accepted outcomes in userland's descriptor-failure bundle,
and all 298 record hashes and 23 outcomes in its newer libc-file bundle. The
second bundle includes fresh failure/descriptor/read-only/writable regressions;
these counts overlap and must not be summed as independent coverage.

- UL-042: seven injected reply/close outcomes, including no replay, connection
  poisoning and dup2 reference cleanup. Summary SHA-256:
  `9240929350a65451c914810c2913b3e93e3562808b1d4e19765cc1a59ee80441`.
- UL-043: four bounded native libc outcomes, including errno, flags, short I/O
  and shared offsets. Summary SHA-256:
  `42c788a3cf5c3d832bae852a5891c6fb1b2b0c06383ad97c14120cf901124c5e`.

Next local action: extend the package witness harness for these explicit consumer
modes and exact semantic controls, then stage/rebuild/boot the latest UL-043
bundle's 23 cases. This review did not run QEMU or establish package consumption
of either new mode. Existing writable transport should suffice; no new native
ABI or package format is implied by the owner contracts.

Sys-init and Aether also record accepted seven-case SI-01–03 / ABI-6 integration;
sys-init's bounded adapter follow-through is now local work, not a blanket producer
wait. Userland's next work is UL-044 buffered-file paths. Native process/exec/TTY,
persistent installation, service ownership and release trust remain separate.

Sources: [failure contract](../../userland/experiments/native-files/FAILURES.md),
[libc contract](../../userland/experiments/native-files/LIBC.md),
[latest evidence](../../userland/docs/evidence/native-libc-files-2026-09-05/summary.json),
[sys-init decision](../../sys-init/docs/decisions/0017-native-init-consumer.md).

## Descriptor consumer checkpoint — 2026-09-05

Userland UL-041 is delivered and package-consumed. The witness harness accepts
an explicit `userland-fds` producer over the existing `files-writable` transport;
no new package format, runtime helper or native ABI is needed. Twelve QEMU boot
outcomes pass: four descriptor cases and eight fresh file-service regressions.
Frozen offsets, early close and leaked final close reach exact client 207/213/216
rejections. Five malformed mode/build/profile/case-set inputs reject before output
creation. All three pinned standards checks and sixteen package fixture scripts
pass on macOS. [Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-fd-transport-2026-09-05/README.md).

Next userland boundary is UL-042's direct lost/malformed reply and final-close
fault injection. UL-041's bounded shared offsets/lifetime are no longer a hold;
libc interposition, process inheritance, native shell/TTY, persistent installation
and service adoption remain separate. A closed endpoint does not prove recovery
from an unobserved mutation. Older checkpoints below retain historical scope.

## Writable scratch consumer checkpoint — 2026-09-05

Userland UL-040 is delivered and package-consumed. The explicit
`stage-files-writable` profile records `service_mode=volatile-scratch-v1` without
changing AENFS001 or existing receipts. Eight transported QEMU boots pass: four
writable cases and four fresh read-only regressions. Wrong data, skipped zeroing
and ignored handle rights reach exact independent client rejections. Four
malformed mode/build/case-set inputs reject before output creation. All three
pinned standards checks and sixteen package fixture scripts pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-writable-transport-2026-09-05/README.md).

Next userland dependency: UL-041's bounded descriptor layer and shared-offset/
lifetime evidence. Writable scratch itself is no longer a hold. Persistent
storage, native process/exec/TTY, sys-init adoption and shared owner review remain
separate. Volatile scratch does not authorize package installation or mutation
replay. Historical checkpoints below retain their original evidence scope.

Updated: 2026-09-05. Ordered work, with observable acceptance. No legacy workflow commands are required.

## Native launch/channel/file transport checkpoint — 2026-09-05

Explicit AENEX001 launch, AENCH001 channel and AENFS001 read-only file-service
transport profiles now preserve six pinned artifacts with separate receipts and
required build-option metadata. Legacy supervised/memory profiles stay compatible.

The kernel launch/channel/file suites and independent userland UL-038/UL-039
consumers now pass package staging and image reconstruction: **22 case outcomes,
20 QEMU boots and two prepublication structural rejections**. Exact fault/stop,
wrong-image/count/data/root and truncated-frame outcomes are retained. All three
standards checks and sixteen ordinary fixture scripts pass on macOS.
[Contract](../docs/NATIVE-LAUNCH-TRANSPORT.md) and
[evidence](../docs/evidence/native-launch-channel-2026-09-05/README.md).

The offline cached Linux image passes standards and the parser fixture but lacks
`make`; its full package suite stops with exit 127. The missing Linux make tool remains a recorded host limit; BSD host validation is no longer required.

The next native integration boundary is userland UL-040's independently accepted
writable-scratch consumer and an explicit package transport option contract.
Read-only UL-039 is delivered, not a remaining blocker. Sys-init channel/lifecycle
adoption and shared PD owner review remain separate; native shell/pkg-mgr still
needs process/exec/descriptor and usable filesystem semantics. No native install,
service activation, persistent storage or authenticated release claim is added.
Memory is no longer a prerequisite hold. Other host package/trust work remains
possible; this checkpoint does not claim the entire product is finished.



## 1. Harden the local package path — complete for the bounded fixture

- Express phase ordering so parallel make cannot extract/build/stage before prerequisites complete.
- Verify the actual copied source bytes before extraction; a same-size corruption must stop the package path before downstream output.
- Define a private output-root contract before broadening mutation; reject unsafe roots and preserve prior outputs on tested failures.
- Document the actual make dialect required by the Aether development build; no BSD make compatibility campaign is required.

Done when the local fixture succeeds serially and under parallel invocation, tampering fails before extract, and relevant negative checks pass in disposable roots. Keep this slice shell/make; do not add network fetch or native Aether dependencies.

Validated with `sh tests/check.sh`: ordered serial/parallel runs, copied-source corruption rejection, private-root guards, and failed-publication preservation. GNU Make 3.81 is the tested dialect; BSD make compatibility remains unclaimed. See [the implemented contract](../docs/BUILD-FIXTURE.md) for the single-writer and trusted-recipe limits.

## 2. Inspectable package state — complete for staged regular files

Implement a bounded private-root fixture using authoritative package records and editable `world`; derive ownership and reverse-dependency views. Register only payload matching validated evidence. Support inspection, verification, and non-deleting orphan reports. Define path/type semantics explicitly before expanding beyond regular files.

Done when records round-trip deterministically, edited roots change reports predictably, missing/corrupt/conflicting payloads are classified, invalid data preserves prior records, and no command writes a real prefix or deletes payload. Reuse the archived BG-009 research selectively; its generation/GC phases are no longer mandatory prerequisites.

Validated by `tests/package-state.sh`: evidence-bound registration, immutable/idempotent records, editable roots, ownership/dependency views, payload discrepancy reporting, cyclic orphan closure, malformed-state rejection, and failed-publication preservation. No persisted indexes or deletion authority were added. See [the state contract](../docs/PACKAGE-STATE.md).

## 3. Aether artifact handoff and sys-init contract — boot handoff verified; service contract pending

Agree the smallest concrete artifact/image handoff with Aether and service descriptor boundary with sys-init. Record target ABI/toolchain identity separately from host identity. Stage one relevant artifact and manifest; only claim integration when the receiving project actually consumes it with recorded evidence.

Host-side work can proceed while target loaders and service contracts evolve. Native POSIX support is not a prerequisite for host staging; it is a prerequisite to claiming this shell tool runs natively.

The pinned kernel/flat-fixture pair was staged by `mk/aether-boot.sh`, consumed by Aether's existing image builder, and passed its two-CPU smoke test. [Evidence and limits](../docs/AETHER-HANDOFF.md) are retained. [Service handoff cases](../docs/SERVICE-HANDOFF.md) are proposed only: sys-init's BG-027 still owns the unimplemented schema, validator, and enablement contract. This dependency does not block host-only package work.

## 4. First useful package lifecycle — source/dependency and local binary transport working

Select one real source package and bounded dependency case; define archive format, ownership conflicts, configuration behavior, and installation transaction/recovery semantics. Prove build, staged install, inspect, verify, update, and remove in a disposable root. Reopen deletion scope explicitly before implementing remove. Add a minimal CLI once these command contracts are clear.

The pinned static zlib 1.3.2 recipe and local zpipe 0.1 utility now build/test/stage/register. Both records verify, world closure keeps the dependency, corrupted source/dependency inputs fail, and host/target observations are bound into manifests. See [the reproducible procedure and evidence](../docs/ZLIB-PACKAGE.md). This completes the source-build portion, not the full lifecycle. The [binary experiment](../docs/BINARY-PACKAGE.md) now exports/imports those real packages with descriptor pins, target checks, exact dependency fingerprints and recorded ordinary file modes. Imported zpipe runs successfully. [Explicit recovery](../docs/IMPORT-RECOVERY.md) now handles matching interrupted imports with one record rename and idempotent retry. State v2 permission tracking is implemented. Configuration-aware upgrades, power-loss durability and deletion scope remain unresolved before updates/removal. Aether-userland owns base selection; no base list is assumed.

## Later, when evidence supports it

- Binary trust policy: fail-closed eligibility, signer/key lifecycle, freshness/replay policy, provenance, and clear rebuild escape paths (old BG-011, BG-029, BG-043).
- Bootstrap seed/toolchain and options/overlays; dependency resolution driven by actual package cases (BG-012–015, BG-026–028, BG-030).
- Aether-native isolation and reproducible-build validation. Other-OS qualification in BG-032–040 is retired; archived dry runs do not establish confinement.
- Transaction durability, optional generations/rollback, and non-deleting reachability experiments after baseline state (BG-009, BG-031).
- Governance, security response, and contributor documentation as a usable release approaches (BG-016, BG-021).

The complete old backlog is preserved in the archive. These themes replace its promotion gates; tasks about maintaining the retired planning machinery are retired, not engineering dependencies.

[Read-only update preflight](../docs/UPDATE-PREFLIGHT.md) now reports proposed differences and installed-drift/reverse-dependent blockers. It does not apply replacements.

[Configuration/replacement policy](../docs/REPLACEMENT-POLICY.md) defines implemented three-way comparison and conservative local-file preservation. Its retained-payload private-root replacement is now implemented with prepare/finish commands, pinned recovery and a pending-state guard; pruning and live-prefix writes remain unimplemented.

Real zpipe 0.1 → 0.2 replacement now validates active/retained executable behavior and cross-version streams with unchanged zlib/world. The thin [CLI](../docs/CLI.md) now exposes the proven explicit command contracts with human/TSV and plain/color modes. Controlled wrapper/group interruption tests now preserve receipts before reporting unknown outcomes. Closed-stream/render-interruption tests now retain private raw receipts. Receipt-loss recovery now passes against actual prepared/completed binary-fixture transactions, including forged-pin rejection. Next review current sibling handoff readiness before selecting the next integration fixture; cancellation of arbitrary descendants remains unproven.


The supervised six-artifact transport is now included in the ordinary test gate,
following boot v2. Its synthetic transport checks remain distinct from the saved
native supervision witness. The memory proposal has since gained bounded implementation and consumer
evidence, recorded below. The newest launch/channel/file checkpoint above
supersedes that prerequisite hold; it does not authorize package activation.


Native-memory v1 now has kernel and userland acceptance plus a package-staged
boot witness: [native-memory transport](../docs/NATIVE-MEMORY-TRANSPORT.md).
The current memory prerequisite hold is closed for this bounded consumer.
Authenticated artifact admission, native filesystem/install semantics, broader
process/TTY support and release gates remain separate work.
