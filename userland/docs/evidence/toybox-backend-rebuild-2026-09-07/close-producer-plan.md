# CAT-06 scoped close policy

Pre-code contract,2026-09-07. Select a private APP_CLOSE_POLICY image with actual
cat_main, preserving old experiment modes. After actual xexit callbacks/flush,
consume input then output, attempt exactly one ASCII `cat: close failed\n` message
if either close failed, flush stderr while live, then consume stderr. Preserve
prior64; promote0 to1 on any close/diagnostic failure. Closing stderr cannot create
a fresh fallback sink. Unknown outcomes suppress all later channel traps, including
diagnostic attempts; local consumption never claims remote acknowledgment/reclaim.

Latch attempted re-entry during private cleanup: return120 to the nested call,
perform no nested effects, let the original cleanup finish and promote0 to1
(preserve64). This is the explicit bounded hook policy, not support for arbitrary
recursive Toybox xexit or signals. Existing fixed callbacks are unchanged.

Opt-in owner witnesses independently verify exact diagnostic/prefix, ordered
input/output retirement before stderr writes, terminal/liveness and two-generation
remote cleanup. Model unknown close at each alias; known input-close failure plus
diagnostic EIO/EINTR/malformed/cut/close failure. Use a separate uncertainty latch
so known failure does not masquerade as unknown. Existing profiles/flags must keep
their exact oracles. Mutants omit the diagnostic, force success, replay a consumed
close or suppress the re-entry latch and must reject1505/1501/1504/1501.

No kernel API/grant/quota, SDK, standards pin or sibling change. Same Rust1.98.0
edition2024/C clang-format21.1.8 conventions and scoped FFI/buffer lifetime apply.
Only synchronous owned buffers cross the existing transport; stdout callbacks
remain fixed, cleanup owns alias state, owner retains remote authority. Read
DEVELOPMENT/STANDARDS, Foundations O/I/E, Experience and captured consumer review
from the preceding finalizer evidence. New diagnostic is bounded plain ASCII on
stderr, no new boot marker or fallback authority. Consumer adoption remains theirs.

Select normal, three close errors, three uncertain closes, diagnostic failures,
short diagnostic, prior64/re-entry and four exact mutants. Run prior finalizer,
usage/error/cat, full213 command, host/Zig/pins/workflow/format. Freeze sources and
retain failures before edits. Update NATIVE-CAT/workflow/STATE. Fresh complete
upstream rebuild and independent consumer intake remain next; no R1 scope change.


## Fresh rebuild qualification contract

Initial23 cases pass with verified retained baseline objects. Before final
qualification, extend this recipe to remove those private extracted objects and
recompile all17 Toybox translation units and the adapter from the hash-verified
retained source/configuration. Keep SDK libc/CRT as pinned dependencies, not a
fresh SDK build claim. Record old/new object identities, exact commands and all
source files under the retained baseline tree. Rebuild patched xwrap, probe and
musl callback per case as before; all23 cases must pass again. No compiler/config,
kernel/runtime source or contract change is introduced. Initial recipe/result are
retained separately; final qualification uses the source-rebuilt recipe.


Candidate integration selection, before final qualification: also run actual
cat read/write EIO and malformed-read/cut-write outcomes with APP_CLOSE_POLICY.
Reuse the existing independently checked applet-error owner settings for those
four cases (no close-error injection or finalizer-only32-byte accounting). This
checks that the new cleanup policy composes with upstream error/poison paths,
without imposing close-diagnostic ordering on the applet's earlier diagnostics.
No runtime source change; source-rebuilt final recipe now selects27 cases.
The earlier23-case source-rebuilt recipe/result are retained separately.
