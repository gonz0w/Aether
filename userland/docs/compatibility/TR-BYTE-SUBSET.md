# Package-script tr byte subset

UL-013/066 candidate profile,2026-09-07. Tested Linux reference only; no native or
pkg-mgr adoption. [Machine-readable forms](tr-byte-subset.json) bind the evidence.
This is a local consumer compatibility description, not a new shared standard.

| ID | Exact arguments after tr | C-locale deletion set |
| --- | --- | --- |
| TR-B01 | -d '[:space:]' | Bytes9,10,11,12,13,32 |
| TR-B02 | -d '\012\040-\176' | LF(byte10) and printable ASCII(bytes32–126) |

For finite input, retain all other bytes in original order, including NUL/high
bytes. Empty input produces empty output. Successful execution must exit0 with
no stderr. Error reporting and complete pipeline cleanup remain separate gates;
a plausible output value cannot substitute for checking failure. This profile
covers only the two literal argument forms, not arbitrary tr syntax or Unicode.

[Ten fresh tests](../evidence/tr-subset-2026-09-07/README.md) pass under both pinned
GNU9.11 and BusyBox1.38.0: every byte and empty input for both forms, plus numeric
whitespace normalization. Passing this subset does not remove BusyBox's four
broader differences or replace GNU as the provisional general comparison choice.
Existing common-suite /dev/full tests cover individual output failure; no fresh
full sibling pipeline/error-path acceptance is claimed here.

The dated source census covers14 pkg-mgr/mk *.sh files and finds10 tr-bearing lines
across6 files. Nine use TR-B01 and one uses TR-B02. sys-init/scripts has no *.sh
files in this scan; that is not evidence of no dynamic/generated utility use.
The textual scan is not a shell parser or exhaustive executable-call analysis.
Hashes bind reviewed files and lines; any relevant caller change invalidates reuse.

Five matching package scripts explicitly export LC_ALL=C. verify-metadata.sh does
not establish it globally; caller inheritance/entry points need owner verification
before claiming profile compliance for every invocation. No sibling source was
changed, executed, messaged or accepted. Consumer-owned integration should pin the
selected binary, establish locale, propagate failures and exercise actual pipelines.

The [UTF-8 finding](../evidence/tr-utf8-2026-09-07/README.md) remains separate:
literal multibyte deletion can produce invalid UTF-8. This byte subset does not
promise character-aware behavior. UL-007/012 own native/pipeline/package integration;
UL-013 owns wider subset requirements; UL-016 trust and new helper review remain.

[Package-owner handoff](../TR-OWNER-HANDOFF.md) now specifies TRI-01–07 for locale,
plausible-output/nonzero-status, unavailable dependency and cleanup integration.
All owner cases are NOT RUN here. It reuses current caller identities and does
not duplicate or modify package machinery.
