# First libc exec staging witness — 2026-09-11

The actual source-built musl execve wrapper calls a private staging hook and uses
upstream __syscall_ret for error conversion. The real C caller observes ENOTSUP
for an unsupported mask, ENOENT for an unknown path and EACCES after denied native
image admission. Rejected exec preserves FD1/FD10 CLOEXEC and the next input byte.
Successful /next replaces the image without returning; the replacement validates
argv/env and its survivor descriptors, reads c and exits62. Two generations reclaim
six domains. All205 connections cases, five launch cases and host tests (99 Python,
five Rust descriptor tests) pass. False-return and retained-CLOEXEC controls require
client220/owner1950 and client216/owner2040 respectively, with zero reclaims.

## Scope and implementation

Pinned musl 1.2.6 execve.c retains its original signature and body structure; only
the native syscall expression becomes the staging call plus musl error conversion.
The verified archive supplies private headers and COPYRIGHT. No installed SDK,
sibling repository, kernel, dependency or release pin changes. Private upstream
compilation follows the existing upstream warning policy; first-party clients
retain -Wall -Wextra -Werror. The pre-code selection is in NATIVE-SHELL-STARTUP.md.

One context with all blockable signals already masked and valid stable pointer
buffers is required. Other mask states return ENOTSUP before traffic. Only the
owner's fixed /next image authority and /denied rejection control are selected;
unknown paths return ENOENT. The wire carries the caller's path, bounded argv/env
record and descriptor snapshot before freeze. Native commit validates the argument
record, retains identity and feeds the real new-image startup stack. This is not
arbitrary pathname lookup, threaded/pointer-fault-safe execve, signal-unmasked exec,
consumer acceptance or release readiness. Mask guard/restoration and broader
consumer-required contracts remain the next work. No retry or recovery is claimed
for unknown completion.

## Failed attempts

All five full attempts are retained with frozen sources, logs and complete artifacts.
The first four stopped before connections target execution; host and launch passed
in all five attempts.

1. The installed public syscall.h shadowed the internal __syscall_ret declaration.
2. A textual include correction mistakenly affected the existing rebind build;
   it was restored before proceeding.
3. Pre-including internal syscall.h expanded a macro inside unistd.h's declaration.
4. -I did not override the same directory's system classification. Direct preflight
   failed and the shell continued into a full attempt with the same compile failure.

5. The first native request rejected2110 with zero reclaims. Diagnostic triage1
   separated the argument read as2112; triage2 observed raw EINVAL. The272-byte
   record exceeded the existing256-byte channel request limit. Bounded reads fix
   it without a kernel change; triage3 passed both generations. Each triage directory
   retains the changed owner source, commands, artifacts and serial output, based
   on attempt5's otherwise unchanged sources. These are diagnostics, not substitutes
   for the complete final suite.

The final quote-only search path preserves upstream include order and passes the
recorded wrapper preflight. The full suite is rerun on corrected frozen sources.

## Integrity and reproduction

Commands, timings, tools and source/artifact hashes are retained in results and
snapshots. Reproduce using the complete connections and launch commands in
NATIVE-CONNECTIONS.md with the recorded SDK/tools lock. libc-inspection.json and
linked disassembly verify main calls execve, and execve calls __aether_execve_stage
then __syscall_ret; both public-wrapper and deliberate broken-stage artifacts are
identified. Generated original/patched upstream sources and object files remain
in the full artifact archive. run-sources captures execution bytes; sources adds
final documentation. Archives are read back against recorded hashes.

change.patch compares the previous shared-close packet. compatibility.json checks
all202 prior cases: kernel load segments and entry match, with only nonloaded
.debug_line differences permitted. Changed exec owner payloads are listed explicitly;
other payloads match outside developer entropy. qualification.json records counts
and bounds. final-checks.json retains host, format, workflow, standards and diff
checks. collect.py verifies the prior sealed manifest and four-file simplicity
snapshot. manifest.json seals this packet and all attempts. Independent reader and
matching-revision SDK/dash acceptance remain pending.
