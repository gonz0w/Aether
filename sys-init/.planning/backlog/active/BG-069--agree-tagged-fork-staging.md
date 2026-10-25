---
id: BG-069
title: Agree tagged descriptor fork staging and thaw ordering
status: active
created: 2026-10-22
source_type: research-follow-on
area: native
---

Essential BG-067/v1 prerequisite from docs/research/TAGGED-FORK-STAGING.md.
Libc bridge now reports only __aether_fork_stage missing. Current kernel copy
success resumes parent, while pinned ProcessFiles.inherited_child requires parent
frozen through local clone. Resolve that explicit precondition with userland/Aether;
do not assume remote serialization or request a new kernel primitive without proof.

Acceptance: exact versioned stage/owner framing distinguishing old83/64; full tagged
snapshot authority and file/stream clone rules; known refusal/error/thaw mapping,
unknown no-replay/retained obligations; child-only TLS/auxv/context rebind and fresh
304-byte startup/file/channel generations/history; ordering proof and matching
owner/library inputs. No sibling modification/message or approval implied.
Follow-on BG-070 implements/links/qualifies once this exact boundary is supplied.

## 2026-10-22 progress — decision0202

Aether's serialized admission choice and separate serialized-copy17 API resolve
the literal frozen-parent ordering mismatch without changing the old method.
Sys-init selects exact frame69/source-label/no-child refusal rules and prepares
one private admission gate and matching codecs. Six actual-library tests/three
compiling omissions/borrow-reentry denial and exact C frame interoperability pass.
Native stream/copy/readiness/shutdown composition is not complete. New BG-071
requires authoritative read-only file-slot/cloexec validation before native copy;
current API cannot supply it without mutation or a shadow ledger. Preserve earlier
problem text as history; see prototypes/native-filesystem-session/FORK.md.

## 2026-10-22 progress — decision0203

BG-071's pure FILE metadata seam and local mandatory copy preflight are complete:
file-view18 exact current-key presence/cloexec comparison derives from the full
captured map, with no source effect or copy callback on denial. Nine host tests,
six compiling omissions and host/native generic builds pass. Remaining locally
available work: actual stream holdings/source/rights/history capture and native
transaction/handshake/settlement/readiness/shutdown wiring. Aether's actual loader
rejected stage81 for missing PT_TLS; a separately sealed userland real-TLS relink
and actual loader acceptance are required before native shell witness/full fit.
Do not confuse that execution dependency with a blanket implementation blocker.

## 2026-10-22 progress — decision0204

Mandatory stream preflight now checks actual owned SESSION pipe holders/history
and full live console/source fields under the gate. Exact child context-ready
activates existing staged holders before parent success; partial/failing activation
retains obligations and cannot reopen.15 host tests/four compiling omissions/two
borrow denials and host/native library builds pass. The old ABI24 pipe source and
owner remain unchanged; candidate source selection/provenance is explicit.

Corrected TLS85 seal f14badab992cf50de4b3443093ccd4b65aa01b1ba1bcf4fa7447672d26b962d4
and dependency closure verify; our fresh actual unchanged Aether parser accepts
its exact ELF and rejects old stage81/malformed TLS/WX (seven host tests). This
resolves missing TLS input only, not full native execution/fit. Remaining local
owner work: actual holder/copy/refusal/greeting/ready/parent transport composition,
terminal/endpoint/readiness/shutdown and whole fit, then fresh matched native
continued-parent/child/wait/known-refusal/unknown/cleanup/readback acceptance.

## 2026-10-22 progress — decision0205 / placement boundary

Gated capture now closes admission before reading the body and only reserves its
actual decoded sequence after complete validation; partial input/unwind cannot
copy. The bounded exact-header/body/native-channel transport and actual decoder
pass20 host tests/four compiling omissions/strict checks/host+native builds.

Concrete blocking input is now BG-072: native Gate2968 + selected RPC workspace4096
=7064 resident bytes cannot fit the current one4096-byte owner stack page; code is
RO and supervisor allocation denies. Files2208+workspace alone already exceeds it.
See docs/OWNER-PLACEMENT-HANDOFF.md for target LLVM/source proof and the focused
unsent request for8192 private zeroed RW/NX bytes within existing owner backing,
without quota/old-profile changes. FILE/stream/TLS input blockers remain resolved;
full native owner composition resumes with exact producer placement authority,
then complete fit/transaction/settlement/readiness/shutdown/native witnesses.
