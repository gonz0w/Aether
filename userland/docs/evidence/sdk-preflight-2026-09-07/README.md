# SDK preflight byte and storage boundaries — UL-005 / UL-063

[Plan](PREFLIGHT-PLAN.md) scopes UTF-8 JSON intake to 2 MiB and 64 container levels,
with duplicate/nonfinite rejection and explicit evidence-storage failure. These
consumer checks do not revise owner schemas or authenticate receipts.

[Final controls](preflight-final.log) pass three valid decoder cases, eight decoder
rejections, two actual main-entry invalid-intake cases and three simulated storage
failures. Exact byte/depth limits accept; exceeding them rejects. Quoted braces,
escapes and UTF-8 text remain valid. Main intake rejects before copying/execution.
Storage failures return 1 with no success output; absent summaries are not claimed
retained, while an earlier incomplete summary survives the later-write control.

The [prior harness](check-startup-before.py) fails both intake and all three storage
controls: [output](prior-controls.log), [counts](prior-result.json).
The [initial nesting test](preflight.log) failed: this Python interpreter accepted
10000 container levels rather than raising RecursionError. [Initial source](check-startup-initial.py),
[test](test-preflight-initial.py) and [plan](initial-plan.md) preserve that attempt.
The final implementation scans structural UTF-8 bytes outside strings before decoding;
the JSON decoder retains syntax validation. No interpreter recursion assumption remains
in the depth-limit oracle.

[Schema](schema-final.log), [receipt](receipts-final.log) and [copy](copy-final.log)
regressions pass. The [final link](startup-final.log) passes all 13 commands; its
[summary](summary.json) binds source/tool/process records and staged receipt hashes.
ELF remains `d804589de3bf3f225d3ab301b5dadec0c8bbcc7e3890c1684e63e3cf4f908dbe`.
The [first link](startup.log) passed before the depth correction and is retained.
[Verification](verification.json) records interpreter, source hashes and comparisons.
[Quality output](quality.log) records the local gate.

No native execution or sibling change. The final harness and all four control
scripts are copied here for review. This completes the selected local preflight
slice, not independent approval, native acceptance, RSS qualification or protection
against hostile concurrent changes to the private filesystem. Unavailable storage
necessarily limits evidence retention; failures remain failures.
