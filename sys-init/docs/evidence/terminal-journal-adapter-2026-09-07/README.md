# Terminal journal adapter — 2026-09-07

Decision 0161 integrates Terminal cuts with the actual lifecycle model and effect
journal. It validates bounded synthetic facts and the executed launch binding,
then maps normal exit, fault and stop without collapsing equal numeric results.
Application must retain terminal ownership, pending cleanup and exactly one real
reserved reclaim obligation. Replay returns the retained receipt without another
transition. Missing reclaim or incorrect terminal kind closes the adapter while
retaining the resulting state and captured obligations.

All 271 model tests pass, including eight Terminal adapter tests and two source
omission controls. All ten local gates pass in `run-v1m4lwsw`, with unchanged
checked inputs. All twelve native consumer sources, three release locks and
catalog bytes match the preceding checkpoint. This tests actual policy-model and
journal code with synthetic native-origin facts; it does not demonstrate native
source capture or resource disposal. No independent reviewer sign-off is claimed.

Next BG-057: Cleaned admission after the actual reclaim obligation is applied and
remaining resources are verified empty. Native provenance remains BG-058; sustained
reuse remains BG-060 and recovery BG-033. The 185-case native checkpoint and BG-056
producer source-closure limitation remain unchanged.

`source/` and `sources.json` retain checked adapter/runtime/model/test/runner inputs.
`validation/` and `checks.log` retain the complete local run. Source omission
controls deliberately collapse kind by result or omit terminal-kind verification;
both require named assertion failures. Malformed facts, stale generation, early
Terminal, busy effects and missing reclaim are covered alongside exact replay.
The facts and worker identity are injected model fixtures; no native operation or
arbitrary service executes. `sha256.json` seals this scoped evidence package.
