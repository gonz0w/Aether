# Aggregate startup and output pipes — 2026-09-07

Decision 0145 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_startup_pipes.py'` passes four tests. Real startup file conflict
preserves the file and returns a plain failure. Mocked startup interruption returns
130. Real stdout/stderr pipe closures use stdin handshakes, private stub gates,
five-second waits and child cleanup; saved success plus delivery failure is
separate from progress failure stopping later gates. Unavailable diagnostics have
a best-effort control. All attempts passed; no native code executes in fixtures.

All ten `python3 scripts/check-all.py` gates pass in run-axrwya5u with sources
unchanged. Exact commands/hashes are in validation/results.json. Four mandoc lint/
ASCII 78/ASCII 60/HTML commands pass. Independent reader/HTML visual/narrow-layout
review remains pending.

Native audit stdout equals decision 0144; catalog, 24 native inputs and release
locks match baseline. Output startup failures invent no report. Summary flush
failure returns nonzero without rewriting the completed check result; progress
failure records its stage and stops further gates. Failed descriptors are silenced
where possible to prevent shutdown flush noise. Fatal/repeated signals, blocked
I/O, redirection failure and crash durability remain limits; output-root resolution
policy and argparse help/usage behavior are unchanged.

No native/sibling/release-pin/historical-evidence changes; RC1 remains unpublished.
Source copies/diff identify this slice. Planning/decision validation notes and
evidence followed checks; tested Python/inventory bytes stayed fixed. Next is a
BG-054 extended-test plan, not an invented hosted runner or scheduling claim.
