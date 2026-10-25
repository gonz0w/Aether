# Typed C file facade / live Rust host integration — 2026-10-21

UL-007/081/082: the [file-only C facade](../../proposals/FS-FD-FACADE.md) supplies
component-open/read/seek/dup/close/cloexec over the exact selected C transport.
Every call takes an explicit trusted client; private negative errno is distinct
from libc -1/errno. No POSIX symbol interposition, local FD ledger or implicit
file/pipe/console route. Read output is copied only after complete validated reply;
error/EOF and bytes beyond short results preserve the caller's old buffer.

Actual Python3.10.21/3.14.7 each pass74 live host cases/six compiling semantic
omissions. The C facade/client sends actual requests over nonblocking host OS pipes
to the real Rust handler/process policy/AF07 service, which uses synthetic storage.
Rust2021/default Clippy/warnings/unsafe denial/rustfmt and strict C17 diagnostics/
format/UBSan pass. There is no new native object, ELF link, trap/endpoint/OpenZFS,
complete memory fit or shell execution claim. The previous client replay remains
separate unchanged evidence; these cases actually invoke the Rust server.

The twelve-member source-only handoff at
`build/service-deliveries/filesystem-fd-facade-2026-10-21-v1` has manifest seal
`695b758f7d37547ad7ee14f01f0fbfe68cb73549aa69029cc612411b2c5260ce`.
It includes facade/host test sources, exact C dependency/codec and synthetic
fixture, license/contract/dependency identities. Rust libraries remain separately
pinned source dependencies. No native image, SDK or live engine is copied/selected.

Cases cover happy/bytewise FD operations/shared offsets/final alias close,
local no-I/O denials, wrong response generation,4096-byte read/907-byte EOF
remainder, read denial followed by healthy read at unchanged offset, dirty padding,
AF07 body/count/close faults and all64 incomplete padded reply prefixes. The
happy path checks actual explicit EOF behavior, not an assumed cached shortcut.
Caller guard bytes, source/request counters, raw once-only endpoint closure and
one backend drop are independent success oracles. All injected loss cases retire
without replay. C process wait success and outer owned-group cleanup are checked.

Six omission binaries must trigger specific C assertions and failed child status
in Rust: masking semantic errno, omitted data copy, overwriting unused tail,
wrong signed seek origin, replacing close with flag change and masking retired
transport. Compilation, sanitizer crash, timeout or generic Rust failure cannot
pass these controls. Raw source/checker/tool/binary/command/environment/log and
cleanup receipts appear in the retained attempts.

Inputs are verified before use: complete9-member C-client/20-member wire/77-member
service manifests; exact source snapshots; compiler/formatter/native Rust library
pins; LLVM resource headers;99-header host C SDK closure; UBSan runtime and owned
process helper. Source/header/runtime pins recheck after execution. Each compile
is bounded to60s, live suite30s, streams16MiB, clean PATH/LC_ALL/TMPDIR under build/.
The C adapter maps host EAGAIN/EWOULDBLOCK to private -11 and uses1000ms poll waits;
this is host test transport, not a native deadline/scheduler qualification.

Retained failures: initial rustfmt inline-module path preparation error (source/
result recorded in format-setup/); first owned live run51z4opwh expected three
backend reads, but explicit nonzero-length EOF is a fourth actual read under the
existing contract. Corrected only that host oracle; C facade/dependencies stayed
unchanged. Final current qhzp638e and minimum t9d8kirl pass. Every owned attempt,
including failed runs/mutation binaries, is preserved with source/checker pins in
the verified streaming retention archive before exact redundant roots were removed.
See retention.json for full file/byte accounting; physical reclamation not measured.

[Review](review.md), summary.json, candidate.json, final-source.json, raw quality
streams and SHA256SUMS bind scope/evidence. Earlier dependency qualification is
reused only for exact unchanged bytes in its original layer. The local quality
gate is structure/pin validation; independent owner/reader review remains pending.
No sibling edits/messages, new guests, changed limits/pins, real-prefix install,
release/SDK promotion or complete UL-007/081/082/M3/R1 acceptance.

Next is explicit shell startup/file/pipe/console FD routing under an exact consuming
contract, native-copy/failed-exec parent/FD preservation, immutable executable
admission and measured full workspace/code/stack/heap/backing/channel fit. Sys-init
owns complete matched dispatcher/readiness/shutdown; Aether owns native command/
error/cleanup/fresh-boot witnesses. Packages/Zsh/TTY and broader POSIX remain open.
