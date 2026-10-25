# Scratch open-description owner — 2026-09-14

The new transport-independent owner tracks shared offsets and parent/child
holders around the existing scratch backend. [Pre-code contract](../../NATIVE-SHELL-STARTUP.md#scratch-open-description-ownership)
records authority, bounded state, failure rules, test selection and simplicity.
It is not imported by the native supervisor yet and exposes no new public ABI.

Seven owner tests plus six composed backend tests pass in debug and optimized
host builds. They prove shared parent/child writes and sibling-safe close,
independent opens, allocation-before-truncate, poison/no-replay after an uncertain
write, atomic inheritance validation and stale child epochs, rights/bounds with
preserved positions, and malformed replies after open/write/close effects.
Two deliberately broken copies omit offset advancement or close the backend while
another holder remains. Each compiles and fails the exact selected assertion.

The first debug test compile failed because a reusable no-transport closure lacked
an explicit argument type. Adding the fixed-record reference type corrected the
test; no runtime behavior was changed by that fix. Attempt1 source/log and its
retained compiler receipt are archived. Attempt2 passes. All failures, including
the expected mutation rejections, remain available.

Full host checks pass (103 Python tests), including offline standards, workflow
and the new driver. Formatting and the four-member simplicity snapshot verify.
Freestanding no_std optimized object compilation passes; this is not target
execution or a service stack/image budget measurement. All269 previous native
source hashes remain unchanged. No new QEMU or actual dash acceptance is claimed.

Owner identity comes from the authenticated caller, not a client-supplied peer
number. Local FD alias counts and frozen fork/exec tables remain the integration
owner's responsibility. The component's inherit operation alone is not admission
or CLOEXEC validation. Poisoned-owner cleanup requires confirmed native stop and
must be integrated before shell adoption. This code contains no new unsafe/FFI,
allocation, dependency or kernel operation. Original work is BSD-2-Clause.

Next wire this component into the native scratch profile and private C descriptor
adapter, then qualify unchanged fd-leak-control and redirection with real dash.
Matching runner evidence, independent consumer acceptance, public SDK integration
and persistent R1 assembly remain open. Siblings and released pins are unchanged.

Exact source/docs, commands, logs, expected mutants and object outputs are retained.
Generated working directories were archived and verified before removing only
those duplicates. The retained checking script records the original run; use the
unit-test entry point for fresh runs rather than overwriting this sealed packet.
