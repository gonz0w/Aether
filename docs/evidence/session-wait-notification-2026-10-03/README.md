# Asynchronous child notification during endpoint wait

Before-code review, 2026-10-03. Requirement: qualify the existing ABI24 endpoint
wait when a copied child's terminal event posts SIGCHLD after its parent has
parked. The native copy relationship, rather than a numeric PID or new signal
grant, selects the recipient. Aether owns enforcement/private witnesses; userland
owns runtime signal policy and sys-init owns boot policy. No sibling changes,
new operation, released-pin change or actual init acceptance is planned.

Two fresh parent/child generations exercise unmasked interruption and masked
notification. Both peers park on distinct empty channels; the owner delays before
releasing the child. Unmasked wait must return EINTR twice without consuming or
delivering the signal. Masked wait must remain blocked after child termination,
then accept a real byte before unmasking exposes the retained EINTR. Installing
ignore must permit progress. Exact terminal order, reclaims and authorized halt
are required. A wrong EINTR expectation must exit77 and fail the owner oracle.

Forbidden: invented signal-send authority, handler injection, fabricated bytes,
replayed requests, premature parent completion, inherited waits/pending signals,
stale generation notification or treating a watchdog as semantic rejection.
Existing six-domain/ten-channel bounds and owner-only copy/lifecycle/UART grants
remain. Only private Rust witnesses change; synchronous traps borrow live mapped
buffers, copy-result registers must be explicit, panic aborts, and no writable
statics or dependency is added. The kernel/build remain frozen and unchanged.

Tests: fresh positive and deliberate negative native witnesses, existing seven-cycle
endpoint-wait witness, full host/pin/workflow checks, scoped Rust formatting and
optimized ELF/raw/stack inspection. Retain attempts, sources, commands, firmware
and artifact hashes before removing only this run's verified output roots.
Document scoped results in NATIVE-CONNECTIONS, ROADMAP and STATE. Automatic signal
delivery, wider race schedules, public SDK adoption and actual sys-init remain open.

Simplicity: the simpler alternative is the existing self-post-before-park witness;
it cannot test a publication while already blocked. Reuse owner-authorized copy,
SIGCHLD and channel wait, avoiding an external injector or general signal API.
Added complexity is limited to two private schedules; no runtime mechanism or
obsolete compatibility path is introduced or removed.

## Qualification

`qualified.json` passes two copied parent/child generations with exact child17,
parent0 terminal order,306 ticks/300 idle, four reclaims and authorized halt.
The owner waits100 ticks with both peers alive and inputs empty before releasing
the child. For the masked schedule it additionally waits100 ticks after the child
is terminal, verifies the parent remains alive, then sends the real byte. Worker
assertions reject premature wait completion and accidental handler delivery.
The child rejects the parent's endpoints, confirming fresh copy grants. Every
owner-held channel endpoint and task handle rejects stale use after cleanup.

`negative-qualified` compiles the actual worker with a deliberately wrong EINTR
expectation. The child exits17, parent exits77, and the owner emits its failure
marker and terminates with the exact supervisor panic. No clean-halt/qualification
marker is accepted. This is a semantic failure control, not a timeout.
`verify.py` checks the retained positive trace and rejects12 named corruptions.
`baseline/qualified.json` reruns all seven existing wait generations under their
original flags (child notification disabled); it passes with seven reclaims.
Full host tests pass133 Python cases, configured Zig/Rust tests, workflow and
released pin checks. Scope contains only private Rust witnesses; no kernel source,
build policy, sibling or release-pin change. Older ABI22/23 and M4 are not rerun:
those implementation paths are byte-identical and the existing baseline also
passes. This does not fill the older-profile explicit new-op invocation matrix.

Owner raw2072 bytes equals its optimized ELF extraction. Scoped stack estimate
448/4088; worker function152 bytes plus a conservative24 for entry alignment/call,
176/65536 total. Sole indirect owner call4000ee resolves through immutable GOT
cell400810 to memset400790; raw pointer bytes are checked. No indirect jump or
worker indirect call exists. Stack aids reject other indirect targets. These are
bounded inspection estimates, not whole-system stack/security assurance.
`preparation-notes.md` and the initial failing stack aid retain inspection mistakes.
No target attempt failed unexpectedly.

Exact frozen sources/exports, commands, tools/firmware, receipts, assembly and
all generated outputs are retained in this packet. Temporary cleanup is limited
to newly created output roots after every archive member is read back and hashed.
No source or historical evidence is removed.

This closes only the actual child-terminal notification schedule, using the
existing generation-checked copy relationship. It does not implement arbitrary
peer signal send, automatic delivery/restart, SIGINT/TTY policy, cross-core waits,
all interleavings, independent review or a canonical runtime. Next remains the
matching009 userland runtime and genuine sys-init entry/policy composition.

Sealing receipt: 51 generated members in artifacts.tar.gz read
back before three newly owned VM roots were removed. Baseline totals3031 ticks/3023
idle, seven reclaims. Source maps agree across all three runs and current source;
only the two new private witnesses differ from the prior client packet.
