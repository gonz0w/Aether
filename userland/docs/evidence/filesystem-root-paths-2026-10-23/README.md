# Canonical root file paths — 2026-10-23

UL-007/081/082; [pre-code contract/review](../../proposals/FS-ROOT-PATHS.md).
Run from userland: `python3 -B experiments/filesystem-service/check-paths.py`.
[Results](results.json) preserve exact tool/dependency/source hashes, final child
commands, all four attempts and short failures. All generated checker trees were
removed after complete child cleanup; no binary/source archive is retained.

Final pass:22 selected client/13 default client/9 selected descriptor/8 default
descriptor tests, five compiling semantic controls, strict Rustfmt/Clippy/unsafe
denial and host/freestanding builds. Client and Descriptors layouts remain680/8
and1128/8. Actual sealed Rust AF07 service tests use synthetic host storage; no
native path, process inheritance, grant or whole-owner fit qualification follows.
The255-byte deep host walk does not expand the native9-mutation/96-request workload.

Attempt1 fails on a missing test vec macro import. Attempt2 rejects a semantic
control with abort(-6), rather than expected101: an assertion held a test mutex,
poisoning it during unwind and causing a destructor panic. Snapshot test observations
before assertions; production path code was unchanged. Attempts3/4 pass;4 adds the
actual descriptor consumer. Failed attempts remain failed, never replaced by passes.
Python3.14.7 executed; minimum3.10 runner was unavailable and remains missing coverage.
Independent reader and native acceptance remain pending.

[Fresh default inputs](default-inputs.json) reseal the current source tree with
fs_paths unselected:39376/49152 code,7504/8192 resident and8000/8184 conservative
stack. No guest ran. Existing sealed deliveries/released pins stay exact.

Maintainer policy: interactive shell has a writable home; system changes require
an explicit installer/admin operation. This slice remains read-only and cannot
turn path text or process UID into writable authority. Separate trusted home
provisioning, CWD, FILE/libc binding, writes and stable executable admission remain.
