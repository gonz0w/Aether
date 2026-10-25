# Native errno history retention — 2026-09-07

Decision 0154: 180 fresh QEMU cases pass, including three real stale-handle
errno-9 sampling positions and two deliberate omission controls. Earlier replies,
operation/error, token/generation and closed admission survive repeated denials.
Controls discarding the primary or its error binding reject at 1065/1 and 1066/1;
three positives finish at 100/3. The first worker is explicitly reclaimed before
sampling its old handle; the retained target is diagnostic, not live ownership.

witness/ retains actual producer/worker inputs, consumed source, all consumer
images/envelopes, serial/QEMU logs and the 544-command report. Frozen inputs remain
unchanged. Consumer ISO hashes are recorded; generated ISOs remain in private out.
Preflight images range 4512–6568 bytes; maximum full-suite image remains 7248/8192.
All 175 previous ABI-15 images match exactly. legacy-build/ records 151 byte-identical
ABI-6 rebuilds (build-only; no new legacy target execution). Five focused tests and
ten local gates pass in validation/. Only init.rs and binding.rs change among the
24 tracked native inputs; no new unsafe site, producer/worker or release pin change.

Catalog acceptance remains PENDING. The reused normalized producer lacks two
recorded .DS_Store inputs. Its original exact-pin historical exception does not
apply to this new bundle. catalog-candidate-rejected.json and
validation-catalog-rejected/ preserve the failed attempt. The existing catalog
remains byte-identical at 50 bundles / 3,019 cases. These 180 fresh consumer outcomes
are retained separately; they are not claimed as an accepted catalog addition.
BG-056 requires a complete newly witnessed producer bundle. No waiver was added,
no historical bytes repaired and no audit weakened. The runtime witness remains
useful within this explicitly stated producer-evidence limitation.

Source changes add private native qualification cases, not a production init API.
Next BG-058 work is closed Terminal inspection/replay; retirement/recovery remain
separate. Further host-platform qualification stays deferred under decision 0153.
