# EINTR and completed finalization re-entry

Before code, 2026-09-07. Reuse existing owner error injection points but return
complete EINTR (-4). Client observes actual musl errno EINTR, returns1 for copy
or retains usage64, stops data requests and closes all roles. Exact prefixes remain
11/11/0 read,22/11/0 write,0/0/16 diagnostic. Retry-write and force-success mutants
must reject1530/1501; an incorrect errno must produce client114/owner1501.

Factor this conformance client's closes into a bounded once-only finish helper.
After completion, repeated invocation with a different status must return the
original result without a channel trap or resurrecting a binding. Test successful
copy0, usage64, complete-close-error1 and unknown-read1; all existing cleanup/EOF/
backend/reclaim checks remain. Resetting the completion guard must fail client113/
owner1501. This tests completed re-entry only, not recursive in-progress callbacks,
Toybox exit hooks/fflush or a public userland finalization API.

Fixed process-local guard/result, no new authority, kernel ABI, resource budget,
dependency or unsafe boundary. Shared transport only extends opt-in trap counters.
No new diagnostic text or sibling modification. Foundations O/I/E, DEVELOPMENT
and pinned consumer request apply. Freeze sources; retain failed attempts. Run
full command/connections/inherited, host/Zig/pins/workflow and Clang21/Rust2024
checks. Keep transport.h legacy formatting for instrumentation-only edits. Update
NATIVE-CAT, workflow and STATE; preserve prior pins and UL-059 bundle bytes.
