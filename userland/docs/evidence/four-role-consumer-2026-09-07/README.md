# M3 / UL-059 independent four-role parent preparation

The producer SDK matches all231 files in the existing tested userland SDK pin.
The concrete transport difference is now implemented in a separate opt-in parent:
AERIO001 has four roles instead of the legacy pair. Existing native-io/runner/child
sources and default consumer pins remain unchanged.

The independent decoder validates the entire160-byte frame before publishing
refs: exact generation,ordered roles,rights,capacity and reserved fields.648 host
cases pass with UBSan,covering both generations,every byte mutation,all shorter
lengths and invalid generation/oversize controls. Rejected mutations/truncations
leave the destination unchanged. [Controls](final/host-controls.stdout).

The new adapter retains the existing bounded transfer/poison/file logic with four
slots and maps inherited child refs to slots2/3. The new runner uses the real
startup selector and result decoder,launches from copied arguments,closes parent
input,collects once and checks ECHILD,observes shared-output EOF,closes all remaining
roles and maps actual terminal kind/status. It handles the successful-child path;
help/version/local-denial frontend integration is not included in this slice.

[Final build](final/summary.json) links a static native parent ELF with no external
undefined symbols. Compiler warnings are errors. This is compilation/linking only:
**native execution NOT RUN**. No native command,cleanup/reclaim or M3 acceptance
follows from decoder tests. [Header inspection](final/headers.stdout).

[First attempt](attempt-1/summary.json) passed host tests but failed target compile
because the new driver omitted _POSIX_C_SOURCE=200809L needed for SSIZE_MAX.
The driver now uses the existing native profile's define; all tests/build rerun.
Both attempts and exact sources are retained. [Plan](FOUR-ROLE-PLAN.md),
[producer identities](producer-inputs.json), [format](format.log), [quality](quality.log).

Next: source-rebuild the matched owner/backend and existing bytecount child in the
private producer snapshot,insert this parent under logical-startup successful-child
selection,boot and verify independent output,terminal status and six reclaims.
Then exercise wrong-role/omitted-close rejection and relevant existing regressions.
No live producer edit or broader ABI ownership assumption is authorized by this
preparation. Unknown outcomes remain failed/incomplete,not claimed recovered.
