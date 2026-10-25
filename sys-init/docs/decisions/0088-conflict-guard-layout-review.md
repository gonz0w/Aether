# 0088 — Conflict-guard layout review

Build/research plan, 2026-09-06; BG-058 following decision 0087.

Compare the two best retained source revisions (5 and 7) under the unchanged
Rust/profile/linker inputs. For each, test all eight always/never inline choices
for Pending::begin, Pending::conflict_synthetic and Held::offer_synthetic against
all five proposed guard cases. This is a bounded 80-link matrix, not an unbounded
optimizer search. Preserve every instruction/assertion except these attributes;
keep sources outside the live runtime. An acceptable candidate must fit every
positive/control and still needs all 151 existing oracles plus fresh native
consumption. Failed links never count as semantic control coverage.

Also review the current sibling's separately bounded program profile: it permits
8192 supervisor bytes, but that alone does not establish ABI-6 compatibility.
Retain cited source identity and startup/envelope/authority differences; no mutable
sibling source becomes a runtime dependency. Existing native source and standards
pins remain unchanged. Record follow-ons before closing this research, update
quality/planning records and run all nine development gates.


## Result and disposition

Decision 0088 completes the bounded 80-link guard layout study: 78 links exceed
4096 bytes and two isolated forget-reader controls link but were not executed.
No full variant fits. The best same-source variant maps conflict/resources at
4256/4528 bytes, saving 208/96 bytes over the prior separate minima. Existing
Aether ABI 8 is not init-compatible: its bootstrap authority, profile dispatch,
worker slots and completion oracles differ. Hashed research snapshots and a
concrete init-compatible capacity request are retained; no runtime or sibling
source, ABI, bound or pin changed. The accepted 151-case runtime is unchanged.

Next BG-058: obtain a producer decision and separately pinned init-compatible
fixture before adopting a larger image. Then qualify the guard with fresh native
consumption, preserve all 151 cases and add the five proposed cases. Construction
denial, closed reoffer and PH-05–07 remain open. A deeper layout redesign, if
needed instead, requires its own bounded plan. See docs/research/
NATIVE-CONFLICT-GUARD-LAYOUT.md and NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md.

Validation: all nine development gates pass in `out/checks/run-s3ucn1zi`,
with no skipped gates and unchanged checked sources. Independent artifact review
confirms that only the three requested inline attributes vary, every mapped extent
matches the .text section size, and all 78 rejected links contain the size-limit
diagnostic. All eleven live consumer inputs and pinned compiler inputs still match.
No native case executed; the 151-case checkpoint and historical native audit remain
unchanged. Evidence, gate logs and host sample artifacts are retained under
`docs/evidence/conflict-guard-layout-2026-09-06/`.
