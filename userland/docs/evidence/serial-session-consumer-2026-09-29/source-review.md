# Scoped consumer technical review

Reviewed frozen source-pins.json versions of session-owner.rs/session-client.c,
serial_session.py, pipeline_capacity.py, native_launch.zig and x86_64/native_c.zig.
This task supplies technical review; independent human reader approval is pending.

Kernel selector008 explicitly enables both session lifetime and console machinery;
007 retains session-only,006 console-only. ABI selection is23 only for the combined
profile. Envelope size/reserved/length checks preserve112-byte headers and24KiB
owner cap. Four separately replayed controls test disabled configuration, truncated
image, reserved field and007 magic with incompatible008 owner. No admission may
precede these rejections. This is a private profile, not a public SDK migration.

Serial parent invokes real dash main with sh -i +m, four fixed environment entries
and native aux UID1000. Upstream defaults realize exact $ and > prompts without
widening the environment ABI. The template selects the already pinned native
input.o rather than Linux reference input.o; source builder verifies its hash before
link. The script/commands and accepted original source are unchanged.

Client readiness probes direct UART read/close EACCES for parent/copies/replacements.
Native serial capability checking remains kernel-owned. Owner validates stdio
binding presence, full shell generation reference, operation/frame size/tail and
record capacity before forwarding. Owner UART uses only selector f001. Read is
parent-only here; helpers use pipeline bindings. EAGAIN leaves the request pending;
actual one-byte positive progress against larger requests is returned once.
Synchronous stack buffers cross existing borrowed trap calls; no pointer retained.

Prompt emission is the owner quiescence boundary: children handles zero and both
pipe epochs retired. Interactive reads while constructing a job need not already
be quiescent. Host writes fragments at most7 bytes and records actual accepted
counts. Independent checks bind raw prompt offsets, observed UART prefixes, exact
input bytes/progress, parent generations and completed phase terminal identities.
No following command may be preloaded. Raw decoding recognizes exact frozen kernel
record grammars after the boot boundary; all other bytes are preserved as UART.
Incomplete/malformed terminal records cannot be silently filtered into success.

Cancellation requires actual EAGAIN after phase1's4 copies/3 execs, no children,
retired pipes, authenticated parent stop and kind3/detail143 with5 reclaims.
Our offset check permits terminal start at the first byte after the complete
prompt. It rejects cancellation before the prompt or preceding child cleanup.
This does not establish UART unplug/EOF or arbitrary interruption recovery.
Stale serial reference control checks EACCES plus zero body; stale collected wait
checks ECHILD without changed status. Retired stderr still allows session ok and
then wrapper141; route mutation is rejected by separate streams despite UART90.

All35 owner review estimates must bind the exact local raw/ELF hashes. Maximum
3944/4088 leaves144 bytes; serial max3832 leaves256. Contributor call/disassembly
inspection is scoped and reused conditionally, not a formal stack proof or an
independent all-path audit. Broader concurrency, general TTY/jobs/signals, public
SDK, reader review, full M3/R1 and SI-07 versioned runtime remain open.
