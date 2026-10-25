# Retention attempt1 correction

Native console suites passed first execution with complete owned cleanup. The
additional collector incorrectly required one producer scheduling transcript.
On positive connections, slot1/gen1 terminated before slot0/gen1. All six exact
identities/statuses and supervisor100/reclaims6 matched. On wrong input, peer
slot1/gen1 terminated74 and supervisor rejected941/reclaims0 before the parent
could post its optional80 terminal. These are not native failures or retries.

Reviewed frozen scripts/console_smoke.py (positive terminal multiset; negative
requires peer74), user/native-console/relay.rs (terminal state mismatch rejects941)
and relay.c (bad input74; parent failed channel read returns80). No contract
requires that independent terminal order or the optional parent terminal before
the supervisor rejects. Preserve original collector, log and producer transcript.

Before retry, revised collector requires exact positive terminal multiset without
duplicates, increasing generations per slot, exact final supervisor, exact echo
and PASS. Negative permits only required peer74 and optional parent80, exact final
941/0, panic and no PASS. Handoff collector stays unchanged. This supersedes only
the initial plan's exact console scheduling comparison, not lifecycle outcomes.
No source/runtime mutation or native rerun. Independent review remains pending.
