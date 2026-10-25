# Dash scratch fork adapter boundary — 2026-09-15

The opt-in FORK_SHELL_FILES C path receives its scratch grant before dash starts,
validates live extra bindings during fork preparation, then consumes a separate
AESFC001 file receipt after the unchanged three-stream receipt. Counts, rights,
reference generation/sequence/slot and parent scope are checked. The entire child
record validates before either file reference changes; flags and counts remain
copied, and unused bindings receive zero references. The child root binds to its
actual generation and the original owner. Rejection poisons transport before the
existing failed-stage exit, preventing cleanup with unvalidated copied handles.
The owner still must enforce authority and issue that receipt after admission.

## Evidence

`focus.json` records the host witness and two compiled controls. Cases include
FD9/11/15 placement, aliases, different parent/child generations, stale/foreign
references, malformed second references, modes/counts/bounds, atomic rejection,
closed metadata and flags retained through copy. Omitting count validation or
retaining parent references must fail an assertion with exit90. This is C state
validation coverage, not native fork execution or independent authority proof.

`native-compile.json` compiles the actual fork-client.c against the existing native
musl SDK with FORK_SHELL_FILES and the unchanged fd-leak-control script. The script
is captured and its SHA256 matches the consumer intake pin. This is object
compilation, not linking or executing dash. The initial compile record and source
before the rejection-guard addition are retained separately; the final object is
in the binary archive. A long inline comment failed formatting, was wrapped by
the pinned formatter, and the final code was recompiled and format-checked.

`host.log` and `host-final.log` pass104 Python tests and the required Zig/offline
checks. `checks.json` records formatting, workflow and simplicity verification.
`compatibility.json` compares all69 existing public-fork C selections against the
last qualified source archive; preprocessed code matches exactly after normalizing
root paths and removing only blank lines. The final source is rechecked against
those hashes after the opt-in guard change. The initial strict comparison failed
on one blank line in FORK_SHELL_NULL; both raw outputs and its failure note remain.
No existing native profile selects the new mode, and no QEMU result is claimed.

Run the existing `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global`; focused compile commands are in focus.json. Scoped source and
binary inventories pair with verified archives. Only verified duplicate binaries
and extracted copies of the prior sealed source were removed. SHA256SUMS seals
this packet; previous evidence and released pins are unchanged.

## Next boundary

Implement matching owner-side dispatch/admission/holder handling and replacement
helper restoration, then run the unchanged leak-control through actual dash
fork/exec/wait. Successful helper95 and parent22 with empty output must reflect a
real surviving FD9 and removed FD10; parent22 alone is insufficient. Follow with
unchanged redirection, full connections and matching runner before SDK/consumer
handoff. Poisoned-close recovery, persistence and R1 assembly remain open. No
sibling, public SDK, kernel operation or quota change is made here.
