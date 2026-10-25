# 0151 — Provision and qualify Linux Rust tools

BG-054/BG-056, 2026-09-07. Fetch official Rust 1.98.0 release metadata and
Linux arm64 rustc, rust-std, cargo, rustfmt and Clippy archives. Pin rustup 1.29.1
from its release metadata. Verify published SHA-256 digests before execution.
Record exact URLs, archive and installed tool identities; checksums establish
byte correspondence, not independent signer authentication.

Keep dependency setup separate: fetch on host into private out storage, install
inside the pinned cached Linux image with networking disabled and tool homes in
private writable storage. Do not install host tools or alter sibling repositories.
Preserve existing macOS tool entries and all Aether release pins. Add Linux entries
only after actual rustfmt/Clippy versions and behavior are verified. Run the full
Linux suite with read-only source/private writable out and normal gate bounds,
then full macOS checks. Retain failures and do not waive missing tests or tooling.
No native changes, target execution, hosted scheduling or independent sign-off.

Offline Rust installation succeeded but the base image has no C linker. Dependency
setup additionally installs gcc, libc6-dev and binutils into a separate local image
using Debian package repositories. Record package versions, OS and new image ID;
network is limited to setup, and qualification uses --network=none/--pull=never.
The original image remains unchanged; private Rust homes mount read-only for tests.

## Result

Decision 0151 provisions verified Linux Rust 1.98.0 and a separate linker image.
All ten Linux gates pass in `run-bame9hi5`; all ten macOS gates pass in
`run-t_uefwle`. Added Linux rustfmt/Clippy hashes preserve existing macOS entries
and all Aether release pins. Native inputs and audit stdout remain identical.
The OCI image is saved for offline reload; dependency setup, failed missing-image
attempt and exact package/tool identities are retained. Next: independent review
and BSD/illumos qualification; hosted CI still needs a selected provider/remote.
Linux setup: `docs/LINUX-DEVELOPMENT.md`.
Evidence: `docs/evidence/linux-rust-tools-2026-09-07/`.

The first local linker image disappeared between VM sessions; its attempted
qualification exited 125 before testing. A second setup saved the OCI archive and
qualified within the same session. Both setup attempts remain recorded. The image
archive config matches the qualified image ID; reloading it was not separately
executed. Final process/inventory edits follow Linux checks; runtime, test and
tool-setting bytes match the Linux snapshot and macOS validation.
