# UL-007 descriptor closure consumer evidence

The unchanged DASH-fd-closure script passes locally on 2026-09-14 through actual
native dash fork/exec/wait and the pinned helper. All three selected native cases
and separate post-run serial comparisons pass on their first attempts. The script,
helper and complete workload manifest match local consumer bytes before boot.

The helper observes descriptors 3–63 closed after exec, including the fixture's
FD10 CLOEXEC alias. Child0/parent0/backend17 repeat across two lifetimes with six
reclaims; the owner reads back exactly closed ok plus newline. Injected FD3 yields
helper95/owner2130; corrupt wait status yields child0 then owner2310 without a parent
terminal. Both controls reclaim zero. Output is checked through native owner
backend readback, not a separate host stdout capture.

[Plan](review.md), [acceptance](acceptance.json), [oracles](oracles.json),
[serial checks](serial-checks.json), [native receipt](connections-results.json),
[consumer hashes](consumer-input-checks.json) and [execution](results.json) retain
exact scope and identities. Producer seal:
4011c063d1caf827c61b71fe4a5af1505d424db14f2cf25ebaaf74f52b72952c.
All members were verified before consumption; producer-packet retains the verified
non-target-archive members, including earlier failed attempts. Local build outputs
remain in the private root recorded by results.json. Source/SDK integrity and owned
cleanup pass. Local quality gate and Python syntax checks pass.

Self-review checked source/consumer identity, selector scope, failure-control
semantics, complete transcript sequences and cleanup. Transcript comparisons use
preselected producer contracts and traces, not an independent FD implementation.
Independent technical/security/reader review remains pending. The complete
290-case regression was not replayed locally; this is a focused private-adapter
qualification, not writable fd-leak-control, general filesystem support or full M3.

The corrected matched phase-one handoff is ready for replay input preparation:
[read-only intake](phase-one-intake.json) verifies its dependency hashes, all256
runtime source members and all346 support members. The SDK archive hash matches;
per-member SDK restoration checks belong to replay. This intake does not execute
the 431 command-runner and287 connections cases. Use the corrected native packet,
not the earlier handoff whose command-runner owner exceeded its size bound.
Next perform that matched replay, then remaining unchanged workloads and broader
changed-path qualification. Public SDK review, writable files, persistence,
TTY/signals and assembled system acceptance remain open.
