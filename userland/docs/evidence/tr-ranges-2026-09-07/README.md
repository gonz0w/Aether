# UL-066 bracketed-range finding resolved

All eight comparisons pass under the same pinned GNU9.11 and BusyBox1.38.0
binaries and corrected emulator. [Results](guest.stdout), [summary](summary.json),
[verification](verification.json). Both providers agree for the original phrase
and every byte value, in C locale, with exit0 and empty stderr.

| Expression | Original phrase output |
| --- | --- |
| tr '[a-z]' '[n-z][a-m]' | squc]kgsf ossgdr]ec |
| tr 'a-z' 'n-za-m' | squeamish ossifrage |

Each output ends in a newline. The [pinned BusyBox source](upstream-tr.c) documents
that ordinary brackets are literal; class/equivalence constructs have separate
handling. Expanding the first destination produces `[nopqrstuvwxyz][abcdefghijklm]`,
which includes extra literal brackets. It is not the26-letter ROT13 destination.
An explicit positional byte table independently predicts every observed byte.
The plain expression also matches the separately specified literal ROT13 phrase.

The earlier supplementary expectation was incorrect. This is not a new BusyBox
provider defect. The five legacy script successes and five exit99 controls stand;
the old combined INCOMPLETE result and its exact expectation remain preserved in
[historical evidence](../busybox-legacy-2026-09-07/README.md). No binary, upstream
script or old oracle was changed to make it pass. This new result disposes of the
interpretation question separately. Existing four common-fixture differences
remain real comparison findings and are unaffected.

One eight-case execution completed with all process groups cleaned and container
absence confirmed. Sources and staged bytes were reverified. [Plan](RANGE-PLAN.md),
[syntax](syntax.log), [quality](quality.log). Inputs and upstream notices retain
original terms; new adapter is BSD-2-Clause. No native/POSIX/locale-wide claim or
new release-trust approval follows. New legacy/range adapters remain pending review.

Next UL-066 coverage gaps are the unavailable ISO-8859-1 branch and static stty
fault-injection witness, alongside provider/source review. UL-069 remains closed.
