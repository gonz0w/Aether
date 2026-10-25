# Reproduction tool identity — 2026-09-06

Pass on the first fresh-cache reproduction attempt: 85 Python tests, kernel host
and standards/workflow checks, seven M4 target cases and one-core boot/pixel checks.
Five new host cases cover unchanged executables, changed bytes, same-byte symlink
retargeting, disappearance and PATH selection changes. All source/dependency
inventory checks also pass. Local QMP socket access was permitted for these tests.

The receipt records invocation path, resolved executable and SHA-256 for Zig,
Rust launcher, QEMU, xorriso and Python before version probing, checks each after
probing and again after builds. The actual selected Rust compiler is separately
recorded and rechecked through its sysroot. In this run rust resolves to rustup,
while the compiler is the 1.98.0 aarch64-apple-darwin rustc. No installed binaries,
consumer pins, ABI or dependency versions were changed.

These are before/after executable identity observations, not execution attestation,
provenance authentication, dynamic-library/sysroot closure or detection of a
transient replacement restored before the final check. This remains a local
working-tree rebuild with installed tools, not independent release reproduction.

`attempt.json` captures exact command, UTC interval and exit status. `results.json`
contains sources, boot dependencies, commands, tools and artifact identities;
`summary.json` binds that report and `sources.tar.gz`. Logs and artifacts under
2 MiB (except ISOs) are retained. Rebuildable ISO bytes are omitted; all original
output hashes and paths remain recorded. External tools and boot dependencies
are reused pinned/observed inputs, not included in the source archive. No fresh
native-C companion execution, physical hardware or release acceptance is claimed.
