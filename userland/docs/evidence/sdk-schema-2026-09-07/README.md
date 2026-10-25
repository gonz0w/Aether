# SDK consumed-field validation — UL-005 / UL-063

The [plan](SCHEMA-PLAN.md) scopes local field validation without changing an owner
format. Objects, consumed hashes, absolute input/tool paths and canonical relative
SDK inventory paths are checked before copying or executing. Libc receipt fields
are validated after receipt identity verification. Unknown owner fields remain allowed.

[Final schema controls](schema-final.log) pass 24 invalid-input scenarios, six libc
shape controls and a valid unknown-metadata control. The main-entry scenarios
require field-specific incomplete reports and zero copy/process calls. The
[prior implementation](check-startup-before.py) fails all 24 scenarios;
[prior output](prior-schema.log) and [counts](prior-result.json) retain that result.

[Missing/JSON receipt regressions](receipts.log) and the [copy control](copy.log)
pass. The [final startup run](startup-final.log) passes all 13 commands with
receipt-matching copied sources and the original ELF hash
`d804589de3bf3f225d3ab301b5dadec0c8bbcc7e3890c1684e63e3cf4f908dbe`.
[Summary](summary.json) retains process receipts and exact source/tool identities;
[verification](verification.json) records actual interpreter and comparisons.

The [initial startup](startup.log) also passed; [initial source](check-startup-initial.py)
matches its source hash. A subsequent addition records the consumed package-layout
hash, prompting the final rerun. [Initial controls](schema.log) are retained.
[Quality](quality.log) records the local gate. No native execution or sibling changes.
Independent technical review remains pending. JSON resource/duplicate-key limits,
hostile filesystem concurrency and unavailable evidence storage remain outside scope.
