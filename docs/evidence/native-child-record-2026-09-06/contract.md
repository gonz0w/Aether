
## Native child record consolidation — 2026-09-06

Before implementation: group one child's Execution, admission identity, used/running
state, terminal status and stack bounds in a single owner-local Child record.
This prepares bounded concurrent slots without enabling another child yet. Keep
domain-owned admission budget, capability, mappings and current-context selection
outside the record. No ABI, resource limit, scheduling order or consumer change.

Retirement keeps current precedence: absent -2, stale ID -9, running/pending
wait/uncleared exit word -16; success clears the whole record and does not restore
the domain admission budget. Authority, parent role and argument checks stay in
native dispatch. Reclaim clears the record only after stop/clear-TID and mapping
cleanup. Pinning, wake, tick, save/restore and child exit use its embedded Execution.

Before marking complete, test rejected retirement leaves all record bytes/fields
intact, successful retirement clears CPU/TLS/wait/mask/stack/status identity and
preserves a neighboring record, and embedded/array FX state remains aligned.
Run frozen host/standards/format, all native thread profiles and affected memory,
image and M4 regressions. Retain every attempt. This is a kernel prerequisite,
not concurrent pthreads or multi-waiter condition support; next add explicit bounded
slots and per-child observation/selection under a separate executable contract.
