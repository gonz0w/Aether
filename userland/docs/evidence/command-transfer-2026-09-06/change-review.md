# UL-058 CB-08–13 and transport mutation controls

Before code: separately link actual native-io.c to a scripted host peer. Fresh
process per scenario, UBSan explicitly selected (ASan prerequisite remains open).
Short/EAGAIN transfers must preserve exact request/reply bytes; zero, fatal,
overlong and 100000-turn exhaustion must poison with bounded calls. Read/close
lost replies retain local state: destination sentinel unchanged, consumed close
not repeated, subsequent file/launch/collection traffic zero. Reply metadata,
padding and signed result boundaries require exact error behavior. Invalid frame
sizes must emit nothing. Mutate reply validation and transport poison only in
private copies; exact oracle status 90 required, never arbitrary failure.

Extend existing host driver with an explicit suite selection, retaining bootstrap
inventory. No adapter behavior change planned. Run new UBSan suite and mutations,
bootstrap regression and existing 21 host/control tests; native rerun required
only if adapter behavior changes. Thirty-second owned commands, existing pins,
private build roots, source/runtime hashes and cleanup receipts. No source fetch,
new dependency, native proof or reviewer sign-off. Quality/format/syntax checks
required; retain all attempts. NB-01–04 remain next native work.

Actual technical review: current task reviewed independent peer byte construction,
per-process globals, 384/32-byte array bounds, scripted transfer results, sentinel
and call guards, exact budget counters and consuming-close observations. The
source hash matches the previous native adapter; no production mutation remains.
All 55 transfer, 24 bootstrap and 21 command checks pass. The first mutant build
failure is retained and correctly did not satisfy acceptance. Independent reviews
pending; host side-effect models cannot certify actual service completion.
