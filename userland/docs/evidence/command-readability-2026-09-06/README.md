# Command-runner Python readability evidence

UL-063 CSR-03, 2026-09-06. Three drivers have explicit main entry points,
expanded statements/argument lists and separate native expectation helpers.
The client builder names its runner/channel inputs. Imports no longer parse
CLI arguments or begin builds. Existing command bytes, flags, pins, environment,
process cleanup and receipt contracts are preserved.

Source review compares normalized execution ASTs and all eighteen native failure
context/terminal expectations. Host/client/native command sequences and exits
match prior C17 evidence after replacing private output roots. All 21 host/control
cases, seven process controls and nine native cases pass. Five client ELF hashes
are unchanged. Before/after sources, one-off transformation/review scripts and
raw logs are retained. No formatter dependency was added. The CP 79-column target
is not a strict lint gate here: several long hash/path/generated-code and existing
expressions remain; no full PEP 8 conformance claim follows.

Large native images stay in build/native-command-userland-_odv099m with exact
receipt hashes. No failed test attempt occurred in this slice. The source grammar
is checked for Python 3.10; actual execution used the recorded host interpreter.
No other supported interpreter, public CLI or additional native boundary coverage
is claimed. Independent technical/reader reviews remain pending. CSR-04/05 are
tracked through UL-058/059; UL-063 remains active for review and wider migration.
