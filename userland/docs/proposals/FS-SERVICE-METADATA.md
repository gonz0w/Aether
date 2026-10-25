# Authorized metadata service input — UL-082, 2026-10-21

Status: new AF07 host/object candidate, not native-selected or accepted. Aether
has cleared the old writable IPC gate and qualified AF06, its real Rust launch
owner and bounded sys-init activation/recovery. The separately qualified borrowed
metadata getter is now connected to this new authenticated service boundary.
Old AF06/67-member dependency and30-member executable seals remain unchanged.
No public SDK, standards pin, sys-init/pkg-mgr policy or accepted old wire changes.

## Authority and backend

Select all existing AF06 cfgs plus `fs_metadata`. Entry
`aether_fs_metadata_run` has the same nine trusted arguments and72-byte result;
`metadata-service.h` is authoritative for its C signature. Nonreused native
request/reply endpoint holder enforcement, exclusive accounted writable SPA,
trusted fixed dataset/bootstrap identity/shared UTC and all existing import/
drain/export/lifetime obligations remain. The underlying original C provider is
`zpl-metadata.c` **instead of** the directory/mutation/write/read provider, never
in addition. Aether's exact source/tools/native selection must be matched before
using the object; the existing AF06 intake cannot accept its new seal silently.

New METADATA16 is independent of LOOKUP1/READ2/WRITE4/MUTATE_DIR8. `ALL` for this
explicit new variant is31; ordinary AF06 still caps at15. Trusted provisioning
and lookup attenuation must explicitly include16 to delegate metadata. A caller
with other rights receives denied before entering the getter. File lookups still
reject MUTATE_DIR. The service checks authenticated peer/session/retained handle,
then passes its retained object/generation to the exclusive ZPL backend. Clients
cannot attach, select raw objects/generations, or change provisioned identities.

The unchanged borrowed metadata.rs validates the original136-byte C output.
Policy additionally compares identity, cached kind/size and metadata invariants
before publication. Known provider errno returns no metadata. Unsupported backend
support returns explicit95. Invalid metadata/completion retires every alias and
consumes the context before the error response. No pointer/reference escapes,
external mutation/property/export/teardown overlaps a getter, or state/allocation
is retained by this binding. Metadata operations consume no transaction slot.

## AFSRPC07 metadata reply

All inherited AF06 operations use the new `AFSRPC07` magic. AF06 bytes are rejected;
this is not an implicit extension of its opcode6 size/kind response.
Opcode12 has word2 current generation and word3 retained token; words4..7 are
zero. It requests no trailing body. Unknown/stale/foreign tokens cannot name a C
object. Malformed/denied/provider errors publish an ordinary error header only.

Success: existing64-byte header, word1 status0, word2 generation, word5 length112;
words3/4/6/7 zero. Follow with exactly two64-byte frames:112 data bytes, then16
zero tail bytes. The112 bytes are14 explicit little-endian64-bit words:

| Words | Observation |
| --- | --- |
| 0–5 | size, complete raw mode, link count, raw uid label, raw gid label, flags |
| 6–7 | atime signed seconds/two's-complement bits, nanoseconds |
| 8–9 | mtime signed seconds/two's-complement bits, nanoseconds |
| 10–11 | ctime signed seconds/two's-complement bits, nanoseconds |
| 12–13 | birthtime signed seconds/two's-complement bits, nanoseconds |

Nanoseconds must be below1e9. High64-bit owner/FUID labels, special mode/flag bits
and negative seconds are preserved without narrowing. These are raw observations,
not POSIX stat/credentials, ACL interpretation, chmod/chown or permission grants.
A future POSIX consumer must explicitly translate with checked bounds or reject
unsupported representations. Backend object/generation/parent identities are
omitted; a metadata response cannot be submitted as handle authority.

Reuse the existing4096 scratch, complete-frame helpers and explicit endian copies.
No metadata body or prior scratch bytes are sent after any error. No metadata result
is retained or replayed. Loss at the header or either body frame ends the connection,
revokes all handles, consumes its context and attempts both endpoint closes. This
does not prove engine/device quiescence or authorize supervisor replacement.

## Matched producer gate

The supplied candidate is a relocatable Rust object and matching sources/headers/
input/tool/build/notice records, not a launchable replacement service. Aether owns
the separate explicit AF07 intake/provider/client selection and fit review. Retain
all AF06 limits: data4096/names255/rename510, controller/observer8192,4096 stack/no
writable statics,8192-page engine, existing workers/channels/I/O/polls, native
selected workload no more than9 mutations/96 requests, writer60s6000/readers30s3000.
Do not reuse the consumed120s idle qualification or widen SESSION15 lifetimes.
Current object/static checks are not whole-stack or peak-memory evidence.

Smallest proposed native workload: root metadata; existing-file metadata/read/EOF;
create one0600 file, lookup with explicitly delegated READ|WRITE|METADATA22,
write/read4096 and metadata with coherent size; disconnect/export and fresh reader
verify exact original/new file, metadata, namespace and whole guarded medium.
All requests must fit the existing96 allowance and all mutations within9. Preserve
original decoder/zdb-independent field references, full content/EOF and cleanup
oracles. Qualify rights/stale/version/malformed results, partial/lost replies and
failed close without extra effects/replay, including native authenticated holder
denials. Preserve actual errno/progress/stop/quiescence/reclaim distinctions.
No native failure retry or automatic replacement after an uncertain outcome.

Only after native fit/qualification and independent intake should the Rust launch
owner select AF07 and its matching entry/magic/rights. Sys-init then consumes exact
executable/provisioning/live-readiness/shutdown inputs. This proposal does not
close those gates, ABI29 shell/PID/FD adaptation, filesystem-backed loader/runner,
ordinary mode/cross-directory promotion, package identity/layout/closure, Zsh/TTY
or persistent ISO/R1. It supplies the next concrete owner integration input.
