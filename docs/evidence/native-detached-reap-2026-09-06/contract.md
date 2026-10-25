# Detached exit and parent-owned reaping

Use existing native child exit/observe/unmap/retire operations; add no kernel ABI
or quota. Actual musl detached create/exit runs its TSD destructors and unlinks
its thread list, then calls a fixture __unmapself replacement. That replacement
publishes its previously captured mapping identity and exits the child through
0x28001 without unmapping the executing stack. The parent uses only private saved
mapping/ID records, never the departing pthread_t, observes terminal status via
0x2800b, unmaps/zeros the mapping under its memory grant, then retires via 0x2800a.
A published request is not stop confirmation. Fixed two-slot records stay bounded
by the existing four-admission lifetime budget. Parent-driven reaping is fixture
policy, not automatic production detached support or pthread_join substitution.

Gate the child inside __unmapself with the musl list lock still held: parent must
observe it running, leave quota unchanged and get -13 from a direct premature
unmap. Only after releasing the gate and observing stopped may it reap. A reaper
that skips stop observation attempts unmap while live and must fail exact status
291. No stale pthread dereference after exit. Verify callbacks, clear-TID/list
unlock, all-child cleanup, mapping quota and reuse across two batches/supervision.
Dynamic pthread_detach, cancellation/robust mutexes and orphaned-parent recovery
remain unsupported. Canonical detached attributes apply only in this new fixture.

Run both complete lifecycle profiles, host/workflow/format and original upstream
key-source comparisons. Kernel bytes stay identical to the timed qualification;
retain that memory/raw-thread/M4 evidence instead of claiming new execution.
Freeze runtime inputs and preserve all failed attempts.
