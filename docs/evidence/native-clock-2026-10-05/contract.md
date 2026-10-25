# Before-code native clock/deadline contract

SI-01/R1-03: enable a small BSP-only q35 HPET source plus absolute monotonic
compare/park/wake, preserving all delivered-tick ABI behavior. Native-clock is
opt-in and requires native memory/threads/pair. No default SDK, sibling, released
standard pin, quota, production OpenZFS startup or UTC/cross-core claim changes.

Producer Aether supplies native authority/hardware/scheduler. Userland owns POSIX
clock/sleep/condition policy and maintained SDK adoption. Sys-init policy and
pkg-mgr installation stay separate. This is the next clock prerequisite, not full
condition-variable, signal interruption, UTC or complete-engine implementation.

Source: validate q35 host bridge and HPET 64-bit capability/10ns reported period,
no existing enabled HPET/comparator/legacy replacement ownership. Only fixed q35
0xfed00000 is supported; general ACPI discovery/physical/TSC calibration deferred.
Map one uncached supervisor RW/NX device page via two reserved BSP-owned tables,
using a checked boot-table HHDM mapping and otherwise empty kernel PDP slot509.
No user MMIO mapping or pointer/physical address returned. Enable main counter
without comparator/legacy IRQ changes. Ordered bounded high-low-high reads detect
low-word rollover; reject full wrap/regression, stopped/unavailable source and
signed64 nanosecond overflow. Epoch is successful source initialization within
this boot; floor femtoseconds/1e6; q35 resolution10ns. Period validation/scaling
is not empirical physical accuracy calibration or host wall-clock time.

New private thread-cap operations:0x2800f reads monotonic nanoseconds, only clock
selector0 and zero other fields;0x28010 compares a caller-owned RW aligned32-bit
word and atomically parks to absolute ns deadline (at most1s ahead). Authority
first; reserved/word checks before effects. Expected mismatch -11, already expired
-110, bounds -22, bad pointer -14, unavailable -38, source failure -5/overflow -75.
Wait records retain clock domain; legacy tick registrations unchanged. Timeout
wins over simultaneous wake, remaining absolute deadline survives requeue. Wait
pins remain until confirmed completion/teardown. Complete read error wakes with
error, never timeout/success. Return elapsed in RDX in that wait's units. No new
queue/allocation/global mutable authority; per-core bounded context scan remains.

Tests: conversion/capability/regression/overflow/rollover and mixed-clock wait,
expiration/mismatch/requeue/source failure/cleanup models. Actual q35 native
reads progress with unchanged delivered ticks; real100/200ms absolute parks retain
memory/TLS/yield/output and actual idle scheduler witness. Disabled, bad authority,
fields/pointers, MMIO fault, missing HPET and deliberate tick/early-wait controls
must reject exact semantic oracles. Ordinary wait/pair/pthread and selected memory/
backing/mask regressions remain unchanged. Full host/pins/workflow and formats.
Freeze all code/tools during qualification; retain failures and measured timestamps,
QEMU30s/3s teardown and per-build180s. Archive/read back before owned-only cleanup.

Unsafe: trusted bootstrap validates each dereferenced table page against usable/
bootloader memory entries and checked HHDM addition; MMIO access is volatile ordered
kernel-only and serialized IF=0. No user buffer passed to hardware. Firmware and
QEMU remain trusted. Shared read-only table configuration/BSP hardware ownership
is explicit, not kernel-instance compromise isolation. User word validation and
park happen under IF=0; old unmap/protect pins and context reset remain enforcing.
No new signal semantics; no cancellation/retry of timed side effects is assumed.

Simpler interrupt counts cannot represent elapsed time under delayed IRQs. Direct
HPET observation avoids premature TSC calibration, ACPI framework and universal
timer service. Keep periodic PIT scheduler events; tickless/AP/SMP/fast paths later.
One explicit clock-domain field preserves old paths without relabelling them.
Apply SE-01–SE-05 and Foundations O/I/E. Scope/docs: NATIVE-CLOCKS,CLOCKS-TIMERS,
STATE,SI-01,R1-03/workflow; no alternative status tree. BSD2 original code; register
facts from Intel HPET1.0a and QEMU HPET source, with upstream links, no copied driver.

Before diagnostics: opt-in park/timeout records carry only task slot and source ns,
bounded ASCII with the existing machine-marker exception in EXPERIENCE. Retain
host observation timestamps as a baseline, not host wall-time accuracy acceptance.
Expanded service-workers are excluded for this first source/wait qualification.

Additional native tests before implementation: one raw, no-libc child per service
uses the existing descriptor/stack/TLS/TID contract. Parent parks without yield
loops, observes confirmed child wait, checks protect/unmap -13 while word pinned,
then either wakes or moves the clock registration to a second word. Old key can
then be reclaimed; child completion/clear-TID is confirmed before backing reuse.
Native timeout records/absolute start survive requeue; normal primary memory/TLS/
64-yield/output witnesses remain. No actual pthread-condition/musl API claim.

Attempt3 exposes an incorrect new test expectation: existing mapping-pin denials
are -13, not -16. The private probe is corrected to the existing contract; kernel
semantics/bytes do not change. Shared child notification/error words are C11
atomics, with trap memory barriers and confirmed completion before reclamation.

Final scope clarification: selected actual waits are200/400ms. The device reports
a10ns counter tick; observed emulator samples are multiples of1000ns and effective
syscall resolution is not certified. Reported-period scaling is not empirical
physical/TSC calibration. Receipts retain run start/end timestamps, not per-line
host counter measurements. Pre-change/each native entry snapshots preserve earlier
wording. No physical accuracy/latency or complete SI-01 acceptance is inferred.
