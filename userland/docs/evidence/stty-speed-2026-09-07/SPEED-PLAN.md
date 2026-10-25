# UL-066 static stty speed-failure witness

The pinned upstream bad-speed.sh interposes cfsetispeed via LD_PRELOAD, unavailable
for the static candidate. Build separate link-time --wrap=cfsetispeed fixtures from
retained GNU objects and verified musl SDK. Baseline relink must match the candidate
byte-for-byte before fixtures are consumed. No source/candidate mutation, install,
shared boundary or native acceptance. Upstream bad-speed.sh stays NOT RUN.

New BSD-2-Clause C17 wrapper emits a marker then either returns EINVAL or calls
__real_cfsetispeed. Clang21.1.8/lld pinned by original build receipt, strict warnings,
static Linux x86-64, noexecstack/no undefineds. Pin every consumed object/archive,
SDK and tool before build; capture all commands and ELF headers/undefined-symbol
checks. GNU/libc retain upstream notices; fixture is not a distributable provider.

Run baseline, injected failure and pass-through on separate owned PTYs with
ispeed9600. Require baseline/pass-through exit0, injection exit1 with exact marker
and unsupported-ispeed diagnostic. Both wrappers must show interception. Failure
must leave host termios unchanged; successful controls must change speed settings.
Always independently restore/read back termios before closing. All process and
container cleanup required. Reuse approved corrected QEMU/runtime closure and
unchanged owned helpers, no network/capabilities,uid65534,512 MiB,32 PIDs,120-second
container,10-second children. Host compile/link commands each60 seconds.

Quality CP/C/TD/TE and Foundations O/I/E apply. Python3.10+ host standard library.
Run C format/syntax warnings, actual three-case witness and quality gate; retain
failures/source hashes. Technical/reader review pending. This witnesses caller
handling of an injected libc failure, not a kernel speed failure, LD_PRELOAD or
native support. Locale requires separately pinned locale inputs and compatible
candidate semantics; unavailable ISO branch remains NOT RUN.
