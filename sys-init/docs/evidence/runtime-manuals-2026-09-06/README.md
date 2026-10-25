# Model, host and measurement manual evidence

Decision 0101 adds canonical mdoc sources for three existing developer commands.
All eleven selected CLI probes pass. They confirm the model's exit-2 usage
contract, host ignored-argument execution, and measurement exit-64/internal-mode
validation. Normal model and host fixtures pass. The measurement run retains all
24 repetitions (four warmups and twenty measured samples), the expected spawned
silent-child timeout and successful final result. Its complete directory is
under measurements/. These are instrumented host observations, not comparative
performance or native execution evidence.

All three manuals render at 78/60 columns and HTML. Local terminal inspection
found and fixed a long model example and measurement synopsis; final terminal
lines fit their declared widths. The validator's CLI probes ran once; final
manual-only renders were repeated after those layout edits. Initial lint already
had only the three explicit experimental-OS STYLE notices. Final lint still
exits 1 for that exact scoped notice on each manual, not zero-exit strict success.
HTML output is retained; visual and independent reader review remain pending.

All ten aggregate gates pass in out/checks/run-jq4due2q, retained in validation/.
All eighteen inventoried command sources retain their recorded hashes. This
change updates documentation and inventory dispositions only; it does not modify
CLI behavior, native sources, release pins, sibling repositories or historical
evidence. Source copies bind the reviewed commands, their local implementation
inputs and current documentation. Records identify their actual execution paths.

Seven of eighteen inventoried commands have manuals. Builder/native-runner and
standard-checker manuals, detailed configuration/API coverage, independent
review and target installation remain BG-056 work. No reviewer sign-off, target
manual lookup or publication approval is claimed.
