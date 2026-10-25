# Bounded native descriptor facade

2026-09-05. Scope: the user authorized continued cross-project runtime work toward
a shell. For this experiment Aether-userland owns the descriptor/libc facade,
Aether owns native stream enforcement, and sys-init owns launch/fixture lifecycle.
This assigns the previously open facade work for this bounded implementation;
it does not settle the whole future POSIX service topology.

## Implemented behavior

A pinned musl build routes read, write, close, dup and dup2 to native_io.c. The
single-threaded process owns an eight-entry descriptor table, with initial stdin,
stdout and stderr bound to three caller-scoped native streams. Duplicate descriptors
share a stream cursor and reference count. dup selects the lowest free slot;
exhaustion is EMFILE. dup2 validates its source and destination before replacing
the destination; same-descriptor duplication leaves it open. Retaining the source
before dropping the destination also handles two descriptors already sharing a
stream. Last close revokes that native stream. The kernel owns no POSIX descriptor
table. Direct calls to a closed native stream still fail even if user memory is
edited or a stream number is guessed. Legacy raw write is unavailable in this profile.

The scope follows the tested subset of the POSIX.1-2024 [dup/dup2 requirements](https://pubs.opengroup.org/onlinepubs/9799919799/functions/dup.html)
and [read behavior](https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html).
This is deliberately adapted: all streams are nonblocking, there is no fcntl mode
selection, input reads transfer at most four bytes, writes at most sixteen bytes,
requests are bounded to 256 bytes, and only eight descriptors/three native streams
exist. These are fixed profile limits, not a claim of general POSIX conformance.

Input is a 32-byte queue with backpressure and a separately sealed producer.
Reading an empty open queue yields EAGAIN; draining a sealed queue yields EOF.
Bad direction, closed descriptor, invalid user range and zero-length operations
have explicit outcomes. Pointer checks precede queue consumption. Stdout and stderr
have separate retained 256-byte buffers. A full output buffer yields EAGAIN; these
retained fixture buffers cannot drain/reuse capacity during an instance.

## Reproduce

```sh
python3 experiments/native-c/build.py --io
python3 experiments/native-c/test_io.py --aether /absolute/Aether --sys-init /absolute/sys-init --sdk /absolute/emitted-build-directory --work /tmp/new-native-io-run
```

The first command uses the pinned musl archive and LLVM tools already required by
the native experiment. It emits the positive startup ELF/envelope and a bad-dup
control compiled without duplicate reference retention. The second command checks
consumer/artifact hashes, copies Aether into a fresh work directory, and invokes
the sys-init-owned I/O client. It retains source hashes, commands, serial logs and
exact semantic outcomes. Work must not exist. Each subprocess has a 120-second
watchdog and QEMU an independent 30-second watchdog.

Two successive generations exercise shared input across dup/dup2 aliases, invalid
dup2 preserving the destination, exhaustion/reuse, read direction, invalid pointers
without consumption, short reads, zero-length reads, queue-full rejection, sealing
and EOF, denied producer authority, last-close native denial, stdout-to-stderr
redirection, output EOF, terminal reclaim and stale handles. The facade returns
native close failures rather than inventing success. Reinitialization in the second
generation checks that descriptor/stream state does not survive backing reuse.

Four outcomes pass: normal; omitted duplicate retention rejected; withheld output
rejected; omitted backing zeroing rejected. Kernel queue tests additionally cover
wraparound, order, backpressure and sealed drain. Earlier native startup, all five
native-supervision cases, kernel host tests, and default two-core smoke/framebuffer
remain passing. See docs/evidence/native-io-2026-09-05/ for bounded evidence.

## Compatibility inventory and remaining work

| Interface | Current native status |
| --- | --- |
| read/write | Adapted nonblocking stream subset, target-tested |
| close/dup/dup2 | Single-threaded fixed-table subset, target-tested |
| open/fcntl/dup3/lseek/readv/writev | Unsupported; no successful placeholder |
| fork/exec/wait and inherited/CLOEXEC descriptors | Unsupported |
| pipe creation and SIGPIPE | Unsupported; native producer closure errors are not POSIX signal delivery |
| stdio/general printf | Not established by direct read/write tests |
| tty/termios/ioctl, canonical/raw mode, jobs/signals | Unsupported |
| serial console, authenticated session, shell | Not implemented by this fixture |

The test uses an authorized in-memory producer/consumer; it does not read a host
terminal or claim a console prompt. Next: a separately owned console service with
a delegated device/stream boundary, followed by terminal and process semantics.
UL-003/006/007/008/015 remain broader work; this result does not close them. The
new AENFD001 envelope is distinct from existing production candidates and is not
accepted by pkg-mgr's AENSUP01-only supervised transport. No shared release or pin
has changed, and no package activation or installation occurs.
