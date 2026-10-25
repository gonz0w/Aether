# UL-010 principal/session proposal review plan

Scope: prepare a local consumer proposal for IAM-01 review using existing ID-01–05,
O/I/E rules and sys-init R-01/R-14–18. Refer to approved VIR-01/02 and RNG direction
without adopting new shared standards or implementing sibling behavior.

Risk: proposed administrative restart must preserve lifecycle admission and cleanup;
UID projection must not supply authority. Authentication, session lifetime, resource
charges and replay handling require distinct owners and observations. Exact protocol,
verifier and native enforcement remain unselected. No third-party source reused.

Documentation-only change: add docs/quality/IDENTITY-REVIEW.md and link it in the
existing draft inventory, backlog and state. Keep the earlier hashed identity plan
unchanged. No CLI, boot marker, release pin, source or runtime dependency changes.
All LI-01–10 cases remain NOT RUN. Independent owner/technical/reader review pending.

Validation: run python3 -B docs/quality/check.py from the repository root (existing
three bounded child-check deadlines). Check relative links and recorded SHA-256
identities. Retain quality.log and validation.json; structural checks cannot approve
the proposal. No native tests are affected or rerun. Invalidate review on relevant
owner contract changes. Preserve earlier evidence and all failed attempts.

Author consistency review will check that restart scope matches R-14, uncertain
cleanup cannot pass, and requested owner decisions are not described as approvals.
UL-010 remains active; UL-003/009/012/016 retain integration and qualification gaps.
