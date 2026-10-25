# Private two-pool host profile

Before implementation: test one system worker and one delay worker instead of
64 and 4, only in a private copy of pinned OpenZFS libzpool/taskq.c. Keep distinct
queue identities, TSD lifecycle, flags, queue allocation limits, callback behavior,
and all other worker defaults unchanged. Link the complete adapted taskq object
before the immutable engine archives; retain a link map and exact two-line patch.
Original engine files and archives must verify unchanged before and after runs.
This is Aether-owned R1-03 port research, not a native runtime or shared ABI change.

Allowed result: owned-file create/write/import/readback and real synthetic queue
progress/drain pass with exactly one worker creation per fixed pool per lifecycle.
Forbidden: merged executors, hidden default-pool fallback, changed callback/delay
semantics, observer failures accepted as product success, nonprivate media writes,
or conclusions that this workload establishes general queue progress or native
resource capacity. Retain upstream unsupported delayed dispatch (zero) and cancel
(ENOENT); do not claim watchdog support. Source-derived adaptation retains CDDL
and upstream notices; original recipes and review prose use BSD-2-Clause.

Select the complete preceding observer/CPU/role/dispatch negative controls, real
normal/preallocated callbacks on each fixed queue, and warmup plus ten owned-file
processes per CPU view. Validate fixed-role creation counts at every lifecycle
snapshot. A source-rebuilt original 64/4 profile must pass storage but fail the
same profile oracle with the exact fixed-pool worker-count reason. Retain no-write
existing-file denial, wrong-byte rejection, read-only zdb verification, host tests,
pins, workflow and scoped C formatting. Compare resource observations with the
retained preceding default profile, distinguishing cumulative creates from live
peaks and requested stack bytes from committed memory.

No new FFI boundary: the original C implementation and existing observer signatures
remain; no queue/callback pointers escape their current owner or lifetime. One
worker can deadlock future mutually dependent work, so do not merge other pools or
promote this trial into native defaults. Same-object internal calls remain outside
link-wrap counts. Frozen sources, tools, input/patch hashes, raw logs, all failed
attempts and bounded offline runner commands are required (Foundations O-04,
I-03/04/05, E-01–08; approved local TD/TE/CC/CP process). Retain existing 2 GiB,
512-pid, 90/120-second process and 1800-second suite ceilings; start the existing
runner only if stopped. No sibling, release-pin, kernel or grant changes.
Update feasibility, workflow and STATE after qualification; reader review,
extended stress, native memory/stack/thread-stop and real storage service remain
separate gates. Existing machine records are unchanged; no presentation adoption.
