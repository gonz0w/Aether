# Opt-in libc FD bindings and shell link boundary — UL-007/081/082

Current follow-on: [armed fork stage/child constructor](FS-FORK-STAGE.md) now
supplies real native park/rebind/startup reconstruction and a complete pinned
shell link. Earlier missing-stage evidence remains immutable; no matching owner
transaction/native execution or whole-fit acceptance is inferred.

Follow-on: Aether has selected serialized owner admission; the additive
[serialized library API](FS-SERIALIZED-COPY.md) and [fork-frame/child predicate](FS-FORK-FRAME.md)
now supply local tested inputs. No complete armed stage/child constructor or
matching selected sys-init transaction is delivered; earlier link evidence remains
unchanged. Source candidates and independent/native acceptance stay separate.

This batch connects the [sole startup consumer](FS-FD-STARTUP.md) and
[placed context](FS-FD-CONTEXT.md) to actual optional libc entry points and a dash
application entry. Sys-init Decision0200 now supplies a matching startup producer
and host Rust-to-C witnesses. Its complete native dispatcher/process transaction
is still absent. This module does not select or replace the old ABI29 runtime.
Do not link both: they export overlapping libc symbols and greeting readers.

## Actual bindings and storage

`fd-libc-bindings.c` places exactly one4952-byte boot/context object in BSS. There
is no automatic4096 buffer, extra FD ledger, heap allocation or worker. Actual
native backing/address/stack/heap/channel/whole fit remains unqualified. Internal
borrows require stable exclusive single-threaded storage; never reset/copy/rebase
an admitted object. Startup calls the actual auxv/int81 entry once; no implicit
startup on first I/O. Pre-start/retired/finished context I/O fails closed.

The private libc hook `__aether_io(op,fd,pointer,count)` supports op0/read,1/write,
3/close. It returns private negative errno without changing caller errno, including
after callbacks/signal restoration. There is no Linux/native syscall fallback for
unknown operations. Reject unknown op-ENOSYS, out-of-range logical FD-EBADF and
null nonempty buffer-EFAULT. Clamp I/O requests to4096; streams legitimately return
one short chunk at most16. This does not loop/replay an unknown write. FILE writes
remain known-EROFS without source I/O; no success stub or wire extension.

Actual exported `open/open64` support O_RDONLY and optional O_CLOEXEC for one
component up to255 bytes in the already delegated file view. Empty/dot/dotdot
reject; slash paths/other flags explicitly EOPNOTSUPP; null EFAULT/too-long
ENAMETOOLONG. No path/root/directory/native authority is inferred. Unsupported
O_CREAT needs no variadic mode read. open64 uses the same bounded contract.

`fcntl` supports F_GETFD/F_SETFD (only FD_CLOEXEC), F_DUPFD and F_DUPFD_CLOEXEC.
Unknown commands including F_GETFL explicitly EOPNOTSUPP and read no nonexistent
variadic argument. `dup` uses canonical duplication with minimum0. FILE duplicates
come from actual file RPC; streams alias the same physical record. `pipe` uses
existing guarded creator and publishes only a validated pair; null pair EFAULT.
`lseek` uses explicit64-bit off_t/context seek; streams ESPIPE. Native constants
come from pinned SDK headers; host tests use their own host headers, not a claim
that platform flag values match. Wire/context flags normalize to0/1.

Libc wrappers return-1/set errno on errors and preserve incoming errno on success,
including when callbacks clobber it. Private errors outside1..4095 normalize to EIO.
Raw hook normalizes those to-EIO while retaining incoming errno. Functions returning
private structured data (`aefd_shell_start/role/snapshot/redirect/finish`) retain
their existing private/count/receipt contracts; snapshot/redirect/finish preserve
errno. Snapshot is inert data, not native copy/exec authority. Context operation
masks cover all source/alias changes and compound private redirect.

Public `dup2` explicitly returns EOPNOTSUPP for all inputs, with no FD/source effect.
The existing structured redirect is bounded and non-atomic; it may need spare
remote capacity and can leave a hole after a consuming error. It cannot be renamed
into a complete POSIX replacement/error-preservation contract. `aefd_shell_redirect`
exposes it only under its explicit private receipt API. A general POSIX shell
redirection claim requires stronger semantics or a reviewed restricted shell adapter.
No SIGPIPE synthesis, job control, broad pathname/TTY or POSIX conformance claim.

## Wait and exit

The existing raw `__aether_waitpid` client uses unchanged32-byte opcode68 with
PID@4/options@8, zero tail; supported parent slot1, pid-1 or positive, options0 or
WNOHANG. Hold one guard across request/reply. Validate positive canonical child2..4
PID/epoch1..15 and exact specific selection, zero only for WNOHANG, only known
negative ECHILD, zero unused status/reserved bytes. Publish status only on complete
validated positive reply (NULL discards it). Syntax never proves child membership:
the authenticated dispatcher owns records/terminal reservation/collection.

Short/unknown/malformed replies retire transport without status publication or
replay; all32 partial reply prefixes are exercised. Active/busy rejects EBUSY before
retired handling so reentry cannot abort an in-flight transaction. Raw helper
preserves errno; pinned public-fork waitpid/wait3/wait4 perform their normal public
conversion. Host tests execute this new raw client; complete native wait/process
ownership remains unrun. Attempt budget16384 is not a timeout; owner watchdog/stop
is still required around native waits.

`__wrap__exit` calls terminal cached context finish. Only a known clean receipt
preserves requested exit status; unknown/remaining/resource/raw-close error exits141.
Native restoration failure retains fail-stop125. Actual application `__wrap_main`
requires sole startup success/role1 before invoking dash main with sh,-i,+m, then
uses wrapped exit. This is a linked-component entry, not a readiness report or
accepted native boot. No executable is delivered while process stage remains absent.

## Concrete process-stage blocker

The complete link combines the new17 production C units, all32 pinned dash
objects, CRT/libc, public fork/_Fork/TLS-rebind/waitpid/wait3/wait4 and memory adapter
from the sealed ABI29 v2 closure. It fails on exactly **__aether_fork_stage** from
_Fork.c. New startup/libc/wait/exit/application symbols resolve; no old runtime,
ignored undefined symbol or unsupported successful process stub is included.

The old stage emits opcode83/length64 plus the old installed table before native
copy. That cannot preserve the new128-byte tagged FILE/PIPE/CONSOLE map, file
connection generation, pipe history or canonical alias/close-on-exec state. Reusing
it would silently discard required state. The native copy/rebind mechanism alone
cannot authenticate/clonally publish those service-owned descriptions.

Matching next contract must specify authenticated parent quiescence/freeze and
128-map/source/history validation; actual file-description/offset alias and stream
holder cloning; child slot/epoch/channel/file-generation/TLS rebind and new sole
304-byte greeting; known copy refusal rollback and unknown-outcome retirement;
child readiness/terminal settlement and unchanged parent state. Immutable image
lookup/loading and failed-or-unknown-exec preservation also remain prerequisites.
No matching native producer/consumer/dispatcher transaction for these facts is
provided by Decision0200's pure startup encoder/child-record core. Do not zero an
inherited context or send the old snapshot to manufacture successful fork.

This is the stopping point for this integration run. Sys-init must coordinate the
matching owner transaction; userland can then implement/select the stage against
that contract and complete the linked shell. Native dispatcher/readiness/shutdown,
full fit and fresh Aether commands/errors/cleanup remain separate acceptance gates.
Public dup2 and broader shell compatibility remain explicit additional limitations.
No new kernel primitive is asserted necessary solely by this link failure.

## Reproduction and evidence

```sh
python3 -B experiments/filesystem-service/check-fd-libc.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-fd-libc.py
python3 -B docs/quality/check.py
```

Run from repository root with pinned offline inputs. The experiment checks78 new
host scenarios/five compiling semantic omissions plus803 startup/175 context/193
native-call/482 live C/Rust cases and23 retained controls. Actual wrapper bodies
compile with test-only names after host system declarations; the target object
must export real libc symbols and exactly one4952 BSS boot object. Host tests
substitute only the native entry/calls, not context/startup/wrapper logic. Separate
processes keep singleton state fresh. Actual exit23/unknown141 host children and
errno clobber are exercised; scripted native/source replies are not target authority.

Seventeen strict C17 target objects/relocatable link/imports/static frame/layout
are build-only evidence. Full shell link failure is accepted as a recorded block
only for the exact missing fork-stage symbol; any other error fails qualification.
The old v2 outer/bundle pins verify before consumption and afterward; no SDK/dash/
source tree is copied or changed. Clang-format/UBSan and retained Rust/Clippy/unsafe,
actual minimum/current Python, owned60s compile/30s suites/16MiB streams, all failed/
passing attempt preservation and streaming-readback cleanup apply. See
[evidence](../evidence/filesystem-fd-libc-2026-10-22/README.md). Independent owner/
reader and full UL/M3/R1/release acceptance remain pending; research/build is not
native runtime completion.

## Explicit root-path selection —2026-10-23

AEFD_PATH_WIRE selects the separate AEFP0001 codec and permits canonical1–255-byte
root-relative/single-leading-slash reads in a matching owner build. Default
AEFD0001 and slash rejection remain unchanged. Invalid canonical paths fail locally
before FILE I/O; write/create/append flags still fail explicitly. This private
bridge does not add POSIX CWD/normalization/symlinks or change getcwd ENOSYS.
[Path contract](FS-ROOT-PATHS.md) and
[actual complete-owner checks](../../../sys-init/docs/decisions/0221-root-path-owner.md)
keep native runtime, writable home and general persistent exec separate. Public
dup2 remains unsupported; do not infer redirection acceptance from path reads.
