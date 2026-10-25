# UL-067 local backend rebuild

Normal and empty cat backends are rebuilt locally from the captured finalizer
snapshot's C/Rust sources. Their complete ELF bytes match the backend portion of
all25 passing local finalizer/cat payloads. [Results](results.json) bind each case,
native receipt, backend size/hash and comparison. All six owned build commands
complete successfully with process cleanup; no failed attempt occurred.

This closes local backend-build provenance for the [25 native cases](../toybox-finalizer-consumer-2026-09-07/README.md).
Their original receipts remain unchanged. Native tests were not repeated because
the consumed backend bytes are identical; this is a source-build/equality check,
not a new native run or full producer/regression qualification. SDK libc/CRT remain
pinned dependencies, not freshly built in this step.

The [driver](build-backend.py) verifies the snapshot and SDK/tool pins, selects
exact producer compile/link commands, rewrites private output/SDK paths and uses
the existing owned process runner with clean environment and180-second limit.
Rust resolves to the locked compiler/library path. Payload lengths, receipt hashes
and every backend byte are checked. Mismatch fails; expected hashes are unchanged.

```
python3 -B experiments/toybox-native/build-backend.py --snapshot build/toybox-final-consumer-1kzyda6n
```

Scope/review: UL-067 build/evidence closure under Foundations O/I/E and CP/TD/TE;
see [plan](PLAN.md). Codex reviewed command selection, path mapping, source/tool
checks, envelope offsets/lengths and normal/empty selection against the recorded
recipe. No runtime source, authority, ABI, SDK, upstream license or marker change.
Independent reader review remains pending. Outputs stay under build; no target
installation, network fetch or sibling edit.

The [new close-policy producer plan](close-producer-plan.md) describes remaining
diagnostic/re-entry behavior, including `cat: close failed\n` and a failure latch.
That text differs from the earlier local proposed diagnostic; choose and record
exact bytes during completed-handoff review instead of silently changing either
oracle. [Current observation](close-intake-status.json) lacks the final manifest,
native receipt and archive. No close-policy runtime bytes were consumed.
Next: completed close-policy intake, remaining CAT-06 cases and full producer/
regression qualification. UL-067/M3 remain active; optional tuning stays deferred.
