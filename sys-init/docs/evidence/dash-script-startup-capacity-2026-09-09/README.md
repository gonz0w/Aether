# Normal script startup rollback: capacity result

The ordinary startup integration candidate fails the unchanged two-code-page
linker assertion. Measurement-only linking yields **9,152 bytes**, 960 over the
8,192-byte profile. No candidate kernel/image was built or booted. This is one
concrete integration measurement, not proof that all smaller designs are impossible.
The selected stop image previously occupied all 8,192 bytes.

The candidate adds sequential rollback to the ordinary file/stream/shell launch
sites. Confirmed Known startup failure cleans retained endpoints, closes stream
startup handles where applicable, observes provider terminal17 and reclaims before
reporting startup failure1605. Unknown outcomes fail before cleanup. These are
intended semantics only: the candidate never reached native qualification. Existing
separately selected rollback probes remain the evidence for their own limited scope.

Inputs are the frozen Dash script intake sources and exact recorded Rust toolchain,
with the maintained owner patch/modules. `run-script-startup.py` records the attempted
build; `build/results.json` contains its actual failed command and no passing cases.
`build/measurement.json` records the diagnostic command, environment, size and hash.
The diagnostic linker removes only the code-size assertion and is never used to boot.
Candidate sources, adapted producer source and logs are retained here. No runtime
profile, stack limit, released pin, machine protocol or sibling repository changed.

The maintained patch and binding are restored byte-for-byte to the preceding
native stop checkpoint (`restored.json`). No new native behavior is accepted.
Documentation impact: adapter reference, current plan, BG-067 and quality inventory
now state the blocker instead of promising the integration is ready.

## Scoped review and next decision

SE-01–05: retaining fail-fast startup is simpler, and remains the validated fallback,
but does not meet automatic rollback. Reusing the existing paired owner avoids a
second manager; the candidate removes success-only launch handling in three sites.
It adds cleanup control flow rather than new protocol/state machinery. No ownership,
error or resource checks were removed to force it under the limit. O-01/04,
I-01/03–06 and E-01–08 apply; no standards exception is claimed.

BG-067 next needs a scoped size/design review or a matching producer capacity
handoff for this ABI9 three-role script profile, then fresh positive, rejection,
rollback and stop witnesses. The historical ABI16 init profile does not establish
capacity for this separate profile. Do not silently reuse its larger mappings.
Sustained wait/reuse/shutdown and broader shell work remain separate. No sibling
request was sent and no larger budget was adopted.

## Validation

All ten local gates pass in `run-5uw_uetq` with unchanged checked sources.
The previous stop evidence seal verifies all66 files; all five maintained command
source/patch files match that native checkpoint. `git diff --check` passes and
all three released lock hashes are unchanged. No fresh native run is claimed.
