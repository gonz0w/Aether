# Command reply-failure evidence — 2026-09-05

[Plan and contract](../../NATIVE-COMMAND-IO.md#reply-failure-test-plan).
Sixteen final command cases and fifteen regressions (inherited-launch 9,
connections 6) pass. Kernel/host checks, 67 Python tests, all standards checks and
the workflow gate pass. Python syntax and scoped C formatting were checked.

Three client-side injections discard a successful read reply, corrupt read reply
metadata, or discard a successful close reply. Child exit 84 proves the local
checks passed: EIO, unchanged read destination, one injection, locally consuming
close, and no further channel traps through file or launch/collection helpers.
The normal runner then rejects at 69 and the broker at 970/reclaimed 0. The
allow-poison-traffic control deliberately removes the channel guard; forbidden
exchange is detected at child 93 with the same parent/broker rejection sequence.
Unrelated failures cannot satisfy these exact ordered terminal records.

These are deliberately rejected workloads. The broker performed the operation
before the adapter discarded/corrupted its response. The test does not simulate
kernel transport loss, restore a poisoned session, reconcile unknown effects or
prove remote cleanup. Original twelve command cases remain required regressions.
Native ABI, kernel, broker rights/quotas and prior consumer pins are unchanged.

`results.json` binds final source/artifact reports, host log, plan/reference bytes,
approved standards snapshot, and all three run logs. Log creation/last-write UTC
values are filesystem observations; they are explicitly not per-case guest or
process-start timestamps. `sources.tar.gz` retains final sources. Each suite
retains ELFs, raw brokers, envelopes, reports and logs up to 2 MiB; larger artifacts
remain at their hash-identified local output paths. Final command output:
`zig-out/command-runner-suite-vori_qq5`.

The first 15-case attempt passed before adding the disabled-guard control. Its
reports/logs/artifacts are retained under `initial-command-runner`; its source
hashes describe that earlier revision, while the archive contains final sources.
It is not counted among the 31 final source-matched cases. No failures were erased.
No sibling edits, independent adoption, public CLI or complete CR-01 claim follows.
