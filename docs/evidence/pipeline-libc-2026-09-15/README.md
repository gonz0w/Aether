# Seven-binding libc replacement I/O — 2026-09-15

The replacement pipeline now exercises the existing startup descriptor facade and
actual musl read/write/close instead of raw pipe calls. A private PIPELINE_STREAMS
selection extends transport capacity to seven bindings and calls a validated-table
bootstrap/install pair. Existing profiles retain their prior initialization.
The source marks standard bindings0–2 CLOEXEC, so the replacement installs no
fabricated standard-stream backend. Only its exact authorized pipe ends survive.

Under the existing startup signal guard, the client validates the entire table
before installing bindings, references, rights, alias counts and readiness. It
uses dup2 to map its pipe ends to stdin/stdout, closes original aliases, duplicates
a live descriptor with F_DUPFD_CLOEXEC at10, checks its flag, closes it and checks
EBADF. Actual musl I/O then carries ten exact bytes and EOF through both pipes,
with three generations and fifteen normal reclaims. Owner authority remains
independent of descriptor/reference numbers. The new bootstrap publishes nothing
on a mismatched table. Retained FD10 delivery rejects replacement105 then owner2734
with zero reclaims.

## Qualification and failed attempt

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes23 native cases on275 frozen inputs. Final target cases total
62.267 seconds. `python3 docs/evidence/pipeline-libc-2026-09-15/focused-selector.py`
selects all21 existing dash-pipe cases from the regular launch harness and passes.
Replay the selector into a new evidence directory; do not overwrite this packet.
Commands/tool identities/SDK hashes, times, envelopes, ISOs, reports and serials
are preserved. `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0; both host logs record104 passing host tests. Final checks bind pinned
formatters, workflow/standards/experience, simplicity manifest/four members,
whitespace and frozen source verification.

Attempt1 passes the new capacity and host suites, but the legacy compile rejects
a missing closing parenthesis in the shared header's old CAT_ROLES branch. The
new profile did not evaluate that branch. This implementation typo is preserved
with exact sources, failed compile and preliminary passes. Attempt2 corrects only
that parenthesis and reruns capacity, host and all selected legacy cases successfully.
No timeout or unrelated panic qualifies a negative test.

## Compatibility, resources and remaining scope

All25 previous capacity ELF/raw images are byte-identical; all208 available
baseline legacy images are unchanged. The focused selector omits other full-suite
images, recorded explicitly in missing-baseline-images.json; this is not full-suite
qualification. Positive/negative new owners12424 bytes fit16384. Original C is
BSD-2-Clause; no kernel, shared pipe-core, SDK, dependency, quota, sibling repository
or released pin changes. Existing header style is preserved around scoped branches;
new C uses the pinned formatter. The memory adapter is compiled with its raw I/O
hook renamed for this client so the shared descriptor hook is the sole __aether_io
provider; original memory-adapter source and other link modes remain unchanged.

No new unsafe boundary is added: masked synchronous startup keeps buffers live
through validation/publication, and file I/O retains the existing poison/errno and
alias-lifetime rules. This is a private native facade, not a published SDK extension.
The replacement installs real facade descriptors, but actual dash pipeline
orchestration, copied libc rebind, exec/wait consumer scripts, SIGPIPE composition,
full matching suites and independent intake remain open. Persistence/packages/
sys-init R1 assembly is still required; no full-shell or release claim follows.

Source archives preserve both snapshots; review-inputs preserves current guidance
and host test support. The preimplementation review is in NATIVE-SHELL-STARTUP.
collect.py and collect-legacy.py verify every generated file against its archive
before deleting only these four private output roots. Cleanup receipts and failed
attempt archives are retained; prior sealed packets are untouched. SHA256SUMS
covers this packet except itself.
