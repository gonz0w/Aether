# Scratch backend implementation — 2026-09-14

The bounded Rust backend component is implemented but is not wired into a native
service profile. The [owner reference](../../NATIVE-SHELL-STARTUP.md#writable-shell-descriptor-owner-review--2026-09-14)
contains the pre-code requirement and exact private records. This packet is host
transition evidence and target object compilation, not Aether VM execution.

Six tests pass in debug and optimized builds: write/close/reopen/read bounds;
exhaustion before truncation; rights/canonical-record rejection; holes/zero-length
writes/truncation; stale handles/slot retirement; replacement authority and zeroing.
Two isolated mutants remove rights enforcement or truncate on allocation failure.
Both compile, then fail their exact selected assertion with exit101 and one failed
test. Their logs and source copies are retained; these are expected rejections,
not implementation failures. No unexpected test failure occurred.

The full host suite passes (including the new Python driver and offline standards
checks), as do formatting, workflow validation and the four-file simplicity hash
check. A freestanding x86_64 no_std optimized object compiles. The source contains
no unsafe code, allocator, dependency or FFI. The object is not a linked service;
stack/image-budget measurement and native authority validation remain outstanding.

All267 previously qualified runtime inputs are unchanged. Existing native modes
were not rerun because this component is not imported by them. A full matching
connections/runner qualification and affected controls remain mandatory when the
new backend is connected. Neither shared offsets nor FD inheritance are claimed
by these explicit-offset backend tests. No persistence, public SDK or release
acceptance follows. Original work is BSD-2-Clause; siblings and pins are unchanged.

sources contains the exact implementation, test and documentation snapshot.
artifacts.tar.gz retains binaries, no_std wrapper/object and both mutated sources.
All generated members were verified before deleting only their duplicate working
directory. Checks and raw logs remain outside the archive. The retained driver
records the original commands; use the documented unit-test entry point for fresh
runs, never overwrite this sealed packet.
