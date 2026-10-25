# Corrected detached reaper — 2026-10-06

UL-003/015/081 remain active. Aether's current ordered-exit producer witness
confirms a maintained runtime defect: stopped detached A awaits retirement;
detached B holds actual musl list lock while awaiting reaper permission; the reaper
waits for that same lock. The exact old elapsed-v2 archive reproduces detail870,
supervisor401 and zero reclaims locally. Serial controls pass. This is a new
confirmed cycle, not attribution of the earlier engine leap timeout.

The maintained backend makes the thread record pointer atomic. The sole reaper
owns a pending detached record through confirmed stop, unmap and native retirement;
it resets publication/pending and decrements live before publishing free last.
It never takes musl's list lock during detached retirement. Creators and joiners
retain upstream lock serialization. Native grants, musl exit/list bodies and
82/two, 512 and 8192/128 bounds are unchanged. See [technical review](review.md)
for metadata lifetime and acquire/release ordering.

Ten final native cases pass: old-cycle, old-serial, corrected-cycle,
corrected-serial, normal, stop/replacement, lifecycle/busy-final shutdown, full
512 admissions, disabled clock and dishonest early expiry. Exact ordinary
terminals and three-owner reclaim/replacement are required for successful cases;
forced stop is checked by the source-bound supervisor. The old-cycle test removes
its ordering gates before observing the real cycle twice over 1ms; it does not
alter records, retirement, musl locks or exit bodies. ISO app/kernel modules are
read back byte-for-byte. Every tool and VM has bounded ownership and complete
cleanup. Both Python3.10.21 and3.14.7 reject seven SDK/output/usage controls,
three CLI controls and115 semantic trace corruptions.

Fresh private elapsed v3: `build/sdk-deliveries/native-service-runtime-2026-10-06-v3`.
294 members, seal `5adc4f6e9c255df3ead08404fca177d22db00a089429f1c0666fd90dd1812c6d`;
archive `8262b1977be3b8fff449a6e9ac6d86b20acbc7ab0a1e38102287aecff20b9b23`.
The guarded240-member base SDK remains exact. Minimum/current builds and a separate
copy of sealed sources/SDK produce the same archive; the seal's embedded receipt
predates the standalone check, whose final result is [reproducibility.json](reproducibility.json).
Old candidates remain immutable. The [matching UTC v3](../reaper-utc-2026-10-06/README.md)
requires this exact corrected base.

The dated `qualify.py` is final attempt4 for only disabled/early; earlier full
attempt3 source and receipts preserve the other eight final cases. All failed
attempts are distinct: initial denial oracle expected wrong peer code; substring
`cycle` enabled wrappers for lifecycle; disabled build duplicated Zig boolean
flags. Each was a harness error corrected without runtime changes. Initial
unsealed packet preparation used a missing output header path; only that unsealed
partial packet was removed. The hash-bound historical witness is preserved;
`regression-current.c` applies project formatting and is separately executed in
UTC overlap/serial checks. No failed trace is converted to success.

Next dependency: Aether must independently consume corrected elapsed/UTC seals,
rerun ordered/serial exits, lifecycle/exhaustion/stop and actual OpenZFS helper
reuse before persistence. Broader stop/interruption, initial identity, source trust,
production service, initialized pool/transactions/reboot and independent reader
reviews remain open. Wider SESSION is separate; existing finite lab kit remains
usable. No sibling write, owner acceptance or default release promotion occurs here.


[Final checks](checks.json) pass quality/all three pinned standards, project C
format, minimum/current Python syntax, whitespace and both candidate readbacks.
[Retention](retention.json) verifies4856 generated files/links removed,3403 compact
records retained and468672512 allocated file-block bytes disposed. This is not a
measurement of net free disk. Frozen inputs and all immutable candidates remain.
