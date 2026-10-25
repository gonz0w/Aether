# UL-007 / UL-012 experimental lab-image build review

Maintainer directs continued implementation toward a bootable lab instance and
explicitly defers SSDK-06 reader review until later. Preserve that open gate;
it does not block local bounded implementation/testing. No release approval.

Implement a small offline lab-kit builder: select a sealed corrected ABI23 SDK
candidate, rebuild clients, bind whole ELF bytes to the qualified AENMX008 serial
payload, verify actual ISO boot modules and publish a copied UEFI ISO/firmware kit
with machine-readable receipts. This consumes already qualified owner/kernel
bytes; it does not author sys-init policy, packaging state or widen native grants.
No physical-machine, general terminal, persistent filesystem or installed-system
claim. The first lab profile is the bounded three-parent serial-session workload.

Read local standards/distribution applicability, Foundations O/I/E, CP/TE and
Experience pinned CLI/stream/plain/boot rules. Existing boot markers/upstream
prompts untouched. New CLI help/version stdout0, invalid usage stderr64, missing
inputs stderr2, operational failure stderr1, successful kit path stdout0. Plain
ASCII, escaped diagnostics; progress optional. Pin input manifest before use,
complete SDK seal before code loading, actual tools/firmware/ISO/modules/client
bytes. Reject malformed/stale/profile/symlink inputs and output outside build or
existing output. No real-prefix installation or media writing.

Reuse exact owned process helper:60sec/16MiB compiler/image-inspection commands,
checked exit and cleanup; retain incomplete status on failure. Fresh smoke uses
qualified serial harness in an owned group and independent byte/lifecycle oracle.
Ten-minute local suite budget; no detached owner/background monitoring.
Test valid offline build/ISO closure, malformed/missing/stale/profile/alias/ELF
closure rejection, CLI streams/exits and actual3.10/3.14 paths. Record all attempts,
source pins and receipts. Quality/Experience/syntax/whitespace checks required.

Simpler alternative: hand the historical ISO path to the lab. It lacks a maintained
path binding the current rebuild candidate to actual boot modules and a complete
reusable kit. Copying verified qualified bytes is sufficient; avoid a new image
format, package system, kernel owner or generic VM manager. Nothing retired now;
immutable reference evidence stays intact. Scope risk is mistaking a bounded
fixture for unrestricted shell/service acceptance, addressed by explicit profile
and documentation. Current agent technical review; SSDK-06 independent reader
review deferred by maintainer, still pending. Full M3/M5/R1 remain open.
