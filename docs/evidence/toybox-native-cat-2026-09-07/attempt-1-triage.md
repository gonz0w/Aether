# Attempt 1 — patch-anchor guard rejection

No target ran. The recipe required a unique `_exit(toys.exitval);` substring,
but xwrap also has a distinct conditional direct exit in its vfork path. The guard
rejected before patching or compiling the new probe. Retain sources and recipe;
anchor the exact standalone call followed by _xexit's closing brace. Do not alter
the vfork exit or rebound branch. This is a recipe failure, not runtime coverage.
