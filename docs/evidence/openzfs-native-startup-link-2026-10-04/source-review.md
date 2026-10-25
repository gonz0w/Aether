# Native SDK prerequisites and startup boundary

The linked SDK is the same native-musl delivery used by the preceding packets:
`native-c-5olokhku`, libc.a SHA256
8f66b2b383eabd08b8f27c4913f36a91071c4cfb6373cedebd2e69cabfaaeecc.
[Source receipt](musl-source.json) binds the existing musl1.2.6 source archive and
the two reviewed translation units. Original source and actual optimized native
disassemblies are in the artifact archive's `source-review/` directory. The SDK
source archive is read only; no sibling is edited or its recipe executed.

## Established SDK failures

1. On x86_64, `__clock_gettime` falls back from missing clock_gettime to
   gettimeofday for CLOCK_REALTIME, ignores the second error, multiplies the
   caller's existing nanosecond field by1000 and returns0. Actual native raw calls
   both reject ENOSYS without changing the buffer. The public call then returns0
   with the caller's sentinel17 seconds/42 nanoseconds changed to17/42000. This
   is a reproduced false success, not a clock. Monotonic public calls instead map
   ENOSYS to EINVAL; that also prevents using the current SDK as a real clock.
2. Physical/available-page `sysconf` ignores `__lsysinfo` failure and reads fields
   of an uninitialized stack structure. The original public failure expectation
   rejects natively at232 in both contexts. Source and actual linked instructions
   establish the missing guard; no returned page count is used as capacity. The
   subsequent probe avoids this unsafe public query and observes actual sysinfo
   rejection ENOSYS with an unchanged caller-filled buffer instead.

Userland owns the production SDK correction. The smallest source changes to
review are retaining/checking the gettimeofday return before conversion or public
success, and returning-1 on failed __lsysinfo before reading its result. These are
proposals, not implemented or independently qualified fixes. Returning failure is
necessary but does not provide either clock or scoped memory capacity. Other
sysconf branches retain Linux assumptions and are not certified by this review.

The next matched SDK needs native controls for denied calls, unchanged buffers,
honest errno/public return, supported real providers, boundary/overflow behavior
and thread/interruption schedules. Do not merely zero structures, invent dates,
return host memory or suppress errors to pass engine initialization.

## Owner work before engine execution

| Boundary | Required work / owner |
| --- | --- |
| SDK error handling | Userland corrects and qualifies both guards, supplies exact pinned SDK inputs. Aether independently consumes the matching delivery. |
| Time | Aether/runtime defines real bounded monotonic time and, only if needed, explicit realtime semantics. Existing fixture timer ticks are not a calibrated public clock. Userland binds the supported operation and reports all unsupported cases honestly. |
| Resource/configuration | Aether port supplies explicit owner-local memory/CPU limits; whole-machine physical RAM must not become the filesystem service's budget. Review the Linux-derived feature configuration, tunables and actual crypto CPU-state requirements before execution. |
| Identity/entropy | Native uname/getentropy and random-device open currently reject ENOSYS. Supply only the actual engine requirements through explicit granted providers/configuration. No fake entropy, ambient identity lookup or Linux device discovery. |
| Threads/admission | Compose the selected engine queue/ARC/file profile and measure real peak memory/stack, live threads, lifetime admissions, teardown/restart. Current2-child/4-admission fixture is not enough to assume the82/146-host-peak engine works. |
| Volume/config I/O | Existing adapter only supplies fixture mappings/I/O. Actual granted volume read/write/flush and configuration access precede pool startup; Rust owns filesystem service policy. |

Upstream `kernel_init` first queries physical pages, optionally hostid, opens
random devices, verifies uname, creates system taskqs, initializes crypto/Zstd/spa,
loads pool configuration, initializes checksums and creates thread-local state.
The linked startup image is never invoked here. Removing imports or initializing
one TLS marker cannot establish that sequence or a filesystem mount.

The engine startup experiment stops at these concrete unsafe/missing prerequisites.
This does not imply that unrelated kernel work or independently owned shell/init
qualification must stop. No message, owner acceptance or full R1 readiness is
claimed by this local handoff record.
