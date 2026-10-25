# UL-066 candidate locale boundary

Ten Linux reference observations pass: five locale-probe executions and five
pinned GNU tr executions. [Build](build/summary.json), [runtime](runtime/summary.json),
[raw output](runtime/guest.stdout). The probe uses the candidate's exact verified
static musl SDK and pinned Clang21.1.8/lld, with no external undefined symbols or
interpreter. Candidate ELF and SDK bytes remain unchanged.

| Requested LC_ALL | setlocale accepted | Candidate CODESET | MB_CUR_MAX |
| --- | --- | --- | --- |
| C | Yes | ASCII | 1 |
| POSIX | Yes | ASCII | 1 |
| C.UTF-8 | Yes | UTF-8 | 4 |
| en_US.ISO-8859-1 | Yes | UTF-8 | 4 |
| aether_missing_locale | Yes | UTF-8 | 4 |

In all five cases byte0xe9 is not classified alphabetic and toupper leaves it
unchanged. GNU tr translates ASCII AZ to az and preserves the supplied0xe9/0xc9
bytes. These narrow observations do not qualify multibyte Unicode translation,
all locale operations or wide-character classification.

The [archive-verified source audit](source-audit.json) explains the result:
locale_map.c preserves non-built-in locale names with a fallback map;
langinfo.c reports ASCII or UTF-8; byte isalpha is ASCII-only. Relevant musl
sources and COPYRIGHT are retained unchanged under [musl](musl/). An accepted
locale name is not evidence of its requested encoding.

The upstream ISO-8859-1 conditional branch remains NOT RUN for this candidate.
This is a candidate encoding limitation, not merely absent host locale data.
Installing glibc locale data or spoofing the host locale command would not prove
that the musl-linked tr exercises ISO-8859-1 semantics. No such installation or
forced prerequisite was performed. The earlier missing-data interpretation is
superseded by these candidate measurements, with prior evidence preserved.

All ten commands have exact argv/environment/stdout/stderr receipts and complete
process cleanup; the container is confirmed absent. [Plan](LOCALE-PLAN.md),
[format](format.log), [syntax](syntax.log), [quality](quality.log). New helpers are
BSD-2-Clause; source licenses remain unchanged. No shared standards, native
runtime, source-trust or POSIX certification is promoted.

Next UL-066: consolidate provider selection/coverage limits for review. Retain
C-locale GNU evidence, four BusyBox comparison differences, unsupported ISO
profile and separately scoped static-speed witness. Any requirement for true
ISO-8859-1 needs an explicit candidate/libc decision; UTF-8 behavior needs its own
cases. New legacy/range/speed/locale helper review remains pending.
