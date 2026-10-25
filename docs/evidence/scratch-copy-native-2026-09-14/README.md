# Live scratch descriptors through native copy — 2026-09-14

Scope: opt-in scratch_copy on the existing masked native copy operation. The
actual C source opens FD3, duplicates it as CLOEXEC FD4 and writes A. The owner
validates the exact frozen descriptor table, admits the copied child, stages its
file holder and supplies generation-scoped file/root references in receipt bytes
24/28. The child validates those references before readiness. Old receipt tails
remain zero in every other profile.

The parent closes both aliases before child application I/O. The child retains
both flags, writes B through FD3, closes it, writes C through FD4 and closes it.
The Rust owner independently reads exact ABC and closes the verification handle.
The old stream fixture then finishes source71/child72/backend17 twice with six
reclaims. This is live copied-descriptor evidence, not exec/CLOEXEC removal or
unchanged dash redirection. The pure files exec plan is still awaiting native use.

## Results

- Four focused cases pass on their first attempt (`focus-1.log/results/traces`).
- All335 connections cases pass in1040.734636seconds, below the1800second review
  ceiling (`connections.json/log/results/traces`). Per-case timeouts are unchanged;
  the complete-suite outer bound is3600seconds.
- Offset loss rejects owner2507/reclaimed0 after independent readback; early close
  terminates child251 then owner1950/reclaimed0; altered snapshot flags reject
  owner2506/reclaimed0. Exact terminal lists are checked, not timeout acceptance.
- Host Zig and104 Python tests pass (`host.log`); workflow, Rust/C formatting and
  simplicity manifest/four-member hashes pass (`checks.json`).
- All635 previously recorded ELF/raw images compared byte-for-byte unchanged
  (`compatibility.json`). The four new owner images are13816–13832bytes, within
  the existing16384byte envelope; each new client ELF is22064bytes.
- No failed attempt, kernel/quota change, new dependency, sibling edit or released
  pin change. Runtime sources remained frozen throughout qualification.

## Reproduction and retention

`attempt-1-sources.json` pins276 inputs; its tar archive contains those exact
bytes. SDK/toolchain provenance and detailed build/run records are in both suite
results and artifact archives. The required commands are captured in
`connections.json` and `run-full.py`; `focus-selection.py` restricts the existing
harness to the four cases without changing their implementations or oracles.
These scripts are retained evidence, not new developer entry points; rerun to a
fresh output directory rather than overwriting this sealed packet.

Each artifact archive is paired with a complete per-file hash inventory. The
collector verifies every archive member and rehashes the loose originals before
removing only that exact duplicate suite directory. Both cleanup receipts retain
paths, counts and bytes. Prior evidence remains untouched. Source, document and
report hashes are sealed in SHA256SUMS.

## Remaining boundary

Next: image replacement with validated scratch references/surviving table, and
child-local CLOEXEC holder removal without closing a surviving parent holder.
Then unchanged dash fd-leak-control/redirection, full connections and matching
runner, followed by independent userland/SDK acceptance. Poisoned scratch close
and confirmed-stop recovery remain unqualified. No persistent filesystem,
release assembly or full interactive-shell readiness is claimed here.
