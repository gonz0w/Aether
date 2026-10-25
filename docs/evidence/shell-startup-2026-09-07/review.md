# UL-007 startup implementation review

Requirement recorded before code, 2026-09-07: qualify the unchanged userland
startup prerequisite against a bounded native producer/SDK adapter pair.

Aether owns caller identity and capability enforcement; the opt-in single-thread
C adapter owns process-local dispositions, mask and descriptor bookkeeping.
The existing AECAT001 owner supplies all three stream references atomically;
no PID or FD supplies authority. No sibling edits or release-pin changes.

Implement getpid only in the existing runner-local connections experiment:
positive identity = generation * 4 + slot + 1, using actual kernel state. No PID
reuse within its three-generation bound. This is lifetime identity, not an exec
contract. No arguments or pointers; unused arguments rejected. Other profiles
continue ENOSYS.

The adapter admits indices 0..15; inherited descriptors 0..2 start without flags.
F_DUPFD and F_DUPFD_CLOEXEC select the lowest free index >= minimum and share
one underlying binding. Flags are descriptor-local; the last local close invokes
the existing consuming remote close. Duplicate flags are assigned before entry
publication. This is a single-thread/no-exec adapter: concurrent mutation, fork,
exec-close enforcement and cross-process inherited alias accounting are excluded.
Read/write retain existing capability checks, partial transfer and poison rules.

Signal state is process-local in this single-context profile. Support query and
DFL/IGN disposition changes, zero flags and full stored mask (unmaskable signals
9/19 removed). Reject custom handlers/flags explicitly. No signal delivery,
pending queues, sigreturn or successful kill is supplied. Native synchronous
faults and supervisor stop retain their existing semantics. This prerequisite
cannot qualify dash's handler-dependent initialization. Public C adapters, not
Linux-numbered raw signal syscalls, expose these operations. No successful stubs.

Forbidden outcomes: fabricated PID, no-op setters, partially admitted descriptors,
flag omission, duplicated remote ownership, premature remote close, leaked aliases,
authority widening, state surviving replacement or claims of native dash acceptance.
No new dependency, kernel allocation, quotas, unsafe user-pointer kernel copies,
or stack expansion. C interfaces require valid application pointers; kernel
isolation contains invalid pointers as before. The FFI/assembly self query uses
the existing interrupt transport and clobbers. Legacy transport formatting remains
unchanged except a scoped dispatch seam; new C uses Clang21 pinned style.

Applicable: Foundations O-01–05, I-01/03/05, E-01–08; Distribution native/POSIX;
approved unreleased PD-01/02/03/07/08/11/12 guidance. PD-04/05/06/09/10 remain
unimplemented gates. No standards-owner acceptance is inferred.

Tests: unchanged copied consumer probe with exact stage failures for invalid PID,
no-op action/mask and missing CLOEXEC; malformed binding rejection with no traffic;
FD minimum/exhaustion/flags/refcount/rights/real alias I/O, all-bit mask preservation
and state restoration in two fresh generations. Complete command-runner regression,
host/pin/workflow tests, Zig/C/Rust formatting, M4 and native memory regressions.
Retain failed attempts, immutable inputs, target logs, source/artifact/tool hashes.
Independent userland intake and actual dash/fork/exec/wait remain separate.
