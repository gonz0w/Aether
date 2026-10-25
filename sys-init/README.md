# sys-init

This component lives in the Aether system repository. Commands here run from
this directory unless stated otherwise. Start with the pinned [Agent Temper
method](../.agent-temper/METHOD.md), root [engineering policy](../PROJECT.md) and
[public work navigation](../.planning/STATE.md#system-work-index). Under
[root PROJECT cutover policy](../PROJECT.md#public-onboarding-cutover), GitHub
Issues own live work only after verified onboarding/migration. Until then only
the approved bootstrap record owns onboarding. STATE is navigation; component
snapshots and all dated next actions below are read-only historical context.
Local qualification receipts/SDK bundles are excluded from the public snapshot;
a summary is not a public replay or a fresh validation. See the
[repository guide](../docs/REPOSITORY.md) for dependencies and checkout boundaries.
Standards releases/review snapshots and imported hooks remain private; see the
[public-source boundary](../docs/PUBLIC-SOURCE.md). Ordinary public documentation
uses available local policy; affected normative work requires the owner and exact
private inputs. Aggregates that require those inputs remain blocked without them.


The init and service lifecycle project for the Aether operating-system effort, alongside the [Aether kernel](../README.md) and [pkg-mgr](../pkg-mgr/README.md).

The goal is a small, fast, understandable init: familiar POSIX shell concepts, reliable service supervision, clear failure reporting, and recovery from a minimal environment. We will compare existing init systems and select ideas that work well together. Features must justify their complexity.

The [FILE mutation observation seam](docs/decisions/0223-file-write-observations.md)
keeps write completion separate from reply delivery and endpoint cleanup. From the
system repository root run
`PYTHONOPTIMIZE=1 python3 -B sys-init/scripts/check-file-write-observations.py`.
Its plain CLI reports compact evidence and cleanup; inspect a failure before
retrying. This host/no_std checkpoint selects no native owner or guest. Exact
contracts and continuation belong to the linked owning record.

**Status:** tested policy model and bounded macOS host adapter, plus native Aether lifecycle, C supervision and byte-stream experiments. [Native coverage and contract gaps](docs/NATIVE-COVERAGE.md) separates demonstrated behavior from remaining work and mutable companion sources. Production init architecture, language and supervisor recovery remain open.

**Delivery scope:** [simple Aether v1](docs/V1-SCOPE.md): useful boot, simple
service configuration, bounded supervision and orderly shutdown. Broader features
are shelved for a later release. The [direct service pair](docs/SIMPLE-SERVICE-PAIR.md) now handles startup, provider
replacement and reverse shutdown;
[useful boot integration](docs/INIT-COMMAND-ADAPTER.md) now has a verified ABI9
command handoff and seven passing native cases, including controlled stop, within
the 8 KiB code limit. The bounded ABI22 [request loop](docs/SUSTAINED-INIT-HANDOFF.md) now demonstrates
idle, useful reuse and shutdown at completed-cycle boundaries; production
error recovery and complete handoff acceptance remain open. The
[current delivery map](docs/SI07-DISPOSITION.md) separates proven behavior from
the remaining supervision and matched-environment work. Build and boot the current
developer composition with the [offline ABI22 recipe](docs/AETHER-BASELINE.md). Its
explicit service-table profile separates the startup test probe and validates the
three-role order and image mapping. An explicit supervised profile permits one
pre-effect command replacement after known cleanup; after-I/O failure, exhaustion
and unknown cleanup close admission. The [serial boot composition](docs/SERIAL-BOOT-COMPOSITION.md)
selects one shell under one sys-init authority owner. The kernel
lifecycle/wait mechanisms and userland009 runtime now have sealed evidence.
An [owned serial-session candidate](prototypes/native-session/README.md) boots
actual dash through a local sys-init entry and passes immediate/delayed bounded
workloads and denial controls. A confirmed terminal/read-EOF race now has a small
repair and fresh before/after witnesses; the precise earlier failure caller was
not retained. The [maintained serial recipe](docs/AETHER-SESSION.md) now builds and boots the
bounded candidate. Independent userland consumption qualifies its eleven final
denial controls; continued shell use awaits a matching wider SESSION lifetime
profile. Complete v1 acceptance remains open.
A separate [ABI29 filesystem owner candidate](prototypes/native-filesystem/README.md)
now prepares read-only filesystem activation, one small dependent process and
ordered shutdown. Aether's exact native activation/readback and five failed-peer witnesses are now
[consumed locally](docs/decisions/0191-filesystem-native-consumption.md).
Filesystem-backed shell/runner/package acceptance remains open.

Run the policy model with `python3 scripts/check-runtime-model.py`; [results and limits](docs/RUNTIME-MODEL.md) explain its 287 tests and negative controls.

See [the lifecycle experiment](docs/LIFECYCLE-V1.md) for build/test commands, results and limitations.

| Start here | Purpose |
| --- | --- |
| [Project direction](.planning/PROJECT.md) | Goals, scope, and success criteria |
| [Native service lifecycle](docs/NATIVE-SERVICE.md) | One provider/dependent workload and failure controls |
| [Provider normal return](docs/decisions/0020-native-provider-return.md) | Post-admission worker return, cleanup and replacement |
| [Readiness failures](docs/decisions/0021-native-readiness-failures.md) | Distinct silent deadline and malformed-frame rejection |
| [Readiness retry](docs/decisions/0022-native-readiness-retry.md) | Cleanup before replacement and fresh readiness before dependent launch |
| [Retry budget](docs/decisions/0023-native-retry-budget.md) | Three-attempt exhaustion with no further launch |
| [Retry cancellation](docs/decisions/0024-native-retry-cancellation.md) | Cancelled intent closes retry and readiness admission |
| [Native policy review](docs/NATIVE-POLICY-REVIEW.md) | Model alignment and remaining control contracts |
| [Control operations](docs/specs/CONTROL-V0.md) | Logical request identity, conflicts, cancellation and replay proposal |
| [Dependency loss](docs/decisions/0025-native-dependency-loss.md) | Preserve admitted dependents while blocking new admission |
| [Native adapter](docs/NATIVE-ADAPTER.md) | Bounded extraction, target results and sequential-reuse kernel handoff |
| [Native coverage](docs/NATIVE-COVERAGE.md) | Tested native behavior, evidence audit and remaining contracts |
| [System work index](../.planning/STATE.md#system-work-index) | Selected bounded record and continuation |
| [Component history](.planning/STATE.md) | Dated evidence summaries |
| [Runtime draft](docs/specs/RUNTIME-V0.md) | Initial semantics and proposed conformance traces |
| [Roadmap](.planning/ROADMAP.md) | Component capability and completion criteria |
| [Backlog](.planning/backlog/PRIORITY.md) | Existing story IDs and candidate priorities |
| [Research guide](docs/RESEARCH.md) | Where earlier findings live and what needs review |
| [Companion project boundaries](docs/INTEGRATION.md) | Aether and pkg-mgr questions |
| [Working process](.planning/README.md) | How to track and finish work |
| [Contributing](CONTRIBUTING.md) | Change review, test selection and evidence obligations |
| [Updated standards review](docs/STANDARDS-UPDATE-REVIEW.md) | Released pins, draft disposition and remaining adoption work |

The POSIX-facing distribution is the product goal. Aether's current capability multikernel bring-up does not yet establish a POSIX runtime for this init; the mapping needs an explicit contract.

Previous workflow files, including unfinished work, are preserved in the [September 5 archive](docs/archive/2026-09-05-planning-reset/README.md). Historical completion labels and workflow commands do not govern current work.

Shared UI/UX: the consumer [Experience adoption](docs/EXPERIENCE.md) records
applicability; its referenced specifications remain private.

Shared engineering contracts: [Foundations, authority, interfaces and evidence](docs/STANDARDS.md).
The [consumer standards adoption](docs/STANDARDS.md) routes domain contracts;
package/service integration remains a shared candidate proposal.

Real foreground-child supervision and descriptor validation now have a [bounded host experiment](docs/HOST-RUNTIME.md). Run `python3 scripts/check-host-runtime.py`; native integration and production init remain open.

Standards-first work: [adoption review and scoped compliance results](docs/STANDARDS-REVIEW.md). Future shared standards belong in Aether-standards; exact lifecycle implementation remains owned here.

Select affected checks under root [DEVELOPMENT](../docs/DEVELOPMENT.md). For the
current aggregate, run `make check-init` from the system root or
`python3 scripts/check-all.py --current` from `sys-init/`. The default command still
requires the historical audit; both modes also need their private standards
inputs. Unavailable closure remains blocked coverage, and host
checks do not replace fresh native acceptance. See [reports and coverage](docs/DEVELOPMENT-CHECKS.md).

[Native C supervision](docs/NATIVE-SUPERVISION.md) now passes with the sys-init-owned Rust experiment client, including failure controls. Production init remains open.

## License

Original work is licensed under [BSD-2-Clause](LICENSE). Third-party material
retains its own terms. See the [consumer licensing summary](../docs/LICENSING.md) for scope,
contributions and redistribution. Contributors retain copyright in their work.

The [native descriptor/byte-stream checkpoint](docs/NATIVE-IO.md) adds bounded read, EOF, duplication, closure and redirection evidence; console/TTY and a real shell remain next.

Exploratory host performance: `python3 scripts/measure-host-runtime.py`; [method, baseline and limits](docs/HOST-MEASUREMENTS.md).

[Native init ABI-6 consumption](docs/NATIVE-INIT.md) now exercises registered
waits, interrupt-count deadlines, channel readiness and fail-closed supervisor
shutdown with independently authored sys-init policy. Broader recovery remains open.

## Git workflow

Follow root [source-control and integration policy](../PROJECT.md#source-control-and-integration-authority)
and review `git diff`, `git diff --cached` and the actual proposed tree/message
from the system root. Imported hooks remain private; run required affected checks
and public CI. Required checks and separate review precede integration; use only
the owner-approved public destination.

Security issues: use the root [private reporting policy](../SECURITY.md) for
the verified GitHub reporting route and experimental support scope.

The repaired ABI24 serial-shell candidate has a maintained [offline build and boot recipe](docs/AETHER-SESSION.md). It preserves released pins and requires exact qualified owner bytes; use `--smoke immediate` or `--smoke delayed` for bounded consuming checks.

A separate [AF07 filesystem owner candidate](prototypes/native-filesystem-af07/README.md)
now has an [exact native consumer review](docs/decisions/0193-af07-native-consumption.md).
The [original boot-parent mismatch](docs/research/ABI29-BOOT-PARENT.md) is resolved by the corrected v2 input; full native shell composition remains pending. The accepted AF06 delivery and existing defaults remain unchanged.

The corrected [ABI29 v2 dispatcher core](prototypes/native-filesystem-session/README.md)
now passes startup/child-wait host interoperability with the linked client input.
The former parent7 mismatch is fixed upstream; full AF07 FD/path/exec and native
shell dispatcher composition remain pending.

A [bounded file-exchange driver](prototypes/native-filesystem-session/FILE-RPC.md)
now interoperates with the selected C transport in fresh host sessions. Shell
facade routing, executable admission and native placement/fit remain open.
