# UL-066 static stty speed-failure witness

Three Linux reference cases pass with the corrected emulator and private static
link-time fixtures. The original candidate is unchanged. A baseline relink is
byte-identical to its receipt-pinned ELF, SHA256
152165b4edc53b40acfeeee9eaf3f83a7db32bcbcfdd35f403b1609a0756cb14.
[Build](build-final/summary.json), [runtime](runtime-final/summary.json),
[raw results](runtime-final/guest.stdout), [verification](verification.json).

| Fixture | Exit | Wrapper calls | Terminal observation |
| --- | --- | --- | --- |
| Original-equivalent baseline | 0 | 0 | Speed settings change |
| cfsetispeed returns EINVAL | 1 | 1 | Settings unchanged |
| Wrapper calls real cfsetispeed | 0 | 2 | Speed settings change |

The failure emits exactly the interception marker followed by
`stty: unsupported ispeed '9600'` and newline. There is no stdout. Pass-through
emits exactly two markers: GNU apply_settings runs once with checking=true and
once with checking=false. The failing wrapper exits during validation, before
settings are applied. This tests the application's libc-error handling, not a
kernel ioctl denial or a failure after successful validation.

All three PTYs restore exact initial termios before endpoints close. Process
cleanup completes and the owned container is observed absent. The first runtime
attempt incorrectly expected one pass-through marker; its unchanged successful
operation and failed oracle remain [retained](runtime-first/guest.stdout). Source
inspection justified the exact two-marker correction; all three cases were rerun.

The first build's inspection used all undefined symbols and found local _DYNAMIC.
Its baseline ELF already matched the original exactly. Using the original build's
external-undefined-symbol check passes. [Failed inspection](build-first/summary.json)
is retained; no linker flag or binary content was changed for this correction.
Final builds have no external undefined symbols or interpreter. Clang21.1.8 and
lld, SDK bytes and linked objects/archives are pinned in the build receipt.
Commands, target flags and input hashes are retained. [Plan](SPEED-PLAN.md),
[C format](format.log), [Python syntax](syntax.log), [quality](quality.log).

Upstream bad-speed.sh remains NOT RUN because its LD_PRELOAD mechanism does not
intercept a static ELF. This separate --wrap witness covers its intended caller
failure boundary without calling the upstream script executed. No production
patch, native acceptance, source-trust or complete POSIX claim follows. Fixtures
remain private experiments; third-party source terms are unchanged.

The retained package inputs do not include the missing ISO-8859-1 locale data.
Next: qualify the candidate's locale support and acquire/pin suitable test-only
locale inputs if needed, preserving unavailable-locale skips. UL-066 remains
active for that coverage, provider/source review and new helper review; UL-069
stays closed. Legacy/range helper reviews are also still pending.
