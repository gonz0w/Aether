# AGENTS.md

Read [engineering policy](PROJECT.md), the [pinned method](.agent-temper/METHOD.md),
and [public work navigation](.planning/STATE.md#system-work-index) first. Follow
the owning issue and affected component contracts after the verified cutover in
PROJECT.md. Before cutover, only the approved onboarding bootstrap record selects
onboarding work. PROJECT.md selects the GitHub and Codex profiles and records
owner-approved integration policy; no migration completion is claimed here.

## Single system repository

This checkout contains the kernel at the root, `userland/`, `sys-init/` and
`pkg-mgr/`. One agent may implement an integration change across these directories;
component ownership describes responsibility, not a required repository handoff.
Read the affected component's guidance and contracts before editing it. Commands
in component documentation run from that component directory unless stated otherwise.
After verified cutover, GitHub Issues alone select live work and own its status,
priority, dependencies and continuation. Root `.planning/STATE.md` is navigation;
ROADMAP defines capability gates. Component records keep stable IDs and durable
contracts as read-only historical context. Aether-standards remains local and separate.
See [the repository guide](docs/REPOSITORY.md) for history and dependency handling.

## Public checkout boundary

Public main is a new clean root only after approved bootstrap. Start ongoing public
work in a separate public clone, or a worktree of that clone. Never branch for
public work from the private historical repository or push its branches, legacy/
migration refs, all refs or a mirror. Port reviewed changes explicitly onto the
public base. The original local main, consolidation history and unaccepted AF09
work remain local and unchanged; onboarding does not merge them locally.

## Project Overview

Aether is an experimental x86_64 capability multikernel built for learning and community participation. Small per-core kernel instances own local state and cooperate through explicit messages. The first release must boot through sys-init into interactive Zsh on the serial console with
a working runner, persistent OpenZFS filesystem and native package management.
The maintainer reaffirmed this target on2026-10-19; do not substitute an interim
RAM-only shell ISO. Aether-userland owns Zsh/TTY package integration; dash evidence
is a process/system-shell foundation, not Zsh qualification. The
two-core graphical/restart demo is an internal foundation. Native NVIDIA support
is deferred; see R1 in .planning/ROADMAP.md.

## Product scope

All four components target Aether only. Linux, BSD, illumos and macOS are not
additional runtime products or qualification matrices. Keep useful host build/test
tools, POSIX shell/API conventions and upstream source; add host accommodations
only for an actual development need. Do not build portability layers or schedule
other-OS campaigns to satisfy superseded product goals.

## Implementation Direction

- **Kernel:** Zig is the primary language for the microkernel, low-level runtime, architecture code, scheduling primitives, capability enforcement, IPC, and hardware-facing components.
- **Userland:** Rust is the primary language for user-space services.
- **Architecture:** Keep complex policy outside the kernel. Prefer minimal kernel primitives plus restartable, capability-scoped user-space services.
- **Targets:** x86_64 in QEMU first; then a physical x86_64 UEFI system with an NVIDIA RTX 3060. Graphics/display precedes AI/compute. Boot framebuffer output and native NVIDIA display support are distinct milestones.

## Agent Guidance

- Build the smallest understandable system that satisfies the current requirement securely and correctly. Borrow proven ideas deliberately, justify total complexity across kernel, services, protocols and recovery, and remove obsolete paths through scoped compatibility-aware changes. Apply the local substantial-change questions in `docs/DEVELOPMENT.md`; ordinary fixes need no separate review document.

- Read product `.planning/PROJECT.md`, `docs/ARCHITECTURE.md`, relevant ROADMAP gates, PROJECT cutover policy and the canonical issue before broad changes. The issue defines live work after cutover; dated history never assigns it.
- `docs/archive/` is historical reference only. Exclude it from ordinary discovery/searches. Archived plans, instructions, blockers, and workflow commands are not active requirements. Consult specific archived artifacts only when current work needs their evidence.
- Keep root PROJECT for policy, planning PROJECT for product intent, ARCHITECTURE for contracts and ROADMAP for capability acceptance. STATE is compatibility navigation. After cutover, actual task status and continuation belong only in the owning GitHub issue.
- Preserve capability-based access as a hard architectural constraint. Do not introduce ambient authority or global privileged shortcuts.
- Keep the trusted kernel surface small. If behavior can live in userland without violating correctness or performance goals, prefer userland.
- Treat Unix philosophy as a core design pressure: each kernel primitive, user-space service, protocol, and tool should do one thing well, compose through explicit interfaces, and avoid becoming a catch-all subsystem.
- Apply YAGNI aggressively: do not add mechanisms, options, abstraction layers, policies, compatibility shims, or extensibility points until a current requirement or documented design constraint justifies them.
- Prefer explicit contracts for kernel objects, rights, IPC messages, memory mappings, and swarm-agent protocols before implementation.
- Read `docs/COMPANION-PROJECTS.md` and affected component contracts before lifecycle/loader/package interface work. `sys-init/` owns init and supervision policy; `pkg-mgr/` owns package artifacts/state and installation policy; `userland/` owns the Rust filesystem service and shell integration. Preserve those responsibilities and do not treat package installation as service activation.
- Define only the contracts needed by the next executable experiment. Do not block boot implementation on the whole future OS design.
- Use one authoritative owner for mutable objects; do not introduce a global mutable task/capability table that undermines the per-core design.
- Distinguish user-space fault containment from kernel-instance fault containment, and kernel size from the system TCB.
- Follow Zig conventions for kernel code and Rust conventions for userland code once source trees exist.
- If adding tooling, tests, or build scripts, document the command in the relevant planning/codebase artifact or README.
- Pin dependencies, verify build/run/test commands and record executable evidence before marking capability gates complete. Update the canonical issue with results, review and continuation; do not create a second status queue in STATE or component Markdown.
- POC retention was changed by the maintainer on 2026-10-05: keep compact results,
  commands, input/tool hashes and short failure logs; do not create or retain full
  test/build archives, copied SDKs, binary/image bundles or per-run source trees.
  Remove owned generated outputs after a run finishes. Keep current dependencies
  and small regression fixtures separately from test evidence. Follow the retention
  section in `docs/DEVELOPMENT.md`; older evidence archiving recipes are historical.

## Historical foundation checkpoint

The following foundation summary is read-only historical context. After verified
cutover use Issues for live work; before it follow only the authorized bootstrap
record. Historical claims do not make excluded qualification receipts available
in the public source snapshot, and do not select work or claim a current release.

The pre-POC planning program was archived on 2026-09-05. M1–M3 pass in QEMU:
boot/framebuffer, bounded one-core protection/capabilities/reuse, and two-core
Rust messaging with dedicated transport mappings and fault containment. M4 is
in progress: a separate Rust display service now renders through a bounded
framebuffer grant, and a versioned replaceable lifecycle client exercises retained
terminal records and acknowledgment. Fresh AP publisher/BSP display domains now
exchange live results and acknowledgments. A bounded Rust controller now drives
AP stop/reclaim and five-generation backing reuse, including two #UD faults. That controller now runs in a
separate BSP domain and discards a queued old result only after confirmed stop.
Sys-init's actual client passes the unchanged single-core lifecycle v1 seam.
Retained fault records and repeated replacement pass in the bounded fixture;
general fault recovery and public-release preparation remain. Consult the canonical issue for any live continuation after cutover. The public
STATE file is navigation, not evidence that a historical result was requalified. M2
orchestration remains BSP-only; M3 runtime and authority state are per-core.

## Private standards boundary

Read [PUBLIC-SOURCE](docs/PUBLIC-SOURCE.md) for unavailable private inputs and
public check coverage. Consumer adoption records remain in `docs/EXPERIENCE.md`,
`docs/STANDARDS.md` and `docs/DISTRIBUTION.md`; their referenced release/review
bytes are private. They are not a prerequisite to begin ordinary public prose or
self-contained model work that does not change their governed contracts.

Before a user-facing presentation, shared interface/authority, build/evidence,
package/service-boundary or distribution change that needs those normative
inputs, involve the owner and obtain the exact applicable private inputs. Keep
that dependent work blocked until its requirements can be evaluated. Do not
reconstruct private clauses, weaken a check, follow mutable sibling bytes or
claim standards conformance from public source checks. Existing domain contracts,
consumer locks, machine protocols, smoke markers and emergency diagnostics remain
binding. Shared normative changes belong with the private standards owner.

## Licensing

BSD-2-Clause is the default for original work across this system repository and
the separate Aether-standards repository.
Read the consumer [licensing summary](docs/LICENSING.md), root LICENSE and
applicable upstream notices. Preserve third-party terms and
existing notices. Use `SPDX-License-Identifier: BSD-2-Clause` for new original
source files where appropriate. Do not rewrite immutable standards, fixtures or
evidence to add headers. Package recipes do not relicense their upstream payloads.


## Standards review and development process

Before new work, read `docs/DEVELOPMENT.md`. Consult the applicable consumer
adoption record and private inputs only when required by the affected scope.
Documentation/Testing/Coding and Distribution 0.2 content is maintainer-approved
but unreleased. Do not re-request that content approval. Apply the scoped local
process; immutable release pins, implementation reviews and runtime compliance
remain separate.
Use required pinned review inputs for reproducibility; do not follow mutable
sibling bytes. The excluded whole RC1/ADP-01 packet and local qualification
receipts and all standards release/review bytes remain unavailable for public
replay; retained consumer locks remain unchanged. Missing required inputs are
blocked coverage, not a waived gate. Record the requirement, forbidden outcomes,
affected profiles/owners,
test selection, documentation impact and unsafe/resource implications before code.
Update `docs/workflow.json` when adding native references, launch profiles or
script entry points. Use focused affected tests during iteration and before merge;
reserve `zig build test` and broad target suites for major milestones/integration
handoffs or changes with broad or uncertain risk, as defined in DEVELOPMENT.
Do not repeat passing checks without relevant input changes or unresolved concerns.
Preserve all failed attempts; freeze sources during qualified runs. Missing
required runners, reader reviews or extended evidence remain blocked coverage.
The native-home broad host aggregate retains its 300-second bound where its
contract selects it; source-integrity/model CI cannot replace it or grant another guest.
Zero mandatory GitHub approvals for solo maintenance do not waive separate peer
review. Do not claim release readiness, owner sign-off or full draft adoption from
an inventory checker. Apply scoped language/format rules and migration exceptions
in DEVELOPMENT; no mass reformatting or immutable-evidence edits.

## Codex routing

Apply the Codex routing profile selected in PROJECT.md. When a bounded handoff
is useful, assign routine inspection to `temper_workflow`, accepted implementation
to `temper_implementer`, difficult analysis to `temper_analyst`, and final separate
review to `temper_reviewer`. Supply the owning work record and discussion,
applicable policy, relevant inputs, acceptance, checks and edit boundaries.
Follow the recorded resource, escalation and fallback rules; the lead verifies
returned evidence and owns integration. Installation does not change an existing
chat's model or prove runtime role discovery.

## Terra product role

Under the routing policy in PROJECT.md, assign accepted bounded product
documentation, visual inspection, explicitly authorized browser tasks and small
specified UI fixes to `temper_product`. Keep existing role assignments and all
local execution/risk/review limits. The lead may select the recorded Sol
implementer fallback explicitly; missing tools or authority remain blockers.
