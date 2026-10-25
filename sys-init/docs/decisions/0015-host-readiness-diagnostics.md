# 0015: Distinguish readiness framing failures without changing admission

Accepted 2026-09-05 for BG-040/BG-045/BG-054. Preserve the existing first-frame
parser, lifecycle policy and three-field invalid-ready log event. Add a separate
bounded deque of immutable internal diagnostic records: code, service, generation
and received byte count (0–6). Codes are SYSINIT-READY-CLOSED (EOF before bytes),
SYSINIT-READY-INCOMPLETE (EOF during a valid partial prefix), and
SYSINIT-READY-MALFORMED (mismatching prefix). No raw payload or descriptor/capability
value is retained. At most 128 recent records are kept; this is diagnostic
retention, not durable accounting. Older records may be evicted.

A diagnostic records an observation and termination request, not observed death
or cleanup. It cannot mark readiness, admit dependencies, refresh deadlines or
rewrite model terminal causes. One failure produces one record before closing
its reader. Accepted first frames and trailing bytes retain their existing
behavior. Test all three codes, one-record semantics, generation association and
successful first frames with no false diagnostic.

Foundations evidence/interface rules and pinned Experience OUTPUT stable IDs,
separate diagnostic data and no raw untrusted display apply. This adds an internal
Python record, not an operator CLI or a new shared wire schema. No existing log,
CLI exit, test marker or standards pin changes. Future shared diagnostic rules
belong in Aether-standards; exact host fixture codes remain local.
