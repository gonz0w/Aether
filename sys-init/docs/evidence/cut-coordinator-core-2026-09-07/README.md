# Pure cut coordinator core — 2026-09-07

Decision 0157 implements the pure cut-coordinator core: exact immutable synthetic
source/cut identity, six retained records, one active reservation, ordered phases,
pre-application revalidation, explicit callback reentry denial and exact receipt
replay. Uncaptured application closes with Unknown and retains any returned result;
cancellation consumes its serial/record without resurrecting the cut.

All 238 model tests pass, including ten coordinator tests with three embedded
source omission controls. All ten local gates pass in `run-94phzf3m` with unchanged
checked inputs. The controls detect foreign-cut admission, false captured success
and a second actual synthetic adapter application. All twelve native consumer
sources, release locks and catalog bytes remain unchanged. No fresh native
execution is claimed: the 185-case decision 0155 witness remains current, including
its separately tracked BG-056 producer source-closure limitation.

Next BG-059: define and qualify the synthetic resource-disposition/retirement
boundary, including nonempty/partial inventory, stale retirement receipts, premature
retirement, reset omission and post-commit bookkeeping failure. BG-057 retains
real journal/lifecycle and native integration; BG-060 sustained reuse and BG-033
unknown recovery remain open. No resource cleanup, native origin, retirement or
history-reset API is implemented by this pure model slice.

source/ and sources.json retain final model/test/runner inputs. validation/ is the
final full-check snapshot. The initial passing 237-test run and its three changed
source files are retained under validation-before-reentry/ and
source-before-reentry/: review then added the explicit callback guard and its
regression. These are distinct checkpoints, not failed semantic controls disguised
as successful runtime behavior. Model controls execute modified source in isolated
Python modules and require their named assertion failures; they perform no native
calls. The final model runner includes the new source in its own digest inventory.
