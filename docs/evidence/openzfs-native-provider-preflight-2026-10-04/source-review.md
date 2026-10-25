# OpenZFS provider and time-helper review

Pinned original OpenZFS2.4.4 commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1.
Complete prior manifests/archives and every selected regular input reverify in
input-recheck.json. No historical symlink is followed. time-original.h is the
exact upstream libspl header; time-private.h retains its CDDL header. time.diff
shows only dependency includes and the four time helper bodies.

The original gethrtime discards clock_gettime failure and reads an uninitialized
timespec. gethrestime/gethrestime_sec/getlrtime similarly discard gettimeofday
failure. The corrected SDK reports errors honestly but these callers still ignore
them. Do not execute those original helper bodies in the unsupported profile.
The private copy binds gethrtime to the current bootstrap thread grant and returns
only checked virtual time. Denied queries and all unavailable wall-time helpers
terminate125. This is a caller correction, not a replacement production SDK clock.
Only the time-helper consumers are rebuilt here; the previously linked full engine
objects still contain their old inline bodies and must be rebuilt for an engine run.

Existing raw pair clock0x2800e reports10,000,000 virtual nanoseconds per delivered
BSP timer interrupt; it is boot-local/coarse, not calibrated elapsed time or UTC.
The explicit memory0x22000 result is current unallocated grant pages. The one-page
map/unmap observation is sequential, not a reservation under concurrent allocation.
Future-generation rejection is tested; actual retired-generation reuse is not.
The real wrappers have no cached authority/state. No kernel/runtime changes.

Actual upstream sys/simd.h compiles unchanged with the original supporting headers.
Both QEMU CPU views have SSE2 and no OSXSAVE; max actually advertises AVX in CPUID,
but upstream AVX/AVX2/AVX512f selectors reject it. No XGETBV executes without OSXSAVE.
This qualifies those selectors, not every dispatcher/manual tunable, cryptographic
algorithm, asynchronous SIMD interruption or the linked engine's entire feature set.
Do not promote it into a complete CPU-state qualification.

Verified original lib/libzpool/kernel.c is retained in the artifact archive:
- kernel_init reads sysconf physical pages, optional hostid, opens random devices,
  verifies uname, creates taskqs and initializes crypto/Zstd/spa/config/checksum/TSD.
- random_init requires actual readable descriptors; it cannot use fake bytes.
- random_get_bytes_common retries until resid is zero, checks negative reads only
  via ASSERT and makes no progress on a zero-byte read. A future entropy adapter
  must guarantee exact fills or explicit failure, with bounded retry/progress rules;
  returning EOF or suppressing errors is unsafe. Do not invoke it before adaptation.
- boot_ncpus in zfs_context.h follows host sysconf. It is not assigned service CPU
  capacity. physmem/ARC and pool configuration likewise need explicit port policy.

Native startup remains unavailable: real entropy, wall time where required,
identity/configuration, selected feature closure, grant-bound volume access and
measured owner-local memory/thread admission are absent. Current8-MiB large backing
and two-child/four-admission fixtures cannot fit the previously measured82-worker
host profile. Do not merely raise global arrays or reuse an available-pages snapshot
as the engine's budget. These remain Aether/port implementation work, with userland
review required for public SDK bindings; they are not a new external SDK blocker.
No R1 filesystem, package, recovery or release requirement closes here.
