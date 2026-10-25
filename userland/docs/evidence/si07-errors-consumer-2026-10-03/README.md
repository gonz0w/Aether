# SI-07 failure-control consumer — 2026-10-03

Four fresh independently driven AENSI001/ABI22 native cases pass on their first
execution. This consumes sys-init seal
`51362f77dbeef4b91fe8baeadc01c5355f08dd0c9631d0af40367a1346a62866`.
Complete producer/base seals, source archive/overrides, selected ISOs/payloads,
owner raw/ELF, firmware and host tools verify before consumption. The unchanged
v2 parent/child hashes match the actual ISO-extracted payload in all four images.

| Case | Independent native outcome |
| --- | --- |
| split | Real16-byte reply fragments accumulate to32; one useful cycle,0/0/17 terminals,3reclaims and authorized buffered halt |
| lost | Actual write prefix reports2bytes accepted; reader loss leads to exact assertion952; no replay, completion or halt |
| close | Actual EACCES13 leaves Unknown reader/worker; cleanup/stop/start replay denied, exactly2release calls, assertion1406 |
| reclaim | Actual EBADF9 leaves Unknown worker after endpoint close; replay denied, exactly3release calls, assertion1406 |

Four pinned producer trace comparisons and183semantic corruptions pass the
independent host oracle. Fresh ELF inspections pass; sealed code sizes10640,
10864,10072,10056 and producer stack estimates2776,2776,2808,2808 fit existing
16384/4088bounds. No compiler rebuild, general recovery or conformance claim.
See [source findings](findings.md), [review](review.md),
[native results](native-results.json), [oracle controls](oracle-results.json),
[inspection](inspection.json) and [disposition](../../SI07-DISPOSITION.md).

The failed first host inspection script and corrected attempt are retained;
native runs needed no retry. All owned native processes settle through the
unchanged process helper. Quality/syntax/whitespace gates are recorded in gates.json.
All587new work files were archived and read back before redundant build outputs
were removed, reclaiming37,154,816allocated build bytes. retention.json records
the recovery archive and exact inventory. The post-retention oracle replay passes. sha256.json seals
all packet files except itself. Historical evidence and maintained runtime are
unchanged. Independent reader review, broader native schedules, useful-session
integration, SDK disposition and full SI-07/M3/R1 remain open.
