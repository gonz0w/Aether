# Native scratch open-description composition — 2026-09-14

The [reviewed profile](../../NATIVE-SHELL-STARTUP.md#native-open-description-owner-composition)
composes the existing open-description owner with real supervisor/backend IPC.
It writes A through a parent holder, retains a distinct child-holder reference,
closes the parent, writes B through the child, closes it, and opens two independent
read descriptions. Exact A/B versus AB and EOF prove shared versus independent
offsets. Wrong rights and stale references must reject without a transport call.
Both read holders close before the unchanged copy fixture proceeds. The second
backend lifetime repeats from an absent scratch file.

Three focused cases and all328 connections cases pass. The positive completes
source71/child72/backend17 twice with six reclaims. Offset and premature-close
controls fail supervisor2503 with zero reclaims and no application terminals.
They do not pass by timeout. Full-run and focused traces/results are retained.

The final run took1021.06seconds, within the1800 review ceiling, on271 unchanged
frozen sources. Host tests pass including103 Python tests and offline standards;
formatting, workflow and simplicity hashes verify. No kernel change required a
scheduler rerun. Matching command-runner qualification remains open before the
next combined producer handoff; no previous matched result is relabelled here.

Two unsuccessful attempts are preserved. Attempt1 exceeded the legacy8192-byte
owner link limit. The profile now uses the existing16384-byte envelope, with a
9752-byte positive/offset owner and9720-byte early-close control. Attempt2 then
rejected949 at startup because the supervisor still expected ABI9; the opt-in
profile now expects existing ABI17. No kernel limit or worker quota was increased.

Holder transitions in this probe are directed by the trusted supervisor. Actual
application FD aliases, CLOEXEC filtering and frozen fork/exec snapshots do not
yet carry scratch descriptions. No real dash redirection, public SDK, independent
consumer acceptance, persistent filesystem or R1 assembly claim follows. Native
poisoned-owner recovery is also separate from these deterministic holder tests.

Source archives bind all three attempts; final results retain SDK/tool identities,
commands, binaries and serial logs. Compatibility comparison lists changed existing
ELF/raw images rather than assuming byte identity. All failed and successful target
trees are archived and read back member by member before removal of only verified
generated duplicates. Cleanup.json records paths/counts/bytes. Retained scripts
record original commands; new runs must use fresh output directories, never modify
this sealed packet. Siblings, released pins and previous evidence are unchanged.
