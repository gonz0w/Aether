# UL-062 host static, RSS, concurrency and transport stress — 2026-09-07

Host clang --analyze and clang-tidy are silent on runner-parse.c,
parser-extended.c and parser-reduce-oracle.c. An isolated null-dereference
canary emits the analyzer diagnostic on both tools. Parser decode RSS stays
under the 32 MiB observational budget (about 4 MiB here). Dirtied 128 MiB mmap
raises ru_maxrss above 64 MiB; an undirtied reserve does not. Eight forked
children decode a valid carrier and reject a reserved byte, all exiting 0. A
hang child hits the 5-second owned-process timeout with complete process-group
cleanup. After parent bootstrap, 256 native_exchange rounds make exactly 3072
channel_raw calls, then invalid size poisons without further traffic. Explicit
UBSan runs pass on Python 3.14.7 and 3.10.21. No production parser or adapter
source, sibling repository or release pin changed.

Darwin rejected setrlimit of RLIMIT_AS and RLIMIT_DATA in pre-plan probes;
RSS checks are getrusage observations, not kernel enforcement. ASan was not
rerun. Native sanitizer compensation remains the existing denial/reclaim
witnesses, not a sanitizer port. Independent review is pending. This does not
close UL-062.

See [PLAN.md](PLAN.md) and [change-review.md](change-review.md). Commands and
recovery are in [EXTENDED.md](../../../experiments/command-runner/EXTENDED.md).
Each attempt retains sources, tool hashes, streams and process receipts.

| Attempt | Result |
| --- | --- |
| extended-host-kzpon2iq | tidy-canary looked only at stderr; incomplete |
| extended-host-_g9923h9 | transport compile used parser -Wmissing-prototypes on native-io.c; incomplete |
| extended-host-oxq_74l1 | Python 3.14.7: pass |
| extended-host-riflosak | Python 3.10.21: pass |
