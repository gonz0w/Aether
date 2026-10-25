# M4 bounded remote lifetime experiment

The [separate supervisor slice](M4-SUPERVISOR.md) supersedes this combined-client
baseline, adding private supervisor execution and queued-result discard.
The remaining text records the earlier drained-checkpoint experiment.

This extends live display with two publisher generations using the same AP-owned
code/stack backing. Lifecycle v1 stays unchanged. The display image contains a
small Rust control-test routine, not production supervision policy or sys-init
integration. The display keeps its address space and framebuffer throughout.

Generation 1 produces results 1..50, generation 2 produces 51..100. Each result is
acknowledged before the next. After its 50 acknowledgments, the publisher reports
a checkpoint and spins in user mode with dirty stack memory. The Rust controller
observes checkpoint, explicitly stops it, observes stopped, requests reclaim,
and observes reclaimed. Only then may it request a fresh generation. After the
second generation it reclaims without replacement. This is controlled stateless
handoff at a drained checkpoint, not arbitrary in-flight stop or transparent retry.

The BSP gets the initial control handle in the high 32 bits of the packed display
mask argument (expanded by Rust to generation<<32 | 0x100). Slot 0x101 is a fixed
observe-only grant. The AP publisher receives no control grant. These are static
fixture grants, not arbitrary capability transfer. Syscalls: 50 stop, 51 observe,
52 reclaim, 53 replace. RDI is the control handle. Status 0 succeeds, 1 invalid,
2 denied, 6 busy, 3 exhausted. Observe returns generation<<32 | phase in RDX:
1 running, 2 checkpoint (still runnable), 3 stopped, 4 reclaimed. Mutations return
acceptance only; the controller must observe owner-confirmed completion. Only
one request can be outstanding. The fixture permits two generations; a third
replacement returns Exhausted. Accepted stop also closes BSP data access until
replacement observation installs the new endpoint grants. Replacement acknowledgment is observed with the
old control grant, then successful observation delivers the new control grant's
generation and invalidates the old one on the BSP. Ordinary old endpoint handles
also fail after replacement. No arbitrary routing is accepted from user bytes.

A dedicated request/snapshot pair occupies offset 256 of the existing third
transport page, beyond the drained M3 readiness queue. Only trusted kernels map
it. BSP publishes commands; AP validates its own generation/state, performs local
changes and release-publishes state. Neither core mutates the other's runtime.

Stop removes runnable state and endpoint authority on the AP. Reclaim removes
user code/stack PTEs, reloads CR3, checks PTE absence, clears code/stack and saved
register state, and checks zeroing before publishing reclaimed. Kernel mappings
remain for the AP control loop. No DMA or remote user mappings exist. Replacement
reloads immutable reserved boot bytes, changes the stack virtual page, uses fresh
endpoint namespaces and resets execution counters. Rust verifies zero stack data
and rejection of the previous stack address. Terminal stopped state is retained
through reclaimed until explicit replacement consumes it; only forced-stop at
checkpoint is represented here, not a general terminal event API.

Acceptance requires 100 validated/rendered results across both generations, two
confirmed reclaims, denied observation-only mutations, stale control/endpoint
rejection, and the previous access-denial checks. Negative build options
`-Dskip-remote-unmap=true` and `-Dskip-remote-zero=true` must fail before reclaimed
publication. Default smoke requires `AETHER REMOTE LIFETIME PASS`; the earlier
live-display marker cannot establish this slice. Build/test commands remain in
README; negative smoke runs must use separate `-p zig-out/NAME` directories.
