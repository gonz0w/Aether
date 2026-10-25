# M4 live cross-core display slice

The [remote lifetime slice](M4-REMOTE-LIFETIME.md) now extends this baseline with
two generations, owner-confirmed cleanup and a new final acceptance marker.
The remaining text records the original single-generation experiment.

Keep lifecycle v1 and its companion client contract unchanged. After M3 completes,
bootstrap a fresh AP publisher domain and run it concurrently with the existing
fresh BSP display domain. The original M3 domains remain stopped/reserved. This
is a separate live-IPC experiment, not supervised restart or reuse of AP backing.

Reuse the drained request/reply transport pages only after both original workers
have completed IPC and stopped. Request carries BSP acknowledgments; reply carries
AP results. Each phase still has exactly one producer and consumer per queue.
New two-slot tables use distinct display/publisher namespaces, with fixed route
and direction bindings. Old M3 handles and unused slots fail. The readiness queue
is not granted. The display's framebuffer namespace is separate from endpoint
handles; only display can map framebuffer pages.

Register-only send/receive operations remain 1/2 with the existing status codes.
The display receives its link base in R9; request is base, reply is base|1. The AP
publisher gets its base in RSI. Both exercise invalid handles and wrong direction
before work. The AP also attempts a framebuffer read and must fault as unmapped.

For sequence 1..100, the AP computes the running sum and sends
`sequence << 32 | sum`. Rust display checks sequence and triangular-sum value,
renders worker/display progress bars, then acknowledges the exact sequence. The
publisher cannot advance until display acknowledges. The last acknowledgment
must be consumed before publisher exit. Completion requires 100 messages in each
direction on both cores, authority/mapping checks, and publisher termination.
The final display also renders the received sum (5,050) and validated result count
(100). The kernel transports words; it does not calculate results or draw progress.

Both runtimes retain independent local APIC watchdogs. Display fixture completion
returns Busy while publisher terminal publication is pending, rather than racing
its exit. An AP release/acquire flag publishes successful completion; per-core
contexts/capability tables are never remotely mutated. A shared bootstrap gate
starts the publisher after M3 acceptance. No unbounded queue or new transport
page is added. The display alone uses Rust size optimization (`opt-level=s`)
to keep the expanded rendering code within its existing single-page limit.

Smoke requires `AETHER LIVE DISPLAY PASS`, retains prior rendering/isolation
checks, and verifies pixels in both user-rendered bars. `zig build smoke -Dbad-display-message=true -p zig-out/bad-display-message`
must fail in the Rust consumer; skipped drawing must still fail screenshot checks.
This proves concurrent user-space cooperation, not a calibrated performance
measurement, a general display protocol, or cross-core supervisor recovery.
