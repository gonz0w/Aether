# Native connection owner failure probes — 2026-09-08

Eight final native probes qualify the paired-owner boundary on the pinned ABI9
kernel. They are deliberately separate from the real command/file protocol; all
workers in the successful ownership probes are explicitly stopped before cleanup.
Normal command owner variants rebuild byte-identically, preserving prior five
command-case evidence. Code and4 KiB stack bounds, released pins and siblings
remain unchanged. No new unsafe site or runtime dependency is introduced.

| Probe | Actual boundary and oracle |
| --- | --- |
| alloc | Hold five channels; first owner allocation succeeds, second returns EBUSY16. Retain and clean that pair before releasing held channels. Then six actual worker stops/reclaims across all three slots/two generations, result100. |
| alloc-first | Hold six channels; first owner allocation returns EBUSY16 with no owned endpoints. Cleanup makes no native release; release held channels, then result100/six reclaims. |
| launch | Actual invalid argc5 returns EINVAL22 before admission. Retain all four endpoints; cleanup precedes successful launches, result100/six reclaims. |
| stop | Wrapper sends an absent handle to the actual stop syscall, receiving EBADF9. Owner retains Live state/resources; disable this routing fault and stop the original worker, result100/six reclaims. The kernel error is not synthetic; the changed handle is deliberate test routing. |
| close | After controlled terminal, deliberately close the reply reader outside the owner. Cleanup closes request writer then receives actual EACCES13 for reply reader. Retain Unknown plus reader/worker state; further cleanup/start/stop make no backend calls. Expected result1602/reclaimed0 rejection, not recovered cleanup. |
| reclaim | Deliberately reclaim terminal worker outside the owner. Cleanup closes endpoints then receives actual EBADF9 on reclaim. Retain Unknown worker identity with no endpoints; no automatic replay. Expected result1603/reclaimed1 rejection, not owner cleanup completion. |
| alloc-omit | Private cfg omits partial-pair cleanup. The exact retained-resource assertion rejects at1601/reclaimed0. |
| close-replay | Private copied core removes the Unknown validation guard. Replay fails the exact Closed/no-call expectation at1601/reclaimed0. Maintained core stays unchanged. |

Control stop detail is143/kind3; the raw observation encodes144. The probe verifies
the decoded owner result. The kernel does not print worker-exit terminal lines for
controlled stops; final driver expects none and validates exact supervisor/reclaim
and PASS or specified panic context. No absence of a line substitutes for the
probe's actual observation check. Stop acknowledgment is repeated without another
backend stop call, then terminal is observed before reclaim.

The initial allocation probe failed1601/reclaimed0 because it compared decoded
detail against144. Source inspection confirmed143 and stop-invalid-handle EBADF9;
the corrected four-probe run passed. Six-probe and final eight-probe runs add the
native omission/reclaim/first-allocation coverage; all attempts remain retained.
The earlier failure is not reported as a kernel defect or passing evidence.

Final report/commands, raw supervisors/envelopes, serial/QEMU logs and source are
retained. ISO hashes are in reports; generated ISOs stay private under out/.
Source-built sys-init probe supervisors reuse the original pinned userland images
and producer kernel; this is not a new userland source build. Compiler warnings
include the compatible u8-pointer versus c_void memcmp declaration already in
prior images and cfg-unreachable fixture branches; no ABI change follows.

BG-067 next composes controlled stop with the actual command/file-reference
protocol. These isolated boundary probes do not establish graceful application
shutdown, protocol fault recovery, sustained boot or operator shutdown. Independent
review remains open. Full checks follow; sha256.json seals this bundle excluding
only itself.

Final validation passes all ten local gates in run-84vfyg_h with checked sources
unchanged. Tool executable hashes match the previously recorded identities;
final native source matches the staged build, and released locks remain fixed.
`git diff --check` passes. Eight final native probe outcomes pass; the earlier
failed oracle remains retained and no independent approval is inferred.
