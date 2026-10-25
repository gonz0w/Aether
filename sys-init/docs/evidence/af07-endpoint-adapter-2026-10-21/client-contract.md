# Read-only AF07 client — UL-007/081/082

Implemented private allocation-free Rust2021 client:
`experiments/filesystem-service/client.rs`. It speaks the existing AFSRPC07 wire
to the sealed77-member metadata service; no service/Owner/engine source changed.
It reuses that service's Channel, word helpers and optional Framed adapter. This
is a transport client, not the shell's FD table, a supervisor or a second Owner.

Sys-init decision0194 now supplies startup/child/wait policy and consumes the
corrected ABI29 v2 inputs. Its full dispatcher remains incomplete. The new client
covers one missing transport seam; it does not satisfy the complete FD/path/
immutable executable handoff requested there. [Evidence](../evidence/filesystem-af07-client-2026-10-21/README.md).

## Provisioning and ownership

Trusted caller transfers both authenticated counterpart endpoints to Client,
including close obligations on invalid provisioning. It supplies the nonzero,
nonreused service epoch and actual delegated read-only rights (LOOKUP1/READ2,
nonempty subset3). The service must separately enforce matching delegation;
local rights checks do not constrain a hostile caller with a wider server grant.
A valid greeting is a transport observation, not readiness/authority acceptance.
The client cannot authenticate endpoints from frame bytes or numeric labels.

One serialized client holds16 fixed token bindings including permanent root1.
Opaque handles contain epoch/token and must match a retained local entry. The
server's successful lookup sequence must produce tokens2,3,... without reuse,
even after close. A caller must not reuse epochs across replacement connections.
All operations use exclusive mutable access. No native pointers, backend object
identities, credentials, clocks, paths-as-grants or concurrent borrowed buffers.

## Exact wire and local operations

64-byte initialized little-endian frames use AFSRPC07, status/opcode word1,
epoch word2 and token word3. Request reserved bytes are zero. All responses check
magic, epoch, status and the operation's exact token/kind/count/reserved layout.

| Operation | Existing wire / accepted result |
| --- | --- |
| connect | Receive success greeting token1/kind1/root size, bytes48–63 zero. No request sent. |
| lookup | op1, parent token, word4 requested rights, word5 name length; padded64-byte name frames follow. One component1–255 bytes; reject NUL, slash, dot/dotdot. Parent needs LOOKUP, child rights attenuate. Capacity/overflow checked before send. Success token is next nonreused value, kind1 directory/2 file, word5 size, zero tail. |
| read | op2, token, word4 explicit offset, word5 length1–4096, zero tail. File READ only; offset+request length<=signed64 max. Success word3/4 zero, word5 count0..requested, zero tail; receive ceil(count/64) padded body frames, all unused bytes zero. |
| stat | op6/token, bytes32–63 zero; reply retains token and kind, word5 current size, zero tail. This is raw kind/size, not POSIX stat or AF07 metadata op12. |
| close | op3/token, bytes32–63 zero; success bytes24–63 zero. Remove binding only after full acknowledgment. Root cannot be closed individually. Any final-close error retires connection. |
| disconnect | op4, bytes24–63 zero; success reply bytes24–63 zero, then both local closes. Return their two raw outcomes; Ok([-9,-5]) is an acknowledged disconnect with failed local cleanup, not successful shutdown. |

Zero-length read validates active membership, file kind, READ and offset bounds,
clears output and returns0 locally, since AF07 wire length0 is invalid. No provider
refresh or EOF observation is claimed for this case. Client receives count0..length;
actual Owner still enforces its coherent full up-to-EOF provider count. It does
not infer immutable bytes from an open handle, cached size or readonly rights.
Nested directory lookup is explicit handle-by-handle; no pathname resolver,
symlink, cwd, immutable snapshot or executable authorization is implemented.

## Error, interruption and cleanup

All read output4096 bytes is initialized before validation. Known canonical
negative i32 errno replies contain no payload, preserve error identity and may
continue. EIO(-5) and EBADF(-9) conservatively retire; an EIO state3 uncertain/
invalid-completion marker is accepted only with every other payload field zero.
Positive status, out-of-range errno, wrong epoch/token/kind/count, nonzero reserved
bytes or padded body garbage is protocol failure. No error reply has a body.

Any send/receive error may follow partial transfer: retire, discard bindings,
attempt both local closes once, retain both results and admit no further work.
Do not replay lookup, read, close or disconnect. Every failed partial read clears
all previously received bytes. Drop attempts local closes once; it sends no wire
disconnect and proves no server detach/export/reclaim. A fully acknowledged
explicit disconnect is separate from local closes, server context release,
engine drain/export, endpoint revocation and native process/memory cleanup.
Missing close evidence remains failure, not a retry opportunity.

Channel implementations must bound complete-frame calls and independently close
both endpoints. The reused native-ready Framed adapter transfers<=16 bytes,
retains its100000-poll bound and result-bearing direction-aware wait on EAGAIN.
These are existing bounds, not latency or whole-lifecycle watchdog guarantees.
No new wait policy, quota, request ceiling or generation reset is introduced.

## Delivery and acceptance limits

Source candidate: `build/service-deliveries/filesystem-af07-client-2026-10-21-v1`.
It names exact dependency and tool evidence; it is not an executable, SDK release,
service selection or grant. Reproduce with Python3.10+:

```
python3 -B experiments/filesystem-service/check-client.py
```

Host tests run the actual sealed service and Owner with synthetic storage over
bounded in-memory channels, plus hostile reply/short-transfer fixtures. Eleven
tests/eight compiling omissions qualify this scope; Rustfmt/default Clippy and
native no_std generic-library builds are distinct checks. No OpenZFS/native IPC,
monomorphized native runtime, stack/heap fit, libc, FD/fork/exec or shell acceptance.

Next connect shared file descriptions to this client, define exact process FD/
binding/path messages and immutable executable admission against owner contracts,
then consume sys-init's full dispatcher and Aether's assembled native witnesses.
Preserve one live Owner/SPA and native authority. Failed-exec parent/FD preservation,
copy/exec/wait/endpoints, native command/errors/cleanup/fresh boot, packages/Zsh/TTY,
independent reviews and full UL-007/081/082/M3/R1 remain open. No old RAM fixture
or readonly open alone can stand in for immutable executable authorization.
