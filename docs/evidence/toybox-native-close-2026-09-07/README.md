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


## Final qualification and producer intake

The final27-case recipe passes:23 normal/error/re-entry outcomes complete two
generations/four reclaims; four mutants require exact owner1505/1501/1504/1501.
Prior finalizer18, usage20, error11, actual-cat7 and all213 command cases pass.
All98 host tests, Zig tests, released pins, workflow38 groups and Rust/C format
checks pass. No failed target attempt occurred: initial23-case and fresh23-case
recipes/results are retained separately; final attempt3 adds four applet-error
integration cases and is authoritative. Command run took710.1 seconds, within
the1800-second review ceiling. Separate host/format timestamps are unavailable.

Actual cat_main copies binary stdin in this candidate. Input/output close failures
produce the complete18-byte close diagnostic, or its independently observed16-byte
prefix on injected diagnostic failure. Stderr is consumed last. Unknown closes
at all three aliases and uncertain diagnostics forbid subsequent traps while
preserving local/remote distinctions. Complete known failures promote0 to1;
prior64 remains64. Re-entry during cleanup returns120 to the nested caller without
traps, latches failure and forces the outer terminal1 or preserves64. Skipping that
latch rejects1501. Replayed consumed close rejects1504 before a client terminal;
no generic panic is accepted. Independent owners check exact bytes, positions,
ordering, authority, liveness and cleanup.

The candidate rebuild removes verified extracted objects and recompiles all17
selected Toybox translation units and the adapter. Patched xwrap, real musl callback,
probe and owner are rebuilt for each case. SDK libc/CRT are pinned dependencies,
not freshly rebuilt here. Fresh upstream source hashes are recorded and verified
again in the final archive. The candidate backend equals the backend freshly
rebuilt by the full command suite. Six final receipts match frozen runtime inputs;
only the probe and opt-in cat owner close/uncertainty logic changed. Kernel, SDK,
grants/quotas, standards pins and every UL-059 bundle artifact are unchanged.
No sibling was edited or consumer approval inferred.

Candidate ELF:86,288 bytes,22 load pages,4-byte TLS. Largest owner:6,208 bytes within
the8,192-byte cap. These are artifact sizes, not peak-memory/performance results.
qualification.json, owner-artifacts.json and backend-check.json bind those checks.
final-artifacts.tar.gz retains sources/, the final recipe and six output trees;
archive-check.json and handoff-check.json verify source/recipe/upstream/member
identities. ISOs, installed boot duplicates and kernel.elf are omitted while hashes
remain in receipts. Upstream notices and previous immutable evidence are preserved.

[Candidate intake packet](handoff.json) binds the selected ELF/envelope, exact
source archive/recipe, SDK identities and prerequisite artifact hashes. It is a
runtime-source overlay on verified runner/boot scaffolding, not a standalone OS
release or automatic pin update. Reproduce with run-native.py and the exact prior
suite commands in *-timing.json. Host command:
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Unchanged isolated stdio/startup and unrelated kernel profiles were not rerun;
selected target modes cover the affected probe/owner paths. Independent clean
release builds, extended and assembled-image gates remain open.

The producer supplies the bounded CAT-06 close/re-entry candidate and selected
Toybox source rebuild for userland's independent review/intake. It does not mark
CAT-01–08 or UL-067 accepted for that owner. Arbitrary recursive xexit, signal
handling and a general installed cat remain unsupported by this fixture. Consumer
findings can require follow-up. Kernel-side planned OpenZFS worker profiling may
resume while intake proceeds; full R1 shell/runner/persistent-filesystem/package
acceptance is unchanged.
