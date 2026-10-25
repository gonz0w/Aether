# Stop Dash with a live script reference

2026-09-09. Two fresh native cases pass using the existing frozen AECAT004 script
configuration and sys-init paired owners. The stop supervisor links at exactly
8192 bytes, the unchanged code limit; the omission control is8032 bytes. The
existing4 KiB stack and resource/generation bounds remain. No headroom, peak stack
or performance claim is inferred from passing execution.

Dash has actually opened hello.sh through the delegated file root and received its
file reference. At its first complete32-byte file-read request (op7, selector3,
count16 and exact current reference), the owner requires one issued file record,
zero reads/offset, no second record and zero stream positions. It consumes this
request without a backend read or reply, requests native stop, then awaits actual
terminal143/kind3 and request EOF with no partial frame. Dash cannot issue another
request while waiting for that reply. This is an explicit pre-dispatch interruption
point, not cancellation of an in-flight backend effect.

After terminal observation, each retained file reference is closed through the
file service; a stale backend read must return EBADF before clearing its record.
Only after all file records are empty are the three now-unreachable stream aliases
retired. Existing stream readback verifies empty input/output/diagnostic content,
closes the backend handles and checks stale access. Shell cleanup then precedes
stream EOF/terminal17/reclaim and file EOF/terminal17/reclaim. Two generations
complete with supervisor100/reclaimed6. Controlled stop has no normal worker-exit
serial line; its exact kind/detail is asserted by the executing owner.

The omit-close control leaves the live record intact after the confirmed stop.
The existing1599 live-record check rejects with zero reclaims, before either
provider is claimed cleaned. It is a required negative result, not recovered
cleanup. The positive produces no hello output because script input was never
read or evaluated; prior ordinary script execution remains separately qualified.

Both native cases passed their first execution attempt. An initial temporary
runner-generation string replacement failed before a runner/build/native attempt;
correcting that local tooling did not change the candidate or its oracles. Exact
commands, serial/build logs, raw supervisors/envelopes and ISO hashes are retained;
ISOs remain private. Original Dash/service ELFs are reused; owner/kernel are built
from locally frozen inputs. No new Dash/libc build or broader producer-suite replay.

Three ordinary script variants and all five startup-prefix probes rebuild byte-
identically after this compile-selected addition. The original219-file source
snapshot still matches the stage except the explicit cat-roles.rs patch. Boot
helper checks dependency identity/QEMU version; builder pins native tool hashes.
Released locks remain fixed. Existing fixture/memcmp warnings remain visible.
No new unsafe boundary, source dependency, sibling change or shared rule.

SE review: use existing file records and stopped state; no cancellation journal
or new owner is needed. The simpler close-only alternative cannot prove a worker
is terminal and would risk live reference use. We choose existing request_stop,
actual terminal observation, confirmed remote close and retained error rejection.
The selected first-read boundary avoids guessing whether a backend effect happened.
O-04/I-04 preserve ownership until completion, I-05 keeps bounds and E-01–08 bind
artifact/evidence identity. No new standards exception is introduced.

This completes the bounded live-reference stop slice. It does not wire automatic
startup rollback into normal product boot, accept arbitrary partial replies or
backend failure recovery, or establish interactive shell/ENV/exec/pipes/sustained
operation. Next consolidate the normal startup failure path using the qualified
rollback obligations; preserve this exact stop boundary when shaping product code.
Full local checks and final integrity verification follow.

Final validation: all ten local gates pass in run-b631vpir with checked sources
unchanged. Both fresh native cases pass. Three ordinary script images and five
startup probes remain byte-identical; final staged/source copies and released
locks verify. git diff --check passes. No independent review or broader runtime
acceptance is inferred. sha256.json seals retained files excluding only itself.
