---
id: BG-073
title: Obtain bounded in-place FILE broker initialization
status: active
created: 2026-10-22
source_type: measured-native-construction-follow-on
area: native
---

Essential BG-070 construction input. New Aether ABI30 mapping and local safe gate
placement resolve BG-072's missing mapping contract, but the sealed opaque
ProcessFiles by-value constructor still exceeds the one-page stack in measured
size builds. Direct size-z reserves6504 bytes before pushes/callees; noninline
callee5328 plus caller2208 does not fix it. Direct opt3 and isolated opt3+size-z
subsets exceed code16384 (32008/19072), before full owner completion. These are
measured build failures, not universal compiler/full-owner impossibility proof.

[Focused local unsent request](../../../docs/BROKER-INITIALIZATION-HANDOFF.md)
asks Aether-userland for additive safe construction directly into caller-owned
MaybeUninit storage, including nested source/ledger fields; explicit partial
failure/actual cleanup/greeting/epoch/lifetime semantics and concrete target frame
qualification. Preserve old APIs/sealed packets/defaults/limits. No sibling write,
message, larger quota, guessed field layout or complex alternate stack/build path.

Acceptance: matching separately sealed producer candidate and strict host/error/
old-API controls; reviewed local direct gate-field integration with one owner and
no live alias; target call-chain and full code/resource fit; then fresh matched
Aether entry/mapping/transaction/readiness/shutdown witnesses under BG-070/072.
Native composition pauses at this selected constructor boundary. Independent
routing/transaction implementation remains sys-init work, not producer acceptance.

## Integrated candidate — 2026-10-22

The separate fs_in_place API is now implemented in userland and consumed by
Owner::connect_in_place in this repository.35 actual broker/process host tests,15
compiling controls,12 default-client tests/eight controls and26 owner host tests
pass with pinned Rust1.98.0. Default process31/13 controls remain covered; the
array-only alternative differs solely inside disabled cfg functions. Concrete
Framed<Endpoints<Native>> boot construction uses192 local bytes plus24 pushes,
resolving the prior6504-byte aggregate reservation for this selection. No complete
peak-stack bound or native acceptance follows.

The required-root native size-z subset remains16544/16384 code bytes. Size-s
requires17360; a simpler typed-array variant requires16720 and a1104-byte local
reservation, so the smaller elementwise constructor is retained. Code-fit blocks
native admission. BG-070 owns remaining complete-owner transaction/routing/entry/
shutdown and code/stack fit under current limits; this story is not fully accepted
until its existing native obligations pass. No quota increase or new guest.

[API/commands](../../../../userland/docs/proposals/FS-BROKER-INIT.md),
[compact system evidence](../../../../docs/evidence/broker-init-2026-10-22/README.md).
## 2026-10-22 comparison follow-up

Decision0208's separately selected unchanged pinned musl byte comparison brings
the former constructor-only roots from16544 to16008. Construction stack behavior
is unchanged and all producer checks still pass. This resolves only that measured
size excess. BG-070's added positive/refusal publication roots need17440/16384;
complete coherent owner and peak stack/native admission remain open. No budget,
producer API, old delivery or pin changes. See root STATE and decision0209.
