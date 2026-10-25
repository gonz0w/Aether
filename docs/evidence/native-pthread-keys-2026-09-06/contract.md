# Pthread keys and destructor lifecycle

Use existing paired conformance domains, two live children/four admissions, pinned
musl and native grants. Rebuild key create/delete, get and set source unchanged
only for the new key fixtures. No production userland, kernel ABI or pin changes.
Prove values are initially null in children despite parent values, remain isolated,
and destructors run on the owning thread before join/retirement. Exercise cleared
value before callback, one rearm (two calls), repeated rearm bounded by musl's
PTHREAD_DESTRUCTOR_ITERATIONS, and deletion without callback. Recreate a deleted
key before any subsequent access: never use an invalid deleted key. Reuse after
join and supervisor replacement must retain clean thread/quota state.

A callback bypass must fail exact missing-callback status 263 in both domains.
Run all lifecycle cases on default/large backing, host/standards/workflow and
pinned C formatting; compare original and adapted upstream sources. Freeze sources
for target runs and retain failures. No timed/destructor-cancellation/detached
lifecycle support or dynamic key-capacity guarantee is inferred from this witness.
