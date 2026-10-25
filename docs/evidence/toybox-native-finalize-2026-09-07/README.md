# Actual Toybox callback output and finalization failures

Pre-code contract, 2026-09-07. Qualify actual xexit callback-pop/call/free and real
musl buffered output with the existing private normal _xexit cleanup seam. A
finalizer-only mode reads the fixed32 binary input bytes and EOF, then callbacks
write ordered16-byte halves using fwrite into the existing4096-byte stdout buffer.
No channel call may occur during callbacks. This mode does not call cat_main;
normal applet and usage regressions remain separate required evidence.

Actual xexit flushes while all scoped aliases remain live. Its fflush-error
short-circuit legitimately skips ferror; observe and validate both paths. Known
flush EIO/EINTR permits only exact upstream stderr diagnostics, no output retry.
Unknown write completion forbids later traffic. Preserve nonzero64 through flush
or close failure; promote0 to1. All aliases are locally consumed and independent
owners supervise remote cleanup. Re-entry into the private cleanup hook must
reject120 before any channel effect. This does not implement recursive xexit or
signal-safe finalization. Deliberate corrupt output, omitted flush, premature
flush, skipped close and false success must fail exact semantic oracles.

Add only opt-in cat-owner accounting/diagnostics/status for the32-byte buffered
input. Preserve existing owner modes, ABI, grants, quotas, SDK and standards pins.
Rust1.98.0 edition2024 and clang-format21.1.8 conventions apply. Callback buffers
have static lifetime; Toybox exclusively pops/frees nodes, callbacks retain no
nodes. FFI uses the existing x86_64 function/data pointer convention. No new
concurrency, unsafe kernel code, dependency or policy ownership. Read-only upstream
sources and Foundations O/I/E, local DEVELOPMENT/STANDARDS and Experience ASCII
preservation apply. No sibling modification or consumer sign-off.

Select normal/short, flush EIO/EINTR/malformed/cut, close input/output/diagnostic,
nonzero64 plus flush/close failure, private-hook re-entry and five mutants. Rerun
actual cat/error/usage suites, full213 command cases, host/Zig/pins/workflow and
format. Freeze sources during qualification, retain every failed attempt before
edits. Update NATIVE-CAT, workflow and STATE; recursive/signal exit and independent
CAT acceptance remain open after this slice.


## Final qualification

All18 new cases pass on attempt1: thirteen normal/error/guard outcomes complete
two generations/four reclaims; five deliberate mutants reach their exact owner
rejections. Prior usage20, error11, cat7 and all213 command cases pass. All98 host
tests, Zig tests, immutable pins, workflow37 groups, Rust/C formatting and diff
checks pass. No failed native attempt occurred. Full command run took680 seconds,
within the1800-second review ceiling. Host/format timestamps are not separately
recorded and are not inferred from target timestamps.

| Cases | Observed contract |
| --- | --- |
| buffered / short | Read32 plus EOF; callback fwrite accepts32 with zero callback channel calls; xexit flushes exact binary32, then close/terminal0 |
| flush-eio / flush-eintr | Read32/output16; real flush fails and skips ferror; exact upstream `cat: write: ...` diagnostic; terminal1 |
| flush-malformed / flush-cut | Read32/output16 may commit without confirmation; shared poison forbids subsequent channel calls, local aliases retire and owner cleans remotely; terminal1 |
| close-input / close-output / close-diagnostic | Full output32, all locally owned aliases consumed; known close error promotes0 to1 |
| status / status-flush / status-close | Prior64 preserved, including flush/close failures; no additional upstream flush diagnostic for prior nonzero status |
| reenter | Outer cleanup succeeds0; repeated private-hook call returns120 before channel effects; this is not a recursive xexit terminal-policy test |
| corrupt / skip-flush / early-flush / skip-close / force-zero | Client0/120/123/0/0 and owner1505/1501/1501/1503/1501 respectively |

Five final receipts match frozen runtime sources. Only toybox-cat-probe.c and
opt-in cat-roles.rs branches differ from the preceding usage milestone. Other
runtime inputs, SDK libc/receipt/tool-lock, all standards pins and all UL-059 bundle
artifacts remain unchanged. No kernel ABI, grant, quota or sibling was changed.
The finalizer ELF is86,344 bytes,22 load pages and4-byte TLS; largest fresh owner
is6,056 bytes within8,192. These are artifact sizes, not peak-memory/performance
measurements. owner-artifacts.json records exact owner sizes/hashes.

backend-check.json proves the retained finalizer backend bytes equal the backend
freshly rebuilt by this full command suite. Every finalizer owner and probe is
rebuilt. Untouched Toybox baseline objects are verified and reused; a fresh complete
upstream rebuild remains separate coverage, not implied by this run. The real
musl callback and xwrap adaptation are rebuilt per case with retained source/patch
identity. Upstream notices and immutable baseline inputs are preserved.

qualification.json binds source/SDK/UL-059 checks. final-artifacts.tar.gz retains
sources/, run-native.py and all five output trees; archive-check.json verifies
source/recipe bytes. ISO, installed boot duplicates and kernel.elf are omitted
while receipt hashes remain. Reproduce with run-native.py and the exact invocations
in usage/errors/cat/command-timing.json; host command is
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Unchanged isolated stdio/startup and unrelated kernel profiles were not rerun;
selected native modes cover the shared probe/owner paths. Extended and assembled
R1 evidence remain open.

## Consumer compatibility and next action

[Captured consumer review](consumer-review/review.json) records read-only current
userland inputs. Its normal-copy native checkpoint now passes locally. That is
owner-authored existing evidence, not a new consumer run or sign-off here.
CAT-06 still needs a final close-error diagnostic while diagnostic authority is
live, uncertain close and diagnostic-failure coverage, and an agreed re-entry
terminal policy. This slice retains the prior no-final-close-diagnostic behavior;
the private hook returns120 on repeat while the outer cleanup can still return0.
Do not describe that as complete CAT-06 or recursive/signal-safe exit support.

Next resolve those exact bounded CAT-06 gaps, then fresh complete producer rebuild
and independent consumer intake. General signal delivery remains outside this
profile. Preserve the full R1 serial-shell/runner/persistent-filesystem/package
roadmap; no release readiness or narrowed acceptance is claimed.
