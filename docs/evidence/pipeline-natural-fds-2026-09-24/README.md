# Natural pipe descriptor layout — 2026-09-24

Both native attempts pass all 94 cases. Final host checks pass 105 Python tests plus
Zig/Rust checks. Attempt 1’s binary
comparison found 51 changed legacy owner images. Compile-time separation of the
new validator restores all 122 previous ELF/raw images exactly. The new owner is
identical across attempts. Sources and all attempt artifacts are retained.

The opt-in client leaves the second pipe at local fd4/5, whose stable capability
bindings remain5/6. Fork snapshots reflect those returned descriptors. Helpers dup
the needed endpoints onto fd0/1 and close redundant pipe aliases before exec.
Replacement accepts exactly fd0/1/2 with the correct existing bindings and rights;
there is no blanket acceptance of arbitrary descriptor tables. Denied exec preserves
this table. An extra unflagged fd10 alias rejects 2733 before replacement admission
with zero reclaims. Existing shared holder validation remains authoritative.

Real dash main/init/eval still runs inside the already copied writer, while both
replacement workers execute the unchanged pinned consumer helper copy body. The
parent remains a fixture driver. This does not claim unchanged pipeline.sh execution,
an interactive prompt, public handoff or independent consumer acceptance.

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Only three runtime files changed: the client fixture, private snapshot validator and
suite selection. No shared core, kernel/SDK ABI, resource budget, dependency, released
pin or sibling changes. Source snapshots cover 282 inputs. The new owner is 18,168 bytes,
256 fewer than the previous main owner, under the existing 24-KiB ceiling. Its linked
text matches the qualified raw image. Reviewed critical frames remain 2600+136+1080+120
plus 32 return-address bytes: 3968 of 4088 usable, 120 margin. This is scoped linked-binary
review, not a general stack proof; native C workers retain their separate stack.

The archive finalizer verifies runtime snapshots and all final checks, hashes every
artifact both live and archived, and deletes only verified generated duplicates.
Attempt 1 is retained because compatibility review prompted source changes, not because
its native cases failed. No earlier sealed evidence is modified.

Next move real startup into the parent and let dash create its job. Startup requests
before the first fork, private report/readiness, and inherited environment still need
integration. General process/argv/env APIs, full matching native suites, independent
consumer acceptance, serial-shell assembly, persistent storage/OpenZFS, packages and
sys-init remain outside this bounded qualification.

Final native cases total 269.866 recorded case seconds.
The positive completes ten bytes, EOF, three child collections and 15 reclaims across
three generations; the alias control rejects 2733 with zero reclaims. No native cases
failed in either attempt. A post-run summary assertion mistakenly expected owner0
instead of established success100; analysis-correction.json retains this corrected
analysis failure. Native oracles were unchanged.
