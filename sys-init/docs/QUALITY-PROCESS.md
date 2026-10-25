# Change review and validation

Read the pinned [method](../../.agent-temper/METHOD.md), root [engineering
policy](../../PROJECT.md) and root [STATE](../../.planning/STATE.md) first. The
selected bounded record owns scope and continuation; BG records retain component
details. Root [DEVELOPMENT](../../docs/DEVELOPMENT.md) governs focused test cadence,
compact retention and integration after required checks and separate review.
Affected-owner, native-execution and release approvals remain separate requirements.
Commands below run from `sys-init/` unless explicitly marked as system-root commands.

## Current delivery scope

The maintainer accepted [simple Aether v1](V1-SCOPE.md) on 2026-09-07. Apply
quality checks to that delivery scope. Additional framework and testing-platform
expansion is deferred; existing applicable checks and actual release gates remain.

## Platform delivery priority — decision 0153

Maintainer decision, 2026-10-22: sys-init targets Aether only. Other-OS product
support and Linux/BSD/illumos qualification campaigns are withdrawn, superseding
decision 0153's deferral. Keep useful host tooling, POSIX authoring conventions and
focused checks for changed code. Require fresh native Aether witnesses and actual
independent review for corresponding runtime/release claims. Historical platform
results retain their original scope; retiring requirements does not mark tests run.
Hosted CI remains a development delivery decision, not another runtime target.



This is the local process for contributors to the experimental sys-init checkout.
It applies now under the maintainer's standards-review request. It adopts useful
review practices from the [reviewed drafts](STANDARDS-UPDATE-REVIEW.md), without
declaring those drafts released or the entire codebase conformant.

## Simplicity in substantial changes

Apply the unreleased, locally pinned [simplicity extension](SIMPLICITY-ADOPTION.md)
in the existing change description. Name the current requirement and answer:

1. What is the simpler alternative?
2. Why is it insufficient for this requirement, or why are we choosing it?
3. What complexity can this change remove?

“None now” is valid when the necessary cost is explained. Assess responsibility,
control flow, state, ownership, failure/cleanup and whole-system cost, including
configuration, dependencies, protocols and contributor/operator steps. Identify
specific borrowed ideas and what surrounding machinery is needed or deferred.
Use current evidence; formatting, line counts or passing tests do not prove simplicity.
Routine fixes keep proportionate explanations in the ordinary workflow, without
a new template or approval gate. Triage concrete existing findings in the existing
backlog; no mass rewrite or unrequested removal follows from adoption.

## Select checks before changing behavior

Record expected behavior, forbidden outcomes and selected checks before code.
Prefer meaningful test-first work. Reproduce bugs before fixing them, or record
why deterministic reproduction is unavailable and the alternative evidence.
Record the actual sequence, never a retrospective red claim. Use root's focused
cadence for iteration and completion; broaden at integration checkpoints or when
impact is broad or uncertain. Keep domain-specific controls and native gates below.

| Change | Local check | Completion requirement |
| --- | --- | --- |
| Documentation/process | `python3 scripts/check-quality-process.py` and applicable pinned standard checker | References, scope and inventory updated; technical review; reader walkthrough for release-critical guides |
| Model or graph policy | `python3 scripts/check-runtime-model.py` | Independent expected traces, relevant mutation controls and affected final checks |
| Host lifecycle or parsing | `python3 scripts/check-host-runtime.py` | Relevant real-child failure/cleanup cases and affected final checks in the claimed development environment |
| Harness/evidence | `python3 -m unittest discover -s tests -p 'test_harness*.py'` | Missing-tool, timeout, empty-suite and identity/semantic negative controls as applicable; affected final checks |
| Pure sample-receipt and pending-view qualification | Required host Rust `sample-receipts` gate in check-all | Synthetic malformed/partial data, private-view comparison and exact omission controls; native capture/integration requires a separate fresh target witness |
| Native policy, ABI, worker or toolchain | Commands in the affected native decision/reference | Fresh pinned build and consuming QEMU cases, exact positive/negative results, unchanged-input check, compact artifact identities and affected final checks |
| Shared interface | Applicable checks above | Affected-owner review, compatibility decision and matching producer/consumer evidence; no implicit adoption from sibling success |

Current aggregate: `make check-init` from the system root, or
`python3 scripts/check-all.py --current` from `sys-init/`. This runs current source
and host gates without replaying historical native bundles. The default
`python3 scripts/check-all.py` still requires the historical audit and fails when
its retained closure is unavailable. Do not relabel that gap as passing coverage,
refresh historical manifests, or substitute host success for fresh native acceptance.
Select the current aggregate when required by root's test cadence; documentation-only
work uses the documentation row above. The command is offline and has no sibling
dependency. Each stage has a 60-second watchdog; model/host runners also
have 30-second watchdogs. Native init commands have 180-second outer bounds and
a separate guest watchdog; see the exact retained runner for the tested profile.
Required tools and versions are in each builder's pinned receipts and decision.
MacOS arm64 and the pinned Linux arm64 developer image have full-check witnesses
(decision 0151). Each applies to its recorded source/tool snapshot. SMP and physical Aether qualification remain separate; BSD/illumos product
qualification is retired. CI-provider execution is not configured.

Apply root policy for triage, test selection and integration. Failures, skipped
required cases, invalid identity and failed cleanup block the affected completion
claim. Retries diagnose a failure; they do not erase it. Retain compact commands,
input/tool/artifact hashes, outcomes and short diagnostic logs for every attempt.
Remove owned generated outputs after the run; do not create full-run archives,
copied SDKs or per-run source bundles. Existing retained evidence and maintained
regression inputs remain unchanged; never regenerate historical manifests for new code.

## Review scope and known gaps

[Current evidence limits and priorities](EVIDENCE-LIMITS.md) consolidate the
retained-audit checkpoint and separate locally actionable work from missing
artifacts, platform qualification and independent review.

The [inventory](quality-inventory.json) maps subsystems to references, test files,
oracles and evidence. It is an initial subsystem inventory, not complete public
interface or line coverage. Its structural checker verifies records and local
file destinations; it does not authenticate reviews or certify runtime behavior.
Its stdout result uses schema `sys-init-quality-check-v1`; diagnostics go to stderr
with escaped control characters. Help/version exit 0, invalid usage exits 64 and
record/integrity failures exit 1. It does not fetch or modify any input.

Python 3.10+ is host tooling; native Rust uses the recorded 1.98.0/2024 no_std
profile, and the C worker uses the recorded C11/compiler-extension profile.
The draft's C17/Rust2021 pilot choices are not consumer version mandates.
Review new or touched code against CE-01–09, relevant CP/CR/CC rules, and CD-01–04.
Preserve legacy formatting until a separately reviewed formatter migration; do
not apply pilot configurations blindly to Rust2024, generated files or libc.
Decision 0095 provisions the [scoped static gate](STATIC-CHECKS.md): Python syntax
and pinned Rust2024 formatting for two host test files. Decision 0096 adds default-group Clippy on those host harnesses and a native
boundary inventory with source-drift checks. Native/C formatting, ShellCheck,
sanitizers and complete unsafe/error-path acceptance remain gaps.

The native fixtures intentionally terminate at designated assertion results;
this is a test oracle, not production malformed-input error handling. Decision
0021 does not prove rejection cleanup. Decision 0022 supplies a consuming witness
for cleanup and one retry; decision 0023 supplies finite-budget exhaustion.
Decision 0024 supplies local cancellation; BG-040 retains real control delivery,
production timing/backoff. Decision 0025 supplies bounded R-07 dependency-loss
alignment. See the
[native policy review](NATIVE-POLICY-REVIEW.md) before extending runtime claims.
Restricted native contexts remain allocation-free
under their existing profile; the 4 KiB supervisor limit is a fixture bound, not
a distribution memory/performance budget.

## Extended and release stages

Extended fuzz/stress scheduling is **not configured**. Decisions 0146–0147 define
and implement [the local EHT-01 campaign](EXTENDED-HOST-TESTS.md). Eight seeded
orders of 54 cases passed locally (432 executions). Workload/source pins, budgets,
owned teardown, retained attempts, triage and development freshness are recorded.
Release age limits and required platforms still need release-owner decisions.
No background task is created by this document.

Any source, dependency, toolchain, configuration or plan change invalidates the
affected evidence unless an explicit identity/impact review justifies reuse.
Before a release candidate, set age limits and required platforms in its plan;
until then there is no claim that old evidence qualifies a new candidate.
Retain accepted historical evidence without automatic expiry or deletion. Define
release-support and investigation retention before publication.

Aether-dist's proposed RG-01–10 gates need actual assembly-owner review and
assembled-image execution. Component checks do not authorize release. Full
documentation inventory, manual/diagram tools where applicable, offline target
lookup, an independent reader walkthrough, license review and operational support readiness remain publication gates.
The maintainer supplied security@aethersys.org; see ../SECURITY.md. Exceptions require exact scope, owner, reason,
risk, compensating evidence and expiry; pending review is not approval. Critical
authority, corruption, failed cleanup or artifact mismatch cannot be waived into
a passing claim that relies on those guarantees.

Decision 0097 applies 180-second/4 MiB tool bounds and owned process-group
teardown to the older I/O worker builder as well. All four worker profiles
rebuild with identical ELF/envelope bytes. Tool attempts preserve running, pass,
fail, timeout, output-limit, infra-error and interrupted states in a separate
record; existing successful evidence fields stay intact.

Decision 0098 applies the same compiler bounds to standalone lifecycle and
native-supervisor builders through scripts/bounded_tools.py. Each invocation
records caller/helper source hashes, command, bounds and outcome beside its log.
All 23 supported build variants preserve exact raw/envelope bytes. This is
build supervision evidence, not execution qualification for arbitrary inputs.

Decision 0099 adds the [documentation inventory](DOCUMENTATION-INVENTORY.md) and
canonical aggregate-command mdoc source. Update the source identities and
documentation disposition when touching its recorded entry points; independent
review and target packaging remain publication gates.

The canonical [quality-check manual](man/sys-init-check-quality.1) documents the
record checker. It reads evidence and references; it does not execute linked tests
or certify reviewer sign-off. Decision 0100 adds three checker manuals with
source-matched stream/status probes and local rendering evidence.

Decision 0103 adds required synthetic standard-wrapper tests: invalid inputs
must not invoke a checker, and assertion-based reference failures must remain
failures under inherited/parent optimization. Shared releases remain immutable.

Decision 0105 requires the isolated I/O builder's captured imports to be usable
without the source checkout on PYTHONPATH. Its regression removes the helper to
confirm that an omitted build dependency cannot silently pass. Copied native
source and generated artifact identities remain separate from target execution.

Decision 0106 makes host descriptor stage/boundary contracts and the owned
documentation example part of the existing required host suite. Example execution
is explicit; this does not run arbitrary Markdown code blocks.

Decision 0107 adds bounded legacy command capture with retained log prefixes
and adjacent attempt receipts. Actual nonzero smoke exits still reach the
existing semantic checks; timeout/overflow cannot become expected rejections.
Nested compiler groups have their own bounds; full nested interruption cleanup
is not established by an outer group kill. See the decision and source manual.

Decision 0108 caps each aggregate gate's combined stdout/stderr logs at 4 MiB.
Capture preserves separate raw prefixes and reports output-limit independently
of timeout or a child test failure. The 60-second deadline covers pipe draining
and process exit. Child artifacts/hash work and detached nested groups remain
outside these bounds. See docs/man/sys-init-checks.1 and decision 0108.

Decision 0109 bounds inner host/model worker capture to 4 MiB of combined raw
stdout/stderr and 30 seconds through pipe drain/exit. Host capture failures
replay diagnostic stderr only; model failures keep passed/error fields and
include bounded prefixes in error detail. Capture exceptions clean the owned
group and reap the direct child; abrupt outer termination and detached groups
remain separate gaps. The helper is included in successful source hash maps.
See decision 0109 and the updated host/model command manuals.

Decision 0110 adds a one-second cooperative SIGINT grace before aggregate
forced cleanup, allowing responsive Python wrappers to reap separate-group
workers. The grace is additional to the gate deadline; failure identity and
log caps remain unchanged. Forced fallback covers the owned gate group only.
Unresponsive detached descendants, abrupt outer termination, deeper nesting
and pipe pressure remain explicit limits. See decision 0110 and its regression.

Decision 0111 routes SIGTERM during active main-thread aggregate capture through
the interrupted result and cooperative cleanup path, restoring the previous
handler afterward. Secondary SIGTERM during cleanup is ignored. Startup,
between-gate work, SIGKILL, repeated SIGINT and detached/deep nesting remain
outside this guarantee. Background-thread calls keep prior signal behavior.
See the aggregate manual and retained real-signal before/after witness.

Decision 0113 strictly validates static settings and boundary records before
tool lookup: exact schema/fields/types, bounded JSON/depth/collections/strings,
duplicate-key and path/digest checks. Malformed records use structured failure
without command execution. Maintained record bytes and published pins remain
unchanged; ordinary-file/atomic identity and tool closure remain BG-056 work.
See docs/STATIC-RECORDS.md for precise limits and decision 0113 for evidence.

Decision 0114 validates ordinary selected input files and symlink components
within the supplied root, bounds reads and checks file identity around them.
Standalone static checks parse captured JSON and reject changed record bytes
before success. FIFO and controlled replacement/growth/metadata cases supplement
existing tests. Hostile directory races and transitive tool closure remain
outside this result; see docs/STATIC-RECORDS.md for precise scope.

Decision 0115 adds [QUALITY-RECORDS.md](QUALITY-RECORDS.md), covering inventory,
surface/gap, snapshot-manifest and result fields. It distinguishes file/reference
checks from executed tests and independent approval. Matching-pin empty manifests,
snapshot escape and layer/count/reference controls supplement existing tests.
Strict bounded parsing, file policy and snapshot identity/closure remain BG-056.

Decision 0116 strictly validates quality inventory/manifest schemas, types and
bounds before reference traversal. Existing optional gap reference/review_evidence
fields are retained and checked. One captured manifest supplies both its digest
and parsed content. Existing stderr-only failure and success JSON contracts
remain; snapshot bytes and release pins stay fixed. Full closure/file policy
and end-of-run identity remain BG-056 work. See docs/QUALITY-RECORDS.md.

Decision 0117 requires full reviewed-snapshot file membership, rejects snapshot
symlink/special entries and limits traversal to 2,000 entries. Snapshot membership
and listed digests are repeated before success; inventory/manifest bytes must
stay identical. The retained snapshot and released pins are unchanged. This is
not an atomic snapshot; general reference/read policy remains BG-056 work.

Decision 0118 bounds record/snapshot payload reads to 1 MiB and checks ordinary
file identity around each read. General reference paths reject links and special
files without reading their content. Missing-reference error behavior remains.
Controlled replacement/growth tests do not prove atomic traversal or I/O deadlines;
see QUALITY-RECORDS.md. Published pins and retained snapshot bytes are unchanged.

Decision 0119 adds the offline-lock field/lifetime reference and required synthetic
cross-wrapper tests. Child execution is mocked in those tests; the standard gates
separately run the real pinned reference checkers. See OFFLINE-LOCKS.md for remaining
read/traversal, file-policy and verification-to-execution limits.

Decision 0120 applies E-01–08 to bounded standards-wrapper input verification:
1 MiB ordinary-file reads and 2,000-entry traversal, with controlled replacement
and special-file tests. Locks decode ASCII. Shared release bytes/pins are unchanged;
verify-to-execute identity, I/O deadlines and interpreter closure remain open.
See OFFLINE-LOCKS.md and decision 0120; no new exception or native claim is made.

Decision 0121 rechecks standards inputs before and after successful reference
execution. Persistent byte/membership changes reject; real-child controls require
exit 1 even after child success text. E-01–08 evidence is scoped to comparisons,
not atomic execution or interpreter closure. Pins and release bytes remain fixed.
See OFFLINE-LOCKS.md; independent review and remaining BG-056 work stay open.

Decision 0122 executes a private copy of hash-verified standards payloads with
Python -I -S -B and a 64 MiB staging budget. Original/staged identities are checked
and temporary files cleaned on ordinary unwinding. E-01–08 scope remains host
verification, not sandboxing or interpreter/standard-library closure. Release
pins stay fixed; abrupt cleanup, child deadlines and independent review stay open.

Decision 0123 bounds standalone reference children to 30 seconds and 4 MiB
combined raw output, with owned-group cleanup and direct-child reaping on capture
failure. Output is replayed after capture; ordinary successful bytes stay fixed.
E-01–08 scope excludes blocked output sinks, escaped descendants and abrupt outer
termination. Pins remain unchanged; see OFFLINE-LOCKS.md and retained controls.

Decision 0124 handles main-thread reference-capture SIGTERM through interruption
cleanup and reports a plain stderr diagnostic with exit 130. Previous handlers
are restored; background-thread calls are unchanged. Real-child reaping/staged-tree
controls pass in scoped host tests. Existing output exception applies; startup,
staging, postchecks and repeated-signal windows remain open. Pins stay fixed.

Decision 0125 documents native-evidence catalog fields and lifetime rules,
including gaps in strict parsing and read identity. New host controls require
catalog rejection before bundle access and listed membership for required files.
No checker/catalog/native bytes change; see NATIVE-EVIDENCE-RECORDS.md.

Decision 0126 validates native catalog JSON/fields before bundle access and
reports the digest of parsed bytes. Retained catalog/evidence bytes stay fixed;
strict receipts, ordinary-file policy and final consistency remain BG-056 work.
See NATIVE-EVIDENCE-RECORDS.md and the required catalog controls.

Decision 0127 adds ordinary catalog/manifest file reads and strict manifest
validation before payload hashing. Manifest hash and parsing use captured bytes.
E-01–08 scope excludes payload bounds, receipt validation and final consistency;
retained native evidence and pins stay unchanged. See NATIVE-EVIDENCE-RECORDS.md.

Decision 0128 bounds native digest reads to 64 KiB chunks/64 MiB files with
ordinary-file/component and descriptor identity checks. The supplied checkout root
is propagated through hashing. Semantic content reads, receipt schemas and final
consistency remain BG-056 work. Retained native bytes and pins stay fixed.

Decision 0129 routes native semantic JSON/serial/envelope reads through the
4 MiB ordinary-file reader, preserving text decoding/newlines. Controlled late
file replacements reject. Receipt schemas and hash-to-content identity remain
BG-056 follow-ons; retained evidence, native behavior and pins stay unchanged.

Decision 0130 verifies semantic buffers and receipt-correspondence digests against
the pinned native manifest map. Decoding/parsing uses the verified buffer; strict
receipt schemas and final filesystem consistency remain BG-056 follow-ons.
Retained evidence, native behavior and pins stay unchanged.

Decision 0131 requires full native bundle membership and final catalog/bundle
consistency checks. Persistent late changes reject; comparisons remain sequential
rather than atomic. Strict receipt schemas and I/O deadlines stay open under
BG-056. Retained evidence, native behavior and pins remain unchanged.

Decision 0132 applies strict bounded UTF-8 JSON parsing to all native receipt
sites, including object roots, duplicate/depth/non-finite and overflow controls.
Retained bytes and semantic oracles stay fixed; complete per-schema fields/types
remain BG-056 work. See NATIVE-EVIDENCE-RECORDS.md and the required routing tests.

Decision 0133 validates consumer native reports/cases/commands before linked
receipt access. Exact fields, bounded collections/text, digest and scalar types
are covered by retained-variant and malformed-record controls. Producer/worker
schemas remain BG-056 work; native behavior and release pins stay fixed.

Decision 0134 validates linked producer/worker/build receipt fields before use.
All retained variants and nested malformed controls are required tests. SDK
recursion and additional correspondence remain BG-056 follow-ons. Release pins,
native behavior and historical evidence stay fixed; see NATIVE-EVIDENCE-RECORDS.md.

Decision 0135 checks retained I/O supervisor and worker SDK/tool-lock/libc links.
Wrong/missing link controls supplement retained compatibility tests. Missing
historical ISOs are documented limits; SDK semantics and further envelope
correspondence remain BG-056 work. No native behavior or release pins change.

Decision 0136 validates retained I/O envelope layout and embedded correspondence.
Malformed layouts and independently changed image/supervisor controls supplement
retained compatibility checks. SDK semantics remain BG-056 scope review; no
native behavior, historical artifact or release-pin changes are made.

Decision 0137 validates direct/derived SDK fields at fixed retained paths.
Nested malformed controls and multiline patch compatibility cover all 27 retained
occurrences. Structural validation does not accept SDK semantic claims; further
correspondence, missing artifacts and independent review remain BG-056 work.

Decision 0138 binds derived SDK inputs, startup and envelope claims to retained
files and checks embedded ELF correspondence. Contradictory claims and matching
hashes over wrong payloads have controls. Missing direct artifacts remain limits;
no native behavior, release pin or historical evidence changes are made.

Decision 0139 checks producer summary counts and producer/worker dependency links.
Retained variants and contradictory fields have controls. Missing producer
artifacts and bounded source-archive member review remain BG-056 work; no native
behavior, release pin or historical evidence changes are made.

Decision 0140 verifies complete producer summary maps against bounded in-memory
source archives. Retained compatibility and malformed/resource controls apply;
no extraction occurs. Ten normalized producer source-map metadata omissions
remain explicit limits, alongside missing artifacts and independent review.

Decision 0141 compares producer source maps with verified archive inputs. Exact
historical omission scope is recorded in STANDARDS.md; tests reject changed
pins/schema/names/digests and conflicting present entries. New evidence inherits
no waiver. Full source closure and missing artifacts remain explicitly limited.

Decision 0143 bounds aggregate source snapshots with ordinary-file/component
checks, streaming digests, descriptor/path identity and selected-membership
rechecks. Compatibility and malformed/change/cleanup controls apply. Snapshot
error reporting, publication and filesystem deadline/race limits remain open.

Decision 0144 retains snapshot/report errors and atomically replaces aggregate
reports. Temporary-file cleanup, stage/omission detail, interrupted outcomes and
no success summary after publication failure have controls. Startup/output-pipe/
fatal-signal and filesystem durability/deadline limitations remain open.

Decision 0145 handles aggregate output-directory startup and broken output pipes.
Real pipe controls distinguish saved check results from summary delivery failure;
progress failure stops later gates. Fatal/repeated signals, blocked I/O and failed
descriptor redirection remain limits; no global signal policy is changed.

Decision 0147 implements and locally executes EHT-01 outside the normal gates.
Exact plan/corpus/implementation identities and worker IDs/counts are checked;
replay is separate from full qualification. Failure controls and capture cleanup
regressions apply. Scheduling and other-platform/independent review stay open.

Decision 0148 retains a real exact-seed replay and records failed Linux environment
startup separately from test failures. Neither replay nor VM startup counts as
full campaign or additional-platform acceptance. Independent review remains open.

Decision 0149 extends EHT-01 to the pinned Linux arm64 container with matching
plan/corpus/implementation and all 432 ordered executions. The normal ten-gate
refresh remains macOS; broader Linux gates and other platforms remain separate.

## Historical Linux full-check blocker — decision 0150

This chronology records earlier development checks, not a current instruction to
provision Linux/BSD/illumos support. Other-OS product requirements are retired.

The corrected full-check attempt passes standards, experience, distribution and
quality, then blocks at the missing Linux-aarch64 rustfmt identity. The cached
image also lacks rustup. Separate native-evidence/model/host diagnostics pass;
they do not complete the aggregate. A mocked static-input test now explicitly
selects its fixture platform; real tool tests remain required. Provision the
pinned Rust 1.98.0 compiler, rustfmt and Clippy offline and review their Linux
identities before adding platform entries. Existing release/tool pins stay fixed.
Use a private writable /work/out for sample artifacts, alongside read-only source.
Retain initial snapshot/output-mount mistakes separately from tool blockers.
[Evidence](evidence/linux-development-checks-2026-09-07/README.md) preserves attempts.

Decision 0151 provisions Linux Rust 1.98.0 from verified official archives and
adds Linux formatter/Clippy identities while preserving macOS and release pins.
Dependency setup is separate from network-disabled qualification; the Linux
linker image, packages and private tool homes have recorded identities.

Decision 0151 resolves the Linux tool blocker: all ten gates pass with the same
Rust 1.98.0 version and added Linux rustfmt/Clippy identities. The separate linker
image and installed tools are pinned; qualification ran with networking disabled.
See [Linux development setup](LINUX-DEVELOPMENT.md) and
[evidence](evidence/linux-rust-tools-2026-09-07/README.md). Earlier failures remain
retained. Other-OS qualification is retired; hosted CI and independent review remain separate.

Decision 0152 verifies OCI reload, exact image identity, stable Rust tool identities
and all 432 EHT-01 executions offline. Local reuse is now witnessed; independent
review and additional-platform environments remain external inputs.

Decision 0154 supplies fresh native witnesses for errno history retention at all
three sampling positions, with exact omission controls and legacy byte comparison.
No source-format or shared API migration is implied; closed terminal inspection
and whole-cut retirement remain follow-ons.

Decision 0155 qualifies closed terminal storage inspection and denied replay with
fresh Aether execution and four exact omission controls. No public API or reset
is introduced. See its decision/evidence for retained failed revisions and the
unchanged producer source-closure limitation; no independent sign-off is claimed.
