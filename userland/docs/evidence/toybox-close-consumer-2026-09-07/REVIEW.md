# CAT-06 close-policy consumer review

Scope: APP_CLOSE_POLICY under the bounded stdin-only Toybox profile. The completed
producer handoff is captured in a new snapshot. Original source pins, native
profiles and receipts remain unchanged. Foundations O/I/E and CP/C/TD/TE apply.
No kernel/grant/quota/shared-interface change is made locally.

The producer's18-byte `cat: close failed\n` is explicitly selected for this candidate,
superseding the earlier unimplemented local `cat: close: I/O error\n` proposal.
This is a diagnostic choice, not a relaxed outcome: one message after input/output
retirement, while stderr remains usable; exact bytes/prefix and terminal state
must match the original owner oracle. No fallback authority after stderr close.

Codex reviewed the captured C/Rust diff: the input/output loop consumes each alias
once, attempts public stdio diagnostics on failure, flushes and then consumes2.
After uncertainty, stdio attempts reach the shared poisoned transport without
another trap; local close consumption still occurs. A complete EIO response is
kept distinct from unknown completion. Owner uncertainty is latched separately
from an earlier known failure, preserving allowed diagnostic traffic until an
actual uncertain response. Status0 promotes1; prior64 is preserved.

The private hook sets its entry state before cleanup effects. A nested call latches
failure and returns120 without effects; outer cleanup consumes remaining aliases
and cannot return0. The ignore-latch mutant must reject. This is synchronous
private-hook behavior only; recursive Toybox xexit/signals are not qualified.

The native plan includes27 cases with real cat_main, applet error composition,
all three uncertain-close positions, diagnostic EIO/EINTR/malformed/cut/close
failure, short output, prior64, repeat-entry and four semantic mutants. Existing
source-built baseline logic in the producer recipe is preserved without a duplicate
local rebuild. SDK libc/CRT and backend remain pinned dependencies. Each selected
owner is rebuilt. Final outcomes are recorded after execution, not inferred from
producer evidence. Independent reader/maintainer sign-off remains pending.
