# UL-007 unchanged failed-exec proposal

Status: userland intake proposal for Aether's private exec adapter; not implemented,
not sent to another task, and not a shared standard or public SDK contract.

The unchanged [script](workloads/failed-exec.sh) runs /inputs/missing followed by
/inputs/not-executable, requires127 then126, and prints exec errors ok newline.
Its final exit must be0. Keep the original manifest, environment and stdout hashes.
A successful denied /denied probe is prerequisite evidence, not this script.

## Current gap

The [captured exec staging source](../../docs/evidence/dash-acceptance-index-2026-09-14/exec-stage.h)
from suspend-recovery has SHA256
607555d5c759e5656d73b801945153a5b76d06bf3885621749b920955099f961.
Its initial allow-list admits /next, /denied and conditionally /inputs/helper;
other names return ENOENT. Thus /inputs/not-executable cannot yet reach a
present-but-denied route. This is source inspection, not a new native result.

## Required owner selection

Provide an explicitly absent /inputs/missing route and an owner-backed present,
non-executable /inputs/not-executable route. Distinguish ENOENT from EACCES at the
native exec boundary and let unchanged dash derive shell statuses127/126. Do not
fake shell statuses, print the success line in an adapter, or infer authority from
path strings or POSIX mode bits. Reuse the existing denied-image transaction where
appropriate; adding a general filesystem or process service is not required by
this bounded witness.

Rejected replacement must leave the calling image, descriptors, signal mask and
owned references valid so the script can continue. Preserve actual fork/exec/wait
bookkeeping and collect/reclaim every admitted child. Select the concrete expected
terminal sequence before running; the number of child admissions must be measured
from the actual dash path rather than copied from another script's recipe.

Require exact stdout readback and parent exit0, both real command statuses,
restored execution state and cleanup across two lifetimes. Negative controls must
swap missing and denied error identities independently, skip the second attempt,
and reject false success/output. Retain diagnostics without requiring Linux-specific
wording. Infrastructure failure, ENOTSUP, timeout or uncertain cleanup cannot pass.

Pin final sources, SDK/tools and workload bytes, run the focused unchanged script
and controls, then affected command-runner/connection regression on the same set.
Avoid competing long qualifications and select the outer budget before execution;
never extend a deadline retrospectively to relabel an incomplete result. Preserve
owner ABI/resource limits and all failed attempts. Public SDK review remains open.

Simplicity: extend the smallest existing owner-backed denial fixture if its
transaction guarantees fit. A separate loader, synthetic filesystem or alternate
script adds scope without satisfying this requirement. Remove no compatibility
path until its affected consumers have matching evidence.
