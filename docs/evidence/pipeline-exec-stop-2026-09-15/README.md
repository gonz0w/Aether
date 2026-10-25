# Interrupted pipeline exec cleanup — 2026-09-15

The copied-pipeline exec fixture now cancels the whole pipeline at two boundaries:
after the first replacement image is admitted but parked, and after publication
with exactly seven filtered-table bytes delivered. The first replacement must
remain unready. The owner requests stop of all three participants, observes each
exact kind3/status143 terminal, rejects publication of the stopped image, then
removes both pipes' participant holdings, clears local table frames and retires.
No pipe data dispatcher runs in the cancelled generation. Parent/capacity peer
exit normally. Three generations require nine stops, six normal exits and fifteen
reclaims; nine image-load records include six initial and three replacement loads.

## Qualification

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes all21 native cases on274 frozen inputs. Target case total is
55.973 seconds. Existing eighteen cases retain their exact outcomes.
New pipe-exec-stop-admit and pipe-exec-stop-table pass. The pipe-exec-keep-holder
mutant skips one participant's holder removal after confirmed native stop;
retirement must reject owner2736 with zero reclaims. No timeout or generic panic
qualifies that control. There were no failed attempts; intentional rejection logs
remain preserved with exact sources and artifacts.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0 and host.log records104 passing host checks. final-checks verifies pinned
Rust/C formatting, workflow/standards/experience, simplicity manifest and all four
members, whitespace and frozen sources. Commands, tool/SDK identities, timestamps,
ISOs/envelopes and serial hashes are bound in attempt-1-results and its archive.

## Compatibility, resources and limits

Only copies.rs, owner.rs and pipeline_capacity.py change among runtime inputs.
No kernel, shared pipe-core, C worker, SDK, dependency, quota, sibling repository
or released pin changes. compatibility.json records 22 prior top-level ELF/raw
images, with 22 byte-identical. New admission-stop owner9232, table-stop10664
and retained-holder10696 remain below16384. Existing native stop and borrowed-buffer
contracts are reused; no unsafe boundary is added. Channel cleanup and zeroing are
independently required by the enclosing native completion/reclaim path.

This is a deterministic cancellation witness, not detection of arbitrary missing
receipts or production shell policy. The validated tables remain private fixtures;
actual libc descriptor installation/rebind, unchanged dash scripts, SIGPIPE,
additional interruption schedules, full matching suites and independent intake
remain open. Persistence, packages and sys-init assembly remain R1 work. No
full-shell handoff or release-readiness claim follows.

The preimplementation review is in NATIVE-SHELL-STARTUP. Source and review-input
archives preserve runtime and local guidance/test support. collect.py verifies
every generated file against its archive before removing only this attempt's
private output root; cleanup.json records the removal. Prior sealed evidence is
untouched. SHA256SUMS covers this packet except itself.
