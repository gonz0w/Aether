# BG-067 bounded command producer handoff

Before implementation: qualify a matched current-kernel reference using the real
userland four-role runner and bytecount. Freeze imported original sources with
BSD notices. Sys-init replaces the reference supervisor after adapting its native
boundary; it does not acquire authority by swapping its existing ABI16 binary.
This packet is producer evidence, not independent sys-init ownership acceptance.

Use unchanged AENMX001/ABI9, three worker slots, six channels, 8 KiB supervisor
code and separate 4 KiB stack. Preserve existing profiles, pins and kernel code.
Reference owner keeps file/command routing policy; the consuming adapter must
separate lifecycle ownership from that protocol logic within the selected owner.
No extra kernel service, new PID authority or ready-writer substitution.

Build all runner/command objects from pinned imported sources against the strict
SDK. Cases: real abcdef -> 6 newline, empty -> 0 newline, rejected malformed
runner startup without child admission, child #UD before bytecount with preserved
input and empty output, and omitted stdout close retaining failed cleanup.
Positive/empty/fault cases require two generations, exact terminal kinds and six
reclaims. Negative cases require exact terminal/owner rejection; zero reclamation
is retained failure, never recovery. Select fresh host checks and these native
cases; no full-shell or sustained/shutdown acceptance. Sources freeze during runs.

Simplicity: reuse the current broker and grants with two scoped fixture oracle
variants for empty/fault input. No temporary shell or extra image slot. Consumer
adapter work and independent acceptance remain with sys-init; no sibling writes.

## Results and remaining consumer work

See [the exact contract](../../NATIVE-INIT-COMMAND.md). All five native cases pass
in `native-results.json`: positive and empty produce `6\n` and `0\n`; a child
#UD retains kind 2/detail 134 and runner exit 1, with preserved input and no output.
Each completes two generations and six reclaims. Wrong-role startup and omitted
stdout close reject with owner 1401 and 1403 respectively; these retained failures
do not demonstrate recovered cleanup. Native logs and images are in artifacts.tar.gz.

The reference owner uses 7,808/8,192 code bytes (empty 7,784; fault 7,824), with a
separate 4 KiB stack. Sys-init must measure its actual composed owner/stack, adapt
role and endpoint ownership, and handle backend request EOF before terminal
observation. Its existing ABI16 readiness adapter is not this ABI9 protocol.
No capacity expansion or complete consumer unblock is claimed. The consumer must
independently qualify its policy and partial-launch cleanup. Sustained boot,
shutdown, full dash, persistent filesystem and package release remain open.

Sixteen existing `runner_success` variants rebuild byte-for-byte unchanged; see
compatibility.json. This is compatibility evidence, not a fresh full 241-case
run. Fresh `zig build test` passes, including 98 Python tests and pinned standards.
The only runtime-source delta for this task is two opt-in success-owner fixture
oracles. Kernel, ABI, quotas and release pins remain unchanged.

## Retained attempts and reproduction

The first empty case used the older backend's `empty_input` flag and failed owner
1405. `run-attempt-1.py`, native-attempt-1.log and attempt-1-results.json retain it.
The corrected recipe uses the existing stream backend `cat_roles`/`cat_empty`
selection; no backend implementation changed. The initial host run rejected an
inventory entry outside its NATIVE reference/scripts scope. host-attempt-1.log
retains this; the reference was named NATIVE-INIT-COMMAND and the recipe is
recorded as test group AT-INIT-COMMAND instead of changing the inventory checker.

Run `run.py --help` for the SDK/tool-lock inputs, using the invocation in the
contract. Imported C/header files came from Aether-userland's
`experiments/command-runner` and `experiments/native-channel`; inputs/manifest.json
pins the exact copied bytes with their notices. The recipe does not read mutable
sibling sources. Each command, environment override, source digest and case
artifact digest is retained in the result. SDK receipt, libc and locked tool
binary identities are checked; the referenced SDK archive supplies frozen inputs.

`collect.py` captures and verifies source/artifact archives and the prior packet.
manifest.json seals this packet. No sibling repository was modified. Reader review
and sys-init owner acceptance remain external gates.
