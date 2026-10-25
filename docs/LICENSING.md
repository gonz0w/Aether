# Licensing in this repository

This is a consumer summary for the Aether system repository. The applicable
license texts and notices govern the material they accompany. This document
introduces no new shared standard or license grant.

## Original Aether work

[BSD-2-Clause](../LICENSE) is the default for original work in the kernel,
`userland/`, `sys-init/` and `pkg-mgr/`, including source, documentation, examples,
tests, build tools and package recipes. Existing named notices remain in place.
The collective notice “Aether contributors” does not transfer copyright;
contributors retain their rights in their own contributions.

Original work intentionally submitted for inclusion is offered under BSD-2-Clause
unless different terms are identified and accepted first. No copyright assignment
is required. Add `SPDX-License-Identifier: BSD-2-Clause` to new original source
where appropriate. Do not rewrite immutable pins, fixtures or evidence to add a
header.

## Imported material keeps its terms

The default does not relicense upstream code, firmware, compiler/runtime material,
third-party text, vendored releases or modifications subject to upstream terms.
Preserve their license texts, copyright, attribution and provenance. A package
recipe's license is separate from its payload's license.

For example, the imported [Agent Temper method](../.agent-temper/LICENSE) retains
BSD-3-Clause. OpenZFS, musl and boot dependencies retain their own terms; consult
the relevant source notices and [boot dependency provenance](../boot/DEPENDENCIES.md).
Published source permission does not imply permission to redistribute every
external SDK, firmware image or generated binary.

Before adding or distributing an import, record its supplier, revision/version,
input digest, applicable license, local changes and required notices. For a mixed
binary or image, include the first-party license and the applicable third-party
notices. Do not describe the whole artifact as relicensed under BSD-2-Clause.

## Source snapshot and later distribution

The public source snapshot excludes local SDK and generated image bundles.
Maintained imports or offline pins that are included must retain their exact
approved bytes and notices. Publishing this snapshot does not publish separate
companion repositories or change the existing terms of local history.

Any later distribution needs its own complete artifact/license review. Selecting
a permissive default does not establish release readiness, patent clearance,
security support or permission to redistribute a particular proprietary component.
