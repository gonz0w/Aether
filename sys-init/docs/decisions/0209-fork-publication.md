# 0209: Complete bounded child startup and parent disposition transport

2026-10-22 / BG-070. Pre-code review. After the existing serialized copy installs
the child FILE view, send its real304-byte AEFDB001 startup on its newly owned
writer, receive exact32-byte AEFKC001 context-ready on its reader, activate its
staged pipe holders, then send exact32-byte AEFKR001 success to the parent. Reopen
normal admission only after complete parent delivery. This fills the missing
post-copy orchestration using existing codecs, gate, stream cores and Kernel
transport; it is not an application-ready signal or a complete native owner.

The trusted caller owns the actual child/parent endpoints and supplies the exact
startup plan derived from the captured snapshot and admitted copy result. Numeric
endpoint labels and a PID do not confer authority. Validate gate sequence/Bound
PID, canonical child identity, startup encoding and three distinct nonzero endpoint
labels before I/O. Native direction/ownership enforcement remains in the kernel.
No parent/child mutation passes the gate during short transfer/EAGAIN/wait or
before context-ready and full positive disposition. Use one caller-owned304-byte
scratch and the existing finite shared poll budget; zero scratch on return/unwind.

After positive copy, any malformed/partial/lost startup, ready, activation or parent
reply retires the source/gate once and retains actual child/endpoint/holder cleanup
obligations. Never send a negative no-child result, thaw, replay copy, close process
endpoints or infer reclaim from this error. Wrong admission state returns before
I/O; it must not turn an unrelated Idle owner into a retired one. Host unwind
keeps admission closed; native abort is not unwind cleanup. Fixed memory, code,
stack, channels, workers, transaction and watchdog limits remain unchanged.

Tests use actual ProcessFiles/AF07 service and existing pipe cores, with injected
native channel results: successful short/EAGAIN schedule and complete exact output;
every startup/ready/parent short prefix; stale/malformed ready; raw errors, bad
counts/wait/budget; activation failure; wrong state/sequence/endpoint labels and
unwind. Assert no ordinary admission until complete delivery, no negative reply/
replay/endpoint close, exact scratch clearing and preserved once-only source closes.
Compiling omissions must fail named semantic assertions. Build host/native Rust,
Clippy/format and measure the added concrete Native root with the same fixed limit.
No VM or whole-owner fit claim follows from these component tests.

Simplicity: inline the fixed three-step handshake in the existing transport crate;
a second transaction service, queue or retained shadow state is unnecessary.
Reuse the gate as sole admission owner and scratch between phases. This removes
the need for each eventual dispatcher caller to independently order the same
handshake; no general transport/session framework or compatibility fallback.
Implementation-agent review; independent/native owner acceptance remains pending.

The same batch also supplies the complementary known-refusal transport: only
after `resolve_refusal` records actual successful raw thaw-11/no-child settlement,
send the original negative copy errno. Keep admission closed until every reply
byte is delivered. Partial/unknown send retires and never retries or thaws again.
Test all32 short prefixes, raw send error, interrupted delivery and wrong unsettled
state; parent FILE flags/offsets stay unchanged. This uses the same shared bounded
transfer and scratch, with no additional retained transaction state.
