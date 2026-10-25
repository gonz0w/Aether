# 0042 — Preserve unknown outcomes; qualify confirmed producer evidence first

Accepted source review for BG-033/BG-032/BG-057 on 2026-09-06. The
[review](../research/UNKNOWN-EFFECT-RECONCILIATION.md) separates ABI-6 launch/stop/
reclaim returns, worker observations and retained wait status from newer broker
reply-failure behavior. Fifteen selected files are frozen and rechecked; this is
research evidence, not a complete build pin or fresh native acceptance.

Do not add an unknown -> executed/rejected transition to the journal. Reviewed
ABI 6 explicitly excludes replacement and lost-observation reconciliation; newer
command transports poison uncertain connections. A terminal observation can be
true without identifying which effect caused it. EBADF, EOF, timeout and a numeric
handle cannot certify an unknown effect. Retained target-reclaimed wait status is
not a replayable receipt and remains subject to its original registration identity
and completion ordering. No journal slot is released by this review.

Choose the smaller next step: BG-058 specifies and models confirmed received
ABI-6 results tied to live-owner and exact issued obligation identity, separating
execution, terminal and cleanup evidence. Preserve meaningful local reclaim-return
cleanup guarantees without claiming cross-core/device or lost-reply recovery.
A separate native force mapping and full terminal-kind projection need explicit
contracts; the existing adapter does not supply them automatically.

Reject alternatives that treat queued observations as acknowledgments, interpret
all stale handles as successful reclaim, replay launch after lost return, or adopt
ABI-9 replacement capacity as ABI-6 recovery. They lack identity/authority evidence.
No new kernel API or companion backlog change is made without a concrete missing
consumer contract. BG-033/BG-032/OQ-022 retain authoritative reconciliation;
BG-058 is captured before completing this research slice. Local mapping work is
unblocked; recovery in the selected profiles remains unsupported.

Documentation impact: current state, priority, roadmap, authority specification,
standards adoption, quality gap reference and OQ-022. Runtime source, existing
machine/token protocols, shared pins, licenses and historical evidence remain
unchanged. Run all offline checks and retain the source review plus reports.
No implementation or additional test coverage is claimed by this decision.

Validation: all offline gates pass, including the unchanged 165 model tests /
fifteen controls, 48 host tests and 37 harness tests. [Retained evidence](../evidence/reconciliation-review-2026-09-06/README.md)
includes original and late producer-document snapshots. The concurrent completed
command-result update still excludes unknown recovery. No new native execution.
