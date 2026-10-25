# 002: select the native musl transport experiment

Date: 2026-09-05. Status: accepted experiment direction by the user following the
musl audit. This does not accept an Aether kernel ABI or assign sibling work.

Proceed with source-rebuilt musl using a narrow native transport adapter that
initially retains musl's internal Linux-shaped arguments and errors. Establish
an unmodified Clang/musl Linux reference first, then compare behavior and patch
surface. Cover direct assembly entry paths as well as C syscall wrappers.

The security boundary remains capability-enforcing native services. The adapter
cannot turn its own privileges into ambient authority for callers. Keeping Linux
conventions inside the adapter is not a promise to run arbitrary Linux binaries.

UL-003 owns the still-open startup/transport contracts; UL-014 provides reference
evidence; UL-015 implements and tests the adapter after those contracts exist.
Revisit the approach if measured patch burden or semantic compromises outweigh
its benefits. Musl remains conditional on target validation for the base release.
