# Owned serial-session diagnosis

2026-10-03, BG-067, continuation of decision0183. Diagnosis only: no runtime,
shared pin or sibling changes; composition acceptance remains incomplete.

The prior [owned candidate](../owned-serial-session-2026-10-03/README.md) retains
one delayed guest failure. Fresh diagnosis extracts the exact sealed normal and
private check-line diagnostic images, client, kernel and firmware from that
packet. `prepare.py` verifies the selected inputs and archive members against its
manifest. `inputs.json` binds that manifest/archive and driver revisions. This
is a selected-input check, not a fresh full producer-packet audit or compilation.
The executable artifacts/notices remain in the prior packet, not duplicated here.

Three diagnostic delayed cases followed by three uninstrumented delayed cases
pass. Each group ran concurrently in separate single-CPU TCG guests, with separate
firmware-variable files. Every case waits35 seconds after the first prompt and
two seconds after subsequent prompts, sends exact7-byte fragments, and has a
90-second deadline plus bounded capture and emulator group cleanup. All six
emulators were reaped. Raw/status/stderr files and exact drivers are retained.

`check.py` runs the unchanged independently authored producer oracle on all six
traces. It normalizes only a copied receipt label to `delayed` to apply its full
idle/delay contract: exact90 UART bytes, eight admission identities, ten terminal
identities/reclaims, cleanup before prompts and final authorized halt. The original
failed trace is rejected as a negative control. This does not add new protocol
coverage or establish a fix from successful retries.

The original fault RIP0x4033a9 maps to `ud2` in normal owner `dispatch::end`,
following its existing failure diagnostic. That confirms a deliberate fail path,
not which caller/check triggered it. No failing check-line diagnostic reproduced.
Direct `end` calls and unwrap/panic routes are not identified by the current
check-only instrumented image. The next focused step is capture those failure
paths/caller location in a private image, retaining code/stack budget checks;
no generic tracing framework or broad refactor is needed.

The first three private-driver invocations stopped before creating QEMU due to
an undefined local `w`; `native-preflight-failed.py` and the correction description
in `inputs.json` retain that host failure. It produced no guest receipts/traces.
The corrected driver retains separate copies before expanding normal-case labels.

No original failure, historical manifest or runtime source was rewritten. All
six successes are diagnostic evidence, not full integration or release acceptance.

All ten repository gates pass in `out/checks/run-yptbc9xb`, with checked sources
unchanged. The aggregate and raw gate outputs are retained in `validation/`.
Documentation impact is scoped to decision0183, the serial composition guide,
BG-067/state and existing quality surface; no new operator command or API.
