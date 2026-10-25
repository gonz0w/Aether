# Native confirmed-stop pipeline cleanup — 2026-09-15

The private five-worker dispatcher now cancels partial writer frames only after
observing the exact native stop record. Three reused pipe generations distinguish
an incomplete request (zero bytes on both pipes) from a completed write whose
reply is interrupted (ten exact bytes on both pipes). Relay and reader receive
one EOF each. Every schedule requires fifteen admissions/reclaims: twelve normal
exits and three kind3/status143 confirmed stops. No frame or holder survives reuse.

## Qualification

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`: all eleven native cases pass on 273 frozen inputs. Target cases total 29.003 seconds. Exact commands, tool/SDK identities, timestamps, artifact hashes and results are retained in attempt-1-results.json and its archive.
- Eight previous cases pass unchanged in meaning. New pipe-stop-request and pipe-stop-reply pass; pipe-keep-frame deliberately omits buffer cleanup and rejects owner2724 with zero reclaims. The existing wrong-route and write-replay mutants still reject owner2723/2726 with zero reclaims. A timeout or unrelated panic is not accepted.
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`: exit0, all 104 host tests pass (host.log); includes the shared pipe-core checks and offline pin/inventory rejection cases.
- Final checks record Rust 1.98 edition2024, Clang-format21.1.8 and its digest, workflow/standards/experience verification, simplicity snapshot hash and all four members, and whitespace checks.

No failed implementation attempts occurred. Intentional negative cases and all raw
serial/build logs remain in the target archive. The outer owner independently
re-observes exact stop status before closing channels and reclaiming. The dispatcher
checks the seven-byte interruption cursor, clears it only after terminal, removes
both objects' participant holdings, and derives retirement pending flags from the
actual remaining frames/replies. Shared pipe-core behavior is unchanged.

## Compatibility, resources and limits

The base capacity worker/owner and normal pipe worker ELF remain byte-identical to
the preceding dispatch packet; compatibility.json records comparisons. Dispatch
owners change to enforce pending-aware retirement. Largest new owner is 8272 bytes
within 16384; channel/worker/generation limits and kernel mapping bounds are unchanged.
Kernel and shared pipe modules, SDK, sibling repositories and released pins are
unchanged. Three local stop flags extend bounded fixture state; no new unsafe
boundary, service, dependency, public ABI or kernel primitive is introduced.

This is native conformance-worker coverage, not actual dash fork/exec or a full
consumer handoff. Ordinary EPIPE, early-reader behavior, actual seven-binding
fork/exec composition, full matching connections/runner and independent intake
remain open. No general cancellation/recovery, physical hardware or R1 readiness
claim follows. An assembled shell/filesystem/packages/sys-init image is still work.

final-sources.json/tar.gz bind exact runtime inputs. review-inputs captures the
local process/contract documents and host test support; the preimplementation
review is in NATIVE-SHELL-STARTUP. collect.py archives and verifies every generated
file against its original before deleting only this attempt's private output root;
cleanup.json records that removal. Immutable prior packets remain untouched.
SHA256SUMS covers this packet except itself.
