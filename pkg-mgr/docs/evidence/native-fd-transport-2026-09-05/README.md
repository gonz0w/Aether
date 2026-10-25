# UL-041 package consumer evidence — 2026-09-05

Twelve QEMU boot outcomes pass: four descriptor cases, four writable regressions
and four read-only regressions. Host: arm64 macOS. Target: Aether x86-64.
The package witness harness changed; package runtime/receipt formats, sibling
implementations and shared standard pins did not.

| Run | Profile / producer kind | Original evidence SHA-256 |
| --- | --- | --- |
| descriptors | files-writable / userland-fds | 0ef3d55c078b7dd5895d785680e8e89edd0266b4c581fe10086814265177b916 |
| writable | files-writable / userland-files | 2fc11109d39cc1c6a740c2c67a117b04d52027afaed53e594b0c09f587cb58cc |
| read-only | files / userland-files | aa6f55ea1af3d912bf05e9e46a01e2114af0fbba665b13fea35e8f3a0691b5f5 |

Original evidence resides at
`/Users/cam/DEV/Aether-userland/docs/evidence/native-fd-userland-2026-09-05/RUN/evidence.json`.
Producer and tool evidence use that same file/pin for each run. Normalized copies
here preserve its data; external pins refer to original sibling bytes.

Retained roots use `/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-ul041-RUN-2026-09-05`,
substituting the run column. They retain large images, copied tools/dependencies
and payloads. Each result identifies package helper hashes and input pins;
commands, normalized producer/tool evidence, receipts and serial logs are copied
here. All copied receipt/serial hashes and package input closures were verified.
The `sources/` copies identify this harness and unchanged transport implementation.

Reproduce with `python3 tests/native-launch-integration.py`, the table's profile
and producer kind, the original evidence path as both `--evidence` and
`--tools-evidence`, their SHA-256 arguments and a new `--root`. Matching `--aether`
paths are under `/Users/cam/DEV/Aether-userland/build/`:

- descriptors: `native-fd-userland-in__e4vn/Aether`
- writable: `native-writable-userland-1c6yfef6/Aether`
- read-only: `native-files-userland-64rfwi97/Aether`

Five additional input mutations reject before output creation: missing descriptor
mode, integer 1 instead of true, omitted client define, incompatible read-only
profile and incomplete case set. Each test required its specific validation error.

Descriptor negatives require client 207/213/216 for frozen-offset/early-close/
leak-close respectively, supervisor 611 and the exact profile rejection panic.
The positive requires the file-service marker and supervisor 100/reclaimed 3.
Writable/read-only controls retain their original independent status details.

[Contract and limits](../../NATIVE-LAUNCH-TRANSPORT.md): bounded private descriptor
facade, not libc integration, native process inheritance or post-mutation recovery.
No service activation, persistent installation or authenticated release claim.

`macos-fixtures.log` records all three pinned standards checks and sixteen
ordinary package fixture scripts passing after the harness extension.
