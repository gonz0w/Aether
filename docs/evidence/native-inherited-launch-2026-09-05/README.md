# Parent-requested inherited launch evidence

2026-09-05. [Contract and reproduction](../../NATIVE-INHERITED-LAUNCH.md).
Seven new cases pass: normal and parent-first lifetime, native admission rejection
with retry, partial channel-reservation failure with retry, leaked partial
reservation, leaked failed-admission endpoints and incorrect child-rights policy
acceptance. All four positives complete two rounds and six reclaims. The three
negative cases require exact parent/broker failures before any reclaim.

Fresh regressions pass: six shared-file bootstrap, six connections, six program,
six coexist and five writable-file cases (36 native outcomes including the new
seven). Host tests, 56 Python tests and all three offline standards checks pass.
Rust formatting, Python compilation, CLI help and conflicting-profile exit 64 pass.
No kernel source or native ABI changed; memory/default SMP were not rerun.

`summary.json` pins individual source files, reports, tools and the producer source
archive. Captured native source hashes matched working files before retention.
Small binaries, maps, envelopes and logs are retained; larger ISO/kernel outputs
remain at private report paths. Explicit strict-musl/compiler dependencies remain
separate pinned inputs. The earlier five-case draft was superseded by this final
seven-case capture with partial-reservation coverage.

This is Aether producer evidence for one read-only inherited reference requested
by the parent. It does not establish independent userland adoption, multiple-entry
inheritance, libc FD integration, waitpid, fork/exec, unknown-result recovery,
sys-init policy composition, native shell or persistence. Shared standards,
companion sources and immutable pins remain unchanged.
