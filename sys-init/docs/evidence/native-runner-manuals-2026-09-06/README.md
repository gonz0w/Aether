# Native-runner manuals and isolated builder capture

Decision 0105 completes source-manual coverage for the eighteen inventoried
developer entry points, with four native-runner manuals. Twelve CLI probes pass;
they do not launch a guest. All four manuals render at 78/60 columns without
overflow and as HTML. Local terminal inspection was performed; independent/HTML
visual review and target lookup remain pending. Lint retains only the exact
experimental-OS STYLE notice under decision 0099, not zero-exit strict success.

Source review found a real copied-dependency regression: the I/O runner copied
the supervisor builder but omitted bounded_tools.py. The production capture
function now copies the helper, which the existing source inventory fingerprints.
Its regression invokes help in a private copy with no checkout PYTHONPATH and
then removes the helper to demonstrate failure. Six I/O harness tests pass,
including this paired control and the existing input/profile checks.

A fresh io-stop build through that captured builder passes and exactly matches
the retained decision-0098 raw/envelope hashes. The copied sources, logs, tool
receipt and generated artifacts are retained in captured-client/ and
captured-build/. This changes host capture, not native code, compiler options or
semantic markers. No fresh native guest run is claimed or required to establish
this import/copy fix; prior target evidence remains scoped to its frozen inputs.

All ten aggregate gates pass in out/checks/run-xfa9ytax, retained in validation/.
checks.json records commands and render-tool identity; source/ binds current
manuals, inventory, runner and regression. All eighteen command source hashes
match the updated documentation inventory. No release pins, vendor files, sibling
repositories or historical evidence were edited.

Configuration/API detail, legacy subprocess bounds, independent review and
manual installation/lookup remain open. Manual existence alone is not publication
conformance or a claim of production POSIX init.
