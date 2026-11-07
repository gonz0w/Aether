# Zsh home working directory

Owning work: [issue162](https://github.com/gonz0w/Aether/issues/162).
[Approved proposal](https://github.com/gonz0w/Aether/issues/162#issuecomment-6713417824)
and [decision](https://github.com/gonz0w/Aether/issues/162#issuecomment-6713444434).
The guarded QEMU pair passed: unchanged160 writer39.834s/61 requests and new162
cold reader26.895s/83 requests, with228/216 known once-only foreground PTY bytes.
Real physical paths/PWD, relative profile bytes, root denial, returned prompts,
normal exit/export/MODE0/two reclaims/halt and known original-host cleanup pass.
This qualifies the fixed navigation workload; review/delivery is in the owning
issue and does not qualify generic paths, inheritance or assembled R1.

## Selected interface

The default-off cold-reader-only `native_zsh_home_cwd` composition requires the
complete login-startup/home-redirection reader/cold-reopen/file-exec/idle/operator
profile and matched C `AEFD_ZSH_HOME_CWD_BINDINGS`. Keep the same login argv/env,
initial actual cwd `/` and fixed prompt. Rust retains permanent ROOT3/HOME15;
one parent-local selector identifies those held directories without forwarding
namespace authority to Zsh. No global CWD table or extra handle is created.

Before a successful change, existing Client directory_path observes the selected
held directory and must return its actual canonical `/` or `/home`. GETCWD also
queries the held object. Known failure preserves the old selection; malformed,
unknown or failed reply delivery cannot resume a caller with uncertain CWD.
Stat remains unsupported. Ordinary upstream cd tolerates that failure and uses
its real getcwd fallback; fresh linked-route inspection is an acceptance gate.

Only matched AEFP0007 carries this composition. Existing64-byte framing and4096
workspace remain. CHDIR13 takes args `{0,length,0,0}` and one padded64-byte frame
with exactly `/` or `/home`, length1 or5, zero padding; success result0/body0.
GETCWD9 takes zero args/no body and returns result0/body2 or6, actual NUL-terminated
physical path with zero padding. Opcode7 remains reserved; ACCESS8/DIRECTORY10
retain their semantics. Old6 and root2 APIs remain unchanged; no negotiation.

C routes selected chdir through its guarded FILE transaction and checked reply.
Selected getcwd handles the actual required size, including NUL, with existing
NULL/allocation/pointer/overlap/errno conventions and no partial output on error.
No raw kernel chdir or fabricated successful stat is added. CHDIR is parent-only,
after settled startup READ with no active profile I/O/pending reply. Unsupported,
child, stale, malformed and busy requests cannot expose a CWD change.

## Relative read and lifecycle

OPEN1 additionally admits literal `.zprofile` only for parent READ at held HOME,
using the actual HOME lookup. At ROOT it returns EACCES without searching or
claiming ENOENT. Other relative paths/create/write remain denied. Absolute
`/home/.zprofile` is retained for validated automatic startup.

An authorized phase7 reread enters read-ready5 and clears its latest per-read
count/description before lookup. A failed admitted open cannot inherit old
completion. Root-relative denial precedes this transition and preserves7/CWD.
Only one live description is admitted; aliases share offset. Full16-byte read,
last-alias close8 and known reply delivery7 are required again for healthy finish.
Never reset sequence/token/quota or enter create/write phases0–4. New profile
fork is refused before native effects; child CWD/profile inheritance is denied.
Old profiles keep their external-command behavior. The unused helper closes normally.

## Fixed qualification

One fresh unchanged160 writer provisions the same16-byte profile with its existing
228-byte workload and exact9 mutations. One new cold reader uses that exact known-
stopped successful disk, exact0 mutations, with separately bound differing parent/
helper/Owner artifacts and unchanged filesystem executable/terminfo. No other
writer or consumed/failed disk may satisfy this association.

The new216-byte cold workload checks real `cd /home`, standalone physical `/home`,
matching PWD/PID, relative profile bytes, return to `/` with physical path and PWD,
a denied root-relative read preserving the shell, returned prompts and exit0.
Both boots require normal parent/engine, unused-helper close, export/MODE0/two
reclaims/halt/PASS and known original QEMU/Screen/RPC/display cleanup. Logical
cold0 does not imply physically unchanged OpenZFS bookkeeping.

Existing limits remain: Owner81920 RX/Runtime4096/workspace4096/12280 usable stack/
128 backing pages, app/helper384 and engine2048 pages,96 requests/9 mutations,
6000/24000/30000 ticks,330/360/9 seconds,first prompt60 seconds,71-byte max input
stage and64KiB UART. Stop/replan on overflow. Fresh affected fits and separate
review precede the guarded pair; focused delivery needs success and required CI
while141 stays open. No generic paths/stat/symlinks, child CWD inheritance,
authentication, indefinite session, packages or assembled R1 claim follows.
