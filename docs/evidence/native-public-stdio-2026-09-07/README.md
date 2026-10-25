# Native public stdio integration

Pre-code contract, 2026-09-07. Continue R1's UL-067 integration order without
changing release scope. Link a private __stdio_write object over the unchanged
native SDK archive, replacing only its writev call with the qualified scoped
bridge. Exercise real setvbuf/fwrite/fprintf/fflush/ferror on stdout/stderr. Do not
install a libc replacement, add a syscall, or claim Toybox execution yet.

Set the caller-owned stdout buffer before first use, preserving F_SVB and avoiding
an unsupported terminal probe. Buffer remains live through explicit final flush;
stdin uses existing scalar read, with no buffered-input seek claim. Exclusive
single-thread stream ownership; no arbitrary pointer probes, allocation or grant
increase. The actual public routines own FILE state; the probe must not alter it.

Select binary buffered copy, empty, native short writes, stderr D/newline,
formatted usage64, complete write EIO/EINTR, malformed/cut write reply, diagnostic
EIO/cut and deliberate missing diagnostic/corrupted data mutants. Observe buffer
acceptance separately from successful flush; ferror and errno must retain failure.
No automatic retry or diagnostic traffic after unknown completion. Flush while
bindings are live, then retire aliases; independent owner checks positions/bytes,
terminal kind/status, exact cleanup and four reclaims across two generations.

Foundation O-02–05/I-01/03/05/06/E-01–08 and DEVELOPMENT apply. Userland owns libc
and future applet adaptation; pins, SDK, siblings and UL-059 bundle stay unchanged.
Retained musl MIT terms apply to callback source; new probe/recipe BSD-2-Clause.
Record failed attempts before edits and freeze runtime sources during target runs.
Select new native cases, prior internal-stdio/vector/startup suites, full command
regression, Zig/host/pins/workflow and C formatting. Update NATIVE-CAT/THIRD-PARTY,
workflow and STATE. Public exit callbacks and actual cat remain next work.

## Native case coverage

| Cases | Required observation |
| --- | --- |
| copy / empty / short | Exact binary stdout, empty stderr, two generations/four reclaims. First17 bytes buffer without channel calls; next15 overflow musl's effective24-byte buffer. Native short owner limits reads7/writes3. Empty input still follows explicit final flush/close |
| diagnostic | Real fprintf emits exactly D/newline to stderr after full binary stdout; streams remain distinct |
| usage | Actual fprintf with a %s conversion emits the established37-byte usage text; no input consumption, empty stdout, status64 |
| write-error / write-eintr | fwrite accepts11 bytes into the buffer without traffic; first flush succeeds, next read brings input position22, next flush returns EOF with exact EIO/EINTR and ferror; stdout remains first11 bytes |
| write-malformed / write-cut | First11 bytes can commit without confirmation; flush returns EOF/EIO, ferror is set, later fprintf emits no channel traffic; local aliases retire and owner cleans remote bindings |
| diagnostic-error / diagnostic-cut | Owner sees the exact first16 usage bytes; fprintf fails with EIO/ferror, usage64 is preserved; uncertain diagnostic completion forbids further traffic |
| corrupt / skip-diagnostic | Independent owner rejects changed binary output or missing stderr at1505 after client0 |

All public calls come from the existing native SDK archive, linked without LTO;
-fno-builtin prevents original-probe call substitutions. Symbol inspection retains
setvbuf/fwrite/fprintf/fflush/ferror, __stdout_write, __stdio_write and fixture_writev.
The replacement callback is the same verified musl source with its original name
and one syscall-call replacement. It is linked before the SDK archive in this
private image. Existing stdout initialization observes caller-supplied buffering;
no successful ioctl stub or private FILE mutation is introduced.

fflush(NULL) precedes scalar close on all normal/error paths. Preexisting nonzero
status survives subsequent cleanup errors. This is explicit probe cleanup, not a
general C or Toybox exit finalizer. Buffer storage remains valid until main returns.
The positive/error cases use independent Rust checks for exact byte positions,
terminal kind/status, alias consumption, backend closure and four native reclaims.

## Final qualification

All 13 new native cases pass on attempt1: eleven positive/error scenarios and
two exact owner1505 mutants. Prior internal stdio9, vector9, Toybox startup4 and
all211 command-runner cases pass on the same frozen runtime sources. All98 host
tests, Zig/pins, workflow33groups and Clang-format21.1.8 checks pass. No failed
attempt occurred. Five target receipts agree on sources. Every prior runtime
source, SDK identity and UL-059 artifact is unchanged; only the public probe is a
new runtime source. No kernel, installed libc, pin or sibling changed.

Default ELF is44,176bytes, eleven load pages and4-byte PT_TLS. No dynamic memory
grant is selected. This does not measure peak stack/heap or performance. The
formatted-output scope is bounded %s text, not all printf conversions, locales,
allocator failure, concurrent FILE access or general libc compatibility.

Results for native/stdio/vector/startup/command plus raw logs and regression UTC
receipts are retained. qualification.json records source/SDK/bundle checks and
image bounds. final-artifacts.tar.gz retains sources/, run-native.py and all five
run outputs, including original musl/COPYRIGHT and generated callback objects.
ISO/installed-boot duplicates/kernel.elf are omitted; receipt hashes remain.
archive-check.json verifies every archived runtime source and the recipe.

The new recipe uses the hash-pinned musl archive retained by the previous native
stdio experiment. Reproduce with run-native.py above and the exact prior recipes/
SDK/tool-lock commands recorded in the regression timing files. Run host checks
with `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Native commands record UTC boundaries/exits; host/format timestamps remain
unavailable and are not invented. Broader connections/inherited launch suites were
not rerun: shared runtime, loader and harness implementations did not change;
full command and three preceding suites cover the reused paths.

Independent implementation/consumer review, real Toybox applet/exit integration,
extended reliability and assembled R1 remain open. Existing ASCII payloads and
boot markers are preserved under the existing Experience migration scope; no
new presentation adoption or renderer conformance is claimed. The full release
roadmap remains in force, including persistent files, runner and native packages.
