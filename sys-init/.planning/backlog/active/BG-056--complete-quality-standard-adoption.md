# BG-056 — Complete quality standard adoption

Status: active. Owner: sys-init maintainer. Priority: applicable gaps before the
next affected build/change; full profile adoption before publication.

Input: [2026-09-05 review](../../../docs/STANDARDS-UPDATE-REVIEW.md). Local workflow
is in place; the shared drafts remain unreleased. Do not invent owner acceptance.

1. Complete in initial review: worker build subprocesses now have duration/output
   bounds, retained timeout/error logs and independent timeout/overflow regressions.
   A fresh pinned build passes with an unchanged worker ELF.
2. Review current Python/Rust/C unsafe/FFI, ownership and partial-error cleanup;
   record exact findings, affected files, risk, owner and disposition.
3. Complete command/config/API documentation and requirement-to-test inventory,
   including positive/negative examples and exact implementation identity.
4. Select pinned formatter/static-analysis tools for actual consumer editions;
   separate formatting-only migration and exclude upstream/generated/evidence.
5. Document dependency closure and resource budgets per component with measured
   baselines where performance is claimed. Do not infer budgets from code size.
6. Before publication, supply actual technical/reader reviews, manual/diagram
   tooling where applicable, target offline lookup and reporting contact.

Acceptance: scoped records with checks and retained evidence; unresolved items
stay visible with milestones. Coordinate BG-054 extended testing and BG-040
rejection cleanup; do not duplicate those implementation stories. A future
released profile requires a separate explicit pin/adoption review.

## RC1 adoption handoff ADP-03 — 2026-09-06

See the [local clause review](../../../docs/STANDARDS-RC1-REVIEW.md) and its
individual dispositions for current coverage and missing work. This review does
not complete this story, approve exceptions, configure extended runs or change
release pins. Close only the named scoped gaps with actual evidence before the
corresponding conformance/publication claim. Post-R1 features are outside this work.

## First local static gate — decision 0095

[Static checks](../../../docs/STATIC-CHECKS.md) close the initial Python syntax
and two-host-test Rust formatting slice. Installed rustfmt 1.98.0 is pinned for
macOS arm64; other hosts remain blocked pending tool identity and execution.
No native format migration, Clippy/ShellCheck, complete unsafe review or full
profile acceptance is claimed. Continue items 2–6 above and BG-054 separately.

## Reporting contact and independent review

The maintainer supplied security@aethersys.org on 2026-09-06; SECURITY.md and
README now publish it. No delivery test, response SLA or support-period claim
was made. Independent technical/reader review still needs an actual reviewer
and recorded work; the contact response did not supply that reviewer.

## Boundary review and Clippy — decision 0096

Decision 0096 records 50 textual low-level boundary occurrences in 13 native
Rust/C files, with exact hashes and scoped obligations. Source-drift/omission
checks now require an explicit inventory review. The static gate additionally
runs pinned default-group Clippy on two host harnesses and their pure imported
modules. Two host index loops were corrected; no native source bytes changed.
Eleven static-harness cases and all ten aggregate gates pass in
`out/checks/run-74_rx3ah`. The unused shared-method Rust warning remains visible.
The failed intermediate compiler edit and lint-control issue are recorded.

The maintainer supplied security@aethersys.org; SECURITY.md now publishes it.
Independent technical/reader review remains pending. Next local finding: bound
the older I/O worker builder's tools, then qualify exact artifact compatibility.
The boundary inventory is not full per-profile soundness acceptance or a waiver.

## Older I/O builder bounds — decision 0097

Compiler/tool calls now have the same 180-second/4 MiB limits as the service
worker builder, with owned teardown and retained attempt classifications. Four
I/O worker profiles rebuild to identical ELF/envelope bytes. This closes that
CP-02 finding; other older builders and full Python/C path review remain open.

## Standalone compiler bounds — decision 0098

The remaining lifecycle/supervisor compiler calls now use bounded owned runs
and preserve attempt outcomes, logs and helper/caller source identities. Three
lifecycle and twenty supervisor variants rebuild to identical raw/envelope
bytes. Positive/nonzero/missing-tool/timeout/overflow regression cases cover the
shared helper. Complete interface documentation and independent review remain
open; native code and release pins are unchanged.

## Documentation inventory — decision 0099

Eighteen developer entry points now have recorded source identities, argument
declarations and narrative references. Configuration/internal interface families
have coverage and missing-work dispositions. The aggregate command has an mdoc
source with local lint/render checks. Complete remaining manuals, independent
technical/reader review, HTML visual review and target installation remain open.

## Checker manuals — decision 0100

Three additional canonical mdoc manuals cover static, quality-record and native
evidence commands, preserving distinct streams/exits and runtime scope. Twelve
CLI probes and ten aggregate checks pass in out/checks/run-r5bdp085. All three
manuals render at 78/60 columns and HTML; only the documented experimental-OS
STYLE notice remains. Four of eighteen entry points have manuals. Next: remaining
command manuals and configuration/API detail. Independent review and target
installation/lookup still need external evidence before publication.

## Runtime command manuals — decision 0101

Model, host and measurement commands now have source manuals. Eleven CLI probes
and all ten aggregate gates pass in out/checks/run-jq4due2q. A complete measurement
attempt retains 24 repetitions and its expected timeout control, with no native
or comparative-speed claim. Terminal renderings fit 78/60 columns; the documented
OS STYLE notices remain. Seven of eighteen commands have manuals. Next: builder,
native-runner and standard-checker manuals, then detailed configuration/API
coverage. Independent review and target lookup remain publication requirements.

## Standards-wrapper review — decision 0102

Ten of eighteen commands now have manuals. Source review identified two concrete
local verification follow-ups before a uniform fail-closed verification claim:

- The Experience wrapper lacks exact lock-field/version/source validation,
  duplicate-key and release-symlink rejection, and a complete pre-execution
  inventory check. Preserve release bytes and add synthetic controls before
  changing this wrapper; success output and pins remain stable.
- Experience/Distribution reference checks contain assertions, but wrappers
  inherit PYTHONOPTIMIZE without rejecting or normalizing it. Define and test
  assertion-enabled child execution without editing pinned checker code.

The manual probes used normal assert-enabled Python. This is source review, not
a demonstration of every malformed input or an approved exception. Owner:
sys-init maintainer. Prioritize these local gaps before the remaining eight
builder/native-runner manuals; independent review and target lookup remain open.

## Wrapper verification fixes — decision 0103

Experience now validates exact lock fields, symlinks and full manifest inventory
before execution. Experience/Distribution run reference children with assertions
enabled. Four tests cover 45 synthetic scenarios; six real-release runs preserve
original stdout, and every release pin/vendor hash is unchanged. All ten gates
pass in out/checks/run-5aqgn48h. This closes the two decision-0102 findings, not
full verification/tool-closure adoption. Next: remaining eight builder/native-runner
manuals and detailed API coverage; standalone tool bounds remain tracked.
Independent review and target lookup still need external evidence.

## Builder manuals — decision 0104

All four builders have source manuals: fourteen of eighteen commands covered.
Twelve CLI probes, four fresh builds and all ten aggregate gates pass in
out/checks/run-h4b3tn59. Lifecycle/supervisor/I/O artifacts match retained bytes;
service ELF passes structural checks. All four manuals fit 78/60 columns and
retain only the documented OS STYLE notice. Runtime and release pins are
unchanged. Next: four native-runner manuals, then detailed configuration/API
coverage and remaining standalone bounds. Independent/target review stays open.

## Native-runner manuals and capture fix — decision 0105

All eighteen inventoried commands now have canonical source manuals. Twelve
CLI probes and all ten aggregate gates pass in out/checks/run-xfa9ytax. Review
found and fixed the I/O runner's omitted bounded_tools.py capture. The paired
import/removal regression passes, and the isolated io-stop build preserves
retained raw/envelope bytes. No new guest execution is claimed. Next: detailed
configuration/API inventory and remaining legacy subprocess bounds. Independent
reader/technical review, HTML visual review and target lookup remain open.

## Host descriptor reference — decision 0106

All thirteen fields and parse/prepare/activate/start ownership now have a local
reference, six contract tests and an executable temporary example. All ten
gates pass in out/checks/run-qdahttz9; reviewed runtime bytes match the earlier
source snapshot. No runtime/pin change or native execution. Next: remaining
record/API families and legacy subprocess bounds. Installed configuration/API
manuals, independent review and target lookup remain open.

## Legacy runner bounds — decision 0107

Lifecycle and native-supervision command capture now retains bounded logs and
receipts without converting timeouts/overflow into semantic rejection exits.
Six focused host tests and all ten gates pass in out/checks/run-rzmxebis.
Fresh QEMU witnesses pass all three lifecycle and five supervision cases;
all eight client envelopes match retained profiles and 24 native inputs remain
unchanged. The sandbox socket failure and successful lifecycle retry are both
retained. Evidence: docs/evidence/legacy-runner-bounds-2026-09-06/README.md.
Next: nested compiler-group cleanup, remaining runner bounds and record/API
references. Independent technical/reader review remains pending; pins stay fixed.

## Aggregate log bounds — decision 0108

Each aggregate gate now retains at most 4 MiB of combined stdout/stderr, with
a distinct output-limit outcome and separate raw prefixes. Twelve focused host
runner tests and all ten gates pass in out/checks/run-5d53pv35. Manual lint and
78/60-column rendering pass; all 24 native inputs remain unchanged. No fresh
native execution or shared pin change. Evidence is retained under
docs/evidence/aggregate-log-bounds-2026-09-06/. Next: inner host/model capture
bounds, nested compiler-group cleanup and record/API reference coverage.
Independent technical/reader review remains pending.

## Inner capture bounds — decision 0109

Host/model workers now have a combined 4 MiB capture limit and a 30-second
deadline through drain/exit. Eight focused tests and all ten gates pass in
out/checks/run-sr4k1ikf. Model semantic records and host summary count/shape match
the prior run; all 24 native inputs are unchanged. Updated manuals lint cleanly
and evidence is retained in docs/evidence/inner-capture-bounds-2026-09-06/.
Next: nested/outer process cleanup, other resource limits and record/API
references. Independent review remains pending; shared release pins stay fixed.

## Cooperative aggregate cleanup — decision 0110

The aggregate now gives failing gate groups one second of SIGINT grace before
forced cleanup. The before-fix nested-wrapper regression fails as expected;
both new tests and twelve existing runner tests pass with the change. All ten
gates pass in out/checks/run-zayzuf8u. The retained after-probe shows its separate
worker reaped and pipes closed before wrapper exit. Native inputs and inner
helpers are unchanged. Evidence: docs/evidence/cooperative-check-cleanup-2026-09-06/.
Unresponsive detached/deep groups and abrupt outer termination remain open,
along with other resource limits, record/API coverage and independent review.

## Active gate SIGTERM — decision 0111

SIGTERM during main-thread gate capture now follows the interrupted result and
cooperative cleanup path, restoring the previous handler afterward. The retained
default-signal before probe exits -15 without a report; the after probe records
interruption and nested cleanup. Three new tests, fourteen prior focused tests
and all ten gates pass in out/checks/run-pe9urad8. Manual lint is clean; native
inputs and inner helper are unchanged. Evidence: docs/evidence/aggregate-termination-2026-09-06/.
Startup/between-gate windows, SIGKILL, repeated SIGINT and detached/deep ownership
remain open, along with record/API coverage and independent review.

## Static record findings — decision 0112

The field reference and five source/boundary controls expose the next local
validation work, before treating these trusted files as external records:

- Validate bounded JSON, duplicate keys, schema, field types and unknown keys
  before tool lookup; settings and boundary metadata are not strictly parsed.
- Ensure missing/wrong-type fields produce a structured failed record rather
  than escaping via KeyError, TypeError or AttributeError.
- Define and enforce ordinary-file and parent-symlink policy before reads.
- Bind settings/inventory identity across a standalone check, including
  metadata ignored by current boundary equality; retain failed attempts.
- Complete host-tool dependency closure; rustup and dynamic libraries are not
  pinned by current executable hashes.

These are follow-ups, not implementation claims or permission to edit release
pins. Other record/API families and independent publication review remain open.

## Static record reference — decision 0112

The twelve static-tool fields, native-boundary/site fields and result shapes
now have a local field reference with explicit validation limits. Five focused
contract tests and all ten gates pass in out/checks/run-n1dguucj. Reader, settings,
boundary records and native source bytes remain unchanged. Evidence is retained
in docs/evidence/static-record-reference-2026-09-06/. Next: strict bounded record
validation before tool lookup and consistent failures, followed by the remaining
record/API families. Independent publication review remains open.

## Strict static record validation — decision 0113

Static settings and boundary records now validate before tool lookup, with
bounded JSON/depth, duplicate-key rejection and exact schema/field/type rules.
All 22 focused static tests and all ten gates pass in out/checks/run-d8akh8py.
The first deep-JSON test failure is retained; an explicit 32-level limit fixes
Python-version-dependent behavior. Maintained records and native inputs remain
unchanged. Evidence: docs/evidence/static-record-validation-2026-09-06/.
Next: ordinary-file/parent-symlink and standalone metadata identity checks;
tool dependency closure and other record/API references remain open.

## Static input integrity — decision 0114

Selected sources and records now require ordinary files without symlink
components inside the supplied root. Bounded reads check identity around open
and read; captured settings/inventory bytes must match before success. All 27
focused static tests and all ten gates pass in out/checks/run-rzjuf8cz. Maintained
records and native inputs are unchanged. Evidence: docs/evidence/static-input-integrity-2026-09-06/.
Hostile directory races, atomic snapshots and tool dependency closure remain
outside this result. Next: remaining record/API families; independent review
and tool-host closure remain release-readiness work.

## Quality record follow-ups — decision 0115

The field reference identifies bounded strict JSON/schema/type validation,
ordinary-file/symlink policy, complete snapshot inventory closure and stable
identity between hashing/parsing as remaining quality-checker work. The checker
does not execute referenced tests, authenticate owners or attest independent
review. Preserve the retained snapshot and release pins when closing these gaps.

## Quality record reference — decision 0115

The inventory, surface/gap, snapshot-manifest and result fields now have a
local reference distinguishing structural checks from execution/reviewer proof.
All six quality tests and all ten gates pass in out/checks/run-__pahll1. Reader,
snapshot pin and native inputs remain unchanged. Evidence is retained in
docs/evidence/quality-record-reference-2026-09-06/. Next: bounded strict quality
record validation and snapshot input/closure checks; native evidence catalog and
other API references remain open. Independent publication review is still pending.

## Quality record validation — decision 0116

Strict bounded inventory/manifest parsing now precedes reference traversal.
Manifest hash and parse use one captured byte buffer. All eleven quality tests
and all ten gates pass in out/checks/run-ulshq9dr; success stdout matches the
prior run. Snapshot pin and native inputs are unchanged. Evidence: docs/evidence/quality-record-validation-2026-09-06/.
Next: snapshot closure, file/symlink policy and end-of-run identity. Two existing
60-column literal overflows remain publication-layout work; lint passes.

## Quality snapshot closure — decision 0117

Snapshot files must exactly match their manifest plus the manifest itself;
symlink/special entries and excessive tree size reject. Membership, listed
digests and inventory/manifest bytes are rechecked before success. All seventeen
quality tests and all ten gates pass in out/checks/run-fh_3hr_r. Snapshot pin and
native inputs remain unchanged. Evidence: docs/evidence/quality-snapshot-closure-2026-09-07/.
Next: bounded snapshot source reads and general reference file policy; atomic
filesystem guarantees and independent publication review remain outside scope.

Decision 0118 closes bounded quality input reads and ordinary reference file
policy: 21 focused tests and ten gates pass in out/checks/run-xuuqhhmn.
Retained pins and native inputs are unchanged. Remaining offline lock/configuration
reference coverage is next; atomic filesystem reads, I/O deadlines and independent
review stay open. See docs/decisions/0118-quality-input-bounds.md.

Decision 0119 adds OFFLINE-LOCKS.md and four required cross-wrapper tests
(45 subcases); all ten gates pass in out/checks/run-j58r3r5b. No wrapper or pin
changes. Next: bound lock/manifest/payload reads and tree traversal, reject special
files, then review verification-to-execution identity and interpreter closure.
Independent technical/reader review remains pending.

Decision 0120 bounds standards-wrapper reads/traversal and rejects special files.
Twelve focused tests and all ten gates pass in out/checks/run-fq54cl5_. Pins,
success output and native inputs stay unchanged. Next: verification-to-execution
input identity and interpreter/environment closure; I/O deadlines and independent
review remain open. See docs/decisions/0120-standards-input-bounds.md.

Decision 0121 adds pre/post child standards-input rechecks. Fifteen focused tests
and ten gates pass in out/checks/run-4ijd1_d1. Pins, output and native inputs are
unchanged. Next: review verified private execution and interpreter/environment
policy. Atomic execution, I/O deadlines and independent review remain open.
See docs/decisions/0121-standards-input-rechecks.md.

Decision 0122 adds verified private standards execution, Python -I -S -B and a
64 MiB staging limit. Eighteen focused tests and ten gates pass in run-celvo_l3;
output/pins/native inputs stay fixed. Next: standalone child time/output bounds
and cleanup; trusted interpreter closure, I/O deadlines, abrupt termination and
independent review remain open. See docs/decisions/0122-private-standards-execution.md.

Decision 0123 bounds reference-child duration/output and capture cleanup.
Twenty-one focused tests and ten gates pass in run-wo5ygk7e; output bytes, pins
and native inputs stay unchanged. Next: active-wrapper SIGTERM cleanup for staged
trees/children. Escaped descendants, blocked output sinks, filesystem I/O and
independent review remain open. See docs/decisions/0123-standards-child-bounds.md.

Decision 0124 adds active standards SIGTERM cleanup and explicit exit 130.
Twenty-four focused tests and ten gates pass in run-81w8wpg7; output bytes, pins
and native inputs stay fixed. Next: native-evidence catalog field/lifetime
reference. Startup/staging/repeated-signal limits and independent review remain
open. See docs/decisions/0124-standards-termination.md.

Decision 0125 adds the native catalog field/lifetime reference and three required
controls. All 28 native-harness tests and ten gates pass in run-fnv8xqqe; audit
output and checker/catalog/native bytes stay fixed. Next: strict catalog validation
before bundle reads. Bounded artifact reads, receipt validation, end consistency
and independent review remain open. See docs/decisions/0125-native-catalog-reference.md.

Decision 0126 validates catalog JSON and exact fields before bundle access.
All 33 native-harness tests and ten gates pass in run-7bbbia9g; the earlier
source-change aggregate rejection is retained. Catalog bytes/native output stay
fixed. Next: ordinary catalog reads and native manifest validation; receipt schemas,
large-artifact bounds, final consistency and independent review remain open.

Decision 0127 adds native metadata ordinary-file reads and strict manifests.
All 37 native-harness tests and ten gates pass in run-5_9vk5jd; native audit output
and retained catalog/native bytes stay fixed. Next: streaming ordinary-file payload
hashing; receipt schemas, final consistency and independent review remain open.

Decision 0128 adds streaming ordinary-file native payload hashing. All 41 native-
harness tests and ten gates pass in run-wl7174yz; native audit output and retained
catalog/native bytes stay fixed. Next: bounded semantic JSON/serial/envelope reads;
receipt schemas, final consistency and independent review remain open.

Decision 0129 adds bounded ordinary native semantic content reads. All 44 native-
harness tests and ten gates pass in run-hdspju8m; native output and retained bytes
stay fixed. Next: verified-byte semantic parsing; strict receipts, final consistency
and independent review remain open. See docs/decisions/0129-native-content-reads.md.

Decision 0130 verifies native semantic buffers and receipt hashes against the
manifest map. All 47 native-harness tests and ten gates pass in run-718_ig3c;
output and retained native bytes stay fixed. Next: complete bundle membership and
end consistency; strict receipt schemas and independent review remain open.

Decision 0131 adds complete native bundle membership and final consistency.
All 50 native-harness tests and ten gates pass in run-djhnko6x; native output and
retained inputs stay fixed. Next: strict receipt/report JSON parsing; sequential
race limits, I/O deadlines and independent review remain open.

Decision 0132 strictly parses native receipt/report JSON objects. All 53 native-
harness tests and ten gates pass in run-zw1mn0x6; output/retained inputs stay fixed.
Next: receipt/report field and type validation. Filesystem race limits and
independent review remain open. See docs/decisions/0132-native-receipt-json.md.

## Consumer report fields — 2026-09-07

Decision 0133 validates native consumer report/case/command fields before linked
receipt access, with exact fields, scalar types and collection/text bounds.
All 57 native-harness tests and ten gates pass in `out/checks/run-k02c23ut`.
Native audit output, catalog, 24 tracked native inputs and release pins remain
unchanged. Next: producer summary/report and worker/build receipt field validation
under BG-056. Independent review and filesystem I/O/race limits remain open.
Evidence: `docs/evidence/native-consumer-report-fields-2026-09-07/`.

## Linked receipt fields — 2026-09-07

Decision 0134 validates consumed producer summaries/reports, service-worker
receipts and I/O supervisor builds before using linked fields. All 130 retained
linked receipts pass; 61 native-harness tests and ten gates pass in
`out/checks/run-boauxp1k`. Native audit output, catalog, 24 native inputs and release
pins remain unchanged. Next: review additional artifact correspondence and SDK
receipt scope under BG-056. Independent review and filesystem limits stay open.
Evidence: `docs/evidence/native-linked-receipt-fields-2026-09-07/`.

## Artifact correspondence — 2026-09-07

Decision 0135 verifies 22 retained I/O supervisor links and SDK/tool-lock/libc
links in 18 consumed worker receipts. All 63 native-harness tests and ten gates
pass in `out/checks/run-9whx2d2a`. Audit output, catalog, 24 native inputs and
release pins remain unchanged. Missing historical ISO/original-envelope artifacts
are explicit limits. Next: SDK receipt scope and remaining envelope correspondence
under BG-056. Independent review and filesystem limits remain open.
Evidence: `docs/evidence/native-artifact-correspondence-2026-09-07/`.

## I/O envelope correspondence — 2026-09-07

Decision 0136 checks all 22 I/O envelope layouts, reconstructed native hashes
and embedded supervisors. All 65 native-harness tests and ten gates pass in
`out/checks/run-lfrm_fw8`. Audit output, catalog, 24 native inputs and release
pins remain unchanged. Next: scoped direct/derived SDK receipt validation under
BG-056, accounting for legitimate multiline patch text. Missing ISO artifacts,
independent review and filesystem limits remain open.
Evidence: `docs/evidence/io-envelope-correspondence-2026-09-07/`.

## SDK receipt fields — 2026-09-07

Decision 0137 validates 23 direct SDK occurrences and four derived receipts,
including fixed-path nested reads and multiline patch records. All 69 focused
native-harness tests and ten gates pass in `out/checks/run-9nf8l3cz`. Audit
output, catalog, 24 native inputs and release pins remain unchanged. Next: review
SDK artifact/input correspondence under BG-056. Structural receipt checks do not
certify patch/ELF/tool semantics; missing artifacts, independent review and
filesystem limits remain open.
Evidence: `docs/evidence/sdk-receipt-fields-2026-09-07/`.

## Derived SDK correspondence — 2026-09-07

Decision 0138 verifies derived SDK input/artifact hashes and embedded ELF bytes.
All 904 input links, eight artifact links, 72 focused tests and ten gates pass in
`out/checks/run-bp3a1s_e`. Audit output, catalog, 24 native inputs and release
pins remain unchanged. Next: review remaining producer receipt correspondence
under BG-056. Missing direct SDK artifacts are explicit limits; independent
review and filesystem deadline/race limits remain open.
Evidence: `docs/evidence/derived-sdk-correspondence-2026-09-07/`.

## Producer receipt consistency — 2026-09-07

Decision 0139 checks 40 producer summary counts and 54 producer/worker
SDK/libc/tool-lock links, preserving five normalized count omissions. All 73
focused tests and ten gates pass in `out/checks/run-ch5gzenc`. Audit output,
catalog, 24 native inputs and release pins remain unchanged. Next: bounded
producer source-archive member review under BG-056. Missing producer artifacts,
independent review and filesystem deadline/race limits remain open.
Evidence: `docs/evidence/producer-receipt-consistency-2026-09-07/`.

## Source archive correspondence — 2026-09-07

Decision 0140 verifies all 45 producer source archives against 8,307 summary
input entries with bounded in-memory decompression/member hashing and no extraction.
All 76 focused tests and ten gates pass in `out/checks/run-pgv6t__v`. Audit
output, catalog, 24 native inputs and release pins remain unchanged. Next: review
producer source-map omissions and remaining evidence coverage under BG-056.
Ten normalized .DS_Store references are absent; missing artifacts, independent
review and filesystem deadline/race limits remain open.
Evidence: `docs/evidence/source-archive-correspondence-2026-09-07/`.

## Producer source correspondence — 2026-09-07

Decision 0141 verifies 3,420 producer source references and scopes ten historical
metadata omissions to exact bundle pins/schema/names/hashes. All 77 focused tests
and ten gates pass in `out/checks/run-me3ukw5u`. Audit output, catalog, 24 native
inputs and release pins remain unchanged. Next: consolidate remaining evidence
limits and prioritize operational BG-056 gaps. Missing historical artifacts,
independent review and filesystem deadline/race limits remain open.
Evidence: `docs/evidence/producer-source-correspondence-2026-09-07/`.

## Evidence checkpoint and priority — 2026-09-07

Decision 0142 consolidates current coverage, historical gaps and operational
priorities in docs/EVIDENCE-LIMITS.md. All ten gates pass in
`out/checks/run-y2t_prwl`; native audit code/output, catalog, 24 native inputs and
release pins remain unchanged. Next implementation: bound aggregate source
snapshot reads (scripts/check-all.py), followed by report/error-path review.
BG-054 scheduling, missing artifacts and independent review remain separate work.
Evidence: `docs/evidence/evidence-limits-priority-2026-09-07/`.

## Aggregate source snapshots — 2026-09-07

Decision 0143 bounds aggregate source snapshots with traversal/file/total limits,
streaming hashes, ordinary-file identity and selected-membership rechecks. All
five focused snapshot tests and ten gates pass in `out/checks/run-9dv0gmtb`;
legacy current-map compatibility passes. Native audit output, catalog, 24 native
inputs and release pins remain unchanged. Next: aggregate snapshot-error/report
publication review. Filesystem deadlines/races and independent review remain open.
Evidence: `docs/evidence/aggregate-source-snapshots-2026-09-07/`.

## Aggregate report publication — 2026-09-07

Decision 0144 adds atomic aggregate report replacement and stage-specific
snapshot/report failure records. Six focused tests and all ten gates pass in
`out/checks/run-k7q8lxv3`. Native audit output, catalog, 24 native inputs and release
pins remain unchanged. Next: output-directory startup and output-pipe handling.
Fatal/repeated signals, durability, filesystem deadlines and independent review
remain explicit limits.
Evidence: `docs/evidence/aggregate-report-publication-2026-09-07/`.

## Aggregate startup and pipes — 2026-09-07

Decision 0145 handles output-directory startup errors and broken summary/progress
pipes. Four focused tests and all ten gates pass in `out/checks/run-axrwya5u`.
Native audit output, catalog, 24 native inputs and release pins remain unchanged.
Next: BG-054 bounded extended-test plan (corpus, seeds, budgets, cleanup, triage and
freshness), before any scheduling. Fatal/repeated signals, blocked I/O, platform
qualification and independent review remain explicit limits.
Evidence: `docs/evidence/aggregate-startup-pipes-2026-09-07/`.

## Linux Rust qualification — 2026-09-07

Decision 0151 provisions verified Linux Rust 1.98.0 and a separate linker image.
All ten Linux gates pass in `run-bame9hi5`; all ten macOS gates pass in
`run-t_uefwle`. Added Linux rustfmt/Clippy hashes preserve existing macOS entries
and all Aether release pins. Native inputs and audit stdout remain identical.
The OCI image is saved for offline reload; dependency setup, failed missing-image
attempt and exact package/tool identities are retained. Next: independent review
and BSD/illumos qualification; hosted CI still needs a selected provider/remote.
Linux setup: `docs/LINUX-DEVELOPMENT.md`.
Evidence: `docs/evidence/linux-rust-tools-2026-09-07/`.

Catalog acceptance remains pending: the reused normalized producer omits recorded
`kernel/.DS_Store` and `kernel/arch/.DS_Store` inputs. Decision 0141 restricts its
historical exception to exact old bundle pins; this new bundle inherits no waiver.
The rejected catalog candidate and failed validation are retained. The existing
catalog stays byte-identical (50 bundles / 3,019 recorded outcomes). The fresh 180
QEMU outcomes are separate consumer evidence, not a new accepted catalog entry.
BG-056 must obtain a complete newly witnessed producer bundle before catalog
acceptance; do not repair historical metadata or weaken the checker. This limitation
does not negate the recorded runtime execution or block unrelated native work.

## ABI-16 evidence catalog follow-on — decision 0175

The separately sealed 214-case Terminal consumer and 32-case profile replay have
complete new producer source membership. Extend the offline native auditor with
explicit support for the consumer-owned composed intake schema and AENIN003
boundaries before adding this bundle to the catalog. Preserve the 50-bundle/3019
historical catalog and its exact exception scope; no new omission waiver applies.
This auditing follow-on does not block the manually reviewed bounded target result.

## Simplicity triage — 2026-09-07

SE-01–05 process adoption: [record](../../../docs/SIMPLICITY-ADOPTION.md).
Owner: sys-init maintainer. These findings are not runtime defects or approval to
remove existing paths; preserve evidence and prior consumers.

- SE-SI-01, delivery priority: fixture dispatch/assertion exits and the general
  journal experiments must not become the v1 product loop by default. In the next
  two-service composition review (BG-065), identify the direct startup/stop path,
  exact authority/error boundaries and which experimental modules it avoids.
  Acceptance: the existing design description answers all three questions and
  explains responsibility, control flow, current state, failures and total cost.
- SE-SI-02, maintenance risk: accumulated historical “next” statements can revive
  shelved work or create competing status records. Keep the active state/roadmap
  authoritative; as documents are touched, mark historical direction and link
  the current disposition. Do not rewrite immutable evidence or mass-edit history.
  Acceptance: affected entry points agree on the current delivery scope, without
  a new tracker or conformance framework.

Neither finding authorizes post-v1 implementation. Reassess at the next real
change; independent review and actual implementation simplicity remain open.

SE-SI-01 follow-up: BG-065 applies all three simplicity questions to the actual
direct pair component, with explicit ownership, state and failure ordering. The
journal stays outside that path; existing fixtures remain as evidence. SE-SI-02
continues incrementally in active state/roadmap updates, without rewriting history.
