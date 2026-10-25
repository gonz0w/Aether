# Independent writable scratch witness (UL-040)

Four writable native QEMU outcomes and four fresh read-only regression outcomes
pass. The client extends the existing framed protocol harness; the Rust service
and conformance supervisor remain owner-provided. No kernel/sys-init working-tree
implementation or native ABI changed. This is optional, volatile scratch on one
delegated connection, not POSIX VFS, shared descriptor offsets, persistence,
package installation or native shell execution.

## Run and retained evidence

```sh
python3 experiments/native-files/check.py --writable \
  --aether /Users/cam/DEV/aether --sdk build/native-c-xhkdw6jv
python3 experiments/native-files/check.py \
  --aether build/native-writable-userland-gdomcoga/Aether \
  --sdk build/native-c-xhkdw6jv
```

Use the newly printed snapshot for a new regression run. `--writable` compiles the
owner service with its `writable` cfg and the independent C client with WRITABLE.
The default remains read-only; its client requires a zero write-root field.
Positive images use no fault cfg. Both modes retain the source/SDK/tool checks,
private kernel capture, target ELF/TLS inspection, boot dependency verification,
resource bounds and exact panic-oracle rules of [the read-only harness](README.md).
No dependency fetch, real-prefix installation or production authority is involved.

Final writable run: `build/native-writable-userland-gdomcoga`.
Fresh read-only regression: `build/native-files-userland-buw2ocw4`, using that
same captured kernel tree. [Durable records](../../docs/evidence/native-writable-userland-2026-09-05/summary.json)
retain both evidence reports, source and artifact identities, maps, build commands,
smoke arguments and all eight serial logs. These are eight outcomes, not eight
independent features or new cross-project acceptance. Earlier UL-039 evidence
remains historical; the new regression validates the changed client/runner.

## Positive behavior exercised

The service grants a separate write-root in its initial reply. The client verifies
that the read-root and root zero cannot create files, malformed create requests
fail, and the embedded seed files cannot be written or truncated. Seed bytes are
read back after denial. The test operates within the two-open-record,
three-generations-per-record and one-64-byte-scratch-file limits.

With both open records occupied, create returns EMFILE. After closing them,
creation of the same name succeeds: failure did not publish the file. Later
close/reopen also succeeds within the generation limit, checking that the failed
create did not consume a generation. Exclusive create rejects the existing name;
a second scratch name returns ENOSPC. The read-root cannot open scratch for write,
and even the write-root cannot obtain writable access to an immutable seed.

The writable handle writes sixteen known bytes. A separately opened read-only
handle sees them but cannot write or truncate. Each capacity/overflow/oversized
write or truncate failure is followed by exact readback and EOF checks; an invalid
padding request likewise leaves bytes intact. A valid zero-length write at offset
64 leaves the current 16-byte length unchanged.

A write at offset 60 fills the file to its 64-byte capacity. Reads through the
read-only handle verify every gap byte is zero, the final four bytes match TAIL,
and offset 64 is EOF. Shrinking to three bytes then extending to twenty preserves
abc and zeros all newly visible bytes. Extending again to 64 verifies the removed
TAIL bytes are not exposed. Closing/reopening the writable handle yields a fresh
identity, rejects use of the stale handle and preserves the current bytes/length.

Finally the client closes its records and request endpoint, drains service EOF,
and terminates. The owner supervisor requires service exit 17, client exit 29,
a grant-free replacement exit 33 and result 100 with three child reclaims and
channel cleanup before the exact file-service success marker.

## Semantic controls

| Writable case | Exact required outcome |
| --- | --- |
| positive | All assertions above and AETHER NATIVE FILE SERVICE PASS |
| wrong-data | Existing owner wrong_data cfg corrupts a seed read; client exits 205 |
| skip-zero | Existing owner skip_truncate_zero cfg retains removed bytes; client exits 219 when they reappear after extension |
| ignore-rights | Existing owner ignore_write_rights cfg permits mutation through the read-only handle; client exits 218 |

Each negative additionally requires supervisor result 611 before reclaim, the
exact native C profile-rejection panic and absence of the success marker. These
are explicit service mutations, never changes to the positive image. They do not
inject a kernel fault or claim enforcement of an absent POSIX API. Full final
cleanup is established by the positive case; negative cases intentionally stop
at rejection before reclaim.

The separate read-only regression passes positive, corrupted data, truncated
request and weakened root-validation cases with its original exact statuses.
It exercises the default bootstrap without write authority, rather than treating
a writable pass as proof of the read-only boundary.

## Limits and next work

Offsets are supplied per request, not shared POSIX open-file positions. This
single-client fixture intentionally delegates both roots to one client; it is
not selective multi-client delegation or login policy. Scratch exists only in
service memory and vanishes at termination. A lost mutation reply has an unknown
outcome; there is no replay/deduplication guarantee and automatic retry is not
established. No rename, unlink, append concurrency, fsync, persistent storage,
SMP, interrupted RPC or concurrent clients are tested.

UL-041 will prototype a bounded single-client userland file-descriptor layer over
this tested protocol, with shared offsets for duplicates, local descriptor
lifetime and failure cases. It must distinguish facade behavior from native
fork/exec inheritance and reject unsupported operations. Process/exec/TTY support,
shared PD owner review and release trust remain separate open work.
