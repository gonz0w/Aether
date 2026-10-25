# Real SDK target candidate for consumer review

2026-09-07. Exact candidate bytes are in [target.kv](target.kv), SHA-256
1b9c2fedc9cebba0785c4f4ec5157abaf580e886eae3cb8f809375a70062ab8e.
Status: **prepared for review, not accepted for real-package transport**.
This responds to userland's
[provenance clarification](../../../../Aether-userland/docs/SDK-ADMISSION-RESPONSE.md).

## Proposed missing-provenance representation

The original selected build receipt substantiates compiler_target=x86_64-linux-musl
through its explicit field and captured config.mak invocation. All embedded record
content hashes were checked. It does not substantiate original build_os/build_arch;
later consumer tool observations and today's machine are not replacements.

This candidate uses the literal token unrecorded for both fields. This explicitly
revises the proposed provenance representation for this selected candidate: those
values mean the original observations are absent. They do not mean an OS named
unrecorded, a wildcard, portable compiler support, or permission to substitute
another profile. The caller still selects the SHA-256 of the entire exact target.
Any later recovered observation changes those bytes and requires a new pin/review.
The exact two selected receipt hashes and original receipt bytes are unchanged.

The current validator treats identity strings as bounded inert data; accepting the
syntax does not certify their truth. No parser change or global unknown-value
fallback was introduced. Consumer review must explicitly accept this missing
provenance for the bounded data-transport experiment or require substantiated fields
from a separately evidenced build. It must not silently treat the candidate as a
fully observed SDK build or production toolchain qualification. No Apple build or
historical installer reconstruction is requested or performed.

## Executed preparation

prepare.py is the one-off preparation source, not a supported recipe or packaging
command. It rechecks the 247-file owner material inventory and selected receipts,
creates a fresh private root and stages the full candidate payload:

- 231 original SDK headers/library/startup files in the reviewed isolated layout.
- Unchanged musl COPYRIGHT.
- sdk-target.kv plus exact selected sdk-build-receipt and sdk-native-profile.

All 235 output files match their source bytes and ordinary modes. The existing
manifest tool agrees with an independently assembled expected manifest; the
profile helper checks the exact candidate digest and receipt bindings. All listed
source files/receipts and an unrelated sentinel are unchanged after staging.
commands.json records successful helper invocations. result.json binds source
identities and locates the retained stage; payload.manifest and payload-modes.tsv
identify its complete file set. This preparation passed on its first attempt.

No state directory, package record, host.kv or export/import bundle exists. The
stage is an inert candidate and must not be presented as an accepted SDK package.
Full SDK-01 and SDK-02–08 remain open. No SDK compiler or native executable was run;
the 4557-source native evidence was not rerun or requalified by association.
The full runtime suite was not repeated for this candidate-data/documentation task;
existing helpers are unchanged. Documentation checks are retained in checks.json.

## Required consumer response

Review these exact target bytes and explicitly accept or reject the unrecorded
host fields for the first private SDK transport experiment. Confirm that the two
selected receipt digests remain the intended historical profile. If rejected,
identify the substantiated replacement observation/build rather than requesting
inference from current uname. After that response, pkg-mgr can assemble a fresh
registered package, export/import/recover it and return exact artifacts for the
userland imported-SDK build/native gates. No response or owner approval is inferred
from the validator passing. No message was sent and no sibling was edited.
