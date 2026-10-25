# Owner-local lifetime admission extension (before code)

Requirement: the retained OpenZFS host workload creates281 workers over three
lifecycles; current four lifetime admissions prevent even sequential exploration.
Introduce opt-in native-thread-reuse with512 monotonic lifetime admissions, requiring
memory, threads and the existing two-child profile. This is an experiment ceiling,
not a whole-engine capacity claim. Preserve ordinary four-admission bytes/identities,
all live-slot/memory/stack/TLS bounds, parent-only creation, grants and retirement.
No sibling/SDK/pin change, worker-origin creation or new global object table.

Each successful admission consumes one ordinal; retirement never replenishes it.
Nonrepeating IDs keep existing first identities and stride8. At exhaustion reject
-28 before mutation. Failed/stale/foreign calls cannot spend ordinals or publish
execution. Running children reject retirement and keep mapped backing pinned;
only confirmed stopped/retired contexts allow unmap, zero and reuse. Whole-domain
replacement resets the budget with a fresh generation-bound thread grant, never
reopening an old grant.512 is far below arithmetic/TID overflow; pure ID tests
cover all profiles/owners, exact limits and adversarial ordinal inputs.

Tests: two domains run512 create/compare-wait/observe/retire/unmap cycles with
saved IDs and real cleared-TID completion; final create denies without pointer
mutation; prior IDs deny while a new child exists; foreign grants deny. A four-
admission default still exhausts at four. Actual same-ID kernel mutant must
fail254. Three supervised admissions show fresh quotas and grants. Preserve old
memory/TLS/output/exact64-yield checks. Run complete older pair and pthread lifecycle
suites, entropy/M4/block regressions, host tests, format/pin/workflow/simplicity.
Keep sources frozen, preserve every failure, record artifacts/tools/time and read
all archive members before owned duplicate cleanup. Missing checks stay coverage
limitations. Bare child FS/cookie fixtures do not prove production TCB adoption.

Security/simplicity: increase only bounded lifetime ordinal policy; no larger arrays,
new allocator, generic scheduler, implicit authority or live-slot capacity. A simpler
constant-only global increase would break legacy exhaustion contracts; the opt-in
selection preserves them. None of the existing lifetime checks can be removed.
Full engine remains unavailable:82 live workers, backing geometry/caller-origin,
provider identity/configuration and whole-engine lifecycle require separate work.
