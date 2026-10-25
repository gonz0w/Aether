# Sustained decoder proposal — 2026-09-25

UL-059 / UL-063 / UL-081. **Host-only executable proposal; runtime adoption and
owner review pending.** Source review is in review.md; exact inputs, patched
copies, commands, process receipts and results are retained here. Build artifacts
remain under the private root named in build-artifacts.json.

The small decoder.patch applies only to copied four-role and result sources and
headers. AERIO002 accepts nonzero16-bit epochs and result paths accept the new
0x7b receipt domain, including terminal-exit policy. Versioned function symbols
prevent a v2 caller silently linking to a legacy decoder. Default source files,
accepted runtime binaries, earlier sealed proposal and SDK remain unchanged.

Actual host results, Clang21.1.8 C17 with UBSan on the recorded macOS platform:

- Proposed roles:2,592 cases, eight boundary epochs, every byte mutation and
  truncation, malformed sizes and invalid generation context.
- Proposed results:37,716 assertions, eight boundary epochs, all4095 wire errors,
  terminal exit/cleanup policy, padding, malformed replies, invalid domains.
- Independent peer control: all65,535 epochs, both directions of old/new wire
  rejection, stale expected receipt and zero/overflow context rejection. These
  are decoder observations, not proof of native replay prevention or retirement.
- Unchanged legacy controls:648 role cases and28,159 result assertions.
- Deliberately mixed link fails on ar_roles_decode_sustained_v2 as expected.
- New C formatting and Python syntax pass; every owned child reports complete
  cleanup. No failed or incomplete attempt preceded this passing run. The mixed
  link failure is the intended negative control and its raw output is retained.

Reproduce from repository root with
`python3 -B experiments/command-runner/sustained-decoder/check.py`.
It verifies baseline hashes, creates a fresh build root, pins inputs before use
and leaves all attempts intact. Commands have30-second bounds and16MiB streams.
The driver source supports Python3.10+ syntax but only the recorded interpreter
was executed; no minimum-version qualification is claimed. No network or real
prefix installation is used. No native build or execution occurred.

SUSTAIN-01–03 and06 gain pure-decoder coverage only. Child bootstrap NIO2, full-width
native identity validation, transport poisoning, complete profile linking, owner
cohort invariants, receipt consumption, foreign endpoints, exhaustion before
side effects, five native cycles and authorized shutdown remain untested here.
Review and qualify these before rebuilding/adopting the complete runtime profile.
UL-063's broader audit and independent reader/owner reviews remain open. This
experiment does not supersede the separate dash recovery workload.

Local quality gate passes. All three preceding evidence seals and baseline source
hashes were rechecked successfully; preservation.json records their identities.
