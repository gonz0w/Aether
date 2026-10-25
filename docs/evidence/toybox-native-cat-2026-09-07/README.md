# Actual Toybox cat native execution

Pre-code contract, 2026-09-07. Continue full R1 through UL-067: combine verified
real startup/mask/allocator/locale and public stdio with unmodified cat_main,
loopfiles and xwrite. Scope: admitted cat with no arguments, binary32/empty/short
input. No filenames/options or injected applet I/O failures accepted yet.

Preserve Toybox xexit callback removal/order, fflush/ferror and _xexit rebound
branch. Patch only the _exit argument in _xexit to a private status-returning
cleanup hook after upstream callback/flush processing. No global _exit override.
Two heap-allocated fixture callbacks prove reverse order and signal0; wrappers
call actual fflush_unlocked/ferror_unlocked and observe order. The hook verifies
these observations before consuming the three aliases and preserving status.
Its scope is one synchronous normal exit, not recursive/signal finalization.

Caller-owned callback function pointers use Toybox's existing x86_64 function/data
pointer conversion convention; callbacks are live static functions, nodes owned
and freed by actual xexit. No concurrent mutation or unwinding. Retain existing
memory grant/quotas and actual TLS/mask/startup assertions. Owner independently
checks bytes, terminal kind/status, backend cleanup and four reclaims.

Select binary copy, empty and native short writes; skipped cat_main must fail
owner1505, missing callback/flush must fail client120/owner1501, omitted close must
fail owner1503. Preserve every failed attempt and source snapshots before changes.
Run new target cases, prior public-stdio/startup and full command suite, host/Zig/
pins/workflow/format. Foundations O/I/E and DEVELOPMENT apply; userland owns libc
and applet integration acceptance. No sibling, release pin or UL-059 mutation.
Original probe BSD-2-Clause; copied upstream Toybox/musl retain existing terms.
Update STATE/NATIVE-CAT/THIRD-PARTY/workflow. Actual applet error paths, diagnostics,
re-entry and consumer CAT matrix remain required before full handoff acceptance.

## Executed behavior and boundaries

The probe validates admitted cat/LC_ALL=C and the existing memory grant, then
retains the previous real TLS, mask exchange, locale, xmalloc4096 and setvbuf
assertions. Two extra arg_list nodes hold live static function pointers using
Toybox's existing x86_64 convention. Unmodified cat_main calls loopfiles and
xwrite on stdin/stdout; normal input arrives in native16-byte pieces, while the
short owner returns at most7 read bytes and3 written bytes. No applet source patch
or replacement copy loop is used.

After cat_main returns, actual xexit pops/calls/frees the nodes in reverse order,
passes signal0, invokes actual fflush(NULL), then actual ferror(stdout). Wrappers
observe these calls without replacing their effects. The correct relocation names
are fflush/ferror, despite unlocked alias names appearing in earlier disassembly.
The normal _xexit path calls fixture_finish before _exit; its rebound branch and
separate vfork path are unchanged. The hook verifies observed ordering and live
aliases before consuming all three; no extra allocator or kernel grant is added.

Three positive cases independently check all bytes/positions, terminal0/backend17
across both generations and supervisor100/reclaimed4. Skipping cat_main rejects
owner1505; missing callbacks or flush rejects client120 then owner1501; omitted
stderr close rejects owner1503. A generic panic cannot satisfy any of these cases.
The skip-flush mutant is a separate upstream-source variant, never normal input.

Callbacks intentionally perform no output. Their order and real flush invocation
are tested here; callback-generated buffered output, flush-error propagation,
re-entry and signal paths are not. Real applet EIO/EINTR/unknown handling and usage
need matching owner expectations: Toybox's request sizes and diagnostics differ
from the eleven-byte conformance client. Reviewed writeall stops on negative/zero
progress; that source observation is not native applet error-path qualification.
Cleanup-close failure diagnostics and complete consumer finalizer semantics also
remain open. This is a normal-exit integration step, not full CAT acceptance.

## Final qualification

Attempt3 passes all seven native cases. Prior public stdio13 and startup4 pass,
as do all211 command-runner cases and98 host tests, Zig/pins, workflow34groups and
Clang-format21.1.8. Four final target receipts match frozen sources. Every prior
runtime source, SDK identity and UL-059 artifact matches the preceding receipt;
only the opt-in cat probe is a new runtime source. No installed SDK, kernel, pin or
sibling change. Default ELF:85,400bytes,22 load pages,4-byte TLS. Existing native
memory support is explicitly selected, without a quota increase. These mapped
image bounds are not peak-memory or performance evidence.

[Attempt1](attempt-1-triage.md) failed the unique patch-anchor guard before target
execution. [Attempt2](attempt-2-triage.md) was a failed positive native120/1501;
its object imports show fflush/ferror, while disassembly used their unlocked alias
names. Corrected wrappers call and observe actual public symbols. Both failed
source/recipe/artifact sets are retained and verified against their own receipts.
No failed positive is relabeled as a passing rejection test.

Native/public/startup/command results, raw logs, UTC command/regression timing,
exit disassembly and attempt2 undefined symbols are retained. qualification.json
binds source/SDK/bundle checks. final-artifacts.tar.gz contains sources/, recipe
and all four run outputs, including upstream sources/notices and per-case patched
xwrap sources/objects. ISO/installed-boot duplicates/kernel.elf are omitted while
receipt hashes remain. archive-check.json verifies final source/recipe bytes;
both failed archives were separately verified. Host/format timestamps remain
unavailable rather than invented.

Reproduce with run-native.py above; preceding public/startup recipes and the full
command invocation with exact SDK/tool lock are recorded in *-timing.json. Run
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Connections/inherited launch and earlier internal-vector suites were not rerun:
shared runtime/loader/transport implementations are unchanged and full command,
public stdio and startup regressions cover the directly reused paths.

Independent consumer review, actual applet errors/options/usage, callback output,
close-error diagnostics, re-entry/signal behavior and full CAT acceptance remain
open. Sources preserve rebound/vfork code, but those branches were not executed.
No general finalizer, POSIX, filesystem/package or assembled R1 claim follows.
