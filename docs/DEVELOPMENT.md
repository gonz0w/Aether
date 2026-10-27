# Development and standards checks

> Public consumer routing: apply [PROJECT's cutover rule](../PROJECT.md#public-onboarding-cutover).
> After verified onboarding/migration, “canonical work record” in this guide means
> the owning GitHub issue. STATE is navigation and legacy queues are read-only.
> Before cutover, only the approved bootstrap record owns onboarding. Execution,
> review, source-freeze, resource and acceptance requirements below stay binding.
> Local qualification receipts and the whole RC1/ADP-01 packet are excluded from
> this snapshot; required missing evidence remains blocked coverage.


## Public input availability

The [public-source boundary](PUBLIC-SOURCE.md) identifies private standards,
review snapshots, imported hooks and qualification inputs omitted from this
checkout. Retained adoption records and lock hashes do not supply those bytes.
Ordinary public prose and self-contained kernel model changes use the available
local rules and affected contracts. If a selected change requires private
normative inputs, involve the owner and obtain the exact inputs before dependent
work; do not reconstruct their clauses or treat their absence as an exception.

The hosted jobs are **Source integrity** (Agent Temper digests, selected
Python syntax/JSON and conventional PR titles) and **Kernel models** (five
self-contained pure Zig roots plus the complete three-method AF09 actual-body
suite). Both jobs retain a five-minute whole-job timeout. The AF09 command is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_native_af09_drain.py -v
```

These are bounded source checks. `zig build test`, the
workflow inventory checker, standards wrappers and `make check-system` retain
private-input prerequisites and are blocked without them. `zig build` retains
its documented boot dependencies. No native or full host qualification follows
from hosted jobs. The detailed commands below describe their original applicable
scope; select them only with their required inputs and execution authority.


The system source tree now includes `userland/`, `sys-init/` and `pkg-mgr/`.
An integration change may span these directories in one branch. Read their local
guidance and keep runtime responsibilities distinct. Root test cadence and
retention rules apply across the tree; older component archive recipes do not
require keeping full runs. See [REPOSITORY](REPOSITORY.md) for commands and history.

For contributors to the experimental x86_64 QEMU POC. Read root
[PROJECT](../PROJECT.md) for recorded engineering policy and the pinned
[Agent Temper method](../.agent-temper/METHOD.md) for the work lifecycle.
[STATE](../.planning/STATE.md) is compatibility navigation. After verified
cutover read the owning issue and discussion before implementation. [ROADMAP](../.planning/ROADMAP.md)
holds capability gates, not executable assignments. Run commands from the
repository root after the pinned setup in [README](../README.md). This workflow
provides the local OS process and checks under that policy. The maintainer has
approved Documentation, Testing, Coding and Distribution v0.2.0 content. Publication and formal immutable version-pin adoption remain
pending; do not repeat the standards-content approval request. Existing released pins still apply.

## Before changing behavior

1. Read the canonical issue selected under root PROJECT cutover policy, root
   PROJECT, the affected component guidance, the authoritative interface reference
   and, when the affected contract requires them, the exact private standards
   inputs with the owner. Confirm finite scope, acceptance, readiness
   and required authorization in that record before implementing. Use the
   [review record](STANDARDS.md#updated-drafts-and-local-process) to distinguish
   released rules from reviewed draft guidance.
2. In the canonical work record, record the requirement, allowed result, forbidden
   outcomes, affected owner/profile, and intended tests **before** implementation.
   Link that record from the PR or review rather than maintaining a second plan.
   Include authority, buffer/handle ownership, cleanup, concurrency, quotas and
   compatibility. Select tests by affected interfaces and consumers, not just paths.
3. State documentation impact. Update the reference and examples with behavior.
   Keep proposed, experimental and accepted behavior distinct. Use Markdown for
   narrative, mdoc for new manuals, and accessible Mermaid source when useful.
4. Review new dependencies, unsafe/FFI/assembly boundaries and build flags. Record
   origin/version/digest/license, necessity, feature closure, offline setup, removal
   path and resource cost. Document pointer validity/aliasing, panic/unwind and
   synchronization obligations at each new or revised unsafe boundary.

No new runtime framework or language migration is required. Existing Zig kernel,
Rust services and C conformance-client ownership remain unchanged.

## Security during POC development

Security is a primary design outcome. Apply this checkpoint prospectively within
the existing task or PR review; ordinary changes need only a few sentences, not a
separate security document or a retrospective hardening campaign.

For new or changed behavior, identify:

- The untrusted caller or input, the protected state, and the authority required.
  Note any new trusted service, dependency, unsafe boundary or shared state.
- What must remain true under malformed input, stale authority, partial progress,
  peer failure or resource exhaustion, selecting the cases relevant to the change.
  Include ownership and cleanup when execution can be interrupted or retried.
- The focused tests that demonstrate those properties, and what they do not cover.
  Select fuzzing, state-machine or concurrency tests when the new input or lifetime
  complexity warrants them; fixture counts alone are not security assurance.
- Any deferred protection or validation, its present exposure, and the concrete
  trigger for revisiting it, such as broader caller access, an ABI commitment,
  persistent data or physical hardware. Keep follow-up in the canonical work
  issue rather than a parallel security backlog; link any
  lasting interface requirements from that record.

Use this review to avoid expensive design rework before interfaces and ownership
become established. Do not expand a feature into unrelated legacy cleanup. A known
authority bypass, corruption or unsafe reuse in the affected path must be fixed or
the affected behavior kept unavailable; POC status does not waive those invariants.
Existing release security and independent-review gates still apply. Report bounded
test evidence separately from whole-system security claims.

## Simplicity in substantial changes

The consumer retains this local substantial-change review. Its referenced
standards review snapshot remains private; this text does not reproduce or
replace that normative input. In the existing task/PR or design description,
answer:

1. What is the simpler alternative?
2. Why is it insufficient for this requirement, or why are we choosing it?
3. What complexity can this change remove?

“None now” is valid when the necessary added cost is explained. State the current
requirement; when borrowing, name the specific idea, required surrounding mechanisms
and deferred scope. Review coherent responsibility, control flow, state, visible
ownership/effects, failure/cleanup and total implementation, integration, operating
and maintenance cost. Justify each new service boundary, compatibility path and
retained experimental mechanism against the bootable-shell requirement. Keep
bounds, authority and lifetime checks even when they add code. Neither line counts
nor passing tests prove simplicity. Do not split cohesive code merely to shorten it.

Use proportionate explanations for routine fixes; no additional form, review system,
status tracker or mandatory refactor. Route concrete findings to bounded work
issues under the recorded priority policy, ordered by delivery impact and risk; ROADMAP keeps the
capability gates. Remove obsolete paths only after identifying users, replacement
and recovery implications; preserve immutable evidence and pins.
The next signal/process design must complete this assessment before implementation.
The original initial-application review remains private under
[PUBLIC-SOURCE](PUBLIC-SOURCE.md); it is not runtime conformance or independent
sign-off.

When a change requires this private extension, its exact review inputs and
integrity checks remain required with the owner. The public checkout cannot run
that private snapshot verification. Record unavailable coverage; never substitute
mutable sibling bytes or a public source-integrity result.

## Test selection and cadence

The maintainer selected focused testing on 2026-10-06. This supersedes the former
blanket `zig build test` requirement for every completed change or merge in the
POC. Apply the reviewed TD-01–03 stages: relevant checks remain required before
merge, while broad runs occur at meaningful integration checkpoints.

| Stage | Required selection |
| --- | --- |
| Routine iteration | Changed component's host tests, applicable syntax/format checks and the smallest target workload demonstrating changed behavior, relevant denials and cleanup. Documentation-only changes use applicable available source/link/syntax checks; standards-dependent checks stay blocked when required inputs are absent. |
| Completed change / before merge | Run affected checks on final bytes, including direct consumers and required semantic failure controls. Reuse unchanged results only with an explicit input/impact check. Do not rerun unrelated suites merely because a change is finished or committed. |
| Major milestone / integration handoff | Run `zig build test` once on final bytes plus the complete affected native/component suites and composed workload. Examples include shell handoff, maintained SDK intake, engine startup/restart, persistence and assembled boot-to-shell. |
| Broader risk or unexpected regression | Expand immediately when shared ABI/authority, scheduling, memory ownership, common build inputs or toolchain changes affect multiple profiles, or failures reveal wider impact. Select those profiles and the full host suite when impact is broad or uncertain. |
| Release candidate | Full applicable assembled-system and supported-target plan, matching independent evidence and existing release gates. |

Focused means selected by contracts and consumers, not merely changed file paths.
Keep relevant allowed/denied, stale authority, exhaustion, interruption and cleanup
cases. If a maintained runner lacks a safe subset, run its existing affected
component suite; do not invent an unverified case filter or claim unrun cases pass.
A host-only result cannot replace required native evidence. Document the selected
commands, omitted scope and next broad checkpoint in the canonical work record
in the owning issue.

Qualified builds hash live kernel/user/scripts inputs. Do not run host tests that
create temporary omission sources in those trees concurrently with a frozen build
or campaign. Complete those tests first; a disappeared temporary input is a failed
source-freeze attempt and must be preserved, not excluded or silently retried.

After a passing final run, repeat or broaden it only for changed relevant inputs,
new failures or an unresolved concern. Do not run both the same final subset and
its enclosing suite repeatedly without a reason. Historical results on different
inputs do not qualify a changed boundary; missing required runners remain blocked.
This cadence adds no runner, scheduler, parallel tracker or release exception.

Focused host selection uses the existing unittest discovery command, for example:

```sh
python3 -m unittest discover -s tests -p test_openzfs_resources.py -v
python3 -m unittest discover -s tests -p test_openzfs_arc.py -v
```

Use the corresponding native command from the interface reference/workflow inventory
when behavior changes. Broad checkpoint commands remain:

```sh
python3 scripts/check_workflow.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

With its private inputs present, the workflow checker validates the reviewed
draft snapshot and coverage inventory.
It rejects missing native references, unlisted developer entry points, new launch
profiles without references, empty test groups and malformed review records. It
never executes commands from the inventory. `zig build test` includes this check,
host tests, harness tests and all three immutable standards checks. Those private
standards inputs are absent here, so this aggregate cannot pass in a public-only
checkout. This is a
broad checkpoint command, not a requirement for every edit or commit. Before merge,
apply [PROJECT's integration policy](../PROJECT.md): required checks and separate
review must verify final bytes and the impact review for reused results. Agents may
integrate accepted work under that policy; affected-owner reviews, native-execution
approvals and release gates still apply. No hosted CI or branch protection is
configured by this process.

[workflow.json](workflow.json) maps native references, developer tools, stable test
group IDs, commands, oracles, budgets and gaps. IDs identify suites; the native
`results.json` case names identify individual controls. The inventory is a baseline,
not evidence that every required technique or documentation surface is complete.
`--help` entries are discovery instructions, never runtime acceptance.

| Change | Additional required selection |
| --- | --- |
| Native ABI, authority, loader, process/FD or memory | Affected positive and semantic rejection cases and direct consumers; affected older modes; complete affected profile at interface adoption/handoff or when impact cannot be bounded; actual consumer review and matching-revision target evidence before adoption |
| Per-core, interrupt, scheduler, transport or display | Affected target regressions, using `python3 scripts/regression.py` when its shared foundation changes; applicable single-core/native profiles; explain memory ordering, lock/context and resource implications |
| Harness/oracle | Harness unit checks and affected target suites; deliberate broken implementation must fail for the exact named reason |
| Toolchain, flags or dependencies | Fresh affected builds and target modes; identify actual artifacts and review consumers; Debug host tests do not qualify optimized target modes |
| Documentation/process only | Applicable available local links, syntax, source integrity and meaningful checker tests; affected private-input checks remain blocked when unavailable; no unrelated QEMU run |

Use each reference's documented invocation and pinned SDK/tool lock. Only use
subsets the runner supports and preserve its setup and semantic oracles. Per-case
build commands have a180-second timeout. QEMU readers and other native profiles
retain30-second host watchdogs and their existing3000-tick fixture ceilings.

Maintainer approval2026-10-19: **bounded storage-writer experiments, including the
Rust bridge, may use a fixed60-second host watchdog and6000-delivered-tick kernel
ceiling**. This standing ceiling supersedes the earlier one-attempt budget
approvals; their receipts remain historical and do not become30-second passes.
Select the writer profile explicitly and record its bound. Transaction, authority,
memory, worker, observation and cleanup limits remain unchanged. This approval
neither expands transaction capacity nor authorizes unbounded uptime or retries.
Unexpected failures still stop for triage; investigate before another guest.

Separate maintainer decision2026-10-19: the private fixed `--eight-writes` batch
may select exactly eight append-only transaction records and a10240-byte combined
observer ceiling (compiled9704). Existing two-record/8192 profiles remain unchanged.
Writer60s/6000, readers30s/3000, other grants/memory/workers/I/O/observations and
verification/export/cleanup limits remain unchanged. No reset or automatic retry;
this is a fixed finite experiment, not general sustained-service qualification.

Maintainer request2026-10-19 authorizes the next continuous-write lifetime slice:
private `--write-lifetimes` may test successful single-record retirement/reuse with
fresh epochs and permanent outcome retention. The native schedule stays exactly
eight writes and the combined observer ceiling8192 (compiled7596), below the prior
10240 allowance. Old append-only profiles remain unchanged. This does not authorize
failed-record/error/device reset, more native transactions, longer execution,
automatic retry, unbounded service acceptance or changes to userland call policy.

Maintainer request2026-10-19 also authorizes matched native intake of the exact
userland filesystem-service candidate. A separate explicit writable IPC selection
may compose existing AENBD003/ABI25 with the standing60s/6000 writer scope; this
removes only the old channel exclusion from the private writer-budget build guard.
Its other conditions remain. Two channels/three generations,8192-page backing,
4096-byte controller,32 observations, workers/authority and one16-byte write/context
stay fixed. Old selectors cannot opt into writable IPC without this selection.
Native failure/cleanup/recovery and independent consumption remain acceptance gates.

Focused host inventory ceilings remain300 seconds; the complete root `AT-HOST`
gate uses the standing900-second aggregate in [PROJECT](../PROJECT.md#complete-host-gate-budget-2026-10-26).
Target-suite ceilings remain1800 seconds, except the owner-adopted5400-second
complete eight-case AF09 offline family in
[PROJECT](../PROJECT.md#af09-offline-family-budget-2026-10-26). Its one aggregate
covers the whole suite, including final verification and cleanup; child, stream,
compiler-file and runtime limits remain unchanged, with no guest permission.
These are limits, not performance guarantees. Missing required tools/runners block the selected
check. Keep dependency setup separate from offline execution. Full-file/media,
ordered export/drain, cleanup and fresh-reader gates apply at either budget; no
budget or passing inventory checker establishes release readiness.


AF09 host-gate disposition,2026-10-25: [issue2](https://github.com/gonz0w/Aether/issues/2)
records the separately reviewed private attempt05 complete `zig build test` pass:
530.184 seconds within a one-run900-second aggregate,976 Python tests with
terminal OK, final source/tool and accepted legacy-pair checks,9115 prepared
input hashes, six image/kernel identities and owned cleanup. Attempts01–04 remain
failed and preserved privately. The exception is consumed; the default300-second
host ceiling,180-second leaf/auxiliary bounds and4MiB diagnostic streams remain.
It grants no automatic retry or guest. Private receipts, standards and dependencies
are unavailable in this public snapshot; this dated result is not public replay.

The preceding dated result retains the policy in effect for that attempt. The
owner’s 2026-10-26 decision in [PROJECT](../PROJECT.md#complete-host-gate-budget-2026-10-26)
now governs complete host gates; the historical single-run exception stays consumed.
[Issue3](https://github.com/gonz0w/Aether/issues/3) owns public AF09 integration;
[issue56](https://github.com/gonz0w/Aether/issues/56) owns the separate guarded
legacy-profile gap, and [issue4](https://github.com/gonz0w/Aether/issues/4) owns
any later native qualification after a fresh exact disposition.


## Source conventions

| Language | Current owner profile |
| --- | --- |
| Zig | 0.16.0; `zig fmt --check <changed.zig>`; explicit allocator/ownership and reviewed safety/build mode; target evidence for low-level changes |
| Rust | 1.98.0, source compilation edition 2024; `rustfmt +1.98.0 --edition 2024 --check <changed.rs>`; no_std and panic=abort where defined by existing build; safety obligations on unsafe/FFI; Clippy rollout remains pending for standalone rustc fixtures |
| C | Clang/LLD 21.1.8; current freestanding C11/GNU scope and `-Wall -Wextra -Werror`; stronger draft diagnostics require scoped review, not blind rollout |
| Python | Current tested 3.14.7; standard library, four spaces, readable code; subprocess argument arrays, explicit deadlines/status and private resources; syntax plus behavioral tests |
| Shell/make | Declare actual dialect before adding scripts; quote data, check failures and use owned temporary roots; no new shell/make dependency is introduced |

The focused SESSION transport host test (`python3 -m unittest discover -s tests
-p test_session_channel_wait.py`) executes the actual move body under pinned
Clang21.1.8. Its current macOS runner requires an installed SDK selected explicitly
with `xcrun --show-sdk-path`; missing compiler/SDK is failed coverage. These host
headers are separate from the sealed musl SDK used for native client builds.

For new C files, use the reviewed draft configuration explicitly:

The following formatting invocation needs the exact private review configuration;
it is unavailable in the public-only checkout. Obtain it through the owner when
required by the affected work.

```sh
clang-format --style=file:docs/standards-review/2026-09-05-approved/drafts/coding-v0.1.0/configs/clang-format.yaml --dry-run --Werror path/to/new.c
```

Use clang-format 21.1.8, record its identity and do not resolve an arbitrary PATH
binary as equivalent. Formatting existing code is a separate mechanical change.
Existing two-space/compact C and Rust style-edition differences are migration work,
not a reason to rewrite immutable evidence or reformat unrelated sources. Before
modifying such a file, record the exact formatter edition/style used and review
whether to migrate it separately. Python's existing compressed harness code also
needs scoped cleanup; do not mix a whole-harness rewrite into a semantic change.
Formatter success does not establish safety or full Coding-profile compliance.

## Evidence and failures

Freeze sources and tools before a qualified run. Never edit source during a run
whose report checks source hashes. If input changes, keep the attempt and rerun
affected suites on final bytes. Bind evidence to source/patch bytes, exact artifact
and tool digests, flags, platform/firmware, commands, start/end UTC, planned cases,
expected/observed outcomes and raw logs. Current older receipts lack some of these
fields; preserve compact historical results, not retroactive compliance.

Keep each attempt's result and short diagnostic logs even after a successful retry. Distinguish
product failure, timeout, infrastructure error, not-run and unknown in the retained
triage note; an old harness's `incomplete` field alone is insufficient classification.
Negative tests require the named rejection and side effects; generic panic, timeout
or nonzero exit is not success. Retain owned VM teardown failures as test failures.
Do not broadly kill processes or delete shared directories to make a run pass.

For each completed change, link its compact final result and failed-attempt summaries
from its canonical work record to the evidence README or retained result. On
2026-10-05 the maintainer explicitly disposed of the accumulated POC test archives
and generated build trees and selected compact
retention for future work. This supersedes older local archive/readback recipes.

Keep commands, source/tool/artifact hashes, cases, outcomes, scope and short logs.
Do not generate source tarballs, archive whole run directories, copy SDKs into
evidence, or retain test ISOs, disks, binaries, link maps and compiler caches per
attempt. Maintained suites call `scripts/evidence.py` after completion, including
failure, to remove generated files from their own run directory and retain JSON
results and logs of at most1MiB each. Large logs keep their tail and original hash;
`results.json` itself remains complete. Artifact hashes describe the executed bytes,
not a promise that those bytes remain stored. Private experiments must follow the
same policy rather than calling historical archiving recipes.

Small fixed regressions belong in `tests/fixtures`, with checked pins and original
notices. Current build dependencies belong in `.deps`, with one verified copy and
documented provenance, rather than a chain of historical evidence archives.
The current private SDK/OpenZFS inputs are documented in `.deps/native-current`;
they are not released SDK or filesystem acceptance. Clean inactive `zig-out` and
workspace caches when no build uses them; do not remove sibling/shared tool caches.
Do not invoke retired packet manifest/archive validators as current acceptance.
Historical byte replay is unavailable after disposal. A future actual release or
specific defect investigation must explicitly select its necessary retention scope;
this POC policy does not claim the release support/investigation gates are satisfied.

## Extended testing and release gates

Aether's extended testing owner is the project maintainer; the contributor running
an experiment owns that run's triage and temporary resources. Proposed daily
parser fuzz/lifecycle stress and weekly SMP/soak/hardware slots are **not running**.
Corpus/seed management, workload iteration limits, suite watchdogs, performance
baselines and scheduled infrastructure are missing. These are blocked coverage;
no automation, CI provider or reviewer has been invented. Define these before
calling the extended stage complete. New crashes retain their seed and become
fixed regression cases before merge. Review flakes, escaped defects, gaps and
runtime/resource trends in the canonical work record in the owning issue.

Until a reviewed cadence exists, release readiness cannot rely on extended evidence.
For a future candidate, require fresh target evidence after the last relevant input
change and within seven days of review; this is an initial local ceiling, not a
waiver of missing fuzz, soak or hardware tests. Changing the ceiling requires an
explicit candidate/plan review. Do not advertise RTX 3060, persistent storage,
POSIX, networking or installation support from emulated bounded fixtures.

Before release, the assembly owner must supply all applicable RG-01–RG-10 gates:
identity/provenance, clean independent build, boot/recovery, workflows, update/data
preservation, security/trust, reliability/resources, compatibility/targets,
performance/experience and documentation/publication. Current component passes do
not satisfy assembled-image gates. A monitored security contact, independent build
and reader reviews, complete manuals/offline target lookup, target matrix and actual
release decision remain missing. No publication is authorized by a green check.

Exceptions name clause/case, exact scope, reason/risk, accountable reviewer, issue,
compensating evidence and expiry. Missing reviews are pending, never approved by a
status field. Authority bypass, unexplained corruption, failed cleanup and mismatched
artifacts cannot be waived while retaining the affected claim. Track outstanding
implementation work in canonical issues, with capability
gates in ROADMAP; this document is process, not another backlog.

## Fresh-source inventory check

M4 reproduction must reject added, removed, modified or symlinked source inputs
during its run. Only top-level .deps, .zig-cache and zig-out are excluded from the
post-build source inventory: dependencies have their own full comparison, while
caches/artifacts are expected outputs. An output-like name nested inside a source
directory is still source. The existing __pycache__/.DS_Store exclusions remain.

The original correction affected scripts/reproduce.py and its host tests only, with
no runtime ABI, authority, dependency or quota changes. Its selected verification
was addition/removal/modification/symlink counterexamples, permitted output
activity and nested-output-name rejection, followed by
`python3 scripts/reproduce.py` on final sources. That command runs host checks,
M4 target regressions and one-core smoke with fresh private Zig caches. It is
a working-tree reproduction, not an independent committed build or release gate.
For current work, select reproduction under the test cadence above and retain
compact commands, input/tool hashes, outcomes and short logs under
[evidence and failures](#evidence-and-failures). The runner removes its generated
source/dependency/build tree; do not preserve a per-run source archive. Native C
companion profiles are unchanged and excluded.

Reproduction tool identity extension: record invocation path, resolved executable
path and SHA-256 before version probes, verify again after probes and after the
selected builds. Rust additionally records the compiler under the selected
sysroot, so a rustup launcher hash is not mistaken for compiler identity. Reject
missing/replaced executables and symlink retargeting even when bytes match.
Tests cover unchanged identity, changed bytes, retargeted links and disappearance,
followed by fresh-cache reproduction for that original change. This adds no
toolchain dependency or ABI; it observes installed executable bytes, not
library/sysroot closure, provenance,
execution attestation or protection against transient replacement/restoration.

## RC1 review follow-up: rendering and negative controls

ADP-01-W01 tooling checks require the candidate's pinned Mermaid CLI 11.17.0,
Puppeteer 25.10.0 and Chrome 152.0.7977.75. Follow the reviewed Documentation
`TOOLING.md` setup in the local candidate archive; use its lockfile in an owned
temporary installation. Put that installation's `node_modules/.bin` on PATH and
set `PUPPETEER_CACHE_DIR` to its browser cache before running:

```sh
python3 -B docs/standards-review/2026-09-06-rc1-adp01/inputs/tools/check-candidate.py --strict
```

The [tooling receipt](evidence/adp01-tooling-2026-09-06/README.md) records the
existing matching installation used locally. Temporary paths are not durable
prerequisites. This check validates candidate examples, not Aether manual coverage,
font/renderer accessibility acceptance, independent readers or runtime adoption.

For a release-designated artifact, the assembly owner must explicitly include
`-Drelease-artifact=true` in the recorded `zig build` command. This build-time gate
rejects all 39 currently classified intentional negative-test boolean controls
before executing build steps. It adds no runtime switch. Default experimental
builds continue to permit those controls. The host inventory test requires review
of new boolean options; new non-boolean controls also require explicit human review.
This gate does not select a production profile or establish release readiness.
Retain exact flags and artifact identity at assembly. The
[guard receipt](evidence/adp01-build-guard-2026-09-06/README.md) covers actual option
rejections, accepted controls, payload equality and seven QEMU regression cases.
ADP-01-W04 remains partial: extended schedules, corpora and resource evidence are
still missing. ISO byte reproducibility remains unproven.

## Private pipe core checks

The host suite includes `python3 -m unittest discover -s tests -p test_pipe_owner.py -v`.
It compiles/runs 79 Rust tests covering pipe ownership, two-pipe routing,
descriptor preparation, session child collection, exec-vector validation and bounded
scratch authority/offset/cleanup/exhaustion, and compiles the same modules without
std for x86_64-unknown-none using Rust 1.98.0. Failed runs retain compiler/test
receipts and artifacts under zig-out/pipe-owner-host-*; successful disposable host
outputs are removed. This is core behavior/compilation evidence, not authenticated
native transport, signal delivery, target resource qualification or pipe support.

Serial stream-oracle checks: `python3 -m unittest discover -s tests -p test_pipeline_console.py -v`
verifies host rejection of altered/missing/extra stream bytes, missing/duplicated/failed
children, incorrect cleanup, missing prompts, duplicate completion and panic. This is
host-oracle coverage, not a replacement for the full native capacity suite. In the
AENMX006 experiment, the stdio owner checks authority, framing and lifetime while
the host checks exact workload output. Nonserial capture fixtures retain their scope.


For the scoped session-channel lifetime core (host coverage, not native SESSION):

```sh
zig test kernel/native_channel.zig --test-filter session --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The full host command includes these tests. Native qualification still requires the
profile and matching suites described in NATIVE-SHELL-STARTUP; this command alone
does not establish guest-visible fifteen-generation reuse.


Historical native AENMX007 process/channel resource invocation (not SESSION),
with its original dependency and tool-lock paths retained:

```sh
python3 scripts/pipeline_capacity.py --case session-lifetime --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

For new work, select the exact current dependency and tool identities through the
owning record and [native shell contract](NATIVE-SHELL-STARTUP.md). The old sibling
path and dated output above are not current inputs or execution authorization;
do not infer a valid replacement by renaming paths. Existing native approval and
resource/cleanup requirements apply before a selected invocation runs.

The complete capacity invocation without `--case` also runs the stale-worker-epoch,
old005 lifetime-bound, disabled007, malformed-frame, old-owner and oversized-owner
controls. A focused pass does not replace those or matching producer regressions.

The session core cases exercise nine pipe generations, fifteen independent child
lifetimes and retained wait-reply/reclaim barriers. They do not execute the native
session dispatcher. `test_pipe_owner.py` also retains its separate exec-request
progress profiles. Guest SESSION acceptance requires the composed workload in
NATIVE-SHELL-STARTUP, not these host state transitions.


The bounded SESSION observer has a focused host command:
`python3 -m unittest discover -s tests -p test_session_smoke.py -v`.
Its five counterexample tests run in the normal host discovery suite; they do not
substitute for the composed cases in the full capacity suite. The new native record
parser is included in `zig build test`. SESSION producer qualification is recorded in NATIVE-SHELL-STARTUP; independent
consumer acceptance remains open and resource-only evidence stays separate.


Maintainer decision2026-10-20: a separately selected fixed service-lifetimes
profile may perform exactly eight16-byte writes in one live SPA, each through a
fresh consumed C context and checked successful record retirement. This supersedes
the one-transaction count only for that new profile. Existing service/4096 engine
profiles stay unchanged. Observer<=8192, writers60s/6000/readers30s/3000, controller
4096,8192-page backing, channels/workers/I/O/32 observations and all verification/
export/drain/cleanup guards remain fixed; no retry or failed-history reset.
[Concrete workload](OPENZFS-FEASIBILITY.md#approved-eight-write-native-service-workload--2026-10-20)
records the now-approved implementation scope; publication and owner acceptance
still require matching native/consumer evidence.


Maintainer decision2026-10-19: the separately selected fixed mixed filesystem
service profile may perform exactly eight total mutation attempts: four namespace
operations and four16-byte writes, with typed success-only namespace0/service16
retirement, AFSRPC03 and explicit trusted directory rights15. This supersedes the
one-attempt namespace count only for that new profile. Follow the approved concrete
sequence in OPENZFS-FEASIBILITY. Writers60s/6000, readers30s/3000, observer8192,
controller4096, backing8192 pages/two channels/three generations/32 observations and
all worker/I/O/authority/verification/export/drain/cleanup limits remain fixed.
Old profiles/pins remain unchanged; no failed-history reset, automatic replay/retry,
unbounded service or implicit consumer/ISO/R1 acceptance.


## Approved separate filesystem-service data profile — 2026-10-20

The maintainer approved the concrete4KiB proposal in OPENZFS-FEASIBILITY after the
ABI26 mixed-wait gate. A separately selected AFSRPC04 profile may carry1..4096-byte
read/write bodies through bounded sequences of existing64-byte frames and use
length-checked1..4096 success-only write retirement plus namespace0. The fixed
native positive workload remains8 mixed mutations with4 writes of4096 bytes;
interruption cases stop early as specified. Existing16-byte profiles stay exact.
64 complete requests,100000 attempts per64-byte frame,60s6000 writers/30s3000
readers,8192 observer,4096 controller/no writable statics,8192-page backing, two
channels/three generations/32 observations and other worker/I/O/authority/cleanup
limits stay fixed. Fit or stop; no failed reset/replay or automatic retry. This
permits the data-path experiment, not operational/R1 or release acceptance.

For the next native qualification capture the actual native-qemu-command.json
before cleanup and freeze emulator/boot/tool identities before and after runs.
The preceding temporary helper's wrong command filename lost transient argv;
source-derived templates and post-run observations are explicitly weaker evidence.
Do not rerun unchanged passing guests solely to recreate ephemeral paths.

Maintainer decision 2026-10-20: the separately selected filesystem activation
profile may use an 8192-byte supervisor code ceiling (two RX pages), one4096-byte
RW/NX stack and no writable statics. Check zero code tails and immutable backing
aliases. Older profiles retain4096 code bytes. This supersedes only that code/
backing-page bound for the approved activation profile: workload9/96, observer8192,
engine backing8192 pages, channels/workers/I/O, authority, writer60s6000/readers30s3000
and all original recovery/export/drain/cleanup checks remain fixed. No retries or
failed-history reset. See OPENZFS-FEASIBILITY for the concrete integration scope.

Maintainer decision2026-10-20: separate `fs_names`/AFSRPC05 may accept1..255-byte
components and<=510 combined rename bytes. Keep old AF04/seals unchanged. Reuse
4096 scratch; all other code/stack/observer/engine/channel/worker/I/O/authority,
9-mutation96-request workload, frame/poll,60s6000 writer/30s3000 reader and
verification/cleanup limits remain fixed. Fit/time/unexpected failures stop for
triage; this is no operational uptime or release authorization.

## Separate operational storage lifetime decision — 2026-10-20

The maintainer explicitly approved the proposal in OPENZFS-FEASIBILITY: a separate
profile permits healthy storage execution past the old6000-tick fixture stop,
with **one fixed120-second qualification**,65s idle and post-idle mutation/readback.
Keep the new native workload exactly9 mutations/96 complete requests and all
existing memory/authority/channel/worker/I/O/observation/poll/cleanup limits.
Its independent reader remains30s/3000 and validates the declared120s writer
timestamp window. Old writers remain60s/6000 and old readers30s/3000; do not
silently select the new mode or reinterpret an old candidate. Checked counters
and monotonic-time exhaustion still reject; no automatic restart, reset or replay.
Unexpected failure stops for triage, not another automatic guest. The separate
profile/owner/SDK identity and startup/shutdown behavior require the scoped review
before admission. Approval is not runtime acceptance, publication or release.

## Approved separate filesystem/SESSION composition — 2026-10-20

The maintainer approved the separate combined profile proposed in
[OPENZFS-FEASIBILITY](OPENZFS-FEASIBILITY.md#proposed-separate-combined-storagesession-profile--decision-required):
seven domains,35MiB/8960 backing pages (one8192-page engine plus six128-page peers),
twelve channel records. This is a new private selection, not relaxation of old
profile guards. Engine82-helper execution stays separate from single-context
process copy/exec. Initial qualification retains9 filesystem mutations/96 requests,
writer60s6000/readers30s3000 and existing controller/data limits. Measure fixed
kernel metadata and peer fits before admission; reject excess, stop unexpected
failure for triage and do not reuse the consumed120s idle approval. No sys-init
acceptance or Zsh resource/ISO qualification is implied by the resource decision.

## Approved separate 16 KiB filesystem/sys-init owner — 2026-10-20

The maintainer approved the separate controller fit proposal in
OPENZFS-FEASIBILITY: owner code<=16384, four immutable RX code pages and one4096
RW/NX stack, checked zero tails/no writable statics (statically resolved immutable
GOT permitted). Existing8192 profile remains exact. Backing8960 pages/35MiB,
seven domains/twelve channels, helper/process authority,9 mutations96 requests,
writer60s6000/readers30s3000 and all other limits remain fixed. Actual adapted
owner size and fresh scoped stack inspection precede admission; the old15120
sys-init result alone is not integrated-owner acceptance. No new sibling edit,
long-lived profile, reset/retry/replay, old120s rerun or release authorization.

## Complete owner measurement before code budgeting —2026-10-22

The maintainer explicitly supersedes the16KiB optimization gate for new native
owner composition. Complete the coherent owner and measure its actual code and
call graph before selecting a documented code budget with reasonable headroom.
Do not infer a new limit from partial required roots, remove security checks to
fit, or treat offline measurements as native admission. Historical16KiB profiles,
sealed inputs and released pins remain exact; a newly selected runtime allowance
needs matching parser/linker/mapping/rejection checks after that measurement.
Capability boundaries, immutable RX code/RW-NX data,4096 stack,8192 owner data,
35MiB backing/seven domains/twelve channels,9/96 qualification workload,
watchdogs, cleanup and persistence stop-and-review rules remain in force. No
automatic growth, production readiness, changed old profile or VM retry follows.

## Approved separate guarded owner stack —2026-10-23

The maintainer approved decision0212's separate8192-byte owner RW/NX stack,
initial RSP0x802000-8 and unmapped guards at0x7ff000/0x802000, drawn from the same
128-page owner partition. Match an explicit versioned profile, loader/entry and
8184-byte usable-stack check; old4096-byte profiles remain exact. Keep8192 owner
data,35MiB/seven domains/twelve channels,9/96 workload,watchdogs,poll/I/O/authority
and cleanup checks unchanged. Complete exec/startup readiness, then measure the
whole owner and choose a code budget with headroom. Approval is not native or ISO
acceptance and does not waive the persistence stop-and-review rule.
