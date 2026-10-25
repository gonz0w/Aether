# UL-007 shared mask and dup2 consumer qualification — 2026-09-07

PASS: all227 native command cases run locally on the captured shell-mask snapshot.
Fourteen startup-family cases include the prior nine, dup2 success/three controls,
and the omitted internal-mask control. The actual musl block/restore helpers and
public facade observe one caller-owned mask; the separate C mask is removed.
This qualifies bounded mask/descriptor prerequisites, not full dash or signal delivery.

Normal startup and dup2 return0 in two generations with owner100/four reclaims.
Wrong self-duplication and flags return70/71 with owner1501; leaked close triggers
owner1503. Omitting the internal mask helper returns73/owner1501. Prior10/20/21/30
stage and four malformed admission110 controls retain their original oracles.
Expected rejection records with reclaimed0 are not positive cleanup witnesses.

[Results](results.json) record exact argv/environment and complete outer cleanup.
[Native receipt](native-results.json) retains all227 cases, commands and artifact
hashes; [startup subset](startup-cases.json) identifies14 cases. Raw serial/QEMU
logs are in cases/. Full build outputs remain under the private path in results.
No failed attempt occurred. No producer oracle or runtime source was edited.

The source archive's186 members are checked before private extraction over the
previous verified build scaffold; every producer runtime source hash matches.
The complete resulting input inventory is retained and unchanged after execution.
All4311 reused SDK regular files match before and after; native/host tools and
private Rust wrapper are checked against prior pinned evidence. That dependency
receipt is the previous dash-startup-native packet; no new libc build is claimed.
The one-off reproduction script is retained as run.py, using the existing owned
process helper and1800-second outer bound. It is not a new public CLI/framework.
The results status, case count, source checks and cleanup receipt determine outcome.

The producer's broader348-case report and newer native self-upcall/restorer work
remain separate. Host/kernel suites outside this unchanged command recipe were
not rerun here. The local quality gate covers both adopted draft snapshots and
all three released standards checks. See [simplicity/source review](review.md).
Independent technical/reader review, actual custom-handler delivery, full dash
initialization, fork/exec/wait and pipes remain open. Next consume a completed
handler/process delivery against the prepared actual-shell workloads. No sibling,
released pin, runtime refactoring or optional utility expansion occurred.
