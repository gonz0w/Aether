# 0186: Qualify serial-session entry and final-action denials

2026-10-04, BG-067 before-code scope. Requirement: reject every mismatched boot
handle before admission; preserve producer grant enforcement and deny final halt
while console authority remains live, even after shell/child settlement.

The simpler alternative is retained wrong-ABI and pre-admission busy-halt evidence.
Choose their existing mechanism with narrowly mutated private source copies, but
those traces do not cover all five boot handles or a console still live after ten
terminal/reclaim events. Add no maintained runtime branch, recovery policy,
profile engine or public CLI. This removes ambiguity in the acceptance matrix;
no runtime complexity is removed or introduced.

Freeze current recipe inputs/tools first. Build five single expected-handle
mutations, two actual wrong console-grant syscall probes (-13), and a private
omitted-console-close after the real workload with actual halt denial (-16).
Markers exist only in private controls to distinguish confirmed syscall results
from unrelated failure. Preserve maintained raw/ELF bytes and released pins.
The controls do not mutate kernel/client bytes or prove their missing/wrong-image
loader matrix. Boot argument comparison is distinct from producer grant rights.

Each private artifact must fit16KiB code/4088 scoped stack; retain linked assembly,
raw/ELF parity and immutable builtin inspection before boot. Compose from verified
sealed inputs, preserving client/spare/entropy and all six boot components.
Use existing bounded tool runner (180s/4MiB) and native smoke (90s/1MiB UART/4MiB
stderr, owned live-group cleanup). Failure is expected only after the exact
supervision boundary, unique control/failure markers, owner UD2/vector6 and panic;
no halt/fixture completion. Early cases have zero admission/terminal records.
Late busy halt requires the original exact workload and all ten terminals before
denial, no replay, and no successful halt. Host teardown does not establish guest
cleanup of retained console authority. Timeouts/missing tools are not denials.

Use independent negative oracles and trace mutations; run full local checks,
update existing quality/planning guidance and retain failed attempts in a new
sealed packet. Foundations O-01–05/I/E-01–08 apply. Distribution B/RL remain scoped
transport/evidence guidance, not ABI24 acceptance. Finite admission exhaustion,
uncertain cleanup/transport schedules, complete component-loader negatives and
independent assembled review remain next work. No sibling modifications or broader
platform campaigns. Original/borrowed terms and immutable evidence remain intact.
