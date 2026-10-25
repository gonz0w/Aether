# AF07 read-only transport client — 2026-10-21

UL-007/081/082. [Contract](../../proposals/FS-AF07-CLIENT.md), [pre-code review](review.md).
Sys-init decision0194 now consumes corrected linked ABI29 v2 and prepares startup/
child/wait core; full dispatcher still needs filesystem FD/path/exec translation.
All56 retained sys-init packet members verify; see sys-init-intake.json. No sibling
script/guest executed or sibling acceptance/sign-off inferred.

Eleven host tests and eight compiling semantic omissions pass with actual
Python3.10.21/3.14.7. Rust1.98.0/2021 strict warnings/unsafe denial, default Clippy,
rustfmt and byte-identical native no_std generic-library builds pass. summary.json
binds final runs and hash. Generic-library generation is not monomorphized native
runtime, engine link, stack/heap fit or execution. Tests exercise actual sealed
AF07 service/Owner with synthetic storage over in-memory channels, not OpenZFS.

Coverage includes255-byte/nested component lookup,4096-byte read bodies, EOF/zero
reads, token lifetime/exhaustion, rights/name/offset denial before transfer,
malformed greeting/status/reserved/token/count/body/padding, failed final close,
every missing read-body frame prefix, all lookup send-prefix failures and local
endpoint-close errors. Pinned Framed adapter executes short7-byte transfers,
EAGAIN/wait and every partial greeting prefix. No replay/reconnect/epoch reset.
Both local close outcomes remain explicit; they prove no native reclaim/export.

Eight compiling omissions must fail actual assertion-based tests: ignored epoch,
wrong lookup token, lost retirement, omitted initial/partial read clearing,
ignored body padding, delegated rights widening and token reuse. Results/logs
retain exact argv/environment, input/source/tool hashes, process deadlines and
cleanup. New code is safe allocation-free Rust; no sanitizer or broad native/
POSIX/security/performance/recovery claim is made.

Attempts are retained, including two initial failures. First test provider returned
a requested count past EOF; real Owner correctly returned EIO, fixed by respecting
synthetic file EOF. Next mutation run detected token reuse through unwrap panics,
but the driver's stronger assertion-only oracle rejected the evidence. Added an
explicit successful-admission assertion; no protocol behavior was weakened. Final
current/minimum runs pass all tests and controls. No lint suppression was added.

Source-only five-member delivery:
`build/service-deliveries/filesystem-af07-client-2026-10-21-v1`, manifest SHA256
`050aef4bede9bcaacfc6f07e590a6c1aa4b4d39cb8fc81b3bc0138daea7d367a`.
Unchanged77-member service dependency manifest:
`98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8`.
Old descriptor/client/service/evidence/pin bytes remain fixed. No new native
campaign, lifetime/quota/authority expansion, sibling change/message or install.

Next wire shared descriptions to this client, define exact process/path/binding
translation and immutable executable admission with owners, then full sys-init
integration and Aether assembled native witnesses. The existing descriptor core
is owner-local; this client is not yet its backend. Read-only open or content
hash alone is not immutable executable authorization. Native failed-exec parent/
FD preservation, resource fit/cleanup/fresh boot, packages/Zsh/TTY, independent
reviews and full M3/R1 remain open.

Quality/pins/documentation inventory, actual minimum/current Python syntax and
tracked whitespace checks pass. retention.json binds four exact attempts and
full member hashes/sizes; archives were read back before redundant roots were
removed.58640463 logical build bytes removed,19924687 archive bytes retained;
physical disk reclamation was not measured. Historical builds remain untouched.
