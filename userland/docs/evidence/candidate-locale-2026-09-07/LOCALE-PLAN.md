# UL-066 candidate locale qualification

Verify musl1.2.6 locale behavior before attempting the unavailable GNU ISO-8859-1
branch. Pinned locale_map.c accepts names with fallback maps; langinfo.c reports
ASCII or UTF-8; byte isalpha is ASCII-only. Host locale availability cannot prove
candidate encoding. No new locale package, shared contract or production change.

Build a private C17 static probe against the same verified SDK/tools as stty.
Observe setlocale(LC_ALL, ""), CODESET, MB_CUR_MAX and byte0xe9 classification and
uppercase under C,POSIX,C.UTF-8,en_US.ISO-8859-1 and an invented locale-name control.
Require acceptance but ASCII/1 for C/POSIX and UTF-8/4 otherwise; byte0xe9 is not
alphabetic and uppercases unchanged. Test pinned GNU tr upper-to-lower on ASCII
plus high bytes under each environment; require exact ASCII-only translation.
Five probe runs plus five tr runs; success does not establish actual named locale
support. The ISO prerequisite remains false unless CODESET really matches it.

Quality CP/C/TD/TE and local Foundations O/I/E apply. BSD-2-Clause original code,
upstream terms unchanged. Verify source archive/files, SDK/tool hashes and static
ELF closure. Reuse owned helpers,60-second build commands,10-second guest commands,
120-second offline container,512 MiB,32 PIDs,uid65534,no capabilities,read-only inputs.
Pin and capture all argv/env/outputs, all attempts, process cleanup/container absence.
Run C format, strict warnings, Python syntax, ten live observations and quality.
Review pending. No native, ISO single-byte, locale-wide or POSIX claim follows.
