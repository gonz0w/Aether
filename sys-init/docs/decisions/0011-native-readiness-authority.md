# 0011: Test caller-local readiness authority

Accepted 2026-09-05 for BG-032/BG-040. The frozen BG-055 kernel's
kernel/arch/x86_64/native_c.zig supervision dispatch and NATIVE-SUPERVISION.md
operations 0x20000–0x20009 are the experiment reference. Worker-local notification
and generation queries reject supervisor callers with -13 before inspecting
arguments. Control operations reject worker callers with -13 before lookup.
Notification arguments are unused; they do not name a recipient. Repeated local
notifications retain the same boolean history. No delegation API exists here.

Add an opt-in authority worker which checks denied control calls before its
output rendezvous. Exercise zero, factory-shaped and malformed holder/argument
values for launch, status, reclaim, legacy output, completion, stop, input and
stream reads. Any unexpected result exits before rendezvous. These are guessed
values, not transferred capabilities or a complete peer-isolation proof.

The supervisor tests denied notification/generation queries before launch, while
live, after terminal and after reclaim, using zero/factory/current/stale values.
Observe unchanged status after misuse. Generation one exits without notification;
generation two notifies twice with ignored nonzero arguments then exits, retaining
only its own readiness. Keep output/EOF, reclaim and stale-operation assertions.
A policy expecting supervisor notification success must reject at assertion 501;
omitted-zeroing must reject independently. Preserve prior fixture bytes.

Retain source/link inputs and execution evidence. Scope is BSP-only native
conformance, not POSIX, delegated readiness, hostile SDK provenance, production
language selection, supervisor recovery or cross-core authority. Existing shared
standards remain unchanged; future shared rules belong in Aether-standards.
