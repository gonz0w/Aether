# Parent-owned terminal collection evidence

2026-09-05. [Contract and reproduction](../../NATIVE-INHERITED-LAUNCH.md).
Nine inherited-launch cases pass. The previous admission/rollback/lifetime cases
now include foreign/stale receipt rejection and post-file-close process-result
probes. Two new mutations alter the observed exit detail or return success twice;
the parent rejects at 249/250 and the broker at 970/reclaimed 0 respectively.

Fresh regressions pass: six shared-file bootstrap, six connections, six program,
six coexist and five writable-file cases (38 target outcomes including the new
nine). Host tests, 56 Python tests and all three offline standards checks pass.
Rust formatting and Python compilation pass. Kernel and ABI are unchanged;
memory/default SMP were not rerun.

`summary.json` pins reports, tools, individual sources and the producer archive.
All captured target source hashes matched the final working files. Small binaries,
envelopes, maps and logs are retained; large ISO/kernel outputs remain at report
paths. Explicit libc/compiler dependencies remain separately pinned inputs.
Intermediate runs preceding the final collection/file-lifetime separation are
not the acceptance capture; a source-changing regression run correctly rejected
its input drift and was rerun after edits finished.

This is Aether producer evidence for one-shot collection of the fixture child's
normal exit. It does not establish POSIX waitpid, arbitrary child outcomes,
exactly-once result delivery, lost-reply recovery, fork/exec, independent consumer
adoption, shell execution or persistent installation. No sibling sources or
immutable standards/consumer pins changed.
