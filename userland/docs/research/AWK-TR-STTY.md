# Awk, tr and stty provider checkpoint

UL-066, 2026-09-06. Contributor decision reference for experimental package
selection. See [the base matrix](BASE-PROGRAMS.md) for initial command requirements.

## Awk

All three evaluated providers pass the same eleven actual package-script fixtures
on the Clang-built host binaries. [Build and evidence](../../experiments/awk-reference/README.md)
detail the exact source identities, scope and negative cases. Prioritize mawk's
Clang/musl evaluation, retain One True Awk as an alternative and gawk as the broader
compatibility reference. None is admitted to the native base yet.

Mawk publishes dated archives and a maintained change history; that helps us track
inputs, but it does not prove source authenticity or safety.
[Upstream maintenance and archives](https://invisible-island.net/mawk/).
One True Awk documents a best-effort maintenance policy and Unicode string behavior;
retain both in the support/compatibility review.
[Upstream README](https://github.com/onetrueawk/awk).
Gawk 5.4.0 changed its default regular-expression engine. This is a reason to run
its own regressions and package patterns, not assume identical behavior from an
older gawk result. [Upstream release announcement](https://lists.gnu.org/archive/html/info-gnu/2026-02/msg00011.html).

## tr

Keep GNU tr first in the evaluation order, with BusyBox tr as the alternative.
The immediate package use is deletion of C-locale whitespace; the base also needs
translation and squeeze behavior. GNU documents single-byte locale limitations,
so explicitly use LC_ALL=C for package records. Do not advertise this as Unicode
text transformation. [GNU tr reference](https://www.gnu.org/software/coreutils/manual/coreutils.html).

Before selecting a version: pin coreutils and BusyBox archives/configs; inspect
source, helper libraries, optional features and notices; compile with Clang/musl;
compare whitespace deletion, translation, squeeze, NUL/high bytes, invalid arrays,
short I/O and output failure. Keep Toybox's pending implementation out of this
initial provider selection. No tr binary was built or tested in UL-066's host awk
comparison.

## stty

GNU stty remains the first candidate because it can share a reviewed source and
update process with GNU tr. BusyBox supplies both applets too, so compare actual
feature/closure costs before deciding. Neither binary provides the underlying
Aether terminal service. [BusyBox applet documentation](https://busybox.net/downloads/BusyBox.html).

GNU stty normally controls stdin and offers a saved-state form through -g. Its
saved form excludes window size, so a successful save/restore test must not claim
that every terminal property was restored.
[GNU stty contract](https://www.gnu.org/software/coreutils/manual/html_node/stty-invocation.html).

Required owner-provided tests include granted/denied terminal access, raw/canonical
and echo transitions, unsupported mode preserving state, EOF versus empty input,
normal restoration and stale restoration after session replacement. Use disposable
PTYs on the host and exact delegated device/session authority on Aether. Do not
change the user's terminal to test these cases. No PTY or native mode-change test
ran in this slice. Session-generation protection belongs in the terminal boundary,
not in a stock utility's saved-state string.

## Status and next work

UL-066 remains active. The completed part is source-pinned host awk comparison
and this provider order. Missing: static musl builds/upstream suites, tr/stty exact
source/config/closure comparisons, security-fix review and native acceptance.
UL-016, UL-008 and UL-012 retain trust, terminal and packaging ownership. Independent
review is pending; no new shared standard, source pin upgrade in another project,
package recipe or native ABI is created here.

## Subsequent build checkpoints

Mawk static musl validation is recorded in the awk experiment. The
[pinned tr/stty source and GNU build attempt](../../experiments/tr-stty-reference/README.md)
now identifies BusyBox feature gaps and GNU's missing Linux UAPI header prerequisite
(UL-068). No tr/stty runtime or final provider acceptance yet.
