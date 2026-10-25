# Matching command-runner qualification — 2026-09-14

Requirement: complete the unchanged 431-case command-runner suite on the exact
265-source inventory qualified by [suspend recovery](../suspend-recovery-2026-09-14/README.md).
That sealed packet retains the previous 1800-second timeout at 429 started cases;
no final result was produced. Do not infer success from partial logs.

Before execution: wait for the two observed independent consumer suites to finish,
then retry with a 3600-second outer deadline. Individual build/QEMU watchdogs,
case selection and semantic failure oracles remain unchanged. A deadline overrun
is a failed/incomplete attempt, never an accepted negative control. The previous
run competed with other suites; this is a plausible timing contributor, not a
proven diagnosis or performance qualification. The documented 1800-second review
ceiling remains applicable; report and investigate any completed overrun.

No runtime, ABI, authority, ownership, dependency, SDK or released pin changes are
planned. Preserve prior archives. Freeze source bytes through the run and bind the
results to the prior inventory, SDK and tools identities. Verify every target file
against its archive before removing this attempt's redundant unpacked directory.
Update STATE, roadmap and the existing companion handoff with the actual result.
Independent owner acceptance and broader signal/filesystem/release gaps remain
separate. This is a qualification retry, with no new runtime abstraction or feature.

## Bounded replay intake

This packet is pending qualification until `qualification.json` records the
complete result and SHA256SUMS seals it. Do not use an in-progress directory as
an accepted handoff. After completion, `inputs.json` will pin the preceding
recovery source/result archives, the existing archived SDK, and this packet's
support inputs. No target or SDK archive needs to be copied into a new packet.

For independent replay, verify all referenced hashes, restore `support.tar.gz`
first and the pinned recovery `sources.tar.gz` second into a fresh owned directory.
Use a confined extractor: reject absolute/traversing paths, special files and
escaping links. Verify every restored entry against support-files.json and
sources.json. Restore the archived SDK separately, preserving its confined
`obj/Makefile -> ../musl-1.2.6/Makefile` link and third-party terms.

With the restored Aether root as the working directory, use the existing commands:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /absolute/private/sdk/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /absolute/private/sdk/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Use the pinned tool identities, external tool setup and offline boot inputs.
Run the two target suites sequentially, retaining logs, results, artifacts and
all failures. Host deadline: 300 seconds. Target outer deadline: 3600 seconds for
this retry; report elapsed time against the existing 1800-second review ceiling.
Per-case build and guest watchdogs remain unchanged. Never silently fetch inputs.
The expected complete counts are 316 connections and 431 command-runner cases;
verify each semantic oracle and frozen source hashes, not merely process exit.

The unchanged dash wait.sh runs a background helper returning 7, waits for that
PID, checks status 7 and prints `wait ok\n`. Producer traces require helper7,
dash0 and backend17 across two generations, six reclaims and exact output.
Failure controls qualify missing suspension, ordering, stop/reuse, stale-parent
notification isolation and failed-frame retry. Each applies only to its named
bounded fixture; this is not arbitrary shell process or signal compatibility.

Userland owns independent consumer acceptance and the UL-081 supported SDK
boundary. Consume the complete matching fixture/owner; do not install the private
adapters as stock libc. Terminal-derived SIGCHLD and handler-only sigsuspend are
opt-in; default termination during suspension, nested delivery and eventual
unblocking of blocked posts remain gaps. Fixed executable routes are capability
grants, not persistent path lookup. Writable filesystem workflows, OpenZFS,
package management, sys-init assembly and interactive R1 remain separate work.

## Existing consumer coverage

Userland records 13 passing focused native cases and separate serial comparisons
in its `docs/evidence/dash-wait-consumer-2026-09-14` packet, using the preceding
suspend-stale source set. `consumer-reference.json` pins the read-only evidence
checked here. That is bounded prior consumer acceptance; the two new stack-frame
controls and complete matched suites are not covered by that receipt. Independent
technical review and the public SDK boundary remain pending. No sibling was edited.

## Completed qualification

All 431 command-runner cases pass in 1434.00 seconds on the same frozen
265-source inventory, SDK and tools as the prior 316-case connections run.
The restored source/support package passes host checks using existing shared
compiler caches. This closes the matching producer-suite gap, not independent
consumer acceptance. The previous timeout remains sealed in the recovery packet.

This run completes within the existing 1800-second review ceiling. The prior
timeout remains an incomplete attempt; the new result does not retroactively pass it.

The support archive captures pre-result progress documentation. This README and
current STATE supersede that historical status; runtime sources remain identical.
