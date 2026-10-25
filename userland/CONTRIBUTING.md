# Contributing to experimental Aether userland

Start with the pinned [method](../.agent-temper/METHOD.md), root [engineering
policy](../PROJECT.md), root [work selection](../.planning/STATE.md), [component
guidance](AGENTS.md) and [quality workflow](docs/quality/PROCESS.md). Local UL records
own component details; historical STATE summaries do not select new work.
This repository does not yet ship a supported POSIX shell system. The workflow defines change review, test selection,
source rules, documentation coverage and explicit release blockers.

From `userland/`, run `python3 -B docs/quality/check.py` with Python 3.10+
for the offline standards/inventory gate. A passing result is structural evidence;
run the relevant experiment commands before accepting behavior changes. If a pin
fails, investigate the changed bytes before updating it. Do not install into a real
prefix or fetch dependencies as a hidden test step.

Use stable UL backlog IDs. Keep shared standards in Aether-standards and local
implementation contracts here. Original contributions use BSD-2-Clause; preserve
upstream notices and immutable evidence. No dedicated private security-reporting
channel has been established in this experimental checkout; establishing a real
maintained reporting policy is a prerequisite to a supported release (UL-016).

The [quality checker manual](man/man1/aether-userland-quality.1) documents its
options and failure outcomes. See [offline manual reading](man/README.md).
