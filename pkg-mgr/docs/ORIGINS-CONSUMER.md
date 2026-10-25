# Aether-origins consumer boundary

Status: pkg-mgr engineering review and proposed experiment, 2026-09-06.
The OC-H1 host byte fixture below is implemented; no runtime source adapter, fresh
eligibility, base admission or shared-profile acceptance is established. Original work: SPDX-License-Identifier: BSD-2-Clause.
Exact reviewed inputs and validation are retained in
[the review evidence](evidence/origins-consumer-review-2026-09-06/README.md).

## Responsibility and review disposition

Aether-origins supplies source collection, object retention and signed publication.
pkg-mgr owns consumption policy, execution, local state and installation. Userland
owns base membership and provider selection. sys-init owns service activation;
Aether owns native authority and storage mechanisms. This split is suitable for a
bounded local experiment; central ownership/source-profile adoption remains pending
in Aether-standards. Published Foundations/Distribution bytes are unchanged.

The OR-02 proposal is directionally compatible with the shell/make baseline, but
requires changes/clarification before a source package can be admitted. This is an
agent-authored consumer review, not independent reviewer sign-off, origins agreement
or maintainer release approval. No message or change was sent to a sibling project.

## Findings requiring disposition

| ID | Observed contract mismatch | Requested resolution / acceptance |
| --- | --- | --- |
| OC-01 | origins-source-v1 uses namespace/name; mk/check-root.sh rejects slash in PKGNAME | Keep repository identity and package ID intact. Define an explicit collision-checked mapping to local package names and bind it to local selection policy. Never silently strip namespaces. Initially test one explicitly mapped package; competing mappings reject. |
| OC-02 | Logical paths use lowercase tokens only; Makefile, LICENSE and uppercase upstream paths cannot be represented directly | Define whether paths are virtual input labels or preserved materialization paths. If labels, provide explicit reviewed mapping; if paths, revise the grammar and collision rules. Do not lowercase signed paths. Test case-distinct names on the selected filesystem; reject unsupported materialization. |
| OC-03 | Record object references permit 1 GiB, but OR-03 and the restricted TUF probe permit 16 MiB | First byte-handoff profile is capped at 16,777,216 bytes per object. Check signed size before transfer. Larger inputs are unsupported, not chunked/truncated or silently fetched elsewhere. Measure actual SDK/source closure before raising limits. |
| OC-04 | Dependencies are unique by package and have one build/target role | Clarify same package needed in both roles, host tools versus code-generation target, and cross-toolchain identity. First fixture has no dependencies; it cannot qualify the general graph. Reject conflicting role/identity descriptions rather than dropping one. |
| OC-05 | Release-map, SDK, target-profile and review/evidence schemas remain opaque | Agree exact versioned inert formats, traversal/bounds, signed target bindings and userland selection evidence. Matching opaque hashes alone cannot establish complete closure or target support. |
| OC-06 | Input records have no materialization-mode or entry-point invocation policy; pkg-mgr recipes/helpers can run arbitrary code | Specify private tree layout, modes and explicit helper invocation before executing recipes. Do not transfer store mode 0400 into installed-file metadata or add executable permissions implicitly. Require pinned shared helpers and separately authorized execution. |
| OC-07 | Optional TUF probe returns a verified path and relies on caller time/cache; pkg-mgr's research snapshot helper can exit 0 when minisign is absent | Neither result is fresh source eligibility. Introduce a separately reviewed structured consumer result with all required predicates and current policy/state binding. Preserve existing helper outputs/exits. Missing verifier must reject the new strict path. |
| OC-08 | OR-02 describes delegated publishers; the restricted TUF profile rejects even empty delegations and bounds root advances from original enrollment | Treat this as a separately named top-level-only experiment, not full OR-02/overlay adoption. Agree lifetime budget/recovery behavior without resetting history. General delegation and overlay eligibility remain unsupported. |

The source JSON parser is also a real implementation dependency: do not translate
JSON with ad hoc shell/awk or execute make to read metadata. Bound bytes and nesting,
reject duplicates/unknown fields and verify original canonical bytes. Evaluate a
narrow host development parser first; no Python package-manager runtime requirement
is selected here. Current source.kv remains a separate descriptive byte-check format.

## Proposed admission sequence

This is a semantic contract for owner review, not a new wire format or command.

1. Obtain explicit local repository enrollment and package selection. Bind initial
   root identity, exact release/map/record references, local package mapping,
   profiles/options and policy generation. A URL/name supplied by a mirror has no
   enrollment authority. Reject unknown required capabilities before execution.
2. Start from the current trusted state and credible UTC uncertainty interval.
   Authenticate publication metadata using a reviewed verifier. Preserve newer
   authenticated metadata floors even if later payload admission fails.
3. Resolve the entire selected source/recipe/helper/dependency/SDK/license/evidence
   closure using the pinned map. Enforce per-object and aggregate budgets, identity,
   path/type and graph rules. No fallback to another release, provider or URL.
4. Transfer verified objects into an owner-controlled private cache, retaining the
   expected digests from authenticated references. Rehash the copied bytes; never
   derive a replacement expected digest from newly downloaded contents. Partial
   output or unsuccessful producer status is not a completed cache object.
5. Revalidate policy, selection, trusted-time interval and state generation. Commit
   required trust-state advances under the separately specified storage contract.
   Only after known completion can the consumer return fresh eligibility.
6. Bind that outcome to the same bytes and execution intent at use time. Only then
   can a separately authorized pinned recipe run. Build, stage, register, install,
   boot selection and service activation remain distinct operations.

Inspection/integrity success, fresh eligibility, execution authorization and
installation completion must be distinguishable outcomes. An outcome record is
an observation, not a bearer permission that arbitrary files can forge. The final
consumer must validate trusted provenance/current state instead of trusting a
caller-provided success flag. Exact field names and exit codes remain unsettled.

## Trust state, time and failure boundary

Trust state is separate from package records, world and origins' byte-store marker.
At minimum it binds repository enrollment/root history, accepted role versions,
selected release identity, policy/state generation and trusted-time floor/provenance.
A lower local package version deliberately selected for historical work must not
lower the accepted security-metadata floor. Re-enrollment is not routine recovery.

Use one owned writer or explicitly reject conflicting updates. Define metadata
cache versus committed authority, pending intent, durable write/flush ordering,
restart reconciliation and storage errors before returning strict success. A
rename or SIGKILL fixture cannot establish power-loss durability. Disk-full,
uncertain commit, stale/corrupt backup and lost history block fresh eligibility;
retain evidence and any known newer floors. Do not repair by trusting mirror state.

The owner must provide an independently authenticated recovery checkpoint or other
reviewed anti-rollback authority after lost state. The exact mechanism is open;
this document does not require a TPM or invent an existing Aether storage service.
The roots/time/version floors cannot be secured against rollback solely by another
file on the same rollback-prone disk. State the operator/hypervisor trust assumptions.

Time inputs need provenance, acquisition age, uncertainty and a retained floor.
An interval supplied by test code is not a trusted clock. Require all relevant
metadata to remain valid throughout the interval and recheck at final admission.
Unknown time, regression and expiry reject. Historical inspection is explicitly
non-fresh, does not mutate trust state and does not authorize installation.

Failure may retain verified metadata/cache and private diagnostic scratch. It must
not publish eligibility, execute recipes, change installed records/world, delete
payload or activate services. Unknown delivery requires reinspection, not assumed
success. Existing pending replacement guards remain unchanged.

## First bounded experiment: OC-H1

Implemented host fixture: offline byte handoff only, with explicit host fixture
pins and a frozen origins exporter snapshot. No origins JSON parser or TUF adapter
is needed for this first seam. It does not admit dash or any other base package.
Use a tiny synthetic checked-in payload, not a new package/provider choice.

Keep three distinct owned locations: origins store (creates nonexistent root),
consumer transfer scratch, and an initialized pkg-mgr private fixture root beneath
its checkout (existing empty 0700 directory). Never reuse markers or point pkg-mgr
at the origins store. Invoke only the frozen, inspected exporter; not a moving
sibling script or a command read from a receipt.

Capture exporter stdout into a newly created private file. Check exporter status,
then use pkg-mgr's existing verify-source operation with externally pinned source.kv
identity. Report integrity-only success. No make invocation, archive extraction,
recipe evaluation, registration, trust-state write or successful fresh-eligibility
result is permitted. A failed export may leave a private partial file for evidence;
it is never published as admitted input. No output modes are used as authority.

| Case | Independent oracle and forbidden outcome |
| --- | --- |
| Exact round trip | Copied bytes equal the checked-in payload and external size/hash; existing source verifier succeeds; installed/trust state unchanged |
| Same-size mutation after export | Existing verifier reports source hash mismatch; no recalculated expected hash and no downstream execution |
| Truncated/wrong-sized bytes | Existing verifier reports size mismatch; no source consumption |
| Producer fails after partial stdout | Export failure recorded separately; partial bytes never qualify even if a verifier could read them |
| Missing exporter or hash provider | Tool/infrastructure failure, not a semantic identity-rejection pass |
| Symlink/special-file or unsafe root | Reject according to frozen producer/consumer contract; never dereference outside owned roots |
| Retry identical identity | Same bytes and explicit outcomes; no overwrite of unrelated cache/state |

Before implementing OC-H1, pin the actual producer files/dependencies and fixture
input, state time/resource budgets, and run the standards gate. Retain positive and
semantic-negative logs plus before/after state identities. The full host suite is
required if runtime or harness behavior changes. A passing OC-H1 closes byte transfer
only; actual OR-04 package admission still needs OC-01–08 disposition, owner-approved
base/source/license/SDK closure and matching strict consumer evidence.

## Compatibility and follow-up

Do not replace mk/pkg.mk, package state v2, existing source/snapshot metadata,
binary transport or recovery contracts. Source distribution is the current origins
scope; existing binary evidence stays intact. No solver, daemon, deletion, native
installation or broad overlay support is opened by this review.

OC-H1 now passes 13 host cases. Next pkg-mgr work is the bounded inert source-record
inspection contract/parser, after OC-01–06 format disposition; strict eligibility
separately needs OC-07–08 trust/recovery agreement. Origins and standards owners can use the findings above
for OR-02/04 revision; userland supplies actual admission/closure evidence. Those are
pending handoffs, not instructions already delivered or accepted. Native shell,
filesystem and target admission remain separate release blockers.

## OC-H1 execution checkpoint

Run `python3 tests/origins-source-handoff.py`; the normal `sh tests/check.sh`
also runs it before the isolated shell fixtures. The exporter, contract, license,
payload and source.kv are retained under fixtures/origins-exporter with pin.json.
The harness verifies those bytes before execution. It initializes a private root
by invoking check-root.sh directly, without make/recipe evaluation.

Thirteen cases pass, including a complete correct payload from a failing producer
that must never reach the verifier. Missing hash tooling is a distinct consumer
error. Symlink and FIFO denial use the real frozen exporter. Evidence and the
initial corrected setup failure are in
[the OC-H1 results](evidence/origins-byte-handoff-2026-09-06/README.md).
This closes the byte-only test seam, not OR-04 package or strict trust acceptance.


## OC-H2 inspection checkpoint

The [host inspector](ORIGINS-SOURCE-INSPECTION.md) now resolves OC-01–06 handling
within a read-only boundary: preserve IDs/paths, validate declared roles, report
transfer-size limits and keep opaque closure/profiles unresolved. It does not
resolve general materialization or admission contracts. Producer changes remain
pending owner agreement. No source-record revision or shared pin changed.


## OC-H3 local handoff proposal

The [declared-closure profile](ORIGINS-CLOSURE.md) supplies concrete synthetic
release-map, selection/mapping, SDK/profile and evidence schemas with an executable
consumer. These are review formats, not accepted origins/userland contracts.
Complete declared input verification remains separate from real SDK completeness,
base selection, publication authenticity and local execution authority.
