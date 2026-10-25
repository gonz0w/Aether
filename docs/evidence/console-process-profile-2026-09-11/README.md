# Serial transport in the process-owner layout

AENMX003 / ABI18 explicitly combines existing UART handoff with AENMX002's
three-image layout, 16KiB owner allowance, one-page stack, six channels and existing
worker quotas. Factory/image/channel registers are unchanged; R9 is the third
image grant. The initial owner additionally owns the existing console selector.
Old formats retain their old grants/limits. No new UART syscall, kernel queue,
TTY policy, dependency, SDK publication or sibling change is introduced.

The existing relay moves endpoint pairs to separate console and client domains,
then hands UART exclusively to the console. A real binary payload including NUL,
ESC and CR crosses COM1 and both domains and returns unchanged. Bootstrap and peer
UART access are denied. The recipient exits with its grant still open; third-image
workers use slots0,1,2,0 and are denied UART, including generations2/3 in the former
console slot. Six exact terminal/reclaim records are required. The final envelope
pads the small compiled relay owner to 16KiB, exercising all four mapped code pages.

All 301 selected QEMU cases pass: 231 connections, five launch, 23 init-large,
32 init-composed and 10 console cases across all five modes. Host, Zig/Rust/C format,
workflow and standards checks also pass. Wrong serial input requires peer74 and
owner941/reclaimed0. The deliberate generation-check omission produces fresh
slot0 generation2/detail71 then owner941/reclaimed2, proving that a closed flag
cannot mask the missing generation check. The mutation was repeated against the corrected witness; production enforcement
was restored after each isolated mutation and before final checks. Existing emergency and console-test markers remain.

## Attempts and test selection

The initial preflight completed binary exchange and three reclaims, then failed
the existing connections six-reclaim gate. The witness was extended; the first
full-round console case then exhausted the existing three-generation slot limit
at owner953/reclaimed4. The final witness distributes reuse across slots instead
of relaxing either limit. The original preflight and full-round failure, all
successful intermediate modes, and the expected generation mutation are preserved.
Two mutation-edit helper assertions rejected ambiguous source text before mutation;
the corrected edit was scoped to consoleOperation. No failed attempt is hidden.

Both qualified rounds froze their source inputs. The first round qualified the
kernel, full connections, launch and both init-capacity suites, plus the four old
console modes. Only user/native-console/relay.rs and scripts/console_smoke.py then
changed to correct the new console witness schedule/oracle. Neither is compiled
or imported by the launch_smoke.py profiles. Those profiles' kernel, harness and
all compiled sources remain identical. Their inventory-only hash differences are
explicit in profile-source-scope.json. All five console modes and host checks were
rerun after the correction. The eight passing old console cases from the first
round remain additional evidence, not double-counted in the 301 selected cases.

## Scope and next action

The requirement and SE-01–SE-05 review were recorded in NATIVE-CONSOLE.md before
implementation. An explicit format composes proven enforcement without silently
broadening existing process profiles. Reuse the existing relay and slot/generation
ownership checks, preserve all limits, and keep terminal policy in user space.
There is no new allocation framework, unsafe interface or catch-all kernel service.
The new format is a local producer contract, not a shared standards release or
independent consumer approval. Existing release and candidate object pins remain.

This proves serial authority is available in the shell's process-owner layout;
it does not wire dash stdin or establish an interactive shell. Next compose a
separately owned console backend with dash's shared stdio and process requests.
Raw UART EAGAIN must remain distinct from EOF; pending-input scheduling must not
starve child requests. Interactive startup, terminal policy, live signals and
recovery need their own executable evidence. Persistent loading and R1 assembly
remain open. Sys-init retains service startup policy; userland retains terminal
policy and pkg-mgr package installation. No owner/reader sign-off is inferred.

## Reproduction and evidence

Use the commands and pinned SDK/tools in timing records. The new case is:

```sh
python3 scripts/console_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Omit --connections for v1; --handoff, --handoff-fault and --relay retain old modes.
Run connections/launch/init-large/init-composed through launch_smoke.py with the
same SDK/tools. run-sources captures the first frozen round; console-run-sources
captures the corrected console round; sources includes final documentation. Each
suite receipt retains its own full inventory and exact commands/artifacts.
compatibility requires unchanged older process worker/owner payload bytes outside
developer entropy; kernel changes for the explicit profile are recorded. Source
and artifact archives are read back against hashes. Failed/first-console artifacts
have separate archives. final-checks includes the four-file simplicity pin check;
manifest seals this packet. Never overwrite sealed evidence when replaying recipes.
Only verified superseded unpacked outputs are removed, with paths/bytes/archive
hashes in cleanup.json. Current suite baselines remain unpacked.

Collection initially matched attempts.md while searching for attempt directories;
that failed helper and its error are retained. The corrected helper filters to
directories. Final source and artifact indexes contain251 and4867 files respectively,
plus separately indexed attempt/first-console artifacts. Twelve superseded unpacked
directories were verified and removed; current baselines and all archives remain.
