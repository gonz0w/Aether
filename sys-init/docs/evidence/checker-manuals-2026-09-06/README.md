# Offline checker manual evidence

Decision 0100 adds canonical source manuals for static checks, quality records
and native evidence. All 12 CLI probes pass: help, version, invalid usage and
normal execution for each command. checks.json records commands, exits, tool
identity and source hashes; adjacent files retain both output streams.

All three manuals render as ASCII at 78 and 60 columns and as HTML. Terminal
text was inspected locally; the initially long synopsis was split into separate
invocations so commands remain copyable at the narrow width. HTML output is
retained; independent technical/reader and HTML visual review remain pending.
Initial sentence/line-length warnings are retained in initial-lint.log and fixed.
Each final lint invocation exits 1 with only the exact explicit-OS STYLE notice
recorded under decision 0099; this is not zero-exit strict-lint success. The
validator checks the exact notice and rejects other diagnostics.

All ten aggregate checks pass in out/checks/run-r5bdp085, retained in validation/.
Existing failure-path harness tests still pass. No runtime or checker source
changed; inventory identities were verified against all 18 entry points. Native
execution was not run or needed for these documentation changes. Release pins,
historical bundles and sibling repositories are unchanged.

Four of eighteen inventoried developer commands now have source manuals. The
remaining commands, field/API documentation, independent review, complete tool
closure and target installation/lookup remain BG-056 work. No reviewer sign-off
or publication authorization is inferred.
