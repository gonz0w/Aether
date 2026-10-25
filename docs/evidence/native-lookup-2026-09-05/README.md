# Executable lookup witness

2026-09-05. [Contract and command](../../NATIVE-LOOKUP.md).
Seven lookup cases, five ordinary launch cases, four channel cases, five writable
file-service cases and seven native-init cases pass in QEMU. Host tests, 44 Python
tests and three offline standards checks pass. Rust formatting, Python compilation
and help/error exit checks pass. Source pins were compared with the current files
before retaining reports, small binary artifacts, maps and serial logs here.

The kernel and build.zig hashes match the accepted native-init producer unchanged.
No new memory, legacy consumer or default SMP run was needed for this user-space
lookup/launch-fixture and shared runner change; their prior evidence remains
separate. No companion adoption, POSIX exec, file-backed loader or shell is claimed.
Large ISO/kernel outputs remain at the private paths in summary.json; strict-musl
and compiler/linker inputs remain explicit separately pinned dependencies.
