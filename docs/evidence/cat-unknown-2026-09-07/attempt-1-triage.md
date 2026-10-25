# Attempt 1: owner oracle error

Truncated read reached client status1, then owner1506 at native cleanup. The new
oracle expected -9 from repeated native channel close; kernel/native_channel.zig
requires -13 for the stale/unowned capability. POSIX local close still uses EBADF.
This is a test-oracle defect, not a timeout or accepted negative case. Archive
retains matching frozen sources and all generated cases/raw logs, excluding ISOs,
installed boot duplicates and kernel.elf with identities in receipts. Remaining
cases were not run. Correct only the native stale-close expectation to -13 and
rerun full command and host checks on final sources before qualification.
