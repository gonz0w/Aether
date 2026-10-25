# Boot-owned backing reservation — 2026-10-04

[Before-code contract](contract.md) / [private reference](../../NATIVE-BACKING.md).
The isolated BSP experiment validates the complete Limine memory map before
selecting one usable, aligned64MiB region above low1MiB/below4GiB. Reserved/unknown
ranges are excluded; overlap/wrap/zero/count/insufficient-space/alias errors reject
before writes. It uses only the initial canonical HHDM, dirties/clears the owned
region and verifies every byte through volatile word reads. The BSP retains it
until VM teardown. No user/AP/device/allocator or service binding is admitted.
Ordinary/native fixtures and their quotas remain unchanged. All lab modes are
excluded from release-designated artifacts.

First pure-model attempt passes two suites and exposes noncanonical HHDM-base
acceptance in the third. Failed source/log/executable remain. Corrected base
validation passes all three suites before runtime integration. First target link
fails because unused protection assembly references an eliminated handler; exact
build source/log/object remain. Second target attempt excludes that assembly only
in the isolated lab and passes all four modes: real64MiB reservation; overlapping
map rejection; final-byte corruption; omitted clear. Negative modes produce the
exact expected panic and no reservation success marker. A private removed-map-
validator model fails the named actual Zig test, proving that oracle is sensitive.

Full137 Python tests plus Zig/Rust/three new planner suites/pins/workflow pass.
Fresh five origin, five lifetime and four native entropy cases pass on the new boot
path. Hardware entropy11/block7/M4seven pass. Prior112 pair/pthread lifecycle cases
remain bound to byte-identical native context/ABI/memory/adapter bodies in the
sealed origin packet; this stage changes only isolated boot selection, not those
mechanisms. Missing reader/production SDK/admission acceptance remains coverage.
No full-engine, filesystem or R1 readiness claim. No sibling/pin modification.

Use pinned offline tools: `python3 docs/evidence/native-backing-plan-2026-10-04/native.py`,
then `zig build test`. Supporting SDK/regression recipes select owned copies of
sealed inputs; no mutable sibling bytes are followed. Clang/LLD21.1.8, Rust1.98.0,
Zig0.16.0 and QEMU11.1.1/qemu64/q35/TCG tools/argv/source/time/artifact identities
are retained. Builds180seconds, VM30seconds and owned teardown3seconds; force-kill
fails. Every new archive member reads back before only owned verified duplicate
cleanup. Original planner/probe/recipes are BSD-2-Clause; reused SDK/source notices
retain upstream terms. New fixed ASCII marker follows the scoped Experience exception.

64MiB is an experiment reservation ceiling, not measured engine admission, heap/
stack high-water or a physical-hardware/IOMMU guarantee. Native roots do not yet
map this backing. Next constant-size metadata plans off the16KiB exception stack,
then one explicit native owner with reviewed physical/RW-NX/immutable alias/table/
cleanup geometry. Do not multiply larger static arrays across every State. Actual
live-worker capacity, native allocation/stack observations, identity/configuration,
feature closure and complete startup/fini/restart still precede persistent R1 work.
