# Selected Zsh home redirection contract

Issue158, base04659b100b09feb215951230ab38df28786eb3ac. Cam approved
[the design](https://github.com/gonz0w/Aether/issues/158#issuecomment-6710522629)
and [gates](https://github.com/gonz0w/Aether/issues/158#issuecomment-6710663004).
This local experiment contract adds no shared standard or kernel interface.
Status: qualified bounded experiment. The warm writer and matching cold reader
passed in QEMU; issue158 records delivery and remaining gates. The original exact
wire contract is retained in the private contract02 evidence.

## Selection, authority and scope

Rust `native_zsh_home_redirection` and C
`AEFD_ZSH_HOME_REDIRECTION_BINDINGS` select AEFP0006 on the existing complete
filesystem/process/MODE/SIGINT/file-exec/operator composition. The writer is
warm; `native_zsh_home_redirection_reader` additionally requires the cold
composition. Reader without redirection rejects at compile time. Old profiles
keep their closed dependency guards, magic, limits and behavior. New redirection
excludes historical helper-home-write and AEFD_DUP2_WIRE/AEFD_WRITE_WIRE/CWD
variants. No peer negotiation. Child pre-exec copies use006; C placeholders
match006 and get affected fits. The persisted Rust helper has no FILE requests;
its existing336-byte startup closure must still match before byte/fit reuse.

Only the exact admitted parent generation may create `/home/note` in the writer
role, once, and perform one1..16-byte write to its actual WRITE4 description.
Use existing held HOME15 authority and atomic AF09 Create; root3, terminfo and
sealed probe stay protected. Named paths, modes and UID labels are not grants.
Authorize aliases by description/actual handle, never logicalfd1 or a fixed
remote fd. Parent note reads use actual READ2 references; child note operations
reject. Refuse fork before freeze/copy while note I/O or aliases are live; check
inherit defensively too. After all note aliases close, existing helper
eligibility remains. No generic table, service, metadata request or new quota.

The selected provider implements real process-local umask initialized0077,
returning the previous mask and storing `requested & 0777`. Consume mode on
direct open/open64 and patched fopen paths exactly once. Creation accepts only
WRONLY|CREAT|EXCL, optional NOCTTY/CLOEXEC, and effective0666 & ~mask ==0600.
Reject other effective modes/flags before source effects. Read accepts RDONLY
with optional NOCTTY/CLOEXEC. No TRUNC/APPEND/RDWR/plain writable reopen.
Mode0600 is creation-time enforcement, not cold metadata readback.

## AEFP0006 framing

Keep64-byte little-endian headers and existing nonzero generation/sequence,
one outstanding operation,4096 workspace, exact padding and retirement rules.
Ordinary opcodes1–6 and8–10 retain current meanings; opcode7 stays reserved.
Opcode1 admits the parent note read in its allowed phase only. Opcode11 uses
the existing64-byte typed write receipt and causes, scoped to the note WRITE
description and one nonempty1..16-byte write at shared offset0 only. Reject
read and seek on the active WRITE-only note description before source effects;
other read-only note/terminfo seek semantics stay unchanged. Preserve actual
progress and success-only shared-position advance. No FILE-to-stream fallback.

Opcode12 request words: magic,12,generation,sequence,cloexec0/1,path length10,
effective mode0600,reserved0. Its body is exact `/home/note` padded with zeros
to64 bytes. Validate all fields, binding, role, phase and capacities before
mutation. Malformed requests retire; unsupported authority/semantics reject
without effects using actual local errors. Mark the once-only create attempted
before dispatch, immediately retain its actual completion or failure, and then
acquire/check WRITE4 under the same exclusive loan before publishing a descriptor.

Create replies always have a64-byte header plus64 receipt bytes for validated
opcode12, including errors. Header: magic,status,generation,sequence,remote-fd
on success else0,64,0,0. Successful remote selectors are3..15. Decode into a
temporary and publish only after the complete header/body validates. A partial,
malformed or lost reply never publishes header-only progress or a descriptor.

Receipt words0–7:

| Word | Field |
| --- | --- |
|0| flags: tag0..6 in low3 bits,0x10 means source cleanup present; all other bits zero |
|1| actual validated creation TXG, or canonical0 |
|2| mutation error kind |
|3| mutation error value, signed64 |
|4| raw source input endpoint-close result, signed64 |
|5| raw source output endpoint-close result, signed64 |
|6| post-create error kind, independent of mutation |
|7| post-create error value, signed64 |

Namespace staged bytes are implicitly0: actual AF09 creation validation already
requires zero and this wire cannot encode a nonzero claim. Inactive fields must
be zero. Source closes are raw signed values, not limited errno values; present
`[0,0]` differs from absent cleanup. Bit0x08 (write's offset bit) is reserved.

| Tag | Meaning | TXG | Mutation cause | Post-create cause | Cleanup |
| --- | --- | --- | --- | --- | --- |
|0| NotSent |0| kind1..9 |0| absent |
|1| Reported unassigned failure |0| kind12/value -2147483647..-1 |0| present |
|2| Reported committed failure |any, including0| kind12/value -4095..-1 |0| present |
|3| Reported completed failure |nonzero| kind12/value -4095..-1 |0| present |
|4| Reported unknown |0| kind12/value -5 |0| present |
|5| No validated progress/Unknown |0| kind10/value0 or kind11/raw transport |0| present |
|6| Successful create/open |nonzero|0|0| absent |
|6| Successful create, later open failure |nonzero|0| kind1..12 | present |

Do not narrow tag1's actual remote-error range or discard tag2's anomalousTXG0.
Tag6 with post failure keeps creation successful/TXG intact; it is not NotSent.
An all-zero receipt, tag7, reserved bits or any noncanonical combination rejects.

Cause kind/value to header errno (the existing write vocabulary):

| Kind | Meaning | Value | Errno |
| --- | --- | --- | --- |
|0| no cause |0| only success |
|1| BadFd |0| -9 |
|2| descriptor Full |0| -24 |
|3| Invalid |0| -22 |
|4| Overflow |0| -75 |
|5| Retired |0| -5 |
|6| InvalidCompletion |0| -5 |
|7| Source Invalid |0| -22 |
|8| Source Closed |0| -5 |
|9| Source Full |0| -28 |
|10| Source Protocol |0| -5 |
|11| Source Transport |any signed64| -5 |
|12| Source Remote |-2147483647..-1| same value |

Kinds13–16 are invalid here. Status0 requires tag6/no causes/no cleanup and a
valid FD. Every failure has FD0 and negative status exactly matching the
mutation cause for tags0–5 or post cause for tag6. Use the existing portable
signed-word conversion. Never manufacture a remote cause for a local denial.

## Effect ownership and descriptor publication

Preflight C logical slots, Rust alias/description slots and Client lookup-slot/
token capacity before Create. `open_read_using` already preflights both Rust
tables; use a scoped equivalent for Client capacity if needed. Such preflight
does not guarantee the provider's later lookup succeeds. After successful create,
acquire the WRITE4 reference and perform the infallible table publication under
the original borrow. Keep actual creation outcome/TXG independently of later
acquisition, publication, delivery, write or close outcomes.

Every sent create failure and every post-create failure retires the sole source
once and captures actual endpoint closes. Attempt one typed failure reply if
possible; delivery never reopens admission. Do not add a second explicit handle
close after a primary post-create failure, which would introduce an unrepresented
second cause. If an explicit handle close is itself the primary post failure,
retain that exact cause before source retirement. No rollback or replay.

C retains local NotSent/Remote/Unknown separately. Local NotSent means no FILE
send was attempted and invents no remote receipt. Remote means a complete
canonical receipt; preserve it even if C map installation later fails, recording
that local failure separately. Unknown means any attempted-send partial/lost/
malformed exchange; abort the FILE client and retain local channel-close facts.
Do not overwrite create evidence with subsequent write/close or local cleanup.

Use existing description positions/refcounts and last-alias close; no duplicate
ownership ledger. C may track which remote selectors describe the note writer
for truthful F_GETFL and routed writes, but Rust remains the enforcing boundary.
If needed, a scoped selector-rights bitset follows validated create/dup/close and
is invalid after retirement; no bit can grant server authority or survive reuse.

New scoped dup2 uses existing checked context redirect within one serialized
transaction. Validate the source first; same-FD is a true no-op preserving flags.
Before any effect reject different FILE-to-FILE. Allow traced FILE-to-empty/
terminal and terminal-to-FILE/empty/terminal. Publish success only for known
committed target results. Consume the whole redirect result and contain unknown,
unresolved or consumed failed-close effects; do not translate them into resumed
success. One spare remote selector is required for file alias preparation.
Preserve saved terminal aliases, CLOEXEC behavior and final mode restoration.

## Focused implementation and qualification

Warm writer uses exact9 mutations: bootstrap2, terminfo4, helper ELF1, note
create1/write1. Reader uses original exact0 semantics. Warm operator exception
applies only to the new composition; original cold-only selectors stay closed.
Complete actual type/size16/bytes/EOF/post-stat cold note validation before FD
startup, using READ2 without a new metadata right. No cross-boot PID claim.
The exact warm176/cold70 input bytes and observations are in the approved issue.

The approved [80KiB amendment](https://github.com/gonz0w/Aether/issues/158#issuecomment-6711120030)
selects only this writer/reader Owner through default-off kernel
`native-zsh-home-redirection`; its closed guard requires file-exec/operator.
Admit at most81920 Owner RX bytes; older profiles retain73728. Keep4096
Runtime/workspace,12288 mapped/12280 usable
stack,128 Owner backing pages, application384/engine2048 loader ceilings and all
other grants/worker quotas. Fresh affected parent, Owner, matched C placeholder
and engine fits precede images. Stop/replan on overflow. Keep each operator boot
6000/24000/30000 exclusive ticks,330s workload/360s total/9s stop, first prompt
within60 host seconds,96 requests,9 mutations,64KiB captures and no network.

Before code select positive/negative tests for field/state canonicality, partial
or malformed replies, progress retention, mask/mode/flags, source-level parent/
child/stale/protected-path denial, shared aliases/last-close/stdout+stdin restore,
one attempted create/write and no replay, old profiles and warm9/cold0 closure.
Use actual changed functions and existing bounded runners. No full-host or
repeated65-second/interactive campaign. Required separate source/artifact/run/
result reviews and protected CI remain;141/general peaks/R1 stay open.

Simplicity: reuse AF09 exclusive creation, existing descriptions and checked
redirect. Truncation, unrestricted replacement and a new service are unnecessary
for the current workload. No obsolete path is removed because old profiles
remain qualified compatibility consumers. No new dependency or unsafe boundary
is planned; any necessary unsafe borrow must state its actual lifetime before use.
