# AF07-backed read-only file descriptions — UL-007/081/082

Current maintained common core now specializes one/four views, with opt-in
[process view policy](FS-PROCESS-DESCRIPTORS.md). Default aliases remain one view
and pass the same regressions. The original ten-member source delivery/evidence
below is immutable; the new process candidate carries the revised common core.
No old wire or native admission/authority semantics change.

The maintained `remote-descriptors.rs` now combines the actual AF07 client with
shared offset/descriptor logic in `file-descriptions.rs`. `descriptors.rs` is the
small owner-local adapter for the same core. The remote path constructs no Owner
or SPA and does not take over the operational server's context. This is a private
Rust library handoff, not a new shell wire, C ABI, supervisor or native runtime.

[Qualification](../evidence/filesystem-remote-fds-2026-10-21/README.md) runs the
actual sealed AF07 service and Owner with synthetic storage/in-memory channels.
It is host interoperability, not OpenZFS/native authority or shell acceptance.
Original five-member owner-local/client deliveries and77-member AF07 service
remain immutable. The maintained owner-local Failure::Policy variant becomes
Failure::Source, retaining the exact original policy error inside. This is a
source-only experimental API change, not any machine protocol or SDK pin.

## Source ownership and operations

`Descriptors::connect(channel, epoch)` consumes dedicated authenticated endpoint
obligations and creates a fresh AF07 client with trusted LOOKUP|READ delegation.
The caller must provision the matching service grant; numbers/paths/FDs never
authenticate it. Fresh connect avoids importing unknown preexisting client handles.
Invalid provisioning returns the client's error and both local close results.
No external source mutation/borrow or epoch reset is exposed through this table.

Shared state has13 bindings/descriptions, file FDs3–15; console0–2 is outside this
core. Each binding holds description index/cloexec; each description holds one
source handle/offset. All effects require exclusive mutable access. Both actual
adapters implement the same synchronous Store seam: regular-file open, bounded
explicit read, current size, final close, fatal classification, retirement and
consuming disconnect. No async/RPC framework, allocation or reference counter.

| Operation | AF07-backed behavior |
| --- | --- |
| open_read(name, cloexec) | Capacity before lookup. Single validated root component1–255 bytes. op1 requests READ2 only. Directory results close their handle before returning remote EISDIR(-21). Successful opens have independent handles/offset0. |
| duplicate(fd, minimum, cloexec) | Lowest free file FD>=minimum; same retained handle/shared offset. Explicit per-FD flag; no remote lookup or new native authority. |
| read(fd, length, output) | Clear4096-byte output before validation. length<=4096 and offset+requested length<=signed64 max. AF07 read advances shared offset only after full successful result/body. Errors preserve offset; all error/tail bytes zero. |
| seek(Set/Current/End) | Checked signed64 calculation. End queries AF07 stat's current raw size; errors preserve offset. No provider seek, pathname identity or POSIX stat inference. |
| close(fd) | Remove binding; only last alias sends op3. Any failed final close retires entire table, discards references and consumes local endpoint obligations without replay. FD numbers may be reused; server tokens cannot. |
| set_close_on_exec / commit_exec_close | Flags belong to individual FDs; commit removes only flagged bindings, final-close only when no alias remains. Destructive step only AFTER confirmed native image admission. No staging/rollback/native exec is implemented. |
| cleanup | Observe both local close outcomes after retirement. Failed close evidence stays failed. |
| disconnect | Consumes table, discards bindings, sends AF07 op4, validates full reply and closes both local endpoints. Return raw outcomes: Ok([-9,-5]) means acknowledged disconnect with failed cleanup. |
| Drop / abort | Local endpoint closes once only, no wire disconnect/replay. Not server detach, native revocation, export/quiescence/reclaim or successful shutdown. |

The added Client::abort exposes the existing local shutdown operation; it returns
both endpoint results and cannot reconnect/send. Existing frame bytes and earlier
client methods are unchanged. All previous client tests and eight omissions are
rerun plus an explicit abort/no-send/no-retry test. The original source candidate
is still valid in its prior scope; new combined source delivery carries abort.

## Failure and authority boundaries

Failure::Source preserves actual policy or AF07 errors. Known remote errno may
continue when the client remains live. Fatal malformed/partial/uncertain responses
retire both client and table. Core independently rejects oversized source counts,
clears output before returning any read error and publishes no failed offset.
Store adapters are trusted source boundaries, not pluggable untrusted providers.
Client's conservative EIO/EBADF behavior and zero-length local read remain as in
[AF07 contract](FS-AF07-CLIENT.md). Existing Owner still enforces provider coherent
full up-to-EOF count. Requested signed64 range is stricter than general POSIX.

This table represents one serialized description owner. It does not authenticate
multiple process callers, implement fork sharing, offer cross-process FD binding
or supply shell descriptor messages. Reading bytes through a readonly handle does
not freeze them or authorize executable admission. No write/create/append, path
resolver/cwd/symlinks, metadata/mode/UID conversion, image staging or loader here.
Failed exec must preserve parent/FD state until actual owner-confirmed admission;
this library provides only the later close-on-exec commit operation.

## Reproduce and consume

```
python3 -B experiments/filesystem-service/check-client.py
python3 -B experiments/filesystem-service/check-descriptors.py
python3 -B experiments/filesystem-service/check-remote-descriptors.py
```

Each driver pins Rust1.98.0/native libraries, unchanged owned helper and exact77-
member AF07 dependency before use; records source/tool/argv/environment, bounded
process outcomes and cleanup in its new build root. Host counts12/12/8 and
compiling omissions8/8/11 respectively. Use actual minimum/current Python; native
no_std generic libraries are separate typed preparation, not concrete linked
runtime code, resource fit or Aether execution. Independent review stays pending.

New source-only candidate:
`build/service-deliveries/filesystem-remote-fds-2026-10-21-v1`. Includes the shared
core, both adapters, updated client and tests, license, contract and dependency
record. It references original immutable service/descriptor/client candidates;
no duplicate engine/native SDK or guessed filesystem references are shipped.

Next: authenticated process FD/path/binding messages and cross-process lifetime/
failed-exec contract, immutable executable admission with sys-init/Aether, then
full startup/copy/exec/wait/endpoints/readiness/shutdown composition and native
code/stack/heap fit/command/errors/cleanup/fresh-boot witnesses. Packages/Zsh/TTY,
independent reviews and full UL-007/081/082/M3/R1 stay open. Current sys-init core
and old RAM fixtures cannot replace these inputs; no guest/quota expansion here.
