# Scoped boundary review

Reviewer: Codex,2026-09-25. This is a targeted dependency assessment, not completion
of UL-063's whole source audit, independent reader review or runtime approval.
Source hashes and unchanged copies are retained in inputs.json and inputs/.

| Boundary | Current behavior | Required opt-in implementation review |
| --- | --- | --- |
| four-role.c:ar_roles_decode | Accepts only generation1/2 and AERIO001; validates full frame into a candidate before publishing | Separate v2 magic, bounded epoch and exact native cohort identity; retain atomic publication and every field/padding check |
| four-role-io.c:bootstrap | One bootstrap attempt; reads native generation, uses role decoder, then publishes refs/rights; failure poisons connection | Select v2 as a complete build profile; full-width generation validation before narrowing; no old/new fallback |
| native-io.c:bootstrap | Two bindings, generation1/2, word28 zero; validates both before publishing | Tagged v2 bootstrap and bounded epoch for child payload too; update cannot stop at runner |
| runner-result.c:ar_admission | Restricts generation1/2, constructs legacy receipt | New profile's bounded receipt domain and exact expected epoch |
| runner-result.c:ar_collection/decode | Accepts only two legacy receipts; exact reply receipt, padding, status and kind | Same v2 domain; consumed/foreign/stale receipt and malformed error rejection |
| runner-result.c:ar_terminal_exit | Calls receipt_valid again; requires cleanup exactly1, normal kind and byte-sized detail | Must use v2 domain too; otherwise valid sustained completion still maps to failure |
| four-role-runner.c | Startup/select failure returns110, then admission, close, bounded wait, repeated ECHILD check, EOF and final closes | Preserve every cleanup boundary and terminal policy while selecting consistent v2 helpers |
| prepare-four-role.py | Builds parent with four-role adapter and existing result code; child delivered separately | Both payloads and profile/SDK/build manifest required; no stale reused child binary |

Field arithmetic: file role index starts at bit16. With OR encoding,
0x71000000|0x10001 equals0x71010000|1: a larger epoch aliases another role's old
reference. The proposed nonzero16-bit domain avoids this overlap and explicitly
retires at exhaustion. Full native identity and authenticated connection ownership
remain mandatory; private selectors cannot supply either.

Existing transport limits, exact frame sizes, one-shot bootstrap, poisoning after
ambiguous exchange, close-before-send state and complete-pair publication remain
important. A new decoder must not reset bootstrap/poison state or retry an ambiguous
side effect simply because its epoch is different. Retirement cannot be proven by
this arithmetic check; it requires real owner/native observations.

Follow-on source review must include selected build paths, caller/transport lifetime,
new malformed/stale controls, native objects/linking and actual producer/consumer
composition before behavior is accepted. No runtime source was edited in this slice.
