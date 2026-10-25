# Implementing-agent source review

Pre-code scope/simplicity/ownership/test plan is in the existing change review.
Actual review: preflight is source-effect-free until guarded snapshot; reservation
is consumed before transmission and never reused after uncertainty. SENDING and
PARENT prevent completion reentry mid-I/O. Known correlated completion restores
mask/cache and exact boot bytes; partial/unknown closes parent once and exits116.
Negative owner errors paired with positive native copy intentionally fail closed.

Child quarantines before any callback; rejects request sequence/native PID/PPID/
new grant mismatches before borrowing. Real target wrapper verifies old/new auxv
around pinned rebind; host replacement is qualification-only. No old context
finish/abort/leave/close executes. Fresh greeting is fully matched before copied
metadata is discarded and private context initialized. New native pointers and
fresh generation/sequence/close state are explicit. Temporary new-channel guard
metadata is invalidated after transfer without a mask leave or close. Ready send
precedes upstream TID/list repair/application return. Partial ready/new guard
failure closes only new endpoints, records raw results and fail-stops. No local
receipt claims native settlement. Source labels remain an explicit owner proposal.

Actual entry/host private-copy and default libc/frame regressions pass; semantic
omissions exercise quarantine, rebind, correspondence, reconstruction, unknown
retirement, guard transfer and close. Native object/disassembly/full link checks
are separate from host behavior. Old static _DYNAMIC sentinel is checked against
baseline shape/no relocation/dynamic binding, never hidden by a linker ignore flag.
Full resource fit/matching native transaction/owner and reader review remain open.
Prior candidates and sealed evidence retain bytes; no story is marked complete.

Delivery `build/service-deliveries/filesystem-fork-stage-2026-10-22-v1` has81 manifest members; seal
`7923584cb093e2c459ae45468ca1021dd92054e771d2de569ebcee15b3c143fe`. Complete279,256-byte ELF SHA256
`bbad8594bfeab70135a9b153dec88030278dfcfd423c2646103889ba00e21413` matches between final minimum/current qualifications.
New source/checker, old frame/libc contracts/dependency receipts, exact build-plan,
linked artifact and original dash/musl notices retained. No SDK/dash source tree
or owner implementation duplicated; checker snapshots require maintained layout
and pinned predecessor/ABI29 inputs. This is an opt-in client, not a boot kit.

All fourteen exact owned attempts were archived and streaming hash/size readback
checked before removal: 45,587,276 logical bytes removed,
5,210,960 archive bytes retained. Physical reclamation not
measured. Current Python/lzma retention is separate from minimum qualification.
Final quality/syntax/whitespace/source and prior-input verification accompany seal.
