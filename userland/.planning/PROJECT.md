# Project

Established 2026-09-05 from the user's project direction and toolchain discussion.

## Outcome

Define and validate a modern, security-focused userland that pkg-mgr can package
and sys-init can start on Aether, progressing to a workable POSIX TTY system.
An interactive Zsh session with reliable pipelines, job control and recovery is
the first user-facing destination. A prompt alone is insufficient.

## Accepted direction

- Prefer Clang/LLVM for C packages; use host cross-compilation before self-hosting.
- Investigate musl as the leading libc candidate without assuming superior
  security/performance or compatibility with the existing native kernel ABI.
- Prefer a small system/recovery shell separate from interactive Zsh.
- Keep the base small, maintainable and capability-scoped. Security is critical.
- Proceed with a native musl transport experiment preserving internal conventions
  (decision 002); retain an unmodified Linux reference for comparison.
- Track research, integration dependencies, and executable evidence from the start.

## Not decided

Final musl adapter design and target validation; production target
triple/ABI; POSIX service ownership/topology; final shell/utility versions; utility
provider; authenticated login and administrative authority; filesystem layout;
dynamic linking; exact POSIX conformance scope (Distribution PX-01 proposes POSIX.1-2024 as the requirements reference). See UL-002 through UL-013.

## Scope and boundaries

This project owns userland requirements, package evaluation, cross-toolchain
experiments, and end-to-end acceptance. Runtime-service implementation ownership
must be agreed explicitly. Aether owns kernel mechanisms and loader contracts;
sys-init owns bootstrap/supervision policy; pkg-mgr owns recipes, artifacts,
installation and trust policy. Native Rust services do not require all imported
applications to use Rust, nor determine sys-init's language.

Initially exclude graphical desktops, native GPU terminal work, network services,
SSH, a self-hosted compiler suite, and a full Linux binary-compatibility promise.
They can become follow-on work after the TTY base is demonstrated.

## Shared experience

Adopt Aether Experience v0.1.0 and the Hearth palette for new first-party user-facing work. `docs/EXPERIENCE.md` records the pin, scope and migration status. This shared presentation contract does not change kernel authority, service lifecycle, package state or upstream interfaces. Existing surfaces migrate through separately tested implementation work.

## Bounded runtime ownership — 2026-09-29

The maintainer explicitly assigned the bounded libc/POSIX runtime implementation
to Aether-userland. This repository owns its adapter build, SDK component closure
and consumer qualification. Aether retains kernel ABI/grants/enforcement and the
fixture owner; sys-init retains supervision policy and pkg-mgr package policy.
No general POSIX service assignment or sibling implementation edit is implied.

## Lab-first continuation — 2026-10-03

The maintainer directs continued implementation toward a running bootable lab
instance and will perform SSDK-06 reader review later when time permits. That
review stays open without blocking local coding and experiments. This direction
does not approve SDK/release promotion or transfer sibling implementation policy.
The first delivered lab artifact is the existing bounded x86-64 UEFI VM session
profile; unrestricted sessions and physical-lab hardware require further evidence.


## Persistent filesystem service direction — 2026-10-18

The maintainer's [current owner handoff](../docs/evidence/filesystem-policy-2026-10-18/producer-pair.json)
assigns the operational Rust filesystem service to Aether-userland and commits R1
to retained OpenZFS behind it. Aether owns native engine/block contracts; sys-init
and pkg-mgr retain activation/install policy. Deliver persistent shell/runner and
package bytes/records first; snapshot/rollback is post-R1. The first private
[policy implementation](../experiments/filesystem-service/README.md) is host-tested
under UL-082; live bridge/transport/engine and assembled acceptance remain open.
