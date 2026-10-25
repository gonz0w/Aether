# Native composition size study — 2026-09-06

Decision 0080 identifies a build-feasible retained-sampling candidate: all 120
compiler configurations fit, with a 4048-byte maximum (48-byte margin). The candidate
uses optimization s, recorded inlining choices and normalized diagnostic paths;
all twelve paired-path images match. Nine candidate host tests and two omission
controls pass. This is build/host evidence only; the current runtime is unchanged.
Next: explicit profile/default compatibility decision and a fresh 127-case native
witness before adoption. Seeded admission, full launch composition, malformed native
injections, NT-05–07, journal retirement and recovery remain open.

See `docs/research/NATIVE-COMPOSITION-SIZE.md` for comparisons and acceptance limits.
Attempt 1 is a linker-loader failure, not size evidence. Attempts 2–5 compare frozen
revisions and explicit inlining changes at levels 2/s/z. Attempts 6–7 compare two
normalized paths. Attempt 8 builds the complete assembled candidate and runs its
pure host validator tests/controls. No actual candidate target execution occurred.
`candidate.patch` is review material only; it was not applied to the runtime.

Validation: all nine development gates passed in `out/checks/run-k0yx267y`;
results and fresh host sample-receipt artifacts are retained in the study evidence
under `validation/`. The ten current native inputs and worker/builder hashes still
match decision 0079. No candidate target execution or runtime adoption is claimed.
