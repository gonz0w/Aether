# Selected Zsh filesystem integration

[Issue137](https://github.com/gonz0w/Aether/issues/137) completed the first real
Zsh prompt, one builtin and normal exit/export/cleanup through
[PR138](https://github.com/gonz0w/Aether/pull/138). Its scoped fit and delivery
decisions remain specific to that checkpoint.
[Issue143](https://github.com/gonz0w/Aether/issues/143) completed the fixed
parent/helper checkpoint through [PR144](https://github.com/gonz0w/Aether/pull/144):
real helper exit7, parent prompt return, checked final exit/export and three
reclamations. [Issue145](https://github.com/gonz0w/Aether/issues/145) adds the fixed
helper write with independent cold readback described below. General filesystem
execution and redirection remain open. The canonical
[execution policy](../../docs/policy/execution.md#selected-real-zsh-filesystem-composition-2026-11-02)
records the approvals and limits.

## Retained pre-trial offline evidence for issue137

The following measurements and preparation limits describe that earlier
builtin-only candidate. They do not qualify the new external-command composition.

The selected source is implemented and separately reviewed. The fresh Zsh/tinfo
executable is1,274,352 bytes and fits314 pages including the existing mapped stack;
its initialized TLS remains4 bytes. The Rust Owner uses44,376/49,152 code bytes,
3,408/4,096 Runtime bytes, the existing4,096-byte workspace and6,152/8,184 bytes
under the unchanged conservative compiled stack inspector. Real producer-bound
namespace epoch and in-place construction regressions cover the two corrected
integration defects. These measurements are offline fit, not target execution.

Only selected Zsh `execute()` receives a derived-source noinline attribute. This
keeps its large external-command scratch frame out of the builtin dispatcher;
actual local dispatcher frame is17,080 bytes. The separate external helper still
uses49,368 bytes and is outside this builtin-only trial. No PATH_MAX, feature,
heap, stack limit or upstream source tree is changed. Complete stack/heap demand
and actual whole-session request use remain unmeasured; partial frame sums,
remaining pages and the expected33-request model cannot substitute for them.

The installed Screen4.00.03 passed one owned host-PTY preflight: actual VT100
clear/home/cursor placement in an80x24 hardcopy, exact input bytes, raw8-bit/no-flow
settings and normal exit with known process cleanup. This does not qualify the
future QEMU serial PTY or actual Zsh. The fixed proposed command input is34 bytes
including CR; old terminal-fixture input lengths are not reused as its oracle.

Cam's [diagnostic evidence decision](../../docs/policy/execution.md#fixed-diagnostic-evidence-decision-2026-11-02)
replaces the complete pre-image peak-proof prerequisite for this fixed builtin
experiment. Completed actual route/known-defect/structural checks plus a guarded
workload may establish scoped fit under all existing limits. Complete/exact/general
peak demand remains unclaimed. Fresh image/media/consumer review still precedes
execution; no image, guest or successful workload is claimed here yet.

The private development workspace provides these bounded recipes after their
exact source/tool freeze and lead release:

```sh
python3 -B tools/zsh-target-fit.py --filesystem
python3 -B tools/zsh-owner-fit.py
python3 -B tools/zsh-screen-probe.py
python3 -B tools/zsh-witness.py INPUT_DEP MANIFEST_SHA SEAL_SHA FREEZE_JSON FREEZE_SHA
python3 -B tools/zsh_run.py prepare WITNESS IMAGE_REVIEW_SHA
python3 -B tools/zsh_run.py run PROPOSAL PROPOSAL_SHA PEER_REVIEW PEER_SHA DECISION
```

The first two retain300-second aggregates and180-second children; the host frontend
probe has30 seconds total. Image and disposable-media preparation launch no guest.
Only explicit `run` selects one reviewed proposal under the recorded authority:
120 seconds total,60 seconds including the shared9-second stop,64KiB raw UART and
one attempt. A changed candidate needs diagnosis, review and fresh media. Screen's
private control FIFO and live process identity, actual PTY settings and rendering
are checked before the one34-byte input submission; closed Screen diagnostic pipes
do not imply server exit. QEMU pipe EOF remains failure. Compact exact inputs/commands/results/failures remain
private; public source alone lacks the full SDK/recipe environment. Temporary
executables/maps/objects are retained only through review/checkpoint, then removed.
Current dependencies stay separately pinned. One interrupted earlier host test
has unknown child-cleanup evidence and remains quarantined rather than reused or
counted as passing; later completed checks retain their distinct identities.

## Fixed diagnostic observation

The selected diagnostic build adds `AEFD_ZSH_DIAGNOSTIC` to the filesystem
provider only. One four-byte BSS observation requires a real `tgetent` return1,
no failed `tgetent`, and a positive authenticated terminal read while real Zsh
`zleactive` is1 before and after the read. An otherwise-zero app exit becomes144
if that observation is missing; cleanup failure141 retains precedence. This
observation adds no TLS, allocation, syscall or capability.

After both checked normal exits, namespace disconnect/export, backing reclaim
and admission-mode restoration, the Rust Owner writes one exact49-byte row:

```text

AETHER ZSH OWNER v=1 requests=NN mode_cleanup=0
```

`NN` is the actual two-digit whole-session count14..96. The row includes its
leading and trailing LF, uses the existing workspace and bounded console writes,
and records confirmed partial prefixes without replay. `mode_cleanup=0` records
the Owner's checked restoration to admission mode; it does not establish that
Zsh explicitly requested restoration. The matched expected-six engine normal
exit and export checks supply mutation completion evidence; this row invents no
mutation count. Default providers and old machine records remain unchanged.

The existing `native-zsh-terminfo` selection omits routine successful STORAGE
WAIT park/wake rows, CLOCK park rows and ordinary CLOCK deadline-timeout rows.
Normal deadline expiration still returns `-110` and its elapsed value; registration,
completion and scheduling are unchanged. Nonzero channel-wait diagnostics and all
fault, panic, admission, terminal, cleanup, Owner, halt and PASS rows remain, as do
raw application terminal bytes. Other profiles keep their exact existing traces.
The64KiB raw UART ceiling is unchanged; quiet routine output is not completion or
hang evidence. The focused source checks and actual-emission fixture are in
`tests/test_native_zsh_terminfo_trace.py`; they do not launch a guest. Run the
source checks from the repository root:

```sh
python3 -B -m unittest discover -s tests -p test_native_zsh_terminfo_trace.py -v
```

## Authority and lifecycle

The existing Rust Owner retains the sole AF09 namespace endpoints and HOME15/root3
bindings. App preflight and commit observe untouched namespace channels; the app
receives process endpoints only and waits for FD startup. The Owner then consumes
the two greetings once, creates and reads back the exact VT100 entry, and publishes
startup only after checked provisioning. Four provisioning plus two engine bootstrap
mutations use six of nine. The twelve initial service requests, later probes,
FILE operations and teardown share the original96 requests without renewal.

Keep the actual .terminfo directory reference and namespace epoch until healthy
teardown; no reconnect, rebind, second ledger or namespace mutation after
provisioning. Contain an admitted app if provisioning cannot make it ready. Retire
access before closing the held view once and performing checked disconnect.
Fatal/unknown Client outcomes preserve their consumed close receipts; never replay
close, write, disconnect or an operation whose effect is uncertain.

The only directory name is `/home/.terminfo`. The only entry names are the literal
`/home/.terminfo/v/vt100` and `/home/.terminfo/./v/vt100`, resolved to the same
real allowed file. General dot/dotdot rejection stays unchanged. Names, advisory
UIDs and opaque view keys confer no native authority. Independent opens have
independent positions; descriptor duplication shares the existing description.

## Closed startup and FILE wire

The selected C macro is `AEFD_ZSH_FILESYSTEM_BINDINGS`, and the Rust cfg is
`native_zsh_filesystem`. The macro includes the existing canonical terminal chain
and excludes general PATH/DUP2/CWD/WRITE/FORK/EXEC selections. Old304-byte startup
variants and ordinary profiles remain unchanged.

Selected startup is336 bytes: `AEFDB008` with `AEFDT008`, factory0, and the existing
first304-byte terminal/identity/MODE layout. Bytes304–319 contain four little-endian
u32 credential labels1000;320–323 source-kind1;324–327 flags0;328–335 reserved0.
Validate the entire record before publishing context or getters. These labels are
unauthenticated development metadata. They are not accounts or permission grants.

AEFP0004 uses the existing64-byte header, process generation/sequence and4096-byte
payload maximum. FILE selectors are3–15. Existing ops1–6 retain open/read/seek/dup/
close/CLOEXEC semantics; opcode7 and unknown operations reject and retire. The
selected additions are:

| Opcode | Arguments | Successful result/body |
| --- | --- | --- |
|8 ACCESS | `[mode, path_length, 0, 0]`, mode0 or4; padded allowed entry name | result0, no body after real read-reference acquisition and checked close |
|9 GETCWD | all zero | result0, length2, `/` plus NUL, after retaining the actual root cwd |
|10 DIRECTORY | `[0, path_length, 0, 0]`; padded exact allowed directory name | result0, length32: four little-endian u64 values described below |

DIRECTORY returns typed directory-kind2, actual size, a nonzero opaque held-view
key and actual namespace epoch. This wire kind is explicitly mapped from AF09's
directory kind1. The key identifies this single immutable held view within this
exact authenticated app binding; a local constant key is sufficient within that
scope. It is neither a POSIX inode/device identity nor an invocable capability.
No request accepts that key as authority. Every cache build/rebuild revalidates
the same live reference through existing opcode6 before returning the observation.
Stale, retired, unknown or non-directory results publish no valid view.

All body padding to64 bytes is zero. Read the common16-byte prefix once, then
classify exactly32-byte selected TTY/MODE or64-byte FILE headers and their validated
body. One operation is outstanding. Check the exact admitted app generation,
sequence, live slot/epoch and operation fields before effects. Wrong versions,
reserved bytes, lengths, partial/unknown frames and unknown operations retire;
never resynchronize the stream or replay an uncertain request. Well-formed
unapproved names fail truthfully before unauthorized traversal.

## Selected application consumers

Real pinned musl FILE buffering continues through the sole descriptor context.
Preserve raw/libc errno, short prefixes, EOF, seek and once-only finalization.
Publication completes while the whole-operation mask is held; context is idle
before restoring the saved mask and permitting handler reentry. No second4096-byte
buffer or nested guard is introduced.

Port only selected ncurses `db_iterator.c` directory probe/cache/equality to the
typed held view. Keep actual existence/type checks and duplicate elimination.
Do not fabricate successful full or partial libc stat. Keep pristine upstream
bytes and record the small derived patch's exact source/output provenance.
Zsh's separate stat probes remain truthfully unsupported; real held-root GETCWD
supplies its fallback. General filesystem identity and METADATA16 remain absent.

After checked startup and before real Zsh bootstrap, checked environment setup
sets `TERMINFO=/home/.terminfo` and `PS1=AETHER-ZSH> `. The kernel retains its four
slots `TERM=vt100`, `LC_ALL=C`, `HOME=/`, `PWD=/`; no inherited terminfo/module/
startup-script override is admitted. Preserve required static ZLE/complete/compctl,
multibyte support, consumed initialized TLS and nonrecursive exit finalization.

The kernel selection is default-off `native-zsh-terminfo`; it requires the exact
large application/MODE/SIGINT closure. Namespace custody remains in the Owner,
with selected AENAP002 admission and no namespace auxv transfer to the app.
All original grants, pages, stacks, heaps, channels, requests, mutations and
watchdogs remain unchanged. Offline fit is not runtime resource sufficiency.

## Verification boundary

Focused tests cover actual startup/framing/providers, positive and malformed/stale/
partial/fatal cases, old-profile compatibility and semantic omissions. Actual
new Zsh, Owner, expected-six engine and kernel artifacts need matching route,
layout, resource/request and consumer review before the bounded native trial.
The proposed real trial runs `zsh -f -i +m`, real tgetent/ZLE and a builtin marker,
then normal exit, mode restoration and clean export on disposable no-network
media. The selected VT100 frontend needs real PTY/input/termination checks;
serial byte capture alone does not qualify an emulator. No current result here
claims a prompt, login, external command, cold persistence, package or R1 gate.

## Selected parent/helper extension

The [owner-approved issue142 design](https://github.com/gonz0w/Aether/issues/142#issuecomment-6589424662)
selects the separate issue143 implementation. `native-zsh-external`,
`AEFD_ZSH_PROCESS_BINDINGS` and `native_zsh_process` name its closed kernel,
consumer and Owner selections. They extend the real terminfo/MODE parent only
for one child at a time. Existing selections keep their original bounds.

The [issue143 capacity decision](https://github.com/gonz0w/Aether/issues/143#issuecomment-6591806304)
allows only this external selection to use73,728 Owner RX bytes and three mapped
stack pages (12,288 bytes,12,280 usable). The stack is `[0x7ff000,0x802000)`
RW/NX, zeroed, with absent guards at0x7fe000/0x802000. ABI31 and
RSP0x802000-8 stay unchanged. Runtime/workspace remain4,096 bytes each; maximum
Owner mappings are18 RX+3 stack+2 data=23 of128 pages. Total backing stays11,520
pages. The unchanged AENFS006/AENMX011 magic cannot choose this allowance;
explicit kernel selection uses `parseExternalApplication`, while old
`parseApplication` retains49,152 bytes and the two-page stack. The app's limits,
channels and execution/capture bounds are unchanged. A fresh matched Owner fit
and separate review remain required. The scoped workload-fit and delivery
conditions are recorded in the execution policy linked above.

Pure controls run from the repository root with
`python3 -B -m unittest discover -s tests -p test_zsh_owner_capacity.py -v`.
The test also supplies actual kernel-body fixtures; their bounded compiled
results are separate from pure checks and native qualification.

The fixed target is the existing `/inputs/helper status` test executable,
owned image C003, with real exit7. At the actual +m prompt,
`(exec -c /inputs/helper status)` forks once through Zsh's real synchronization
pipe, executes with two arguments and a non-null empty environment, and returns
to the parent. A subsequent `print -r -- $?` must report7 and a real prompt.
The image selector is not an installed OpenZFS path or general utility claim.

The Rust Owner retains the sole AF09 Client/epoch, HOME15/root3 and terminfo/FILE
custody. One stable mutable context exists per process. Use a new closed selected
fork/exec frame containing the full336-byte context and checked parent/child
identity; never compress it into the older304-byte snapshot or reuse its magic.
Retain shared descriptions, positions, pipe endpoints and CLOEXEC flags through
checked admission/rebind. Rebind all child-local pointers and endpoints under
the existing saved-mask guard; child pending signals start empty. An exec refusal
preserves the old child image/descriptors; close CLOEXEC only after known commit.

Only the admitted selected parent can create the one child. Construct its native
admission/clock identity from its actual slot/generation, with namespace fields
remaining kernel custody provenance rather than exported endpoints. Preserve
exact Owner/A001/unadmitted launch guards and selected AENAP-startup suppression.
Exec preserves native process generation and the child-local lifetime binding.
Child `tty_signal_owner_generation` is null, not numeric0. No new syscall or
capability kind and no global mutable owner/table is introduced.

The terminal core keeps its existing four aliases. The authenticated Owner proxies
child READ/WRITE through retained descriptions, without inventing a child Caller
for the single-caller terminal core. Parent MODE/control/private restore and the
existing SIGINT target remain parent-only. An explicit Parent/Child/Contained
read lease excludes competing consumers. This helper performs no input; child
canonical/ISIG reads reject EOPNOTSUPP before consumption. This is not general
POSIX terminal inheritance or child VINTR/job-control support.

Use the pinned target's existing waitpid branch (HAVE_WAIT3 absent, HAVE_WAITPID
present) and its actual Owner route. Parent-scoped child selectors and only
WNOHANG1, WUNTRACED2, WCONTINUED8 are admitted; no stop/continue events exist in
this closed profile. Report real encoded exit status, truthful ECHILD/no-change
and untouched status output when no status is returned. No fake rusage: existing
getrusage remains ENOSYS without buffer writes and supplies no usage evidence.
Actual generation-checked SIGCHLD/sigsuspend supply notification and waiting.

After a real child terminal, reserve/cache status, deliver the reply, mark known
collection, reconcile transport/descriptors/native reclaim, then restore Parent
read lease. A prompt READ arriving during reconciliation remains pending until
that lease returns. Do not require reclaim before status delivery, return false
WNOHANG0 for cleanup delay, lose notification or expose another reader. Unknown
delivery/copy/exec/cleanup contains the session without replay. Final parent exit
still restores mode and closes/exports/reclaims the actual session.

Before any image, correct and measure the known external execute frame beyond
48KiB without increasing stack or reducing PATH_MAX. Fresh parent/helper/Owner
code/runtime/workspace/stack/heap/backing/TLS/request fits and affected semantic
checks remain required. Only exact reviewed artifacts/media and known-cleanup
selection may enter a later bounded guest. Issue137's fit and full-host delivery
exceptions do not transfer; issue141's coverage/UNKNOWN history stays separate.

### Parent/helper selected startup and frame serialization

The process selection uses full336-byte `AEFDB009`/`AEFDT009` snapshots. It retains
all four bytes of every binding, including kind5's nonzero duplex-description tag
in byte3. Do not convert that tag into the old three-field Rust Binding type.
Terminal labels remain0x7a000001/0x7a010001/0x7a020001; a child receives proxy
labels on its authenticated process connection, never another terminal-core Caller.
The seven-source/two-pipe histories and existing tagged pipe references remain.
A freshly admitted child/helper FILE client begins at sequence1 on its new
checked map/channel generation; the parent retains its existing next sequence.
The first copied child retains process counter1 and sends exec sequence2.
Only parent slot1 or child slot2 is valid in this selected representation.

Snapshot offsets0..295 retain the complete identity/map/source/history layout.
At296 the parent has pipe factory0x76050001, and at300 parent MODE control is
0x7d000001. Both fields are0 for the child. Credential bytes304..335 retain four
u32 values1000, source-kind1 and zero flags/reserved bytes. The whole startup,
including exact identity, role, authenticated channel generation, all bindings,
sources and padding, validates before publication. Native process generation
and map/channel generation remain separate checked identities.

| Frame | Exact extent and layout |
| --- | --- |
| Fork `AEZFK001` |368 bytes:32-byte operation header, then the complete336-byte parent snapshot |
| Exec `AEZEX001` |672 bytes:32-byte operation header, complete336-byte child snapshot,32-byte padded path,272-byte argv/env representation |
| Parent disposition `AEZFR001` |32 bytes:magic, sequence, actual slot2 PID or bounded negative known refusal, zero reserved word |
| Child ready `AEZFC001` |32 bytes:magic, sequence, actual slot2 PID, zero reserved word |
| Exec refusal `AEZER001` |32 bytes:magic, sequence, bounded negative refusal, zero reserved word |

The operation header contains8-byte magic, u32 version1, u32 total extent, u64
sequence and u64 reserved0. Sequence0 and u64 maximum reject; counter reservation
and exhaustion never reset or replay. Snapshot begins at32; exec path is368..399
and arguments400..671. The existing272-byte arguments format retains u64 argc
1..4, u64 envc0..4 and eight32-byte string slots; each used string has a terminator
within31 bytes and zero tail, and every unused slot is zero. This is bounded
representation, not permission for arbitrary paths, environments or executables;
the selected workload and Owner admission still require their exact contract.

The selected C `fd-zsh-process` and Rust `zsh_process_frames` codecs are inert
validators/serializers. Rust uses a borrowed full snapshot view so no alias tag or
advisory field is lost. Invalid decode publishes no view or sequence; encode
validates before output effects. Child correspondence preserves exact binding,
source, pipe-history and credential bytes while requiring its actual child
identity, distinct map generation, no MODE/factory authority and distinct native
endpoint observations. Complete runtime fork/exec/controller/lease wiring and its
native qualification are separate acceptance; codec tests do not establish it.
Existing008 and older304-byte formats and their control paths remain unchanged.

The selected C provider now stores one `aefd_fork` aggregate in
`fd-zsh-external.c`; both the external-startup getter and the fork getter borrow
that same `boot`. The consumed initialized entry guard remains the sole4-byte
TLS object. `fd-fork-stage.c` captures a complete snapshot while holding the
existing mask, sends368 bytes, authenticates the correlated parent disposition,
and rebuilds child-local pointers only after the actual new-grant rebind.
`fd-exec.c` sends672 bytes and accepts only an exact known negative refusal after
raw thaw-11; an unknown result retires the context. These C paths do not implement
the Rust Owner's copy/commit, shared-description or terminal lease policy.

The parent keeps its mutable `zsh -f -i +m` argument storage. A helper provider
selects `AEFD_ZSH_HELPER_ENTRY` with `AEFD_ZSH_PROCESS_BINDINGS` and external
startup, omits the parent diagnostic, and adds `fd-zsh-helper-entry.c`. That entry
consumes its actual336-byte startup, requires role2, publishes native READY, and
passes the CRT's actual argc/argv to real main before the existing checked exit.
It supplies no replacement argument or environment record. Both providers add
`fd-zsh-process`, `fd-fork-stage`, `fd-fork-native`, `fd-exec` and `fd-exec-native`
to the filesystem provider set; neither links the legacy `fd-fork-frame` codec.
The strong `waitpid` definition in `fd-libc-bindings.c` uses the actual Owner68
route; its raw helper preserves caller errno, copies status only for a fully valid positive
reply and rejects other flag bits, child slots and malformed reply bytes.

`fd-zsh-runtime-tests.c` is a focused controller fixture against the actual C
providers. It covers short transfers, fresh helper refusal paths, pipe creation,
CLOEXEC and duplex-tag inheritance, child-local pointer rebind, stale receipts,
exec argument/environment serialization and refusal containment, wait flags and
status-output preservation, masked reentry, and real checked helper finalization.
Its injected native observations are host qualification, not native execution.
The independently linkable codec fixture remains `fd-zsh-process-tests.c`.
The matched Rust controller tests, actual linked resource fits, separate review
and approved fixed native trial are recorded in issue143 and PR144. Fresh
candidates still require matching fits and reviewed image/media before execution.

### Selected parent/helper completion observation

Only the external profile uses this exact row, with leading and trailing LF:

```text
AETHER ZSH OWNER v=2 requests=NN child_status=1792 exec_ready=1 child_reclaimed=1 parent_lease=1 mode_cleanup=0
```

NN is the actual14..96 service request count. Child status1792 is the actual
encoded normal exit7 reserved and delivered through the wait reply; it must
agree with the real child terminal. `exec_ready` requires the matched C003
receipt, publication and fresh helper readiness. Reclaim, parent read lease and
mode cleanup report completed phases. Missing or unknown facts contain the
session instead of emitting this success observation. No capability or pointer
is printed; the older v1 profile retains its exact row.

The fixed external trial submits `(exec -c /inputs/helper status)`, observes the
child terminal and reclaim followed by a parent prompt, then submits
`print -r -- $?` and requires standalone7 plus another prompt before `exit 0`.
Each input submission is once-only; unknown submission or cleanup stops without
replay. Supplied UART controls are synthetic and cannot establish execution,
image association, actual frontend/input or known process cleanup. Fresh linked
fits and separately reviewed image/media still precede any guest.

### Qualified fixed helper checkpoint

The actual issue143 trial passed in34.169s with33/96 Owner requests. Zsh
collected normal helper status7, printed7 and returned to its prompt, then
completed parent/engine normal0 exit and export. All21 cleanup records and three
reclamations completed; mode cleanup was0 and halt2884/6000ticks. Actual
Screen/PTY/input and known host cleanup were separately reviewed.

This is the [explicitly approved fixed-workload scope](https://github.com/gonz0w/Aether/issues/143#issuecomment-6591806304).
[Issue141](https://github.com/gonz0w/Aether/issues/141) retains full-host coverage;
general peaks, arbitrary exec, child job control, login, persistent shell writes/
reboot readback, packages and R1 retain separate gates.

## Selected fixed home write

[Issue145](https://github.com/gonz0w/Aether/issues/145) extends the held helper
with the [approved scoped design and gates](https://github.com/gonz0w/Aether/issues/145#issuecomment-6594800206).
At the real prompt, the fixed input is `(exec -c /inputs/helper home-write)`,
then `print -r -- $?`, then `exit 0`. Each line ends in CR; the staged input
is58 bytes in total and is submitted once at the corresponding prompt boundary.
The new helper opens existing empty `/home/probe` with O_WRONLY, writes exactly
16 bytes `AETHER-ZSH-HOME\n` once and closes once. It returns0 only after a full
write and a known successful close. It does not create, truncate, append or retry.
The old `status` helper and its exit7/v2 observation remain separate.

`AEFD_ZSH_HOME_WRITE_BINDINGS` and `native_zsh_home_write` select AEFP0005 on
the existing process profile. Rust keeps sole namespace custody. Admission
requires the exact committed helper generation and actual READY publication;
parent, pre-exec, stale, wrong-path and wrong-mode requests reject before effects.
Existing allowed FILE operations retain their fields, DIRECTORY remains10 and
reserved7 remains denied. The selected additions are:

| Opcode | Arguments | Successful result/body |
| --- | --- | --- |
|12 fixed home open | `[cloexec, 11, 0, 0]`, exact padded `/home/probe` | checked WRITE-only FILE selector after actual empty-file lookup |
|11 checked write | `[fd, 16, 0, 0]`, exact padded fixed payload | count16 and the existing64-byte correlated mutation receipt |

Do not enable historical AEFW0001 OPEN_HOME10 on this dialect. Retain completed,
short, failed and unknown write/close outcomes across reply loss and cleanup;
only known success advances position. A known successful close clears the local
write-fd marker before that number can be reused readonly. A failed selected
close retires the client after retaining its status, so finalization cannot replay
it. Unknown effects contain; neither retained commit nor local staging is success.

After real helper0, checked wait/collection, child reclaim, restored parent lease,
normal parent/engine exit, export and mode restoration, the selected Owner emits
this exact row with leading and trailing LF:

```text

AETHER ZSH OWNER v=3 requests=NN child_status=0 exec_ready=1 child_reclaimed=1 parent_lease=1 write_bytes=16 write_closed=1 mode_cleanup=0
```

`NN` remains the actual whole-session count14..96. The new engine requires exactly
seven completed mutations within the unchanged9-mutation limit. Other profiles
keep their old counts/rows. The existing external kernel composition and all
Owner/application/engine, time, request, capture and no-network limits remain.
Fresh affected parent/helper/Owner/engine fits and separate review precede a guest.

Independent pristine and recovery readers use fresh readonly original OpenZFS
imports. Recovery checks the actual file bytes and EOF, the full terminfo tree,
the real1268-byte VT100 hash, metadata/ACL/link/time rules and complete allocated
object inventory. Both preserve the original file/data/metadata checks. Only clean
readonly shutdown and runtime health permit publication of40 bytes: the original
metadata digest32 plus `ZSHPR001` or `ZSHWR001`. Compare every digest byte across
roles. Eight-byte scalar framing occupies the existing selected320-byte capture;
other slots/defaults remain256. Reader code never exports the pool.

Public pure reader checks run from the repository root:

```sh
python3 -B -m unittest discover -s tests -p test_home_zsh_reader.py -v
```

Private bounded recipes use `tools/zsh-target-fit.py --home-write`,
`tools/zsh-owner-fit.py --home-write` and the closed `--home-write` witness/run
selection. Pure checks and offline fits do not qualify persistence.

The fixed issue145 native checkpoint passed: real Zsh launched the helper, it
completed16 bytes and close, Zsh printed0 and returned to its prompt, then the
parent and exact-seven engine exited/exported normally. The35.657-second writer
used36/96 requests, restored admission mode and completed21 cleanup phases and
three reclamations. All host holders and finite clients stopped cleanly.

The31.319-second independent cold-reader cohort also passed. Both fresh original
providers completed all three reader generations and cleanup; the recovery role
verified the exact payload/EOF, terminfo asset/tree and metadata/inventory. The
full preserved original-metadata digests matched, and each disk remained byte
identical before/after its reader with intact outside-region canaries. These are
fixed-workload results, not general resource peaks or assembled-system acceptance.
Fresh parent/helper fits are318/28 pages; Owner RX71,632, Runtime4,056 and
conservative stack9,712 remain within the approved limits. The linked reader
capture-profile growth is0 bytes, within16KiB. The explicit issue145 checkpoint
exception leaves full-root coverage in issue141; login, arbitrary redirection/
exec, packages and R1 retain their own gates. Delivery and exact source identity
are recorded in issue145.
