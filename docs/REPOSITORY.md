# Working in the public system repository

This consumer contains the kernel at its root plus `userland/`, `sys-init/` and
`pkg-mgr/`. Runtime ownership, languages, release pins and experiment limits stay
unchanged. Standards, distribution, installer and origins companions remain
local; this repository does not publish them.

Read [PROJECT](../PROJECT.md#public-onboarding-cutover), root
[AGENTS](../AGENTS.md), the pinned [method](../.agent-temper/METHOD.md) and affected
component guidance. GitHub Issues become the sole live work authority only after
verified onboarding/migration. Until then the approved bootstrap record owns that
operation. Root STATE is compatibility navigation; component planning records
are read-only historical inputs. ROADMAP supplies capability gates, not tasks.

## Use the public checkout

The proposed public default branch is a new clean `main` from the owner-approved
curated snapshot. This is not a merge into the original local main and does not
publish the private consolidation history. Confirm the destination and source
manifest before bootstrap; no configuration or migration completion is claimed
by this guide.

After bootstrap, create ongoing branches from public `main` in a separate public
clone, or a worktree of that public clone. A worktree of the private historical
repository still shares private refs/objects and is not the public working base.
Do not merge or push private branches, legacy/migration refs, all refs or a mirror.
Port a reviewed change explicitly onto the public base and inspect its exact
published tree. Use only the confirmed public remote and approved refs.

Keep original local repositories, Git/JJ metadata, working files, historical refs
and unaccepted AF09 work intact and local. The accepted private consolidation
`0c84f5463abeb25b9cb776ad6d52d41e02f979d7` and original local main
`78c13fc5f5329bb590c2ab4772f2e1e2372dc067` are local provenance, not public ancestor
claims. This source snapshot does not imply that they merged locally.

## Ownership and work

One accepted integration change may span components while preserving their
contracts. Sys-init owns lifecycle policy, userland owns services/shell/FILE
integration, pkg-mgr owns package state and installation, and the kernel enforces
its native authority boundaries. Installing a package does not activate a service.

After cutover, read the owning issue and discussion, inspect current source and
reviews, and confirm finite acceptance and prerequisites before implementing.
Keep progress, actual checks, dependencies and continuation in that issue.
Durable contracts and decisions stay in source; legacy IDs remain useful links.
A historical next action or folder name is not current authorization.

Public PR submission remains owner-only. Diff/tree/message review, coherent commits, required
affected checks and separate peer/owner review still precede integration. A
zero-mandatory-approval solo-owner branch rule is not a review waiver. Native,
resource, publication and release approvals remain separate.

## Commands and coverage

Component documentation commands run from the component directory unless stated
otherwise. Root entry points include:

```sh
make check-userland
make check-init
make check-packages
make check-kernel
# Only when the selected integration scope requires it:
make check-system
```

These commands require private standards and, for affected profiles, local SDK/
qualification inputs; public-only aggregate coverage remains blocked. They
preserve their existing prerequisites and acceptance, rather than promising
that all local SDK-dependent checks run from a fresh public checkout. Follow
[DEVELOPMENT](DEVELOPMENT.md#test-selection-and-cadence) for focused checks and
required broad gates. `check-init --current` coverage remains distinct from an
unavailable historical replay. `check-system` is not assembled boot-to-shell or
release acceptance. Required missing inputs, runners or review are blocked
coverage; small hosted source-integrity/model checks are not substitutes.

## Pins, evidence and generated output

Standards releases, draft/review snapshots and imported Git hooks remain private.
Retained consumer adoption records and lock hashes identify private requirements;
they are not a published byte closure. See [PUBLIC-SOURCE](PUBLIC-SOURCE.md).
Ordinary public prose and self-contained model work use available local policy.
Affected normative changes need the owner and the exact private inputs before
dependent work can proceed. Builds must not follow mutable sibling bytes or
silently replace a lock.

The public snapshot excludes local qualification receipts, SDK/source/image
bundles, full test/build archives and the obsolete whole RC1/ADP-01 packet.
Historical summaries may refer to those unavailable inputs; their hashes do not
establish public replay or freshness. A missing required packet stays a gap.
Maintained small regression fixtures and non-standards dependency pins are
separate curated inputs; standards content is excluded.

Generated outputs belong in ignored private build/cache/stage roots. Retain
compact commands, source/tool/artifact identities, outcomes and short failures
under the existing [retention policy](DEVELOPMENT.md#evidence-and-failures), then
remove only owned generated outputs. Do not add new SDK copies, image bundles or
source archives as evidence. Preserve immutable releases, fixtures and historical
records; never change a seal to make a stale result pass.

Read [GITHUB](GITHUB.md) for hosted settings and migration verification,
[LICENSING](LICENSING.md) for this consumer's summary, and the applicable upstream
notices for imported material.
