# Interactive parent pipeline — 2026-09-24

Final qualification passes 105 capacity, 358 connections, 431 runner and four console
cases (898 native checks), plus 105 Python tests and Zig/Rust host checks. All target
suites match the same 287 runtime inputs. This is producer evidence for the private
serial profile; shared SDK and R1 completion remain open.

## Requirement and result

Actual dash `sh -i +m` receives this command only after its real serial prompt:

```sh
printf 'pipe data\n' | /inputs/helper copy | /inputs/helper copy
```

The host waits for the returned prompt and all three child terminal records, then sends:

```sh
echo after; exit 0
```

The final 105-case capacity suite passes. Three fresh shell generations produce six
prompts, six host command events, exact 16-byte stdout and four-byte prompt capture
per generation, fifteen successful terminals and fifteen reclaims. The owner closes
its console grant after all generations and verifies that it no longer permits reads.
One-byte UART transfers exercise short-count progress; empty RX retains the blocking
stream request without fabricating EOF or replaying a completed write.

This integrates parent-driven pipeline construction with serial input/output. It is
still one bounded pipeline plus a follow-up builtin per shell generation. Arbitrary
successive jobs, combined exec/substitution/redirection in this owner, installed SDK,
general signal/TTY behavior, persistent filesystem and sys-init/package assembly are
not qualified by this packet. Earlier accepted components retain their own scope.

## Contract and security scope

AENMX006 / bootstrap ABI20 retains the AENMX005 layout, six bootstrap arguments,
24-KiB owner code cap and existing six-domain memory/channel limits. It additionally
authorizes only the bootstrap owner to use UART selector 0xf001 through existing v1
read/write/close operations. It does not authorize handoff. Parent and copied children
verify direct UART access is denied; they use only their authenticated stream channels.
004/005 retain ABI19 and their prior authority. No sibling or released pin changed.

The existing pipe/stdio owner forwards bounded bytes; there is no new service, queue,
allocator or terminal policy. Native pointers borrow live frame storage synchronously.
Malformed/stale stream authority is checked before device effects. This bounded native
owner is additional trusted user-space code; a test pass is not whole-system security
assurance or independent implementation approval.

The pinned native dash input object disables its Linux tee optimization and selects
upstream's one-byte fallback, as in earlier serial profiles. No new upstream patch or
fake successful tee operation is introduced. Main/jobs/helper selections and tool/SDK
pins are in the results. Existing ASCII prompts and emergency markers are unchanged.

## Checks and resources

- `attempt-5-results.json`:105 capacity cases, including serial positive and three
  rejections: changed output 2743/reclaimed 0, wrong grant 2795/reclaimed 0, and 006 with
  the capacity option disabled rejected before admission.
- `host-attempt-2.log`:105 Python tests plus Zig/Rust and offline standards/workflow
  checks. `format-checks.json` covers the changed Zig/Rust/C source formatting.
- `connections-attempt-1-results.json`:358 cases, including earlier serial exec and
  substitution; `runner-attempt-1-results.json`:431 cases. Both pass on matching runtime
  bytes. Legacy reports additionally retain five Finder metadata files.
- Console handoff and connections each pass their positive and changed-input controls.
- `stack-review.json`: linked serial owner 18616 bytes; reviewed critical path 4000 of
  4088 usable stack bytes, leaving 88. Old pipeline/early-reader paths remain 3968/3984.
  Audited ELF text matches the actual raw owner bytes used by the final capacity suite.
  This is scoped linked-path inspection, not a formal whole-program stack proof.

Further growth on this stack requires review before implementation. No resource cap
was increased. Concurrent regression wall time is not a performance benchmark. The filesystem-observed
full-suite durations stay below the existing 1800-second review ceiling.
Of 142 earlier capacity ELF/raw images, 87 are identical and 55 Rust owner images change;
all existing C ELF images remain identical. Changed owners have fresh target evidence.

## Exploratory failures retained

All failures are diagnostic/product attempts, not accepted negative-test results:

- Attempts1/2: real prompt followed by construction 2739 before host input. Review
  found missing blocking-read retention; temporary opcode diagnostics did not change
  the failure. Attempt3 retains EAGAIN correctly and sends the pipeline, but still
  rejects 2739 before copying children.
- Probes1–3 reuse attempt3's C/kernel inputs with diagnostic Rust owners. Probe2
  identifies the duplicate-create guard; probe3 identifies slot2/created=true.
  Generic dash input had created a Linux tee staging pipe before the application pipe.
- Attempt4 selects the existing pinned native input object. Pipeline, returned prompt
  and follow-up execute, then the capture oracle rejects 2743: it counted 16 bytes as 15.
- Probe4 reuses attempt4's C/kernel inputs with the corrected literal-derived length.
  It passes three generations. Attempt5 then freshly builds the entire 105-case suite
  on final sources; no temporary diagnostic reason codes remain.
- `stack-attempt-1.log`: audit preparation raised StopIteration before compiling;
  corrected audit command and output are preserved separately.

`run-attempt.py` and `run-probe.py` preserve the final local invocation helpers. The
historical probe results record their actual base report hash and commands; probes1–3
used attempt3, while probe4 used attempt4. They are mixed-source diagnostics, not
substitutes for final qualification. Source snapshots and raw logs retain those bytes.

## Reproduction and retention

From the repository root, with the pinned SDK and tools available:

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Console regressions use `scripts/console_smoke.py --handoff` and `--connections`
with those same SDK/tool arguments. Exact build/VM commands, times, flags, sources,
artifacts, output, exchange events and pins are retained in reports and archives.
The new capacity cases and serial exchanges record timestamps. Legacy launch reports
do not provide instrumented whole-suite timing; filesystem-observed durations in
`run-times.json` are approximate, not performance evidence. Runtime sources remain
frozen during final qualification. `runtime-change.patch`
compares against the preceding sealed parent packet, not the dirty Git baseline.

Each artifacts archive has a per-member SHA-256 map. `archive.py` reads every archive
member back and compares the still-present original before deleting only that run's
owned duplicate directory. Cleanup receipts record the original path, byte count and
archive digest. Failed evidence is retained under the same policy as accepted evidence.

`consumer-review.json` records read-only review of userland's sealed 12/12 acceptance
for the earlier parent scripts. It does not claim consumer acceptance of the new006
serial profile. Independent new-interface acceptance and shared SDK integration remain
open. Released standards and prior sealed packets are unchanged.
