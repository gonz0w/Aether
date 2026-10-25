# Offline standards manual evidence

Decision 0102 adds source manuals for the three offline standards wrappers.
Twelve normal/ignored-help/ignored-version/ignored-argument probes pass with
identical output per wrapper. Three isolated unchanged-wrapper copies with no
lock/release produce the expected exit 1 and stderr-only failure; Experience
uses a traceback while Foundations/Distribution print short messages. These
controls do not modify original locks, wrappers or vendored release files.
checks.json records all fifteen probes and manual-render commands.

The initial render had only explicit experimental-OS style notices. A later
source-accuracy edit introduced a sentence-layout warning; it was retained in
intermediate-lint-warning.log and corrected. Final lint exits 1 only for each
exact explicit-OS STYLE notice under the existing decision-0099 disposition.
All three manuals render at 78/60 columns without overflow and as HTML. Terminal
text was inspected locally. HTML visual and independent reader review remain
pending; this is not a zero-exit strict-lint or target-lookup claim.

All ten aggregate gates pass in out/checks/run-wu69zxpk, retained in validation/.
inputs-unchanged.json verifies all wrapper, lock and vendored file hashes before
and after the probes. Reference checks used an environment without
PYTHONOPTIMIZE and with PYTHONDONTWRITEBYTECODE=1. No optimized-check acceptance
or complete malicious-input review is claimed. The extracted source copies
bind exact local review inputs without duplicating or altering released bytes.

The validator captures the normal/ignored-argument/render probes. Missing-lock
controls were added separately and are retained with their unchanged scripts,
commands and stdout/stderr. Final renders were repeated after prose wrapping.

Ten of eighteen developer commands now have manuals. BG-056 prioritizes
Experience lock/symlink/pre-execution inventory validation and explicit
assertion-enabled child execution for Experience/Distribution. The manuals
record those gaps; runtime/wrapper behavior is unchanged. Independent review,
remaining eight command manuals and target lookup remain open. No shared pin,
sibling repository or historical evidence was modified.
