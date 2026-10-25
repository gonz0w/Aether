# UL-066 legacy BusyBox tr coverage

All five unchanged BusyBox1.38.0 legacy scripts exit0 against the pinned GNU9.11
comparison provider. Each rejects a replacement BusyBox wrapper returning99.
The additional exact-output check for the non-gnu example fails, so the new
combined slice remains **INCOMPLETE**. [Raw results](guest.stdout),
[summary](summary.json), [verification](verification.json).

| Script | Upstream script exit | Failure-control exit |
| --- | --- | --- |
| tr-d-alnum-works | 0 | 99 |
| tr-d-works | 0 | 99 |
| tr-non-gnu | 0 | 99 |
| tr-rejects-wrong-class | 0 | 99 |
| tr-works | 0 | 99 |

The first/fourth/fifth and deletion comparison scripts use GNU-vs-BusyBox diff;
those comparisons succeed. The non-gnu script simply prints the result and checks
command success through sh -x -e. It contains no expected output. Our additional
ROT13 interpretation expects `squeamish ossifrage` plus newline but observes
`squc]kgsf ossgdr]ec` plus newline for its bracketed range expression.
This is a failed supplementary expectation, not a failing upstream exit oracle,
proof of a POSIX defect, or evidence that this source ever promised ROT13 output.
The exact input, output and source hashes remain available for interpretation.
No expected bytes or source were adjusted after observation.

[Plan](LEGACY-PLAN.md) records the predeclared oracles and bounds. One live attempt
ran all ten cases; each process record has complete cleanup, and container absence
is confirmed. Inputs are read-only, uid65534, no capabilities/network,512 MiB,
32 PIDs,15 seconds per child and180 seconds per container. Private comparison-file
bytes and raw streams were captured before container removal. Sources and staged
hashes were reverified. [Syntax](syntax.log) and [quality](quality.log) pass.
Upstream tests and notices remain under their original terms in the pinned archive
and staged legacy directory; the new adapter is BSD-2-Clause.

Next UL-066: compare the bracket/range expression under both pinned providers and
review its intended interpretation before classifying the supplementary mismatch.
Preserve the five upstream successes and the separate failing output expectation.
The four earlier common-fixture differences, locale/static fault coverage, source
trust and native acceptance remain open. New adapter review is pending; UL-069's
approved emulator/recovery scope remains closed.
