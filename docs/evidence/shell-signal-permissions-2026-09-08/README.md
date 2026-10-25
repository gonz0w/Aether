# Native signal return mapping transitions

Before implementation: use the existing explicit anonymous-memory capability in
only the new runner cases. Copy a valid signal payload into a granted page, then
remove write/read access or unmap it before attempting return. Each attempt must
return EINVAL without publishing a saved mask or changing readable payload bytes.
Restore access to inspect bytes; reuse after unmap must be zero. Normal musl
return must still succeed. A control that leaves the valid page writable must
resume the saved continuation and fail the missing-rejection oracle at terminal
81/owner 1501. Faults and timeouts are failures, not accepted rejections.

Scope: kernel-owned mapping validation, native command fixture and launch harness;
no public signal API or sibling changes. Reuse the existing raw memory operations
and return-attempt trampoline; no new allocator, grant type or kernel switch.
One page is owned locally and released on the positive path. The valid-control
escape leaves its page for normal domain teardown. Assembly switches RSP only
across the trap and restores it on rejection; it must not access an inaccessible
page on rejection. Tests: full command-runner, host suite, C format and Python
syntax. Sources freeze during qualification; retain any failed attempts.

Simplicity: a copied frame on one existing granted page isolates permission
validation without modifying the live handler stack. No simpler C-only return
attempt can set the required RSP. No obsolete mechanism is removed in this slice.
Saved continuation mapping transitions remain separate coverage.

## Attempt history and remaining blocker

The first run passed both new mapping cases, then the existing state fixture
failed at terminal 75/owner 1501. Its ELF matches the previous qualified ELF
exactly (cad86548929e5feede217d5948da44c12a5ca8be22cf48f4dab7dc2fd400d4bc).
Six isolated boots of that ISO passed. The combined check was split into statuses
82–86 for entry, handler mask, XMM, mask query and restored mask, retaining 75
for the existing handler-count negative oracle. Twenty isolated boots with those
diagnostics passed. Neither retries nor diagnostics establish a root cause.
Signal stability qualification remains blocked on diagnosing the initial failure.

The initial source and report are retained, along with both complete target
artifact directories and the isolated diagnostic logs/images. Only the fixture
and launch harness differ from the previous runtime snapshot. Kernel, build
configuration definitions, sibling repositories and immutable pins are unchanged.
The final host suite, including 98 Python tests, passes. Formatting, syntax,
workflow and simplicity snapshot verification pass. A premature source-receipt
check found no final results.json while the suite was running; it is repeated
after completion. No test failure is discarded or relabeled as success.

## Final run

All 237 command-runner cases pass on the fresh run. The mapping positive completes
two generations/four reclaims; the writable control fails exactly at terminal
81/owner 1501. This records bounded mapping coverage and does not clear the
intermittent state-fixture failure, confer consumer sign-off or deliver full dash.
