# CLI binary lifecycle acceptance

2026-09-07 UTC. Test-only extension of the real binary helper fixture. No runtime,
artifact format, release pin or sibling change. Export base/app through the CLI
with exact pinned exported receipts and empty stderr. Ordinary imports and their
existing invalid-inner/duplicate checks use the CLI; successful imports require
exact imported rows and empty stderr.

Keep helper-level process interruption injection unchanged. Copy its retained app
stage into another private root and recover through the CLI twice. Each attempt
must emit exactly recovered/app with empty stderr, preserve base record and world,
match the app record and verify all staged payload bytes/modes. The two complete
file snapshots must match. Existing original-root recovery negatives and interrupted
record-publication retry checks continue; normal recovery goes through the CLI.

Forbidden outcomes: incorrect receipts, lost old pending input, changed unrelated
records/world, invalid payload adoption or non-idempotent repeated recovery. File
snapshots bind paths/hashes/modes, not directory metadata or persistence. Synthetic
host packages and injected process death cannot qualify native installation or
power-loss durability. No human renderer or repository authenticity claim.

Selected checks: standards, development inventory, changed-shell lint, coverage
controls and fresh full sh tests/check.sh under its 600-second watchdog. Preserve
all attempts and exact dirty executable/fixture inputs in this evidence directory.

Result: the CLI lifecycle marker and full-suite completion appeared exactly once;
the suite passed in 220.4 seconds. Executable/fixture entry
names, sizes, hashes and modes remained unchanged from inputs.json. Existing
interrupted recovery and retained replacement cases also completed. This is a
private host witness with real package helpers, not native release acceptance.
