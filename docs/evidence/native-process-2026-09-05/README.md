# Connection-bound launch broker witness

2026-09-05. [Protocol, invocation and acceptance limits](../../NATIVE-PROCESS.md).
Six process cases pass: positive two child generations, incorrect inheritance
acceptance, widened caller namespace, repeated collection, partial request and
requester exit with an owned child. Negative cases require exact requester exit
codes and broker rejection after the specified reclaim count. Positive completion
requires both worker outcomes, requester exit 29 and three reclaims.

Five ordinary launch, seven lookup, four channel, five writable-file and seven
native-init regressions pass. Host checks, 44 Python tests and three offline
standards checks pass. Rust formatting, Python compilation, help and incompatible
mode rejection checks pass. Source and serial hashes were compared with the
completed reports before retention. Reports retain explicit SDK/tool pins, commands,
small input binaries, maps and serial logs; large ISO/kernel outputs remain in
the private paths in summary.json. Source copies cover the new broker/requester,
lookup module and runner. The producer worker libc remains separately pinned.

No kernel or build.zig changes: their hashes match the accepted native-init
producer. No additional memory, legacy userland consumer or default SMP target
runs were needed for this fixture/runner change. Their earlier evidence remains
separate. No companion file, shared standard, immutable release or consumer pin
changed. This is Aether conformance evidence, not independent userland adoption.

The original non-LTO broker exceeded the strict linker bound; fat LTO and one
codegen unit yield 2888 bytes without changing the one-page/no-writable-statics
limit. Failed builds are not target acceptance. Empty inheritance is enforced;
shared file descriptors, production process service placement, fork/in-place exec,
POSIX waiting, file-service coexistence and native shell support remain open.
