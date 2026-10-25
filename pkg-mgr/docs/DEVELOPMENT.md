# Development checks and review

For pkg-mgr contributors working on the experimental private-root host prototype.
Read the pinned [method](../../.agent-temper/METHOD.md), root [engineering
policy](../../PROJECT.md) and root [work selection](../../.planning/STATE.md).
The selected bounded record owns scope and continuation; component records retain
details. Root [DEVELOPMENT](../../docs/DEVELOPMENT.md) governs focused cadence,
compact retention and integration after required checks and separate review;
affected-owner, native and release gates remain. Run commands from `pkg-mgr/`.
POSIX sh and GNU Make 3.81+ are the implementation baseline; Python 3.10+ is the development-tooling baseline (this review tested 3.14.7).
Aether is the only product target; host checks support development, without a required Linux/BSD matrix. The reviewed draft identities are in
[standards-review.json](standards-review.json); this is a review snapshot, not a
released standard pin. Builds never read or execute a moving sibling checkout.

## Change selection

Apply root policy for test selection, failure triage, retention and integration.
Before behavior changes, state the requirement, host/native profile, independent
oracle, forbidden outcomes, interfaces and test commands in the owning bounded
record. Prefer meaningful test-first work. Reproduce bugs before fixing them,
or record why deterministic reproduction is unavailable and the alternative
evidence. Record the actual sequence without retrospective red claims. The
[subsystem inventory](development-inventory.json) maps source, references, tests and
known gaps. Update it for new commands, formats or subsystems. Preserve exact machine
output, exit status, boot markers and domain-owned ABI values.


### Simplicity in substantial changes

The explicitly adopted [SE-01–SE-05 snapshot](evidence/simplicity-adoption-2026-09-07/snapshot/SIMPLICITY.md)
extends the reviewed coding baseline. In the existing change description, answer:

1. What is the simpler alternative?
2. Why is it insufficient for this requirement, or why are we choosing it?
3. What complexity can this change remove?

Name the current requirement. If borrowing, identify the specific proven idea,
the problem it solves and mechanisms needed or deferred; do not inherit an entire
framework by association. Assess coherent responsibility, readable control flow,
state/ownership/effects, failure/cleanup and total implementation, integration,
operation and maintenance cost. Include algorithms, configuration, protocols and
dependencies where relevant. Keep bounds and security checks; never replace vetted
crypto or subtle parsers just to reduce dependencies. Use evidence for claimed
resource/performance benefits, not arbitrary function/file length limits.

"None now" is valid for question 3 when the required cost is explained. Small fixes
retain the ordinary brief explanation and selected checks; no second review system,
mandatory extra form or separate design document is added. On the next real design
change, record this scoped assessment with its normal review and actual outcome.
Triage existing findings in ROADMAP by delivery impact/risk, preserving immutable
releases, failed evidence and useful compatibility paths until a scoped replacement
is justified. See [adoption and verification](STANDARDS.md) for snapshot identity.

### Selected checks

| Stage/change | Commands and expected scope | Budget and prerequisites |
| --- | --- | --- |
| Documentation/process | `python3 tests/check-development.py`; `sh tests/check-standards.sh` | 60 seconds each; Python, sh; offline file destinations and syntax, not prose/anchor/reader certification |
| Shell changes | `python3 tests/check-development.py --lint PATH ...` | 60 seconds per tool; ShellCheck 0.11.0 required, no auto-install or hidden configuration |
| Before merge: runtime/build/parser changes | Affected inventory cases; `sh tests/check.sh` at broad checkpoints or when no safe subset exists | 10 minute operational deadline; Python, sh, GNU Make, standard host utilities; sixteen fixture scripts, no native execution |
| Recipe/compiler changes | `sh tests/bytecount-integration.sh` or `sh tests/zlib-integration.sh` as affected | 10 minutes; reviewed local compiler/source prerequisites in recipe docs; retained private roots |
| Native interface/harness changes | `python3 tests/native-launch-integration.py --help` or memory counterpart, then exact documented invocation | Set a total budget in the run plan; existing per-process QEMU deadlines and owned process cleanup remain required; pinned source/images, QEMU and tool closure |
| Release candidate | Exact artifact-bound supported-target plan and applicable shared gates | Blocked until missing target, provenance, documentation and recovery evidence is supplied |

Budgets above are maintainer triage deadlines for existing host workloads, not performance
claims. `sh tests/check.sh` now enforces a 600-second whole-suite deadline through a
Python development watchdog. It owns a process group, sends TERM then KILL during
cleanup, propagates failures/signals and retains suite.log/result.txt in its printed
private run root. A successful leader leaving descendants fails with 125; timeout
uses 124. Children must remain in the group; this is not hostile-process confinement.
The internal check-fixtures.sh entry bypasses the watchdog and is not the release
validation entry point. CI/scheduled deployment remains separate. Individual
Python process calls in the new static checker use 60-second deadlines. Do not claim
CI deployment or scheduled coverage from these local commands.

## Coding scope and lint migration

Apply the reviewed CE/CS/CP/CD/CA design guidance to new/revised first-party work:
validate bounds and types before use; keep subprocess arguments separate; define
ownership, partial effects and cancellation; use private roots; check meaningful
statuses explicitly. `set -e` and path normalization are not safety proofs. Preserve
upstream and generated style. Do not introduce a formatter or runtime dependency
without a scoped decision and tool identity.

The initial ShellCheck 0.11.0 audit reported 112 diagnostics across existing shell
files. That historical migration baseline is resolved by the later scoped reviews
and the current 38-file check recorded in [the rc1 review](STANDARDS-RC1-REVIEW.md).
The intermediate 98/62 counts below remain historical evidence, not current findings.
Raw findings are retained in the review evidence. Changed shell files
must pass the explicit lint command, or receive a narrow reviewed exception recording
rule, exact lines, rationale, owner, risk, compensating tests and expiry milestone.
No blanket exclusions are installed. Revisit each affected finding before merge;
triage path/transaction findings first. No known authority or data-loss failure may
be waived. The configured active-shell check is clean with the three exceptions below;
complete coding/security/portability conformance remains unproven.

The normal suite now runs `python3 tests/check-development.py --lint-all`, checking
all active shell files with ShellCheck 0.11.0 as well as source syntax and inventory
references. Missing/wrong-version ShellCheck fails this required development gate.
The standalone development checker without --lint or --lint-all still reports lint
as NOT RUN; it is only a documentation/syntax subset. No check here certifies prose,
complete threat coverage, concurrency safety or all interpreter versions.

## Evidence and remaining gates

Retain compact commands, tool versions, platform, deadlines, source/patch and
artifact hashes, expected/observed outcomes, timestamps and short diagnostic logs
for every attempt. A dirty checkout needs exact input hashes; HEAD alone is
insufficient. Link results from the owning record and remove owned generated outputs
after the run; do not archive complete runs, SDKs or per-run source trees. Existing
frozen records and maintained regression inputs remain unchanged. A changed input,
configuration or plan invalidates affected evidence. Preserve failure, timeout,
skipped, infrastructure-error and unknown separately; failed cleanup and retries
remain failures. Keep compact evidence for active claims. Production retention
through the support/security period needs release-owner policy before publication.

These gaps block broader claims; they are not approved exceptions:

- **Extended testing:** no deployed schedule or bounded fuzz/soak driver. Before
  adopting scheduled coverage, define parser corpora, daily bounded parser/transaction
  exploration and weekly soak workloads, owned cleanup, seeds, budgets and triage.
  Evidence must match the candidate; choose maximum age before release testing.
- **Targets/recovery:** Aether full-storage and physical
  power-loss recovery, concurrent writers, authentication/freshness and assembled
  target installation remain unproven or outside current scope.
- **Documentation:** current Markdown references are experimental. The three first-party mdoc pages have host rendering, staged lookup and curated
  example evidence. Actual release packaging, complete semantic coverage, independent
  onboarding/recovery reader walkthrough and publication approval remain pending.
  New diagrams need source, text alternative and pinned renderer evidence.
- **Review:** reviewer identities and approval must come from real review. The
  inventory is a subsystem starting point; complete public-surface coverage and
  reader/technical review remain publication gates.

For an explicit read-only drift check (never part of the offline build), run:

```sh
python3 tests/check-development.py --standards-source ../../Aether-standards
```

A changed/missing reviewed document fails with review required; it never updates
our snapshot or executes sibling code. New files are discovered through review of
the catalog/registry; this checks the recorded files, not the whole sibling tree.

On a standards update, compare the canonical catalog and release registry with the
three local locks; inspect applicable draft changes, record exact reviewed identities,
and update local scope/gaps. Adopt a new immutable release only through explicit
vendor/lock updates after verification and affected-owner review. Never regenerate
a release pin merely to repair a failed integrity check.

The canonical [2026-09-05 approval](../../../Aether-standards/docs/APPROVALS.md)
records maintainer approval of all four draft profiles, including Markdown/mdoc/
Mermaid defaults. This supersedes older pending content-approval wording. No repeat
approval is needed; independent review, implementation coverage and immutable release
assembly remain distinct. Verify the linked approval receipt before release adoption;
it was not yet present during this concurrent update.

The [2026-09-06 replacement review](evidence/host-replacement-faults-2026-09-06/README.md)
brings the remaining shell findings to 98. Replacement and binary-fixture files
pass scoped lint; two injected storage-operation cases pass. Actual full-storage
and durability qualification remain separate.


The source-metadata fixture now includes 71 deterministic mutation/control cases
(seed 20260906), with five seconds per invocation. Inputs include required-key
omission/duplication/empty values, order permutations, unknown keys, malformed
size/hash fields and shell-looking/64-KiB URI values. Exact statuses and diagnostic
lines are checked; target bytes and a command-injection marker must remain unchanged.
This is a bounded regression corpus, not general fuzzing or a parser input-size cap.
Each attempt retains its input records, stdout/stderr and results.json under a
printed private root. It does not certify snapshot freshness or signature policy.


The [trust parser review](evidence/trust-parser-review-2026-09-06/README.md) makes
mk/verify-metadata.sh lint-clean without suppressions; the repository audit now has
62 remaining findings. Source-record differential tests preserve exact output and
status. Descriptive metadata validation does not establish freshness or signer trust.


## Reviewed lint exceptions — 2026-09-06

The final shell review has zero unsuppressed diagnostics. This establishes the
configured static check, not complete security or portability review. The pkg-mgr
maintainer owns these narrow migration exceptions; this implementation review does
not invent independent release approval. Revisit at ShellCheck upgrades, changes to
these lines, or the host-preview release review, whichever happens first.

| Rule and exact scope | Reason, risk and compensating checks |
| --- | --- |
| SC2329: `cleanup` definition in bin/pkg-mgr | Invoked by the EXIT trap. False unused-function finding; removing it would lose cleanup. CLI lifecycle/output fixtures exercise cleanup and retained-output paths. |
| SC2329: `interrupted` definition in bin/pkg-mgr | Invoked by INT/HUP/TERM traps. False unused-function finding; signal behavior is verified by twelve wrapper/group cases and output-delivery controls. |
| SC2086: `set -- $length_bytes` in mk/aether-boot-v2.sh | Exactly four decimal bytes from od; intentional word splitting has no glob metacharacters. Input must already have a valid bounded header/length. Boot-v2 positive/malformed-length fixtures exercise this path. Revisit if the producer or byte decoding changes. |

All directives are adjacent to the single function/statement they cover. There is
no file-wide disable, hidden .shellcheckrc or blanket finding baseline. No known
memory, authority or data-integrity defect is waived. Mechanical CDPATH quoting,
explicit conjunction guards and quoted literal labels preserve the existing contract.
Make-exported phase variables are used directly after root validation; unused aliases
and an unused blob-row size binding are removed/marked as intentionally unused.


## CLI manual checks

`man/pkg-mgr.1` owns the command/option reference; docs/CLI.md owns workflow and
validation context. The normal suite runs tests/check-manuals.py: help/manual name
coverage, required sections and curated positive/negative private-root examples.
Available mandoc is used for strict lint, HTML and 60/80-column terminal output;
missing optional rendering is explicitly NOT RUN. Before release, use
`python3 tests/check-manuals.py --render-required` to fail on a missing renderer.
Tool binary identity, platform, source hashes, examples and rendered outputs are
retained under the printed run directory. This checks names and curated behavior,
not completeness of every option's semantics or authentic reviewer approval.
Actual release packaging/target lookup and independent technical/reader
walkthroughs remain pending. No new package-manager runtime dependency is added.


The package-state manual adds exact coverage of the 19 evidence keys in schema
order, required sections, world/explicit-root and no-orphan examples, and duplicate
world rejection without partial output. Both manuals are linted/rendered and staged
under private share/man/man1 and man5 directories. Host `man -M` lookup and display
must select the staged pages. `--render-required` now requires both mandoc and man;
normal developer checks report unavailable optional rendering/lookup explicitly.
New pages must be added to the checked manual inventory; unregistered pages fail.
This is a host staging witness, not a produced release package or native lookup.


The binary-format manual covers the descriptor and target keys in exact order,
bundle inventory, file modes, dependencies and publication/recovery limits. All
three pages are now checked. Release documentation validation requires
`python3 tests/check-manuals.py --render-required --binary-example`. The extra flag
runs the compiler-dependent bytecount lifecycle and compares the actual bundle
inventory, ordered keys and four digest bindings with the documented format. The
normal compiler-free check reports that example as NOT RUN. This does not certify
remote authenticity, native execution or independently reviewed release packaging.


## Source closure checks

`python3 tests/check-source-snapshot.py` creates an opt-in development snapshot,
checks repeated archive byte identity and verifies host-tar extraction against exact
input bytes/modes. It is excluded from the normal suite because assembling all
historical evidence is a separate release-preparation operation. Run the normal
suite and required manual/compiler checks from its extracted tree as described in
[SOURCE-SNAPSHOT](SOURCE-SNAPSHOT.md). Archive repeatability, relocated execution,
independent review and public-release approval remain distinct claims.


The opt-in `python3 tests/check-host-setup.py` records required tools for the first
macOS arm64 preview profile, including Apple-selected binaries behind command
shims. Missing prerequisites and wrong ShellCheck versions fail. This does not
restrict the normal portable fixture runner, install tools or qualify untested
toolchain versions. See [HOST-SETUP](HOST-SETUP.md) for evidence limits.


`python3 tests/check-public-source.py` is an opt-in full-checkout release-preparation
check. Its explicit source mapping, documentation-edit receipt and archive manifests
are described in [PUBLIC-SOURCE](PUBLIC-SOURCE.md). Validate the extracted candidate
with the normal suite, required manuals/compiler example and host preflight; assembly
success alone is not acceptance. No package runtime dependency is introduced.


## Origins byte-handoff fixture

The normal gate runs `python3 tests/origins-source-handoff.py` before the sixteen
isolated shell fixtures. It uses a pinned in-repository producer snapshot and
standard-library host Python, with no sibling/runtime dependency. Thirteen bounded
cases check the real source verifier, failed-export gating and private state
preservation. Frozen producer shell is explicitly linted. Evidence is retained
under a printed .pkg-mgr-live-origins-* root. See [consumer scope](ORIGINS-CONSUMER.md)
and [evidence](evidence/origins-byte-handoff-2026-09-06/README.md). No authenticated
source admission or complete native tool/bootstrap qualification is implied.


## Origins source-record inspection

The normal gate runs `python3 tests/origins-source-records.py` alongside OC-H1.
The development-only inspector uses Python standard-library JSON with pre-parse
byte/depth limits and an external original-byte hash pin. The bounded corpus
checks inertness, structural/canonical rejection and file/output boundaries.
See [the interface and limits](ORIGINS-SOURCE-INSPECTION.md). No runtime dependency,
source admission or full schema/producer agreement follows from this host result.


## Origins declared closure

The normal gate also runs `python3 tests/origins-closure-cases.py`. The local host-review
consumer verifies a pinned synthetic package graph and every declared object with
explicit mapping/profile/budget controls. [Contract](ORIGINS-CLOSURE.md). No package
execution or real SDK completeness is claimed; runtime/shared adoption stays pending.


## Standards follow-up — 2026-09-07 UTC

[The local test plan](TEST-PLAN.md) now defines critical-case mappings, planned
extended cadence, workload/seed/budgets, triage, seven-day host evidence freshness
and change invalidation. The development gate validates eleven critical-case
locations; its own positive and ten rejection controls run in the normal suite.
This is a bounded mapping, not complete case coverage or evidence of scheduled runs.

[The reader procedure](READER-REVIEW.md) maps the 13 CLI commands, seven options
and primary formats to canonical references, with actual review still pending.
[Security reporting](../SECURITY.md) now routes to security@aethersys.org; triage
assignment and support commitments remain open.

The first-party zpipe source passes the candidate C17 selected-diagnostic syntax
check against available host headers; [evidence](evidence/standards-followup-2026-09-07/zpipe-c17.json)
records the command/compiler/source. This changes no recipe compiler flags or
formatter policy and supplies no pinned dependency, sanitizer or native evidence.
Python 3.10 was not found on PATH; minimum-version execution remains not-run.
