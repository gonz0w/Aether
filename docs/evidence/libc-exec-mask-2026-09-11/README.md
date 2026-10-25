# Libc exec caller-mask guard — 2026-09-11

The private source-built libc exec witness now accepts caller masks0 and16. Its
hook saves and blocks the mask after bounded argument validation, before snapshotting
descriptors or sending transport records. Known denied image admission restores the
saved mask before returning through musl errno conversion. Success carries a bounded
saved-mask record to the replacement, which verifies full blocking and installs
its descriptors before restoring the caller mask and entering application I/O.
Both positive cases repeat two generations/six reclaims.

All209 connections cases, five launch cases and host tests (99 Python, five Rust
descriptor tests) pass. Skipping failure restoration requires source221/owner1950;
skipping replacement restoration requires source222/owner1950. Both controls reject
before reclaim. The previous masked-only public exec cases remain regressions.

## Ownership and limits

AEEMSK01 is a32-byte fixture record after the argument block, with the saved u64
at8 and a zero tail. The owner checks canonical bits and matching masks across the
denied and successful requests, and relays it after the survivor table. Private
connection binding selects the process; the record cannot select another process
or introduce ambient mask authority. Buffers are fixed and synchronous. Reuse the
existing mask helpers, descriptor table and owner; no kernel, installed SDK, sibling,
dependency or release pin changes. The pre-code selection and simplicity assessment
are in NATIVE-SHELL-STARTUP.md. No failed attempt occurred in this qualification.

This proves mask state ordering, not delivery of live pending handlers. Caller
buffers must remain valid and stable; arbitrary-pointer faults, threaded callers,
general executable lookup and unknown transport recovery are outside this witness.
The next integration is a composed public fork/exec/wait external-command candidate,
with remaining live-signal and consumer requirements explicit. No independent
SDK/dash acceptance or release readiness is claimed.

## Reproduction and integrity

Use the complete connections and launch commands in NATIVE-CONNECTIONS.md with the
recorded SDK/tools lock. Timing/results files bind commands, tools and cases.
run-sources captures frozen execution inputs; sources includes final documentation.
Source and target archives are read back against recorded hashes. change.patch
compares the previous libc exec packet. compatibility.json checks all205 prior
cases: kernel load segments and entry remain identical, permitting only nonloaded
.debug_line differences. Changed older exec payloads are listed explicitly; other
payloads match outside developer entropy bytes. qualification.json records counts,
changed files and owner bounds. final-checks.json retains host, format, workflow,
standards and diff checks. collect.py verifies the previous sealed manifest and the
four-file simplicity snapshot. manifest.json seals this packet. Independent reader
review and matching-revision consumer acceptance remain pending.
