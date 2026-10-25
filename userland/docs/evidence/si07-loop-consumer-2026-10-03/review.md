# UL-058/UL-063 quiescent request-loop review — 2026-10-03

Before-code plan: independently consume sys-init's sealed ABI22 request loop and
replay seven cases. Producer manifest pin2115a58e13d5632c48cc4a9cf4d69cc74d5ffc81555aee743307a4126f3bfb62.
Verify every sealed member and selected external ISO/firmware before copying into
a new build root. Bind ISO payload to exact v2 runner/bytecount and owner image.
No sibling edits/messages, policy changes, public CLI adoption or standard pin update.

Cases: halt before any work; one cycle; six cycles past former cutoff; buffered rh
with complete cleanup before halt; invalidx without admission; omitted UART close
requires explicit busy-halt rejection, not successful shutdown; private65536 r
requires pre-admission rejection. Ordered terminal0/0/17 and completion/request
markers, fresh prompt-gated input delayed200ms and exact3-per-cycle reclaim are
independent oracles. Queued intent is deferred to the next quiescent boundary;
this does not test arrival during a specific backend effect or mid-effect cancellation.

Reuse the reviewed interactive driver lifecycle from the earlier SI-07 consumer,
with its process.py-owned group,120sec outer/90sec inner deadline,16MiB files and
2MiB serial cap. No detached subprocess or monitoring. Fresh firmware variables
per VM. Preserve serial/error logs, actual inputs, failed attempts and cleanup.
Original Python BSD-2-Clause; owner/vendor bytes and terms retained.

Review input planning/success.rs/sustained_owner.rs; normal lifetime/authority stays
sys-init-owned, kernel grants/ABI remain Aether-owned, userland supplies payloads.
CE/CP, O/I/E, TD/TE apply within pinned quality process. Simpler choice: exact ISO
replay with small ordered oracle; no generic cancellation framework or source rebuild.
No obsolete path removed here. Run host oracle mutations, quality/syntax/whitespace
checks; native7cases must pass independently before documenting this checkpoint.
Remaining partial/unknown reply, cleanup failures, wider idle/wakeup schedules,
useful-session composition, independent reader/SDK and full SI-07 acceptance stay open.
