# Mawk static Linux-reference plan

UL-066 continuation, 2026-09-06. Reuse the pinned mawk source, unmodified musl SDK
and verified Toybox cross-compiler wrapper; no upstream patches. Explicit Linux
configure target and target-only libraries. Inspect ELF and configuration before
execution. Retain cross-configuration assumptions, commands, all attempts and
source/tool/SDK hashes. No real installation or network during build/test.

Run all three upstream check scripts in an owned offline container using an explicit
QEMU wrapper, then reuse the eleven package-script fixtures. Candidate cases are
Linux-emulated, not native Aether. Shell helpers are from the pinned image. Missing
tools, skipped/empty suites, timeouts or cleanup failures are not passing coverage.
Bound build phases to 240 seconds and each suite container to 180 seconds, with
512 MiB memory, 32 PIDs and private scratch. Preserve upstream license and fixtures.
Apply E/PX/CD/CP/TD/TE/DP; independent review and full security/source-authentication
review remain pending. tr/stty source/build comparison stays in UL-066.

Initial run found a real NaN-comparison failure: configure probes link symbols
isnan/isinf without math.h, but the pinned musl exposes them as macros. Verify
both interfaces with a target compile/link probe before setting their configure
cache answers; execute that probe under QEMU and require its negative/positive
classifications. Preserve the failing build and suite; do not alter upstream
expected outputs. Rerun all suites and consumer fixtures after this correction.
