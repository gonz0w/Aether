# Maintained ABI22 developer recipe — 2026-10-03

Requirement: replace dependence on dated composition scripts with one maintained
offline build/run command for the existing useful workload. No native owner,
shared ABI, payload policy, released standard pin or sibling source changed.
[Guide](../../AETHER-BASELINE.md), [lock](../../aether-baseline.lock.json),
[prior disposition](../../SI07-DISPOSITION.md).

## Reviewed change and simplicity

The simpler alternative was to retain only dated experiment drivers. Those remain
valuable evidence but make contributor reproduction depend on temporary paths
and procedure. The chosen recipe reuses the verified source archive, dependencies,
three payloads, Rust owner and existing bounded-tool helper. It adds one explicit
entry point and one local experimental composition lock. No generic build system,
installer, new image format or descriptor interpreter is added. This removes
manual source-copy/environment/rebuild/run steps from future baseline iteration;
it does not delete historical drivers or grow runtime machinery.

The recipe verifies bytes before archive parsing/staging; archive membership,
ordinary-file type, size and path rules are checked. Inputs/tools are rechecked
before successful publication. Each invocation owns a fresh out/ directory and
child process groups. Failed commands retain status and bounded logs; preflight
failure creates no output. This is trusted host execution with bounded subprocess
capture, not a host sandbox, authenticated input source, filesystem deadline or
complete race-proof/shared-library closure. Sources under sources/ are the final
builder, its helper, focused controls and consumed local lock.

## Fresh consuming evidence

Both commands ran from /Users/cam/DEV/sys-init on macOS arm64:

```sh
python3 scripts/build-aether-baseline.py out/abi22-baseline-recipe-1 \
  --dependencies out/si07-loop/.deps --smoke
python3 scripts/build-aether-baseline.py out/abi22-baseline-recipe-final \
  --dependencies out/si07-loop/.deps --smoke
```

Both exit 0. initial/ retains the first run, preceding host-only failure-phase
reporting, output-parent-traversal rejection and help-spacing fixes. Its exact
builder source was not captured, so it is supporting evidence only. final/ is the
consuming witness for the retained final source. The final run records 3,012 ticks,
3,004 idle ticks, three reclaims, ordered terminal statuses 0/0/17, one useful
completion and halt. QEMU exits 0 after owned-group shutdown. Each result.json
records exact argv, tool paths/digests, ISO digest and output identities. Generated
ISOs remain in the named local out/ directories; this packet retains their hashes,
owner raw/ELF, envelope and logs, not the ISOs or dependency payloads themselves.

Both builds reproduce qualified owner.raw (10,152 bytes,
84bf743cc1bac1f926b4a00997509a64b1a0f5a29c805a7ee7d48a27e3dfb4da) and owner.elf
(24,248 bytes, 96bf4f50dc6523b0ce1943bbd850a24d26cb457ac7f9a6ebf0cfa11a7a862e2d).
The rebuilt envelope is byte-identical to the prior normal witness. Exact ELF
identity permits reuse of that witness's scoped stack inspection: 2,696 bytes,
4,088 usable. This is not an independent complete stack proof. Tool identities
and source/dependency manifests are pinned by the retained lock, which resolves
to the sealed si07-loop and si07-owner evidence. The recipe rebuilds the kernel
and sys-init owner; it reuses the three frozen userland payloads rather than
claiming a userland source rebuild. ISO byte identity is not required or claimed.

## Controls, review and limits

Nine focused host tests cover archive missing/changed/duplicate/link/traversal
members, source budget, changed pins/symlinks, malformed envelope/profile/size,
existing-output preservation, parent traversal before intake, preflight failure
without output, failed-phase retention with no later stages, and real help/version/
usage exits. Tool-failure injection is a mock host control, not a native failure
or standalone timeout campaign; existing bounded_tools controls cover its runner.
See focused-tests.log and the aggregate receipt retained after checks.

Foundations E-01–08, O-01–05 and I-01/03/05/06 apply. Distribution RL-01/02/05
require exact experimental scope and assembled release separation; B-01–04's
older multi-module transport is not imported into AENSI001/ABI22. This recipe adds
no service descriptor or authority mechanism. Experience adoption covers plain
ASCII progress on stderr, result JSON on stdout and explicit exits. Host paths in
errors follow the existing developer exception; no operator renderer is claimed.

This is local technical review, not independent reviewer approval. Fixed-memory
bytecount, finite epochs, test startup/grant probes, developer r/h console,
protocol coverage gaps and profile separation remain as documented. The next
small slice is a build-time validated inert service table and separate test setup;
bounded supervision and explicitly matched usable environment follow. Full SI-07
and v1 remain open. Broader platforms and shelved lifecycle features stay deferred.
