# Bounded file-backend recovery

All401 command cases and98 Python host tests pass, with offline pin/workflow
checks. Final run: command-runner-suite-xfkpp2iw. command-results.json records
the complete target run; manifest.json binds this packet.
Scope: AECAT004 native file forwarding after a complete malformed backend reply.
This packet is producer evidence, not consumer acceptance or release readiness.

The file service performs a real open/read/close and corrupts reserved reply byte12.
The owner validates the entire reply before publishing a handle, advancing the
read position or retiring a description. Invalid replies close the client reply
endpoint. The unchanged poison client requires EIO, unchanged read-buffer sentinels,
no partial open publication, consuming local descriptor cleanup, restored signal
mask and no further channel calls. The owner rejects further client requests.

After observing client1, the owner requests scoped stop and queries the file-service
terminal record for kind3/detail143 before clearing descriptions. It never retries
the uncertain operation or guesses a backend handle. Stream cleanup still requires
normal17; all endpoints close and six workers are reclaimed across two generations.
Forced stop produces no normal-exit log line. Exact logs therefore contain client1
and stream17 per generation; the owner checks the retained stop record twice, and
an omitted-stop control must reject1601 after client1 with zero reclaims.

Commands use the existing captured native SDK and tools lock:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The reference contains the before-code requirement and simplicity review. No new
kernel API, wire version, quota, upstream object, SDK default, sibling change or
released pin. Three workers, six channels, two local records and the8192-byte owner
limit remain. Complex policy remains outside the kernel. The checked exchange
shares request encoding with the existing fatal wrapper. Private callers provide
zeroed reply storage and do not expose it after failure. Reusing that buffer avoids
an aggregate reply copy; common helpers are explicitly kept out of line.

## Attempts retained

- command-runner-suite-8h75f0i1: build incomplete, zero executed cases. The initial
  backend-open owner exceeded the linker-enforced two-page code limit. Full source
  input snapshot, result, log and generated artifacts are retained.
- Size-only preflights also rejected several intermediate layouts. Their compiler
  logs, command/size records and source overlays are retained rather than erased.
  Each overlay replaces the four runtime files in the first full source snapshot;
  other runtime inputs were unchanged. The final shared-reply preflight builds all
  selected new and old poison variants under the unchanged bound (largest8120).
  These are compilation checks, not native execution. No linker limit was raised.
- command-runner-suite-sy9hq6i9:11 cases passed; backend-open was incomplete under
  an incorrect harness expectation of a normal-exit line for forced stop. Its log
  has client1/stream17 twice and supervisor100/reclaimed6. The correction changes
  only the harness's exact serial expectation; runtime sources remain identical.
  Full failed-attempt sources, result, log and artifacts remain in this packet.

collect.py verifies the final frozen runtime inputs, previous sealed packet and
four-file simplicity snapshot before retaining sources and target artifacts. Its
archives are read back and hashed. manifest.json binds the packet after review.
Host preflights remain separate from the final host log. No fresh M4 run was
selected because no kernel or M4 path changed.

Missing/partial replies and bounded backend timeout injection remain unqualified.
The checked transport returns uncertainty on failure, but those branches need
separate target witnesses. This immutable embedded file service is not persistent
storage, OpenZFS, a general VFS or the complete dash/exec/wait/pipeline handoff.

The sealed snapshot contains213 sources and12809 target artifacts, including both
unsuccessful full-suite attempts. owner-sizes.json records all final cat variants;
the largest remains8120 bytes. review-checks.json records final scoped checks.
