# 0154 — Native errno history retention

BG-058 PH-06, 2026-09-07. Continue the pinned AENIN002/ABI-15 producer from
0094; current sibling progress is not a new accepted syscall contract. Foundations
O-01/O-03/O-04, I-01/I-03–06, E-01–08 and scoped CE/TD/TE apply. No producer,
worker, release or shared ABI change. History already closes on a native sampling
error; this slice qualifies retained ownership/history rather than adding reset.

Three native cases explicitly reclaim the first worker and reuse its slot, then
sample its stale diagnostic handle at position zero, one or two. Require actual
errno 9 at the correct operation, every earlier raw return intact, closed admission,
no terminal replay, no new sample/conflict producer, retained token/generation and
counters. Cleared reader ownership reflects actual prior fixture cleanup. Repeated
denials and final replacement cleanup must preserve the complete Sample. Positives
finish at 100/3. Controls erase the primary (1065/1) or its error binding (1066/1)
after replay. These are local oracle omission controls; no new unsafe code or ABI.

Run strict 8192-byte links and all 180 native cases with fresh QEMU execution,
plus existing local gates. Preserve prior evidence and compare prior images.
Native closed Terminal inspection/replay and PH-07 retirement remain next work.

## Native result

Decision 0154 passes 180 fresh native Aether cases, including three real errno-9
history positions and two omission controls. Complete earlier replies, native
error operation, token/generation and closed admission survive repeated denied
replay/capture/conflict requests. All 151 legacy ABI-6 images rebuild identically.
No producer, worker, shared ABI or release pin changes; this is a bounded history
retention witness, not a reset/retirement or production init claim. Next: closed
Terminal inspection/replay, then BG-057 PH-07 retirement.

Prior ABI-15 byte comparison: 175/175 identical.
Maximum image: 7248/8192 bytes. All ten local gates pass in `run-3_8s3g44`.

Catalog acceptance remains pending: the reused normalized producer omits recorded
`kernel/.DS_Store` and `kernel/arch/.DS_Store` inputs. Decision 0141 restricts its
historical exception to exact old bundle pins; this new bundle inherits no waiver.
The rejected catalog candidate and failed validation are retained. The existing
catalog stays byte-identical (50 bundles / 3,019 recorded outcomes). The fresh 180
QEMU outcomes are separate consumer evidence, not a new accepted catalog entry.
BG-056 must obtain a complete newly witnessed producer bundle before catalog
acceptance; do not repair historical metadata or weaken the checker. This limitation
does not negate the recorded runtime execution or block unrelated native work.

## Validation and handoff

Decision 0154 passes all 180 fresh Aether native cases: three errno-history
positions plus two omission controls extend the prior 175 cases. All 175 previous
ABI-15 images and all 151 legacy ABI-6 rebuilds remain byte-identical. Five focused
runner tests and all ten local gates pass in `run-3_8s3g44`. No kernel/worker,
shared ABI or release pin change. Next BG-058: closed Terminal inspection/replay
without resetting history; BG-057 retirement follows.

Catalog acceptance is separately pending under BG-056: the historical normalized
producer omits two recorded .DS_Store files, and its exact-pin exception cannot
carry forward. The rejected catalog candidate and failed audit are retained;
existing catalog bytes remain unchanged. The 180 fresh QEMU outcomes are witnessed
consumer results, not a new accepted catalog entry. Obtain a complete newly
witnessed producer bundle; do not repair old records or weaken the audit.
Evidence: `docs/evidence/native-history-errno-2026-09-07/`.
