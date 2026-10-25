# SDK profile validator

Implemented 2026-09-07: the narrow, non-publishing identity check from the
[admission proposal](SDK-ADMISSION-PROPOSAL.md). Userland's
[response](../../userland/docs/SDK-ADMISSION-RESPONSE.md) permits scoped
implementation and selects exact receipt bytes. The later [target decision](../../userland/docs/SDK-TARGET-DECISION.md)
accepts literal unrecorded historical host fields for one exact private data
profile. This is explicitly absent provenance; do not use today's uname to fill it.

```sh
sh mk/sdk-profile.sh /absolute/target.kv EXPECTED-TARGET-SHA256 \
    /absolute/sdk-build-receipt /absolute/sdk-native-profile
```

EXPECTED-TARGET-SHA256 is SHA-256 of the **entire canonical target.kv**, selected
independently by the caller. It is not the native receipt digest. The eight-row
profile schema and 4096-byte ceiling are defined in the proposal. The helper
checks readable regular, non-link inputs; the size before parsing; exact ASCII
row order, keys, values and final LF; the full caller pin; and both receipt hashes.
It uses existing SHA-256 provider selection. Provider failures reject. Metadata is
inert: receipt content is not executed or interpreted as a native ABI.

Success returns 0 with no stdout. Invalid argument count/pin syntax returns 64;
validation failure returns 1 with an ASCII sdk-profile-error diagnostic on stderr.
The helper uses private TMPDIR scratch and cleans it on normal success/failure
and handled HUP/INT/TERM. Existing hash-provider diagnostics may also appear.
SIGKILL cleanup, hostile filesystem races and receipt-size resource bounds are
not established. Inputs and their parents must remain caller-controlled under a
single writer. The 4096-byte bound applies to the target, not receipt contents.

This helper does not check package manifest binding, descriptor integrity, profile
provenance truth, native capabilities, compiler usability or source authenticity.
It publishes no stage/record and changes no input. The [SDK transport](SDK-TRANSPORT.md) now adds manifest-bound profile equality
and complete record/blob/state validation before publication; invoking this helper alone is not package admission.

[Tests](../tests/sdk-profile.py) exercise 65 synthetic cases: grammar mutations,
identity limits, receipt substitution, independent pin selection, input type and
selected hash-provider failure. Successful self-consistent changed receipts require
an explicitly changed caller target pin; retaining the old pin rejects them.
Every case checks empty stdout, input preservation and cleaned private scratch.
The full development suite invokes these controls. They do not qualify the real
SDK package or execute a native consumer. Existing host-v2 helpers are unchanged.

Evidence and verified userland receipt selections are retained in
[the checkpoint](evidence/sdk-profile-validator-2026-09-07/README.md).
The helper is now integrated with explicit SDK export/import/recovery branches
and synthetic publication controls. Userland has since accepted exact target bytes with explicitly unrecorded
historical host fields for private data transfer. The [real handoff](SDK-REAL-HANDOFF.md)
records executed owner transport; native and compiler acceptance remain separate.
