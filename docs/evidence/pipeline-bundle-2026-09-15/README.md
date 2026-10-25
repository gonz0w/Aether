# Five-worker bundle prerequisite — 2026-09-15

The candidate parser accepts AENMX004's 112-byte header, including five disjoint
16-byte developer entropy slices. Three image templates and the existing 16 KiB
owner limit remain. The ordinary bundle parser and native start do not accept this
candidate. This is input-validation work, not an enabled five-worker native profile.

The [preimplementation review](../../NATIVE-SHELL-STARTUP.md#five-worker-bundle-and-capacity-review--2026-09-15)
records ownership, O/I/E and SE applicability, exact layout, compatibility and
selected checks. Sharing the three-image parser avoids duplicate bounds/slicing.
No sibling, released pin, authority, dependency or kernel capacity change.

All 14 launch/ELF tests pass, including three new cases for slice separation,
malformed framing/reserved/length/version rejection and exact upper limits. All
104 host checks and required Zig checks pass. The intentional short-entropy mutant
fails expected80/found48. Native kernel compilation passes with the hash-verified
previous pipe-status envelope; it was not booted. No new native runtime or full
regression claim is made. The first standalone test used the default cache and
failed on permissions before tests ran; parser.log is retained. The documented
repository-cache retry passes with identical sources.

Commands:

```sh
zig test kernel/native_launch.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig fmt --check kernel/native_launch.zig
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

kernel-command.json preserves the exact compilation invocation; kernel-result.json
labels its compile-only scope. The mutant command/result is in short-entropy/.
Sources, support/review inputs, test binaries and generated kernel outputs are
archived with verified hashes; prior evidence remains unchanged. SHA256SUMS seals
this packet. Replay into fresh output roots, never overwrite this evidence.

Next: implement the opt-in six-state/ten-channel profile and 80-byte bootstrap,
keep old-profile PID stride unchanged, check mapping/backing budgets, then qualify
native worker and channel boundaries. Native dispatcher wiring, actual pipeline
and early-reader, full matching suites and independent intake remain open.
