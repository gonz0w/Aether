# Read-only descriptor core — 2026-10-21

UL-007/081/082 now has a private owner-local file-description core using the actual
unchanged AF07 Owner policy. Aether has consumed the corrected ABI29 v2 client;
the matching sys-init dispatcher remains external work. This local step does not
change that client, service wire, engine, native mechanism or old seal.

The core keeps FD flags separate from retained file descriptions. Duplicates
share offsets and final-close lifetime; separate opens have independent offsets.
File FDs3–15 reserve console0–2, fixed13 bindings/descriptions fit the existing
root-plus16-handle budget. Capacity is checked before lookup. Root LOOKUP|READ
attenuates to file READ; PID/UID/FD/path labels grant no native authority.

Actual Python3.10.21 and3.14.7 each pass12 real-Owner host tests and eight compiling
semantic omissions, strict Rust1.98.0 warnings/unsafe denial, default Clippy and
rustfmt. The native no_std **generic library** builds identically on both runs;
this is not a monomorphized/linked engine or executed native descriptor runtime.
Host tests use instrumented synthetic storage, not OpenZFS, AF07 channel traffic,
QEMU or a shell. No Rust host sanitizer is claimed; explicit misuse/failure controls
and the safe implementation are scoped evidence, not whole-runtime safety proof.

Tests cover independent/shared offsets, seek/EOF/tail clearing, final handle
close/nonreused identity, capacity/no lookup effect, invalid names, repeated
directory rejection without handle leaks, per-FD close-on-exec, signed bounds,
bad descriptors, known backend errno, bad completion/retirement, stale context,
read-only denial and sole backend cleanup. All eight omissions compile and fail
at test assertions: lost offset advance, early shared-handle close, missing error
clearing/retirement, closing unflagged exec FDs, wrong flag update, live FD overwrite
and widened read range. First Clippy attempt rejected an equivalent capacity
expression; corrected without suppression. An intermediate passing run predates
the added omissions/comment clarification; final minimum/current runs include all.

[Contract](../../proposals/FS-DESCRIPTORS.md) and [review](review.md) name the
dedicated-context restriction and failure/commit boundaries. Reads are capped4096
and requested ranges must fit signed64 before provider effects. There is no write,
directory traversal, fork replication, C/libc adapter, native loader or credential
translation. `commit_exec_close` is only a local destructive step **after confirmed
admission**; it is not failed-exec rollback or ambiguous-outcome recovery.
Local detach/Drop is not endpoint closure, SPA export, native reclaim or halt.

The separately sealed source-only input and dependency reference are in
summary.json. Exact dependency77 members, source/tool/standard-library pins,
compiler flags/env, output/status/cleanup and every attempt are retained through
the compact archives. Historical binaries/evidence are preserved. The native
generic artifact hash is comparison evidence, not a delivered executable.

Reproduce from this checkout with pinned tool/dependency bytes using
`python3 -B experiments/filesystem-service/check-descriptors.py`. It creates
an owned build root; each compile has60s and test30s bounds/16MiB streams.
No native campaign, sibling mutation/message or release/SDK/standards repin.
Next integrate authenticated process FD dispatch, AF07 transport and actual
filesystem-loaded exec without duplicating the live Owner/SPA context. Native
file/command/error/cleanup/fresh-boot witnesses, peak resource fit, independent
reviews, packages/Zsh/TTY and full M3/R1 remain open.

Final quality/pin/inventory, minimum/current Python syntax and whitespace checks
pass. The source-only five-member candidate seal is
`f93c01950d710737158774b51d48f01fff2c06bb7bf97a4114d7bbb689f616e2`.
Seven exact new owned roots were compacted/read back before disposing59434344
logical bytes;743873 compact archive bytes remain. Physical reclamation was not
measured. Actual final tool-manifest/Rust-library pins are retained in the final
current/minimum receipts; all prior attempt versions remain available.
