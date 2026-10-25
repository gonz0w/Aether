# Filesystem activation consumer review — 2026-10-20

BG-067 / decision0191. Aether has consumed the exact sys-init-owned ABI29 entry
and engine in eight fresh guests. The [original sealed receipt](native-receipt.json)
has SHA256 `eb792686dadc0f5e17c4fc2538b5b6cb9c53e2da618213cbadf1ee0d528dcd5b`.
[Local review](review.json) verifies all18 consumed input identities against the
actual current files, including our frozen ELF/raw/source and selected process.
This turn runs host consumer checks only; no guest or sibling checker is executed.

Aether reports pristine-file baseline, actual activation, fresh exported-pool
reader and five hostile-peer cases passing. The actual owner is unchanged2072
bytes/raw SHA `c0a01ec913eb44de96d27d93ac71416df015951cdb12095c09c7b17e9e8d706e`,
with the same1096/4088 scoped stack. The writer admits engine0/process1, settles
both, records14 cleanup boundaries, eight balanced primary waits and halt2473/
reclaimed2. Reader reports all780248 original file bytes/hash/EOF/metadata, three
reclaims/21 cleanup boundaries, and preserves the exported guarded medium.

The read-only workload does not mutate file contents; original engine import/
export **does change pool metadata**. Writer media differs from pristine. Fresh
reader media must match the writer's exported medium, and all five failed-peer
media must match their own pristine input. Do not collapse these three comparisons
or claim that activation leaves all disk bytes unchanged.

## Independent local checks and limits

Five tests in `tests/test_harness_filesystem_consumer.py` validate retained data
without any sibling/tool dependency. They bind13 frozen local inputs and the
actual linked UD2 at0x400028. Each failed-peer tail retains the first kernel M1
marker and complete subsequent kernel span. Independent exact expected sequences
verify early startup71/malformed greeting admit no dependent; reply-generation,
exit72 and reply-close settle only process1. Failed engines have no reclaim
phases3–7 or successful halt. Automatic terminal stop1/2 remains distinct from
reclamation.65 kernel-span corruptions and eight receipt corruptions reject.
These are fixed protocol doubles, not real-engine crash or device-quiescence tests.

The stored strings are normalized retained text, not original raw UART bytes.
The positive tails omit admissions and early cleanup; full positive-trace oracle
replay is unavailable from this packet. Positive results are source/artifact-bound
producer-executed native witnesses, not a new local VM run or independent complete
positive-trace replay. Full raw serial hashes remain in the sealed producer record;
we do not reconstruct missing bytes or reuse reported counts as missing traces.

[Producer host/triage history](producer-host.json) retains the earlier failed
campaign/oracle correction and unchanged executable comparison. The earlier
expectation of no failed-engine cleanup incorrectly included automatic terminal
stop1/2; the corrected oracle excludes only explicit reclaim3–7. No source/limit
weakening or fictional reclassification follows from this local review.

## Disposition

The old missing native-assembly/actual-owner gate is closed in this bounded scope.
Default serial recipes, prototype source, old locks, released standards and sibling
files remain unchanged. Native behavior changes still require fresh matching
consuming witnesses; release/independent assembled reviews remain separate.

Next product dependencies: a matching ABI29 shell/client dispatch/PID/FD closure,
filesystem-backed execution and package metadata/bytes/promotion, and userland's
Zsh/TTY delivery. Wider SESSION still has fifteen child lifetimes. These are
concrete companion inputs, not permission to mix existing ABI24/29 profiles,
clone POSIX services here or start a general lifecycle framework. The [next boot
handoff](../../FILESYSTEM-BOOT-HANDOFF.md) records the smallest requested input.

Validation: all ten `python3 scripts/check-all.py` gates pass with unchanged
checked sources. [Local check receipt](local-checks.json) pins the full report
and exact consumer-test source; inert `consumer-test.txt` preserves those bytes.
Five focused tests/73 semantic corruptions pass, new local links resolve, all nine
ABI24 maintained source pins match and `git diff --check` passes.
