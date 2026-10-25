# UL-007 acceptance reconciliation — 2026-09-14

Verified all twelve workload script/stdout contracts, helper identity and every
member of three selected sealed local evidence packets. Five unchanged scripts
have bounded native evidence; seven remain unqualified. The original producer-pinned
workloads.json was not changed. [Current matrix](../../../experiments/dash-native/ACCEPTANCE.md)
and [verified index](verified-index.json) distinguish current acceptance from the
historical proposal. This is evidence reconciliation, not new native execution.

Pinned the latest producer exec-stage source and prepared the
[failed-exec proposal](../../../experiments/dash-native/FAILED-EXEC.md). The present
adapter returns ENOENT for the non-executable test path; its missing/denied route
distinction needs owner implementation. No sibling file was changed or message sent.

The latest suspend-recovery producer matching runner is incomplete after timeout;
its 316 connections results are producer evidence, not new userland acceptance.
No competing native qualification was started. [Review](review.md) and [verifier](verify.py)
record selection. Python syntax and local quality checks pass. Independent reviews,
public SDK boundary and full M3/assembly remain open. No new build artifacts beyond
small evidence/check receipts were created.
