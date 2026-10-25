# 0012: Exercise known live-peer handles without transferring authority

Accepted 2026-09-05, BG-032/BG-040. Use the unchanged frozen BG-055 two-slot native
I/O profile. Its supervisor binding authorizes control operations; workers have
caller-local readiness regardless of unused holder arguments. Numeric handle
knowledge is not a grant. No shared ABI or standards change is proposed.

Launch both slots at generation one and rendezvous on output while unready.
Supply each worker the other's exact handle as eight little-endian stdin bytes.
A P command makes a worker attempt status, reclaim, output, stop and input/seal
operations on the known live peer, requiring -13. It then notifies readiness with
the peer handle as the unused argument and emits an acknowledgment, staying live.
Before the second P command, the supervisor must observe the first caller ready
and the peer still unready, with its output unmodified. After the second command,
both are ready. Run both slot orders. Explicitly stop/reclaim the first actor and
verify the second remains live-ready before its normal exit/reclaim.

Keep exact output/EOF, terminal history and stale-handle checks. An intentionally
wrong policy attributing the first notification to the peer must fail at assertion
607. Omitted zeroing must reject independently. Two reclaims preserve the existing
I/O completion contract. Both workers use the same immutable image; slot identity
is distinguished by the supervisor's handles, not a new worker identity API.

This is controlled single-core live-peer coverage, not delegated authority,
exhaustive noninterference, SMP, deadlines or supervisor recovery. Retain source,
SDK link inputs, commands and execution separately. Keep old profiles byte-stable.
