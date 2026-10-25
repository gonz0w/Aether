# UL-067 full captured producer regression

All213 native command-runner cases pass locally on the captured finalizer-era
producer. The unmodified producer suite rebuilds its clients, services, supervisors
and kernels, then checks the original positive/negative oracles. The snapshot
inventory remains unchanged after execution. The owned outer process group exits0
with complete cleanup within its1800-second ceiling. No failed attempt occurred.

[Outer results](results.json) record argv, environment, tools, SDK identities and
process cleanup. [Native results](native-results.json) retain all213 case outcomes,
source and artifact identities and original producer command records. Raw serial
and QEMU logs are under cases/. All build/inspection logs, ELFs, payloads and ISOs
remain in the private native output directory named by the receipt. Producer child
records retain their original schema; they are not presented as separate owned
process receipts. See [review](REVIEW.md) and [plan](PLAN.md).

The suite covers existing cat role/admission/error/usage controls and runner
startup, local output, denial, lifetime, forwarded argument, terminal and public
result cases. Expected profile rejection must satisfy its semantic oracle; a
generic panic cannot pass a negative. This is regression evidence for this exact
producer, not a claim of public CLI, shell or POSIX support.

```
python3 -B experiments/toybox-native/regress-producer.py --snapshot build/toybox-final-consumer-1kzyda6n
```

SDK libc/CRT and boot inputs remain pinned dependencies. Tools are hash-checked,
Rust uses the private verified wrapper, and the environment excludes ambient
configuration. No network fetch, installation, sibling edit, source/oracle change
or consumer pin replacement. Prior evidence remains intact. Original/upstream
licenses and output markers remain unchanged.

Together with local finalizer/cat execution and byte-identical backend rebuilds,
this resolves the broad command-suite regression gap for the captured revision.
The newer close-policy candidate is not part of it. Next qualify a completed
close-policy handoff against the explicit remaining CAT-06 requirements, rerunning
affected regressions for that new revision. Independent review and UL-067/M3
acceptance remain open; optional tuning stays deferred.
