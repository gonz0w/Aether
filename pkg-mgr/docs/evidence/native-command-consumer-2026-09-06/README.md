# Package-staged command consumer — 2026-09-06

All 53 reconstructed native cases pass: 22 successes and 31 exact expected
rejections. [Result](result.json) binds package inputs, frozen producer tools,
transport receipts, reconstructed images and serial logs. [Commands](commands.json)
retain exact invocations and per-command exits; raw command logs, images and boot
dependencies remain at /Users/cam/DEV/pkg-mgr/.pkg-command-consumer-20260906-2.
Each case's serial log and transport receipt is also copied under cases/ here.

The images were independently reconstructed from verified package-staged bytes,
not simply booted from the accepted owner ISO. Existing boot-v2/connections
transport verifies the same three-image envelopes. Exact terminal/cleanup/panic
oracles cover finite command behavior, NB-01–04, copied startup, collected-result
mapping and uncertain replies. Successful cases have six reclaims; negative
cases preserve their specific result and terminal distinctions. Uncertain
admission permits optional normal child0 termination without assuming scheduling.
Output byte verification remains with the native owner backend, not runner EOF.

Attempt 1 failed before output creation on a host executable symlink check;
[retained failure](attempt-1.txt) records the correction to hash resolved tool
bytes. Attempt 2 passed all boots with final input checks. No failed native boot
was discarded. Oracle fixtures test all 53 shapes and semantic corruptions.
The normal sixteen-fixture suite passes in 302.450 seconds under its 600-second
watchdog, including all 38 shell lint checks. The 193-file development source
assembly repeats/extracts with matching bytes/modes; frozen candidate unchanged.

This is bounded package transport consumption, not native execution of bin/pkg-mgr,
filesystem-backed loading, persistent installation, full public aether-run CLI,
unknown-resource recovery or independent release approval. Native help/local
outcomes and remaining runner controls retain their owner gates. Shell/tools,
native artifact admission and filesystem publication remain the R1 dependencies.
No sibling sources, shared pins, runtime protocols or old selectors changed.
