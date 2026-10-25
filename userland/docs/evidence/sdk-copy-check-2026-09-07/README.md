# SDK copied-source validation — UL-005 / UL-063

The startup harness now checks copied probe/adapter bytes against the selected
receipt before compilation. This closes the gap between checking live sources
and consuming their copies. [Plan](STARTUP-PLAN.md) records scope and limitations.

The [control](control.log) injects changed destination bytes while preserving the
live source hash; the fixed harness returns incomplete with zero process commands.
The [prior implementation control](prior-control.log) fails at the first attempted
compile. No actual compiler executes in that control. The original source and
imported SDK are not mutated. [Prior source](check-startup-before.py) is retained.

The [final link run](startup-final.log) passes all 13 recorded commands, including
expected failure controls. [Summary](summary.json) retains exact process records,
source/tool pins and staged hashes. All four staged sources match the receipt.
The resulting ELF remains
`d804589de3bf3f225d3ab301b5dadec0c8bbcc7e3890c1684e63e3cf4f908dbe`.
The [first successful run](startup.log) is preserved; a plan-wording clarification
triggered the final rerun so the consumed plan identity matches the final document.
[Initial plan](initial-plan.md) matches that first run's recorded hash.

[Verification](verification.json) records interpreter/platform and comparisons.
[Quality output](quality.log) records the local gate. The native suite was not
rerun: this change affects host source staging, not native sources or protocols.
Private work directories must remain owned and unmodified after validation;
this is not protection against arbitrary concurrent writers to those directories.
Independent review and full UL-005 acceptance remain pending.
