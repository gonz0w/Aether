# Selected Zsh filesystem integration

[Issue137](https://github.com/gonz0w/Aether/issues/137) owns implementation and
qualification. Cam approved this scoped design on2026-11-02; the canonical
[execution policy](../../docs/policy/execution.md#selected-real-zsh-filesystem-composition-2026-11-02)
records the answer. The contracts below are selected implementation requirements,
not evidence that a prompt or runtime qualification has passed.

## Current offline evidence

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
