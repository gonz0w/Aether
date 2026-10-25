# Package-owner tr subset handoff

UL-013/066,2026-09-07. Proposed owner integration work, prepared locally and not
sent. No sibling approval, execution or mutation. Userland's
[TR-B01/02 profile](compatibility/TR-BYTE-SUBSET.md) defines exact byte behavior;
pkg-mgr owns its script status, locale, environment and publication contracts.
This is a proposal under existing standards, not a new cross-project API.

## Inputs and observed code

Use the [dated caller snapshot](evidence/tr-subset-2026-09-07/caller-census.json)
and [handoff identity](evidence/tr-owner-handoff-2026-09-07/inputs.json). Recheck
caller hashes before applying this review; moving files invalidate line references.
GNU9.11 and BusyBox1.38.0 pass ten exact expression tests. Existing error cases
and provider limitations remain separate from full script integration.

- mk/sdk-rebuild-plan.sh:103 explicitly rejects a failed binding-byte tr command
  before checking its output. This is a source observation, not a new runtime pass.
- mk/state.sh:177 nests tr in command substitution inside a test condition. The
  enclosing comparison consumes captured output; an explicit check of that tr
  status is not visible at this site. Exercise the actual owner entry point before
  determining the consequence. Do not infer correct handling from set -e alone.
- mk/verify-metadata.sh:61 normalizes byte_count inside an assignment, followed by
  decimal validation. Caller context can matter for shell error handling; inspect
  all actual entry paths and status results. This file does not globally export C
  locale, unlike the other five matching package scripts.

These observations identify acceptance questions. They do not establish an
exploitable vulnerability, false package acceptance or a defect in either tr
binary. Locale inheritance may already be sufficient for some entry points;
explicit evidence is required before claiming every invocation meets the profile.

## Proposed owner cases

Use the owner's existing disposable roots/fixtures and supported entry points.
Pin the selected tr and shell. Retain exact argv/env/stdout/stderr/status and
before/after package artifacts; inject only within the private test environment.
Do not install a replacement command in a real prefix or change shared PATH.

| Case | Controlled condition | Required owner observation |
| --- | --- | --- |
| TRI-01 | Normal pinned tr for both expressions | Existing successful fixtures and exact results remain unchanged |
| TRI-02 | tr emits nothing and exits23 | Non-success according to the owner contract; no success/publication inferred from empty output |
| TRI-03 | tr prints the expected decimal size then exits23 | Nonzero tool result is handled even though captured bytes look valid |
| TRI-04 | tr writes plausible binding-filter output then exits23 | Existing explicit failure route fires; output is not consumed as successful validation |
| TRI-05 | Missing/non-executable selected tr | Distinguish unavailable dependency from a successful empty transform; preserve owner exit/diagnostic contracts |
| TRI-06 | C locale versus inherited C.UTF-8/invented locale | Document which entry point establishes the required C profile; no claimed ISO support from locale-name acceptance |
| TRI-07 | Output/write failure and interruption within owner bounds | Failure propagation and cleanup observed; scratch/temporary publication and prior artifacts remain consistent with owner contract |

These are proposed cases, all owner runtime NOT RUN here. Do not copy the package
state parser or recipes into userland to manufacture integration evidence. The
owner should implement any needed status/locale correction using its conventions,
with affected regression tests. Merely changing a global shell option is not an
acceptance result; shell portability and existing statuses must be preserved.

## Return evidence and disposition

Return exact revised caller/shell/tr identities, cases attempted, expected/actual
statuses, output and cleanup evidence, and unchanged/changed artifact inventories.
Record any case outside the existing package contract as an explicit owner decision.
Userland can then bind that receipt to TR-B01/02 and update UL-013/066 integration
status. Local expression coverage already passes; it does not block unrelated
userland research. No background monitoring or automatic sibling acceptance.

Quality review scope: documentation/source inspection only, applicable DW/DP/TD/TE
and Foundations ownership/evidence rules; no source or shared pin changes. Identity
verification and quality gate apply; no runtime rerun is needed for this proposal.
Technical owner review and separate reader walkthrough remain pending. UL-007/012
native/package acceptance and UL-016 source trust remain independent.
