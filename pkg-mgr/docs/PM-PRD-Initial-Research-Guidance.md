# Package research for Aether

Maintainer decision, 2026-10-22: pkg-mgr is an Aether-only component in this
repository. The original cross-OS research mandate is retired, including Linux/
BSD product support, per-OS sandbox adapters and platform qualification campaigns.

Use [.planning/PROJECT](../.planning/PROJECT.md), [architecture](ARCHITECTURE.md)
and [roadmap](../.planning/ROADMAP.md) for current requirements. Study other package
managers only to solve a concrete Aether problem: readable recipes, explicit build/
install boundaries, trustworthy inputs and recoverable package state. POSIX shell
and make remain implementation choices, not a promise of other-OS support.

The [original research prompt](archive/2026-10-22-cross-os-research.md) is historical
reference only. It does not authorize portability work or replace current decisions.
