# Natural parent wait scheduling — 2026-09-24

Final qualification passed in attempt2. Preimplementation review: NATIVE-SHELL-STARTUP.md,
Shell wait scheduling prerequisite. Child exec/I/O in the new opt-in profile may
progress independently of parent wait arrival. Completion requires all three scoped
children collected and the final reply fully delivered, instead of eight fixture
probes. Parent performs three waitpid(-1) calls and verifies unique normal exits.

A forced-late schedule delays first wait intake until all three children have terminal
records. It must pass. A control restores the old first-wait-before-exit restriction
and must reject2751 with zero reclaims. Existing interrupted-reply and scope controls
remain in the full suite. This is still private parent orchestration, not actual dash
main/eval or unchanged script acceptance. Fixed argv/empty environment and private
report/readiness remain. No kernel/SDK, shared core, sibling, pin or resource change.

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Attempt1 passed all90 native cases and host checks, but review found a residual
legacy counter assertion in the natural profile. The final change removes that
counter dependency entirely, retaining only a first-reply flag for the forced-late
test schedule. Attempt1 sources, audits and logs are retained; attempt2 reruns the
complete selection on final bytes. This is a review correction, not a failed native case.

## Final qualification

Attempt2 passes all90 native cases in248.851 recorded case
seconds.105 Python host tests plus Zig/Rust checks pass. Ordinary and forced-late
natural waits collect three distinct children with normal status, preserve full
streams/EOF, and complete15 reclaims over three generations. The old first-wait
assumption control rejects2751 with zero reclaims after all three child terminal
records; the negative does not require parent exit. Replies remain fragmented to
seven-byte sends and collection cannot finish until the final reply is delivered.

All114 previous images remain byte-identical. Three runtime sources changed among281
frozen inputs. Positive owner sizes are17544 bytes (ordinary) and17624 (forced late),
within the existing24-KiB limit. Both linked text extractions equal qualified raw;
reviewed critical depth remains3968 of4088 usable stack bytes, leaving120. The changed
Wait poll is shallower. This scoped linked-binary review is not a general stack proof.
No kernel, shared core, SDK, resource budget, sibling, dependency or released-pin change.

Attempt1 also passed all90 native cases; its original sources, logs and stack audits
are preserved because the post-run review removed the residual probe-counter logic.
No failed native attempt is hidden. finalize.py verifies both source snapshots and
archives all generated outputs, compares archived and live hashes, then deletes only
the verified duplicate run directories. SHA256SUMS seals evidence after updated docs.

Natural collection is still scoped to the existing three authorized children; it is
not general process lifecycle or arbitrary waits after collection. Actual dash main,
startup metadata/directory authority, parent construction, descriptor assumptions,
private readiness and fixed argv/env remain integration work. Reuse existing scoped
startup facilities; no successful compatibility stubs. Independent consumer replay,
unchanged pipeline acceptance and assembled serial shell remain open, followed by
persistence/OpenZFS, packages and sys-init R1 assembly.
