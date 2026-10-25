# Session channel lifetime core

2026-09-24. Implements the channel object's bounded fifteen-generation creation
entry, with existing three-generation creation preserved. The new entry is not
reachable from native launch/admission: AENMX007/ABI21 and SESSION remain unimplemented.
This is a preparatory kernel component, not native session acceptance.

## Scope and guarantees

Channel.create and Channel.createSession use one private creation implementation
with compile-time limits3 and15 respectively. Busy objects reject with EBUSY(-16),
retired objects with ENOSPC(-28), and rejection changes no state. The retirement
comparison now rejects generations beyond a selected bound as well as at it.
There is no layout/size, allocator, authority, syscall, wire or release-pin change.
Only a future kernel profile selector may select the new entry; request bytes cannot.

The two new host tests exercise the actual channel code across all15 generations:
all prior reader/writer capabilities remain invalid; ownership transfer removes the
former holder's access; partial closure prevents reuse; last closure zeroes unread
bytes; distinct channel identities remain isolated; exhaustion does not mutate;
legacy objects still retire after three uses. Stream capacity stays32 bytes.
They do not prove native process quiescence, dispatcher fairness or pipe EOF.

A separately copied stale-lookup mutant ignores the capability's generation bits.
The new test rejects it at the stale-reference assertion with TestUnexpectedResult.
The mutant never replaces runtime source or enters native artifacts. Its source,
command and expected failure are retained. Passing this control is evidence of this
specific test sensitivity, not coverage of all lifecycle bugs.

## Reproduction and limits

```sh
zig test kernel/native_channel.zig --test-filter session --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The existing dirty worktree is preserved. No sibling, old evidence or standard pin
is modified. Frozen source/support inventories include tests/test_build_policy.py;
archive verification precedes deleting completed owned output roots. Native suites
are sequential; exact tools/flags, transcripts and artifacts are retained. The
matching native regressions exercise the existing three-use path, not the new entry.

Next integrate explicit profile-selected allocation/admission limits, reusable pipe
and child lifetimes and authenticated identity tracking, then run the complete
unchanged composed script and controls. That native qualification and independent
consumer replay remain required before any SESSION or full-shell claim.


## Final results

- Complete105-case capacity,358-case connections and431-case command-runner suites
  pass:894 native cases on identical287 runtime inputs. Connections/runner also
  record five Finder metadata inputs; those are not build inputs. Each suite
  finishes below its1800-second review budget; exact elapsed times are retained.
- Full host command exits0 with110 Python tests plus configured Zig/Rust and offline
  standards checks; direct execution confirms both new channel tests pass. The
  generation-blind mutant fails exactly at stale-reference rejection.
- All148 capacity worker/owner binaries match the preceding packet. All105 kernel
  executables change and are qualified by fresh target runs. Existing owner stack
  audits therefore remain applicable to identical owner bytes; no new stack claim
  is inferred for an unimplemented session owner.
- All306 host/source-support inputs are frozen. The only changed source versus
  the prior qualified snapshot is kernel/native_channel.zig; channel.patch retains
  the exact scoped change. Full source archives, tool/SDK hashes, flags, logs and
  artifact inventories are included. No build/native failures occurred; the
  deliberate host mutant failure is retained separately.
- Format, simplicity snapshot, workflow and whitespace checks pass. Final archive
  readback and source verification are recorded in verification.json; cleanup
  receipts bind the verified archives to removed owned output directories.

This closes the channel-core substep only. Profile-selected guest reuse and the
composed-session workload remain unimplemented and unqualified.


Archive retry: the first runner archive was rejected because output-root .DS_Store
changed after inventory hashing. The mismatch audit checked every member; all
other files match. The failed archive, original inventory digest and failure log
are retained. The original earlier metadata bytes were not snapshotted; only their
digest survives. No generated directory was deleted by that failed attempt. The
unchanged archive verifier is rerun against the retained originals; only successful
readback/original-file verification permits cleanup. This is a packaging failure,
not a native test failure or permission to bypass verification.


The runner retry verified all8796 members before cleanup. All three completed output
roots were removed only after successful archive/original-file checks, reclaiming
9,979,300,569 bytes (about9.3 GiB). The failed compressed archive remains preserved.
All three native reports have identical tool-lock, tool inventory and SDK receipt
hashes. The final verification rereads every archived artifact before sealing.
