# CLI dispatch contract test

2026-09-07 UTC. New test only; package runtime and release pins unchanged.
Independent table covers all 13 public commands. Controlled helpers expose their
basename and argv as NUL-separated data, return raw multibyte/control-containing
TSV output and diagnostics, and supply statuses 0, 2 and 73. All 39 combinations
must preserve helper identity, argument boundaries/order, streams and status.
Twenty-two missing/extra-argument cases must return exact usage status 64 and its
existing diagnostic before any helper invocation. Every case must clean scratch.

Forbidden outcomes: wrong dispatch, argument splitting/reordering, stream/status
rewriting, helper calls on invalid arity and leaked CLI temporaries. Five-second
child deadlines and the full suite's owned-group 600-second watchdog bound execution.
Controlled helpers do not establish actual package authority or populated-state
semantics. No new CLI output or accepted command behavior is introduced.

Selected checks: focused dispatch, development inventory, changed-shell lint,
coverage controls, all standards pins and fresh full sh tests/check.sh. Retain exact
dirty input identities and every run result. No native or release approval claim.

Full suite passed in 209.2 seconds under the 600-second watchdog.
Dispatch and full-suite completion markers appear exactly once. All executable and
fixture input names, sizes, hashes and modes remained identical to inputs.json.

Three disposable CLI mutants were rejected: the first binary helper selection
changed to state; helper command/root arguments swapped; and the TSV exit changed
to zero. mutation-controls.json records mutant hashes and failed assertions. The
checked-in CLI was never modified. This demonstrates sensitivity to these specific
defects; it is not a complete mutation campaign or actual package-engine witness.
