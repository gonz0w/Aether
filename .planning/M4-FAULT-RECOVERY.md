# M4 retained fault records and repeated replacement

Extends M4-SUPERVISOR to five generations on the same AP code/stack backing and
page tables. No module or lifecycle-v1 ABI change. Each generation delivers 20
acknowledged results. Generations 1..4 then queue one extra, unacknowledged result;
the supervisor discards it after confirmed terminal state and the next generation
recomputes it. Display validates all 100 results, ending at 5,050, and refreshes
its endpoint grant after each 20-result group. Only stateless computation retries
are demonstrated.

Generations 1, 3 and 5 checkpoint and spin until explicit supervisor stop.
Generations 2 and 4 execute UD2 after queuing their extra result, without a
checkpoint or stop request. The AP exception path disables the worker and its
endpoint authority, records reason 2 (fault), detail 6 (#UD vector), and publishes
stopped. This slice validates that unrequested user fault path at a fixed workload
boundary, not recovery from every exception or arbitrary instruction/I/O state.
Kernel faults, NMI, double fault and machine check are not worker recovery events.

Terminal word is reason<<32 | detail: forced stop is 3/0, fault is 2/6. AP owns
this word in the existing control transport, publishing it before the terminal
snapshot. Supervisor observation of stopped closes BSP endpoint access even when
no stop request was sent. Syscall 57 with a current control or observe grant
returns the terminal word, or Busy before terminal publication/during replacement.
It remains readable after transport discard and memory reclaim. Replacement is
an explicit authorization to consume it; new-generation reads cannot expose the
previous terminal word. Old-generation handles are rejected after rebinding.
This bounded profile has one controller, not a general multi-observer event ABI.

Every reclaim removes the active user stack PTE, reloads CR3, verifies absence of all
user stack entries and code mapping, zeros the same physical code/stack backing,
and clears the saved frame. Each generation uses a fresh virtual stack page;
Rust probes the previous page as unmapped and verifies zero data in its new page.
No additional physical worker pages, queue pages or kernel stacks are allocated
per generation. Final acceptance requires five reclaims, two faults and three
forced stops. A sixth generation returns Exhausted. Generation-limit arithmetic
and terminal retention are host-tested.

Supervisor checks the exact terminal record before discard, after discard and
after reclaim, with yields between reads. `-Ddrop-remote-terminal=true` deliberately
clears a fault record during reclaim and must fail in the supervisor before replacement.
Existing stale-generation, discard, unmap, zeroing and supervisor-fault negative
checks remain applicable. Default smoke requires `AETHER FAULT RECOVERY PASS`;
the earlier supervisor marker alone is insufficient. Commands remain in README.


The automated `python3 scripts/regression.py` suite now includes stale result
generation rejection. The fault-injected publisher tags sequence 21 as generation
1 after replacement. Display's status-5 failure produces one extra bounded ASCII
diagnostic only when its kernel-owned counters show 20 acknowledgments and 21
received results on the live generation-2 namespace. The harness requires first
cleanup, that diagnostic, and the unchanged display-check panic in order. This
is fixture evidence, not a new syscall, authority grant or user-message parser.
Earlier unrelated display faults cannot substitute for that context.
