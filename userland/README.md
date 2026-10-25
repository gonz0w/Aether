# Aether userland

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


Current consumer contracts: [boot-session filesystem lifetime](docs/proposals/FS-SERVICE-LIFETIME.md)
and [first Zsh closure](docs/ZSH-CONSUMER.md), with [target-link status](docs/ZSH-TARGET-LINK.md). Their linked GitHub issues own live
selection and status; the records distinguish host proofs from native readiness.

2026-10-22 UL-007/081/082: [real TLS shell relink](docs/proposals/FS-FORK-TLS.md) corrects
stage81's missing PT_TLS defect. A checked initialized four-byte C17 TLS object
survives the full link; Aether's unchanged actual ELF parser accepts the279568-byte
shell under default limits (79/128 pages including16 stack pages).1010 stage cases/
nine controls, frame5847, default/opt-in libc78 each and seven parser tests pass on
minimum/current Python. Native execution/whole peak fit and matching sys-init
transaction/owner/reader/full UL/M3/R1 remain open; old sealed bytes stay fixed.

2026-10-22 UL-007/081/082: [authoritative file view v1](docs/proposals/FS-FILE-VIEW.md) now
exports exact remote FILE presence/cloexec from the sole ProcessFiles ledger,
without source calls or mutation.31 process tests/13 controls plus borrow/compiler
and external host/target checks pass; default remote regressions pass. This supplies
sys-init0202/BG-071's requested input. BG-069/070 still require owner consumption,
exact pre-copy file/stream comparison, complete native transaction/settlement,
whole fit and fresh Aether witnesses. Full UL/M3/R1 and owner/reader remain open.

The [armed fork stage/child constructor](docs/proposals/FS-FORK-STAGE.md) now
links the full pinned shell with real __aether_fork_stage, guarded live capture,
child quarantine/rebind and one-shot context reconstruction.1008 host cases/seven
controls plus5847 frame/78 libc cases pass. This resolves the missing-stage link
block for the opt-in candidate; it is not a native boot witness.

Aether has selected serialized owner admission. The matching
[serialized file-view API](docs/proposals/FS-SERIALIZED-COPY.md) and new client
candidate await sys-init BG-069/BG-070's actual gated transaction, startup/ready/
parent disposition and settlement/readiness/shutdown. Whole resource fit and fresh
native qualification follow. Existing default bindings/pins remain unchanged;
immutable exec/public dup2/packages/Zsh/TTY and the persistent ISO remain open.

The [typed C file facade](docs/proposals/FS-FD-FACADE.md) now exercises actual C
requests through the Rust handler/process views/AF07 service over host pipes.
Open/read/seek/dup/close/cloexec, read denial and reply-loss cases pass locally.
Matching dispatcher, immutable exec and native fit/execution remain open; older
ABI29 candidates remain unchanged.

Aether now reports the AF07 operational owner linked and natively qualified,
including fresh recovery. The separate [ABI29 shell client candidate](docs/proposals/SESSION-FS-ABI29.md)
adapts startup/PID/parent/wait identity and now links complete pinned shell/helper
inputs, with host initial backing checks passing. Matching sys-init dispatcher,
filesystem-backed FD/exec and native runtime qualification remain next; the
persistent shell/package/Zsh ISO is still incomplete.
The [v2 client correction](docs/evidence/session-abi29-boot-parent-2026-10-21/README.md)
now accepts the actual generation0 boot supervisor/PID7 with strict native identity
checks; the earlier candidate's14/21/28 assumption was a startup bug.
The new [read-only file-description core](docs/proposals/FS-DESCRIPTORS.md) passes
owner-backed host tests for shared offsets, duplication, final close and failure
cleanup. The [AEFD0001 file-message candidate](docs/proposals/FS-FD-WIRE.md) now connects
checked process views to open/read/seek/dup/close/flags RPCs, with actual C/Rust
host interoperability and caller-owned workspace. The linked shell still needs
facade/startup/console/pipe integration, immutable exec and native composition.

A secure, maintainable TTY userland for Aether, packaged by pkg-mgr and supervised
by sys-init. The first destination is a useful POSIX shell environment; X and
other graphical desktops are outside the initial scope.

**Status:** Native dash now completes the composed session through three real
serial prompts in each of three parents, retaining shell state and checking cleanup.
[Latest serial qualification](docs/evidence/serial-session-consumer-2026-09-29/README.md)
passes169 native cases and132 Python plus configured Zig/Rust host checks.
Userland now owns the bounded runtime; its
[extracted candidate](docs/evidence/session-runtime-extraction-2026-09-29/README.md)
passes49 fresh native executions and a byte-identical standalone rebuild.
SDK promotion/reader reviews, broader SI-07 integration and full M3 remain open.
The [lab-image builder](experiments/lab-image/README.md) now supplies a bounded
x86-64 UEFI VM kit with a fresh three-parent interactive dash boot witness.
SSDK-06 reader review is deferred by the maintainer while implementation continues.
The explicit ABI24 runtime now survives delayed prompt input and produces a matched
[one-parent lab kit](docs/evidence/session-channel-wait-consumer-2026-10-03/README.md).
The [actual sys-init entry is now independently consumed](docs/SYSINIT-SESSION-CONSUMPTION.md);
its [read-EOF race repair is independently qualified](docs/evidence/sysinit-read-race-consumer-2026-10-04/README.md)
with a matched sys-init developer kit. The
[maintained owner recipe now rebuilds exactly](docs/evidence/sysinit-recipe-consumer-2026-10-04/README.md)
and supplies a fresh source-rebuilt boot kit. Broader composition/recovery remains open.
The [maintained boot checker](experiments/lab-image/README.md#check-a-delivered-abi24-kit)
now verifies a selected kit and exercises a fresh immediate or delayed VM boot.
Native authority and finite fixture limits remain unchanged.
The [corrected service reaper](docs/evidence/reaper-fix-2026-10-06/README.md) and
[matching UTC variant](docs/evidence/reaper-utc-2026-10-06/README.md) now provide
new sealed v3 candidates after a reproduced detached-exit lock cycle.
The [independent intake and engine helper reuse check](docs/evidence/fixed-reaper-consumer-2026-10-06/README.md) passes.
The [new Rust filesystem policy layer](experiments/filesystem-service/README.md)
now owns session/handle write authority, policy UTC, coherent aliases and retirement
after uncertain writes. It passes13 host tests and eight semantic-omission controls.
Aether reports native existing-file write/fresh-VM readback and assigns the operational
service here. Aether now reports successful Rust-write/fresh-recovery and eight finite
C writes, clearing the old timeout/callback blocker. The new bounded service request
loop and native entry pass host/ABI/object checks, including reply-loss retirement.
[Matched writable IPC selection and provisioning](docs/proposals/FS-SERVICE-TRANSPORT.md)
remain needed before native service launch and persistent shell/package assembly. OpenZFS is the R1
engine; snapshot/rollback follows R1. Wider SESSION support remains separate.

Shared standards are owned by Aether-standards (the local companion repository).
Our consumer [standards adoption](docs/STANDARDS.md) and
[Distribution applicability map](docs/DISTRIBUTION.md) identify relevant scope;
required private inputs must come through the owner before dependent changes.

| Start here | Purpose |
| --- | --- |
| [Project](.planning/PROJECT.md) | Intent and accepted direction |
| [Architecture](docs/ARCHITECTURE.md) | Proposed boundaries and runtime requirements |
| [M2 acceptance](docs/M2-ACCEPTANCE.md) | Bounded native C gate and next shell dependency |
| [Roadmap](.planning/ROADMAP.md) | Milestones and acceptance |
| [Backlog](.planning/BACKLOG.md) | Component candidates, dependencies and open questions |
| [System work index](../.planning/STATE.md#system-work-index) | Selected bounded record and continuation |
| [Component history](.planning/STATE.md) | Dated evidence summaries |
| [Clang/musl research](docs/research/CLANG-MUSL.md) | Findings, sources, first experiments |
| [Pinned musl audit](docs/research/MUSL-1.2.6-AUDIT.md) | Source requirements and adapter recommendation |
| [C runtime proposal](docs/C-RUNTIME-PROFILE.md) | First target experiment contracts |
| [POSIX inventory](docs/compatibility/README.md) | Native compatibility gaps and shell acceptance plan |
| [Descriptor fallback checks](experiments/descriptor-fallback/README.md) | Setter-denial evidence and experimental rollback patch |
| [Independent broker execution](experiments/native-process/RUNTIME.md) | Named worker launch/collect, denial and cleanup controls |
| [Native dash integration gaps](docs/NATIVE-DASH-GAPS.md) | Current broker/companion seams and prepared independent requester |
| [Bounded buffered files](experiments/native-files/STDIO.md) | Native FILE buffering, seek/flush errors, errno and cleanup |
| [Bounded libc file calls](experiments/native-files/LIBC.md) | Native C entry points, errno, short I/O and explicit unsupported operations |
| [Descriptor failure handling](experiments/native-files/FAILURES.md) | Lost acknowledgements, reply validation and failed-close cleanup |
| [Bounded file descriptors](experiments/native-files/DESCRIPTORS.md) | Shared positions, duplication, final-close lifetime and failure controls |
| [Writable scratch witness](experiments/native-files/WRITABLE.md) | Authority, rollback, zeroing and read-only regressions |
| [Native file consumer](experiments/native-files/README.md) | Four independent read-only protocol/authority/data cases |
| [Native channel consumer](experiments/native-channel/README.md) | Six independent native helper/transfer/cleanup cases |
| [Native process handoff](docs/NATIVE-PROCESS-PLAN.md) | Canonical shared draft, pending review and next consumer work |
| [Process/FD witness](experiments/process-reference/README.md) | Fork, exec, wait, sharing and failure evidence |
| [Dash reference](experiments/dash-reference/README.md) | Pinned shell build, twelve script cases and native dependency audit |
| [Package candidates](docs/research/PACKAGES.md) | Provisional base selection |
| [Decision 001](docs/decisions/001-toolchain-direction.md) | Accepted toolchain direction and limits |
| [Native memory adoption](docs/NATIVE-MEMORY.md) | Exact ABI adapter and target consumer results |
| [Native memory plan](docs/NATIVE-MEMORY-PLAN.md) | Shared allocation proposal and implementation gates |
| [Native C handoff](docs/NATIVE-C-HANDOFF.md) | Concrete consumer requirements and ownership proposal |
| [Host launch model](experiments/launch-profile/README.md) | ELF, TLS, RELRO and initial-stack validation |
| [Linux runtime results](experiments/musl-reference/RUNTIME.md) | Passing probes, traces and compiler-runtime witness |
| [Musl reference build](experiments/musl-reference/README.md) | Offline build, isolation checks and ELF evidence |
| [Compile probe](experiments/c-object/README.md) | Reproduce the first host check |

System components: [kernel](../README.md), [sys-init](../sys-init/README.md),
[pkg-mgr](../pkg-mgr/README.md). Their interfaces and implementation retain their
respective ownership. Read affected contracts and the root-selected record before integration.

Shared UI/UX: the consumer [Experience adoption](docs/EXPERIENCE.md) records
applicability; its referenced specifications remain private.

Shared engineering contracts: [Foundations, authority, interfaces and evidence](docs/STANDARDS.md).
The [consumer standards adoption](docs/STANDARDS.md) routes domain contracts;
package/service integration remains a shared candidate proposal.

Bounded native C now has an opt-in [source-rebuilt musl experiment](experiments/native-c/README.md) with two private contexts and semantic negative controls. General POSIX services remain separate work.

## License

Original work is licensed under [BSD-2-Clause](LICENSE). Third-party material
retains its own terms. See the [consumer licensing summary](../docs/LICENSING.md) for scope,
contributions and redistribution. Contributors retain copyright in their work.

The [native descriptor/byte-stream checkpoint](docs/NATIVE-DESCRIPTORS.md) adds bounded read, EOF, duplication, closure and redirection evidence; console/TTY and a real shell remain next.

Contributor entry point: [Contributing](CONTRIBUTING.md) and the [quality workflow](docs/quality/PROCESS.md).

[Minimal Toybox reference](experiments/toybox-reference/README.md): six applets built with Clang/musl and exercised under QEMU Linux; native port remains open.

## Git workflow

Follow root [source-control and integration policy](../PROJECT.md#source-control-and-integration-authority)
and review `git diff`, `git diff --cached` and the actual proposed tree/message
from the system root. Imported hooks remain private; run required affected checks
and public CI. Required checks and separate review precede integration; use only
the owner-approved public destination.

[Private native elapsed-clock adapter](experiments/native-clock/README.md): explicit-grant monotonic reads and absolute sleep with native deadline/error evidence; POSIX timed conditions and SDK promotion remain open.

[Maintained private service runtime](experiments/native-service-runtime/README.md):
opt-in musl thread/retirement and monotonic-wait SDK supplement, qualified in fresh
native VMs. Actual OpenZFS engine intake and broader POSIX acceptance remain open.


[Private shared UTC runtime](experiments/native-utc/README.md) now supplies an
opt-in explicit RTC-as-UTC estimate with checked calendar and libc timestamp
failure paths. Four final native cases and exact minimum/current/standalone
rebuilds qualify its sealed handoff. Aether has consumed it and checked actual
engine timestamps; historical engine liveness observations remain retained, while
current service integration and wider shell SESSION have separate acceptance gates. [Focused runtime schedules](docs/evidence/runtime-liveness-2026-10-06/README.md)
pass but do not resolve that engine observation.
