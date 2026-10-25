# Scoped technical review

Current-task review traced actual Toybox main/mask/fflush/terminal calls through
one session state. The separate stderr observer is explicitly fixture authority,
not a target grant. Diagnostic finalization bypasses the public post-finish guard
only via the private vector path while retaining shared poison checks. Lost ACK
commits two bytes then blocks later transport. Known/unknown close injection closes
real Linux descriptors before reporting failure, without claiming native reclaim.
The original control relink remains byte-identical. Normal finalization checks
mask restoration/flush and rejects a late public write. The compiled wrong-mask
variant triggers exact terminal guard124 after real Toybox startup/copy.

Eight cases, one compiled mutant, wrong-status/trace controls, CLI/grammar and
quality gate pass; static ELF properties verified. Initial socket restriction and
earlier passing run are retained. Unchanged component sources/manifests verify
host UBSan reuse; no Linux sanitizer, native implementation or owner acceptance is
claimed. Same-task technical review only; independent review remains pending.
