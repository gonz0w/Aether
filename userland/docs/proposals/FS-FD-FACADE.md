# Typed C file facade and live host integration — UL-007/081/082

The opt-in `fd-facade.c` adapts the [C file transport](FS-FD-CLIENT.md) into typed
component-open/read/seek/dup/close/cloexec calls. The caller supplies an explicit
trusted file-client context. This is the file-only C seam for the next shell
integration; it does not replace libc symbols or the linked ABI29 shell's FD table,
startup, pipe, console, process or exec wire. No old candidate, native authority,
quota, standards/SDK pin or sibling implementation changes.

## File-only C API

Include `experiments/filesystem-service/fd-facade.h` and link `fd-facade.c` plus
the exact selected `fd-client.c`/headers. All calls take `struct aefd_client *`.
The caller must already have initialized that client with authenticated endpoints,
nonreused generation and dedicated4096-byte workspace. The facade acquires no
native authority. It creates no local FD ledger, second Owner/SPA or pathname
resolver. In particular a POSIX FD number does not decide whether this context
owns a file, pipe or console. The consuming runtime must route by truthful binding
under an explicitly agreed startup/descriptor contract.

| Call | Inputs / nonnegative result |
| --- | --- |
| aefd_file_open | pointer/length component1–255, cloexec0/1; returns file FD3–15 |
| aefd_file_read | file FD3–15, valid output range/count0–4096; returns bytes copied |
| aefd_file_seek | file FD, signed64 displacement, whence0 set/1 current/2 end; returns signed64 nonnegative position |
| aefd_file_dup | file FD, minimum0–15, new cloexec0/1; returns FD3–15 |
| aefd_file_close | file FD; returns0 only after validated close response |
| aefd_file_set_cloexec | file FD, flag0/1; returns0 only after validated flag response |

Negative return values are private errno, not POSIX libc `-1/errno`. Known semantic
errors pass through unchanged, including missing=-2, bad live binding=-9 and
read-denied=-13. Local invalid inputs map to -22 with no request; retired/unknown
transport maps to -5 and never reconnects/replays. There is no write/create/append,
full pathname/cwd/stat, dup2, F_GETFD, pipe/console fallback or exec success stub.
No result publishes native copy/admission/settlement or immutable image authority.

The facade inherits the transport's valid/disjoint storage, serialized access,
nonreentrant callbacks and lifetime obligations. Read output may be NULL only for
count0. Count greater than4096 rejects rather than silently truncating or splitting
a request. The result must fit the bounded wire contract. Positive read bytes are
copied from the private workspace only after the complete header/body/padding is
validated. Errors and EOF leave the caller's output unchanged; successful short
read leaves bytes beyond the returned count unchanged. A zero read still makes
an actual file RPC to validate the process/FD; it is not local unconditional success.
Signed seek is encoded as the existing wire's two's-complement64-bit field.

The internal workspace still follows the transport's exchange/abort rules. A read
rejected before calling the transport (NULL output with nonzero count or count
above4096) does not clear a preceding valid workspace result. No new4096-byte
automatic runtime buffer is added. Pointer validation, actual endpoint authority,
individual callback deadlines, process freeze/copy and native lifecycle remain
trusted caller/owner requirements. A C function interface is not an enforcement
boundary against a caller that can bypass it.

## Live host integration

```
python3 -B experiments/filesystem-service/check-fd-facade.py
```

The checker compiles a C consumer using the actual facade/client and a Rust host
server using the unchanged selected handler/ProcessFiles/AF07 service. Rust starts
the C consumer as an observed child. Actual bytes travel bidirectionally over host
OS pipes. The C adapter uses nonblocking read/write and bounded poll; host EAGAIN/
EWOULDBLOCK map to the client's private -11 wait result. This host adapter is not
an Aether trap/endpoint implementation. Whole-pipe-write success confirms host
transport delivery only; it cannot prove the client validated the response.

Rust binds the existing shell1/generation1 policy key, dispatches actual C-generated
messages and holds PreparedReply until complete host writes. Explicit abort/EOF,
partial reply and injected malformed response retire the existing source. The
service runs the existing synthetic storage fixture in a bounded channel thread.
No additional native engine or live SPA is created. The outer owned command group
has a30-second suite watchdog and retains child cleanup; each compile is bounded
to60 seconds, streams16MiB, clean environment/private build roots.

Seventy-four live host cases cover happy/bytewise requests, local no-I/O denials,
wrong response generation,4096-byte reads/907-byte EOF remainder, read denial then
healthy read with unchanged offset, nonzero padding, AF07 body/count/close faults
and all64 incomplete padded-body prefixes. Happy flow checks missing/bad FD,
component-open, shared offsets after dup/close, signed end seek, EOF, cloexec and
last-alias close. The nonzero-length EOF read is an actual fourth backend read;
zero-length closed-FD read rejects. All fault cases preserve caller output and
retire without replay; source/request counters, one local close and one backend
drop are checked independently of C exit. The C consumer observes both actual
host endpoint closes; repeated abort performs neither again.

Six compiling omissions require their specific C assertions plus a failed child
status in Rust: semantic errno conversion, lost read copy, excess tail copy,
wrong seek origin, omitted real close and masking retired transport. Compiler,
watchdog or generic Rust failure cannot satisfy these controls. Default Clippy,
strict Rust2021 warnings/unsafe denial/rustfmt, C17 strict diagnostics/format and
UBSan apply. Full source/tool/LLVM resource/header/runtime closure is pinned before
compilation; host SDK headers are recorded before C compile and rechecked afterward.
Actual Python3.10.21 and3.14.7 qualify the recipe. Neither native ELF/object/link,
full-stack/heap/backing/channel fit nor POSIX/native shell conformance is claimed.

[Evidence](../evidence/filesystem-fd-facade-2026-10-21/README.md) retains every
attempt, including module-path preparation failure and the initial EOF-count
oracle correction. Runtime dependencies remain exact sealed inputs. The separate
source-only handoff is `build/service-deliveries/filesystem-fd-facade-2026-10-21-v1`.
Independent affected-owner/reader and assembled native acceptance remain pending.

Next explicitly select file/pipe/console routing and startup FD binding in the
shell runtime, preserve native-copy/failed-exec parent and descriptor state,
establish immutable executable admission and measure full resource fit within
existing limits. Sys-init retains full dispatcher/readiness/shutdown composition;
Aether supplies exact native command/error/cleanup/fresh-boot qualification.
Packages/Zsh/TTY and full UL-007/081/082/M3/R1 remain open.
