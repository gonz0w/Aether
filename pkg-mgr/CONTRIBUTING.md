# Contributing to pkg-mgr

This is an experimental private-root package manager. Start with the pinned
[method](../.agent-temper/METHOD.md), root [engineering policy](../PROJECT.md), root
[work selection](../.planning/STATE.md), [README](README.md) and
[architecture](docs/ARCHITECTURE.md). Component records retain owning details and
stable IDs; local STATE's historical next actions do not select new work.
The [development process](docs/DEVELOPMENT.md) defines check selection, evidence,
review and remaining release gates. [Shared standards](docs/STANDARDS.md) identify
released requirements and draft migration scope.

Before changing behavior, record the intended result, affected interfaces, forbidden
outcomes and selected tests in the owning bounded record. Prefer meaningful
test-first work. Reproduce bugs before fixing them, or record why deterministic
reproduction is unavailable and the alternative evidence. Record the actual sequence
without inventing a prior red result. Update the canonical reference
and inventory when a surface changes, or explain why documentation is unaffected.
Keep formatting changes separate. New dependencies need purpose, exact origin/version,
license, offline/bootstrap implications and an update/removal path.

For substantial design changes, answer the three simplicity questions in the
existing [development review](docs/DEVELOPMENT.md). Ordinary small fixes keep their
proportionate explanation; no extra review document is required.

Select affected checks using root DEVELOPMENT's focused cadence. Run commands
from `pkg-mgr/`; documentation-only work uses the local development/standards gates.
Use the bounded aggregate when required or no safe subset exists:

```sh
sh tests/check.sh  # includes required ShellCheck 0.11.0 for all active shell files
# Fast targeted lint while iterating; also required for each new or revised first-party shell file:
python3 tests/check-development.py --lint tests/check.sh
```

Select additional compiler/native checks using the development process. Report missing
required tools as blocked. Never turn a skipped check into a pass. Review changed
ownership, cleanup and authority boundaries before style. Interface changes require
matching producer/consumer evidence and actual affected-owner review; do not invent
sign-off. Preserve failed attempts and exact input identities.

Original contributions use [BSD-2-Clause](LICENSE). Preserve upstream notices and
source provenance. Recipes do not relicense their payloads. Proprietary firmware or
drivers require component-specific redistribution review and target evidence; the
shared policy permits them but approves no individual component. Report vulnerabilities through [the security policy](SECURITY.md). Triage ownership
and support commitments remain publication gates.
