# Initial base-program provider matrix

UL-064, 2026-09-05. Reference for contributors selecting the experimental script
and TTY base. This is a candidate plan, not an install manifest or a supported
POSIX distribution. Read [package direction](PACKAGES.md) and the
[native compatibility inventory](../compatibility/README.md) first.

## Provider decisions for evaluation

Keep dash 0.5.13.5 as the pinned system-shell experiment and Zsh as the interactive
destination. Evaluate an explicit Toybox applet allowlist for ordinary utilities.
Select external providers separately where that candidate does not cover our needs.
The plan below selects evaluation order; source authentication, builds, dependency
closure, licenses and target tests still determine package admission under UL-011/016.

Toybox's upstream 0.8.14 status page lists the ordinary file/text commands used
below as completed, but lists awk, stty, tr, expr, diff, its shell, more and vi as
partially implemented. Do not enable pending applets just to fill a manifest.
Upstream completion is not Aether portability or full POSIX conformance.
[Source: upstream status](https://landley.net/toybox/status.html).

Use dash builtins inside scripts where appropriate. External programs still need
executable forms of utilities such as printf and test; a builtin alone does not
satisfy every caller. The [pinned builtin source](base-programs/dash-builtins.def.in)
and configured UL-034 builtin table establish presence, not tested native behavior.

## Command matrix

Each BP ID is a stable requirement group; acceptance examples are planned, not run.
All new utility providers below have native status **not tested**.
UL-065 now supplies [Clang/musl Linux-reference results](../../experiments/toybox-reference/README.md)
for Toybox cat/wc/printf/test/true/false; this does not promote native status. Dash has twelve
Linux-reference outcomes only. No shell or utility tier is promoted here.

Prerequisite labels: **IO** = general libc streams/errors; **PATH** = delegated
namespace, cwd and metadata; **PROC** = execution, inheritance and collection;
**PIPE** = pipes and signals; **TTY** = termios and session authority. Current
bounded probes do not satisfy these labels in full. Test all failures in an owned
scratch namespace and preserve upstream statuses and output contracts.

| ID | Command | Provider to evaluate | First required behavior and denial/control | Prerequisites |
| --- | --- | --- | --- | --- |
| BP-01 | sh | dash, existing pin | Existing shell cases plus ENOEXEC fallback, FD >=10, failed redirection cleanup | IO PATH PROC PIPE |
| BP-02 | printf | dash builtin; external Toybox | Literal format, escapes, empty arguments; output failure cannot succeed | IO PROC |
| BP-03 | test, [ | dash builtins; external Toybox | String/integer/file tests, false versus syntax failure, closing bracket | PATH PROC |
| BP-04 | true, false | dash builtins; external Toybox | Exact success/failure status through direct external execution | PROC |
| BP-05 | echo | dash builtin; external Toybox | Basic text only in owned scripts; prefer printf for escapes/options | IO PROC |
| BP-06 | pwd | dash builtin; external Toybox | Logical/physical cwd and unavailable directory handling | PATH PROC |
| BP-07 | cat | Toybox | Binary/empty/multiple input, partial writes; read error and broken output | IO PATH PROC |
| BP-08 | wc | Toybox | Byte/line counts, missing final newline, empty input; read failure | IO PATH PROC |
| BP-09 | head | Toybox | Selected line/byte limit, empty input; early reader exit with no writer leak | IO PATH PROC PIPE |
| BP-10 | tail | Toybox | Last lines/bytes and nonseekable input; missing file. Follow mode is a later option. | IO PATH PROC PIPE |
| BP-11 | grep | Toybox | Basic/extended/fixed matching, no match versus error, invalid pattern | IO PATH PROC |
| BP-12 | sed | Toybox | Substitution/address/script file, invalid expression and write failure | IO PATH PROC |
| BP-13 | sort | Toybox | C-locale tab-separated keys, duplicates; temporary-storage exhaustion | IO PATH PROC |
| BP-14 | ls | Toybox | Directory entries and metadata; denied traversal and hostile filename display | IO PATH PROC |
| BP-15 | cp | Toybox | Exact bytes, mode policy and partial-copy failure; symlink/destination races | IO PATH PROC |
| BP-16 | mv | Toybox | Same-filesystem rename; explicit cross-filesystem failure/copy behavior | PATH PROC |
| BP-17 | rm | Toybox | File removal, missing file, denied parent; recursive link boundaries | PATH PROC |
| BP-18 | mkdir | Toybox | Creation, parents, umask, existing nondirectory and denied parent | PATH PROC |
| BP-19 | rmdir | Toybox | Empty directory only; nonempty/denied removal preserves entries | PATH PROC |
| BP-20 | chmod | Toybox | Numeric/symbolic modes, umask interaction; metadata never grants native authority | PATH PROC |
| BP-21 | ln | Toybox | Hard/symbolic links; existing destination, denied source and link escape | PATH PROC |
| BP-22 | env | Toybox | Controlled environment and execution; missing/non-executable command | PROC PATH |
| BP-23 | find | Toybox | Type/link predicates, grouping and traversal; inaccessible subtree and link cycle | PATH PROC |
| BP-24 | awk | Separate provider review: One True Awk, mawk, gawk | Actual pkg-mgr scripts, tab fields, arrays, regex, numeric values, stderr path and malformed input | IO PATH PROC PIPE |
| BP-25 | stty | GNU coreutils candidate; compare BusyBox | Read/save/restore modes; unsupported request preserves state, stale/denied control | TTY IO PROC |
| BP-26 | tr | GNU coreutils candidate; compare BusyBox | C-locale deletion/classes, squeeze, binary bytes; output failure | IO PROC |
| BP-27 | basename | Toybox | Suffix removal, trailing slashes, empty input and operand boundaries | IO PROC |
| BP-28 | dirname | Toybox | Root, relative and repeated separators; no filesystem lookup implied | IO PROC |
| BP-29 | cmp | Toybox | Equal/different/truncated input versus I/O error | IO PATH PROC |
| BP-30 | cut | Toybox | Byte/field selection, delimiters and missing delimiters; invalid range | IO PROC |
| BP-31 | uniq | Toybox | Adjacent duplicates/counts, empty input; output error | IO PROC |
| BP-32 | tee | Toybox | Multiple outputs and selected append behavior; one destination fails | IO PATH PROC PIPE |
| BP-33 | touch | Toybox | Create/update times; missing authority and timestamp policy | PATH PROC |
| BP-34 | mktemp | Toybox | Exclusive private creation, collision and unsafe template rejection | PATH PROC |
| BP-35 | sha256sum | Toybox | Published known-answer vectors, missing/corrupt file; digest is not signer trust | IO PATH PROC |
| BP-36 | ps | Provider deferred until process observation contract | Granted process view, stale/foreign identity denial; no procfs assumption | PROC |
| BP-37 | kill | dash builtin first; external provider review later | Correct signal delivery and target denial, not merely command return status | PROC PIPE |
| BP-38 | expr | GNU coreutils candidate only when scripts require it | Numeric/string/operator boundaries and false/error distinction | IO PROC |
| BP-39 | diff | GNU diffutils candidate for development needs | Same/different/error status; no unsupported algorithm/option claim | IO PATH PROC |

Dash also supplies cd, read, getopts, command, exec, export, readonly, set, unset,
shift, trap, wait and other shell state operations. They belong to the shell's
acceptance suite, not standalone rewrites. Grammar keywords are not external
packages. Job-control builtins in a compiled table do not establish TTY support.

## Why separate awk and terminal reviews

One True Awk is a portable C candidate with an upstream regression suite. Its
current source also has UTF-8 semantics and a best-effort maintenance policy;
review code-point versus byte behavior under our locale scope. Building it involves
a parser generator and a host table generator, which need their own pinned build
identities. Do not call it selected or more secure based on size or provenance
alone. [Upstream documentation](https://github.com/onetrueawk/awk).

Compare it with [mawk](https://invisible-island.net/mawk/) and gawk using the same
actual scripts, dependency review and failure cases. Keep Toybox awk outside this
first comparison because of its upstream pending status. No custom awk is planned.

GNU coreutils supplies documented tr and stty behavior. Its stty requires a POSIX
terminal interface, so importing it cannot implement our terminal service. Evaluate
only required programs and their closure; a source package choice need not mean
shipping every binary. [GNU command reference](https://www.gnu.org/software/coreutils/manual/coreutils.html),
[stty interface](https://www.gnu.org/software/coreutils/manual/html_node/stty-invocation.html).

BusyBox remains a viable comparison candidate, with its upstream licensing and
source-delivery obligations retained. No GPL provider is rejected just for being
GPL. [Upstream licensing](https://busybox.net/license.html).
Uutils remains deferred until a viable Aether Rust standard-library target exists;
its supported-platform matrix does not establish Aether support.
[Upstream platform matrix](https://uutils.org/coreutils/docs/platforms.html).

## Package workflows and privilege boundary

The current pkg-mgr README requires GNU-compatible make and a SHA-256 tool. Its
inspected mk scripts already use awk, tr, sed, sort, cmp, find and mktemp. In
particular, awk diagnostics use `/dev/stderr`, and index checks require tab-key
sorting under LC_ALL=C. These are concrete compatibility cases, not an exhaustive
command trace. A target port must provide or explicitly adapt the stderr path;
never give awk an ambient device namespace merely to satisfy that spelling.
[Inspected input identities](base-programs/review.json).

Keep host build tools separate from the boot payload. GNU make, archive/extraction,
patch, compiler and signature-tool needs require an exact pkg-mgr workflow audit
before any target inclusion. Do not replace its recipes or trust verification here.
The package owner has a host bytecount package; that does not prove native package
execution. A SHA-256 utility does not replace signature/key/freshness policy.

The first Toybox build should start with no applets enabled and add only the reviewed
list. Avoid privileged applets, network services and Toybox init/login/shell in this
profile. A multicall binary must receive only the grants needed for its admitted
command. Its shared executable hash and argv[0] do not independently authorize
another applet; the launch owner must bind the command identity and grants together.
Whether packaging uses multicall links or separate executables remains a measured
build/authority decision. Do not change the broker contract in this research slice.

## Ordered acceptance work

1. UL-065 completed the initial reference slice; see the results above. Its scope
   was to pin and inspect Toybox candidate source, licenses, build helpers and
   selected config. Start with cat, wc and external printf/test/true/false. Build
   offline with pinned Clang/musl, inspect imports and run upstream plus independent
   Linux-reference cases. Record counts, omissions, exact exits and failure controls.
2. UL-066: pin awk comparison inputs and run actual package-script witnesses with
   a frozen locale/environment. Review GNU tr/stty and BusyBox source/closure before
   choosing versions. Retain maintenance, security-fix and provenance findings.
3. Extend per-command option and native-interface inventories. Add PATH/text programs
   only when their real prerequisites are available; UL-063 still precedes UL-058
   native harness edits. Use the existing shell-case IDs for pipelines and cleanup.
4. UL-005/012/016: hand exact artifacts, command paths, modes, links, dependency and
   license manifests, source trust, manuals and tests to packaging/assembly owners.
   Only exercised target commands can become supported base members.

This completes the initial provider matrix, not UL-011's build, security and
compatibility review. Independent technical review remains pending. No target
command, runtime-service ownership or release pin changes in this slice.
