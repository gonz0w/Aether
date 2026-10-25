# UL-067 close-revision command regression — 2026-09-07

All213 native command cases pass locally on the captured close-policy snapshot.
The original producer suite rebuilds its clients, services, supervisors and kernels
and applies its unchanged positive/negative oracles. The complete pinned source
inventory remains unchanged after execution. The owned outer command exits0 with
complete cleanup within its1800-second bound. No failed attempt occurred.

This closes the current-revision CAT-08 broad command regression gap. The older
213-case finalizer run remains separate historical evidence; the new producer's
own run is not used as a substitute for this local execution.

```
python3 -B experiments/toybox-native/regress-producer.py --snapshot build/toybox-close-consumer-q91nkwbt --execution-receipt build/toybox-close-consumer-q91nkwbt/close-execution-eegzst56/execution.json
```

[Results](results.json) retain tool/SDK/input/driver/explicit wrapper-receipt hashes,
exact argv/environment and owned cleanup. [Native results](native-results.json)
retain all213 outcomes, original producer command records and artifact identities.
Raw serial/QEMU logs are under cases/. Build/inspection logs, ELFs and ISOs remain
in the private native output directory named in the receipt. Child producer records
retain their schema; they are not separate owned process receipts.

The retained runtime diff shows two changed common sources: cat-roles.rs and
toybox-cat-probe.c. In particular, the owner changes its uncertain-reply traffic
guard, which warrants checking older error paths. All existing command cases pass
on the new source. This suite includes conformance fixtures; it is not213 runs of
upstream cat_main. The separately qualified27 actual-applet close cases retain their
own evidence. No SDK rebuild, source authentication or full CAT acceptance follows.

Only the local driver gained explicit wrapper-receipt selection; its old finalizer
default remains available. No producer source/oracle, sibling tree, release pin or
installation changed. The native guest watchdog is unchanged. See [review](review.md).
Full actual-applet matrix, independent review and UL-016 release provenance remain
open. Native dash still awaits matching identity/signal/FD producer support;
UL-007/M3 are not complete. Optional tuning stays deferred.
