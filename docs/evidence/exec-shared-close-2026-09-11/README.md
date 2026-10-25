# Shared exec close-reply containment — 2026-09-11

Four cases qualify missing and17-byte final stdout-close receipts with a normal
peer waiting for acknowledgment or a peer already terminated by #UD. The backend
performs the close then stalls. The owner retains the source's committed/frozen
identity, sends no successful close acknowledgment and does not publish or retry.
Source/backend and any live peer must reach confirmed forced stop before endpoints
close and records are discarded. Faulted peers retain exact134/kind2. Each positive
case completes two generations/six reclaims. Zero-padding a partial receipt fails
at2100; skipping backend stop fails2101, both with zero reclaims.

All202 connections cases, five launch cases and host tests (99 Python, five Rust
descriptor tests) pass. Forced stops emit no spontaneous terminal lines; the owner
checks raw144/kind3. The fault cases additionally require exact peer134/kind2 lines
for both generations. No timeout or generic panic substitutes for these outcomes.

## Scope and review

Reuse the existing incomplete backend, bounded receiver and private connections.
The scoped containment branch distinguishes live from already-terminated peers.
No new kernel ABI, service, allocator, SDK, dependency, release pin or sibling change.
The conservative fixture holder records are abandoned only after every domain is
stopped, not accepted as successfully released from a partial receipt. The complete
pre-code requirement, forbidden outcomes and simplicity assessment are in
NATIVE-SHELL-STARTUP.md. No failed native attempt occurred in this qualification.

This fixed RAM backend disappears with the stopped domain. The result does not
establish persistent close reconciliation, owner-failure recovery, public execve,
consumer SDK/dash acceptance or release readiness. The next integration is the
actual libc exec staging call path, using these bounded producer mechanisms.
Unknown native commit receipts and consumer-required contracts remain open.

## Reproduction and integrity

Use the connections and launch invocations in NATIVE-CONNECTIONS.md with the exact
recorded SDK/tools lock. Timing/results files retain commands, tools and cases.
run-sources captures frozen execution inputs; sources includes final documentation.
Both source and target archives are read back against recorded hashes. change.patch
compares the preceding peer-terminal packet. compatibility.json verifies all196
older cases: identical kernel load segments/entry, permitting only nonloaded
.debug_line differences. Changed older exec payloads are listed explicitly; other
payloads match outside developer entropy bytes. qualification.json records counts,
changed files and owner bounds. final-checks.json records host, format, workflow,
standards and diff checks. collect.py verifies the preceding sealed manifest and
four-file simplicity snapshot. manifest.json seals the complete packet. Independent
reader review and matching-revision consumer acceptance remain pending.
