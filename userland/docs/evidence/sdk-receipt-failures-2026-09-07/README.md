# SDK receipt failure retention — UL-005 / UL-063

The startup harness now initializes its report before reading prerequisite SDK
and package-layout receipts, inside the existing exception/report boundary.
[Plan](RECEIPT-FAILURE-PLAN.md) records the scope and remaining limitations.

[Receipt controls](receipts.log) pass three cases: missing SDK receipt, missing
layout receipt and malformed SDK JSON. Each retains the exact prerequisite error,
an incomplete summary and zero process commands. The [prior harness](check-startup-before.py)
fails all three with uncaught errors; [prior control output](prior-controls.log)
is retained. Fixtures use private build paths; real receipts remain unchanged.

The [copied-source regression](copy.log) passes. The [full startup run](startup.log)
passes all 13 commands, including its expected compiler/link failure cases. The
[summary](summary.json) retains exact argv, cleanup, tools and source hashes.
ELF remains `d804589de3bf3f225d3ab301b5dadec0c8bbcc7e3890c1684e63e3cf4f908dbe`.
[Verification](verification.json) records the actual interpreter and comparisons;
[quality output](quality.log) records the local gate.

No native execution, sibling mutation or source-trust promotion. Structurally
invalid but parseable receipts and inability to create/write the report directory
remain separate follow-ons. Independent technical review remains pending.
