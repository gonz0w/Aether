# UL-007 native background wait consumer evidence

On 2026-09-14 the unchanged DASH-wait script and twelve associated native signal
lifecycle/control profiles passed locally on the frozen suspend-stale producer
source set. All thirteen separate post-run serial comparisons pass. The script,
helper and full workload manifest match local consumer bytes before execution.

Actual dash launches the helper in the background, waits for its real status7,
and writes wait ok. The positive run requires helper7/parent0/backend17 twice and
six reclaims. Owner backend readback checks output bytes; this is not a separate
host capture of shell stdout. Disabled notification routing rejects parent233/
owner1950 with zero reclaims.

The remaining profiles exercise notification before entry and after observed
parking; stopped, blocked and ignored parents; repeated terminal observations;
and replacement-parent isolation. Skipped parking and stop reject2330/2331.
Injected duplicate posting produces parent236/owner1950 with zero reclaims;
injected stale posting produces replacement237/owner1950 after exactly three
reclaims. The stale positive allows the replacement's own child to wake it and
finishes six reclaims. Stopped parents correctly lack invented terminal records.

[Plan](review.md), [selected oracles](oracles.json), [acceptance](acceptance.json),
[native receipt](connections-results.json), [serial comparisons](serial-checks.json)
and [consumer identities](consumer-input-checks.json) record scope and outcomes.
[Execution receipt](results.json) binds the source set, selector, driver, plan,
SDK receipt and tool lock. The producer packet seal is
8d4f4645ec611fc7bd7b28acffd4d0211fe0af254f73b41d68ea3190cac92c14.
Every producer member was verified before consumption; non-target-archive members
are retained in producer-packet. Local target artifacts remain in the private build
root recorded in results.json. Historical failed producer attempts are preserved.

The local native run and retention passed on their first attempts. All owned
execution cleanup is complete; source and SDK hashes remained unchanged. Python
syntax and the local quality gate pass. The transcript oracles were selected from
reviewed producer contracts and final retained traces before local execution;
these are independent transcript comparisons, not an independent signal model.
Mask/handler/parking/handle behavior relies on the native fixture assertions and
selected fault controls. Self-review covered this distinction, selector scope,
consumer byte identity and cleanup. Independent technical/security/reader review
remains pending.

This qualifies the selected BSP single-context private adapter. It does not
qualify eventual unblocking of ignored/blocked notifications, general default or
nested delivery, a public installed SDK, full POSIX signals or an interactive
shell. The complete 314-case suite, matched command-runner and scheduler checks
were not rerun locally. Phase-one matched replay and descriptor-closure consumer
qualification remain next work, followed by remaining original workloads and
broader changed-path regression. M3, writable files, persistence and assembled
system acceptance remain open.
