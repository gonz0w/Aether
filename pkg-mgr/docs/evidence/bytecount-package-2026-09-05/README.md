# Bytecount host package evidence — 2026-09-05

`integration.log` records a passing opt-in shell/make/compiler lifecycle. The pinned
source rejects a same-size mutation before extraction. Parallel build, registration,
state verification, binary export/import, exact package-record/license comparison
and all eleven staged/imported output/status cases pass. These repeat the same
command cases at lifecycle boundaries; they are not separate feature counts.

`run.json` identifies invocation, source/helper/test pins and equal built/imported
binary hashes. Origin evidence identifies the verified userland preparation bundle.
Host/compiler identity is copied from the staged host.kv; this is a macOS host
binary, not native Aether. Build/tamper logs, record, source/manifest and binary
metadata are retained here; full payload and imported root remain under:
`/Users/cam/DEV/pkg-mgr/.pkg-mgr-live-bytecount.pOsKVn`.

No compiler or library was installed, no dependency fetched, no sibling changed
and no live prefix written. The unchanged command source and BSD license are
packaged together. Userland owns future source/native integration/base selection.
Exact output readback for a native command is not proven by host execution.
[Recipe and reproduction](../../BYTECOUNT-PACKAGE.md).

`macos-fixtures.log` records all three pinned standards checks and sixteen active
fixture tests passing. Standards pin validation is separate from runtime conformance.
