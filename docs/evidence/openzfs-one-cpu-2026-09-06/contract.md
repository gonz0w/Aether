# One-CPU engine-view experiment

Opt-in Linux link wrapper: only sysconf(_SC_NPROCESSORS_ONLN) returns one;
all other queries call the real sysconf unchanged, including return/errno.
This models one assigned CPU for engine sizing. It changes neither Linux affinity
nor kernel scheduling, max_ncpus=64, physical-memory discovery, worker constants,
stack attributes or work semantics. Interposition covers executable references,
not internal dynamic-library calls. It is not a production resource-discovery API.

Use an atomic counter to prove online-CPU queries occur during the engine workload,
reset after observer/environment checks and inspect after completion. Record real
host online CPUs separately from the modeled value in a new versioned JSON record.
Preserve existing demand/name/environment schemas and markers. Self-check query
routing, unchanged page/physical-page results, invalid-query return/errno and
modeled value. A deliberate two-CPU response must fail exact CPU-view diagnostic
(exit 2), independent of the host's actual CPU count. No media for this control.

Use the unchanged pinned engine, static archives and private owned-file workload.
Run one warmup plus ten fresh processes in each of the modeled and default views
on identical final observer source. Compare named cumulative creation demand;
no native performance, live-census, affinity or peak-memory inference. Retain
existing observer controls, file conflict/wrong-byte rejection and read-only zdb.
Freeze sources/artifacts, retain failures, run host/pins/workflow and formatting.

Foundations ownership/evidence and Distribution PF baseline rules apply. This
experiment does not choose queue caps or change kernel/sibling/release contracts.
Document fixed floors and remaining dependency/live-resource measurements before
selecting native service capacity or reusable admission semantics.
