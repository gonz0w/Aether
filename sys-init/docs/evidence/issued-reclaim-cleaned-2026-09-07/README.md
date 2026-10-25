# Issued reclaim and Cleaned — 2026-09-07

Decision 0176 executes the exact generated-dependent reclaim occurrence,
acknowledges it, and applies Cleaned. The driver checks the original source and
full Started token, records actual reader-close and worker-reclaim tuples before
interpretation, and clears each reference only after its own zero success.
Returned/Applied/Executed cannot precede the actual work. Repeated execution and
acknowledgment deny. Partial errors preserve Unknown, actual returns and remaining
references; History admission closes. Closed-reader EACCES (-13) and stale-worker
EBADF (-9) are observed kernel outcomes, not manufactured errno.

Cleaned requires the exact acknowledged reclaim, its original-owner retirement
metadata, a retained Terminal cut and no generated resource references. It moves
the dependent from phase 2 to 3, preserves the original Terminal history, emits
no effect and replays without mutation. Invalid resources/sources deny before
application. Unexpected transition or pool contents retain Unknown and close.
Raw reclaim tuples remain local through acknowledgment; this is not persistent
recovery or extended raw-return retention.

Ten new cases pass in fresh Aether execution: reclaim and Cleaned positives both
return 100/reclaimed 3; token/early-ack/reader/worker/error controls return exact
1100–1105 contexts, and Cleaned controls return 1108/1109 after one reclaim.
All 214 prior ABI-16, 208 ABI-15 and 151 ABI-6 images rebuild byte-identically.
Those 573 comparisons reuse earlier target evidence; this is not a new 224-case
execution campaign. The maintained composed suite now selects 224 cases with
the pinned service worker. All ten local gates pass in run-gsx2lahk; the Rust
core passes 25 tests and 17 omission controls across ten top-level Rust groups.

Default Cleaned linking rejects at 18,616 bytes. Only its three probes add fat LTO
and one codegen unit; positive is 14,728 bytes. Reclaim stays size-s (positive
13,912 bytes). Code stays bounded at 16,384 bytes and stack at 4096. All ten final
paths execute without guest faults; this is not a stack high-water/headroom or
performance claim. Storage/Application remain 1976/1992 bytes, with no allocation
or added unsafe site. Shared release, producer, worker and old profile pins stay
fixed; sibling repositories and historical evidence are unchanged.

Retained failures include the first nested fixture-launch stack fault, the stale
reader's incorrect EBADF oracle, a nested stale-worker fixture stack fault, the
three default-profile Cleaned link rejections, and the stale 22-test local oracle
after adding three passing core tests. Fixture preparation/reuse now runs in the
caller, the errno expectation matches the enforcing kernel, and the required
core count is 25. No failed attempt is counted as acceptance.

The provider is still disposed by fixture cleanup; it has not traversed policy
Terminal/Cleaned after dependent Cleaned. Next BG-057/BG-058: complete that
two-service teardown and preserve both histories. Then address fixed storage
retirement/reuse under BG-060. Recovery (BG-033), independent review and new-profile
catalog audit support (BG-056) remain separate. No current kernel blocker.

witness/ retains the ten final executions, copied sources/inputs, commands, raw
images/envelopes, serial/QEMU logs and ISO hashes. attempts/ preserves all earlier
target/build attempts and restricted drivers. ISOs remain in private out/.
The three reclaim-*-build directories retain every compatibility image and command.
validation/ and rust/ retain passing local checks; failed-local-checks/ and
failed-rust/ retain the stale-count failure. Producer provenance remains bound
through decision 0175; its full source archive is copied unchanged in inputs.
adoption/ records the handoff; sha256.json seals this bundle.

Final adoption refresh: all ten gates pass in `run-pt9wjd5t`, with unchanged checked
inputs. post-validation/, post-rust/ and postchecks.log retain this refresh.
Installed executable identities still match decision 0175 pins.
