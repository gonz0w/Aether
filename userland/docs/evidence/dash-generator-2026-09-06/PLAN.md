# UL-077 — controlled target-generator build stages

Avoid nested cleanup owners: compile target generators locally, invoke all four
from the top-level Python owner, then finish local make. Replace generated compiler
subprocess forwarding with exec; local configure/make/tool calls use the unchanged
owned process helper. Guard generator names against unplanned make re-execution.
Do not change upstream source/recipes; use the pinned Makefile.am generator list and
source arguments, validated before use. Preserve compiler options and target ABI.

Containers get a read-only private build-tree mount plus one writable obj/src child
mount, with cwd there. Lifecycle receipts stay outside that writable subtree.
Validate paired/exclusive mount arguments, private-root/subdirectory and delimiter
bounds before client calls. CP-01–03, O-03/04, E-01–08 and UL-063 apply. No nested
remote owner may be killed by the local make watchdog. No shared pins/sibling edits.

Run model mount/guard controls on 3.10.21/3.14.7; real boundary control must write the
allowed child and fail writing its parent. Build fresh pinned dash, require all four
container lifecycle receipts and fail guards, audit imports, and run twelve guest
cases on fresh artifacts. Compare generated semantic tables/imports and record ELF
identity without assuming byte reproducibility. Keep exact tool/script/SDK/connection
identities, all failed attempts, output and independent container absence checks.
Run local quality/whitespace gates. Independent review and true remote creation/
service-loss ambiguity remain open; no native or whole-release acceptance.
