# Pending disposition and mixed cuts — 2026-09-07

Decision 0159 qualifies exact-member pending release and mixed-cut retirement in
the pure model. Applied Terminal receipt and actual synthetic pending/source identity
must match; success requires both a matching return and an empty position. Replay
does not release another member's position. Uncertain release retains started state,
source, returned diagnostic and Applied receipt while closing without retry.

Mixed cuts retire only Cleaned members, after confirmed earlier Terminal pending
release and resource preflight. Other members and their pending position/history
remain untouched, including when marking fails. All 254 model tests pass, including
eight pending/mixed-cut tests. Four core, three retirement and two pending source
omission controls pass their expected assertion-failure oracles. All ten local
gates pass in `run-v7stuqiq` with unchanged checked inputs. Native consumer sources,
release locks and catalog bytes remain unchanged; no new target run is claimed.

BG-059's pure synthetic qualification is complete; this is not full native NC
conformance. Next BG-057: integrate the actual lifecycle/journal adapter with exact
source qualification, whole-cut effect capture and cleanup/admission gates, then
obtain fresh native consumption. BG-058 retains complete native launch provenance,
BG-060 sustained history/reuse and BG-033 unknown recovery. BG-056 producer source
closure remains separately pending; the existing 185-case native witness is unchanged.

source/ and sources.json retain final model/fixture/runner/contract inputs.
validation/ contains all ten local gate results; fast-model.log records the direct
254-test run. Model controls execute modified source in isolated modules and must
fail their named assertions. Native calls are absent. The fixture may serialize
two logical Terminal members through one pending position, but this is explicitly
not two simultaneous native terminal captures or a new sampling profile. Existing
native sources and producer/standards pins remain unchanged.
