# UL-059 host parser/admission/local-output integration plan

Before code: connect actual carrier decode/selector, admission decoder and local
output helper in a single-use host-only frontend candidate. Compile the six text
fixtures from their retained proposal pins into private generated data. No native
runner, grant, package or producer change; no new shared interface allocation.

Local help/version/usage invokes no admission callback and delivers the exact
selected fixture through existing logical sink callbacks. Valid launch selection
calls admission exactly once with the owned complete invocation/environment.
Only a complete known 32-byte rejection with valid generation/padding and errors
-2/-13/-16 selects unavailable/denied/capacity. Accepted admission retains receipt
and returns a separate admitted action without local output or cleanup; collection
is a later owner. Unknown, malformed, unsupported known errors and invalid startup
return failure without fabricated usage/precondition diagnostics, retries or closes.
Retain original parser action and validated raw admission facts separately from
local delivery/close failure. All callback authority remains caller-owned.

Host tests exercise real carrier/parser inputs, exact bytes/stream separation,
complete invocation forwarding, accepted generations1/2, each local/rejection
route, absent/unknown/truncated/padded/wrong-generation replies, invalid carriers,
unclassified errno, positive status, local write/close failure and unknown, plus
re-entry. Three semantic mutants must detect launch-on-help, errno collapse and
accepting a malformed rejection. Pin Clang21.1.8/fixtures before consumption;
strict C17/UBSan, owned30s/file16MiB commands, Python3.10 grammar, pinned format and
quality standards checks. Reuse existing checker with an explicit frontend suite;
preserve default6130/four-mutant mode and its CLI stream/exit behavior. Run it and
mapped/parser/result/21 command regressions. Retain all attempts and source/tool/
fixture/plan identities. O/I/E, CE/CC/CP and TD/TC/TE apply under existing adoption.
Current-task review only; independent and owner reviews pending. No ASan/native
sanitizer or native RL-01–12 acceptance is claimed. Original code BSD-2-Clause.
