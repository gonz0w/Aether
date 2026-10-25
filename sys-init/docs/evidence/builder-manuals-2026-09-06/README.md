# Builder manual evidence

Decision 0104 adds canonical source manuals for all four standalone builders.
Twelve help/version/missing-operand probes and four fresh default builds pass.
The service and I/O worker builders use the previously reconstructed offline I/O
SDK and reviewed tools/receipt, with exact commands retained in checks.json.
Builder-generated inputs/ and tool logs preserve the captured C inputs.

Fresh lifecycle/supervisor raw and envelope bytes match decision 0098. The I/O
worker ELF and envelope match decision 0097. The service worker passes its
existing structural checks; no new native execution or full variant compatibility
is claimed. The two legacy builders and shared helper match the decision-0098
source copies; the I/O builder matches the decision-0097 captured source. All
eighteen current command hashes also match the documentation inventory. These
identities justify retaining earlier variant evidence for unchanged code.

All four manuals render at 78/60 columns and HTML. Initial lint contains only
the explicit experimental-OS STYLE notices, retained under decision 0099's
scoped disposition. Long initial synopses/examples were adjusted; final terminal
output fits its declared widths and was inspected locally. HTML visual and
independent reader review remain pending. Lint is not claimed as zero-exit strict
success: each final lint exits 1 with exactly the one recorded STYLE notice.

All ten aggregate gates pass in out/checks/run-h4b3tn59, retained in validation/.
No builder/runtime implementation, native source, shared release pin, sibling
repository or historical evidence changed. Builds produce inert artifacts and
are not a target-runtime witness or publication authorization.

Fourteen of eighteen developer commands have manuals. The four native-runner
manuals, detailed configuration/API coverage, standalone tool bounds and actual
independent/target review remain BG-056 work.
