# Handler entry after ambiguous read replies

Before implementation: reuse owner-side malformed and truncated first-read replies.
The guarded read must poison the connection before pending handler entry. Handler
write/close attempts must return EIO without a new channel trap; local descriptor
retirement still occurs. Caller receives EIO with its sentinel read buffer unchanged,
observes the restored mask, retires remaining descriptors without traffic, and exits1.
Existing owner verifies read position11/no output, backend closure, retained terminal,
channel closure and two generations/four reclaims. Skipped handler injection must
reject client98/owner1501 after the uncertain reply.

Reuse existing poison counters, handler hook and private mask-delivery option.
No kernel change, new wire messages, authority, quota or allocation. This bounded
post-reply test is smaller than asynchronous partial-request cancellation; it does
not qualify that or nonlocal error exits. Full command and host/pin checks run on
frozen sources with strict C compilation and scoped whitespace checks. Preserve
attempts, pins and siblings. Previous M4 remains scoped; no new M4 claim.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain command/source/tool
identity and target logs. collect.py verifies the previous known-error packet,
simplicity snapshot and every archived source/artifact member.

Results: all 276 command-runner cases and host/pin checks (98 Python tests) pass.
Both ambiguous-reply positives complete two generations/four reclaims with no
post-poison channel calls and unchanged caller buffers. Skipped injection rejects
client98/owner1501/reclaimed0. Sources stayed frozen; no failed or interrupted
qualification attempts occurred. Scoped whitespace checks pass. Nonlocal exits
after ambiguous replies and arbitrary partial-request cancellation remain open.

Packaging correction: the first collector accidentally omitted the selected target
directory and produced an empty artifact archive. That packaging attempt is retained
in collection-attempt-1. Restore directory collection and require nonempty artifacts
before sealing; the native qualification itself did not fail or change.
