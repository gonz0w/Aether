# Native five-worker capacity — 2026-09-15

The opt-in AENMX004/native-pipeline-capacity profile runs five isolated workers
with owner slot5, ten scoped channel objects and 80 bytes of per-slot developer
entropy. Default builds retain four State entries, old entropy/channel limits
and the four-entry PID stride. Three reusable image factories remain; worker
slots are separate from image templates. Completion requires fifteen reclaims
and all channel endpoints closed/zeroed. This is a capacity witness, not an
assembled shell pipeline or sys-init policy implementation.

## Review and qualification

The [capacity contract](../../NATIVE-SHELL-STARTUP.md#native-five-worker-capacity-witness--2026-09-15)
records requirements, O/I/E and SE clauses, ownership, bounds, cleanup, unsafe
transport obligations and test selection. Fixed opt-in array sizes reuse existing
mapping, scheduling, channel enforcement and lifecycle primitives without dynamic
allocation or a new shared authority ledger. No sibling, released pin, dependency,
image factory or service-policy change.

The positive case admits all five workers before releasing any. Across three
lifetimes it checks actual musl getpid/getppid, slot-specific entropy, TLS reset,
wrong-owner endpoint/factory/lifecycle denial, worker-slot5 denial, ten-channel
exhaustion and stale handles. The second lifetime explicitly stops slot4; all
other workers exit0. Fifteen admissions/reclaims and fourteen normal terminal
markers pass. After the third lifetime both channel and worker generation pools
reject further allocation. The kernel's final gate checks all retired admissions
and zeroed channel state.

All five capacity cases pass: the positive; bad entropy (worker73/owner2607 with
zero reclaims); a shortened candidate header; enabled build with old magic; and
new magic with the build option disabled. The last three reject at the named
profile/envelope boundary. Three build guards reject absent memory, threads and
large backing with the exact explanatory message. All 104 host checks pass.
The ordinary seven-case kernel regression passes, including remote cleanup and
framebuffer controls. All 21 selected legacy pipe cases pass on the final sources; all 208 comparable
ELF/raw client/owner images are identical. The focused selector omits 485 other
baseline images; full matching suite coverage is not claimed.

The qualified kernel mapping span is 7,995,392 bytes, within the existing 16 MiB
limit. The owner is 2,224 bytes within the unchanged 16 KiB maximum. Each worker
reports 21 used/107 remaining pages from its 128-page arena. These are mapped or
reserved fixture bounds, not peak system memory, performance or total TCB claims.

## Compatibility fix and failed attempts

Actual SDK getpid exposed a kernel mismatch: zero-argument calls leave argument
registers unspecified, but the kernel demanded zeros. The kernel now ignores
those registers while preserving the profile gate and exact identity calculation.
The worker uses musl getpid and a raw call with nonzero unused registers. Existing
prelude wrappers had hidden this issue by clearing the registers; no successful
stub or ambient authority was introduced.

1. The first kernel build found a dependency loop between channel storage and its
   initializer's inferred type. An explicit Channels type removes that loop.
2. The second attempt reached the loader, which correctly rejected a worker ELF
   without TLS. The witness now contains and checks a real TLS value; loader
   restrictions were preserved.
3. The third attempt admitted all five workers but they returned72 due to the
   getpid mismatch. The actual kernel fix above is included in final inputs.
4. The fourth attempt passes all five capacity cases on 272 frozen inputs.

The first ordinary regression run could not bind its QMP screenshot socket in
the sandbox. The authorized retry with socket access passes all seven cases.
Both roots and logs remain archived. This is an infrastructure failure, not a
runtime rejection. Failed attempts, exact source archives and artifacts are
preserved; no failure was converted into a passing result.

## Replay and preservation

```sh
python3 scripts/pipeline_capacity.py --libc-build <pinned-sdk> --tools-lock <pinned-tools.json>
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/regression.py
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

Capacity results record commands, source/tool/SDK digests, per-case timestamps and
raw serial logs. The ordinary regression additionally checks framebuffer output
and requires a permitted local QMP socket. C formatting uses clang-format21.1.8
and the pinned draft style; Rust uses1.98.0/edition2024 and Zig0.16.0.

Each attempt's archive has a per-file hash manifest. Generated roots are removed
only after every archived member and original is verified. cleanup.json and the
legacy cleanup receipt identify exact removed duplicates. Final sources and
review inputs remain replayable; prior sealed evidence is unchanged. SHA256SUMS
seals the packet. Never overwrite this packet when replaying.

## Remaining work

Connect the private two-pipe/seven-binding owner to native descriptor dispatch,
copy/exec admission and pending/completed frame cleanup. Qualify the unchanged
pipeline and early-reader workloads, full matching connections/runner and
independent SDK/userland intake. Persistent filesystem/OpenZFS, package execution,
recovery gaps and sys-init R1 assembly remain on the release path.
