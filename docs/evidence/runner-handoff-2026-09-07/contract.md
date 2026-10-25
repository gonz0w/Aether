# RL audit and bounded producer return package

Before code, 2026-09-07. Audit the exact retained userland RL-01–12 proposal and
owner-return request. Close four producer coverage gaps: positive one-byte writes
for usage64 and denied ENOENT2; a help client sending launch op4 must reject before
admission (1302); a second-generation parent collecting generation1 receipt must
reject at1404 after exactly three prior reclaims. Existing state machines enforce
these outcomes; add only selected test configs and deliberate client controls.
No runtime ABI, authority, policy, unsafe/resource limit or pin changes. Request
buffers stay synchronous bounded stack borrows. Preserve existing tests and all
attempts, run full command/compatibility/host/format suites on frozen sources.

Then export a complete active regular-file source archive with manifest, exact
profile selectors, RL dispositions, current test receipts/artifacts and all failed
attempts from this local-outcome program. Exclude git/cache/dependency/output and
historical archive trees explicitly; dependencies remain pinned external inputs.
Userland independently reviews, pins and rebuilds; no sibling edits/messages.
A review candidate is not published standards, userland acceptance or R1 release.
Unknown admission/collection recovery remains unsupported. Update reference,
workflow and STATE and verify archive members/hashes after extraction.
