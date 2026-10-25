# Actual musl stdio write-loop reference (UL-067)

The [fixture](stdio-loop-controls.c) exercises musl1.2.6's actual __stdio_write
source and FILE layout with the [private vector bridge](VECTOR.md). It is a static
Linux reference executable, not a native image or installed libc replacement.
The candidate source is copied from the verified archive, renamed and changed at
one call site: syscall(SYS_writev, becomes fixture_writev(. An independently
renamed control retains the real Linux writev call and writes two vectors through
a pipe; the reader verifies their exact concatenation. No stdio loop is simulated.

9,720 cases combine prefix and new-data lengths0–17, backend short-write limits
1/7/16, success/EIO/zero-progress/lost-ack/malformed replies, and fault placement on
the first or second transfer. Cases in which a later fault is never reached remain
successful and are not counted as exercised faults. Exact assertions check committed
byte order, confirmed progress, return count for the new-data vector, F_ERR and
FILE write-buffer reset/clearing. The backend independently records committed and
acknowledged bytes; a lost acknowledgement may commit bytes without confirming any.

Both lost-ack and malformed replies poison shared bridge state. A subsequent
logical diagnostic attempt must fail without another backend call. This fixture
has no native diagnostic grants; it does not adopt FD mapping or stdout/stderr
policy. Full public fwrite/fprintf/fflush, finalization and native lifecycle remain
separate from direct invocation of this real internal callback loop.

Two compiled mutants clear poison or overwrite the gathered prefix. Both must
emit the assertion marker and exit99. A fixture-only __assert_fail override uses
that deterministic terminal result; it does not change candidate libc behavior.
The first mutant run reached its assertion but abort did not finish before60s;
that incomplete run and its cleanup are retained. It is not counted as a passing
mutant or proof of signal/abort support. The final full run passes both mutants.

## Build, limits and reproduction

```sh
python3 -B experiments/toybox-reference/check-stdio-loop.py
```

Requires the existing pinned Clang21.1.8/musl Linux SDK, source archive, retained
standalone receipt and running local Podman VM/image. Python3.12+; help/version
stdout0, invalid usage stderr64. No image pull, network or VM startup. Private
container input/root are read-only, UID65534, capabilities dropped,512MiB/32PID,
60-second process bound and exact-name cleanup. Tools, SDK, internal header bytes,
patch identities, source and logs are retained in
[evidence](../../docs/evidence/toybox-stdio-loop-2026-09-06/summary.json).

New source uses C17 warnings/format. Compiling against private musl headers needs
their source include ordering and -Wno-unused-parameter for an upstream inline
helper; renamed upstream source also uses -Wno-sign-compare. Original fixture
callback arguments are explicitly consumed. Initial missing include tree, missing
off_t exposure and alternate include-order failures are retained. No upstream
header/style was edited. Static ELF checks are separate from runtime results.

Linux UBSan is not provisioned. Unchanged vector.c's prior host UBSan evidence is
reused; this is not sanitizer coverage of the actual Linux callback fixture.
Minimum-Python runtime and independent review remain pending. The [shared host session](SESSION.md) now tests poison/finalizer composition
separately; integrating it into this real musl-loop executable remains unperformed. Process-mask state remains a
proposal and native role/admission/cleanup cases remain NOT RUN.
