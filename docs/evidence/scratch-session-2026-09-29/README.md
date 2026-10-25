# Scratch session producer delivery — 2026-09-29

Requirement: integrate the pinned unchanged consumer scratch session in three native
parents. Preserve AENMX007/ABI21,15 lifetimes, three children/two pipes,24KiB owner
and4088-byte stack. Userland owns scripts and subsequent acceptance; Aether owns
this private owner/adapter contract. No sibling, public SDK, kernel ABI or pin edits.

Before code: add two typed scratch-description bindings after the existing seven
bindings. Retain the16-FD table, common alias/CLOEXEC machinery and existing pipe
routing. Validate the full descriptor table, then project only pipe bindings into
existing pipe lifecycle operations. Never reinterpret a scratch selector as a pipe.
Use a small owner-local volatile namespace with exact frozen seeds, bounded bytes,
shared offsets, explicit holder bits and non-wrapping namespace/description IDs.
Authenticating the connection remains the dispatcher's responsibility. Names, FD
numbers and selector values alone cannot grant authority. No filesystem persistence
or image authority is added. The legacy five-binding/two-peer scratch adapter is
not compatible with this four-peer session and stays unchanged.

Forbidden: client-generated denied errors, truncated stale data surviving truncate,
closing another alias's holder, premature reuse, protected-object mutation, fabricated
AB/EOF, unobserved child2, quota growth or claiming full shell/SDK conformance.
Select parser/authority/alias/stale/exhaustion host controls, linked owner inspection,
then the composed native workload and semantic mutations with confirmed cleanup.
Run relevant existing session/native regressions and the configured host suite.
Retain failures, freeze runtime sources during runs and archive verified duplicates.

Simplicity: reuse existing descriptor handling and pipe primitives; two extra typed
bindings avoid a temporal scratch/pipe overlay. This adds only the state the current
script needs, with no generic VFS or service framework. Explicit bounded storage
and holder ownership keep the new trusted surface auditable. No new unsafe/assembly
boundary is needed; existing synchronous transport borrows buffers for each call.
Update STATE, ROADMAP, interface and workflow with exact results and remaining gaps.

## Result and ownership

Producer qualification is complete. The original consumer script/helper and both
seed files remain hash-pinned in consumer-inputs.json/tar.gz. Three dash parents
produce the exact52-byte stdout and19-byte stderr, with21 copies,15 helper
replacements,18 image admissions and24 terminal/reclaims. Slot0 uses generations1–3;
slot2 uses1–15 (denied child at1/6/11, reader at2/7/12, argv at3/8/13, pipeline writer
at4/9/14, closure at5/10/15). Slots3/4 use1–3 for the other pipeline stages. The
reader is collected and reclaimed before argv/pipeline work. All other healthy
stages and parents exit0. This is a private volatile fixture, not OpenZFS or a
persistent/general filesystem, shared SDK adoption or an assembled R1 shell.

149 capacity cases and five unchanged non-pipeline command regressions pass.
127 Python tests and the configured Rust/Zig/offline-pin checks pass; the pipe-core
wrapper includes79 Rust tests and no_std compilation. Twelve scratch native log
comparisons and96 lifecycle/stream counterexamples pass. Frozen native logs and
reports are in capacity-artifacts.tar.gz/results.json; legacy and initial runs
have their own archives and receipts. None of the existing broad connection or
runner suites is claimed as rerun. Kernel bytes and ABI/resource limits were not
changed; the selected full capacity suite covers the shared session machinery,
and the legacy commands exercise the existing adapter consumers.

## Authority and data checks

The private owner authenticates each request through its existing endpoint and
native identity ledger. Namespace selectors alone are not grants. Opcode86 accepts
only canonical bounded frames, explicit modes and two frozen paths. Denied writes
return EACCES and no description; the exact requesting child must terminate2 with
no committed replacement image. A copied child2 without that owner decision stops
the parent and requires confirmed cleanup. Protected bytes are immutable; every
successful final observation checks them, exactAB, the cleared truncated tail,
two written/read bytes, actual EOF, one denial and zero holders.

Scratch bindings7/8 are distinct from standard0–2 and pipe3–6. Full descriptor
snapshots are validated before projecting away file entries for pipe operations.
Aliases share one description offset/peer holder. Copy inherits holders only after
native admission; exec validates first and applies CLOEXEC releases before publishing
replacement execution. Confirmed terminal clears remaining holders before reuse.
A namespace is reset only after cleanup; description allocation sequences never wrap.
The stale-reference control sends the closed writer's selector after binding reuse
for the new reader and requires EBADF with a zero reply body before real reading.
It cannot satisfy the new read or advance its offset.

Safe Rust stores at most32 data bytes and two descriptions. Host tests cover foreign
peers, stale namespaces/types, malformed frames, descriptor and allocation exhaustion,
write capacity, rejected inheritance/commit and truncation beneath a live reader.
The latter returns EOF at the old reader offset without subtraction underflow.
The existing synchronous transport retains its buffer ownership and signal masking;
no new unsafe/assembly interface, service process or dependency was added. Arbitrary
interruption during these private exchanges, general filesystem concurrency, wider
namespace service recovery and fuzzing are not newly qualified. Those become gates
before promoting this fixture into a shared SDK/service, rather than implied by
this bounded success. Security and independent reader review remain separate.

## Frozen controls

| Case | Exact outcome after cleanup |
| --- | --- |
| composed | Three parents0; exact streams and24 reclaims. |
| lose-b | Store a zero in place of B on the real second write; parent0, eight reclaims, stdout contains A-NUL; owner2880 rejects final file state. |
| bad-read | Corrupt the real reader reply from AB to @B; normal24 reclaims; exact stream oracle rejects. |
| wrong-denied | Change authenticated EACCES to ENOENT while preserving no handle/protected bytes; child2 alone still looks healthy; owner2882 rejects after eight reclaims. |
| skip-read | Fabricate EOF before reading; parent0, eight reclaims, missing AB; owner2883 rejects missing data/EOF proof. |
| skip-request | Client fabricates EACCES/child2 without owner lookup; confirmed parent stop (kind3/detail143), two reclaims, owner2884. |
| early-close | First alias close retires the writer while another alias remains; later write fails, actual parent141, one reclaim, owner2885. Exact stderr is `sh: 7: printf: printf: I/O error`, no newline. |
| wrong-env | Reader succeeds; argv helper91/parent66, four reclaims, owner2886; stdout is denied/AB prefix. |
| fd-leak | Closure helper95/parent68, eight reclaims, owner2887; no final diagnostic/success. |
| stderr-error | Retire actual parent stderr; write and exit-time close fail, parent141/eight reclaims, owner2888; exact stdout through closed-ok and empty stderr. |
| stale-reference | Old writer selector rejected after binding reuse; unchanged positive streams and24 reclaims. |
| bad-byte | Change healthy pipeline payload byte; normal24 reclaims; exact stdout oracle rejects. |

All mutant flags are opt-in fixture builds. No timeout substitutes for a terminal
or reclaim. Complete allowed prefixes, identity/admission sets and completion order
are executable in scripts/scratch_smoke.py. Original positive workload bytes never
change; the bad-byte case is an explicit client mutation recorded in its build.

## Linked resource inspection

All26 rebuilt legacy/session/recovery/failed-exec/scratch owner variants have matching
ELF-to-raw bytes. Maximum immutable code is18808/24576 bytes; maximum estimated
stack is3896/4088, leaving192 bytes. owner-bindings.json records every image digest
and bound. The inspect-owners.py aid retains disassembly and call-path details;
inspect-indirect.py binds1002 indirect call sites to immutable memcpy/memset/memcmp
pointers. Register-loaded call paths were inspected against the generated assembly.
These are scoped static inspection aids, not a formal stack proof, kernel-stack
measurement or independent review. Native completion is additional evidence; none
of the previous3768-byte estimates was reused for changed code.

## Attempts, source identities and replay

The first composed native run passed. Its303 runtime sources were reconstructed
from the subsequent narrow control edits and verified individually against that
run's original hashes before archiving as initial-sources. The original image/logs
remain in initial-artifacts. The first host checker counterexample incorrectly
swapped a denied terminal with a later admission, which is still a legal ordering;
the failing test is retained and now swaps the two actual phase terminals instead.
The first archive invocation supplied a relative path and was rejected before
mutation; its absolute-path retry verified all members before deleting duplicates.
An initial workflow entry lacked its required reference and was corrected before
the successful workflow/host checks. No failed native attempt is hidden.

The full149-case native run used controls-1-sources.json/tar.gz and passed unchanged
source-hash checks. Afterward only the new host oracle was tightened to require the
observed early-close diagnostic and formatted locally; the native source and binaries
did not change. All12 logs were rechecked, all96 counterexamples rejected again,
and the final127-test host suite passed with an added exact-diagnostic counterexample.
final-source-inputs records the delivered source/checker version; the distinct
native source version remains available. The final replay-inputs archive includes
source, support, frozen consumer inputs, dependency metadata, invoked evidence
drivers and standards snapshots. Its isolated host replay verifies completeness.
SDK/tools remain external, pinned by the native report and supplied tools lock.

From the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/pipeline_capacity.py --libc-build /path/to/pinned/native-c-build --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 docs/evidence/init-command-handoff-2026-09-08/run.py --libc-build /path/to/pinned/native-c-build --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The capacity command's `--case scratch-composed` selects focused coverage only.
Inspection/replay helpers accept the full capacity output directory before its
verified archive cleanup. Retained archives, hashes, timing/exit receipts and logs
replace redundant unpacked trees. No sibling repository or sealed prior packet was
modified. Released standards pins remain unchanged.

## Next external gates

Userland must independently replay SCRATCH-SESSION-01–06 against this delivery and
supply the real serial-session composition. SI-07 separately needs complete
versioned bootstrap/transport and rebuilt runner/bytecount; pure decoder tests are
insufficient. Shared SDK integration, independent reviews, persistent filesystem,
packages and the assembled boot-to-shell R1 remain open. Producer evidence does
not approve those owners or declare the release ready.
