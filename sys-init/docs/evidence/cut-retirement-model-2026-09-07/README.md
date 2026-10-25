# Cut retirement model — 2026-09-07

Decision 0158 adds pure resource-disposition and retirement qualification. A single
Retirement owner requires the exact Applied Cleaned receipt, prior lifecycle phases,
source-bound empty inventory, applied reclaim and no unresolved obligation. Both
members pass preflight before either is marked. Exact replay makes no new marks.
Partial callback failure closes the owner and preserves started/retired progress,
both observations, receipts and any returned diagnostic without resetting history.

All 246 model tests pass, including eight retirement tests with three embedded
source omission controls. The controls detect premature retirement, ignored live
inventory and history reset. A reserved-but-unapplied Cleaned cut explicitly denies.
All ten local gates pass in `run-ngufsiwl` with unchanged checked inputs. All twelve
native consumer sources, three release locks and catalog bytes remain unchanged;
the 185-case native witness remains the runtime checkpoint. This is synthetic
model evidence, not native cleanup, resource authority or a new target run.

Next BG-059: NC-06 terminal-application pending disposition and mixed-phase cut
retirement, still retaining exact receipts/history. BG-057 owns actual journal/
lifecycle/native integration; BG-060 sustained reuse and BG-033 recovery remain
open. No sampling reset, replacement, sustained reuse or recovery API is added.

source/ and sources.json retain the final model, fixture, runner and contract.
validation/ is the final full-check snapshot. The prior passing run and test source
are retained separately: review added an explicit reserved-but-unapplied receipt
case before final acceptance. The three source omission controls run modified
modules and require their exact named assertion failures; no kernel call is made.
The model permits only cuts whose members are all Cleaned at this entry point.
It adds two fixed logical slots each for disposition, observation and returned
result; no native memory or power-loss claim follows. The historical producer
source-closure limitation under BG-056 is unchanged; no catalog entry is added.
