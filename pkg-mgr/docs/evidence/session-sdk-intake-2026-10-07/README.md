# Session SDK intake — 2026-10-07

Package-owner inert review of userland's selected private AENMX009/ABI24 bundle.
Identity verification passes; **the bundle is not admitted as a package**. No
candidate code, compiler, emulator, package publication or sibling write occurs.
This is not independent release approval or a new standards/release pin.

## Executed inspection

`python3 docs/evidence/session-sdk-intake-2026-10-07/audit.py` verifies the externally
selected archive digest `5389197b0041870d939fe621550a95f1890771377e2d75cb7687f9f8c9d1e2d6`
and manifest digest `2c15d39bdf109497796b19f3006d7276812b156b36b17ed95c71d9e39e3e6eef`.
Selection comes from userland's dated candidate-artifact.json, not hashes invented
from an unreviewed delivery. These are local identity checks, not authentication.
The one-shot script refuses to overwrite result.json. To repeat, retain this
attempt and use a separately reviewed output copy; do not erase the receipt.

[Result](result.json) records exact dirty-tree input hashes, tool/platform identity,
574 regular archive members (3,908,740 bytes), equality with the producer member
inventory, the manifest's 573 rows, and archive revalidation after inspection.
All archive modes are 0644. The archive is read without filesystem extraction or
support-module imports; README and recipe are copied as inert review excerpts.
The audit bounds membership, member/total sizes and names for this exact selected
archive; it is not a general hostile-archive parser or concurrent-writer guarantee.

All **231 musl SDK files are byte-identical** to the retained imported SDK's usr
subtree. This comparison does not requalify the old package's records, modes,
receipts or native profile. The containing delivery additionally has runtime,
application, fork/wait sources, support scripts, 37 prebuilt objects and nine
archives. Its own [README](candidate-README.md) explicitly describes prebuilt
CRT/libc/dash inputs. It is a bounded rebuild bundle, not complete source-only
reconstruction of every upstream component.

The [recipe](candidate-recipe.json) binds the private profile and exact external
tools. It is reviewed as inert data; no host toolchain setup or Apple qualification
was performed. The existing SDK remains a separate build-input package.

## Compatibility and disposition

| Finding | Existing coverage and next requirement |
| --- | --- |
| Same musl bytes, larger runtime delivery | Keep the existing SDK record/profile. Identical libc does not qualify changed runtime/bootstrap/application objects or ABI24. No SDK replacement is justified by this comparison. |
| No artifact.kv, package.tsv, target.kv, modes.tsv or dependencies.tsv | This is a producer build bundle, not local-sdk-directory-v1. Missing package tables are expected at this boundary, not a producer bug. Do not feed it to sdk-import or manufacture acceptance from its seal. |
| Session runtime is outside the accepted standalone aether-musl-sdk content scope | Before packaging, agree package identity/layout, complete source-versus-prebuilt inventory, exact build/native receipt selections and external tool/component dependency boundary with userland. Existing SDK transport only admits aether-musl-sdk with no package dependencies. Do not rename this whole bundle to bypass that restriction. |
| Complete source build remains separate | Trace the prebuilt CRT/libc/dash inputs to exact upstream sources, patches and reproducible recipes before claiming source-only delivery. This review verifies shipped bytes, not that full chain. |
| Native execution needs a matched composition | The producer's ABI24 lab witness remains scoped to its kernel/owner/client closure. Metadata grants no rights. No new package-native admission or bin/pkg-mgr execution is established. |
| Storage and package-ready tool closure remain open | Aether's October 7 STATE records failed pool creation and stopped persistence qualification. Follow the existing native prerequisites and ISO card after owner evidence; no pool retry here. |

Applicable released Foundations O-01/O-02 preserve ownership and authority; I-02
keeps recipe inspection inert; E-01/E-04/E-05 separate pinned input identity,
producer native claims and this consumer check; I-08 excludes durability claims.
No new exception or shared policy is needed. All released pins remain unchanged.

The simplest useful action is this bounded comparison and the existing regression
checks. A new importer or generalized package role would add policy and failure
paths before the producer/consumer contract exists. No runtime complexity is
removed now. This one-shot evidence capture adds no installed command, subsystem,
format, test-suite entry or parallel tracking system; the development inventory's
existing SDK entries remain applicable.

## Checks and stopping condition

[Checks](checks.json) retain commands, statuses, durations and raw stdout/stderr
for the existing 65-case SDK profile and 24-case transport suites. These are
synthetic host controls, not transport of the new bundle. Standards and development
gates are recorded separately in gates.json. No runtime source changes require a
new full-suite run; no build/native witness is inferred from these tests.

Next package work requires the scoped runtime package handoff described above.
The existing [native prerequisite inventory](../../NATIVE-PACKAGE-PREREQUISITES.md)
and [ISO test card](../../ISO-PACKAGE-TEST.md) still govern installed execution.
Userland's deferred reader review is not itself a development stop. Package scope,
source closure and native/storage contracts are the actual remaining boundaries.
