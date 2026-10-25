# UL-007 unchanged argv and signal-table — local native evidence

On 2026-09-13 all seven selected native cases passed using frozen Aether producer
sources and the existing pinned local SDK/tools. Independent post-run serial
checks confirm every terminal and supervisor sequence. Both unchanged consumer
scripts, the helper and the complete workload manifest match local bytes.

DASH-argv preserves quoted whitespace, a literal wildcard and WITNESS=value through
real fork/exec/wait. DASH-signal-table obtains USR1 through a real substitution
pipe, collects its child, installs its trap and signals itself. Each positive
case completes two child0/parent0/backend17 lifetimes with six task reclaims.
Backend readback verifies argv ok and signal ok in the owner; those output bytes
are not separately captured as host shell stdout.

Argument and environment corruption cause child91/owner2130. Skipping the helper
causes child0/owner2310. Dropping signal posting causes child0/owner2175; bypassing
the PID guard causes parent signal10/owner2176. All five controls reclaim zero,
as required by the retained owner rejection contract.

[Plan](review.md), [acceptance](acceptance.json), [native receipt](connections-results.json),
[serial checks](serial-checks.json), [consumer hashes](consumer-input-checks.json)
and [execution/inputs](results.json) retain scope and exact identities. The
producer seal is a95c142b4f21038bf102794f33ae12830c1d7a6dfa58e3785620668cc4c2db0c.
Its verified packet is retained under producer-packet, excluding target artifact
archives after verification. Local artifacts remain in the private build root
recorded in results.json. Prior evidence is unchanged.

The native execution passed on its first local attempt. Initial retention used
serial.log instead of native-serial.log and failed before assertions; the script
and failure record are retained. Corrected retention passed all seven checks
without rerunning native cases. The quality gate and Python syntax checks pass.
Self-review covered the focused selector, source/SDK checks, consumer byte identity,
serial oracles and claim boundaries; independent technical/security/reader review
is pending.

This is focused acceptance on a private producer adapter, not a public installed
SDK. The producer's full 287-case regression was not rerun locally. Next qualify
the remaining changed native pipe/exec controls and consume the consolidated
phase-one handoff. Original DASH-substitution, concurrent pipelines, filesystem
redirection, interruption/TTY and assembly remain separate open gates. The bounded
self-USR1 implementation does not establish general POSIX kill/signals. M3 remains
open; no release-readiness claim follows.
