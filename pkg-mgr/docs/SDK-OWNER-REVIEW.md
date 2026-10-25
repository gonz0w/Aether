# Userland SDK handoff: pkg-mgr review

2026-09-07. Local design response to userland UL-005's
[proposal](../../userland/docs/SDK-PACKAGE-HANDOFF.md) and
[owner packet](../../userland/docs/SDK-OWNER-REVIEW.md).
This selects the scope for a future private cross-SDK experiment. It is not a new
wire format, implemented recipe, maintainer sign-off or native release approval.
No sibling repository was modified or message sent. Aether remains the sole release
target; no Apple qualification or packaging work is opened.

## Verified material

The [local receipt](evidence/sdk-owner-review-2026-09-07/verification.json) verifies
manifest SHA-256 0887ee33354e2f177373b83a2d2d8af492adb5d5393eae3f52a1b68da5cdbfe8,
all 247 listed regular files, their exact set, sizes, ordinary modes and hashes,
and all 231 SDK files against the captured consumer inventory. Links, special files,
duplicate paths and unexpected files were absent. The separate musl COPYRIGHT
matches the member read from the SHA-256-verified musl 1.2.6 archive. The archive
was not extracted and the preparation script was not executed.

This is integrity of local review materials. It is not source authentication,
complete rebuild closure, successful staging or native consumer qualification.
The input directory remains owned by userland; reverify before later consumption.

## Selected local design and unresolved representation

| Concern | pkg-mgr decision for the first experiment |
| --- | --- |
| Scope | One private cross-SDK data package, provisionally named aether-musl-sdk; compiler stays an explicit external build prerequisite. No compiler distribution, live prefix or service activation |
| Layout | Map sdk/stage/usr/include and sdk/stage/usr/lib into usr/local/lib/aether-sdk/musl-native-experimental/usr/include and usr/local/lib/aether-sdk/musl-native-experimental/usr/lib beneath ROOT/stage/aether-musl-sdk. Preserve every selected regular file and its ordinary mode; keep the SDK separate from build-host search paths |
| Notices/provenance | Include unchanged musl COPYRIGHT at usr/local/share/licenses/aether-musl-sdk/COPYRIGHT. Retain the pinned archive, transformation/patch and build receipts as source provenance; the 231-file SDK list alone is insufficient |
| Identity | Bind build-host/tool observations separately from produced-artifact architecture, exact native profile/producer and selected adapter closure. A Linux-musl compiler string is not an Aether ABI, and host-only must not describe target runtime support |
| Dependencies | Keep libc, headers and startup objects together initially. A consumer must bind the exact SDK record plus its separately selected adapters and compiler/linker inputs. Do not claim the SDK includes the adapters merely because receipts mention their hashes |
| Updates | Explicitly enumerate affected static consumers using dependency records and retain their build-input identities. An SDK replacement cannot update already linked code; rebuild and requalify each affected consumer before selecting it. No new solver or automatic rebuild service |
| Recovery | Reuse only the existing single-writer, caller-controlled private-root rules after profile admission is implemented. An occupied stage rejects; explicit pinned recovery may adopt only an exact retained stage. No installed-payload deletion or crash-atomic publication claim |

The layout is a logical mapping, not a command to create these paths in a live
system. Headers exposing functions do not establish their native implementation.
The 14 library/startup files include multiple startup variants; preserve the input
set, but choose and qualify a concrete link invocation instead of linking all of
them or assuming every variant works on Aether.

A separately named cross-SDK admission profile is required before SDK-02. Preserve
[host-binary-target-v1](BINARY-PACKAGE.md) behavior and its rejection of unsupported
runtime values. An unvalidated sidecar or free-form note is insufficient: identity
must be manifest-bound and checked on both export and import. This review does not
assign a wire-format version, a native ABI name or a fake host observation. Exact
schema, producer binding, compatibility behavior and wrong-profile tests remain a
bounded implementation design to review with userland before changing the parser.

## Compatibility findings and next evidence

| Finding | Existing coverage | Missing work / disposition |
| --- | --- | --- |
| All 231 SDK inputs are regular 0644 files | State v2 records regular bytes/modes; v2 transport rejects links/special types | SDK-01 payload mapping and license path now pass in the layout witness below; complete profile-bearing stage and registration remain open |
| Current export/import requires host-only and compares host/compiler fields | mk/binary.sh and manifest-bound host.kv preserve current admission | SDK-02/03 need an explicitly checked cross-SDK identity profile; do not bypass or relabel existing checks |
| Build receipt names I/O and memory adapters by hashes | Captured libc/startup/header identities verified | Adapter source/object bytes and matching native producer closure are not a complete consumer kit in this bundle. Select and capture them before SDK-05/08 |
| Existing build commands refer to original build locations | Original commands and patch receipts retained | SDK-05 needs a reviewed invocation using only imported SDK paths and explicit external tools; missing inputs must fail without host-header/libc/helper fallback |
| Exact dependency records and rdeps already exist | Package-state views and dependency fingerprints are implemented | SDK-07 must demonstrate stale static consumers after an input change and their rebuild/retest; existing views do not automatically bind arbitrary compiler inputs |
| Two-step stage/record publication and retained-stage recovery exist | Host transport interruption controls pass | SDK-04/06 must consume those semantics with the actual SDK/profile; native flush/crash outcomes remain storage-owner work |
| Source archive and notices match local pins | Hash identity and notice inclusion checked | UL-016 source trust and complete compiler acquisition/rebuild closure remain separate; no exception or authenticity approval granted |

The [payload-layout witness](evidence/sdk-layout-2026-09-07/README.md) now stages
231 SDK files plus COPYRIGHT in a fresh private root; all bytes/modes match and
the existing manifest tool agrees with an independent oracle. This closes only
the payload-layout portion of SDK-01. The complete profile/receipt-bearing stage
remains open, and SDK-02–08 remain **NOT RUN**. No package record or bundle exists. The [admission proposal](SDK-ADMISSION-PROPOSAL.md) now specifies a strict
cross-SDK profile, explicit commands and rejection oracles for owner review.
Actual import requires that representation to be agreed and implemented; consumer
build/native qualification requires the selected adapter/producer inputs above.
Keep this SDK work separate from running pkg-mgr itself on Aether.

## Current native release position

The kernel now records 111 command cases for combined runner/child roles and real
ENOENT/EACCES/EBUSY denied launches. Its next actions still include successful child
execution through the combined carrier, diagnostic-failure coverage and an immutable
producer handoff for independent userland adoption. This review reads owner reports;
it does not rerun or adopt those cases into pkg-mgr's existing 53-case transport pin.
Userland's UL-059/067 and native shell/filesystem-backed package execution remain open.
Sys-init reports BG-058 follow-ons queued. Read the exact captured owner identities
in the receipt before relying on this checkpoint; moving STATE files are not pins.

[Native package prerequisites](NATIVE-PACKAGE-PREREQUISITES.md) still govern the
bytecount import/verify/run/reboot path. The SDK material handoff does not provide
filesystem namespace, native package admission, durable publication or removal.

Applicable pinned Foundations scope: O-01/02 preserve owner and authority separation;
E-01–05 distinguish identified inputs, private operations and actual consumer
acceptance. Local [standards adoption](STANDARDS.md) and stricter
[recovery limits](IMPORT-RECOVERY.md) remain in force. No shared policy exception,
immutable-release edit or candidate pin adoption is introduced.

## Consumer response and first implementation — 2026-09-07

Userland supplied its [technical response](../../userland/docs/SDK-ADMISSION-RESPONSE.md)
and exact build/native receipt selections. The [profile validator](SDK-PROFILE.md)
now checks strict target syntax, the full target pin and both receipt hashes, with
synthetic preservation controls. This clears the earlier receipt-selection wait
for scoped implementation. Historical build-host fields are still incomplete;
real target construction must not substitute current uname observations.

SDK transport integration and full package/consumer gates remain open. The
validator does not establish manifest binding, package publication or native ABI
acceptance. No package-stage result above is promoted by the consumer response.

## Synthetic transport implemented — 2026-09-07

[SDK transport](SDK-TRANSPORT.md) now supplies explicit export/import/recovery
branches with both profile receipts manifest-bound. Synthetic record/mode equality,
independent-pin rejection, interruption recovery and failed result delivery are
covered. This advances scoped implementation; the actual 231-file SDK package
remains unqualified until historical target provenance and exact target bytes
are settled. SDK-01–08 real-package gates are not closed by these fixtures.

## Exact target candidate prepared — 2026-09-07

[Target candidate and provenance decision](evidence/sdk-target-candidate-2026-09-07/README.md)
provides canonical bytes and a 235-file unregistered payload with both selected
receipts. It proposes literal unrecorded host fields because the original
observations are absent; compiler_target is substantiated from the captured build.
Profile/hash/manifest checks pass, but userland must review the explicit missing
provenance representation before real-package transport acceptance. No current
uname value, new host build, package registration or native qualification was used.

## Accepted target and real transport — 2026-09-07

Userland accepted the exact candidate and its unrecorded historical host fields
for private data transport. The [real package handoff](SDK-REAL-HANDOFF.md) now
provides source/imported/recovery roots, descriptor and record identities, 235-file
equality, six denials and killed-stage recovery evidence. This supersedes the
receipt/target-review wait above. Imported compilation, static rebuild tracking
and native consumer gates remain with userland; no release acceptance is inferred.
