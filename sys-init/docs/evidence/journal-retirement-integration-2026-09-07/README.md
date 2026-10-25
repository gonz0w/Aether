# Journal retirement integration — 2026-09-07

Decision 0163 qualifies the actual JournalRuntime, CleanedAdapter, CutCoordinator
and Retirement together. Mixed Cleaned/Launched and Cleaned/Terminal cuts retire
only the Cleaned member and preserve the other member's real journal obligation,
synthetic pending position and lifecycle state. Old release/retirement replay is
inert. Cleanup does not substitute for pending release, and retirement performs
a fresh resource inspection. Uncertain release or marking closes the coordinator
while retaining Applied receipts, partial tombstones and actual journal state.

All 287 model tests pass, including seven new integration tests and two source
omission controls. All ten local gates pass in `run-zegjjv6m`, with unchanged
checked inputs. All twelve native consumer sources, three release locks and catalog
bytes match the preceding checkpoint. Runtime algorithms are unchanged: this is a
composition witness using trusted synthetic resource, pending and mark callbacks.
It is not native disposal or independent reviewer sign-off.

Next BG-057/BG-058: review the native adapter mapping against the current 185-case
checkpoint and define a bounded consuming integration witness for the three-phase
cut, pending release and retirement path. Native provenance/resource ownership
remain explicit requirements. BG-060 retains sustained reuse, BG-033 recovery and
BG-056 the producer source-closure limitation; no historical waiver is broadened.

`source/` and `sources.json` retain exact runtime/model/test/runner inputs.
`validation/` and `checks.log` retain the full local run. `model-fast.log` retains
`python3 -m unittest discover -s tests -p test_runtime_model.py` against the same
source/test inputs. All prior native and standards evidence is unchanged.

The seven integration tests exercise mixed cuts, sequential cleanup, replay,
independent pending release, resource reinspection, uncertain callbacks and copied
receipt denial. Two source omission controls test missing release prerequisites
and an incorrectly selected Terminal member. Resource metadata and pending/mark
operations are synthetic; no native resource operation or arbitrary service runs.
`sha256.json` seals the package.
