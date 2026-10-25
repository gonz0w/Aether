# Aether userland

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

Shared standards are owned by [Aether-standards](../Aether-standards/README.md).
Use our pinned [standards adoption](docs/STANDARDS.md) and
[Distribution applicability map](docs/DISTRIBUTION.md) before relevant changes.

| Start here | Purpose |
| --- | --- |
| [Project](.planning/PROJECT.md) | Intent and accepted direction |
| [Architecture](docs/ARCHITECTURE.md) | Proposed boundaries and runtime requirements |
| [M2 acceptance](docs/M2-ACCEPTANCE.md) | Bounded native C gate and next shell dependency |
| [Roadmap](.planning/ROADMAP.md) | Milestones and acceptance |
| [Backlog](.planning/BACKLOG.md) | Ordered work, dependencies, open questions |
| [State](.planning/STATE.md) | Evidence and next action |
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

Companions: [Aether](../aether/README.md), [sys-init](../sys-init/README.md),
[pkg-mgr](../pkg-mgr/README.md). Their interfaces and implementation remain owned
by those projects. Consult their current state before integration.

Shared UI/UX: [Aether Experience and Hearth palette](docs/EXPERIENCE.md), with pinned offline specifications and staged implementation adoption.

Shared engineering contracts: [Foundations, authority, interfaces and evidence](docs/STANDARDS.md).
The [global catalog](../Aether-standards/docs/CATALOG.md) routes domain contracts;
package/service integration remains a shared candidate proposal.

Bounded native C now has an opt-in [source-rebuilt musl experiment](experiments/native-c/README.md) with two private contexts and semantic negative controls. General POSIX services remain separate work.

## License

Original work is licensed under [BSD-2-Clause](LICENSE). Third-party material
retains its own terms. See the [shared licensing policy](../Aether-standards/docs/LICENSING.md) for scope,
contributions and redistribution. Contributors retain copyright in their work.

The [native descriptor/byte-stream checkpoint](docs/NATIVE-DESCRIPTORS.md) adds bounded read, EOF, duplication, closure and redirection evidence; console/TTY and a real shell remain next.

Contributor entry point: [Contributing](CONTRIBUTING.md) and the [quality workflow](docs/quality/PROCESS.md).

[Minimal Toybox reference](experiments/toybox-reference/README.md): six applets built with Clang/musl and exercised under QEMU Linux; native port remains open.

## Git workflow

Review [the local Git workflow](.githooks/README.md), then run
`python3 .githooks/setup.py` after cloning. Hooks are opt-in per clone;
run the owning quality checks before integration. No origin is configured yet.
