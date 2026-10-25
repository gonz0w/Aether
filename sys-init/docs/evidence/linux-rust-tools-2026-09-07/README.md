# Linux Rust tools and full qualification — 2026-09-07

Decision 0151 completes all ten Linux gates with real Rust tools and all ten macOS
regression gates. The same Rust 1.98.0 version is used on both; Linux executable
hashes are added without changing existing macOS entries or Aether release pins.
Native audit stdout matches both platforms and the prior witness; 24 native inputs
and the catalog remain fixed. No new native execution occurred.

provision/ retains official Rust 1.98.0 release metadata, checksums, download URLs,
installer/component identities, offline installation output, package setup logs,
Debian OS/package versions and image inspection. Rustup 1.29.1 and five component
archives were checked against published SHA-256 values before installation.
Downloads used official HTTPS; checksums establish correspondence, not independent
signer authentication. Dependency network setup was separate from network-disabled
installation and qualification. The original cached image was not modified.

The first linker image was lost across VM sessions: its qualification exited 125
before any gate. The second setup saved an OCI archive and kept provisioning and
qualification in one session. Both attempts are retained. Container logs, exact
commands, named cleanup and driver scripts are included. Scripts reference their
original temporary path locators; use LINUX-DEVELOPMENT.md for the reuse procedure.

linux/ and macos/ retain the passing reports and raw logs; sample-output/ retains
Rust test sources, binaries and receipts. review.json lists final documentation
identity differences after the Linux snapshot. Tool settings, tests and runtime
bytes match that snapshot; the documentation changes were checked on macOS.

Large component archives, installed tool homes and the 245 MB OCI image remain
working artifacts under out/linux-rust-provision; working-artifacts.json records
paths, sizes and digests rather than duplicating them here. Downloads' initial
paths precede relocation under mirror/dist. Archive config was checked against
the qualified image ID; a fresh reload was not separately exercised. If working
artifacts are removed, restore verified artifacts or make a new recorded setup.
This metadata bundle is not a standalone installation archive.

Host dependency licensing remains upstream. No sibling repository, host toolchain,
system helper, release pin, native behavior or scheduler was changed. Independent
technical/reader review, BSD/illumos and hosted CI remain separate requirements.
