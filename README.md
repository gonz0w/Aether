# Aether

[![Source checks](https://github.com/gonz0w/Aether/actions/workflows/ci.yml/badge.svg)](https://github.com/gonz0w/Aether/actions/workflows/ci.yml)

Aether is a hobby operating system built to learn how a small, understandable
system can fit together. It is an experimental x86_64 capability multikernel,
with a Zig kernel and Rust user-space services.

Each participating core owns its local kernel state and cooperates through
explicit messages. Capabilities describe what a domain may access. Higher-level
policy belongs in services that can be isolated and replaced.

There is plenty left to build. Questions, careful bug reports, research notes
and documentation feedback are welcome.

## Where it stands

The accepted foundation includes bounded QEMU experiments for UEFI boot,
protected user domains, capability-controlled IPC, two-core messaging, a Rust
framebuffer service and supervised worker replacement. Native C, filesystem and
shell integration have their own narrower experiments and evidence.

**Aether is not yet a complete boot-to-shell distribution.** The first release
still targets sys-init booting into interactive serial **Zsh**, with a working
runner, persistent **OpenZFS** behind the Rust filesystem service, and native
package management. Existing dash sessions and framebuffer demos are foundations
for that goal. General recovery and assembled-system qualification remain open.

QEMU x86_64 is the first target. Physical x86_64 bring-up follows; native NVIDIA
display support is deferred. The boot framebuffer does not provide a native GPU
driver.

Read the [architecture](docs/ARCHITECTURE.md) and
[R1 acceptance gates](.planning/ROADMAP.md#r1--first-release-persistent-boot-to-shell-system)
for the contracts and limits behind these statements. Follow [Issues](https://github.com/gonz0w/Aether/issues)
for current work; a dated experiment is evidence for its recorded inputs.

## One repository, four components

| Component | Responsibility |
| --- | --- |
| [Kernel](docs/ARCHITECTURE.md) | Per-core execution, capabilities, memory, IPC and hardware-facing mechanisms |
| [userland](userland/README.md) | User-space services, filesystem policy, C runtime and shell integration |
| [sys-init](sys-init/README.md) | Boot ordering, readiness, supervision and shutdown policy |
| [pkg-mgr](pkg-mgr/README.md) | Package artifacts, package state and installation policy |

Package installation does not activate a service or create authority. Shared
interfaces stay explicit, and each mutable object has an authoritative owner.
The [repository guide](docs/REPOSITORY.md) explains component commands and pins.

This public snapshot is focused on source and versioned documentation. Local
qualification receipts, SDKs, prepared images and generated build bundles are
excluded; local working history is preserved separately. Standards releases,
review snapshots and imported Git hooks also remain private. The
[public-source boundary](docs/PUBLIC-SOURCE.md) identifies unavailable inputs and
which checks can run here. A fresh checkout cannot replay every historical result.

## Build the kernel experiment

The documented setup is validated on arm64 macOS. No other host setup is
qualified yet. Install the exact versions in the
[dependency and boot guide](boot/DEPENDENCIES.md):

| Tool | Pinned or tested version |
| --- | --- |
| Zig | 0.16.0 |
| Rust | 1.98.0, with `x86_64-unknown-none` |
| QEMU | 11.1.1 |
| xorriso | 1.5.8.pl02 |
| Python | 3.14.7 tested |

You also need `curl` and a working Rust toolchain manager. Package-manager latest
versions may differ from these pins; check before building.

From the repository root:

```sh
rustup toolchain install 1.98.0 --profile minimal --target x86_64-unknown-none
python3 scripts/deps.py
zig build
zig build run
```

Setup downloads checksum-verified Limine and OVMF inputs into `.deps/`. Subsequent
kernel builds use those local inputs. The generated image is `zig-out/aether.iso`;
the run command opens QEMU. Close its window or press Ctrl-C to stop.

For checks, start with the [development guide](docs/DEVELOPMENT.md) and choose the
checks affected by a change. The broad `zig build test` gate and component/native
suites have additional prerequisites; missing local inputs are blocked coverage.
The hosted jobs are **Source integrity** (Agent Temper digests, selected
Python syntax/JSON and conventional PR titles) and **Kernel models** (self-contained
Zig roots). They do not validate private standards or establish native
OS behavior or release readiness. `zig build test` and `make check-system` retain
their required private standards/local inputs and are blocked without them;
`zig build` keeps its documented boot prerequisites.

## Join in

- Use [Issues](https://github.com/gonz0w/Aether/issues) for reproducible bugs and bounded feature requests.
- Use [Discussions](https://github.com/gonz0w/Aether/discussions) for questions, design exploration and
  sharing experiments.
- Read [CONTRIBUTING](CONTRIBUTING.md) before proposing work. Pull requests are
  currently opened by the repository owner; public issue reports are welcome.
- Report vulnerabilities through the [private security route](SECURITY.md).

The [wiki](https://github.com/gonz0w/Aether/wiki) is a short navigation guide. Versioned source documents
hold technical contracts and historical summaries. Issues become the sole live
work authority after verified onboarding/migration; legacy planning queues remain
read-only context.

## License

Original Aether work uses [BSD-2-Clause](LICENSE). Imported code, firmware and
other third-party material retain their own terms and notices. See the
[repository licensing summary](docs/LICENSING.md) before reusing or distributing
mixed artifacts.
