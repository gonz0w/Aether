# Scope and owner review

Requirement and pre-code selection are in NATIVE-SHELL-STARTUP's copy-profile
thread identity prerequisite. The current copy-mode set_tid_address returned a
slot number while getpid returned a generation-bound process ID. Preserve pointer
validation and registration/pinning effects; change only the return value in the
single-context connections copy profile. Legacy/threaded profiles are unchanged.

Musl's inspected gettid.c reads the pthread cache rather than issuing SYS_gettid.
Its _Fork.c __post_Fork updates that cache from set_tid_address and also resets
thread-list/robust bookkeeping and releases the abort lock. Calling it blindly as
a standalone rebinding helper would bypass its surrounding fork obligations.
A new raw gettid syscall would not repair the cache. No such syscall is added.

The native memory adapter reads getauxval(0xa000) on each call; musl getauxval reads
libc.auxv. Current Aether command transport separately caches input/output grants,
bindings, startup descriptors, user counts and readiness. Rewriting only auxv
would leave those caches and inherited descriptions unresolved. Source ownership:
userland owns the eventual SDK/musl hook, Aether owns these conformance adapters
and the capability/lifecycle mechanism. No sibling edits or adoption claims.

Forbidden outcomes: stale or conflicting copied-child identity, implicit authority
from a TID, invalid clear-TID replacement losing the old pin, parent registration
being copied into the child, or raw registration being called a libc cache update.
The native witness observes the deliberately stale child cache explicitly while
checking the kernel return value. Public fork/exec, descriptor inheritance and
post-fork signal/thread composition remain open.

Selection: host/pin/workflow, complete 18 connections with exact legacy-TID negative
control, five launch, seven M4 and 431 command cases. Reuse current fixed pools,
asm trap declarations and source/timing/artifact capture; no dependency, service
or memory-layout changes. Additional copied page remains within existing limits.
The direct registration pointer points to owned writable memory; the existing
mapping pin and clear-on-stop path retain lifetime responsibility.
