# Command I/O integration candidate — 2026-09-05

[Contract and reproduction](../../NATIVE-COMMAND-IO.md). This is an Aether-local
producer/integration candidate using real public musl I/O, not independent
userland adoption or completion of the public CR-01 runner.

Nine final native command cases pass: nonempty, empty, rejected native launch,
partial reservation, one-byte writes, full output, wrong startup, wrong status
and skipped storage. Success scenarios require two exact terminal sequences and
six reclaims. The full-output case correctly reports command exit 82. Negative
controls require exact ordered command/runner/broker context and designated panic.
Link maps require musl read/write/close; all built ELFs have no undefined symbols
or Linux syscall instructions. Command code computes its output from real reads.

Forty-six native regressions pass: file-I/O 5, inherited-launch 9, shared-files 6,
connections 6, program 6, coexist 6, writable-files 5 and read-only files 3.
`zig build test` passes kernel/host checks, 56 Python tests and three offline
standards checks. Python compilation, scoped Rust/C formatting, CLI help and
mutually exclusive profile rejection (exit 64) were also checked. Kernel hashes
match the previous file-I/O source snapshot; default boot/SMP/memory suites were
not rerun. No sibling files or immutable consumer pins were changed.

`summary.json` pins reports, tools and 178 source files in
`producer-sources.tar.gz`. Each suite directory retains results, ELF helpers,
raw brokers, envelopes, maps, build and serial logs. Large ISO files remain at
the recorded local suite paths; their hashes are in the reports. Final command
output is `zig-out/command-runner-suite-jlh46tgj`. The base broker is 6936 bytes,
within the existing 8192-byte limit. Sources in the final archive match every
accepted suite's source inventory.

`initial/` retains exploratory build/run logs and available reports/serial logs.
These include corrected Rust keyword, missing TLS, oversized native transfer,
environment-slot and exhausted retry-generation mistakes, plus earlier passing
iterations before stronger inspection/oracles. They are not acceptance results
and their earlier source snapshots are not represented by the final archive.

The conformance runner still exits 29 per the harness convention. A public CLI,
independent consumer, abnormal-child/unknown-delivery coverage and packaged
reconstruction remain separate CR-01 work. No shell, fork/exec, persistence,
shared owner approval, release or full system conformance is claimed.
