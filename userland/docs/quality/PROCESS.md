# Contributor quality workflow

This how-to is for Aether-userland contributors. It applies from UL-060 onward
in this experimental checkout. First read the pinned [method](../../../.agent-temper/METHOD.md),
root [engineering policy](../../../PROJECT.md) and root [work selection](../../../.planning/STATE.md).
The selected bounded record owns scope and continuation; UL records retain component
detail. Root [test cadence and retention](../../../docs/DEVELOPMENT.md) apply.
Run commands from `userland/` with Python 3.10 or later. No target installation
or network access is required for the local gate. Missing native SDKs and tools block the affected test stage.

## Adoption and authority

The maintainer approved four standards profiles on 2026-09-05. We adopt their
applicable development requirements for new or revised first-party work, with
existing-content migration tracked below. The [approval record](../vendor/aether-approved-drafts/2026-09-05/docs/APPROVALS.md)
and [receipt](../vendor/aether-approved-drafts/2026-09-05/docs/approvals/2026-09-05-drafts.json)
are retained verbatim. The snapshot is a reviewed draft input, **not a release**.
The separate local manifest pin identifies its bytes. Existing Experience,
Foundations and Distribution v0.1.0 release pins remain unchanged.

| Profile | Local adoption and remaining boundary |
| --- | --- |
| [Documentation](../vendor/aether-approved-drafts/2026-09-05/drafts/documentation-v0.1.0/README.md) | DW/DS/DM/DG/DP for changed documentation; Markdown narrative, mdoc manuals, Mermaid diagrams. Initial coverage inventory is incomplete. |
| [Testing](../vendor/aether-approved-drafts/2026-09-05/drafts/testing-v0.1.0/README.md) | TD/TC/TE for change planning, test selection and evidence. Aether-dist gates are a future release handoff, not a userland certification. |
| [Coding](../vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/README.md) | CE/CD/CA and applicable language clauses for new/revised original source. Preserve upstream, generated and historical evidence bytes. |
| [Distribution extensions](../vendor/aether-approved-drafts/2026-09-05/drafts/distribution-v0.2.0/README.md) | EV records apply to claims. CT/PD/MR guide acceptance planning; unresolved ABI, TTY, fork/signals and affected-owner acceptance remain open. |

The snapshot contains the approval inventory and licensing/approval records. Links
from it to older release content resolve through the [existing adoption index](../STANDARDS.md)
or canonical Aether-standards; it is not a complete published documentation bundle.
New shared requirements belong in Aether-standards. On an update, review the actual
diff and approval scope, retain the old snapshot, explicitly select a new review
identity, and run the local gate. Never regenerate hashes to hide unexpected drift.

## Change procedure

1. Read the applicable clauses and the bounded record selected by root STATE.
   Preserve its owning UL record where applicable; use [the change review outline](change-review.md)
   within that record rather than creating a parallel assignment. Name requirements,
   affected consumers, success and forbidden outcomes before code. Prefer meaningful
   test-first work. Reproduce bugs before fixing them, or record why a deterministic
   reproduction is unavailable and the alternative evidence. Record the actual
   sequence; never describe later tests as a prior red result.
2. Review ownership, lifetimes, authority, bounds, concurrency, error identity and
   cleanup. Record dependency closure, licenses, exact tools/flags, resource limits
   and update/removal paths for new dependencies. No new runtime dependency is
   introduced by this adoption; the checker uses Python's standard library.
3. Select tests by behavior and risk, including affected consumers. Update canonical
   references and [coverage](coverage.json), or explain no documentation impact.
   Keep technical review separate from independent reader walkthroughs.
4. Run the local gate and relevant stage below using root's focused cadence.
   Retain compact records of failed/incomplete attempts and the final result:
   plan/source/tool/artifact hashes, commands, expected and observed outcomes,
   short diagnostic logs, timeouts and cleanup evidence. Remove owned generated
   outputs after completion; do not archive complete runs, SDKs or source trees.
5. Review findings before marking the UL item complete. Missing tools, unknown
   outcomes and pending reviewers are incomplete coverage. Never invent sign-off.
   Update the owning record and root STATE's selection/status as needed; record
   follow-ons as candidates. Rerun affected checks if source or plan changes.

## Check stages and ownership

Apply root policy for test selection, triage, retention and integration; preserve
actual affected-owner review and native/release acceptance. Commands below
are offline after separately provisioned, pinned dependencies. A stage's timeout
is an upper bound, not a performance claim. Keep outputs in private build roots.

| Stage | Commands, platform and limits |
| --- | --- |
| Local process/docs | `python3 -B docs/quality/check.py`; Python 3.10+ host, three child checks at most 60 seconds each. Validates pins and inventory structure, not prose or runtime. |
| Local command changes | `python3 experiments/command-runner/check.py --sdk build/native-c-xhkdw6jv`; provisioned macOS host, pinned Clang 21.1.8 and strict SDK; 21 host/control cases plus native object inspection. Allow 5 minutes; missing SDK blocks this selection. |
| Before completion/merge | Local gate plus changed experiment's documented build/regression commands. Keep exact argv, tools, platform, deadline and cleanup in its plan. For native command changes use [NATIVE.md](../../experiments/command-runner/NATIVE.md); 9 current QEMU cases, each guest bounded by its 30-second watchdog, 15-minute suite budget. |
| Interface/authority | Matching producer and consumer revisions, affected-owner review, allowed/denied/malformed cases and native witnesses. Host controls cannot substitute for target enforcement. UL-058 adds the next command-boundary coverage. |
| Extended | Manual weekly review while development is active, and before any candidate. UL-062 now supplies executable host parser sweep/replay/minimization, clang-tidy/analyze, observational RSS metrics, forked concurrency, a 256-round host transport loop and a pinned-ASan deadlock diagnosis (`experiments/command-runner/EXTENDED.md`). Pinned Clang 21.1.8 ASan is incompatible with this macOS 27 dyld/malloc path; PXE-04 stays blocked. No automation was installed. |
| Release candidate | Documentation completeness preflight: `python3 -B docs/quality/check.py --release`. Currently fails on draft entries. Also require exact assembled-target tests, source trust, manuals/diagrams rendering and offline lookup, technical review, independent onboarding/recovery walkthroughs and applicable ten-gate distribution review. This checker cannot authorize release. |

Before a candidate, extended evidence must be at most seven days old and match
relevant source, tools and plan. Any affecting change invalidates reuse regardless
of age. Establish actual workload thresholds before the first run; missing workloads
block release. Retain compact evidence throughout development under root policy;
keep existing frozen records unchanged. Any later release requires retention through
its declared support and vulnerability-investigation period. Track escaped defects,
flaky attempts, missing cases, duration and resource regressions in each UL evidence record and the weekly review.

## Source checks and migration

New original C uses declared C17 unless its reviewed native/assembly boundary needs
an extension. Keep current pinned build diagnostics; record any additional diagnostic
selection and each suppression. Use `docs/quality/clang-format.yaml` with Clang-format
21.1.8 in non-mutating `--dry-run --Werror --style=file:docs/quality/clang-format.yaml`
mode on new C files. Reformat existing files as a separate mechanical change before
behavior edits where feasible; do not rewrite retained evidence or upstream code.

Python host tools support 3.10+ and the CP profile: sequence subprocess arguments,
explicit working directory/environment, bounded waits and checked exits. No Python
formatter dependency is imposed. Syntax and meaningful controls run on the actual
interpreter recorded with results. Rust/Zig/shell changes require their language
profile and pinned rustfmt/Clippy, zig fmt or ShellCheck/declared-shell checks in
that change's plan. No blanket claim for those languages follows from C tests.

Host sanitizers are required where compatible and selected by risk; UL-062 inventories
missing host instrumentation and the compensating native strategy. Native tests have
bounded isolation/reclaim oracles; this is not a native sanitizer port.

| Gap | Scope, risk and required follow-up |
| --- | --- |
| UL-061 | Complete documentation/test case inventory, exact revisions and reader review; current records are draft. Expand subsystem entries into all supported public surfaces before publication. Bytecount is experimental; public aether-run, shell/TTY, configuration/package/service workflows are not yet shipped. Add actual manuals and offline target checks before shipping commands. |
| UL-062 | Parser sweep/replay/minimization, host static/RSS/concurrency/transport, pinned-ASan diagnosis, family/stage matrix and native compensation limits now exist. Remaining: ASan on a compatible pinned toolchain/OS, kernel RSS enforcement, broader corpora/schedules, independent review. Finish before a candidate. |
| UL-063 | Audit existing first-party C/Python boundaries and formatting, starting with command-runner before UL-058 behavior changes. Review dense code and subprocess cleanup; preserve source-pinned historical runs. No security defect is waived by this migration. |

These are migration gaps, not approved release exceptions. A deviation must record
exact rule/case and candidate/plan, reason, risk, accountable reviewer, evidence,
compensation and expiry/milestone. Pending approval stays pending. Authority bypass,
corruption, uncontained effects, failed cleanup and invalid provenance cannot be
waived for claims that rely on those guarantees. No whole-repository compliance or
release readiness is asserted by this process adoption.

## RC1 review follow-up

Before relevant migration work, consult [ADP-02 / UL-070](RC1-ADP02.md) and its
profile-qualified clause register. It records current gaps for UL-061–063, including
manuals, exact toolchain/minimum-interpreter scope, C/Rust/FFI and POSIX coverage.
This review does not upgrade release pins or satisfy independent publication gates.

## Contributor checker reference

The [quality command manual](../../man/man1/aether-userland-quality.1) documents
actual options, streams, exits, files and recovery; [manual reading](../../man/README.md)
requires only an offline host mandoc. Its [surface record](quality-command.json)
binds checker source identity and QD-01–09 contract checks. Keep the entry draft
until independent review and applicable packaged lookup are supplied. UL-071's
host rendering/CLI evidence does not close UL-061 or establish minimum-version
execution on Python 3.10/3.12.

## Owned reference execution (UL-072)

Quality and standalone release wrappers now route reference execution through
`docs/quality/processes.py`, reusing the existing command-runner helper unchanged.
Each execution retains inputs, separate output streams and a cleanup receipt in
an owned `build/quality-process-*` directory. The child gets the same absolute
Python with `-B`, fixed PATH/LC_ALL and a private TMPDIR, not the parent environment.
Output is replayed after cleanup. Timeout, surviving descendants, nonzero exit or
unresolved cleanup cannot pass; output files are bounded at 16 MiB each.

Run `python3 -B docs/quality/test-processes.py` when changing this adapter, wrappers
or the underlying helper (POSIX host, 60-second suite budget). It includes real
child/descendant and output-bound controls; do not place an independently killed
session owner around another owner and infer cleanup of both. Current tests cover
Python 3.14.7/3.13.15 plus source-built 3.10.21/3.12.14 (UL-073). Detached hostile children, owner SIGKILL and a total deadline
for in-process validation are outside this contract. The maintainer accepted this scoped implementation review on 2026-09-06; minimum-series evidence
is scoped to the exact tested patch releases and quality paths. Preserve these
historical receipts; new runs follow root's compact retention and owned-output cleanup.

## Qualification and manual review handoff

[UL-073 qualification](../evidence/python-qualification-2026-09-06/README.md)
provides actual isolated Python 3.10.21/3.12.14 tests. These limited offline runtimes
do not qualify all Python modules or all repository tools. The maintainer approved [the independent review packet](MANUAL-REVIEW.md) with
no findings on 2026-09-06. The approval is scoped to that packet, not broader
source migration, packaged lookup or publication.

## Maintained-source discovery

Use the dated [source census](SOURCE-INVENTORY.md) to inform a bounded UL-061/063
scope only when selected through root STATE. It records exact maintained paths
and documentation routes, including Git hooks. Static call hints do not establish defects, runtime qualification or audit
completion; generated/imported source and non-source interfaces need separate work.


## Simplicity extension adoption (UL-080)

On 2026-09-07 the maintainer explicitly requested adoption of the additive
[Coding v0.2.0 simplicity extension](../vendor/aether-review-snapshots/2026-09-07/coding-v0.2.0/README.md).
SE-01–05 applies prospectively to first-party design, code, tooling and process.
This is an explicitly adopted, unreleased process snapshot, separate from the
2026-09-05 approved profiles, frozen rc1 kit and released standards pins.

Source: Aether-standards commit `049fa158c1b9e799c799a0713a418601d4885c2e`,
clean extension paths at capture. All four source documents and SHA256SUMS were
copied verbatim. Manifest SHA256:
`8c3d8095acc9b6283a5f6970bc4ce6e7e4646a04fb759f8cf2940ed494cbeff8`. The local pin is simplicity.sha256; the existing quality command
checks both snapshots before running validators. No build reads a sibling tree.

Use the three questions in [the existing review outline](change-review.md) for
substantial design changes. Keep routine small-fix workflows proportionate; no
second review system or numerical complexity limit is introduced. Review coherent
responsibility, visible state/effects, straightforward control flow, checked failure
and cleanup, and combined implementation/integration/operating/maintenance cost.
A little duplication may preserve useful boundaries; source size or passing tests
alone does not establish simplicity. Preserve required safety evidence and failures.

The 2026-09-07 adoption identified UL-007's full-dash integration as its next design
change; this is historical context, not current work selection: assess the necessary
libc interposition, process/signal/FD ownership and retained compatibility paths in
its existing review before selecting implementation. Do not claim a future review
has occurred. Existing concrete triage is tracked in UL-081; implementation is
selected by release impact/risk, not a mass cleanup campaign. Adoption evidence and
this change's scoped assessment are in [the local review](../evidence/simplicity-adoption-2026-09-07/README.md).
