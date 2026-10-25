# Actual dash over serial — 2026-09-11

Actual dash runs with `-i +m`, prints `$ ` and consumes a host-sent
`/next; exit $?` command. Its replacement child reads a later host byte through
inherited stdin, exits72, and dash waits and exits72. Two sessions share a single
Rust UART backend. The backend then exits17; a fresh worker in its old slot must
be denied the still-open UART grant and exit17. All six terminal/reclaim outcomes
are required, with16 stdin bytes,24 stdout bytes and2 stderr prompt bytes per
session. The positive transcript contains two actual prompts and two host command/
child-input exchanges. Bootstrap, shell and child lack direct UART authority.

This is a bounded interactive execution proof in the kernel harness. Sys-init,
persistent executable loading and package management are not assembled into this
image. The owner accepts two fixed /next sessions with expected exit72 and finite
watchdogs; it is not a general shell image with indefinite human think time. Echo,
line editing, TTY/session policy, job control, pipelines/redirection, cancellation
and backend fault recovery remain separate work. No new kernel ABI, released pin,
installed SDK or sibling repository change is involved.

## Qualification

| Check | Result |
| --- | --- |
| Complete connections suite | 238 cases pass, including three serial dash cases |
| Launch regression | Five cases pass |
| Console ABI18 regression | Two cases pass |
| Host/harness/workflow/offline pins | `zig build test` passes |
| Rust/C format, workflow, standards, experience, whitespace | Pass; commands in final-checks.json |
| Simplicity extension | Pinned SHA256SUMS and four files verified |

The `-serial-tee` case keeps the original input object and requires the pipe-call
failure and owner2140 with zero reclaims and no child admission. `-serial-wrong`
sends b to the child and requires child224/owner2130 with zero reclaims. Generic
panic or timeout does not pass either oracle. Existing ordinary/explicit dash
commands, descriptor, wait, pending-input and recovery controls remain regressions.

[Attempts](attempts.md) preserves both failed rounds. The first revealed the
stdin tee/pipe dependency after reaching the prompt. The second executed the child
and returned both72, then correctly rejected my mistaken input-byte expectation:
the15-byte script plus child byte requires16. The final run changes that assertion
and preserves output/lifecycle requirements. All selected sources were frozen per
run; final documentation updates are distinguished from frozen implementation.

## Native input configuration

The pinned input.c matches the prior main-configuration reference source hash for
dash0.5.13.5. `AETHER_NATIVE_NO_TEE` returns EINVAL from stdin_tee before pipe
allocation, selecting the unchanged upstream preadfd one-byte fallback. This is
necessary because UART truthfully provides neither canonical TTY nor seekable
file semantics. It avoids consuming a future child's stdin and does not claim
pipe support. Parser, evaluator, flush behavior and wait remain upstream.

`build.py` uses the hash-verified headers/config/SDK includes/tools from the earlier
main-configuration snapshot. Original and patched-disabled relocation disassembly
match; enabled code adds no imports. The prior snapshot's source-authentication
and generated-header limitations remain; this is not fresh upstream authentication.
The original source, exact patch, native source, COPYING.dash and build outputs are
retained. `user/native-command/dash-input-native/input.o` is a hash-pinned producer
candidate used only for these native serial links. Previous main/jobs candidates
and the immutable upstream object inventory remain unchanged. Third-party terms
are preserved. Independent SDK/userland review and adoption are still required.

## Ownership and resources

[Plan](plan.md) and [configuration review](configuration-review.md) record scope,
forbidden outcomes, SE01–05, affected owners, unsafe obligations and test selection.
AENMX003/ABI18 supplies the unchanged one-way UART handoff. The backend exposes
three logical streams through the existing32-byte private channel frames. Only
a canonical EAGAIN permits a read retry; malformed/incomplete replies retain the
existing failure behavior. There is no new kernel queue or escaping user pointer.
UART spans are synchronous borrowed stack slices, maximum16 bytes per request.

One all-zero reset request may reopen logical streams after all three close and
before the second session. Old shell/child domains are reclaimed before new
references are published. This narrow reset belongs to the private experiment,
not a shared service-restart or TTY API. The backend keeps its grant until exit;
generation binding, rather than closing the grant, denies the final replacement.
Six channels, three slots, generation limits,16 KiB owner mapping and4 KiB owner
stack remain unchanged. The console-only pre-fork frame allowance is64 to cover
one-byte input plus startup; old profiles retain16. Peak stack and performance
baselines are not measured by these functional tests.

## Evidence and follow-up

`*-timing.json` records exact commands, times, durations and return codes.
`*-results.json` records cases and source/tool hashes. `dash-exchange.json` records
the host's command and child-input bytes. The copied serial transcripts show exact
terminal and rejection contexts. `run-sources.*` preserves frozen inputs;
`sources.*` adds final progress/reference updates. `change.patch` compares the
previous pending-read packet. `artifacts.json` indexes the read-back-verified
archive. Each failed attempt retains its own source and artifact archives.
`qualification.json` records counts and owner size; `manifest.json` seals this
packet. `cleanup.json` records hash-verified removal of superseded unpacked outputs
while keeping their archives and the latest target output directories.

Next review the native input candidate with SDK/userland owners, extend the bounded
session/command lifecycle, then compose sys-init and persistent executable loading.
This packet is producer evidence, not independent consumer acceptance or R1 release
approval. No sibling repository was modified or messaged by this work.

The final snapshot contains255 source files and4,311 target artifacts. Maximum
compiled owner size is9,528 bytes, within the existing16 KiB mapping. Verified
cleanup removed 2.93 GiB of superseded unpacked outputs.
Recorded helper scripts are audit artifacts; do not rerun them inside this sealed
packet. Use the live documented commands with a fresh evidence destination.
