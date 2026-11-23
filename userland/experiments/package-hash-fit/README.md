# Native package hash provider fit

Issue [17](https://github.com/gonz0w/Aether/issues/17#issuecomment-7102531685)
selects the first leaf of unchanged `pkg-mgr/mk/verify-metadata.sh`:
`hash-file /pkg/input`. This experiment measures standalone `dirname` and
`sha256sum` from the existing pinned Toybox 0.8.14 source against the guarded
native musl 1.2.6 SDK. It does not select additional applets.

Before implementation, the expected consumed behavior is `dirname PATH` producing
its parent directory plus newline, and `sha256sum /pkg/input` producing the
64 lowercase hexadecimal digest followed by Toybox's normal filename record.
The unchanged consumer extracts the initial digest. Missing/unreadable input and
output errors must fail truthfully. Target linking, source review and any host
semantic controls will be reported separately from native execution.

Use the existing source route in `sys-init/docs/R1-ZSH-SOURCE.md` to rebuild one
SDK, then generate the two closed standalone configurations and link their actual
target objects. Preserve the upstream algorithm and native syscall transport.
Record source/tool/ELF identities, unresolved symbols, actual parser geometry and
available stack analysis. An unresolved or unsupported runtime dependency is a
result to report, not a reason to add successful stubs.

Forbidden outcomes: guest execution, kernel/Owner/ABI changes, increased caps,
Linux runtime substitution, arbitrary utility expansion, fake syscall providers,
full native package import claims or silently ignored build failures. Generated
source, SDK and objects stay under `userland/build/package-hash-provider` and are
owned temporary outputs. Retain compact commands, hashes and failure summaries;
remove owned generated outputs after the lead has reviewed the measurements.

Run from the repository root after the documented native SDK source build:

```sh
python3 -B userland/experiments/package-hash-fit/build.py \
  --sdk userland/build/package-hash-provider/sdk \
  --archive .deps/source-inputs/toybox-0.8.14.tar.gz \
  --tools-lock .deps/source-tools.json \
  --work userland/build/package-hash-provider/final
```

The archive is the existing Toybox source lock's HTTPS input with SHA-256
`827e4cdfd69f5da973e00e2a59b30b3c9857fb7fae74c362fd0b4f96be7929b0`.
It may be acquired from `https://landley.net/toybox/downloads/toybox-0.8.14.tar.gz`.
The script verifies the archive, supplied tool lock, existing generator sed pin,
and fresh SDK receipt before consumption. It calls the unchanged
`filesystem-service/r1-zsh-source.py` helper builder for the exact package
provider set, then replaces only the application objects at link time.
The measured baseline reproduces the existing 42,904-byte bytecount helper.

Toybox uses the native SDK's `x86_64-linux-musl` compiler/source convention with
only the guarded Aether libc and current helper providers at link time. This
selects the musl header definitions needed by unchanged upstream Toybox. It does
not supply a Linux runtime. The script rejects linked `syscall` instructions.
Provider compilation keeps the existing helper flags; Toybox objects use `-Oz`,
function/data sections and the upstream unsigned-char/no-strict-aliasing settings.
Only one effective standalone applet may remain after preprocessing.

The actual kernel `native_elf.parseApplication`, `native_launch.layout` and
`native_launch.backingPages` inspect both normal and stripped ELFs. Their generic
application geometry acceptance does not approve FILE intake or execution.
Stripping must preserve program headers and TLS bytes. The only allowed loaded
byte differences are ELF section metadata fields in the ELF header, which the
receipt reports explicitly. Local stack frames are filtered to functions that
remain in the linked ELF; they do not prove a complete libc call graph, peak
stack usage, allocator demand or workload fit.

Measured results and the unrun runtime checks are in [receipt.json](receipt.json).
The owning GitHub issue remains the live work record.

The measured candidates are **not selected-ready**:

| Candidate | Linked ELF bytes | Stripped bytes | Kernel backing pages |
| --- | ---: | ---: | ---: |
| dirname | 103144 | 78584 | 42 |
| sha256sum (read-error patch) | 119288 | 92408 | 46 |

Both pass the actual generic application parser/layout checks; both exceed the
current 49152-byte executable FILE intake. Each page count includes the existing
65536-byte loader stack. The largest measured linked C source local frame is
600 bytes for dirname's provider startup and 760 bytes for sha256sum's generic
hash transform. These are local frames, not maximum call-chain or heap usage.

Current helper semantics independently deny the required runtime: pathname open
rejects `/pkg/input`, the stdout FILE policy accepts only the prior `6\n` bytecount
result, and the current executable selection is `/pkg/bytecount`. A future
Owner-managed pipe/descendant/FILE design remains separate work.

Source review also found a correctness blocker in pinned Toybox's builtin hash
path before the local correction: `lib/hash.c` lines359–360 use `i = read(...)` followed by `if (i<1) break`.
A negative read therefore enters digest finalization, and `do_hash` in
`toys/lsb/md5sum.c` prints the digest without an error check. Failed opens and
stdout flush failures do have failure paths. The actual-function witness and scoped correction below address this source
defect. Current native pathname/pipe/intake acceptance remains open. The initial
fit performed no host or guest applet execution.

## Scoped hash read-error correction

Before changing upstream source, reproduce the negative-read case with the actual
pinned `hash.c`, `xwrap.c` and standalone SHA applet. The host harness replaces
only `read` calls in `hash.c` and `xwrap.c` with a controlled read-fault provider;
positive reads use the real host file. It retains upstream `xread`, diagnostics,
`xexit` and digest formatting. No hash algorithm or native syscall is mirrored.

The reproduction command is:

```sh
python3 -B userland/experiments/package-hash-fit/check-read-error.py \
  --archive .deps/source-inputs/toybox-0.8.14.tar.gz \
  --generated userland/build/package-hash-provider/final/sha256sum/toybox-0.8.14/generated \
  --tools-lock .deps/source-tools.json \
  --work userland/build/package-hash-provider/read-error-pristine --pristine-only
```

Expected controls: `abcdef` and true EOF retain correct digest/status; pristine
initial EIO and partial data followed by EIO incorrectly complete a digest with
status0. After the single selected builtin read-to-`xread` patch, both faults
must exit nonzero without a completed digest. A scoped fresh SHA target link,
actual parser and stripped-byte comparison must follow. Reuse the existing SDK.

Forbidden outcomes include changing the SHA algorithm, applying the patch to
other applets or the disabled LIBCRYPTO branch, changing archive pins, fabricating
native providers, adding an error framework, broad utility/host-port work, guest
execution or treating the host fault double as native POSIX evidence.

The pristine reproduction passed before the patch was authored: initial EIO
returned status0 with the empty-file digest; three real bytes (`abc`) followed
by EIO returned status0 with the digest for that truncated input. The local
[patch](sha256-read-error.patch) changes only the builtin loop's `read` call to
upstream `xread`. The builder checks archive, before-source, patch and after-source
hashes, applies it only for the selected SHA source tree, and rejects LIBCRYPTO.
The original archive, dirname and other experiments remain unchanged.

The final focused commands are:

```sh
python3 -B userland/experiments/package-hash-fit/check-read-error.py \
  --archive .deps/source-inputs/toybox-0.8.14.tar.gz \
  --generated userland/build/package-hash-provider/final/sha256sum/toybox-0.8.14/generated \
  --tools-lock .deps/source-tools.json \
  --work userland/build/package-hash-provider/read-error-checked

python3 -B userland/experiments/package-hash-fit/build.py \
  --sdk userland/build/package-hash-provider/sdk \
  --archive .deps/source-inputs/toybox-0.8.14.tar.gz \
  --tools-lock .deps/source-tools.json \
  --work userland/build/package-hash-provider/sha-patched --applet sha256sum
```

All eight final host cases pass. Both variants preserve exact `abcdef` and
empty-file digests with status0. Both patched error cases return status1 with
empty stdout and `sha256sum: xread: Input/output error` on stderr. The check
compiles the actual standalone applet, hash, xread and diagnostic/finalization
sources; only the host read-fault provider is substituted. This establishes
source error-path behavior, not native transport/diagnostic acceptance.

The affected SHA target was rebuilt against the same SDK and unchanged helper
providers. Normal and stripped candidates pass the actual kernel parser and
layout checks, without undefined symbols or `syscall` instructions. The stripped
SHA grows32 bytes and one backing page at a segment boundary. No cap was raised.
The earlier dirname measurements are retained without repeating that build.
