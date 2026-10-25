# UL-007 startup producer handoff — 2026-09-07

The unchanged userland startup prerequisite passes natively against this bounded
producer/SDK adapter pair. This is available for **independent userland intake**,
not native dash acceptance, SDK-owner sign-off or a release.

Start with [handoff.json](handoff.json), [the contract](../../NATIVE-SHELL-STARTUP.md)
and [preimplementation review](review.md). The original consumer source is
`user/native-command/startup-consumer.c` in the source archive; its digest matches
the captured userland `experiments/dash-native/startup.c`. A wrapper performs
AECAT001 role admission before calling its unchanged probe, then exercises native
alias I/O and supplementary state/denial checks. It is deliberately not dash.

## Qualified behavior

- Kernel caller identity is stable within a lifetime and changes with generation.
  The public getpid adapter uses the real native query; IDs confer no authority.
- Public sigaction DFL/IGN and sigprocmask operations round-trip real local state.
  Unsupported custom handlers and flags reject explicitly. No asynchronous signal
  delivery, pending queues, signal-aware waits or internal musl-mask adoption.
- Three inherited capability-bound streams seed descriptors 0–2. A sixteen-entry
  local table supports lowest-index duplication, CLOEXEC flags, exhaustion and
  last-alias remote close. Actual I/O through an alias survives closing FD0.
  No fork/exec, concurrent mutation or exec-time CLOEXEC enforcement is provided.

Nine new target cases pass: normal, four producer mutants, and four malformed
bootstrap cases (rights, FD, stale generation and missing role). The unchanged
consumer exits zero in both normal generations; the owner independently checks
exact stream content, all remote closes, terminal kinds and four reclaims.
Mutants fail at exact consumer stages 10 (PID), 20 (disposition), 21 (mask), and
30 (missing CLOEXEC), followed by the expected owner rejection. Malformed admission
returns 110 with no public FD/signal state or client I/O publication.

The full final command-runner suite passes **222 cases**. Another **41 cases**
pass in both memory profiles (12/13), large image (9) and M4 (7). Those unaffected
regressions used identical final kernel bytes before the wrapper's TLS fix and
case ordering change; their original source receipts remain separate. Host tests
(98 Python tests plus Zig/pins/workflow, 41 groups), scoped formatting and diff
checks pass. [Qualification](qualification.json) preserves profile receipts and
source differences. No independent rebuild, consumer review or full standards
conformance is claimed. The legacy harness records commands/hashes/raw logs but
not complete per-case wall-clock events; broader evidence-format coverage remains
an open process limitation.

## Reproduce and consume

1. Verify this packet's [manifest](manifest.json) and the hashes in handoff.json.
2. Safely extract producer-source.tar.gz into a private directory. It includes
   503 source/build/offline dependency and standards inputs. Planning prose in
   that frozen snapshot precedes final qualification; this record and current
   repository STATE carry the final result.
3. Verify and safely extract the referenced SDK archive from the retained SI-06
   packet. All 4,311 regular SDK files were checked against the SDK used here.
   Its repaired relative Makefile link is already retained there; no SDK source
   or sibling repository was modified for this delivery.
4. From the extracted source root, run `zig build test --cache-dir .zig-cache
   --global-cache-dir .zig-cache/global`, then `python3 scripts/launch_smoke.py
   --command-runner --libc-build /absolute/extracted/native-c-5olokhku
   --tools-lock /absolute/path/to/tools.lock.json`. Provide the pinned local tools;
   builds do not fetch a mutable SDK or update release pins.
5. Independently rebuild the startup consumer, inspect its exact stage exits and
   owner cleanup observations, and record acceptance in userland. Public adapter
   interposition and explicit bootstrap are required; stock SDK symbol availability
   alone is insufficient. Kernel/adapter/source/envelope must remain a matched set.

[Source verification](source-check.json) and runtime.patch separate this change
from earlier uncommitted work. target-artifacts.tar.gz retains all five complete
successful target directories, with every regular file verified in
[target-artifacts.json](target-artifacts.json). The positive envelope, ISO and
serial log are also directly available through handoff.json. These are internal
startup-test artifacts, not an interactive-shell release image.

[Attempt 1](failures.md) failed before startup execution because the wrapper lacked
the loader-required TLS segment. The correction adds the same private TLS witness
used by existing clients; the loader is unchanged. Its original source, complete
target directory and failed log are retained. No failed case was relabelled a pass.

Next gates: SDK/userland intake, actual dash handler-dependent initialization,
then fork/exec/wait and pipe/redirection workloads. Existing SI-06 and UL-059/067
handoffs and all release pins remain intact. No sibling implementation or approval
record was changed.
