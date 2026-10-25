# Unchanged dash file-descriptor leak control — 2026-09-15

The unchanged consumer fd-leak-control script now runs through actual dash
fork/exec/wait. Its helper detects the inherited non-CLOEXEC writer at FD9 and
returns95; dash returns22. Expected stdout is empty. The owner retains one
shared file description across both processes and closes the backend only after
its final holder releases it. FD10 is removed at exec. This is volatile scratch
storage, not persistent filesystem or installed SDK acceptance.

## Qualification

- `connections.json`, `connections-results.json` and `connections.log`: all348 connections cases pass on262 frozen
  runtime/support inputs in1093.866605seconds, below the1800second review ceiling.
  The wrapper allows3600seconds; per-build180 and per-QEMU30 watchdogs are unchanged.
- `connections-traces.json` and the four serial logs retain exact new outcomes.
  Positive: child95, parent22, backend17 twice, owner100/reclaimed6.
  Parent-reference grant: child80/owner1980. Missing description:
  child224/owner2130. Skipped actual helper: child0/owner2130.
  Every control has zero reclaims and the exact ordered rejection, not a timeout.
- Positive owner14136bytes, dash ELF257504bytes and replacement ELF26216bytes
  fit existing bounds. The controls' owners are at most14152bytes. No kernel,
  scheduler, ABI envelope, service quota or released standards pin changed.
- `host-final.log`: required Zig and104 Python host checks pass. `owner-host.json`
  retains all33 composed Rust tests, including current-holder record scope,
  poisoning, count limits, closure and unchanged rejection state.
- `compatibility.json`: all661 pre-existing top-level ELF/raw images match the
  preceding scratch-exec-last full suite byte for byte.
- `checks.json` and `final-checks.json`: formatting, workflow, released standards
  and the four pinned simplicity inputs pass. The existing connections test-group
  oracle and shell/companion references were updated; no new public script command.

## Inputs and attempts

`final-sources.json/tar.gz` capture every input named by the final native report.
`review-sources.json/tar.gz` separately capture host tests and current reference
updates. The locally pinned script SHA256 is
1e66c6d1748a1789137bc200e9919c34296fadf8f4088ecea275c681a5f64f7d.
The harness verifies its output/status pins and the existing captured consumer
helper/SDK/tool inputs; full commands, SDK receipts and tool hashes are in the
native report. This packet does not claim a new standalone SDK handoff.

Two early selector attempts stopped on overly specific text anchors before any
native build. Their exact scripts/logs are retained. The next build failed because
FORK_SHELL_FILES and the harness both defined FORK_SHELL_ARGV; the helper now guards
that definition. The initial transformed-harness native run then passed the
unchanged script. After regular inclusion, the grant control rejected at the
existing incomplete-readiness check1980, earlier than the predicted1950. The
corrected oracle requires child80 followed by1980/reclaimed0. No runtime behavior
was weakened to satisfy that oracle. The positive and all three controls then
passed in the regular harness and the full suite.

`initial-native-sources.json/tar.gz` were reconstructed from final bytes and
preserved earlier inputs and verified against every recorded initial source hash.
`compile-failure-sources.json` defines the verified helper overlay for the failed
build. `regular-attempt-1-sources.json/tar.gz` preserve the earlier oracle inputs.
Initial selectors consume the initial harness snapshot; the regular selector
consumes the corresponding regular/final snapshot. Prior evidence packets and
sibling repositories remain unchanged.

## Retention and limits

The four focused output trees and full suite are archived with per-file hashes,
reports and serial evidence. Every member and original was rehashed before
removing only the verified generated duplicate. Cleanup receipts record the exact
paths and bytes. Deliberate failures and unexpected failed attempts are retained.

This is producer qualification. Next qualify the unchanged redirection script's
duplicated writes and file readback. Matching command-runner results and independent
SDK/consumer acceptance remain required before handoff. Poisoned-close recovery,
persistent storage, package/sys-init assembly and R1 readiness remain open.
