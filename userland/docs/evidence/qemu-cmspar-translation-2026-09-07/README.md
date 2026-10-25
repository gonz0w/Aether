# UL-069 host translation witness — 2026-09-07

[cmspar.patch](cmspar.patch) adds one guarded CMSPAR row to QEMU 10.0.11's
linux-user cflag table. Both termios translation directions use this table.
The archive and all 117 retained files (including 103 build packages) match pins.
[Plan](TRANSLATION-PLAN.md) and [driver](check-translation.py) record the scope.

Ten complete compile/run commands pass their expected outcomes. The original
and wrong-host-bit tables exit 20 at the independent oracle. The patched,
missing-host-definition and missing-target-definition variants each pass 1024
combinations of character size/control flags in both directions. The synthetic
host CMSPAR bit deliberately differs from the pinned target bit. Unsupported
variants omit it explicitly; they do not claim functional CMSPAR support.

Tests compile actual upstream translation functions and non-baud table rows,
not a complete emulator. QEMU GPL/LGPL notices and license files are retained
under the summary's original/ tree; generated fragments retain their notices.
New standalone orchestration/oracle source is BSD-2-Clause, without relicensing
upstream code or derived generated translation units.

[Summary](summary.json) retains compiler, selected host SDK identities, original
inputs, generated artifacts and all argv/exits/cleanup. [Verification](verification.json)
records comparisons. The first compile failed because host libSystem could not be
located: [initial summary](initial-summary.json), [stderr](initial-compile.stderr),
[driver](check-translation-initial.py), [unformatted control](control-initial.c).
The final run selects the existing MacOSX27.0 SDK explicitly and formats only new
original C. [Run log](run.log), [format check](format.log), [quality](quality.log).

Full Linux emulator builds, actual PTY behavior, partial failure/restoration and
GNU/BusyBox consumer reruns remain NOT RUN. Existing runtime images are unchanged.
Source authentication remains UL-016; selected host link inputs are not a complete
host SDK closure. The maintainer approved this slice on 2026-09-07; see
[review receipt](maintainer-review.json). No detailed findings or reviewer logs
were supplied. Full emulator/runtime acceptance remains open.
