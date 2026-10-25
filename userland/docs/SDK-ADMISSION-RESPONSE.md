# Userland response to cross-SDK admission — UL-005

2026-09-07. Technical consumer review of pkg-mgr's
[admission proposal](../../pkg-mgr/docs/SDK-ADMISSION-PROPOSAL.md), at the exact
hash recorded in [selection.json](evidence/sdk-admission-response-2026-09-07/selection.json).
The proposed separation of inert SDK data from executable host-v2 admission is
suitable for this bounded experiment. This is this task's technical assessment;
maintainer sign-off, implementation tests and native acceptance remain separate.

## Verified owner work

Independently compared the owner's private stage against userland's original SDK
inventory: all 231 SDK files and musl COPYRIGHT have the expected paths, hashes
and ordinary 0644 modes, with no extra payload files, links or special entries.
This corroborates the payload-layout part of SDK-01. No profile-bearing record or
SDK export/import bundle has been delivered yet. Existing evidence is not renamed
or promoted to full SDK-01 acceptance.

## Selected receipt bytes

Use the two exact files beside selection.json. Recheck the selected SHA-256 values
before copying; these are local reviewed inputs, not source-authenticity evidence.

- `sdk-build-receipt`: composite of the original SDK build receipt, command argv,
  configure log, generated config.mak and patch records, each with its source hash.
  Later consumer tool observations are separately labelled. Original complete
  host environment and dependency closure are not reconstructed or invented.
- `sdk-native-profile`: byte-identical to the existing UL-044 native-stdio-files
  libc evidence receipt. It binds the same SDK build receipt and 231 SDK inputs,
  exact captured kernel source inventory, producer/consumer artifact hashes,
  cases and command options. All 4557 captured kernel source hashes were verified
  again. This selects that historical bounded native-memory/file profile, not
  the latest kernel checkout, public command runner or a new ABI.

The native receipt is existing userland consumption evidence identifying the
kernel-owned profile. It is not a new normative profile authored by userland or
a kernel-owner signature. Its captured kernel contract remains authoritative.
Selection does not rerun its native cases or claim every libc entry is supported.
I/O/memory/stdio adapter objects remain separate SDK-05/08 consumer inputs; they
are not added to the SDK package by selecting this receipt.

## Representation review and implementation requirements

The following details resolve the consumer interpretation of the proposed design:

1. EXPECTED-PROFILE-SHA256 must mean SHA-256 of the complete canonical `target.kv`
   bytes. It must **not** mean only `native_profile_sha256`. Otherwise changing
   the build receipt and target while retaining the native receipt could evade
   the intended independently selected profile binding. Keep these two digests
   distinctly named in tests and documentation. The descriptor pin is separate.
2. Receipt selection above supplies inputs for target construction, not a final
   caller target pin. The owner must record the actual build-host provenance used
   in build_os/build_arch and then return exact canonical target bytes for review.
   The original receipt lacks a complete host observation; do not fill its fields
   from today's uname or infer them solely from a compiler executable path. If the
   design needs a historical observation that cannot be substantiated, explicitly
   revise that provenance representation or obtain a fresh qualified build.
3. Manifest binding, exact target equality and both receipt hashes must be checked
   on export, import and recovery before publication. Keep wrong-profile tests
   self-consistently rehashed so that they actually test the independent caller
   pin. Unsupported receipts/roles/versions must not fall back to host-v2.
4. A profile receipt is inert evidence. Matching its hash does not authorize
   execution, activate services or certify a importing host/toolchain. Preserve
   the selected package name, empty dependency-list scope and legacy host-v2
   rejection/exit contracts. SDK-05 compiler isolation and SDK-07 static consumer
   rebuild evidence are still required.

No incompatible requirement was found in the proposed regular-file layout,
strict grammar, independent pins, recovery or explicit branch design, subject to
these clarifications. The stated output-delivery error case correctly separates
committed state from a successful caller receipt and needs its planned test.

## Next owner action

pkg-mgr can continue bounded parser/transport implementation and synthetic
controls under its own workflow using these selected receipts and interpretation.
Resolve and return the exact target provenance/bytes before claiming the real
package positive case. No additional userland package-state implementation is
needed. Return SDK-01–04/06 package records, bundles, root locations, all failure
attempts and exact source/tool identities. Userland then verifies those artifacts
and prepares the imported-SDK consumer for SDK-05/07/08.

UL-005 is active for this coordination response; full package and native gates
remain incomplete. No sibling file was changed, message sent, service started or
release pin updated by this review. The prepared files are local handoff inputs.
