# V4 queued bytes and client-reply recovery

All397 command cases and98 Python host tests pass, including offline pin/workflow
checks. No unexpected failed target attempt.

This packet qualifies client-side ambiguity after a known backend result. It does
not qualify a lost backend reply, backend crash or general service restart. Final
suite counts and frozen source/artifact identities are in qualification.json.

V3↔V4 mismatch uses the existing header acknowledgment, then an atomic16-byte
body write. The receiver consumes one tagged witness byte and rejects the version
with15 bytes still unread. Both directions require unpublished state, client110
and client110/stream17/file17 order across two generations with six reclaims.
The V3 receiver retains its prior interface. A wrong witness must fail client108/
owner1501 with zero reclaims; a timeout or missing body does not satisfy the oracle.

Six file cases complete a real open, four-byte read or consuming close through
the unchanged Rust service. The owner then corrupts a reserved client-reply byte
or sends16 of the32 reply bytes and closes that writer. The client must observe
EIO and poison, preserve all16 read-buffer sentinel bytes, avoid partial open
publication, consume local close, restore the native signal mask and issue no
subsequent channel calls. It locally closes all remaining facade descriptors and
exits1. The owner independently rejects any post-poison request or partial frame.

Only after observing that terminal may the owner retire retained file records.
Open/read reply failures leave exactly one known record; close reply failures
leave none because the backend close already completed. Known records are closed
through the healthy backend and an explicit read of the consumed handle must
return EBADF with zero payload. No operation is replayed. Backend/stream shutdown,
endpoint closure and native reclaim then require client1/stream17/file17 order
and six reclaims across two generations, with empty streams and exact file
open/read counts. Skipping owner retirement must reject owner1599 after client1;
this control claims no native reclaims or successful recovery.

The boundary is deliberate: the owner has a checked backend response before
corrupting/cutting the client response. Existing fatal checks for an unknown
backend outcome remain unchanged. Confirmed service-stop recovery for that separate
failure is the next implementation, not evidence supplied by these tests.

No new kernel API, resource quota, service protocol, sibling, upstream object,
SDK default or released pin. The largest new owner variant is8056 bytes within
the existing8192-byte bound. Keep that constraint visible for subsequent work.
Compact C conventions remain under DEVELOPMENT's migration exception; Rust uses
edition2024. Optional counter/fault controls affect this native fixture only;
no fresh M4 run is selected.

Commands from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 scripts/check_workflow.py
python3 docs/evidence/shell-file-reply-recovery-2026-09-09/collect.py
```

The collector verifies final sources, the prior sealed descriptor packet and
simplicity snapshot, and reads back both archives. The recursive manifest seals
all evidence. Matching consumer acceptance, uncertain backend recovery, actual-main
ENV, persistent OpenZFS and the assembled serial-shell release remain open.
