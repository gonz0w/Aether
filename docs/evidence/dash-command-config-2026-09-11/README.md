# Ordinary dash command: native fork configuration

Actual dash now evaluates `/next; exit $?` without an explicit subshell. An opt-in
AETHER_NATIVE_FORK_EXEC guard in source-built jobs.c routes vforkexec through the
existing makejob/forkshell/shellexec implementation. The evaluator and wait3 path
remain upstream. This is an explicit shell build choice; libc vfork is not aliased
to fork and shared-address-space/suspended-parent semantics are not claimed.

The replacement verifies argv/environment, TLS, PID/parent, restored mask and
stdio with FD10/CLOEXEC removed, reads a and exits 72. Dash collects that real status
and exits 72. Two generations require backend17, three final backend closes each
and six reclaims. The unchanged owner stays within its 16 KiB code and one-page stack
bounds, six channels and three worker slots. /next names a fixed delegated image;
it does not perform persistent filesystem lookup or PATH search.

All 231 connections cases and five launch cases pass, plus host and format/pin/
workflow checks. The ordinary unconfigured branch exits 2 and rejects owner1950
before fork/reclaim. Leaked child CLOEXEC rejects child224/owner2130; corrupting the
actual wait status rejects parent73/owner2130, with zero reclaims. Generic panic or
timeout is insufficient. The four prior explicit-subshell cases remain regressions.
No failed build or target attempt occurred in this packet.

## Source and configuration review

inputs/jobs.c matches src/jobs.c in the retained reference source manifest under
shell-main-config-2026-09-09/inputs. The exact guard is inputs/fork-exec.patch;
jobs-native.c preserves upstream notices and COPYING.dash. The existing immutable
main-config snapshot supplies hash-verified headers, generated headers, config and
SDK includes. These retain their documented source-authenticity/generator/native-
configuration limits; they are not freshly authenticated or regenerated here.
No build follows a mutable sibling checkout. build.py verifies source/tool hashes
and retains commands, preprocessed output, imports and relocation disassembly for
original, patched-disabled and enabled objects. Original and disabled disassembly
match; the enabled object's only import removal is vfork, with no new imports.
Its helper calls forkshell and shellexec. disabled-comparison.json records equality.

The enabled jobs.o and pin live in user/native-command/dash-fork-inputs. The harness
verifies that pin on every selected link. Native ENV-guard main and the other 30
pinned dash objects remain unchanged. Final executable disassembly records actual
main/evaluator/vforkexec/forkshell, private musl fork/execve and wait3/wait4 calls.
The old unconfigured executable is a separate negative control. Kernel source,
ABI, existing dependency/standards pins and sibling repositories are unchanged.

SE-01–SE-05 review and the pre-code selection are in NATIVE-SHELL-STARTUP.md.
Implementing vfork introduces shared state and parent suspension beyond the current
requirement. Existing copied-process setup is smaller, already qualified and keeps
one owner. The guarded source change preserves the default branch for comparison
and avoids a fake libc compatibility shortcut. No new protocol, global process
state, service, allocation framework or unsafe kernel boundary is introduced.
Complex policy remains outside the kernel. This review is by the implementing
contributor; independent owner/reader approval is not inferred from passing tests.

## SDK and userland handoff

UL-007 SDK/runtime and userland owners can now review and independently reproduce
this bounded ordinary-command producer candidate. Start with manifest.json,
qualification.json and the complete connections-results.json, then verify sources
and artifacts against their indexes before restoring them into a fresh checkout.
The full sources.tar.gz includes the driver, owner, private staging adapters,
configuration object/pin and harness; run-sources records the frozen execution inputs.
Final documentation is captured separately in sources. This packet is not an
instruction to overwrite an installed SDK or consume mutable Aether source.

The selected case is
`copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command`; its -legacy,
-keep and -status variants are required semantic controls. The prior -dash case
runs the explicit-subshell command. Reproduce using the recorded command in
connections-timing.json (with fresh output destinations):

```sh
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The harness captures the exact private musl fork/_Fork, execve and wait3/wait4
build commands and patches in its artifact tree. fork-client.c stages descriptor
inheritance and the private copy/rebind path; exec-stage.h stages the existing
fixed-image replacement protocol. shell-client.h owns this bounded test's initial
bootstrap/environment and known terminal cleanup. These are fixture adapters,
not a production libc API or universal cleanup implementation. Do not install the
fixture's fixed authority, single-fork/descriptor limits or exit72/73 cleanup policy
as general SDK behavior. Review ownership, stable valid pointer assumptions,
mask/lifetime obligations and error handling before any broader integration.

The matching owner is AENMX002 / ABI17 with the unchanged three-image bootstrap,
existing endpoint/image/factory grants and signal-copy opt-in. AECAT003 startup
supplies scoped fixture identity/cwd; exec publishes AECAT001 plus survivor table
and mask. Publication, retained status and acknowledgments remain in the existing
user-space owner. Sys-init continues to own supervision policy and pkg-mgr package
installation; neither is replaced or implicitly activated by this handoff.

Independent SDK/userland execution and review are requested work, not recorded
acceptance. Ordinary native execution is now demonstrated for this one command;
full-dash acceptance still needs arbitrary pointer/path safety, failures and
recovery, live SIGCHLD, redirection/pipelines, interactive serial I/O and persistent
executable loading. No release readiness or complete POSIX/vfork claim is made.

## Evidence and cleanup

The source/artifact archives are read back against their hashes. compatibility
requires all prior 227 worker/owner payload bytes unchanged outside developer
entropy and identical kernel loadable bytes. owner-sizes checks existing versioned
limits. final-checks records host, format, workflow, standards and whitespace
checks, including the four-file simplicity snapshot. The manifest seals this
packet after verified duplicate-output cleanup. Current baseline outputs remain
unpacked; only superseded directories verified against preserved archives are
removed. Do not overwrite this packet when replaying helper recipes.

Final archive review added the companion navigation document, which was outside
the inherited source inventory. The corrected archive contains249 files; original
collection metadata and the correction are retained. Runtime inputs and artifacts
are unchanged. Both superseded unpacked baseline directories were verified against
their sealed archive and removed; cleanup.json records the exact paths and bytes.
