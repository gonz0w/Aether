# Validate mapping coverage once, retain every live-context pin

Before-code scope,2026-10-05. R1-03 repeated dynamic-service replacement still
exceeds30 seconds. Native protect/unmap constructs a valid owner mapping plan,
then calls the identical full arena coverage scan again for every running child
solely to check FS/clear-TID pins. With82 live records and8192 owner records this
multiplies metadata work; no ownership changes between those calls under IF=0.
Do not assume this is the only delay or weaken the watchdog to qualify stress.

Keep the full primary range/length/alignment/arena/anonymous-coverage preflight and
its error order. Extract only the existing two-page FS and4-byte clear-TID overlap
checks into a method on the already validated range Plan. Range calls it before
coverage exactly as before. Child preflight calls it once per live context, then
keeps full TLS-region and stack overlap checks unchanged. Wait-address pins,
authority, table resolution, detach/CR3/zero verification/quota return remain.
No pin may disappear, no user bytes or addresses are trusted through this helper,
no mapping/authority is retained outside the owner-serialized operation. Plans are
private trusted values; require range construction before child pin checks. Stop
and interrupted/failed operations retain their original cleanup obligations.

Simpler alternative: keep repeated whole range scans. They check identical stable
coverage needlessly for every child, so share only scalar pin validation from the
already-validated range. Remove repeated coverage work without a persistent index,
cache, allocator, new ABI/flag or general VM refactor. No external dependency or
new unsafe boundary; existing per-core owner/IF-clear and compiler/trap contracts
still apply. Total coverage work becomes records+request pages+live-context pins;
this is an algorithmic observation, not calibrated latency or WCET.

Before changing runtime, retain a fresh current-baseline repeated-service timeout.
Then qualify all twelve copied copy/dynamic/mask/origin controls, repeated full
service replacement, a four-round322-admission reuse schedule and a real pin-bypass
control. The control uses RW protect on a pending live thread,
requires EACCES, and exact373 fails when the existing skip-pin mutant allows it.
The guard page may change in that isolated mutant; it is not production acceptance.
Both baseline and changed target use the same QEMU/software emulation profile and
180/30/3-second build/guest/teardown bounds. Retain failed attempts, snapshots,
commands and semantic control context; freeze all inputs during each run.

Add focused Plan pin boundary/coverage-order model checks and run full host/pins,
selected maintained190 memory/pair/lifecycle/stack/signal target regressions,
formats/simplicity/link/AST/source checks. Update local reference/workflow/STATE/
ROADMAP/feasibility only after qualified evidence. Verify archive members before
removing only owned duplicate roots. No public ABI/SDK/quota/default pin/sibling
changes, broad runtime refactor or production OpenZFS adoption. Full engine
resources/providers/calibrated clocks, production helper placement, actual consumer
and reader reviews and assembled R1 remain separate requirements.

Development attempts: workflow mutation initially selected nonexistent `references`
key instead of the inventory's `interfaces`; no inventory write occurred before
that KeyError. Corrected to interfaces. Direct Zig model invocation without the
workspace cache flags failed compiler_rt/std loading with PermissionDenied; retain
model.log and retry with the existing local cache/global-cache command. Neither
failure is a model/correctness result or a reason to widen host permissions.


Before attempt3: thirteen native cases pass, including repeated full-service
replacement and four-round reuse. Pin-bypass control fails its exact373 context:
it also invokes the ordinary early-unmap test with pins disabled, producing fault6
instead of the intended semantic terminal. Preserve raw mutant fault/panic evidence;
not373 acceptance. Isolate the RW protect assertion from destructive
live unmap in that fixture only; normal early-unmap remains elsewhere. Add matching
non-mutant pinned-protect positive and rerun all fifteen. Runtime remains unchanged.
