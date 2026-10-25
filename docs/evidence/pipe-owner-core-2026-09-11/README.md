# Bounded pipe owner core

Pre-implementation scope: implement the selected pipe contract's owner-local FIFO,
canonical request handling, staged child holders and terminal-based endpoint
release in safe Rust. This is a private fixture component, not an installed SDK
or a new shared service. Native dispatcher/adapters and real parent/child target
qualification remain required; host state-machine checks cannot establish them.

Allowed effects: authenticated parent creation, scoped endpoint I/O, bounded
backpressure, child holder publication after readiness and release after confirmed
terminal observation. Forbidden: authority from wire process IDs, early EOF with a
writer, partial enqueue, stale-generation access, implicit retry after applied I/O,
release on stop request or collection-dependent EOF. The dispatcher must supply
identity from the real connection, retain pending frames and completed replies,
and establish terminal/quiet state before invoking cleanup. No kernel, quota,
released ABI, standard pin or sibling change is planned.

Selection before code: Rust host cases for framing, direction and factory denial,
FIFO/wraparound/full-buffer progress, zero-length operations, staged/failed copy,
last-reader EPIPE, buffered EOF before wait, stale terminal/reference rejection,
retirement with pending frames and exhaustion. Compile the same module in a
no_std x86_64 object; this proves compilation only. Run Rust formatting, the host
suite and offline workflow/pin checks. Native acceptance remains NOT RUN until
this core is connected to the authenticated dispatcher and private C adapter.

Simplicity: a fixed 256-byte ring and two process holder rows are sufficient;
a new service/channel or general object registry would add ownership and recovery
work. Reuse the dispatcher's frame/reply storage rather than duplicate pending
buffers here. No obsolete path can yet be removed. Existing contract SE-01–05,
O-01–05, I-01/03–06, E-01–06 and PX-01–03 apply. The core adds no unsafe, FFI,
allocation, dependency or synchronization boundary; its mutable borrow is exclusive
owner access. Native integration must still measure the whole owner image/stack.
New Rust uses rustfmt 1.98.0, edition 2024. Tests follow the existing Rust-via-Python
host runner. Documentation will distinguish host-tested core from native support.

## Results

Implemented `user/native-connections/pipe.rs` as an unconnected safe Rust component.
All 12 host cases pass. Five deliberately broken variants fail the exact selected
assertion: early EOF, retained terminal writer, false full-write success, old pipe
generation acceptance and false EPIPE success. Mutated sources, command output and
compiled host artifacts are preserved. The no_std x86_64 object also compiles;
its debug object size is not a linked owner-image or stack measurement.

`zig build test`, the dedicated Python runner, Rust formatting and `git diff
--check` pass. The prior sealed review and all four simplicity snapshot files were
verified. Introduced local links pass. The 257-source snapshot is read-back verified
and frozen across qualification; existing native source/build inputs are unchanged.
No kernel change, sibling mutation, dependency change or pin update occurred.

The first packaging script failed while decoding an unchanged binary as text,
after all tests had completed. Its script and failure are retained. The corrected
continuation selects changed hashes before decoding; completed checks were not
rerun. This is a packaging failure, not an unexpected product-test failure. Five
expected mutant failures remain distinct in checks.json.

Native adapter, authenticated connection mapping, fork-plan v2, actual process
readiness/terminal observation, reply-loss containment, FD alias/reservation,
SIGPIPE and real dash substitution remain NOT RUN. The next step is native wiring
and real parent/child acceptance; this packet does not complete the contract's
first native acceptance step or unblock full pipe support for companion projects.
