# Failed-exec session producer delivery — 2026-09-29

Requirement: consume independent RECOVERY-01–06 acceptance and integrate the unchanged next failed-exec composition through authenticated owner lookup. Preserve AENMX007/ABI21, 15 lifetimes per slot, three children, two pipes, 24KiB owner and4088-byte stack. No sibling, SDK, released pin or SI-07 profile changes.

Forbidden: pathname-only client error synthesis, treating argv[0] as lookup authority, replacement on denied lookup, side effects before complete validation, stale waits, invented native success or timeout as denial. Userland owns workload and subsequent acceptance; this repository owns the private fixture protocol and native evidence.

Before code: use a distinct bounded exec request carrying the actual path separately from argv, resolve only the owner-owned fixture namespace, keep the existing helper replacement path and legacy opcode84 unchanged. Missing yields ENOENT, present non-executable yields EACCES, only granted helper is executable. Bind denied decisions to authenticated native child identity and terminal status before reclaim. Validate reserved bytes and complete vectors before mutation. No generic filesystem or new kernel authority mechanism is needed.

Tests: malformed path/vector/header and authority cases; unchanged host suite; full affected capacity cases; five non-pipeline regressions if kernel behavior changes; exact native identities/counts/streams, deliberate wrong errors, fabricated denial, stale wait, environment, descriptor and stderr controls. Inspect linked owner stack before claiming resource fit. Record all attempts and freeze sources during runs. Update existing STATE, ROADMAP and interface/workflow references with verified results and remaining gaps.

Simplicity: reuse bounded authenticated session transport and replacement logic; a client pathname special case cannot prove owner authority. One explicit request variant is sufficient; no new service, abstraction or public ABI. Security scope includes untrusted paths/vectors, channel identity, interrupted requests, denied image state, descriptor ownership and cleanup. Native side effects remain in the existing owner; parsing is inert. Broader filesystem, SDK, serial and whole-release security remain separate.

## Intake and retained attempts

The selected consumer receipts under consumer/ are a snapshot, not a full copy
of that packet. Its SHA256SUMS describes the original450-member userland packet;
acceptance-intake.json records verification and the exact producer binding.
RECOVERY-01–06 is independently accepted. The new failed-exec work remains a
separate producer delivery until userland replays it.

Attempt1 reached native success, then the host dispatcher referenced an uninitialized
serial variable. Its log passes the completed independent oracle when read back;
the original failure remains recorded and does not become a clean suite run.
Attempt2 passed133 cases, then the skipped-request negative unexpectedly completed
normally: its C define had no matching body after an editing mismatch. The ordinary
negative harness rejected it. The mutation and stale-wait scheduling were corrected.
The first formatting pass also used the formatter's default style; the current
source uses the pinned scoped style. The initial snapshot helper named a nonexistent
build.zig.zon and was corrected before it wrote output.

The initial host run before the new test passed119 Python checks. The next host run
ran122 checks but failed a stale expected Rust test-count string (all70 Rust core
tests actually passed); the corrected host run passes122 Python checks and the
configured Zig/Rust/pin checks. None of those host results substitutes for native
semantic controls. All failure logs remain.

Test selection: full capacity coverage covers every consumer of session-owner.rs
and session-client.c, including earlier SESSION/recovery variants. Five unchanged
non-pipeline command cases also pass. The kernel implementation is unchanged, so
prior358-connection/431-runner results are not claimed as rerun for this delivery.

## Authority and simplicity review

The bounded path parser is inert and safe Rust. The existing synchronous channel
transfer owns all borrowed buffers; no new unsafe pointer or assembly interface
is introduced. Opcode85 accepts no image grant field, distinguishes the actual
lookup path from argv[0], validates fixed lengths, padding, bounded strings and
unique environment keys, and consults the owner's two-entry fixture namespace.
This is no mounted or persistent filesystem. Failed lookup cannot enter the
freeze/admit/descriptor-commit branch. Native image-commit queries must remain
(0,0,0) at reply and terminal observation. The owner's endpoint/handle ledger and
existing kernel authority checks authenticate callers; paths and PIDs are not grants.

Collection/reclamation gates the next phase; slot2 generations1/2,6/7,11/12 are
failed commands,3/8/13 argv,4/9/14 pipeline,5/10/15 closure helpers. Slots3/4 are
the other pipeline stages at generations1–3. Parent slot0 completes generations1–3.
Final observation requires24 reclaimed workers and exact streams. The skipped
request control demonstrates that status127 alone cannot stand in for a real
owner decision: the owner stops the parent and confirms cleanup. A stale collected
identity is challenged while the second failed child occupies the reused slot.

The tradeoff is one explicit private opcode and a small bounded owner namespace,
reusing the existing replacement and lifetime mechanisms. The simpler client-side
pathname special case would fail the required authority witness. No generic VFS,
new kernel policy, global mutable authority table or additional service was added.
Malformed request host controls, existing native authority regressions and scoped
semantic controls are bounded evidence, not fuzzing or whole-system security proof.

Attempt3 passed134 cases, including the corrected skipped-request denial. Retiring
the parent's actual stderr binding then exposed the unchanged client's exit-time
close failure: native parent141 and eight reclaims, while the initial owner oracle
expected the script's57. The mismatched-context run is retained as a failure. The
final control explicitly requires parent141, the observed closed-stream cleanup
outcome, with exact stdout prefix and empty stderr; it does not weaken close or
transport poisoning. A host counterexample rejects a guessed57 result. The new
host baseline is123 Python tests after adding that counterexample.

Deferred scope: this retains the existing synchronous bounded fixture transport.
Arbitrary interruption midway through the new path/vector exchange is not newly
qualified as a restartable service protocol. Promotion into the shared SDK/runtime
requires its owners' transport/interruption and consumer review; no general TTY,
filesystem daemon, sustained cohort or production service conformance is claimed.
The scripted owner asserts expected workload phases; it is not an unrestricted
exec server for arbitrary clients. The malformed-request parser is host-tested,
while matched native fixture inputs exercise the admitted and denied lifecycle.

## Final result and replay

All137 capacity cases and five unchanged non-pipeline command cases pass. All123
Python and configured Zig/Rust/pin checks pass. Nine independent new-case comparisons
and56 checker corruption controls pass. Three unchanged dash parents produce exact
60-byte stdout/25-byte stderr,21 copies,12 successful helper replacements,15 image
admissions and24 terminal/reclaims. Denied children never admit an image. Slot2
finishes generation15 without widening its lifetime bound.

After the frozen native run, only the independent host oracle and its tests were
strengthened to bind each admission to the exact expected slot/generation before
its terminal. All nine new logs pass re-analysis (bad-byte is the expected stream
rejection), and host checks pass again. native-source-inputs preserves the exact
executed source set; final-source-inputs records delivered checker improvements.
No native image or kernel source changed after the qualified run. Attempt evidence
and these distinct source sets remain separate.

| Control | Required native result | Reclaimed |
| --- | --- | --- |
| wrong missing | child126, parent51, owner2860 |2|
| wrong denied | children127/127, parent52, owner2861 |3|
| wrong environment | helper91, parent53, owner2862 |4|
| descriptor leak | closure helper95, parent55, owner2863 |8|
| skipped request | child127, parent confirmed stop143, owner2864 |2|
| retired parent stderr | parent wrapper141 after failed close, owner2865 |8|
| stale collected wait | ECHILD with unchanged status; normal composed result |24|
| corrupted output | normal cleanup, ordinary host stream rejection |24|

The final packet includes sources, consumer pins, SDK/tool receipts, all attempts,
linked resource review and verified artifact archives. Replay by extracting
replay-inputs.tar.gz into a fresh directory and verifying replay-inputs.json.
Use the pinned external SDK `/Users/cam/DEV/Aether-userland/build/native-c-5olokhku`
and tool lock `zig-out/init-capacity-2026-09-06/tools.lock.json`:

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

`--case failed-exec-composed` selects the positive. The historical five-case driver
and all20 frozen input files are explicitly included in the export this time:
`python3 docs/evidence/init-command-handoff-2026-09-08/run.py` accepts the same
SDK/tool-lock options. Keep replay outputs separate from this sealed packet.

Next owner action: userland independently replays EXEC-SESSION-01–06 and supplies
scratch/real-serial compositions. SI-07 separately awaits its complete versioned
bootstrap/transport and rebuilt runner/bytecount; its current proposal and decoder
hashes are retained as dependency context. Shared SDK, independent reader reviews,
persistent filesystem and assembled R1 remain open. No sibling repository,
released pin or public ABI changed. This is not a full interactive filesystem shell.
