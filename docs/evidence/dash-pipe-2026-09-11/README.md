# Actual dash command substitution

Status: qualified for the scoped native producer cases below. See [PLAN](PLAN.md).

Pinned actual dash and musl now exercise public pipe(), fork, dup2, close, read
through EOF and wait3 in the private producer. Exact pipe bytes and independent
backend stdout readback both equal `pipe\n`; normal child0/parent0/backend17
occur twice with six actual reclaims. The negative header and false wait-status
controls require owner2174 and parent1/owner2176 respectively, with zero reclaims.
This first integration uses the bounded stream backend, not UART input. Same-parent
pipe reuse, serial adoption, installed SDK acceptance and R1 assembly remain open.

The first preflight compiled but could not build its kernel because the audit
helper used the nonexistent `native-process-copy-signals` option. Correcting it
to the existing `native-copy-signals` option produced three passing QEMU cases.
Both attempts retain sources and command/error logs. Formatting and harness
registration were completed before the final qualification freeze.

Run the existing commands with the pinned SDK/tools:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

No kernel source, sibling, SDK, released pin, resource quota or upstream object
changed. Unsupported exec fails ENOTSUP. The new dispatcher is a bounded workload
owner, not a general process server. Unanticipated failure contains the fixture;
independent consumer/reader review and broader recovery coverage remain pending.

## Simplicity and implementation review

1. The simpler alternative is to retain the scripted pipe client alone. It proves
   the endpoint mechanics but cannot show that dash's parser, substitution,
   redirection and wait ordering compose. We choose pinned upstream dash objects
   with a small private adapter, reusing the existing pipe core and stream backend.
2. Extending the old exec dispatcher would couple its three-binding replacement
   and status72 witnesses to five-binding pipe snapshots. This focused dispatcher
   admits one child, observes two request routes and retains one wait result. It
   uses the existing framing, masks, ready/complete handshake and backend protocol;
   no generic service, VFS, new wire format or extra privileged kernel state is
   introduced. Copy failure rollback and live-pipe exec are intentionally deferred.
3. No old path can be removed now: scripted probes still cover faults, stop,
   reply loss and SIGPIPE schedules that this shell command does not exercise.
   The actual-dash profile supplies integration evidence alongside those controls.

Authority is selected from the connected parent/child route, never an asserted PID
in a pipe request. Admission validates all sixteen FD slots before copy, stages
both endpoint holders and publishes them only after child readiness. Ordinary
stdio references differ between parent and child while sharing backend positions.
The terminal observer checks request-route EOF before releasing remaining holders.
Wait completion follows actual child terminal and pipe EOF, and reclaim follows
acknowledgment. Unexpected states fail closed rather than fabricate completion.

Public pipe() accepts the same valid writable two-int storage as the private
adapter; invalid user addresses are not claimed to return EFAULT in this fixture.
The owner uses fixed stack buffers, no allocator and no new unsafe block. Native
calls borrow these buffers synchronously; no borrowed pointer is retained across
copy or reply. Image bounds do not establish general stack/performance bounds.
This is an implementation self-review; independent reader review remains open.


The first complete connections attempt stopped during the new dash profile's
kernel build after 125 passing cases: combined flag groups duplicated Zig boolean
options for signal actions/public access. The harness now adds only mask-delivery
and termination for the new pipe profile, leaving action/public/copy-signals to
the existing dash group. The failed suite and its frozen preflight source snapshot
are retained. The earlier claim of a full-harness dash pass was premature; only
focused execution had passed at that point. Final qualification is a fresh run.

## Results

All 268 connections, five launch and two console cases pass (275 QEMU cases).
The final focused positive and both semantic controls pass. Host/harness, scoped
Rust/C format, workflow, three released pins and simplicity checks pass. The
unsupported file-binding/pipe-exec configuration controls still reject by their
named diagnostics. All prior copied public-fork client ELFs are byte-identical.

The maximum owner image is 10832 bytes under the unchanged 16 KiB bound; this
is not a peak-memory or worst-case stack claim. Exact identities, traces, source
snapshots, source patch, build commands and run timings are retained. Preflight
archives preserve the failed build-option attempt, first successes and final frozen
success. The initial full-suite build failure is also archived. Only archive-verified unpacked preflight and failed-suite duplicates are removed; final
suite outputs remain available. No owner sign-off or installed consumer acceptance
is inferred from passing producer tests.
