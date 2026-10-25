# UL-063 CSR-01/02 tooling correction

Before public-runner behavior, replace direct-child subprocess timeouts in the
three command drivers with a local owned process-group helper. Record argv, cwd,
explicit environment, executable identity, start failure, timeout, exit and group
cleanup before enforcing success. Fixed private stdout/stderr files retain partial
logs; cap each at 16 MiB via child RLIMIT_FSIZE. Parent exits with descendants still
alive must not pass. Kill remaining owned group and reap direct child within five
seconds; do not infer cleanup if it fails. No general daemon/detached-child support.

Use a clean environment and absolute preverified tool selections. Preserve test
case env overrides exactly (missing LC_ALL tests must remain missing). Retain
resolved tools/hashes and explicit host Python identity. Existing C source, C11,
protocols and exits unchanged. Test normal/nonzero, missing tool, timeout with a
live grandchild, early leader exit with descendant, and poisoned caller PATH/CC.
Rebuild native client ELFs and run 21 host/control cases. Native driver migration
requires its nine native runs before completed acceptance. Keep incomplete stages
explicit. Apply CP/CD/TD/TE and Foundations E; preserve historical receipts.

First native driver run exposed a rustup-provided dynamic-library search path
that direct pinned rustc does not supply. Retain linker SIGABRT and completed
process cleanup. Pin rust-lld and toolchain dylibs, then supply only that verified
toolchain lib directory explicitly. Native artifacts can exceed 16 MiB, so the
native driver declares a separate 512 MiB per-file ceiling; helper controls and
small client/host builds retain 16 MiB. No ambient DYLD variables are inherited.

Second attempt showed the Rust LLVM library path must not reach Zig (library
name collision). Scope that path to rustc commands only; keep Zig/QEMU and smoke
environments free of loader overrides. Retain the failed Zig version check.

Third attempt reached nested producer builds, which invoke rustc through PATH.
Provide a private hashed Python rustc wrapper that adds the pinned library path
only when executing Rust. Keep producer sources unchanged; other tools receive
no Rust loader override. Retain this failed build and descendant cleanup records.

Fourth native attempt reached image construction and rejected missing xorriso in
the private PATH. Pin the existing image tool explicitly; no fallback to ambient
PATH. Retain failed build; boot dependency verification remains producer-owned.
