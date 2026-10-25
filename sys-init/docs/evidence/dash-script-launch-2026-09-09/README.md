# Native script startup rollback probes

2026-09-09. Five final native probes pass in the frozen three-service script
configuration. The three ordinary script variants rebuild byte-identically.
No runtime profile, pool/generation limit, released pin or sibling changes.

The selected probe attempts file service2, stream1, then shell0. Each failure
sets argc5 in the relevant startup record and receives actual kernel EINVAL22
before worker admission or endpoint transfer. The owner retains four endpoints,
no worker and Cleanup phase. Explicit cleanup must return Idle with no resources.
Already started providers have sent and validated their greeting; no shell or
client file request has been admitted. Stream startup nevertheless creates three
empty file handles. Before EOF, readback requires empty contents, each handle is
closed, and stale read must return EBADF9. Providers are then observed at17/kind1
and reclaimed, stream before file. All owner resource inventories must be empty.

| Probe | Exact terminal/result oracle |
| --- | --- |
| file | No admitted workers; result1605/reclaimed0. |
| stream | File service17; result1605/reclaimed1. |
| shell | Stream17 then file17; result1605/reclaimed2. |
| omit-cleanup | Omit failed shell's endpoint cleanup; retained-resource check rejects1604/reclaimed0 before provider teardown. |
| omit-stream-files | Omit the stream startup handles' closure; stream exits123, expected-terminal check rejects1604/reclaimed0. File service remains unclaimed as cleaned. |

The frozen profile only accepts result100 with exactly six reclaims. These short
prefix probes therefore deliberately finish through an expected profile rejection
with distinct1605 context after their rollback assertions.1604 indicates a failed
probe invariant; only the named omission controls expect it. They do not claim a
normal boot/PASS, operator shutdown or recovered ambiguous operation. Reports
retain exact commands, serial sequences, raw images, ISO hashes and child cleanup.
ISOs remain private. Only the five final cases count toward this coverage.

The initial shell-failure attempt incorrectly assumed provider EOF alone sufficed.
Stream terminal123/owner1604 exposed its already-open handles. That failure and
the two earlier passing prefixes remain retained. A corrected four-case run passes;
the final fifth control separately demonstrates sensitivity to the missing stream
retirement. This was a probe cleanup omission, not a kernel fault or passing result.

Probe selection compiles away from the three ordinary images; no automatic startup
rollback has been wired into their success-only fixture entry. The evidence proves
explicit rollback using the retained owner and service protocol. Integration of
that failure path into an eventual product boot loop remains separate. The new
script_launch_probe.rs is selected only by script_launch_probe; optional flags
select the failed slot or omission. Existing ABI9 ownership probes cover broader
allocation/Unknown handling separately, without transferring those claims here.

SE review: the requirement is rollback of an actual startup prefix, before client
admission. Reuse fixed three-owner state and existing backend requests. A generic
rollback engine adds no value; one bounded reverse-order cleanup suffices. Correct
file-handle retirement is necessary ownership work and cannot be replaced by a
shorter EOF-only sequence. No new normal-path state, unsafe boundary or shared rule.
O-04/I-04 preserve resource ownership and observed completion; I-05 retains bounds;
E-01–08 retain frozen inputs, exact negative semantics and the failed attempt.

Next qualify controlled stop after shell admission, including outstanding file
references. These launch probes do not establish cancellation of a file operation,
interactive shell, full V4 error recovery or sustained idle/shutdown. Full local
checks and final integrity verification follow.

Final validation: all ten local gates pass in run-brtw09oo with checked sources
unchanged. Five final native probes pass; three ordinary script images remain
byte-identical. Final staged/source copies and released locks verify;
`git diff --check` passes. The initial failed attempt is retained, and no
independent review or automatic product-recovery claim follows.
