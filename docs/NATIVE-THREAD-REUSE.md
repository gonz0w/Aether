# Private native lifetime-admission profile

Status: experimental producer extension,2026-10-04; not public SDK adoption.
`-Dnative-thread-reuse=true` requires `-Dnative-memory=true`,
`-Dnative-threads=true` and `-Dnative-thread-pair=true`. It changes only the
owner-local lifetime admission ceiling from4 to512. Existing two live slots,
memory/backing geometry, parent-only creation, mapping checks and syscall fields
are unchanged. Default profiles still admit four successful creates per lifetime.

The domain owns its grant, child records and monotonic ordinal. Successful creation
consumes one ordinal; failed creation and retirement do not replenish or consume
it. IDs retain their first identity and stride8. Exhaustion returns-28 before
mutation; no wrapping or stale-ID reuse. Running child retirement remains-16;
stack/TLS mappings remain pinned. Stop, clear-TID handling and retirement precede
backing release. Save an admission ID independently of the clear-TID word.
A fresh supervised domain generation gets a fresh grant and budget; prior grants
are invalid. A higher ceiling does not imply512 simultaneous workers or filesystem
capacity. The retained host workload's281 creates justify this bounded experiment,
while its82 live workers still cannot fit. No new userland policy is supplied.

Before-code scope and executable receipts belong to the
[lifetime packet](evidence/native-thread-reuse-2026-10-04/README.md).
Use its `setup.py`, then `native.py`, with pinned offline tools. Builds180seconds,
VM30seconds and owned teardown3seconds; force-kill is failed evidence. It tests
512 safe reuse cycles, unchanged default exhaustion, exact identity-bypass
rejection and fresh supervised replacements. Existing pair/pthread lifecycle,
entropy/block/M4 regressions and host checks remain required before completion.
No ordinary native profile, released pin, sibling repository or SDK is changed.
