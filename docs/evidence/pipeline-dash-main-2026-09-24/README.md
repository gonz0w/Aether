# Real dash startup inside the pipeline — 2026-09-24

Qualification passed in one native attempt. See the preimplementation review in NATIVE-SHELL-STARTUP.md.
The copied writer invokes the pinned native main object through real main/init/eval,
with existing public musl signal operations and scoped identity/cwd facades. Both
replacement helpers run the unchanged pinned consumer copy body. Parent construction,
report/readiness and fixed argv/env remain private; this is not unchanged pipeline.sh
or full-shell acceptance.

The owner sends a64-byte identity/directory packet only to the copied writer. It checks
all reserved bytes, current generation and native auxiliary IDs before publication.
The immutable /work view accepts only the authorized slot/reference, retains fragmented
replies in the existing dispatcher, and never resolves arbitrary filesystem paths.
Host decoder tests and native denied/stale cwd probes cover this new scoped boundary.
A command-byte mutation must reject2743 for incorrect captured output.

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

## Qualification and scope

All92 native cases pass in263.881 recorded case seconds.
105 Python host tests plus Zig/Rust checks pass; the existing exec-request host runner
now also executes three directory-decoder tests (five Rust tests in that runner).
Real dash main/init/eval produces exact ten-byte data through both consumer helpers,
with EOF, three distinct waits and15 reclaims across three generations. The command
byte mutation produces normal shell/helper exits but rejects2743 with zero reclaims.
Native copied-shell probes verify matching auxiliary IDs, usable cwd, EACCES for a
wrong directory reference and EBADF for a stale reference. Host tests cover other
caller slots, request padding/length/opcode and namespace escape denial.

All118 previous ELF/raw images are unchanged. Six runtime files changed, including
one new pure decoder module;282 runtime inputs stayed frozen. The host test source is
retained in review-inputs. Both new owner programs are identical18424-byte images.
The positive linked text equals qualified raw; reviewed depth3968 of4088 usable owner
stack bytes leaves120. The startup packet sender frame200 is shallower. This is scoped
linked-binary review, not a general stack proof. The shell worker ELF is257688 bytes;
its retained disassembly shows __wrap_main calling the pinned main, which calls init
and evalstring, and the scoped exit wrapper. Native C stack remains separate from the
one-page Rust owner stack; no resource budget or kernel/SDK ABI changes.

The existing source/main/object pins were verified before build. Native signal operations
are used in this shell profile. /work is a connection-scoped immutable directory view,
not persistent storage or arbitrary path resolution; the copied shell receives this
new narrow authority through its existing owner channel. No ambient UID/path authority,
global mutable namespace, dependency, sibling modification or released-pin change.

One native attempt, no failed native cases. finalize.py validates source snapshots and
checks, archives every generated file, compares live/archive hashes, and removes only
the verified duplicate suite directory. SHA256SUMS seals the packet; prior evidence is
unchanged. Native malformed startup-packet/truncation permutations remain unqualified
before broadening this fixed-owner bootstrap into a consumer API.

Next move real shell initialization to the parent and let dash construct the pipeline
job through the scoped factory/copy/descriptor/wait path. The present real shell runs
inside the already copied writer: it does not evaluate the unchanged full pipeline.sh,
create its helper children or provide an interactive prompt. Parent orchestration,
private report/readiness, general argv/env and independent consumer acceptance remain.
Serial-shell assembly, persistence/OpenZFS, packages and sys-init remain R1 requirements.
