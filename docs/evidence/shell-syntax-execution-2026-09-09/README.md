# Consumer syntax-error execution

All 426 command cases and 98 Python host tests pass, with Zig, offline pin and
workflow checks. Final run: command-runner-suite-c3f31pqg. The selected consumer script
is unchanged `if then` plus newline (eight bytes), verified against userland's
manifest and the C fixture literal before execution. Actual pinned guarded dash
main receives `sh -c`, WITNESS=value, LC_ALL=C, PATH=/nonexistent and admitted
PWD=/work. This selects command-string input; it does not add a new script-file
path or claim the remaining shell workload set.

The positive case requires empty stdout, native diagnostic
`sh: 1: Syntax error: "then" unexpected` plus newline, exit2 and four reclaims
across two generations. Exit2 and empty stdout are the unchanged consumer oracles;
the exact native diagnostic is a separate producer check, not a requirement to
match a Linux script pathname. Skipping main returns0 and rejects owner1501;
omitting adapter descriptor closure retains exit2 and rejects1503. Both controls
require zero reclaims and their exact client terminal context.

## Dependency finding

Userland's phase-one argv case runs an actual external helper, and signal-table
uses command substitution before trap/self-signal. They need native process,
exec/wait, descriptor and pipe composition. Their complete original scripts,
stdout oracles, manifest and helper source are retained under consumer-inputs;
none is rewritten or counted as passing. The local reference and ROADMAP record
the corrected dependency ordering and the next process design requirements.
No sibling changes, independent acceptance or production service assignment follow.

## Reproduction and scope

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

scope-review.json and the before-code reference record ownership, forbidden
outcomes, cleanup, bounds and simplicity. Reuse the existing parser/main and
stream owner; no new service, kernel/wire/SDK interface, unsafe boundary, quota,
upstream object or released pin changes. C retains its compact-style migration
exception and pinned warning checks; Rust uses edition2024. No fresh M4 run is
selected because kernel/M4 paths are unchanged. The owner preflight is5760 bytes
within8192. This is producer syntax/cleanup coverage, not full dash, native process
composition, TTY, persistent storage or release readiness.

collect.py verifies frozen sources, the prior sealed packet and the four-file
simplicity snapshot, then reads back source and target archives. run-timing.json
records this run's exact outer command, UTC endpoints and monotonic elapsed time.
The final manifest binds this packet. Existing evidence remains unchanged.

All 281 prior cat-owner images are byte-identical. The largest owner remains8152
within8192. No native attempt failed. The full run took about1419 seconds, below
the1800-second review ceiling. Sources and artifacts are retained by the collector.

Verified archives retain 213 frozen sources and 8,650 target artifacts.
