# Dash startup rollback capacity handoff — BG-067

Status: local handoff prepared; no producer change or acceptance claimed.

The current AENMX001/ABI9 three-role script profile admits8,192-byte supervisor
code and a separate4,096-byte stack. The validated ordinary script uses8,176 bytes;
its live-file stop selection uses8,192. Integrating confirmed startup-failure
rollback into ordinary startup measures9,152 bytes and fails the enforcing linker.
Nine [small layout alternatives](evidence/dash-script-size-review-2026-09-09/README.md)
save no space (constant-slot specialization grows to10,528). The maintained code
remains at the validated stop checkpoint.

The simpler route is a producer-defined bounded capacity option for this existing
three-role composition. Aether owns the mechanism, encoding, compatibility and
budget decision; sys-init owns rollback and its acceptance. No new magic, ABI,
size or stack allowance is selected here. At least9,152 code bytes are needed by
this measured normal candidate; that is a lower bound, not a final profile request
or proof that every control/stop variant fits. The previous AENIN003/ABI16 capacity
work applies to a different envelope and is not interchangeable.

## Required producer handoff

Provide an explicit opt-in profile, frozen source/artifact manifests, build commands
and tool identities. Define code admission and mapping bounds, entry/alignment,
RX permissions and separate RW/NX stack/guard behavior. Preserve current AENMX001
admission and its rejection of oversized images unless a versioned compatibility
change is explicitly agreed. Existing launch arguments, three image/worker roles,
six channels, transfer ownership, terminal observation and reclaim semantics must
remain specified; capacity must not silently expand runtime authority or quotas.

Qualify exact-boundary/over-limit and malformed admission, executable-code mapping
and stack isolation with native witnesses, plus retained current-profile regressions.
A bigger linker assertion alone is insufficient: the frozen native_launch.bundle
also rejects supervisor sizes above8,192. Shared release pins remain unchanged.

## Sys-init acceptance after intake

Verify the complete packet before consuming it; build from local frozen inputs.
Measure all selected candidates under the new enforcing linker and separately
validate the stack. Run ordinary script, missing-root and missing-close cases;
real file/stream/shell startup failures; endpoint and stream-file cleanup omission
controls; and live-file stop/close omission. Require the existing exact output,
terminal, resource and reclaim oracles. Confirm unknown startup outcomes perform
no rollback/retry, using appropriate fault evidence before extending that claim.
Retain all failures and compatibility results, then run all local checks.

This handoff concerns startup rollback in one bounded script composition. It does
not request a service-manager framework, general shell support, sustained runtime,
new scheduling machinery or a release. Sustained wait/reuse/shutdown remains in
SUSTAINED-INIT-HANDOFF.md. No sibling changes are authorized by this document.

## ABI17 consumption — 2026-09-11

Capacity is resolved for the bounded startup integration: ten native script cases
and four compatibility/admission cases pass. Normal rollback is9,152 bytes and
the largest selected stop image9,264 within the explicit16,384-byte profile, with
the unchanged4,096-byte stack. See `docs/evidence/dash-startup-abi17-2026-09-11/README.md`.
The opt-in script-abi17.patch requires bootstrap17; old ABI9 inputs remain available.
Actual launch EINVAL rollback is qualified; additional startup-error coverage and
sustained wait/reuse/shutdown remain separate. Released pins and siblings unchanged.
