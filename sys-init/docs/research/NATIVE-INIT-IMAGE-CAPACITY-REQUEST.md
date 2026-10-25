# Init-compatible image capacity request

2026-09-06; BG-058 / decision 0088. Proposed consumer requirements for the Aether
native producer owner. Decision 0089 queues this request as
[Aether SI-05](../../../.planning/ROADMAP.md#si-05--init-compatible-supervisor-image-capacity).
It remains a request, not an accepted ABI, shared standard or producer implementation.

## Problem and requested decision

Our exclusive conflict guard preserves primary/diagnostic histories and closes
Driver admission on conflict. The best complete layout in the bounded study needs
4528 bytes; the existing init fixture permits 4096. Aether's separate 8192-byte
program profile does not dispatch init operations or supply the init bootstrap
grant. See [the retained comparison](NATIVE-CONFLICT-GUARD-LAYOUT.md).

Please define a separately versioned init-compatible test profile with a bounded
supervisor image capacity, proposed at 8192 bytes. Two pages cover the observed
4528-byte maximum and leave room for still-unqualified guard paths; this is an
experimental fixture allowance, not a distribution or production memory budget.
The producer chooses wire magic, ABI identity and exact contract. Existing
AENIN001/ABI 6 bytes, its 4096-byte limit and existing rejection behavior remain
unchanged. No relabelling as ABI 8 or widening of our live linker is accepted.

## Required producer contract and evidence

- Define worker/supervisor slots, startup registers and caller-bound authority.
  Preserve the init grant and clock/observe/reserve/poll/cancel/release semantics,
  or explicitly version their replacements with a consumer migration mapping.
  A third executable grant cannot substitute for init authority.
- Define bounded envelope lengths, checked arithmetic, reserved fields, exact
  payload length, code pages, tail initialization and stack bounds. Keep code
  immutable RX without writable aliases and the separate stack non-executable.
- Define cleanup and owner-death behavior for every mapped supervisor page and
  retained resource. Preserve terminal identity, generations, pending-wait
  ownership and stop/reclaim semantics. Retain old profile regressions, exits and
  markers; define any new profile completion oracles separately.
- Supply positive evidence of executing an instruction on the second page,
  boundary cases below/at/above the selected limit, malformed/truncated/overflow
  rejection before admission, and mapping/cleanup checks. A successful parse or
  first-page execution alone is insufficient.
- Supply fresh source/tool/input hashes, raw logs, exact expected outcomes and
  a reproducible producer bundle. Preserve historical pins and evidence bytes.

## Consumer acceptance after the producer decision

Record the separately accepted contract and offline producer pin before changing
the harness, linker or adapter. Rebuild and run all 151 current semantic cases
against it, with profile-specific bootstrap/oracle changes reviewed explicitly;
retain the old ABI-6 regression evidence. Add the five proposed conflict guard
cases (two positives and three exact omission controls), then separately qualify
denied construction and closed reoffer. Failed links in 0087/0088 supply no native
semantic coverage. Host acceptance of Held does not establish Driver closure,
physical capacity or retention after guard destruction.

BG-058 remains open until this dependency and its consuming witness are resolved.
PH-05/06 and BG-057 PH-07 retain their separate scope. Exact sys-init lifecycle
algorithms and evidence stay here; Aether owns its native producer contract.
Any future shared engineering rule belongs in Aether-standards through its catalog
and contribution/versioning process, rather than a new local copy of shared rules.


## Delivery and scoped consumer refresh — decision 0090

Aether delivered AENIN002 / ABI 15 with an 8192-byte limit and the specified init
bootstrap/operations. The pinned consumer packet and independent 151-case refresh
are retained in `../evidence/native-init-capacity-consumer-2026-09-06/`. Default
ABI-6 images rebuild identically. This clears the profile dependency; the guard's
five proposed cases and additional construction/reoffer qualification remain open.


Decision 0091 supplies all five requested guard outcomes alongside 151 fresh
regressions under the same ABI-15 producer pin. Largest guard image is 4528 bytes.
This completes the requested capacity/guard consumption slice; the separately
listed construction, reoffer and broader retention/capacity work remain open.
