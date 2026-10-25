# Linux development environment

Decision 0151 / BG-054. This is a developer container, not an Aether runtime or
an installed distribution package. Release pins and native inputs are unchanged.

Rust 1.98.0 compiler, rustfmt and Clippy are required. Linux executable identities
are in `static-tools.json`; macOS entries remain separate. Setup downloaded the
Rust release manifest and components from static.rust-lang.org, verified published
SHA-256 checksums and installed offline into private `out/linux-rust-provision/tools`.
The compiler also needs a linker and libc development files. A separate image
adds Debian gcc, libc6-dev and binutils; exact installed versions and image identity
are retained in the decision's evidence. No check command installs dependencies.

## Reuse the local environment

Working artifacts are under `out/linux-rust-provision/`. They are not guaranteed
by a source checkout: if absent, restore verified artifacts or perform a newly
recorded dependency setup. Do not silently select a newer Rust version or change
pins to match whatever is installed. Upstream component licenses remain upstream.

The provisioned OCI archive is `image-second/image.oci`; its SHA-256 is
`b37ac81c10aff65615ceab2aef76b40d5abcae8246a227d74525921e979b8688`.
The saved image ID is
`fd26f551a6fc1f577f37707b4ac872bcea5e59b7b95ae20f5f550c7eca323c02`.
Check the archive digest before loading it. Loading it does not fetch packages.
Keep Podman startup, image loading and execution in one live command session in
this automation environment: separate sessions lost VM/image state during the
recorded attempts. That observation is not a general Podman failure diagnosis.

Qualification commands are retained verbatim in the evidence. Use the saved image
ID, `--pull=never`, `--network=none`, read-only source and tool mounts, dropped
capabilities, no privilege escalation, two CPUs, 1 GiB RAM, 128 PIDs and a private
512 MiB tmpfs. Set `RUSTUP_HOME=/tools/rustup`, `CARGO_HOME=/tools/cargo` and include
`/tools/cargo/bin` in the container PATH. Mount the private tools directory at
`/tools:ro`. Provide private writable mounts for `/results` and `/work/out`;
sample-receipt tests write artifacts below `/work/out/sample-receipts`.

Copy all required source inputs, including `.planning` and `.githooks`, into the
private snapshot. Run `python3 scripts/check-all.py --output-root /results` from
`/work`. Keep sources unchanged for the run and inspect every gate and the final
source-identity result. Retain errors, timeouts, missing tools and skipped cases;
separate component diagnostics do not qualify the aggregate. Clean up the named
container on success or failure. Do not add a scheduler as part of local reuse.

## Scope

A Linux pass applies to its exact image, toolchain and source snapshot. It does
not qualify BSD/illumos, PID 1, native Aether, physical hardware or a release.
Independent technical/reader review and hosted CI remain separate work.

## Reload witness

Decision 0152 loaded the checksum-verified OCI archive into a fresh Podman session,
verified the exact Linux arm64 image ID and ran all eight EHT-01 seeds offline.
All 432 executions passed with no skips; plan, corpus, implementation and actual
orders match the prior campaign. Rustc, cargo, rustfmt and Clippy versions/hashes
match before and after. This witnesses reload and EHT-01 reuse; the full ten-gate
Linux witness remains decision 0151.

[Reload evidence](evidence/linux-offline-reload-2026-09-07/README.md) retains commands,
raw logs and identity checks. No further local test repetition is required solely
to stand in for missing independent review or an additional OS environment.
