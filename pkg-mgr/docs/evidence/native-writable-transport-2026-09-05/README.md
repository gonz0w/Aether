# UL-040 package transport witness — 2026-09-05

Eight QEMU boots pass: four independently accepted writable cases and four fresh
read-only regression cases from the same userland-owned kernel capture. Host is
arm64 macOS; target is Aether x86-64. No sibling implementation or standard pin
changed. [Transport contract](../../NATIVE-LAUNCH-TRANSPORT.md).

| Run | Profile | External producer/tool evidence SHA-256 |
| --- | --- | --- |
| writable | files-writable | fdea2047d5931c7472b0fae9bae2df67d5527eeb234d47710a4100383a6e6ad5 |
| read-only | files | 3f2fd448f6a159f91c2d71f2ebf9ead09e2e0192f27b81cfe647b5db6ac32889 |

Original evidence paths are beneath
`/Users/cam/DEV/Aether-userland/docs/evidence/native-writable-userland-2026-09-05/`,
with each run's `evidence.json`. Normalized producer/tool copies here retain data;
the external pins apply to the original bytes. Source snapshots here identify
this package-side implementation; results record its whole helper closure.

Retained private roots:

- `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul040-writable-2026-09-05`
- `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul040-read-only-2026-09-05`

These retain large images, copied dependencies/tools, logs and payload bundles.
Small results, commands, receipts and serial logs are copied here and hash-checked.
Positive cases require the exact file-service pass marker and three reclaims;
negatives require their specific client status, supervisor 611 and profile panic.
See each run's result and serial files; a timeout is not an accepted rejection.

Reproduce using `python3 tests/native-launch-integration.py` with the table's
`--profile`, `--producer-kind userland-files`, original `--evidence` and
`--tools-evidence`, both external pins and a fresh `--root`. Matching `--aether`
paths are `/Users/cam/DEV/Aether-userland/build/native-writable-userland-gdomcoga/Aether`
and `/Users/cam/DEV/Aether-userland/build/native-files-userland-buw2ocw4/Aether`.

Four additional input controls reject before output creation: false writable mode,
integer 1 instead of boolean true, missing service cfg, and incomplete accepted
case set. Ordinary fixtures check mode omissions/unknown values/relabeling too.

This is inert artifact transport plus bounded volatile service execution. It is
not persistent installation, POSIX descriptor offsets, automatic retry, service
activation, signer authentication or native pkg-mgr execution.

`macos-fixtures.log` records all three pinned standards checks and all sixteen
ordinary package fixture scripts passing after this change.
