# Signal return target mapping checks

Before implementation: preserve the existing anonymous memory grant and W^X
contract. It cannot create executable pages or alter fixed code/stack mappings.
Verify those denials; do not add executable grants solely for a fixture.

Copy the current signal payload into aligned static storage. Set saved RSP to an
owned page, then make that page read-only, inaccessible or unmapped. Each return
must reject with EINVAL, preserving the payload and active mask. Repeat with
saved RIP targeting non-executable, inaccessible and unmapped storage. Valid
stack and valid code controls must resume the saved continuation and fail the
missing-rejection count at terminal 87/owner 1501; faults/timeouts are not passing
controls. A tiny naked continuation restores the original RSP before jumping to
original RIP, with no stack access beforehand. Its static scratch is single-owner
fixture state, valid only during this synchronous upcall. Normal path releases
its one granted page; valid-control escape relies on domain teardown.

Select full command-runner and host suites, formatting/syntax/pin checks. Freeze
sources and retain all attempts. No kernel, ABI, quota, sibling or released-pin
changes. Simplicity: existing grants, raw traps and copied-frame trampoline cover
the current contract. No new executable-memory interface or production abstraction
is justified. General executable mapping transitions remain outside this grant.

## Results

All 241 command-runner cases and host/standards checks pass, including 98 Python
host tests. Six target rejections run per generation; the positive completes two
generations/four reclaims. Both valid-target controls fail exactly at terminal
87/owner 1501. No failed or interrupted attempts. Formatting, Python syntax,
workflow and pinned simplicity hashes pass. Kernel/build files match the prior
qualified snapshot; only the C fixture and launch harness change at runtime.
Prior evidence, released pins and sibling files are preserved. No general
executable-mapping mutation, asynchronous delivery or full-dash acceptance claim.
