# Bounded buffered files (UL-044)

Four native cases pass using pinned musl buffering over the existing file service
and native-memory v1. The separate [probe](stdio-probe.c) calls public FILE APIs;
[adapter code](stdio-adapter.h) bridges internal vector transfers and seeks to
the tested descriptor layer. Original musl fread/fwrite/fseek/fgetc/fclose,
allocation and FILE-list machinery remain linked from the unchanged archive.
The runner builds five narrow replacement objects from pinned local musl sources.

## Adaptations and findings

Musl's internal read/write callbacks use readv/writev, bypassing the five-operation
scalar hook. Replacement callbacks call the adapter's private two-vector helpers.
They validate counts and total size, gather/scatter at most 16 bytes per service
request, return short counts and preserve vector order. These are internal stdio
bridges, not public readv/writev adoption. Buffers must be valid local memory.
The internal seek callback now reaches the bounded public lseek adapter.

Public fdopen accepts only `r` and `r+`; `r+` requires an alias of the fixture's
known writable scratch handle. Other modes, append and close-on-exec are rejected
before allocation. The renamed upstream fdopen core still allocates and initializes
FILE objects. Public fopen supports only `r`, closing its newly opened descriptor
on setup failure. It does not adopt upstream fopen's direct syscall path or unchecked
flag setters. No new mode/umask/permission model, standard streams or TTY is claimed.

The input fflush audit found that upstream ignores a failed seek while discarding
unread buffered data. The candidate replacement now returns EOF, sets F_ERR and
preserves the buffer on that failure. A one-shot injected EIO tests the failed
seek; clearerr followed by retry must recover the next byte. The original upstream
fflush object is a control and fails this exact assertion. This is a local candidate
patch; the pinned archive and upstream sources remain unchanged.

A native run also exposed errno contamination: a successful close's internal
channel polling overwrote the prior ENOSPC from a failed flush with EAGAIN. The
raw `__aether_io` hook now saves/restores errno around descriptor calls, leaving
musl's syscall return conversion responsible for publishing errors. This lets
fclose report the flush error while still closing the descriptor. A control
injecting EAGAIN after the hook reproduces the failure.

Native memory is enabled only for this mode, using the existing userland adapter
and owner kernel option. Dynamic FILE allocation is real; allocation/cache metadata
may remain until instance exit. Supervisor cleanup still requires three reclaims.
This does not establish general memory-plus-service conformance, cancellation,
concurrency, restart, reconnect, persistence or POSIX filesystem support.

## Cases

| Case | Independent oracle |
| --- | --- |
| positive | Unsupported modes; buffered writes spanning both vectors; 26 exact bytes via fread; EOF and seek reset; failed input sync preserves unread bytes; ENOSPC flush/ferror and retry; failed implicit flush at fclose preserves ENOSPC and closes the FD; read-only reopen, FILE-list cleanup and nonzero vector witnesses |
| baseline-flush | Original upstream input fflush ignores injected seek EIO; client 189 |
| corrupt-vector | Flip the first byte of a vector read; exact-byte assertion rejects at client 186 |
| leak-poll-errno | Reintroduce EAGAIN contamination after raw I/O; fclose errno assertion rejects at client 196 |

Positive completion requires client 29, service 17, replacement 33, supervisor
100/reclaimed 3 and the existing file-service marker. Each control requires its
exact client status, supervisor 611/reclaimed 0 and profile-rejection panic.
Timeout and generic boot failures are never accepted. The fault injection is
consumer-local; no service/kernel working-tree source is modified.

Two initial compile attempts exposed missing musl internal include paths and
upstream sign-comparison warnings. Upstream objects use their internal include
layer and suppress unused-parameter/sign-comparison warnings; local sources keep
Wall/Wextra/Werror. The next incomplete native run exposed the real fclose errno
bug above. Final cases reused the original kernel capture after those corrections.

```sh
python3 experiments/native-files/check.py --aether ../aether \
  --sdk build/native-c-xhkdw6jv --stdio-files
```

[Retained evidence](../../docs/evidence/native-stdio-files-2026-09-05/summary.json)
includes four stdio cases and twenty-three fresh libc/descriptor/fault/file
regressions, exact patch/source/header/tool/SDK identities, link maps, commands,
images and serial logs. The compatibility inventory records the bounded FILE
subset. Formatted I/O, automatic exit flushing, all FILE modes and invalid pointer
handling remain untested. Next work refreshes the native dash integration gaps
and the companion mechanism handoff; these FILE cases do not close the shell tier.
