# Pool diagnostic consumer review — 2026-10-07

UL-003/015/081. Host review found three attribution gaps in Aether's prepared
failure125 decoder: malformed observation/terminal records are ignored, and an
additional contradictory supervisor result is ignored. Each synthetic corrupted
trace still attributes runtime site96. This is a diagnostic evidence defect,
not attribution of the previous native failure or a runtime reaper defect.

[Reproductions](host-14.json), [captured inputs](inputs.json),
[technical review](review.md), and [proposed owner patch](owner-proposal.diff).
The patch is **proposed, not applied to Aether or accepted**. It rejects malformed
reserved records and conflicting supervisor results before site decoding, preserves
36 valid sites, and rejects20 corruption controls on Python3.10.21 and3.14.7.
The existing decoder rejects16 selected controls. Exact nine runtime catalogue
rows and instrumented-source digest match the maintained sealed-v3 backend.
No native guest, pool image, compiler build or bulk archive was generated here.

Captured owner receipt reports a build-only engine (4,419,072 bytes,7840 more
than the failed run); original runtime reconstruction is byte-identical before
instrumenting its private copied backend. These are owner-reported build results,
not an independent ELF/map rebuild in this review. Changed instrumentation may
change resource pressure/scheduling and cannot explain an earlier run retroactively.
The latest corrected-input native pool attempt exited125 with supervisor401 and
zero reclaims. Unchanged final media bytes do not prove absence of transient writes,
flush completion, retirement or device quiescence. Cause remains unknown.

Next Aether-owned actions: review/adopt the decoder correction and obtain renewed
human disposition for one disposable diagnostic run under the existing uncertainty
stop rule. No automatic pool retry, quota increase or forced cleanup is authorized
by this review. Earlier failure evidence remains. Physical-vdev owner progress
has moved beyond the earlier empty-SPA gate; this review does not independently
accept every intervening storage stage. Pool/persistence/M3/R1 and wider SESSION
remain open. The finite ABI24 lab kit remains usable; reader review is deferred.

Validation: `python3 -B docs/evidence/pool-diagnostic-review-2026-10-07/check.py`.
Owned host logs/cleanup receipts retained; quality (including all three published
pins), minimum/current syntax and whitespace checks pass. Captured source readback
is checked before consumption. No shared pin/runtime/SDK/sibling change.
