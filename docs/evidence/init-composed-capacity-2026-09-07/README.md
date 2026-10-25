# SI-06 composed init producer — 2026-09-07

AENIN003 / ABI 16 provides a separately versioned, opt-in 16 KiB supervisor code
profile. The two-worker init contract, grants and 4 KiB stack remain unchanged.
V1/V2 keep their exact 4/8 KiB limits and markers. The source contract is in
[contract.md](contract.md) and [NATIVE-INIT](../../NATIVE-INIT.md).

Producer qualification is complete: **453 selected target cases pass**, including
32 V3, 23 V2 and nine V1 cases, all 213 command-runner cases, both 46-case pthread
suites, memory/image/console and seven M4 regressions. All 98 host tests plus
Zig, standards, workflow and format checks pass. [producer.json](producer.json)
is the consumer entry point; [completed.json](completed.json) composes the passing
checks on one frozen implementation while preserving the infrastructure failure
and its source-matched retry. Verify manifest.json before consuming artifacts.

## Evidence scope

The new-profile suite has 32 passing cases: full lifecycle code runs on page four
after executing jumps on pages one, two and three. Boundaries cover 4095/4096,
8191/8192/8193, 12287/12288 and 16383/16384 bytes. The host parser separately checks
one-byte acceptance, all identifiers and malformed lengths. Zero, 16385, u32 max,
reserved, truncated and extra payloads reject; V1/V2 reject oversized V3 payloads.
Code aliases/permissions and zero tails are verified before entry. Dirty tail
rejects before entry. Actual writes to pages two, three and four, stack execution
and a below-stack guard write fault with their specified errors and verified
whole-domain shutdown. Normal completion is distinct from owner-failure cleanup.

A safe extraction of the source and SDK passes host tests and all 32 cases again
in a fresh private checkout. This is a same-owner offline rebuild, not independent
consumer acceptance or reproducible ISO-byte certification. The packet preserves
all attempts, including the compile-format failure, SDK link repair and sandboxed QMP failure described
in [failures.md](failures.md). No previously failed run is counted as passing.

[review.md](review.md) records authority, mappings, cleanup, arithmetic and the
separate composed-stack assessment. A private copy of sys-init's refined 0174
candidate changes only its expected ABI and linker bound. Its 11,680-byte positive
returns 100 with three reclaims; five controls return 1094–1098 with the expected
retained state and no native faults. All six execute on the unchanged one-page
stack. This is a bounded path witness, not a stack high-water measurement or a
promise that future reclaim/Cleaned code fits. Sys-init's own source/pins and
acceptance state remain unchanged.

## Offline consumption

Verify manifest.json and producer.json before extraction. Extract
producer-source.tar.gz into a fresh source directory and sdk-inputs.tar.gz into a
separate fresh SDK directory using a safe tar reader. The SDK's old absolute
Makefile link is replaced by the equivalent relative link within its own tree;
regular source/runtime bytes are unchanged. Keep tools.lock.json and verify the
installed tools against it and tool-identity.json. These pin installed executables,
not a portable packaged compiler/library closure. No setup/download is hidden in
qualification.

From the extracted source directory, with its zig-out directory created, run:

```sh
python3 scripts/launch_smoke.py --init-composed --libc-build /ABS/SDK/native-c-5olokhku --tools-lock /ABS/PACKET/tools.lock.json
python3 scripts/launch_smoke.py --init-large --libc-build /ABS/SDK/native-c-5olokhku --tools-lock /ABS/PACKET/tools.lock.json
python3 scripts/launch_smoke.py --init --libc-build /ABS/SDK/native-c-5olokhku --tools-lock /ABS/PACKET/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

target-attempts.tar.gz retains all 19 passing target directories. The separate
source-rebuild-target.tar.gz and consumer-study.tar.gz retain their complete
artifacts and logs. Failed attempts remain separate; none is rewritten as a pass.
source-archive-check.json and archive-verification.json record archive checks.

The source manifest binds all 499 regular build/reference/planning/boot inputs;
historical evidence directories are intentionally separate. Frozen planning text
predates completion; this packet and producer.json record the producer result.
The SDK source and runtime closure is retained with its upstream notices. Tool,
SDK, boot and consumer inputs remain explicit; no mutable sibling checkout is a
hidden build dependency. Native case logs record exact commands and artifacts;
outer suite receipts add timestamps and frozen-source identity. Limits remain
180 seconds per build, 30 seconds per QEMU run and 1800 seconds per suite.

After verifying the packet, sys-init can independently adopt the profile and
rebuild its full affected Terminal/reclaim-capture controls. Issued reclaim,
Cleaned, arbitrary stack growth, supervisor recovery and release assembly remain
separate. This handoff does not authorize a consumer pin change or claim its
acceptance, and does not publish a release. Aether returns to the planned ARC
serial-eviction experiment after this requested unblock.
