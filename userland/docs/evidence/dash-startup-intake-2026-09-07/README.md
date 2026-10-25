# UL-007 startup delivery intake — 2026-09-07

The producer dependency for the bounded startup probe is now delivered. Verified
all49 files in the producer packet manifest, the referenced SDK archive digest,
and all503 regular source archive members before safe private extraction. The
consumer source exactly matches our unchanged startup.c. Source and SDK archives
are captured under the private build path in intake.json; live sibling inputs are
not required for subsequent extraction/rebuild. No release pin or sibling changed.

Producer qualification reports222 command cases including nine startup cases.
These remain producer results: independent userland native execution is NOT RUN.
This intake is source/provenance validation, not runtime acceptance or SDK-owner
sign-off. The producer packet retains its initial missing-TLS failure separately.

Next: extract/verify the captured SDK, review adapter/bootstrap/owner code, and
independently rebuild/run the startup cases with exact stage and cleanup oracles.
The stock SDK alone is insufficient: the matched public adapter and AECAT001
admission are required. DFL/IGN disposition and stored masks provide bounded real
state transitions; custom handlers/delivery, raw musl signal paths, UID/GID and
fork/exec/wait remain unsupported. Native dash and UL-007 are not complete.

Technical intake review: Codex verified path confinement, regular-only/unique
archive members, complete manifest membership, SHA256 identities and unchanged
consumer source. Foundations input/evidence and quality rules apply. No runtime
or harness source changed. Independent technical/reader review remains pending.
