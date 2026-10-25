# tr/stty provider evaluation (UL-066)

Contributor reference, 2026-09-06. GNU coreutils 9.11 is the leading evaluation
input; BusyBox 1.38.0 is the comparison input. Both source archives are pinned in
[source.lock.json](source.lock.json). No final package selection follows from
this source/build slice. See [the plan](PLAN.md) for tests and stage boundaries.

The official [GNU release announcement](https://lists.gnu.org/archive/html/coreutils-announce/2026-04/msg00000.html)
identifies coreutils 9.11. [BusyBox's release page](https://busybox.net/) identifies
1.38.0, released May 13, 2026, as unstable. The originally considered 1.37.0 was
superseded before acquisition; neither its bytes nor an old binary was consumed.
BusyBox's published SHA-256 matches the downloaded archive. HTTPS and matching
hashes establish these research bytes, not independent signer authentication or
security-fix completeness (UL-016).

## Source comparison

| Area | GNU coreutils 9.11 | BusyBox 1.38.0 |
| --- | --- | --- |
| Build structure | Separate src/tr and src/stty targets; shared src/libver.a and lib/libcoreutils.a (gnulib) | Applets plus shared libbb; select TR/STTY and required feature options |
| tr classes | Twelve classes including graph and print | FEATURE_TR_CLASSES required; ten named classes, graph/print absent in source table |
| tr repetition | Repeat-count parser and representation | Source explicitly excludes [x*N] and [x*] |
| tr byte processing | UCHAR_MAX + 1 alphabet | 256-entry alphabet; [:space:] expands ASCII whitespace |
| stty interface | termios and ioctl, generated speedlist.h | termios and ioctl through libbb helpers |
| Tests available | tr.pl, tr-case-class.sh; five stty shell suites | tr.tests plus five legacy tr tests; no dedicated stty test located in archive |
| License | tr/stty GPL-3.0-or-later; preserve gnulib/per-file notices | Distribution LICENSE specifies GPL version 2 only; preserve per-file notices |

These are pinned-source observations, not complete dependency or security audits.
The archive supplies all third-party source and notices. Applet size labels and
source line counts are not measured binary size, attack surface or performance.

The live pkg-mgr sources use `tr -d '[:space:]'` in boot/metadata/state scripts.
That narrow requirement supports testing both providers, but it is insufficient
for accepting a broader POSIX utility. BusyBox's absent classes/repetition keep
GNU first in the evaluation order. Explicitly test unsupported and malformed
constructs rather than allowing silent compatibility gaps.

BusyBox recover_mode scans saved-state fields with sscanf into unsigned values
and assigns them to termios fields. GNU's stty-invalid.sh has explicit overflow
regressions. This identifies a useful comparative malformed-state test; it does
not establish an exploitable vulnerability or a runtime failure in BusyBox.
Both need an actual terminal implementation. Never run upstream stty suites
against the user's terminal: some access /dev/tty and restore on completion.
Use an owned PTY/session and independent before/after termios measurements.

## Reproduction and remaining work

After separately acquiring the exact archives and provisioning the existing
pinned Clang/musl SDK, run:

```
python3 -B experiments/tr-stty-reference/build-gnu.py --uapi UAPI_BUILD_DIRECTORY
python3 -B docs/quality/check.py
```

The builder verifies source/tool/SDK hashes, extracts privately, configures the
Linux x86-64 target, disables optional NLS/ACL/xattr/capability/SELinux/Smack/GMP
integration, and requests only tr/stty. Shared gnulib configuration and build
closure still matter; two executable targets do not imply only two C files.
Cross-configure guesses remain in logs and need relevant runtime witnesses.
No real-prefix install or dependency download is performed by the builder.

BusyBox minimal configuration/build, common byte/error fixtures, upstream tests,
disposable PTY tests, source authentication/security review and native acceptance
remain separate acceptance steps. Independent review is pending. UL-066 stays
active; UL-008 and UL-012 own native TTY and packaging follow-ons.

## Build checkpoint

The first attempt (`build/coreutils-musl-7e_jpks_`) failed because direct
executable targets did not create required generated headers. The corrected
attempt (`build/coreutils-musl-gr9day6m`) explicitly completes Automake's
BUILT_SOURCES and reaches gnulib compilation. It then fails at
lib/copy-file-range.c:24: the verified musl SDK has no linux/version.h.

No GNU tr/stty ELF or runtime pass is claimed. The shared archive compiles code
beyond what these commands ultimately link; do not infer that tr itself calls
copy_file_range. Retained configuration guesses and compiler format-security
warnings also require review. Neither supplying a made-up kernel version header
nor suppressing function detection would establish a valid SDK.

UL-068 will provision a separately pinned Linux UAPI header set in a new reference
SDK view, preserving the existing verified musl SDK bytes, and rerun this build.
This is local toolchain work; no companion completion is needed. BusyBox build
closure may require that same header set and remains untested.

`test-gnu.py` and `cases.py` prepare seventeen Linux-QEMU checks, including four
private-PTY checks. Only syntax and runner rejection controls (empty inventory,
changed binary digest) have run. The actual seventeen cases and upstream suites
are NOT RUN until binaries exist. Execute the runner against the successful
printed build directory, then review its cases.json and container cleanup status.
[Retained evidence](../../docs/evidence/tr-stty-source-2026-09-06/summary.json)
records the incomplete builds and source-only findings.

## GNU runtime checkpoint — 2026-09-06

[UL-068's case-sensitive Linux UAPI export](../linux-uapi/README.md) supplies
verified Linux 6.18.49 x86 headers without changing the original musl SDK. The
GNU builder now requires `--uapi UAPI_BUILD_DIRECTORY` and validates the export
inventory, extraction receipt and case-sensitive filesystem before consumption.
Use the UL-068 reproduction sequence to mount the header view before building.

The completed build uses pinned Clang/LLD/LLVM ar/ranlib and the explicit
`--disable-threads` profile for these single-thread utilities. One intermediate
build used macOS archive tools and failed to link; the next linked but failed
strict ELF inspection on four optional weak gnulib thread probes. The final
single-thread configuration removes those unresolved probes without stubs or an
inspection waiver. No upstream C/header patch was made. These configuration
choices do not establish a profile for all other coreutils programs.

Final static Linux x86-64 ELF sizes are 123,016 bytes (tr) and 182,640 bytes (stty),
unstripped. No interpreter/dynamic section, unresolved external symbols, W+X load
segment or executable stack was found. File size is not a security/performance
ranking or native loader enforcement witness.

All seventeen independent checks pass under QEMU in the pinned offline image:
twelve tr byte/error cases, no-terminal failure, PTY save, echo disable, exact
termios restoration and malformed-mode rejection with unchanged termios. Actual
before/after states and expected observations are retained. The user terminal was
not touched; the PTY and container were closed/removed. Runtime kernel is Linux
6.18.10-200.fc43.aarch64; this is not native Aether, TTY authority, job control,
window-size restoration or complete POSIX acceptance.

[Evidence](../../docs/evidence/gnu-tr-stty-2026-09-06/summary.json) retains the
intermediate failures, final configuration, binaries, input identities and runtime
observations. Upstream test suites and BusyBox's build/common-fixture comparison
remain in UL-066. Source authentication/security review and independent reviewer
walkthroughs remain open; GNU is still a provisional provider.

## BusyBox comparison checkpoint — 2026-09-06

BusyBox 1.38.0 builds with pinned Clang/LLD and musl as one 87,056-byte,
unstripped static Linux x86-64 ELF. Generated applet inventory contains only
`tr` and `stty`; shell aliases, SUID and runtime installer support are disabled.
The first attempt accidentally retained a shell alias and failed final linking
because the compiler wrapper added startup objects to partial links. The final
builder explicitly disables the alias, handles `-r` without startup objects,
and checks the generated two-applet table. No upstream C source patch was made.
Static inspection finds no external undefined symbols, dynamic loader, W+X load
segment or executable stack. This is not a security or performance ranking.

The same seventeen Linux-QEMU fixtures yield thirteen matches and four `tr`
differences. GNU passes all seventeen again with the shared runner update.

| Fixture | BusyBox observed | Required by the comparison fixture |
| --- | --- | --- |
| Repetition | `ax*]` plus newline | `axxx` plus newline |
| Print class | Empty output | Space followed by `A` |
| Invalid class | Exit 0, no diagnostic | Exit 1, diagnostic |
| Reversed range | Exit 0, no diagnostic | Exit 1, diagnostic |

The common BusyBox run remains INCOMPLETE; expectations were not relaxed.
All five `stty` checks match, including private-PTY mutation and exact restoration.
These cases strengthen GNU `tr`'s provisional position; they do not select a final
`stty` provider or establish complete POSIX behavior.

BusyBox's unmodified focused `testsuite/tr.tests` passes all five tests through
an explicit QEMU/applet wrapper. The upstream harness compares stdout; it is not
an independent exit-status oracle. Its `/bin/echo` helper comes from the pinned
container, not the candidate. Legacy tr scripts and GNU upstream suites remain
unrun, and this archive has no dedicated stty test. Containers are offline,
resource-bounded and removed; the user's terminal is untouched.

Reproduce after mounting the verified UL-068 header view:

```
python3 -B experiments/tr-stty-reference/build-busybox.py --uapi UAPI_BUILD_DIRECTORY
python3 -B experiments/tr-stty-reference/test-gnu.py BUSYBOX_BUILD_DIRECTORY
python3 -B experiments/tr-stty-reference/test-busybox-upstream.py BUSYBOX_BUILD_DIRECTORY
```

The common runner's exit 1 is expected for the four recorded differences.
[Retained evidence](../../docs/evidence/busybox-tr-stty-2026-09-06/summary.json)
includes the failed build, corrected configuration, source archive and license,
binary, exact tools/commands, fixtures, upstream inputs and cleanup receipts.
BusyBox's unstable release label and independent source authentication/security
review remain selection concerns under UL-016. UL-066 remains active; next work
is the GNU upstream suite. Native TTY, packaging and independent reviews remain
UL-008, UL-012 and UL-061–063 respectively.

## GNU upstream tr checkpoint — 2026-09-06

The pinned coreutils 9.11 `tests/tr/tr.pl` passes **134 cases** with the existing
static musl GNU tr binary: 67 fixtures each using redirected stdin and a pipe.
Unmodified `Coreutils.pm` checks stdout, stderr and exit status. The runner
requires the complete named inventory and exit 0, so zero tests cannot pass.
A separate wrapper returning 99 exercises the same inventory and correctly fails
with exit-status mismatches and upstream status 1. Both containers are removed.

The first attempt lacked File::Compare in the pinned image's minimal Perl; the
second lacked the upstream-required CuSkip preload. Both stopped before tests and
remain incomplete in evidence. The successful runner loads archive-verified
CuSkip/Coreutils in upstream order. Its private 64 MiB scratch tmpfs supplies
isolation instead of upstream CuTmpdir; fixtures and comparison logic are unchanged.
Pure-Perl File::Compare 1.1006 and Text::ParseWords 3.30 are separately pinned from
local macOS Perl 5.34, with original notices and Perl license texts retained. They
run under the image's Perl 5.40.1 and are test-only dependencies. This is not an
installation of Perl or selection of Perl for the target userland.

```
python3 -B experiments/tr-stty-reference/test-gnu-upstream.py build/coreutils-musl-bdcrzzq6
python3 -B experiments/tr-stty-reference/test-gnu-upstream.py build/coreutils-musl-bdcrzzq6 --failure-control
```

The local helper files must match `perl-helpers.lock.json`; the existing pinned
image and source archive are required. No image download or header mount occurs.
[Evidence](../../docs/evidence/gnu-tr-upstream-2026-09-06/summary.json) retains all
six attempts, source/helper identities, raw observations and final runner snapshots.
The failure-control runner returns success only when the upstream failure is
observed; it does not mean the intentionally broken candidate passed.

The separate `tr-case-class.sh` and all five stty scripts remain NOT RUN. Reviewed
prerequisites define the next work: private controlling PTY and getlimits for
invalid inputs, private PTY for row/column checks, strace for the main script,
and a separate budget for expensive option pairs. `bad-speed.sh` uses LD_PRELOAD
fault injection, which cannot intercept this static ELF. Do not waive that
boundary or count a skip as coverage; design an appropriate fault witness before
claiming that error path. Source/security and independent reviews remain open;
UL-066 is active and no companion wait is needed for further reference tests.

## GNU shell and PTY checkpoint — 2026-09-06

GNU's unmodified `tr-case-class.sh` completes with status 0 using the pinned
static musl tr through QEMU. The image lacks `en_US.ISO-8859-1`, so the script's
conditional locale block is **NOT RUN**; its available C-locale cases pass.
The separate locale probe and shell trace retain this distinction.

All **eleven** upstream `stty-row-col.sh` checks pass on a new controlling PTY,
including decimal, hexadecimal and octal row values. Independent Python ioctl
and termios measurements confirm exact restoration of the initial 24x80 window
size and termios state. The same script with `/dev/null` stdin returns its
expected prerequisite skip (77), demonstrating that a missing terminal cannot
look like a successful test. This is reference Linux session behavior, not native
Aether authority or general terminal recovery acceptance.

The first run was marked INCOMPLETE because our marker checker expected uppercase
`OK`; upstream emits lowercase `ok`. The corrected runner requires all eleven
exact, ordered success lines, status 0 and restoration. Both attempts are retained.
Shell syntax checks pass, upstream temporary directories are removed, both PTY
descriptors close, and both owned containers are removed with cleanup status 0.
Host-image utilities provide test support; only tr/stty are candidate binaries.

```
python3 -B experiments/tr-stty-reference/test-gnu-shell.py build/coreutils-musl-bdcrzzq6 --getlimits build/getlimits-musl-eoy5yrnq
```

The runner checks binary/archive hashes, copies the tests plus upstream init.sh
and init.cfg unchanged, and uses a 64 MiB private scratch tmpfs in the pinned
offline image. Each script has 45 seconds inside a 180-second container budget.
[Retained evidence](../../docs/evidence/gnu-shell-2026-09-06/summary.json) includes
source snapshots, traces, runtime identities, before/after measurements and cleanup.
No host terminal or header image is used.

Next: provide the exact upstream getlimits helper for `stty-invalid.sh`. The main
stty script's tracing requirement, expensive option pairs, missing locale branch
and static bad-speed fault-injection limitation remain explicit coverage gaps.
UL-066 stays active; source/security, independent review, native TTY and packaging
acceptance remain separate follow-ons.

## GNU invalid-input checkpoint — 2026-09-06

The upstream noinst `getlimits` helper builds in a fresh private tree with the
same pinned Clang/musl/UAPI profile and passes strict static ELF inspection.
QEMU execution reports the target unsigned-long overflow boundary as 2^64.
This is a test helper, not a new selected userland program or installed package.
Rebuild after mounting the UL-068 header view:

```
python3 -B experiments/tr-stty-reference/build-getlimits.py --uapi build/uapi-volume/linux-uapi-1vb3wr6r
```

The extended shell runner above now requires `--getlimits`. It verifies the helper
binary receipt and runs `stty-invalid.sh` unchanged on a new controlling PTY.
The suite passes two saved-setting overflow rejections, all four `/dev/tty`
argument regressions and all twelve malformed speed values. Independent readings
confirm exact termios and window-size restoration. Existing tr shell cases and
eleven row/column checks still pass; no-TTY prerequisite control still skips 77.
The unavailable ISO-8859-1 branch remains untested.

Empty helper inventory and changed helper digest controls reject before container
launch. Scratch is empty, container cleanup succeeds, original musl SDK and 1,028
UAPI headers remain unchanged, and the private header image is detached.
[Evidence](../../docs/evidence/gnu-stty-invalid-2026-09-06/summary.json) retains the
helper binary/build logs, upstream inputs, exact invocation traces, restoration
measurements, rejection controls and source identities. Upstream diagnostics and
configuration guesses are retained, not a source-security audit.

Next: main stty tracing prerequisites and expensive option-pair coverage. The
static bad-speed injection and missing locale branch remain separate gaps.
UL-066 stays active with independent review, source trust/security, native TTY
and packaging acceptance still open.

## GNU extended stty findings — 2026-09-06

Add `--extended` to the shell-runner command to enable upstream `stty.sh` and
`stty-pairs.sh`. The latter gets 240 seconds; the owned container gets 420 seconds.
The four earlier script/control expectations still hold, but the extended run
correctly reports **INCOMPLETE**:

- Main `stty.sh` returns 0. Its final input-speed tests occur after its saved-state
  restoration and leave changed speed-related control flags (`c_cflag` 191 to
  852159). Our independent restoration check fails; window size is unchanged.
  The image has working strace, but tracing the host QEMU process is not an
  independent guest syscall or native Aether witness.
- The unmodified option-pair script completes with status 1 and 188 operation
  failures, all in commands containing `cmspar`. Its 9,029 traced stty calls
  include setup/restoration. Exact termios/window restoration succeeds. No options
  were removed to make the suite pass.

Six isolated parity requests narrow the issue: the candidate under QEMU cannot
set `cmspar`, while the image's stty can set it on a separate equivalent PTY.
Both can clear it. A combined candidate `parodd cmspar` request fails but applies
PARODD, showing that failure is not a promise of atomic rollback. This implicates
the candidate/configuration or emulation path rather than a blanket Linux PTY
limitation; it does not yet prove which component is responsible.

[Evidence](../../docs/evidence/gnu-stty-extended-2026-09-06/summary.json) preserves
both runs, traces, all failed pair commands, upstream sources, exact input
identities and before/after states. Scratch is empty, PTYs are closed and both
containers are removed. No user terminal, target install or sibling was touched.

Next: inspect pinned QEMU termios translation and candidate flag definitions;
measure explicit restoration separately from upstream script success. Missing
locale, static bad-speed injection and independent source/security reviews remain
open. UL-066 remains active; native TTY acceptance is separate.

## Reference emulator diagnosis — 2026-09-06

The pinned image reports QEMU 10.0.11 (Debian `1:10.0.11+ds-0+deb13u1`), host
coreutils 9.7-3 and strace 6.13. Candidate musl defines CMSPAR as `0x40000000`.
Three isolated trace/readback cases locate the observed loss in the reference
emulation path:

- Candidate `cmspar` reaches the host TCSETSW without that bit, then fails its
  readback check. The image's stty submits and retains the bit successfully.
- With CMSPAR seeded by the image command, host TCGETS includes it, but the
  candidate prints `-cmspar`. This demonstrates read-direction loss too.
- Explicit host restoration succeeds on all three private PTYs; cleanup succeeds.

The [upstream v10.0.11 source](https://gitlab.com/qemu-project/qemu/-/raw/v10.0.11/linux-user/syscall.c)
uses cflag_tbl for both translation directions and omits CMSPAR. This is consistent
with the runtime finding. The retained hash pins the downloaded upstream research
snapshot; it does not authenticate or rebuild Debian's exact source and patches.
[Evidence](../../docs/evidence/qemu-termios-2026-09-06/summary.json) contains the
source, notices, version output, host ioctl traces and measured restoration.

UL-069 now tracks a separately pinned reference emulator correction or replacement,
with set/read/clear, partial-failure and restoration controls before full suite
reruns. No QEMU patch, image upgrade or weakened expectation has been applied.
The 188 parity failures remain incomplete acceptance; they are not evidence of
an Aether kernel defect or a reason by themselves to reject GNU stty. Main-script
natural cleanup still differs from explicit recovery, and native TTY, locale,
static fault-injection and independent review gaps remain open.

## Legacy BusyBox scripts — 2026-09-07

All five pinned legacy tr scripts now exit0, and all five exit99 wrapper controls
are rejected under the corrected reference emulator. The non-gnu script has no
output oracle: its bracketed-range example prints `squc]kgsf ossgdr]ec`, failing
our supplementary ROT13 expectation. This additional finding stays incomplete
pending expression/source interpretation; it is not an upstream exit failure or
POSIX defect claim. No prior provider differences are waived.

Run `python3 -B experiments/qemu-termios/run-legacy.py` with the retained pinned
consumer prerequisites. [Evidence](../../docs/evidence/busybox-legacy-2026-09-07/README.md)
records all ten results, input hashes, cleanup and next investigation.

The supplementary bracket-range finding is now resolved by
[eight pinned-provider comparisons](../../docs/evidence/tr-ranges-2026-09-07/README.md).
Both providers agree on the original phrase and all256 bytes for both expressions.
Ordinary brackets are literal, so `[n-z][a-m]` is not the ROT13 destination `n-za-m`.
Our extra expectation was incorrect. The historical failed check is retained;
this is not a new BusyBox defect. Existing four provider differences remain.

## Static stty speed-error boundary — 2026-09-07

A private baseline relink matches the original candidate byte-for-byte. Separate
--wrap=cfsetispeed failure/pass-through fixtures pass three PTY cases: baseline
success, injected EINVAL with exact unsupported-ispeed diagnostic and unchanged
settings, and real-call success. All restore and clean up. Source confirms two
pass-through invocations (validation and application); the earlier one-marker
expectation failure is retained. [Evidence](../../docs/evidence/stty-speed-2026-09-07/README.md).

```
python3 -B experiments/qemu-termios/build-speed.py
python3 -B experiments/qemu-termios/run-speed.py build/stty-speed-build-kf8c9grr
```

This supplies a static caller-error witness; upstream bad-speed.sh itself remains
NOT RUN. Its LD_PRELOAD mechanism cannot intercept this static binary. The locale
branch still needs compatible pinned locale inputs and candidate qualification.

## Candidate locale qualification — 2026-09-07

[Ten observations](../../docs/evidence/candidate-locale-2026-09-07/README.md) establish
that the pinned musl candidate accepts the ISO-8859-1 name but reports UTF-8; an
invented name does likewise. C/POSIX report ASCII. GNU tr retains ASCII-only case
conversion for the supplied high-byte controls. Source audit matches these results.
The skipped ISO branch is unsupported by this candidate encoding profile, not
resolved by adding host locale data. It remains NOT RUN, with no forced prerequisite.
Reproduce with build-locale.py and run-locale.py in experiments/qemu-termios;
use the new build root as run-locale.py's argument. New helper review is pending.

## Consolidated review — 2026-09-07

[UL-066 provider review](../../docs/quality/PROVIDER-REVIEW.md) recommends continued
mawk and GNU tr/stty evaluation, with BusyBox as a comparison provider. It records
all known failures, unsupported profiles and pending source/native/package work.
The packet is pending acceptance; no runtime or provider promotion is implied.

## UTF-8 characterization — 2026-09-07

[Ten cases](../../docs/evidence/tr-utf8-2026-09-07/README.md) confirm byte-oriented
GNU tr behavior under C and C.UTF-8. Deleting literal é from éê! produces invalid
UTF-8; class conversion/deletion and squeezing do not satisfy the selected Unicode
character expectations. Characterization passes, Unicode operations do not.
The provisional candidate remains scoped to tested byte-oriented script needs.
The earlier reviewed provider packet stays byte-identical; these results are a
separate addendum. Reproduce with run-utf8.py and the retained locale-probe build.
