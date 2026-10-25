# Rust block transport evidence — 2026-09-06

The [Rust transport consumer](../../NATIVE-BLOCK.md#rust-transport-consumer-experimental)
runs in an isolated native task using the existing ABI 14 region grant. Rust owns
the transport and workload; pinned strict-musl owns startup and a minimal C helper
witnesses TLS. There is no new kernel ABI, service protocol or filesystem engine.

## Results

`rust-block-boundary-final-2026-09-06/results.json` records successful final target,
host and Rust/C format commands with UTC intervals. Its target is `block-0fa5wfph`:

- Five cases: write/flush, fresh-VM readback, read-only grant, actual recipient #UD
  followed by generation reuse denial, and the exact corrupt-seed rejection.
- 16-MiB disposable disk, 8-MiB delegated region. First/interior/last sectors are
  checked against host-selected bytes. Multi-sector writes preserve the adjacent
  canary sector; the host compares the entire disk after every successful case.
- 4-KiB read, 8-KiB aligned request rejection, unaligned/empty/overflowing/past-end
  rejection, no preflight buffer changes, forged selector rejection, and native
  closed-grant error observed through a wrapper with cached metadata.
- Host/standards/workflow (85 Python cases plus kernel checks), Rust formatting
  and the reviewed Clang formatting configuration all pass.

`rust-block-final-2026-09-06/results.json` also retains passing older C region,
one-sector native and hardware suites. Kernel and old clients are unchanged by
this work, so M4/console regressions were not repeated. The only subsequent runtime
source edits strengthen the Rust client's transfer-ceiling test and format its C
TLS helper; the matching Rust suite and host checks were rerun afterward.

## Every attempt

- `block-4pnhqbiu`: initial five-case Rust pass, before multi-sector write,
  cached-close and maximum/aligned-over-limit checks were strengthened.
- `block-kedbwr0p`: deliberate omission of read byte-to-sector conversion. A read
  hits the native region limit and exits 77; the unchanged positive suite rejects
  at supervisor 841/reclaimed 1 with the expected native-profile panic.
- `block-4nvsgn23`: deliberate use of 256-byte units for read offsets. An in-range
  wrong sector returns unexpected data; child exits 73 and supervisor rejects at
  841/reclaimed 1. Neither control accepts a generic timeout/boot failure.
- The first qualification wrapper retains its Rust and all three older target
  suites. Runtime and host tests passed, but C formatting failed on the tiny TLS
  helper. This is a format-check failure, not a runtime or infrastructure failure.
- The final boundary wrapper passes after formatting and independently testing the
  size ceiling with an aligned oversized buffer. No outstanding failed check.

The two mutation wrappers restore exact source bytes in `finally`; final source
hashes match the working tree. Each target attempt retains its source archive,
original receipt and artifact archive with generated images, disks and logs.
Every archived source member was checked against its receipt hash. Wrappers,
commands, times, documentation snapshot and checksums accompany the target data.
No earlier failed or successful attempt was removed.

## Limits

This is a Rust I/O component, not a mounted filesystem or a production storage
service. No companion adoption, VFS/POSIX owner assignment, package policy or
shared-standard change is implied. Multi-sector I/O is sequential and non-atomic;
no replay occurs. Native device uncertainty still halts with DMA backing retained.
Nonzero-prefix error and unexpected-completion poisoning paths need separate
fault-injection evidence. VM restart is not power-loss durability, and upstream
engine maturity will not by itself qualify its Aether integration. Independent
consumer review and existing extended release coverage remain pending.
