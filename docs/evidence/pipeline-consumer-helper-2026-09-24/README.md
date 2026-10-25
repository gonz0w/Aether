# Actual consumer helper in the pipeline — 2026-09-24

Qualification pending. The preimplementation review is in NATIVE-SHELL-STARTUP.md.
The existing pinned helper.c is compiled unchanged with main renamed to
consumer_helper_main, then linked without the dash objects into both replacement
workers. Its copy branch performs actual libc reads/writes using inherited fd0/1.
The private wrapper retains bootstrap, descriptor validation, report/readiness,
diagnostic/rights probes and explicit close after helper return. This is consumer
helper execution within the private pipeline, not actual dash main/eval or unchanged
pipeline script acceptance. The parent still orchestrates creation/wait privately.

The negative control skips relay main; after the existing forced first write, it
closes the pipe ends. The actual final reader gets EOF with no output. Exact2743
missing-capture rejection with zero reclaims is required. A generic failure or
timeout cannot pass. Existing authority, malformed exec, interruption and cleanup
regressions remain in the complete suite.

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

No sibling bytes, pins, kernel/SDK interfaces or resource budgets change. Actual
helper uses a4096-byte local buffer on its existing native C worker stack, separate
from the one-page Rust supervisor stack. General environments, dash orchestration,
independent replay and assembled serial-shell acceptance remain open.
