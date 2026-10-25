# Awk package-script comparison (UL-066)

2026-09-06. Reference for contributors selecting the experimental base awk.
Three source-pinned providers build with Clang 21.1.8 on macOS arm64 and each
passes eleven identical package-script fixtures. These are host results, not
Clang/musl, Linux, native Aether or complete upstream-suite results.

| Provider | Exact input | Consumer cases | Host executable bytes |
| --- | --- | --- | --- |
| One True Awk | 5739fd79bcfc75ba7526773d0cf634521f8aca3c; reports 20260426 | 11/11 | 182,888 |
| mawk | 1.3.4-20260302 | 11/11 | 201,688 |
| gawk | 5.4.0 | 11/11 | 1,154,296 |

Sizes are unstripped files from the recorded host builds, not peak memory, target
footprint or a security/performance ranking. All three inspected binaries link
only libSystem.B.dylib. Source bytes, tool identities, commands and dependency
inspection are retained in [evidence](../../docs/evidence/awk-comparison-2026-09-06/summary.json).

## What ran

The [consumer snapshots](pkg-mgr) preserve four actual pkg-mgr awk programs and
its license. [Consumer hashes](consumer.lock.json) bind them before execution;
no sibling source was changed. These scripts cover:

- Valid package names, duplicate and invalid-name rejection, incomplete build
  evidence rejection, exact diagnostics and status.
- Plain ASCII, ESC/tab escaping, valid UTF-8 bytes, invalid high bytes and list
  presentation under LC_ALL=C.
- Update version/add/remove/content/mode/dependency differences.
- Three-way unchanged/package-only/local-only/matching/conflict/uninspectable
  decisions. The unchanged case must produce no output.

Fixtures have independent expected outputs. Only update-diff output is compared
as sorted lines because associative-array iteration order is unspecified; duplicate
lines still affect the comparison. Other outputs and all stderr/status values are
exact. The diff/three-way fixtures intentionally exercise prevalidated-record
consumers; they do not establish complete package-record validation or transaction
safety. Only state-schema's named modes are covered.

One True Awk's Unicode-capable implementation also passed the C-locale byte
escaping cases. We do not infer its behavior in other locales from this result.
All providers used the same local SDK, compiler flags and environment, with no
real-prefix installation. No test required a shell subprocess from awk.

## Build and reproduction

[Source pins](source.lock.json) were recorded after HTTPS acquisition and before
extraction/build. One True Awk uses an exact resolved commit rather than a moving
branch. Independent authentication, release-key policy, maintenance/security-fix
review and distribution eligibility remain UL-016. Build/test do not download.

Requirements: Python 3.12+, pinned Clang, make and Bison from
[tools.lock.json](tools.lock.json), and the recorded macOS SDK. From the repository
root after separate source acquisition:

1. Run `python3 -B experiments/awk-reference/build.py`.
2. Run `python3 -B experiments/awk-reference/test.py BUILD_DIRECTORY`, substituting
   the printed absolute build directory.
3. Run `python3 -B docs/quality/check.py` and inspect the retained records.

Each build phase has a 240-second deadline with owned process-group termination;
each fixed consumer fixture has 15 seconds. Logs and fresh outputs remain under
build/. The final build is `build/awk-build-enclpm4n`; final consumer run is
`build/awk-cases-i12rpcjt`. Missing tools, changed sources/binaries and mismatched
observations fail rather than count as skipped passes. No VM is used in this slice.

One True Awk generates its parser with host Bison and its dispatch table with a
host helper. Mawk uses the release configure/build inputs. Gawk disables dynamic
extensions, MPFR, NLS and readline; the resulting config and otool output confirm
this selected closure. Its normal internal matcher is retained. The first gawk
attempt requested its executable before support/libsupport.a existed; the final
build explicitly builds that subdirectory first. The failed attempt is retained.
No upstream source patch was needed. The entire host SDK/shared-library and
transitive host-tool closure is not hermetically pinned.

## Evaluation decision and remaining work

Prioritize mawk for the next static Clang/musl build and upstream suite. This is
an evaluation-order decision: the current C-locale package scripts need no GNU
extensions, and mawk offers dated source archives and a maintained changelog.
One True Awk remains the alternative; it passes the same consumers and offers a
small portable C implementation. Its upstream best-effort maintenance notice must
be part of the release-support review. Gawk remains the compatibility reference
and the candidate if an actual GNU-specific script requirement appears.

Do not call any provider the final system awk yet. Repeat these fixtures under
the pinned musl environment, exercise full applicable upstream suites, review
regex/resource bounds, parser failures, file/pipe/system calls and native runtime
needs. No performance or security winner follows from 33 host cases.

Licenses: retain One True Awk's Lucent permission/notices, mawk's GPLv2 terms and
gawk's GPLv3-or-later/per-file terms. Complete archives and COPYING/LICENSE files
are retained. Packaging recipes and this project's BSD-2-Clause default do not
relicense any provider. Source authenticators and security reporting/update
ownership require concrete review before supported distribution.

Technical inspection and test execution were performed in this task; independent
review remains pending. UL-066 stays active for musl/upstream testing and actual
tr/stty build comparison. No release or native compatibility tier is promoted.

## Static musl checkpoint — 2026-09-06

Mawk 1.3.4-20260302 now builds with the pinned Clang/LLD 21.1.8 and musl
1.2.6 Linux SDK. The static x86-64 ELF has no interpreter, dynamic section,
undefined external symbols or writable/executable load segment; its stack is NX.
These are file inspections, not Aether loader enforcement. See the
[build and runtime evidence](../../docs/evidence/mawk-musl-2026-09-06/summary.json).

The initial build failed the upstream POSIX-mode NaN comparison test. Configure
looked for linkable isnan/isinf functions without math.h; musl implements these
interfaces as macros. The build now compiles and links a C17 classification probe
against the exact SDK before setting ac_cv_func_isnan/isinf=yes. The runtime
acceptance also requires this probe to classify finite, infinite and NaN values
correctly. No upstream source, expected output or libc patch was made. The
upstream suite permits sign-only differences in printed NaN/Inf; that allowance
was exercised, while the initial comparison failure was rejected.

The corrected build passes ten mawktest groups, forty mawkerrs groups, fpe_test
and all eleven package-script fixtures under QEMU Linux. No suites were skipped.
Groups contain multiple assertions; fifty groups is not an assertion count.
The common consumer runner still passes all 33 host fixtures, and rejects an
empty provider set, a wrong-output provider and a changed binary hash. An initial
harness inventory check missed an indented Begin statement; that incomplete
attempt is retained along with the corrected run.

To reproduce after separately provisioning the existing pinned SDK/tool image:

1. Run `python3 -B experiments/awk-reference/build-musl.py`.
2. Run `python3 -B experiments/awk-reference/test-musl.py BUILD_DIRECTORY`.
3. Run `python3 -B docs/quality/check.py`.

The builder consumes the exact Toybox wrapper/SDK receipts named in its source;
it does not provision or install them. The runtime requires the existing Podman
VM and immutable local image, with QEMU and shell helpers. Each owned container
is offline, read-only except private scratch, unprivileged, limited to 512 MiB
and 32 PIDs, and removed on completion/timeout. See [the plan](MUSL-PLAN.md).

This completes the mawk musl reference slice of UL-066. Source authentication,
security/resource review, native file/process/pipe interfaces and packaging remain
open; GNU/BusyBox tr/stty build comparison is the next selection task. Mawk stays
a provisional candidate, not an accepted native system awk.
