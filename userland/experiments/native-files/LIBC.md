# Bounded libc file witness (UL-043)

Four native outcomes pass using the pinned strict-musl archive and the tested
userland file-descriptor layer. The [probe](libc-probe.c) is a separate translation
unit and calls external C entry points. Link maps confirm that `read`, `write`,
`close`, `dup` and `dup2` come from musl; the new [adapter](libc-adapter.h) supplies
`open`, `lseek` and the existing `__aether_io` transport hook. The archive and SDK
are unchanged. This is an explicitly adapted single-thread profile, not general
POSIX filesystem or shell support.

## Supported scope

- Four initially private descriptors and two open-file records. No implicit
  stdin/stdout/stderr setup. The fixture creates volatile scratch through the
  private API and passes that descriptor to the C probe.
- `open(name, O_RDONLY)` accepts the existing service's single-component names.
  Other flags return ENOTSUP, including write/create/truncate/append, NONBLOCK and
  CLOEXEC. No creation mode, umask, permissions or inheritance is silently ignored.
- Musl read/write return at most 16 bytes per call. Larger valid requests return
  short I/O; counts above SSIZE_MAX return EINVAL. Null nonempty buffers are
  rejected, but arbitrary caller-pointer validation is not established. This
  remains an in-process facade for valid local buffers.
- Musl duplicates share the open-file position; separate opens start at zero.
  Last close consumes the service handle. Errors use C's `-1` and `errno` through
  musl's return conversion or the new open/lseek adapters.
- Public `lseek` supports SET/CUR within absolute positions 0–64, checks signed
  overflow before addition, and rejects END/unknown modes with ENOTSUP. This does
  not adapt musl's internal `__lseek` or establish buffered stdio support.
- Native `openat` and `pipe` are explicitly exercised returning ENOSYS. Unknown
  hook operations also return ENOSYS; other libc symbols are not presumed adapted.

Service handles remain opaque and authority is enforced by the owner service.
No flags or paths create a new native grant. The prior stream/libc fixture is a
separate profile. No kernel, sys-init, pkg-mgr or standards implementation changes.

## Musl audit

The source snapshot records musl 1.2.6 read/write/close/dup/dup2/open/openat/lseek,
`__syscall_cp.c`, pthread cancellation and the native x86-64 syscall header.
The pinned header routes operations 0/1/3/32/33 to `__aether_io`; the weak
single-thread cancellation wrapper uses that header. Maps verify this wrapper
and exclude `pthread_cancel.lo` from these clients. The threaded cancellation
assembly can bypass the hook, so threads/cancellation are not supported by this
witness. Musl close still translates EINTR to success; this adapter does not
produce EINTR and no interrupted-close claim is made.

Upstream open's CLOEXEC fallback and internal stdio entry points are not adopted
by replacing public open/lseek. These remain explicit future audit gates. The
client links a separately compiled channel object with its original hook renamed;
the service keeps the original channel object. Channel transport therefore stays
independent of the descriptor calls it carries. No hook recursion is introduced.

## Target cases

| Case | Oracle |
| --- | --- |
| positive | Short write/read, exact bytes, shared and separate positions, negative relative seek and extreme-offset rejection, read-only denial, descriptor exhaustion, dup2 validation, alias/final close, missing/traversal lookup, unsupported flags and openat/pipe; client 29, service 17, replacement 33, supervisor 100/reclaimed 3 |
| wrong-errno | Return EACCES for a negative descriptor; the independent libc probe rejects at client 200 |
| ignore-flags | Accept unsupported open flags; rejects at client 201 |
| frozen-offset | Omit position advancement in the descriptor layer; rejects at client 205 |

Controls require supervisor 611/reclaimed 0, the exact profile-rejection panic
and no pass marker. A first incomplete compile exposed that SSIZE_MAX needs the
POSIX feature declaration under strict C11; adapter client builds now explicitly
set `_POSIX_C_SOURCE=200809L`. The final suite reused the same kernel snapshot.

```sh
python3 experiments/native-files/check.py --aether ../aether \
  --sdk build/native-c-xhkdw6jv --libc-files
```

[Retained evidence](../../docs/evidence/native-libc-files-2026-09-05/summary.json)
includes the four libc cases, nineteen fresh descriptor/fault/read-only/writable
regressions, source/SDK/tool identities, link maps, native images and serial logs.
The [compatibility inventory](../../docs/compatibility/README.md) records these
adaptations without promoting the native script tier. Next work audits and tests
buffered stdio entry points; fork/exec/TTY and shared PD owner review stay open.
