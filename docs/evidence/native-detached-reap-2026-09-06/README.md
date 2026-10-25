# Detached thread exit and safe reaping

The [contract](contract.md) records the requirement and forbidden premature
reclamation before implementation. Actual musl detached exit runs key destructors
and unlinks the thread list. A fixture `__unmapself` publishes saved mapping
identity and exits through the existing native child operation. The parent owns
reaping: observe that exact child stopped, unmap its stack/TLS under the memory
grant, then retire its native ID. It never dereferences the departed pthread.
No kernel ABI, capacity, release pin or sibling repository changes.

Both children are gated while still executing on their departing mappings.
The positive path must defer reaping and reject direct unmap with -13 and no
quota change. The deliberate missing-observation control fails exact status 291.
Key callbacks, thread-list unlock, quota restoration and two-batch reuse are
checked, including supervisor replacement. Reaping is bounded fixture policy;
production libc integration, orphaned-parent recovery, cancellation, robust
mutexes and dynamic pthread_detach remain outside scope.

Attempt 1 is a fixture/oracle failure, not an accepted negative test: the reaper
scanned every record while the live-child assertion expected no reclamation.
A stopped peer could therefore be reclaimed and produce status 291 on the
positive case. The fix selects exactly one record for each call and accounts for
each completion once. The complete failed snapshot and serial logs are retained
under `attempt-1/`; subsequent qualification uses the corrected frozen sources.

Reproduce with the existing command, adding `--large` for the second profile:

```sh
python3 scripts/thread_smoke.py --pthread-lifecycle \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/check_workflow.py
```

The SDK path identifies the inspected local producer; its tools and source
identities are retained in the producer receipts. Private outputs, bounded VM
runs, exact expected/observed terminals, executable digests and original/adapted
header inventories are retained. Upstream key create/set/get bytes match musl
1.2.6 in all eight relevant producers across both profiles.

`kernel-identity.json` matches all 34 kernel/build inputs against the preceding
[timed-condition qualification](../native-timed-condition-2026-09-06/README.md).
Its raw-pair, memory and M4 results are retained coverage, not newly run tests in
this slice. Current lifecycle sources are separately bound by each result and
source archive. Independent consumer acceptance and release readiness remain open.

Final qualification passes all 76 target cases (38 per profile), 98 Python
tests and Zig host checks. Workflow, pinned Clang formatting and diff checks pass.
Both final suites bind identical runtime source hashes, still matching the current
files after completion. All failed and successful attempt receipts are retained.
