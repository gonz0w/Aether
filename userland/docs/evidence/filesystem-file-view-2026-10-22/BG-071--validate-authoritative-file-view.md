---
id: BG-071
title: Validate fork snapshot against authoritative process file view
status: captured
created: 2026-10-22
source_type: integration-follow-on
area: native
---

Essential BG-069/070 prerequisite; matching userland library input needed.
Current serialized-copy17 ProcessFiles exposes position and flag mutation but no
read-only exact file-slot/cloexec view validation. Aether's selected transaction
requires comparing the tagged request against actual broker state before copy.
Pure shape validation/current process key cannot establish that correspondence.
Do not trust client flags, mutate parent flags to match, use destructive exec-close
as a probe, or duplicate the authoritative descriptor ledger in sys-init.

Request a separately versioned pure API under the current parent key/exclusive
borrow: validate exact thirteen remote FILE slots/presence and per-slot cloexec
against the complete claimed map, or return equivalent bounded read-only metadata.
A pair of presence/flag bitmasks is one possible minimal interface; no API/name is
allocated here. Validate current key, unused bits, hidden/omitted/extra/stale FDs
and flag differences with unchanged parent/no source/native callback on refusal.
Preserve old API/candidate bytes. Actual-library positive/negative/unknown/stale
and same-position/different-flags tests, exact sealed handoff and consuming witness
are required. No sibling change/message or owner approval implied.

Then BG-070 can compare authoritative file view plus actual stream holdings/history
inside the gate before native copy. BG-069 remains active for this final enforcing
preflight; the old native-freeze ordering choice itself is now resolved.
