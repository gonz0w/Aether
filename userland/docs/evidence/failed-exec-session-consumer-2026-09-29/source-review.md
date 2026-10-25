# Scoped failed-exec consumer source review

Reviewed sealed delivered session_exec.rs, session-client.c, session-owner.rs,
source reconciliation, native checker and linked resource records before acceptance.
The private opcode85 separates the32-byte actual lookup path from the272-byte
argv/environment vector. It accepts no caller-supplied image identifier. The parser
checks complete framing/reserved bytes, counts1..4/0..4, NUL termination and zero
padding, unused slots, nonempty environment keys and duplicate keys before lookup.
The two-entry owner fixture namespace resolves helper authority and denies the
non-executable object; absent names return ENOENT. This is not a generic VFS.
The legacy opcode84 retains its own grant/argv contract.

The synchronous owner receives path/vector through the already authenticated peer
channels. Expected first/second denied requests must come from peer1 and occur in
order. Image-commit query must be(0,0,0) both at denied reply and at terminal
observation. Error replies return before descriptor snapshot/image admission.
The owner stores the expected exit on that peer and challenges the actual terminal.
A fabricated client-side ENOENT gives child127 but no decision; bad_denial triggers
confirmed parent stop and normal orphan/pipe/worker cleanup before reporting2864.
Thus status127 alone cannot satisfy this fixture's authority witness.

The child argv/vector remains unchanged for successful exec. Descriptor validation
on a private copy precedes native admission and commit. Fork boundaries for the
first failed child, second failed child, argv and closure require prior child handles
reclaimed; the fresh pipeline may already have its pipes at its first fork. Stale
wait explicitly probes the first collected child while the second occupies the
reused slot, requiring ECHILD and untouched caller status. Slot2 reaches15 exactly.

Parent-stderr retirement is an actual bound-stream denial. The script's failed
printf does not determine final status: the unchanged exit wrapper also observes
close failure and returns141. The producer preserved its earlier guessed57 failure;
consumer acceptance requires141 and rejects57. No successful close/no-op or
poisoning waiver is introduced. Reclaim observations remain privileged and require
empty live worker/channel ownership as in prior accepted SESSION/recovery evidence.

Capacity original receipt differs from delivered source only in the stronger
host failed_exec_smoke.py checker. Its final admission checks bind exact identities
and order; all native sources remain identical. The earlier legacy receipt also
predates later session client/owner changes and includes Finder metadata omitted
from export. Its non-pipeline build does not compile those session files. A fresh
consumer legacy run on delivered sources supplies current evidence; original
receipts remain unmodified. source-reconciliation.json records both identities.
All unrelated differences reject during preparation/qualification.

Resource review remains scoped contributor assessment, not formal verification:
seventeen final owner hashes and their exact stack JSON must match local rebuilt
raw bytes, with maximum3768/4088. The new lookup state adds no unsafe pointer,
assembly, heap, kernel authority, resource limit or published SDK interface.
Arbitrary mid-frame interruption and general restartable-service behavior are not
newly qualified. Native malformed-parser fuzzing, independent human reader review,
shared SDK, general filesystem/TTY and full M3/R1 remain open.
