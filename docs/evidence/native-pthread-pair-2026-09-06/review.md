# Scoped self-review

Kernel and build bytes match the prior 255-case qualification. Current changes
are restricted to the conformance adapter, lifecycle harness and documentation.
Two parent-owned records retain function/argument, handle and actual ID. The raw
trampoline reads the stable per-slot startup pair; the child never reads metadata
written by the parent after publication. Upstream join may unmap the TCB, so the
wrapper snapshots ID first and does not dereference the handle afterward. It
inspects/retire-selects exact IDs, closes the handle and accounts occupied slots.
Only parent admission/join is supported. Total admissions never replenishes.

Tests cover simultaneous live musl TCBs, independent arguments/TLS/errno, opposite
join orders, blocked joins, four total creations, quota and thread-list restoration,
child API rejection, full-slot rejection without quota/output-handle mutation,
supervisor replacement, disabled pair and duplicate identity failure controls.
The complete older lifecycle family and raw pair family are selected on both
memory profiles. No upstream patch changed; source verification checks every
producer. No new dependency or production facade is introduced.

This is self-review, not independent consumer acceptance. Wake-all translation
remains limited to this lifecycle experiment; true wake-one/requeue and multiple
condition waiters remain future work. No general POSIX, pool or libzpool claim.
