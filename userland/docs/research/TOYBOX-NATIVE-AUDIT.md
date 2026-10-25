# Toybox cat/wc native dependency audit (UL-067)

2026-09-06. Pinned-source and existing-artifact review only. Toybox0.8.14 remains a
candidate; neither cat nor wc runs natively under this work. The
[audit receipt](../evidence/toybox-native-audit-2026-09-06/verification.json) verifies
the release archive, ten reviewed source files against the archive,155 prior
evidence files, the recorded configuration/build receipt and original ELF.
The upstream notices are retained. No Toybox source or libc implementation changed.

## Findings by execution path

| Path in pinned source | Facilities actually reached or conditionally used | Native consequence / required witness |
| --- | --- | --- |
| Normal cat/wc: main → toy_singleinit | Both applets lack NOFORK; shared startup calls umask(0), restores it, selects locale, may create/use a UTF-8 locale, allocates4096 bytes for stdout and calls setvbuf | Standalone dispatch does not remove this setup. Establish truthful umask semantics, locale/error handling and allocator/stdio closure in the command profile; separate native memory evidence is insufficient. |
| Shared locale setup | Tries environment LC_CTYPE, then C.UTF-8/en_US.UTF-8 when codeset differs | LC_ALL=C in the launch environment does not imply Toybox keeps C character classification. Review the actual chosen locale, allocation/failure and Unicode cases. |
| cat without filenames or with `-` | loopfiles uses inherited stdin; do_cat reads up to4096 bytes (one byte for -u); ordinary output uses xwrite → writeall | No pathname open on this path. Require inherited input/output authority, real short-read/short-write/EOF/error handling and loss/no-replay tests; scope is narrower than full cat. |
| cat -e/-t/-v and help/version | printf/xputc/help/stdio paths and final flush; option/help handling occurs before normal shared startup setup | Direct-write-only evidence cannot qualify these buffered paths or diagnostics. Preserve upstream output/status behavior; no successful stderr no-op. |
| Both applets with filenames | loopfiles calls open with read-only/CLOEXEC, xnotstdio, then close; xnotstdio may dup and open /dev/null when an open returns FD0–2 | Requires a delegated namespace, actual descriptor ownership and explicit /dev/null policy. Names and FD values are not grants. No native pathname support follows from stream access. |
| Filename cleanup | loopfiles ignores close's return; xnotstdio also has unchecked closes | Source finding, not an exercised failure: a native cleanup-error guarantee needs a deliberate adaptation and failure witness. Do not claim Toybox preserves close errors merely because other helpers use xclose. |
| wc -c, including stdin | Attempts fstat; a nonzero regular-file size takes the metadata shortcut, otherwise upstream streams input | Honest unsupported fstat may take the existing streaming fallback. Test that fallback actually reads; never synthesize successful regular-file metadata. Real shortcut needs coherent type/size/offset semantics. |
| wc default/-l/-w | Read loop, isspace, counters and printf | Prove locale, arithmetic/input boundaries and formatting with actual selected libc; Linux-reference passes are not native evidence. |
| wc -m/-L | utf8towc, wcwidth and iswspace, partial multibyte handling | Additional Unicode/locale boundary; byte-count-only evidence does not qualify it. |
| Final xexit → _xexit | Runs registered callbacks, then fflush(0)/ferror(stdout), then _exit | Current native-entry only bootstraps and calls bytecount_main; bytecount itself owns finish() closes. Replacing that entry with Toybox does not supply cleanup, and code after a Toybox main call may never run. Flushing must precede closing buffered sinks. |
| Multicall dispatch / re-entry | toy_find/argv selection, fallback readlink and inventory terminal_size; toy_exec_which resets signals with recursion support/stacktop enabled, including initial dispatch | Standalone selection removes the multiplexer route at source level, but exact retained code requires a new build inspection. A shared image/argv name does not authorize another applet. |

Source anchors: [main.c](../evidence/toybox-native-audit-2026-09-06/upstream/main.c),
[cat.c](../evidence/toybox-native-audit-2026-09-06/upstream/toys/posix/cat.c),
[wc.c](../evidence/toybox-native-audit-2026-09-06/upstream/toys/posix/wc.c),
[lib.c](../evidence/toybox-native-audit-2026-09-06/upstream/lib/lib.c),
[xwrap.c](../evidence/toybox-native-audit-2026-09-06/upstream/lib/xwrap.c).
These findings identify candidate paths, not a complete call graph or security audit.
In particular, symbol presence is not proof every invocation calls that facility.

The current command native-I/O facade supports the bounded read/write/close path;
it does not provide a pathname/metadata/umask/locale service by adding declarations.
It has no general stderr role. Broader allocator, process and TTY profiles need
explicit composition/acceptance. Upstream errors must remain visible; unsupported
native calls cannot be made into successful stubs to get an applet to start.

## What standalone changes, and what it does not

Upstream [single.sh](../evidence/toybox-native-audit-2026-09-06/upstream/scripts/single.sh)
creates .singleconfig, disables the multiplexer for ordinary applets, carries
selected TOYBOX_* settings and invokes make.sh. main's standalone branch still
calls toy_singleinit before the one applet. This may simplify command identity and
remove dispatch-only reachability, with the standalone measurement now recorded below. The existing multicall ELF remains157,984
bytes and retains the reviewed startup/I/O/metadata symbols; its static link has
already resolved them to the Linux-reference libc, not Aether services.

Do not set NOFORK or bypass initialization just to avoid unsupported calls: that
would change upstream startup semantics and require its own reviewed patch and
failure tests. Do not narrow an advertised full applet silently. Any first native
invocation scope must name supported operands/options and truthfully reject others.
The current bytecount remains a separate small native experiment, not a Toybox port.

## Standalone comparison — 2026-09-06

The unmodified source now builds and passes in separate cat and wc configurations.
[Retained comparison](../evidence/toybox-standalone-2026-09-06/summary.json) includes
actual configs, object imports, defined symbols, tools, ELF checks and raw tests.

| Candidate | Static unstripped ELF bytes | Upstream cases | Independent cases |
| --- | ---: | ---: | ---: |
| Earlier multicall | 157,984 | 162 (reused evidence) | 22 (reused evidence) |
| Standalone cat | 79,888 | 9 | 5 |
| Standalone wc | 85,848 | 25 | 5 |

These are artifact sizes, not timing, runtime memory or security measurements.
Both new suites also reject a deliberately wrong expected output. Binary and empty
stdin, explicit dash, missing file and /dev/full are exercised. All upstream cases
were discovered with no failures/skips. Each candidate ran under the pinned local
QEMU Linux image in bounded, networkless containers with explicit cleanup.

The first two builds retained the hidden CONFIG_TOYBOX default and were rejected
by the configuration check. Fresh builds explicitly disabled that generated symbol,
as upstream single.sh does. Actual CONFIG_TOYBOX_FORK remains enabled despite the
miniconfig request; it matches the baseline and is not evidence of native fork.
Only the selected applet remains enabled. No upstream source was patched. Initial
runtime attempts could not access the Podman socket; retained attempts distinguish
that host restriction from the subsequent passing tests and cleanup.

Both standalone ELFs omit the baseline readlink and terminal_size symbols but
retain toy_singleinit, umask, setlocale, malloc, setvbuf, fflush, _exit and fstat.
Presence is linked closure, not proof that every path ran; cat's fstat is not an
assertion that its ordinary copy loop needs metadata. Standalone dispatch narrows
command selection without removing the shared startup and libc integration work.

## I/O fault checkpoint — 2026-09-06

[Retained fault evidence](../evidence/toybox-io-faults-2026-09-06/summary.json)
now exercises the standalone cat object code with link-time read/write/close
wrappers. A control relink reproduces the original ELF byte-for-byte. This is an
instrumented Linux-reference artifact, not an upstream patch or native witness.

| Injected return | Observed cat behavior |
| --- | --- |
| Reads capped at 3 bytes | Complete exact byte copy; exit 0 |
| Writes capped at 2 bytes | Complete exact byte copy; exit 0 |
| First read returns EINTR | No output; diagnostic and exit 1 |
| First write returns EINTR | No output; diagnostic and exit 1 |
| Two output bytes committed, then EIO | Exactly that prefix; diagnostic and exit 1 |
| Filename close reports EIO after real successful close | Complete output and exit 0; close error ignored |

The baseline copy also passes. Required injection markers and two deliberately
incorrect oracle expectations prevent unexercised faults from passing. Six host
UBSan controls check the wrapper's return values, one-time faults and real-close
call. Link-time wrapping targets external Toybox calls, not libc-internal buffered
I/O; EINTR is an injected return, not a signal-delivery test. The close case does
not model an uncertain remote close or a leaked descriptor. The first relink's
object order was wrong and its equality gate failed; another attempt exposed a
local hidden _DYNAMIC symbol. The final external-unresolved check matches the
original builder; ELF program headers remain recorded. Both attempts are retained.

These observations confirm the close-error gap and show that an Aether adapter
must deliberately decide where interruption retry belongs. Do not promise retry
or cleanup-error reporting from unmodified cat. Independent review remains open.

## Locale and buffered-output checkpoint — 2026-09-06

[Retained evidence](../evidence/toybox-locale-buffered-2026-09-06/summary.json)
adds eight Linux-reference cases and four host UBSan wrapper controls. The control
relink again matches the original cat ELF. Locale wrappers observe actual calls
and the codeset at first input read; allocation denials are injected returns,
not real memory exhaustion.

| Startup under LC_ALL=C | Observed result |
| --- | --- |
| Ordinary startup | setlocale succeeds; C.UTF-8 locale is created and selected; read sees UTF-8 |
| setlocale denied | Denial is ignored; C.UTF-8 is created/selected; copy succeeds |
| First newlocale denied | en_US.UTF-8 fallback is created/selected; copy succeeds with UTF-8 |
| Both newlocale calls denied | uselocale receives null and queries the current locale; read sees a non-UTF-8 codeset; copy still succeeds |

All four copies produce identical exact bytes and status0; exact traces distinguish
the otherwise silent failures. This is cat byte-copy evidence, not wc character
classification or general Unicode conformance. Host sanitizer controls use the host
C locale to check wrapper routing and lifetime; only the QEMU tests establish the
listed musl behavior. No change to global or thread locale policy is proposed here.

Uninstrumented cat -e also produces exact newline-marked output for 4-byte and
12,000-byte inputs. Each returns status1 with a no-space diagnostic when redirected
to /dev/full. These exercise small final-flush and multi-buffer error behavior;
no assertion about the exact failing syscall or flush timing is made without a
separate trace. They complement, rather than replace, the direct-write fault cases.
Two incorrect oracle expectations, three CLI checks, C17 warning/format checks and
the local quality gate pass. Independent review and native execution remain open.

## Next bounded work

Prefer cat for the first adaptation investigation: it has the smaller measured
closure and a simple byte-stream core. This remains a candidate, not package or
native-port acceptance. The direct I/O, locale-denial and buffered-output reference slices are now
recorded above. The [bounded native-cat proposal](../TOYBOX-NATIVE-CAT.md) now records the
minimal invocation scope, exact startup/flush/close/exit ordering and missing owner
interfaces. Next audit the exact native SDK startup/stdio closure and termination
seam before proposing a patch.

Native diagnostics authority, namespace scope and command identity still need the
owning contracts. UL-059 remains waiting for native local output roles; UL-003,
UL-007/008/016 and independent review remain open. No source-authenticity/advisory
review, POSIX conformance, security or performance claim follows. UL-067 remains
active and UL-069 deferred.
