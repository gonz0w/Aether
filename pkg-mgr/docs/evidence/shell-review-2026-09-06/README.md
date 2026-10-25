# Whole-shell lint review — 2026-09-06

All 38 active shell files pass ShellCheck 0.11.0 with --norc --shell=sh.
The normal fixture entry now invokes --lint-all, so a missing/version-mismatched tool
or new diagnostic is a required-gate failure. Python remains development-only.

Changes make empty CDPATH assignments explicit; rewrite conjunction guards as fatal
conditional branches without changing predicates or diagnostics; quote string labels;
use validated make-exported environment variables directly instead of aliases; mark
an unused blob-row size binding; and preserve literal shell text in test arguments.
Before copies of the touched shell implementation/fixtures are retained here.

Three local exceptions are recorded in DEVELOPMENT.md: two callbacks used by traps
(SC2329) and four od decimal bytes intentionally split into positional arguments
(SC2086). They preserve the tested behavior; no known defect or file-wide baseline is
waived. Existing CLI interruption/output, package/state/path and boot-v2 malformed
controls are the relevant behavioral witnesses. The full suite remains required.

Three private tool-adapter controls confirm that --lint-all fails for missing
ShellCheck, a wrong version and an explicit reported finding. Their stdout/stderr
and return statuses are retained in lint-gate-controls.json. These adapters are
never installed in product paths. A real bytecount build/register/export/import
run additionally exercises the phase environment changes with a host compiler.

All sixteen active fixtures, three standards checks and whole-shell lint pass.
Bytecount also passes source tamper rejection, parallel build/register, export/import
and staged/imported output controls. Frozen source/test digests match after both
runs. This closes the initial lint migration with three documented narrow exceptions;
HR-02's broader security review and other release gates are not certified by lint.
