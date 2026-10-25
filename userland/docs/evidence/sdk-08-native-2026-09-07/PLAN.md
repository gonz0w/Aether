# SDK-08 isolated producer snapshot and first native cases

Capture a source-only Aether/sys-init snapshot under build/ (no live-tree
execution, no docs/evidence tarballs, no zig-out). Pin file hashes. Pack the
selected startup.elf as AENATC01. Run pass and native-no-output denial with
cleanup. Do not treat the live sibling as the producer. Historical 2026-09-05
contract remains absent; this snapshot is a new reviewed identity.

Reuse pinned QEMU/firmware via copied .deps, process bounds, and existing
io_smoke/supervisor builders. No sibling writes. Retain failed attempts.
Independent review and full io matrix remain open.
