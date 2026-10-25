# Live C scratch descriptors — 2026-09-14

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#live-c-scratch-descriptor-selection)
connects the private C open adapter to the Rust owner gateway on an authenticated
native connection. The existing stream bootstrap is followed by AESFD001. Five
bindings are enabled only in this profile, explicitly excluding old file/pipe/null
selection. No kernel ABI, quota, additional worker or public SDK change.

The actual C client opens a writer, duplicates it with F_DUPFD_CLOEXEC, writes A,
closes the first alias and writes B through the survivor. It then opens two readers,
checks independent offsets, CLOEXEC flags and EOF, and closes both. The owner
requires zero holders/no poison, independently reads exactly AB and EOF, closes
that description, and acknowledges completion. Only then does the original copy
fixture proceed: source71/child72/backend17 twice and six reclaims. This tests
live native C descriptors, not descriptors surviving application fork or exec.

Three focused cases and all331 connections cases pass. Deliberate offset loss and
CLOEXEC loss each produce client252, owner1950 and zero reclaims. Neither control
passes from timeout or arbitrary panic. Focus/full traces require exact terminals.
No unexpected failure occurred. The final suite took1032.49seconds, within the1800
review ceiling, on275 unchanged frozen inputs. Host tests pass (104 Python tests),
along with formatting, workflow and offline standards/simplicity verification.

The positive owner is9520bytes and client ELF22872bytes; the CLOEXEC-loss client
is22856bytes. Existing four-page owner and loader limits are unchanged. No scheduler
or kernel change required a scheduler rerun. The legacy transport keeps its existing
compact formatting; only scoped preprocessor guards changed. Other touched C and
Rust files pass the pinned format checks. Compatibility.json compares existing
ELF/raw artifacts rather than assuming identity from compile-time selection.

All scratch descriptors close before the strict frozen copy-table check. Metadata
is cleared only for already-closed temporary FDs under the existing signal mask
guard; the extra bindings must be empty. Live scratch fork/exec tables, CLOEXEC
holder removal at exec and unchanged dash fd-leak/redirection scripts remain open.
Scratch close-EIO now selects poisoning rather than the legacy stream-consumed
rule, but direct injected close-EIO and confirmed-stop recovery are not qualified
here. Matching command-runner evidence, independent consumer/public SDK acceptance,
persistence and R1 assembly remain open. Siblings and released pins are unchanged.

Sources, commands, results, SDK/tool identity, binaries and serial logs are retained.
Both generated target trees are archived, read back member by member and compared
to originals before removing their exact duplicates. Cleanup.json records paths,
counts and bytes. The captured scripts record this run; fresh runs must not
modify this sealed packet. Original work is BSD-2-Clause.
