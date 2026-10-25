# UL-013 / UL-066 package tr forms

Both pinned providers pass all ten byte-subset cases. [Summary](summary.json),
[raw results](guest.stdout). Tests use independent deletion-byte sets and cover
all256 bytes,empty input and actual numeric-whitespace shape. No provider was
rebuilt or selected for installation; no sibling script was executed.

[Caller census](caller-census.json) records14 pkg-mgr/mk shell files and10 matching
lines in6 files. The discovered binding expression is now tested explicitly.
Five matching scripts establish C locale; verify-metadata.sh does not do so
globally. The scan's sys-init/scripts *.sh inventory is empty, not comprehensive
proof about sys-init callers. Missing directories in the initial exploratory rg
query were reported before the explicit census; no missing input counts as tested.

[Candidate subset](../../compatibility/TR-BYTE-SUBSET.md) and its JSON define two
literal forms, exact byte behavior and integration boundaries. These are local
requirements, not pkg-mgr adoption or a competing shared standard.
[Plan](SUBSET-PLAN.md), [syntax](syntax.log), [quality](quality.log). Current source
hashes match retained input identities. All process cleanup completes and the
owned offline container is observed absent. Inputs remain read-only; new helpers
are BSD-2-Clause and upstream notices unchanged.

Next: package-owner locale/error-propagation review and actual pinned consumer
integration before native/package claims. Userland's bounded expression tests
are complete; broader provider differences, UTF-8 limitations and new helper
review remain open. No new cross-project action or acceptance is implied.
