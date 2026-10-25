# Sys-init filesystem owner preparation — 2026-10-20

BG-067 / decision0190. This packet retains the new original sys-init ABI29 owner,
its exact native ELF/raw, source/tool/build records and actual host qualification.
**No guest was executed; native ABI/lifecycle acceptance remains pending.**

Final owner:2072 immutable code bytes, one RX page, no writable statics; matched
ELF9080 bytes. Aether's strict read-only intake passes at1096/4088 inspected stack
bytes across nine reachable functions. No indirect calls or inspector relaxation.
This scoped compiled-code bound is not formal whole-stack/interrupt proof.
[Inspection and commands](preparation.json) retain both exact hashes and actual
compiler/Clippy/rustfmt/LLVM identities. [Candidate inputs](candidate-inputs.json)
pin the30-member engine delivery and producer's selected small process image;
the engine-only delivery is not a complete native boot bundle.

Four test functions execute the actual policy. They cover35 injected failure
scenarios, all six bootstrap fields, successful ordered mock teardown, short and
EAGAIN transfer offsets,100000-call frame/million-poll bounds and returned halt.
Three compiling omissions fail at their intended assertions: early readiness,
clean terminal kind/status and reply generation. Default Clippy (policy/tests)
with warnings denied and rustfmt pass. Host doubles are not native holder,
block/grant or trap-wrapper tests. A mock reaching halt is an ordering witness;
the policy rejects any returned halt, including a returned zero.

The candidate admits the exact filesystem, waits for live readiness and an AF06
root, admits one small process at slot1, settles it, then disconnects and settles
the engine before halt. It does not modify files, run the fixed mutation transcript,
adapt full shell roles/PIDs, or implement a filesystem-backed runner. Engine exit0
is the pinned owner's aggregate phase claim; quiescence, recovery and persistence
need native evidence independently.

Earlier attempts remain under `prior-attempts/`. The first weakened readiness
guard escaped the older test because the later recheck still rejected it; tests
now require no greeting IO after bad initial readiness. An initial inspection
failed with Rust's library directory passed to LLVM; a clean environment advanced
to the real rejection of two static/GOT memory-helper calls. Scalar bootstrap
checks and immutable argv removed those calls and reduced stack. The first strict
Clippy run identified the test's manual multiple-of expression; it was corrected
without suppressions. Initial linked artifacts/source/logs remain separate.

Next: an independently reviewed matched AENFS003 native assembly/oracle for this
read-only sys-init workload and failed-exit/authority/cleanup controls. The current
producer runner builds its conformance owner and expects a mutation transcript;
neither its raw swap nor its existing pass can qualify this owner. The local
[delivery guide](../../../prototypes/native-filesystem/README.md) is ready, unsent.
Sibling files, default recipes, old locks and released standards are unchanged.
No complete implementation, independent sign-off, uptime, Zsh ISO or R1 claim.

Final source review corrected terminal interpretation before any guest: rax is
exit_status+1, rdx is retained readiness, r8 is kind. Normal engine exit0 may retain
ready1. The earlier host model and linked bytes remain under
`prior-terminal-interpretation/`; they are not the final candidate. The first full
check stopped at static boundary coverage; the new wrapper's exact sites and
source review are now recorded in the existing boundary inventory.

Final validation: all ten `python3 scripts/check-all.py` gates pass with unchanged
checked sources; [compact record](local-checks.json) pins the retained full report.
Six focused static-record tests pass. The count fixture now reflects17 reviewed
files; its first count failure and a temporary indentation error are retained in
`prior-local-checks/`. All nine ABI24 maintained source pins still match, final
Rust tools/source bytes recheck, new local links resolve and diff whitespace passes.
