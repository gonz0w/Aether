# AEFDT001 tagged startup FD map candidate — UL-007/081/082

`experiments/filesystem-service/fd-bindings.h` supplies a pure decoder and lookup
for a separately selected startup binding map. This prepares an exact consuming
contract for the [typed file facade](FS-FD-FACADE.md) alongside bounded console/
pipe bindings. It does not select the linked shell or change old AEFSH001/installed
records, sys-init activation policy, native limits or existing wires/SDK pins.
Affected-owner agreement and native startup enforcement are still pending.

The concrete issue is overlapping namespaces: logical shell FD3 may refer to pipe
selector3, while the file service also allocates private file FD3. A raw integer
cannot decide which owner receives a request. This map preserves explicit class
and selector separately. It is proposed as a replacement startup table for an
explicit new consumer, not a second live ownership ledger beside startup_fds.
The decoder performs no allocation, source calls, dup/close/flags mutation or
native settlement. Full runtime selection/lifecycle code remains next.

## Exact proposed snapshot

Exactly128 initialized bytes:64-byte header followed by16 four-byte records.
Fields are little-endian; use existing AEFD word helpers. This header is distinct
from the file RPC wire and the existing32-byte identity greeting.

| Header field | Value |
| --- | --- |
| bytes0–7 | AEFDT001 |
| word1 | exact nonzero file-channel generation supplied by trusted bootstrap |
| word2 | 16 records |
| words3–7 | zero |

Each record is {kind,selector,cloexec,reserved}, all unsigned bytes. Logical FD is
its index0–15. Flags are0/1 and reserved byte0. Kind0 is empty and requires selector
and flag0. Kind1 is console, selector0–2. Kind2 is the existing bounded pipe
profile, selector3–6. Kind3 is file, selector3–15. Every other kind/selector/flag
combination rejects, including legacy scratch bindings7–15 presented as pipes.
There is no implicit whole-range file classification.

Stream aliases may share a selector, including the same console stream at multiple
logical FDs. File selectors must be unique across the map: each additional file
binding requires an actual remote duplicate in ProcessFiles. This avoids a local
alias that could close a remote descriptor still used by another logical binding.
A pipe selector3 and a file selector3 are permitted simultaneously; class differs.
Per-logical-FD cloexec values are data to reconcile with actual source flags,
not proof they were enforced. No read/write rights are inferred from these bytes.

The producer must bind this snapshot to the exact admitted process/native identity,
channel endpoint holders/directions, live remote descriptors and matching legacy
stream selector/ref/generation/rights metadata. Channel generation alone is not
native process identity or an authorization token. Endpoint authentication and
actual selector existence/rights/lifetime cannot be established by this decoder.
A shape-valid file entry with no source FD is still unusable. Do not synthesize
native handles from kind, selector, path or POSIX identity. Preserve one AF07
greeting consumer/Owner/SPA and current code/stack/heap/backing/channel bounds.

## Decoder and selection

`aefd_bindings_decode(raw,length,generation,out)` validates every field/record and
all file uniqueness constraints before publishing `out`. It returns1 only on
success,0 otherwise, leaving output unchanged. All pointer ranges are valid;
output must not overlap input. Call only as part of fresh explicitly selected
bootstrap; do not apply to a running map or continue old state on failure. Caller
must stop the image and settle actual ownership when required startup fails.
The decoder does not perform that lifecycle action itself.

`aefd_bindings_lookup(map,generation,logical_fd,out)` requires a successfully
decoded immutable map and serialized access. It checks expected nonzero generation
again, bounds, selected record shape and presence. Return1 publishes exact class/
selector/flag,0 is absent/out-of-range logical FD, and -1 means malformed/stale
map or invalid output/context. Consumers must compare the result exactly to1: -1 is not a route and must
not trigger fallback. Every failed lookup leaves output unchanged. No
whole-map integrity or authentication claim for a caller-mutated C struct.

The consuming facade must branch on the returned class: file calls use the file
client and selector; stream calls use the independently validated stream adapter.
It must never retry a failed file request through a pipe/console fallback. Existing
legacy startup_fds/refs remain unchanged until an explicit new runtime/profile
replaces their representation and implements matching mutations. Native copy/fork
must freeze state across actual admission and reconcile source views; failed or
unknown exec cannot destructively commit cloexec. Immutable image admission is a
separate missing contract; readonly handles/sizes/digests do not authorize exec.

The decoder uses a small fixed16-record temporary, no4096-byte automatic array.
No native object/link/whole-stack/memory fit claim follows from the header design.
This is a local domain proposal, not a new cross-project standard or accepted
sys-init startup API. Affected owners must reconcile and select before integration.

## Host qualification and follow-ons

```
python3 -B experiments/filesystem-service/check-fd-bindings.py
```

The C17/UBSan fixture covers65,536 kind/selector pairs plus exact/truncated/excess
lengths, generation/version/count/reserved bytes, flags, file duplicates versus
permitted stream aliases, stale lookups and complete output nonpublication.
A positive snapshot holds pipe3 and file3 at distinct logical FDs with preserved
class/flags. Total65,951 host cases include grouped lookup assertions; they are
not native process counts. Five compiling omissions must fail specific assertions
for generation, reserved fields, file uniqueness, pipe bounds and class retention.

Clang21.1.8, formatter, LLVM resource headers, host SDK header closure, UBSan runtime,
exact client9/codec and owned command helper are pinned before consumption and
rechecked. C17 strict diagnostics/nonmutating format/UBSan apply. Each compile is
bounded to60s and test30s, streams16MiB, clean environment/private build root;
actual Python3.10.21 and3.14.7 qualify the host recipe. No host IPC, live service,
native trap/object/link/shell or concrete resource-fit qualification in this suite.
Prior facade/live-service tests remain exact unchanged evidence, not rerun here.

[Evidence](../evidence/filesystem-fd-bindings-2026-10-21/README.md). Source-only
candidate: `build/service-deliveries/filesystem-fd-bindings-2026-10-21-v1`.
Next reconcile the proposed snapshot with sys-init, implement new shell table/
startup/dispatch and actual file/pipe/console mutation ownership without duplicate
ledgers, then native copy/failed-exec preservation, immutable exec admission and
complete fit/dispatcher/native commands/errors/cleanup/fresh boot. Independent
owner/reader and full UL-007/081/082/M3/R1/packages/Zsh/TTY remain open.
