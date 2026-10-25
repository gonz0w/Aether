# Native shared-file bootstrap evidence

2026-09-05. [Contract and reproduction](../../NATIVE-SHARED-FILES.md).
Six cases pass: child-first and parent-first lifetime orders, frozen position,
premature backend close, missing child write-denial guard and omitted final close.
Both positives run two fresh generations and require six reclaims. Negative
controls require exact worker/broker outcomes and ordered panic context.

Fresh compatibility regressions pass: six connections, six program, six coexist
and five writable-file cases (29 target cases including the new six). Host tests,
56 Python tests and all three offline standards checks pass; Rust formatting,
Python compilation and CLI help pass. Kernel sources and ABI remain unchanged;
memory and default SMP were not rerun for this user-space fixture change.

`summary.json` pins reports, tool/input identities, individual producer sources
and `producer-sources.tar.gz`. Each target report's sources matched the working
files before retention. Small ELF/envelope/raw binaries, maps and logs are saved;
large images/kernel binaries remain at the private paths in reports. Explicit
strict-musl/compiler dependencies remain separately pinned inputs.

An intermediate early-close control reached another cleanup failure because the
parent could close before child exit was observed. The final fixture explicitly
orders the parent's second read after observed child exit, reaching the intended
surviving-alias failure. An overlapping regression run rejected changed source
hashes during that correction; only the final unchanged-source runs are retained.

This is Aether producer evidence for fixed bootstrap aliases, not dynamic
inheritance, a parent-requested launch, fork/exec, libc interposition, native shell,
persistent files or independent userland adoption. Production service ownership,
unknown-effect recovery and sys-init composition remain separate. No sibling
source, shared standard or immutable pin changed.
