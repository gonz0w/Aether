# UL-069 common comparison review

Uses the scope, standards, review status and retention rules of
[CONSUMER-PLAN.md](CONSUMER-PLAN.md).

The common GNU/BusyBox rerun uses run-common.py after the extended attempt has
confirmed container cleanup. It preserves all seventeen fixture expectations,
changing only selected emulator/runtime paths and printing the existing JSON
report for owned capture. Each provider runs in its own 180-second container.
GNU must match 17/17; BusyBox must retain exactly repeat, print-class,
invalid-class and reversed-range failures. A stable comparison is not BusyBox
acceptance. Guest scratch receipts are discarded with the private tmpfs only after
capturing the complete final report. These existing guest subprocess paths remain
within the older source-migration scope; no broader process-safety claim is made.
