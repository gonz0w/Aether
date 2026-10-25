# Actual musl stdio loop on Aether

Pre-code contract, 2026-09-07. Execute musl1.2.6's real __stdio_write in an
isolated native probe. Copy from the pinned upstream archive, retain COPYRIGHT,
rename the callback and replace its single writev syscall call with a private
adapter over vector-write.h. Do not replace installed libc or allocate a syscall.
Userland retains libc/stdio ownership; this is producer evidence, not acceptance.

Use the actual FILE layout with valid, disjoint borrowed buffer/data objects and
synchronous exclusive access. Check new-data return count, F_ERR, buffer reset on
success and clearing on error. Test a17-byte buffered prefix plus15 new bytes,
three-byte short writes, empty flush, EIO/EINTR and malformed/cut native replies.
Errors must stop, preserve only confirmed progress and never send after shared
poison. The unchanged owner validates exact bytes, positions, aliases and four
reclaims across two generations. A separately identified local zero-progress
injection tests finite EIO behavior; it is not an actual backend zero reply.
Deliberate return-count and prefix-corruption mutants must reject for exact reasons.

No concurrent FILE access, arbitrary-pointer probing, signals, ambient FDs,
allocator, grant/quota increase or kernel change. No global stdio hook, public
fwrite/fflush, Toybox applet or finalizer acceptance. Shared Foundations O-02–05,
I-01/03/05/06 and E-01–08 plus DEVELOPMENT apply. Preserve release pins and old
UL-059 bundle. New source/recipe BSD-2-Clause; copied musl retains MIT terms.
Freeze runtime sources during target runs and preserve failed inputs before edits.
Select new native cases, prior vector and startup cases, full command suite,
Zig/host/pins/workflow and scoped C formatting. Update NATIVE-CAT/THIRD-PARTY,
workflow and STATE with exact coverage and outstanding work.

## Executed native cases

| Case | Native observation |
| --- | --- |
| copy | 32 bytes: buffered prefix17 plus new15, gathered across16-byte messages; callback returns15 and restores all write pointers |
| empty | Live zero-byte write and empty input; no output bytes; FILE remains usable |
| short | Owner limits reads7/writes3; callback advances across the vector boundary and returns the new-data count |
| write-error / write-eintr | Read22 bytes, prefix3/new19, private request cap11; owner confirms11 then returns EIO/EINTR. Callback returns8, sets F_ERR and clears write pointers |
| write-malformed / write-cut | Owner commits11 bytes but acknowledgment becomes uncertain; callback confirms0 new bytes, sets F_ERR/clears pointers; subsequent diagnostic callback makes zero channel calls |
| corrupt | Vector-prefix corruption is detected by independent owner byte check1505 after client0 |
| wrong-count | Deliberately changed success return is detected as client118 followed by owner1501 |

Every image also invokes the real loop with a local zero-progress injection:
nonempty prefix3/new5 must return0 with EIO/F_ERR, clear all write pointers and
make exactly one local injection call with no channel traffic. This does not
claim that a native backend returned zero. Real zero-length output is exercised
in normal cases only; unknown/error cases avoid an extra write before the intended
fault point. All normal/error cases repeat across two generations and four reclaims.

The callback is built from the retained archive with only the symbol and call-site
changes. The generated callback source/object and unmodified internal headers are
retained in native outputs, along with COPYRIGHT and the exact commands. Private
musl header wrappers must precede installed headers; public unistd must precede
internal syscall macros. Upstream sign-compare warnings alone are suppressed for
the copied callback, and system-header treatment applies to upstream headers.
Original probe code keeps -Wall/-Wextra/-Werror and scoped formatting.

This tests the real loop by direct call. It does not wire public fwrite, fprintf,
fflush or Toybox into this callback, register a libc finalizer, or establish FILE
locking/concurrency. Independent consumer acceptance, exhaustive combinations,
sanitizers and extended/physical coverage remain open. The callback operates on
valid same-array buffer pointers and stable disjoint data; invalid arbitrary
pointers are outside this private C contract. Kernel authority is unchanged.

## Final qualification

Attempt 3 passes all nine native cases. Prior vector (nine), actual Toybox startup
(four) and the full command-runner suite (211) also pass on the same frozen runtime
sources. All 98 host tests, Zig tests, three pin checks, workflow (32 groups) and
Clang-format 21.1.8 checks pass. The default probe ELF is 26,664 bytes, seven load
pages and 4-byte PT_TLS. No dynamic memory grant is selected. Mapped pages are not
peak-memory or performance measurements.

[Attempt 1](attempt-1-triage.md) failed callback compilation because private musl
headers followed public SDK headers. [Attempt 2](attempt-2-triage.md) compiled the
callback but failed probe compilation because unistd followed internal syscall
macros. Neither attempt ran a target case; both are retained build integration
failures, not passing rejection controls. Fixes change include ordering only.

Final native/vector/startup/command results and raw logs are retained alongside
qualification.json. Every prior runtime source, SDK identity and UL-059 bundle
artifact matches the previous receipt. No kernel, shared transport, installed libc,
release pin or sibling changed. Broader connections/inherited launch suites were
not rerun because no shared runtime/loader/harness behavior changed; full command,
vector and startup regressions cover the reused paths.

Reproduce with the command above, the unchanged vector/startup recipes and
`scripts/launch_smoke.py --command-runner` with the exact SDK/tool-lock arguments
in command-regression-timing.json. Host command:
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
The native recipe records per-command UTC boundaries/exits, all target receipts
record whole-run times; host/format timestamps remain unavailable and are not
invented. Callback disassembly confirms calls to fixture_writev, not direct
writev syscalls. Source archive identity is not supplier authenticity or review.

final-artifacts.tar.gz retains sources/, run-native.py and native/vector/startup/
command outputs, including generated callback variants, original musl headers and
COPYRIGHT. ISO/installed-boot duplicates/kernel.elf are omitted from the archive;
receipt hashes remain. Both failed archives retain their exact source and recipe
bytes. archive-check.json records successful final archive verification; failed
archives were also checked against their own source/recipe hashes. Independent
review, successful stderr/public stdio, real applet/finalization, sanitizers and
extended evidence remain open. This does not establish consumer or R1 acceptance.

One [post-run audit assertion](audit-attempt-1.txt) incorrectly matched int3
padding as a syscall instruction. The check was narrowed to exact syscall/int
mnemonics and passed; raw disassembly and the failed assertion are retained.
No runtime inputs or artifacts changed, so target results remain applicable.
